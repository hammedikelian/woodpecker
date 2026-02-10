#!/bin/bash
# =============================================================================
# WOODPECKER CI - PRODUCTION SETUP SCRIPT
# =============================================================================
# This script helps you set up Woodpecker CI in production
# Run on your server: bash scripts/setup-production.sh
# =============================================================================

set -e

echo "=========================================="
echo "  WOODPECKER CI - PRODUCTION SETUP"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. Consider using a non-root user with docker group.${NC}"
fi

# Check Docker
echo -e "\n${GREEN}[1/6] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. Please log out and back in, then re-run this script.${NC}"
    exit 1
fi
docker --version

# Check Docker Compose
echo -e "\n${GREEN}[2/6] Checking Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose not found. Please install Docker Compose V2.${NC}"
    exit 1
fi
docker compose version

# Check .env.prod file
echo -e "\n${GREEN}[3/6] Checking environment file...${NC}"
if [ ! -f .env.prod ]; then
    if [ -f .env.prod.example ]; then
        echo -e "${YELLOW}Creating .env.prod from template...${NC}"
        cp .env.prod.example .env.prod

        # Generate secrets
        echo -e "${YELLOW}Generating secrets...${NC}"
        AGENT_SECRET=$(openssl rand -hex 32)
        DB_PASSWORD=$(openssl rand -base64 24 | tr -d '=+/')

        # Update .env.prod with generated values
        sed -i "s/^WOODPECKER_AGENT_SECRET=.*/WOODPECKER_AGENT_SECRET=$AGENT_SECRET/" .env.prod
        sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env.prod

        echo -e "${RED}Please edit .env.prod and fill in your values:${NC}"
        echo "  - DOMAIN"
        echo "  - ACME_EMAIL"
        echo "  - GITHUB_CLIENT_ID"
        echo "  - GITHUB_CLIENT_SECRET"
        echo "  - WOODPECKER_ADMIN"
        echo ""
        echo "Then re-run this script."
        exit 0
    else
        echo -e "${RED}.env.prod.example not found!${NC}"
        exit 1
    fi
fi

# Validate required variables
echo -e "\n${GREEN}[4/6] Validating configuration...${NC}"
source .env.prod

REQUIRED_VARS=(DOMAIN GITHUB_CLIENT_ID GITHUB_CLIENT_SECRET WOODPECKER_ADMIN WOODPECKER_AGENT_SECRET DB_PASSWORD)
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}Error: $var is not set in .env.prod${NC}"
        exit 1
    fi
done
echo -e "${GREEN}All required variables are set.${NC}"

# Create required directories
echo -e "\n${GREEN}[5/6] Creating directories...${NC}"
mkdir -p backups logs

# Start services
echo -e "\n${GREEN}[6/6] Starting services...${NC}"
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Wait for services
echo -e "\n${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check status
echo -e "\n${GREEN}=========================================="
echo "  SETUP COMPLETE"
echo "==========================================${NC}"
echo ""
echo "Services status:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo -e "${GREEN}Woodpecker CI is available at: https://ci.${DOMAIN}${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure DNS: Point ci.${DOMAIN} to this server"
echo "  2. Wait a few minutes for SSL certificate"
echo "  3. Log in with your GitHub account"
echo "  4. Add secrets in Woodpecker UI (Repository > Secrets)"
echo ""
