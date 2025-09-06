#!/usr/bin/env python3
"""Script to start the shared server."""

import sys
import os
import subprocess
import signal
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_server.server import start_shared_server, get_shared_server

def cleanup_old_processes():
    """Kill all old shared_server and radio_player processes and clean temp configs."""
    try:
        # Find and kill old shared_server processes
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        pids_to_kill = []
        current_pid = os.getpid()
        
        for line in result.stdout.split('\n'):
            if 'shared_server.start_server' in line or 'radio_player.modern_gui' in line:
                parts = line.split()
                if len(parts) > 1:
                    try:
                        pid = int(parts[1])
                        if pid != current_pid:  # Don't kill ourselves
                            pids_to_kill.append(pid)
                    except ValueError:
                        continue
            # Only kill start_all.py if it's not the parent process
            elif 'start_all.py' in line:
                parts = line.split()
                if len(parts) > 1:
                    try:
                        pid = int(parts[1])
                        # Check if this is a parent process by looking at PPID
                        if pid != current_pid and pid != os.getppid():
                            pids_to_kill.append(pid)
                    except ValueError:
                        continue
        
        # Kill the processes
        for pid in pids_to_kill:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Killed old process: {pid}")
            except ProcessLookupError:
                # Process already dead
                pass
            except PermissionError:
                print(f"Permission denied killing process: {pid}")
        
        # Clean up temporary config directories
        import tempfile
        import shutil
        temp_dir = Path(tempfile.gettempdir()) / "walls_shared_server"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary config directory: {temp_dir}")
                
    except Exception as e:
        print(f"Error during cleanup: {e}")

def pre_allocate_ports():
    """Pre-allocate ports for known applications and create port files."""
    from shared_server.config import get_config
    import tempfile
    
    config = get_config()
    temp_dir = Path(tempfile.gettempdir()) / "walls_shared_server"
    temp_dir.mkdir(exist_ok=True)
    
    # Get app ports from config (use config defaults)
    app_ports = {
        "radio_player": config.get_app_port("radio_player") or 9999,
        "browser": config.get_app_port("browser") or 9002, 
        "word_editor": config.get_app_port("word_editor") or 9003
    }
    
    # Create port files immediately so apps can detect available ports
    for app_name, port in app_ports.items():
        port_file = temp_dir / f"{app_name}_port"
        port_file.write_text(str(port))
        print(f"Pre-allocated port {port} for {app_name}")
        
        # Update config
        config.set_app_port(app_name, port)
        config.set_app_description(app_name, f"{app_name.replace('_', ' ').title()} Application")
    
    config.save_config()
    return app_ports

def launch_applications(app_ports):
    """Launch applications after ports are pre-allocated."""
    workspace = Path(__file__).parent.parent
    venv_python = workspace / "venv" / "bin" / "python"
    
    # Applications to launch with their commands
    apps = [
        ("radio_player", f"{venv_python} -m radio_player.modern_gui"),
        ("browser", f"{venv_python} -m browser.main"),
        ("word_editor", f"{venv_python} -m Words.word_editor.python_gui.main")
    ]
    
    with open(os.devnull, 'w') as devnull:
        for app_name, command in apps:
            try:
                print(f"Launching {app_name} on port {app_ports[app_name]}...")
                subprocess.Popen(command, shell=True, cwd=workspace, 
                               stdout=devnull, stderr=devnull)
            except Exception as e:
                print(f"Failed to launch {app_name}: {e}")

def main():
    print("Starting Walls shared server...")
    
    # Clean up old processes first
    print("Cleaning up old processes...")
    cleanup_old_processes()
    
    # Pre-allocate ports first
    print("Pre-allocating ports for applications...")
    app_ports = pre_allocate_ports()
    
    server = get_shared_server()
    if server.start():
        print("Shared server started successfully")
        
        # Applications will be launched on-demand by the AI interface
        # when CLI commands are executed that require them
        print("Server ready - applications will start on-demand")
        
        try:
            # Keep the server running
            while server.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down shared server...")
            server.stop()
    else:
        print("Failed to start shared server")
        sys.exit(1)

if __name__ == "__main__":
    main()