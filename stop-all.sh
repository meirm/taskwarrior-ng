#!/bin/bash

# Force stop all TaskWarrior-NG services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}Stopping all TaskWarrior-NG services...${NC}"

# Kill Vite dev server (usually on port 3033)
echo -e "${YELLOW}Stopping Vite dev server...${NC}"
lsof -ti:3033 | xargs -r kill -9 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Kill MCPO server (usually on port 8085)
echo -e "${YELLOW}Stopping MCPO server...${NC}"
lsof -ti:8085 | xargs -r kill -9 2>/dev/null || true
pkill -f "mcpo" 2>/dev/null || true

# Kill any Python MCP server processes
echo -e "${YELLOW}Stopping MCP server processes...${NC}"
pkill -f "taskwarrior_mcp_server" 2>/dev/null || true
pkill -f "python.*mcp.*server" 2>/dev/null || true

# Kill any Node.js processes related to the project
echo -e "${YELLOW}Stopping Node.js processes...${NC}"
pkill -f "node.*taskwarrior" 2>/dev/null || true
pkill -f "npm.*taskwarrior" 2>/dev/null || true

# Kill any remaining npm processes in this directory
echo -e "${YELLOW}Stopping npm processes...${NC}"
pkill -f "npm run" 2>/dev/null || true

# macOS specific: use lsof to find processes using common ports
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Additional cleanup for macOS
    echo -e "${YELLOW}Cleaning up port bindings (macOS)...${NC}"
    
    # Common development ports
    PORTS=(3033 3000 5173 8085 8886 8080)
    
    for port in "${PORTS[@]}"; do
        PID=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$PID" ]; then
            echo -e "  Killing process on port $port (PID: $PID)"
            kill -9 $PID 2>/dev/null || true
        fi
    done
fi

# Check if any services are still running
echo -e "\n${YELLOW}Checking for remaining processes...${NC}"

STILL_RUNNING=false

# Check specific ports
if lsof -i:3033 &>/dev/null; then
    echo -e "${RED}  Warning: Port 3033 still in use${NC}"
    STILL_RUNNING=true
fi

if lsof -i:8085 &>/dev/null; then
    echo -e "${RED}  Warning: Port 8085 still in use${NC}"
    STILL_RUNNING=true
fi

# Check for specific processes
if pgrep -f "vite" &>/dev/null; then
    echo -e "${RED}  Warning: Vite process still running${NC}"
    STILL_RUNNING=true
fi

if pgrep -f "mcpo" &>/dev/null; then
    echo -e "${RED}  Warning: MCPO process still running${NC}"
    STILL_RUNNING=true
fi

if [ "$STILL_RUNNING" = false ]; then
    echo -e "${GREEN}✓ All services stopped successfully${NC}"
else
    echo -e "${RED}Some services may still be running. You may need to restart your terminal or use 'sudo' for stubborn processes.${NC}"
    echo -e "${YELLOW}To force kill with sudo, run: sudo $0${NC}"
fi

echo -e "\n${GREEN}Done!${NC}"