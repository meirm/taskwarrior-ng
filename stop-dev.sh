#!/bin/bash

# TaskWarrior-NG Development Stop Script
# This script stops all components of the TaskWarrior full-stack application
#
# Usage: ./stop-dev.sh [--force] [--clean]
# Options:
#   --force  Force kill processes without graceful shutdown
#   --clean  Clean up all temporary files and caches

set -e

# Default options
FORCE_KILL=false
CLEAN_MODE=false

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
    echo "TaskWarrior-NG Development Stop Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --force     Force kill all processes without graceful shutdown"
    echo "  --clean     Clean up temporary files and caches"
    echo "  -h, --help  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Graceful shutdown"
    echo "  $0 --force      # Force kill all processes"
    echo "  $0 --clean      # Stop and clean up everything"
    echo "  $0 --force --clean  # Force stop and clean up"
    echo ""
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_KILL=true
                shift
                ;;
            --clean)
                CLEAN_MODE=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Find processes by pattern and return PIDs
find_processes() {
    local pattern=$1
    pgrep -f "$pattern" 2>/dev/null || true
}

# Kill processes gracefully or forcefully
kill_processes() {
    local pids=$1
    local name=$2
    local force=$3
    
    if [ -z "$pids" ]; then
        return 0
    fi
    
    echo "$pids" | while read -r pid; do
        if [ ! -z "$pid" ]; then
            if [ "$force" = true ]; then
                print_status "Force killing $name process (PID: $pid)..."
                kill -9 "$pid" 2>/dev/null || true
            else
                print_status "Gracefully stopping $name process (PID: $pid)..."
                kill -TERM "$pid" 2>/dev/null || true
                
                # Wait for graceful shutdown (max 10 seconds)
                local count=0
                while [ $count -lt 10 ] && kill -0 "$pid" 2>/dev/null; do
                    sleep 1
                    count=$((count + 1))
                done
                
                # Force kill if still running
                if kill -0 "$pid" 2>/dev/null; then
                    print_warning "$name process didn't shut down gracefully, force killing..."
                    kill -9 "$pid" 2>/dev/null || true
                fi
            fi
        fi
    done
}

# Stop frontend development server
stop_frontend() {
    print_status "Stopping frontend development server..."
    
    # Find Vite processes
    local vite_pids=$(find_processes "vite.*--port")
    if [ ! -z "$vite_pids" ]; then
        kill_processes "$vite_pids" "Vite" $FORCE_KILL
        print_success "Frontend server stopped"
    else
        print_status "No frontend server processes found"
    fi
}

# Stop API bridge server
stop_api_bridge() {
    print_status "Stopping API bridge server..."
    
    # Find API bridge processes
    local api_pids=$(find_processes "api-bridge.*npm run dev")
    if [ ! -z "$api_pids" ]; then
        kill_processes "$api_pids" "API Bridge" $FORCE_KILL
        print_success "API bridge server stopped"
    else
        print_status "No API bridge server processes found"
    fi
    
    # Also stop nodemon processes that might be running the API bridge
    local nodemon_pids=$(find_processes "nodemon.*server.js")
    if [ ! -z "$nodemon_pids" ]; then
        kill_processes "$nodemon_pids" "Nodemon API" $FORCE_KILL
    fi
}

# Stop MCP server processes
stop_mcp_server() {
    print_status "Stopping MCP server processes..."
    
    # Find Python MCP server processes
    local mcp_pids=$(find_processes "python.*taskwarrior_mcp_server")
    if [ ! -z "$mcp_pids" ]; then
        kill_processes "$mcp_pids" "MCP Server" $FORCE_KILL
        print_success "MCP server stopped"
    else
        print_status "No MCP server processes found"
    fi
}

# Stop any remaining Node.js development processes
stop_remaining_node_processes() {
    print_status "Stopping remaining Node.js development processes..."
    
    # Find npm run dev processes
    local npm_pids=$(find_processes "npm run dev")
    if [ ! -z "$npm_pids" ]; then
        kill_processes "$npm_pids" "npm dev" $FORCE_KILL
    fi
    
    # Find any remaining node processes related to the project
    local node_pids=$(find_processes "node.*taskwarrior")
    if [ ! -z "$node_pids" ]; then
        kill_processes "$node_pids" "Node.js" $FORCE_KILL
    fi
}

# Clean up temporary files
cleanup_temp_files() {
    if [ "$CLEAN_MODE" = false ]; then
        return 0
    fi
    
    print_status "Cleaning up temporary files..."
    
    # Frontend temporary files
    rm -f apps/frontend/start-custom.js 2>/dev/null || true
    rm -f apps/frontend/vite.config.override.js 2>/dev/null || true
    rm -f apps/frontend/.env.local 2>/dev/null || true
    
    # API Bridge temporary files
    rm -f apps/api-bridge/.env 2>/dev/null || true
    
    # Remove log files if they exist
    rm -f apps/*/logs/*.log 2>/dev/null || true
    rm -f *.log 2>/dev/null || true
    
    print_success "Temporary files cleaned up"
}

# Clean up caches and build artifacts
cleanup_caches() {
    if [ "$CLEAN_MODE" = false ]; then
        return 0
    fi
    
    print_status "Cleaning up caches and build artifacts..."
    
    # Frontend build artifacts and cache
    if [ -d "apps/frontend/dist" ]; then
        rm -rf apps/frontend/dist
        print_status "Removed frontend build directory"
    fi
    
    if [ -d "apps/frontend/node_modules/.vite" ]; then
        rm -rf apps/frontend/node_modules/.vite
        print_status "Removed Vite cache"
    fi
    
    # API Bridge cache
    if [ -d "apps/api-bridge/node_modules/.cache" ]; then
        rm -rf apps/api-bridge/node_modules/.cache
        print_status "Removed API bridge cache"
    fi
    
    print_success "Caches and build artifacts cleaned up"
}

# Check if running from correct directory
check_directory() {
    if [ ! -f "CLAUDE.md" ]; then
        print_error "Please run this script from the taskwarrior-ng root directory"
        exit 1
    fi
}

# Check for running processes
check_running_processes() {
    print_status "Checking for running TaskWarrior-NG processes..."
    
    local total_processes=0
    
    # Count processes
    local vite_count=$(find_processes "vite.*--port" | wc -l)
    local api_count=$(find_processes "api-bridge.*npm run dev" | wc -l)
    local mcp_count=$(find_processes "python.*taskwarrior_mcp_server" | wc -l)
    local node_count=$(find_processes "npm run dev" | wc -l)
    
    total_processes=$((vite_count + api_count + mcp_count + node_count))
    
    if [ $total_processes -eq 0 ]; then
        print_status "No TaskWarrior-NG processes are currently running"
        
        if [ "$CLEAN_MODE" = true ]; then
            cleanup_temp_files
            cleanup_caches
        fi
        
        return 1
    fi
    
    print_config "Found $total_processes running processes:"
    if [ $vite_count -gt 0 ]; then
        print_config "  - Frontend (Vite): $vite_count processes"
    fi
    if [ $api_count -gt 0 ]; then
        print_config "  - API Bridge: $api_count processes"
    fi
    if [ $mcp_count -gt 0 ]; then
        print_config "  - MCP Server: $mcp_count processes"
    fi
    if [ $node_count -gt 0 ]; then
        print_config "  - Node.js dev: $node_count processes"
    fi
    
    return 0
}

# Main execution
main() {
    clear
    echo "🛑 TaskWarrior-NG Development Stop Script"
    echo "========================================"
    echo ""
    
    # Check directory
    check_directory
    
    # Parse arguments
    parse_arguments "$@"
    
    # Show configuration
    if [ "$FORCE_KILL" = true ]; then
        print_config "Mode: Force kill processes"
    else
        print_config "Mode: Graceful shutdown"
    fi
    
    if [ "$CLEAN_MODE" = true ]; then
        print_config "Cleanup: Will clean temporary files and caches"
    fi
    echo ""
    
    # Check for running processes
    if ! check_running_processes; then
        print_success "✅ No processes to stop"
        exit 0
    fi
    
    echo ""
    print_status "Stopping TaskWarrior-NG development environment..."
    echo ""
    
    # Stop services in order
    stop_frontend
    stop_api_bridge
    stop_mcp_server
    stop_remaining_node_processes
    
    # Wait a moment for processes to fully terminate
    sleep 2
    
    # Clean up temporary files and caches if requested
    cleanup_temp_files
    cleanup_caches
    
    echo ""
    print_success "🎉 TaskWarrior-NG development environment stopped successfully!"
    
    # Final process check
    local remaining=$(check_running_processes 2>/dev/null | grep -c "Found.*processes" || echo "0")
    if [ "$remaining" != "0" ]; then
        print_warning "Some processes may still be running. Use --force to kill them immediately."
        print_status "Run: ./stop-dev.sh --force"
    else
        print_success "✅ All processes stopped cleanly"
    fi
    
    echo ""
}

# Run main function
main "$@"