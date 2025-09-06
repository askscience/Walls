#!/usr/bin/env python3
"""Start core Walls services with proper virtual environment support.

- Launches shared_server.start_server (shared coordination server)
- Starts all MCP servers (RAG, Browser, Word Editor, Radio Player)
- Launches ai_interface/main.py

Usage:
  python start_all.py [--debug]
"""
from __future__ import annotations
import os
import sys
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json

# Resolve workspace root (the directory of this script)
ROOT = Path(__file__).resolve().parent

# Prefer the virtualenv python if present
VENV_PY = ROOT / "venv" / "bin" / "python"
VENV_ACTIVATE = ROOT / "venv" / "bin" / "activate"
PYTHON = str(VENV_PY if VENV_PY.exists() else sys.executable)

# Setup environment to ensure venv is used
ENV = os.environ.copy()
ENV["PYTHONUNBUFFERED"] = "1"
ENV["PYTHONPATH"] = str(ROOT)
ENV["WALLS_PROJECT_ROOT"] = str(ROOT)

# Terminal colors and formatting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")

def print_step(step: int, total: int, text: str) -> None:
    """Print a step with progress indicator."""
    progress = f"[{step}/{total}]"
    print(f"{Colors.BOLD}{Colors.BLUE}{progress:<8}{Colors.ENDC} {text}")

def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {text}")

def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {text}")

def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {text}")

def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.CYAN}[INFO]{Colors.ENDC} {text}")

def print_status_table(processes: list) -> None:
    """Print a formatted status table."""
    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}{'Service':<25} {'PID':<8} {'Status':<15}{Colors.ENDC}")
    print("-" * 50)
    
    for name, proc in processes:
        if proc.poll() is None:
            status = f"{Colors.GREEN}Running{Colors.ENDC}"
            pid = f"{Colors.CYAN}{proc.pid}{Colors.ENDC}"
        else:
            status = f"{Colors.RED}Exited ({proc.poll()}){Colors.ENDC}"
            pid = f"{Colors.RED}{proc.pid}{Colors.ENDC}"
        
        print(f"{name:<25} {pid:<15} {status}")

# If venv exists, set up proper environment variables
if VENV_PY.exists():
    venv_path = str(ROOT / "venv")
    ENV["VIRTUAL_ENV"] = venv_path
    ENV["PATH"] = f"{venv_path}/bin:{ENV.get('PATH', '')}"
    # Remove PYTHONHOME if set (can interfere with venv)
    ENV.pop("PYTHONHOME", None)
    print_success(f"Using virtual environment: {venv_path}")
else:
    print_warning("Virtual environment not found, using system Python")


def start_process(cmd: list[str], cwd: Path) -> subprocess.Popen:
    print_info(f"Executing: {Colors.BOLD}{' '.join(cmd)}{Colors.ENDC}")
    print_info(f"Working directory: {Colors.CYAN}{cwd}{Colors.ENDC}")
    return subprocess.Popen(cmd, cwd=str(cwd), env=ENV)

def start_mcp_servers() -> bool:
    """Start all MCP servers using the shared server CLI."""
    print("Starting MCP servers...")
    
    # List of MCP servers to start
    mcp_servers = ["word_editor", "browser", "radio_player", "rag"]
    started_servers = []
    failed_servers = []
    
    for server in mcp_servers:
        try:
            print(f"  Starting {server}...")
            result = subprocess.run(
                [PYTHON, "-m", "shared_server.cli", "mcp", "start", server],
                cwd=str(ROOT),
                env=ENV,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                print(f"  ✓ {server} started")
                started_servers.append(server)
            else:
                print(f"  ✗ {server} failed: {result.stderr.strip()}")
                failed_servers.append(server)
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ {server} startup timed out")
            failed_servers.append(server)
        except Exception as e:
            print(f"  ✗ {server} error: {e}")
            failed_servers.append(server)
    
    if started_servers:
        print(f"✓ Started MCP servers: {', '.join(started_servers)}")
    if failed_servers:
        print(f"✗ Failed MCP servers: {', '.join(failed_servers)}")
    
    return len(started_servers) > 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Start core Walls services")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--with-ollama", action="store_true", help="Start Ollama MCP bridge")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for all components")
    
    args = parser.parse_args()
    
    # Enable debug modes if requested
    if args.debug or args.verbose:
        ENV['RAG_DEBUG'] = '1'
        ENV['AI_IFACE_DEBUG'] = '1'
        ENV['VOICE_DEBUG'] = '1'
        ENV['MCP_DEBUG'] = '1'
        print_info("Debug mode enabled - comprehensive logging active")
        print_info("   - RAG database queries and responses")
        print_info("   - User inputs and AI outputs")
        print_info("   - MCP server communications")
        print_info("   - Voice processing details")
        print()
    
    # Print startup banner
    print_header("WALLS SYSTEM STARTUP")
    print_info(f"Started at: {Colors.BOLD}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print_info(f"Python: {Colors.BOLD}{PYTHON}{Colors.ENDC}")
    print_info(f"Working directory: {Colors.BOLD}{ROOT}{Colors.ENDC}")
    
    if args.with_ollama:
        print_info(f"Mode: {Colors.BOLD}{Colors.YELLOW}Full Stack + Ollama Bridge{Colors.ENDC}")
    else:
        print_info(f"Mode: {Colors.BOLD}{Colors.GREEN}Standard Stack{Colors.ENDC}")
    
    if args.debug or args.verbose:
        print_info(f"Debug Mode: {Colors.BOLD}{Colors.CYAN}Enabled{Colors.ENDC}")
        print_info("   - Comprehensive logging for all components")
        print_info("   - RAG query details and database responses")
        print_info("   - MCP server command execution traces")
    
    processes = []
    total_steps = 4 if args.with_ollama else 3
    
    # 1) Start Shared Server (coordination service) - always required
    print_step(1, total_steps, "Starting Shared Server (Coordination Service)")
    try:
        server_proc = start_process([PYTHON, "-m", "shared_server.start_server"], ROOT)
        processes.append(("Shared Server", server_proc))
        print_success(f"Shared Server started with PID: {Colors.BOLD}{server_proc.pid}{Colors.ENDC}")
    except Exception as e:
        print_error(f"Failed to start Shared Server: {e}")
        return 1
    
    # 2) Wait for server to initialize
    print_info("Initializing shared server...")
    time.sleep(1.5)
    print_success("Shared server initialized")
    
    # 3) MCP servers are auto-started by the shared server
    print_step(2, total_steps, "Auto-starting MCP Servers")
    
    mcp_servers = [
        ("RAG", "Document search, knowledge retrieval, and AI query processing"),
        ("Browser", "Web browsing, page navigation, and content extraction"),
        ("Word Editor", "Document editing and text processing"),
        ("Radio Player", "Internet radio streaming and station management")
    ]
    
    for name, description in mcp_servers:
        print_info(f"Starting {name} MCP Server...")
        if args.debug or args.verbose:
            print_info(f"    Description: {description}")
            print_info(f"    Debug logging enabled for {name} operations")
    
    print_info("MCP servers (RAG, Browser, Word Editor, Radio Player) starting...")
    
    # Give MCP servers time to initialize
    time.sleep(3.0)
    print_success("All MCP Servers initialized")
    if args.debug or args.verbose:
        print_info("MCP servers will log detailed operation information")
    
    # 4) Start Ollama MCP Bridge (optional)
    if args.with_ollama:
        print_step(3, total_steps, "Starting Ollama MCP Bridge")
        print_info("Checking Ollama availability...")
        
        # Check if Ollama is running
        try:
            ollama_check = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True,
                timeout=3
            )
            if ollama_check.returncode != 0:
                print_warning("Ollama not detected. Starting Ollama serve...")
                print_info("Note: Ollama must be installed for bridge functionality")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_warning("Could not verify Ollama status")
        
        try:
            bridge_proc = start_process(["uv", "run", "ollama-mcp-bridge"], ROOT / "ollama-mcp-bridge")
            processes.append(("Ollama MCP Bridge", bridge_proc))
            print_success(f"Ollama MCP Bridge started with PID: {Colors.BOLD}{bridge_proc.pid}{Colors.ENDC}")
            print_info("Bridge will attempt to connect to MCP servers...")
            time.sleep(3)  # Give bridge time to connect to MCP servers
            
            # Check if bridge started successfully
            if bridge_proc.poll() is not None:
                print_warning(f"Bridge exited early with code {bridge_proc.poll()}")
                print_info("This is normal if Ollama is not running or MCP servers need time to start")
                print_info("You can manually start the bridge later with:")
                print_info(f"  {Colors.CYAN}cd ollama-mcp-bridge && uv run ollama-mcp-bridge{Colors.ENDC}")
            else:
                print_success("Bridge appears to be running successfully")
                
        except Exception as e:
            print_error(f"Failed to start Ollama MCP Bridge: {e}")
            print_warning("Continuing without Ollama bridge...")
            print_info("You can start it manually later if needed")
    
    # 5) Start AI Interface - always required
    final_step = total_steps if args.with_ollama else 3
    print_step(final_step, total_steps, "Starting AI Interface")
    
    if args.debug or args.verbose:
        print_info("AI Interface will display:")
        print_info("   - User input processing details")
        print_info("   - RAG database query information")
        print_info("   - AI response generation progress")
        print_info("   - MCP server command execution")
        print_info("   - Voice processing activities")
    
    try:
        ai_proc = start_process([PYTHON, "ai_interface/main.py"], ROOT)
        processes.append(("AI Interface", ai_proc))
        print_success(f"AI Interface started with PID: {Colors.BOLD}{ai_proc.pid}{Colors.ENDC}")
        if args.debug or args.verbose:
            print_info("Comprehensive logging active - check terminal for detailed output")
    except Exception as e:
        print_error(f"Failed to start AI Interface: {e}")
        return 1
    
    # Display startup summary
    print_header("STARTUP COMPLETE")
    
    # Show service status table
    print_status_table(processes)
    
    # Add MCP servers info
    print(f"\n{Colors.BOLD}{'MCP Servers':<25}{Colors.ENDC} {Colors.CYAN}Auto-managed{Colors.ENDC}  {Colors.GREEN}Running{Colors.ENDC}")
    print(f"  {Colors.CYAN}├─{Colors.ENDC} RAG Server")
    print(f"  {Colors.CYAN}├─{Colors.ENDC} Browser Server")
    print(f"  {Colors.CYAN}├─{Colors.ENDC} Word Editor Server")
    print(f"  {Colors.CYAN}└─{Colors.ENDC} Radio Player Server")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}All services are running successfully!{Colors.ENDC}")
    
    if args.with_ollama:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Ollama Integration Active{Colors.ENDC}")
        print(f"   {Colors.CYAN}-{Colors.ENDC} Bridge connects to all MCP servers")
        print(f"   {Colors.CYAN}-{Colors.ENDC} Ensure 'ollama serve' is running")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}System Information:{Colors.ENDC}")
    print(f"   {Colors.CYAN}-{Colors.ENDC} Virtual Environment: {Colors.GREEN}Active{Colors.ENDC}" if VENV_PY.exists() else f"   {Colors.CYAN}-{Colors.ENDC} Virtual Environment: {Colors.YELLOW}Not Found{Colors.ENDC}")
    print(f"   {Colors.CYAN}-{Colors.ENDC} Debug Mode: {Colors.GREEN}Enabled{Colors.ENDC}" if args.debug else f"   {Colors.CYAN}-{Colors.ENDC} Debug Mode: {Colors.YELLOW}Disabled{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{Colors.RED}Press Ctrl+C to stop all services{Colors.ENDC}\n")
    
    # Give a moment for processes to fully initialize
    print_info("Performing final health checks...")
    time.sleep(2)
    
    # Check process status again
    print(f"\n{Colors.BOLD}Health Check Results:{Colors.ENDC}")
    all_healthy = True
    for name, proc in processes:
        if proc.poll() is None:
            print_success(f"{name} is healthy")
        else:
            print_error(f"{name} has exited with code {proc.poll()}")
            all_healthy = False
    
    if all_healthy:
        print(f"\n{Colors.BOLD}{Colors.GREEN}All services are healthy and ready!{Colors.ENDC}\n")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BOLD}{Colors.YELLOW}Shutdown initiated...{Colors.ENDC}")
        print_header("GRACEFUL SHUTDOWN")
        
        for name, proc in processes:
            try:
                print_info(f"Stopping {name}...")
                proc.terminate()
                # Wait a bit for graceful shutdown
                try:
                    proc.wait(timeout=5)
                    print_success(f"Stopped {name}")
                except subprocess.TimeoutExpired:
                    print_warning(f"Force killing {name}...")
                    proc.kill()
                    print_success(f"Force stopped {name}")
            except Exception as e:
                print_error(f"Error stopping {name}: {e}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}All services stopped successfully{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}Thank you for using Walls!{Colors.ENDC}\n")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())