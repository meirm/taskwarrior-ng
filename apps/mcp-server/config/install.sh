#!/bin/bash

echo "Installing Taskwarrior-NG MCP Server (FastMCP)..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if taskwarrior is installed
echo -e "${BLUE}Checking Taskwarrior installation...${NC}"
if ! command -v task &> /dev/null; then
    echo -e "${RED}Taskwarrior is not installed. Please install it first:${NC}"
    echo "  Ubuntu/Debian: sudo apt install taskwarrior"
    echo "  macOS: brew install task"
    echo "  Fedora: sudo dnf install task"
    echo "  Arch: sudo pacman -S task"
    exit 1
fi

# Get and display Taskwarrior version
task_version=$(task --version 2>/dev/null | head -n1)
echo -e "${GREEN}✓ Taskwarrior found: ${task_version}${NC}"

# Check Python version
echo -e "${BLUE}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    python_cmd="python3"
elif command -v python &> /dev/null; then
    python_cmd="python"
else
    echo -e "${RED}Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

python_version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}Python 3.8+ is required. Current version: $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $python_version found${NC}"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${YELLOW}Using existing virtual environment: $VIRTUAL_ENV${NC}"
    venv_created=false
else
    # Create virtual environment
    echo -e "${BLUE}Creating virtual environment...${NC}"
    $python_cmd -m venv taskwarrior-mcp-env
    
    # Activate virtual environment
    source taskwarrior-mcp-env/bin/activate
    venv_created=true
    echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
fi

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed from requirements.txt${NC}"
else
    echo -e "${YELLOW}requirements.txt not found, installing core dependencies...${NC}"
    pip install "tasklib>=2.5.1" "mcp>=1.13.0" "pydantic>=2.0.0" "fastmcp>=2.11.3"
fi

# Test the installation
echo -e "${BLUE}Testing installation...${NC}"
$python_cmd -c "
import tasklib
import mcp
import fastmcp
import pydantic
print('✓ All required packages imported successfully')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation test passed${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    exit 1
fi

# Try to initialize taskwarrior connection
echo -e "${BLUE}Testing Taskwarrior connection...${NC}"
$python_cmd -c "
from tasklib import TaskWarrior
try:
    tw = TaskWarrior()
    print('✓ Taskwarrior connection successful')
except Exception as e:
    print(f'⚠ Taskwarrior connection issue: {e}')
    print('This may be normal if no tasks exist yet.')
"

echo
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo
echo -e "${YELLOW}To run the MCP server:${NC}"
if [ "$venv_created" = true ]; then
    echo "  source taskwarrior-mcp-env/bin/activate"
fi
echo "  python /Users/meirm/git/riunx/taskwarrior-ng/apps/mcp-server/src/taskwarrior_mcp_server.py"
echo
echo -e "${YELLOW}For Claude Desktop integration, add this to your config:${NC}"
echo '{
  "mcpServers": {
    "taskwarrior": {
      "command": "python",
      "args": ["/Users/meirm/git/riunx/taskwarrior-ng/apps/mcp-server/src/taskwarrior_mcp_server.py"]
    }
  }
}'
echo
echo -e "${BLUE}For more information, see README.md${NC}"
