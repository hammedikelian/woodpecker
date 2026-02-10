#!/bin/bash
# =============================================================================
# START WOODPECKER CI - LOCAL DEVELOPMENT
# =============================================================================
# This script starts Woodpecker for local development with ngrok
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=========================================="
echo "  WOODPECKER CI - LOCAL DEVELOPMENT"
echo "==========================================${NC}"

# Check Docker
echo -e "\n${YELLOW}[1/5] Checking Docker...${NC}"
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker is running.${NC}"

# Check .env.woodpecker
echo -e "\n${YELLOW}[2/5] Checking environment...${NC}"
if [ ! -f .env.woodpecker ]; then
    echo -e "${RED}.env.woodpecker not found!${NC}"
    echo "Please create it from .env.woodpecker.example"
    exit 1
fi
echo -e "${GREEN}Environment file found.${NC}"

# Start ngrok
echo -e "\n${YELLOW}[3/5] Starting ngrok tunnel...${NC}"
pkill ngrok 2>/dev/null || true
ngrok http 8000 > /tmp/ngrok.log 2>&1 &
sleep 3

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else '')" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED}Failed to get ngrok URL. Is ngrok installed?${NC}"
    exit 1
fi
echo -e "${GREEN}Ngrok URL: $NGROK_URL${NC}"

# Update docker-compose with ngrok URL
echo -e "\n${YELLOW}[4/5] Updating Woodpecker configuration...${NC}"
sed -i.bak "s|WOODPECKER_HOST=.*|WOODPECKER_HOST=$NGROK_URL|" docker-compose.woodpecker.yml
echo -e "${GREEN}Configuration updated.${NC}"

echo -e "\n${YELLOW}IMPORTANT: Update your GitHub OAuth App callback URL to:${NC}"
echo -e "${GREEN}$NGROK_URL/authorize${NC}"
echo ""
read -p "Press Enter when done..."

# Start Woodpecker
echo -e "\n${YELLOW}[5/5] Starting Woodpecker...${NC}"
docker compose -f docker-compose.woodpecker.yml --env-file .env.woodpecker up -d

# Wait for startup
sleep 5

# Start local agent
echo -e "\n${YELLOW}Starting local agent...${NC}"
pkill -f woodpecker-agent 2>/dev/null || true

source .env.woodpecker
export WOODPECKER_SERVER="localhost:9000"
export WOODPECKER_AGENT_SECRET
export WOODPECKER_BACKEND="docker"

nohup ~/bin/woodpecker-agent agent > /tmp/woodpecker-agent.log 2>&1 &

echo -e "\n${GREEN}=========================================="
echo "  WOODPECKER CI IS READY!"
echo "==========================================${NC}"
echo ""
echo -e "Web UI:     ${GREEN}$NGROK_URL${NC}"
echo -e "Agent logs: ${YELLOW}/tmp/woodpecker-agent.log${NC}"
echo ""
echo "To stop:    docker compose -f docker-compose.woodpecker.yml down && pkill ngrok && pkill -f woodpecker-agent"
echo ""
