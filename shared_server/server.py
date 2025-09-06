"""Shared TCP server for Walls applications.

Provides a centralized server that multiple applications can register with
and receive CLI commands through a unified interface.
"""

import json
import socket
import threading
import time
from pathlib import Path
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass
import tempfile
import logging

from .config import ServerConfig, get_config
from .mcp_manager import MCPManager


@dataclass
class AppRegistration:
    """Registration information for an application."""
    name: str
    port: int
    command_handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]
    description: str = ""
    active: bool = True


class SharedServer:
    """Centralized TCP server for multiple Walls applications."""
    
    def __init__(self, base_port: int = 9000, max_apps: int = 10, config_path: Optional[str] = None):
        self.base_port = base_port
        self.max_apps = max_apps
        self.config = ServerConfig(config_path)
        self.mcp_manager = MCPManager(self.config)
        self.apps: Dict[str, AppRegistration] = {}
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.server_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Create temp directory for port files
        self.temp_dir = Path(tempfile.gettempdir()) / "walls_shared_server"
        self.temp_dir.mkdir(exist_ok=True)
        
    def register_app(self, name: str, command_handler: Callable[[str, Dict[str, Any]], Dict[str, Any]], 
                    description: str = "") -> int:
        """Register an application with the shared server.
        
        Args:
            name: Unique name for the application
            command_handler: Function to handle commands for this app
            description: Optional description of the app
            
        Returns:
            Port number assigned to the application
            
        Raises:
            ValueError: If app name already exists or max apps reached
        """
        with self.lock:
            if name in self.apps:
                raise ValueError(f"Application '{name}' is already registered")
                
            if len(self.apps) >= self.max_apps:
                raise ValueError(f"Maximum number of applications ({self.max_apps}) reached")
                
            # Find next available port
            port = self.base_port + len(self.apps)
            
            # Ensure port is available
            while self._is_port_in_use(port) and port < self.base_port + 100:
                port += 1
                
            if port >= self.base_port + 100:
                raise ValueError("No available ports found")
                
            self.apps[name] = AppRegistration(
                name=name,
                port=port,
                command_handler=command_handler,
                description=description
            )
            
            # Write port file for CLI clients
            port_file = self.temp_dir / f"{name}_port"
            port_file.write_text(str(port))

            # Save app config
            config = get_config()
            config.set_app_port(name, port)
            config.set_app_description(name, description)
            config.save_config()
            
            # Auto-start the server if not running
            if not self.running:
                self.start()
            
            self.logger.info(f"Registered app '{name}' on port {port}")
            return port
            
    def unregister_app(self, name: str) -> bool:
        """Unregister an application.
        
        Args:
            name: Name of the application to unregister
            
        Returns:
            True if app was unregistered, False if not found
        """
        with self.lock:
            if name not in self.apps:
                return False
                
            # Remove port file
            port_file = self.temp_dir / f"{name}_port"
            if port_file.exists():
                port_file.unlink()
                
            del self.apps[name]
            self.logger.info(f"Unregistered app '{name}'")
            return True
            
    def start(self) -> bool:
        """Start the shared server.
        
        Returns:
            True if server started successfully, False otherwise
        """
        if self.running:
            return True
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Mark server as running BEFORE starting app threads to avoid race condition
            self.running = True
            
            # Start individual app servers
            for app in self.apps.values():
                self._start_app_server(app)
            
            # Auto-start MCP servers if enabled in configuration
            server_config = self.config.get_server_config()
            auto_start_mcp = server_config.get('auto_start_mcp', False)
            print(f"DEBUG: Server config auto_start_mcp: {auto_start_mcp}")
            print(f"DEBUG: Full server config: {server_config}")
            
            if auto_start_mcp:
                print("DEBUG: Auto-starting enabled MCP servers...")
                mcp_results = self.start_all_mcp_servers()
                print(f"DEBUG: MCP start results: {mcp_results}")
                started_servers = [name for name, success in mcp_results.items() if success]
                if started_servers:
                    print(f"DEBUG: Started MCP servers: {', '.join(started_servers)}")
                failed_servers = [name for name, success in mcp_results.items() if not success]
                if failed_servers:
                    print(f"DEBUG: Failed to start MCP servers: {', '.join(failed_servers)}")
            else:
                print("DEBUG: MCP auto-start is disabled in configuration")
                
            self.logger.info("Shared server started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start shared server: {e}")
            return False
            
    def stop(self):
        """Stop the shared server."""
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
        # Clean up MCP servers
        self.mcp_manager.cleanup()
            
        # Clean up port files
        for app_name in list(self.apps.keys()):
            port_file = self.temp_dir / f"{app_name}_port"
            if port_file.exists():
                port_file.unlink()
                
        self.logger.info("Shared server stopped")
        
    # MCP Server Management Methods
    def start_mcp_server(self, server_name: str) -> bool:
        """Start an MCP server."""
        return self.mcp_manager.start_server(server_name)
    
    def stop_mcp_server(self, server_name: str) -> bool:
        """Stop an MCP server."""
        return self.mcp_manager.stop_server(server_name)
    
    def restart_mcp_server(self, server_name: str) -> bool:
        """Restart an MCP server."""
        return self.mcp_manager.restart_server(server_name)
    
    def get_mcp_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get the status of an MCP server."""
        return self.mcp_manager.get_server_status(server_name)
    
    def get_all_mcp_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP servers."""
        return self.mcp_manager.get_all_status()
    
    def enable_mcp_server(self, server_name: str) -> bool:
        """Enable an MCP server."""
        return self.mcp_manager.enable_server(server_name)
    
    def disable_mcp_server(self, server_name: str) -> bool:
        """Disable an MCP server."""
        return self.mcp_manager.disable_server(server_name)
    
    def start_all_mcp_servers(self) -> Dict[str, bool]:
        """Start all enabled MCP servers."""
        return self.mcp_manager.start_all_enabled()
    
    def stop_all_mcp_servers(self) -> Dict[str, bool]:
        """Stop all MCP servers."""
        return self.mcp_manager.stop_all()
        
    def _start_app_server(self, app: AppRegistration):
        """Start a TCP server for a specific app."""
        def server_thread():
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                server_sock.bind(('127.0.0.1', app.port))
                server_sock.listen(5)
                server_sock.settimeout(1.0)  # Allow periodic checks for shutdown
                
                self.logger.info(f"App server for '{app.name}' listening on port {app.port}")
                
                while self.running and app.active:
                    try:
                        client_sock, addr = server_sock.accept()
                        # Handle client in a separate thread
                        client_thread = threading.Thread(
                            target=self._handle_client,
                            args=(client_sock, app),
                            daemon=True
                        )
                        client_thread.start()
                        
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            self.logger.error(f"Error accepting connection for {app.name}: {e}")
                        break
                        
            except Exception as e:
                self.logger.error(f"Failed to start server for {app.name}: {e}")
            finally:
                server_sock.close()
                
        thread = threading.Thread(target=server_thread, daemon=True)
        thread.start()
        
    def _handle_client(self, client_sock: socket.socket, app: AppRegistration):
        """Handle a client connection for a specific app."""
        try:
            with client_sock:
                client_sock.settimeout(5.0)
                
                # Read the command
                data = b""
                try:
                    while True:
                        chunk = client_sock.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                        if b"\n" in chunk:
                            break
                except socket.timeout:
                    self.logger.warning(f"Timeout receiving data from client for {app.name}")
                    return

                    
                if not data:
                    return
                    
                # Parse command
                try:
                    command_str = data.decode('utf-8').strip()
                    command_data = json.loads(command_str)
                    
                    cmd = command_data.get('cmd') or command_data.get('command')
                    args = command_data.get('args') or command_data.get('data', {})
                    
                    if not cmd:
                        response = {'status': 'error', 'message': 'No command specified'}
                    else:
                        # Call the app's command handler
                        response = app.command_handler(cmd, args)
                        
                except json.JSONDecodeError as e:
                    response = {'status': 'error', 'message': f'Invalid JSON: {e}'}
                except Exception as e:
                    response = {'status': 'error', 'message': f'Command error: {e}'}
                    
                # Send response
                response_str = json.dumps(response) + "\n"
                client_sock.sendall(response_str.encode('utf-8'))
                
        except Exception as e:
            self.logger.error(f"Error handling client for {app.name}: {e}")
            
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except OSError:
                return True
                
    def get_app_info(self) -> List[Dict[str, Any]]:
        """Get information about registered applications."""
        with self.lock:
            return [
                {
                    'name': app.name,
                    'port': app.port,
                    'description': app.description,
                    'active': app.active
                }
                for app in self.apps.values()
            ]
            
    def get_app_port(self, name: str) -> Optional[int]:
        """Get the port number for a specific app."""
        with self.lock:
            app = self.apps.get(name)
            return app.port if app else None


# Global shared server instance
_shared_server: Optional[SharedServer] = None


def get_shared_server() -> SharedServer:
    """Get the global shared server instance."""
    global _shared_server
    if _shared_server is None:
        _shared_server = SharedServer()
    return _shared_server


def start_shared_server() -> bool:
    """Start the global shared server."""
    return get_shared_server().start()


def stop_shared_server():
    """Stop the global shared server."""
    server = get_shared_server()
    server.stop()