#!/bin/bash
# =============================================================================
# WOODPECKER CI - CONTROL SCRIPT
# =============================================================================
# Usage: ./scripts/woodpecker-ctl.sh [command]
# Commands: start, stop, restart, status, logs, backup, update, secrets
# =============================================================================

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo -e "${BLUE}Woodpecker CI Control Script${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show services status"
    echo "  logs        Show logs (use: logs [service] [-f])"
    echo "  backup      Create database backup"
    echo "  update      Update to latest images"
    echo "  secrets     Show how to configure secrets"
    echo "  health      Check services health"
    echo ""
}

check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}Error: $ENV_FILE not found${NC}"
        echo "Run: cp .env.prod.example .env.prod"
        exit 1
    fi
}

cmd_start() {
    check_env
    echo -e "${GREEN}Starting Woodpecker CI...${NC}"
    docker compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
    echo -e "${GREEN}Done!${NC}"
}

cmd_stop() {
    echo -e "${YELLOW}Stopping Woodpecker CI...${NC}"
    docker compose -f $COMPOSE_FILE down
    echo -e "${GREEN}Done!${NC}"
}

cmd_restart() {
    echo -e "${YELLOW}Restarting Woodpecker CI...${NC}"
    docker compose -f $COMPOSE_FILE --env-file $ENV_FILE restart
    echo -e "${GREEN}Done!${NC}"
}

cmd_status() {
    echo -e "${BLUE}Woodpecker CI Status${NC}"
    echo ""
    docker compose -f $COMPOSE_FILE ps
}

cmd_logs() {
    SERVICE=$2
    FOLLOW=$3

    if [ -z "$SERVICE" ]; then
        if [ "$FOLLOW" == "-f" ]; then
            docker compose -f $COMPOSE_FILE logs -f --tail=100
        else
            docker compose -f $COMPOSE_FILE logs --tail=100
        fi
    else
        if [ "$3" == "-f" ]; then
            docker compose -f $COMPOSE_FILE logs -f --tail=100 $SERVICE
        else
            docker compose -f $COMPOSE_FILE logs --tail=100 $SERVICE
        fi
    fi
}

cmd_backup() {
    check_env
    source $ENV_FILE

    BACKUP_DIR="backups"
    BACKUP_FILE="$BACKUP_DIR/woodpecker_$(date +%Y%m%d_%H%M%S).sql.gz"

    mkdir -p $BACKUP_DIR

    echo -e "${BLUE}Creating database backup...${NC}"
    docker compose -f $COMPOSE_FILE exec -T woodpecker-db pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Backup created: $BACKUP_FILE${NC}"
        ls -lh $BACKUP_FILE
    else
        echo -e "${RED}Backup failed!${NC}"
        exit 1
    fi
}

cmd_update() {
    check_env
    echo -e "${BLUE}Updating Woodpecker CI...${NC}"

    echo "Pulling latest images..."
    docker compose -f $COMPOSE_FILE pull

    echo "Restarting services..."
    docker compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d

    echo -e "${GREEN}Update complete!${NC}"
}

cmd_secrets() {
    echo -e "${BLUE}=========================================="
    echo "  CONFIGURING SECRETS IN WOODPECKER"
    echo "==========================================${NC}"
    echo ""
    echo "1. Go to Woodpecker UI > Repository > Settings > Secrets"
    echo ""
    echo "2. Add these secrets:"
    echo ""
    echo -e "   ${YELLOW}GHCR_TOKEN${NC}"
    echo "   Description: GitHub Container Registry token"
    echo "   Create at: https://github.com/settings/tokens"
    echo "   Scopes needed: write:packages, read:packages"
    echo ""
    echo -e "   ${YELLOW}SSH_KEY${NC}"
    echo "   Description: Private SSH key for deployment"
    echo "   Generate: ssh-keygen -t ed25519 -f deploy_key"
    echo "   Add public key to server's authorized_keys"
    echo ""
    echo -e "   ${YELLOW}STAGING_HOST${NC}"
    echo "   Description: Staging server hostname/IP"
    echo "   Example: staging.example.com"
    echo ""
    echo -e "   ${YELLOW}PROD_HOST${NC}"
    echo "   Description: Production server hostname/IP"
    echo "   Example: prod.example.com"
    echo ""
    echo -e "   ${YELLOW}WEBHOOK_URL${NC}"
    echo "   Description: Discord/Slack webhook for notifications"
    echo "   Discord: Server Settings > Integrations > Webhooks"
    echo "   Slack: Apps > Incoming Webhooks"
    echo ""
}

cmd_health() {
    echo -e "${BLUE}Checking services health...${NC}"
    echo ""

    # Check Traefik
    if docker compose -f $COMPOSE_FILE ps traefik 2>/dev/null | grep -q "running"; then
        echo -e "Traefik:           ${GREEN}✓ Running${NC}"
    else
        echo -e "Traefik:           ${RED}✗ Not running${NC}"
    fi

    # Check Woodpecker Server
    if docker compose -f $COMPOSE_FILE ps woodpecker-server 2>/dev/null | grep -q "running"; then
        echo -e "Woodpecker Server: ${GREEN}✓ Running${NC}"
    else
        echo -e "Woodpecker Server: ${RED}✗ Not running${NC}"
    fi

    # Check Woodpecker Agent
    if docker compose -f $COMPOSE_FILE ps woodpecker-agent 2>/dev/null | grep -q "running"; then
        echo -e "Woodpecker Agent:  ${GREEN}✓ Running${NC}"
    else
        echo -e "Woodpecker Agent:  ${RED}✗ Not running${NC}"
    fi

    # Check Database
    if docker compose -f $COMPOSE_FILE ps woodpecker-db 2>/dev/null | grep -q "running"; then
        echo -e "Database:          ${GREEN}✓ Running${NC}"
    else
        echo -e "Database:          ${RED}✗ Not running${NC}"
    fi

    echo ""
}

# Main
case "$1" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs "$@"
        ;;
    backup)
        cmd_backup
        ;;
    update)
        cmd_update
        ;;
    secrets)
        cmd_secrets
        ;;
    health)
        cmd_health
        ;;
    *)
        usage
        exit 1
        ;;
esac
