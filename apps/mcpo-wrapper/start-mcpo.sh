#!/bin/bash

# Start MCPO to expose TaskWarrior MCP server as REST API

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_PORT=${MCPO_PORT:-8085}
API_KEY=${MCPO_API_KEY:-"taskwarrior-secret-key"}
HOST=${MCPO_HOST:-"0.0.0.0"}
PATH_PREFIX=${MCPO_PATH_PREFIX:-"/api/mcpo/"}
FRONTEND_PORT=${FRONTEND_PORT:-3033}
SCRIPT_DIR=$(dirname "$0")

echo -e "${GREEN}Starting MCPO for TaskWarrior MCP server...${NC}"

# Check if MCPO is available
if ! command -v mcpo &> /dev/null; then
    echo -e "${RED}MCPO is not installed${NC}"
    echo -e "${YELLOW}Install it with: pip install mcpo${NC}"
    exit 1
fi

# Display configuration
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  Port: $API_PORT"
echo -e "  Host: $HOST"
echo -e "  Path Prefix: $PATH_PREFIX"
echo -e "  API Key: [configured]"
echo ""
echo -e "${YELLOW}Endpoints:${NC}"
echo -e "  API Base: http://localhost:$API_PORT${PATH_PREFIX}taskwarrior/"
echo -e "  OpenAPI Docs: http://localhost:$API_PORT/docs"
echo -e "  OpenAPI Spec: http://localhost:$API_PORT/openapi.json"
echo ""
echo -e "${YELLOW}Note: MCPO appends 'taskwarrior' to the path prefix${NC}"
echo ""

# Start MCPO
# IMPORTANT: --path-prefix must be BEFORE the -- separator
# mcpo   --config ./config.json   --host 0.0.0.0   --port 8886   --api-key taskwarrior-secret-key   --cors-allow-origins http://localhost:3033   --cors-allow-origins http://localhost:3000   --cors-allow-origins http://localhost:5173   --path-prefix "/api/mcpo/"   --hot-reload
exec mcpo \
  --config $SCRIPT_DIR/config.json \
  --host $HOST \
  --port $API_PORT \
  --api-key $API_KEY \
  --cors-allow-origins http://localhost:$FRONTEND_PORT \
  --cors-allow-origins http://localhost:3033 \
  --cors-allow-origins http://localhost:3000 \
  --cors-allow-origins http://localhost:5173 \
  --cors-allow-origins http://localhost:8080 \
  --cors-allow-origins http://localhost:8085 \
  --path-prefix "/api/mcpo/" \
  --hot-reload 