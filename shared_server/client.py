"""Client utilities for connecting to the shared server."""

import json
import socket
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile


class ServerClient:
    """Client for communicating with the shared server."""
    
    def __init__(self, app_name: str, host: str = '127.0.0.1', timeout: float = 5.0):
        self.app_name = app_name
        self.host = host
        self.timeout = timeout
        self.temp_dir = Path(tempfile.gettempdir()) / "walls_shared_server"
        
    def get_app_port(self) -> int:
        """Get the port number for this app from the port file."""
        port_file = self.temp_dir / f"{self.app_name}_port"
        
        if not port_file.exists():
            # Fallback to default ports for backward compatibility (only for known legacy apps)
            defaults = {
                'radio_player': 9999,
                'words': 8765
            }
            if self.app_name in defaults:
                return defaults[self.app_name]
            # No port file and no legacy default: app is not registered yet
            raise RuntimeError(f"Port file for app '{self.app_name}' not found")
            
        try:
            return int(port_file.read_text().strip())
        except (ValueError, IOError):
            raise RuntimeError(f"Failed to read port for app '{self.app_name}'")
            
    def send_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a command to the app server.
        
        Args:
            command: The command to send
            args: Optional arguments for the command
            
        Returns:
            Response dictionary from the server
            
        Raises:
            ConnectionError: If unable to connect to server
            RuntimeError: If communication fails
        """
        port = self.get_app_port()
        
        try:
            with socket.create_connection((self.host, port), timeout=self.timeout) as sock:
                # Send command
                command_data = {
                    'cmd': command,
                    'args': args or {}
                }
                message = json.dumps(command_data) + '\n'
                sock.sendall(message.encode('utf-8'))
                
                # Receive response
                response_data = b''
                while b'\n' not in response_data:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    
                if not response_data:
                    raise RuntimeError("No response received from server")
                    
                response_str = response_data.decode('utf-8').strip()
                return json.loads(response_str)
                
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.app_name} server on port {port}: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid response from server: {e}")
            
    def is_server_running(self) -> bool:
        """Check if the app server is running."""
        try:
            port = self.get_app_port()
            with socket.create_connection((self.host, port), timeout=1.0):
                return True
        except (socket.error, RuntimeError):
            return False


def send_command_to_app(app_name: str, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to send a command to an app.
    
    Args:
        app_name: Name of the target application
        command: Command to send
        args: Optional command arguments
        
    Returns:
        Response from the app server
    """
    client = ServerClient(app_name)
    return client.send_command(command, args)


def is_app_running(app_name: str) -> bool:
    """Check if an app server is running.
    
    Args:
        app_name: Name of the application to check
        
    Returns:
        True if the app server is running, False otherwise
    """
    client = ServerClient(app_name)
    return client.is_server_running()