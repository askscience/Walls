#!/bin/bash

# Start All MCP Servers Script
# This script starts all three MCP servers for the Walls applications

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directory - get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"

echo -e "${BLUE}=== Starting Walls MCP Servers ===${NC}"
echo

# Function to check if a process is running
check_process() {
    local name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}$name is already running (PID: $pid)${NC}"
            return 0
        else
            rm -f "$pid_file"
        fi
    fi
    return 1
}

# Function to start a server
start_server() {
    local name=$1
    local dir=$2
    local script=$3
    local pid_file="$BASE_DIR/$dir/$name.pid"
    local log_file="$BASE_DIR/$dir/$name.log"
    
    echo -e "${BLUE}Starting $name MCP Server...${NC}"
    
    if check_process "$name" "$pid_file"; then
        return 0
    fi
    
    # Change to server directory
    cd "$BASE_DIR/$dir"
    
    # Check if requirements are installed
    if [ -f "requirements.txt" ]; then
        echo "  Checking dependencies..."
        pip install -r requirements.txt > /dev/null 2>&1 || {
            echo -e "  ${RED}Failed to install dependencies for $name${NC}"
            return 1
        }
    fi
    
    # Start the server in background
    echo "  Starting server..."
    nohup python "$script" > "$log_file" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$pid_file"
    
    # Wait a moment and check if it's still running
    sleep 2
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "  ${GREEN}$name MCP Server started successfully (PID: $pid)${NC}"
        echo "  Log file: $log_file"
    else
        echo -e "  ${RED}$name MCP Server failed to start${NC}"
        echo "  Check log file: $log_file"
        rm -f "$pid_file"
        return 1
    fi
    
    echo
}

# Function to stop all servers
stop_servers() {
    echo -e "${YELLOW}Stopping all MCP servers...${NC}"
    
    for server in "word_editor" "browser" "radio_player" "rag"; do
        local pid_file="$BASE_DIR/$server/$server.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if ps -p $pid > /dev/null 2>&1; then
                echo "  Stopping $server (PID: $pid)..."
                kill $pid
                rm -f "$pid_file"
            else
                rm -f "$pid_file"
            fi
        fi
    done
    
    echo -e "${GREEN}All servers stopped${NC}"
}

# Function to show server status
show_status() {
    echo -e "${BLUE}=== MCP Server Status ===${NC}"
    echo
    
    for server in "word_editor" "browser" "radio_player" "rag"; do
        local pid_file="$BASE_DIR/$server/$server.pid"
        local log_file="$BASE_DIR/$server/$server.log"
        
        echo -e "${BLUE}$server MCP Server:${NC}"
        
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "  Status: ${GREEN}Running${NC} (PID: $pid)"
                echo "  Log: $log_file"
            else
                echo -e "  Status: ${RED}Stopped${NC} (stale PID file)"
                rm -f "$pid_file"
            fi
        else
            echo -e "  Status: ${RED}Stopped${NC}"
        fi
        echo
    done
}

# Main script logic
case "${1:-start}" in
    "start")
        echo "Starting all MCP servers..."
        echo
        
        # Start each server
        start_server "word_editor" "word_editor" "server.py"
        start_server "browser" "browser" "server.py"
        start_server "radio_player" "radio_player" "server.py"
        start_server "rag" "rag" "server.py"
        
        echo -e "${GREEN}=== All MCP Servers Started ===${NC}"
        echo
        echo "To check status: $0 status"
        echo "To stop all: $0 stop"
        echo "To view logs: tail -f $BASE_DIR/*/*.log"
        ;;
        
    "stop")
        stop_servers
        ;;
        
    "restart")
        stop_servers
        sleep 2
        echo
        $0 start
        ;;
        
    "status")
        show_status
        ;;
        
    "logs")
        echo -e "${BLUE}=== Recent MCP Server Logs ===${NC}"
        echo
        for server in "word_editor" "browser" "radio_player" "rag"; do
            local log_file="$BASE_DIR/$server/$server.log"
            if [ -f "$log_file" ]; then
                echo -e "${BLUE}=== $server ===${NC}"
                tail -n 10 "$log_file"
                echo
            fi
        done
        ;;
        
    "help")
        echo "Usage: $0 [start|stop|restart|status|logs|help]"
        echo
        echo "Commands:"
        echo "  start    - Start all MCP servers (default)"
        echo "  stop     - Stop all MCP servers"
        echo "  restart  - Restart all MCP servers"
        echo "  status   - Show server status"
        echo "  logs     - Show recent logs from all servers"
        echo "  help     - Show this help message"
        ;;
        
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac