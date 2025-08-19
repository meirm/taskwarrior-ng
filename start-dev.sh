#!/bin/bash

# TaskWarrior-NG Development Startup Script
# This script starts all components of the TaskWarrior full-stack application
#
# Usage: ./start-dev.sh [frontend-port] [api-port]
# Example: ./start-dev.sh 3000 3001
# Example: ./start-dev.sh 8080 8081

set -e

# Default ports
DEFAULT_FRONTEND_PORT=3033
DEFAULT_API_PORT=8085

# Parse command line arguments
FRONTEND_PORT=${1:-$DEFAULT_FRONTEND_PORT}
API_PORT=${2:-$DEFAULT_API_PORT}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_config() {
    echo -e "${CYAN}[CONFIG]${NC} $1"
}

# Show usage
show_usage() {
    echo "Usage: $0 [frontend-port] [api-port]"
    echo ""
    echo "Arguments:"
    echo "  frontend-port  Port for the frontend server (default: 3000)"
    echo "  api-port       Port for the API bridge server (default: 3001)"
    echo ""
    echo "Examples:"
    echo "  $0              # Use default ports (3000, 3001)"
    echo "  $0 8080         # Frontend on 8080, API on 3001"
    echo "  $0 8080 8081    # Frontend on 8080, API on 8081"
    echo ""
}

# Validate port number
validate_port() {
    local port=$1
    local name=$2
    
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
        print_error "$name port must be a number"
        exit 1
    fi
    
    if [ "$port" -lt 1024 ] || [ "$port" -gt 65535 ]; then
        print_error "$name port must be between 1024 and 65535"
        exit 1
    fi
    
    # Check if port is already in use
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $port is already in use"
        exit 1
    fi
}

# Check if TaskWarrior is installed
check_taskwarrior() {
    print_status "Checking TaskWarrior installation..."
    if ! command -v task &> /dev/null; then
        print_error "TaskWarrior is not installed. Please install it first:"
        print_error "  macOS: brew install task"
        print_error "  Ubuntu: sudo apt-get install taskwarrior"
        print_error "  Arch: sudo pacman -S task"
        exit 1
    fi
    print_success "TaskWarrior is installed ($(task --version))"
}

# Check Python dependencies
check_python_deps() {
    print_status "Checking Python dependencies for MCP server..."
    cd apps/mcp-server
    if [ ! -f "config/requirements.txt" ]; then
        print_error "config/requirements.txt not found in MCP server directory"
        exit 1
    fi
    
    # Check if virtual environment exists, create if not
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -q -r config/requirements.txt
    print_success "Python dependencies installed"
    cd ../..
}

# Check Node.js dependencies
check_node_deps() {
    print_status "Checking Node.js dependencies..."
    
    # Frontend dependencies  
    cd apps/frontend
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install --silent
    fi
    cd ../..
    
    print_success "Node.js dependencies installed"
}

# Check MCPO wrapper dependencies
check_mcpo_deps() {
    print_status "Checking MCPO wrapper dependencies..."
    
    # Check Python packages required for MCPO wrapper
    for pkg in mcpo fastapi uvicorn httpx; do
        if ! python -c "import $pkg" 2>/dev/null; then
            print_status "Installing Python package: $pkg"
            pip install $pkg >/dev/null 2>&1
        fi
    done
    
    print_success "MCPO wrapper dependencies installed"
}

# Update configuration files with custom ports
update_configs() {
    print_status "Updating configuration with custom ports..."
    
    # Don't overwrite MCPO wrapper config.json - it's now static
    # Configuration is passed via environment variables instead
    
    # Update frontend API configuration
    cd apps/frontend
    # Create a temporary environment file for Vite
    # NOTE: MCPO appends "taskwarrior" to the path prefix
    # So the full path is /api/mcpo/taskwarrior/
    cat > .env.local << EOF
VITE_API_HOST=localhost
VITE_API_PORT=$API_PORT
VITE_API_PROTOCOL=http
VITE_API_PREFIX=/api/mcpo/taskwarrior
VITE_API_URL=http://localhost:$API_PORT
VITE_MCPO_URL=http://localhost:$API_PORT
VITE_MCPO_API_KEY=taskwarrior-secret-key
EOF
    cd ../..
    
    # Update frontend vite.config.ts to use custom port
    cd apps/frontend
    # Create a temporary vite config override
    cat > vite.config.override.js << EOF
export const PORT = $FRONTEND_PORT;
export const API_PORT = $API_PORT;
EOF
    cd ../..
    
    print_success "Configuration updated with custom ports"
}

# Start MCPO wrapper
start_mcpo() {
    print_status "Starting MCPO wrapper on port $API_PORT..."
    cd apps/mcpo-wrapper
    
    # Make sure the start script is executable
    chmod +x start-mcpo.sh 2>/dev/null || true
    
    # Set environment variables for MCPO wrapper script
    export MCPO_PORT=$API_PORT
    export MCPO_API_KEY="taskwarrior-secret-key"
    export MCPO_HOST="0.0.0.0"
    export MCPO_PATH_PREFIX="/api/mcpo/"
    
    # Use the mcpo-wrapper start script which uses config.json
    ./start-mcpo.sh &
    MCPO_PID=$!
    cd ../..
    
    # Wait for MCPO to start
    sleep 5
    # Check if the OpenAPI spec is available as a health check
    if ! curl -s http://localhost:$API_PORT/openapi.json > /dev/null 2>&1; then
        print_warning "MCPO may not have started properly"
    else
        print_success "MCPO started successfully on port $API_PORT"
    fi
}

# Start frontend development server
start_frontend() {
    print_status "Starting frontend development server on port $FRONTEND_PORT..."
    cd apps/frontend
    
    # Create temporary vite startup script with custom port
    cat > start-custom.js << EOF
import { spawn } from 'child_process';

const viteProcess = spawn('npx', ['vite', '--host', '--port', '$FRONTEND_PORT'], {
  stdio: 'inherit',
  env: {
    ...process.env,
    VITE_API_URL: 'http://localhost:$API_PORT/api'
  }
});

viteProcess.on('error', (err) => {
  console.error('Failed to start Vite:', err);
  process.exit(1);
});
EOF
    
    # Run vite with custom port
    VITE_API_URL=http://localhost:$API_PORT npx vite --host --port $FRONTEND_PORT &
    FRONTEND_PID=$!
    cd ../..
    
    # Wait for frontend to start
    sleep 5
    print_success "Frontend server started successfully on port $FRONTEND_PORT"
}

# Cleanup function
cleanup() {
    print_status "Shutting down development servers..."
    
    if [ ! -z "$MCPO_PID" ]; then
        kill $MCPO_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "mcpo" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "taskwarrior_mcp_server.py" 2>/dev/null || true
    
    # Clean up temporary files
    rm -f apps/frontend/start-custom.js 2>/dev/null || true
    rm -f apps/frontend/vite.config.override.js 2>/dev/null || true
    rm -f apps/frontend/.env.local 2>/dev/null || true
    
    print_success "Development servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    clear
    echo "🚀 TaskWarrior-NG Development Environment"
    echo "========================================"
    
    # Show help if requested
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi
    
    # Validate port numbers
    validate_port $FRONTEND_PORT "Frontend"
    validate_port $API_PORT "API"
    
    # Check for port conflicts
    if [ "$FRONTEND_PORT" = "$API_PORT" ]; then
        print_error "Frontend and API ports cannot be the same"
        exit 1
    fi
    
    # Display configuration
    echo ""
    print_config "Frontend port: $FRONTEND_PORT"
    print_config "API port: $API_PORT"
    echo ""
    
    # Pre-flight checks
    check_taskwarrior
    check_python_deps
    check_mcpo_deps
    check_node_deps
    
    # Update configurations with custom ports
    update_configs
    
    echo ""
    print_status "Starting development servers..."
    
    # Start servers
    start_mcpo
    start_frontend
    
    echo ""
    print_success "🎉 All servers started successfully!"
    echo ""
    echo "📊 Services:"
    echo "   Frontend:     http://localhost:$FRONTEND_PORT"
    echo "   MCPO Server:  http://localhost:$API_PORT"
    echo "   API Docs:     http://localhost:$API_PORT/docs"
    echo "   OpenAPI Spec: http://localhost:$API_PORT/openapi.json"
    echo ""
    echo "📝 Logs:"
    echo "   Check terminal for real-time logs from both servers"
    echo ""
    echo "🛑 To stop: Press Ctrl+C"
    echo ""
    
    # Keep script running
    wait
}

# Check if we're in the right directory
if [ ! -f "CLAUDE.md" ]; then
    print_error "Please run this script from the taskwarrior-ng root directory"
    exit 1
fi

# Run main function
main "$@"