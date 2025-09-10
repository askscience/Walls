"""CLI operations handler for Word Editor MCP server."""

import asyncio
import socket
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CLIHandler:
    """Handles CLI operations for the word editor."""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        self.host = host
        self.port = port
    
    async def _send_command(self, command: str) -> Dict[str, Any]:
        """Send a command to the word editor GUI via TCP."""
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            
            # Send command
            writer.write(command.encode() + b'\n')
            await writer.drain()
            
            # Read response
            response = await reader.readline()
            writer.close()
            await writer.wait_closed()
            
            response_text = response.decode().strip()
            logger.info(f"Command '{command}' response: {response_text}")
            
            return {
                "success": True,
                "response": response_text,
                "command": command
            }
            
        except Exception as e:
            logger.error(f"Failed to send command '{command}': {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    async def send_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Send a raw command to the word editor CLI."""
        if args is None:
            args = []
        
        # Build full command string
        if args:
            # Escape arguments that contain spaces
            escaped_args = []
            for arg in args:
                if ' ' in arg or '"' in arg:
                    escaped_arg = '"' + arg.replace('"', '\\"') + '"'
                    escaped_args.append(escaped_arg)
                else:
                    escaped_args.append(arg)
            
            full_command = f"{command} {' '.join(escaped_args)}"
        else:
            full_command = command
        
        result = await self._send_command(full_command)
        result["operation"] = "send_command"
        result["original_command"] = command
        result["args"] = args
        
        return result
    
    async def check_status(self) -> Dict[str, Any]:
        """Check if the word editor GUI is running and accessible."""
        try:
            # Try to connect to the TCP server
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5.0
            )
            
            # Send a simple status command
            writer.write(b'status\n')
            await writer.drain()
            
            # Read response with timeout
            response = await asyncio.wait_for(
                reader.readline(),
                timeout=5.0
            )
            
            writer.close()
            await writer.wait_closed()
            
            response_text = response.decode().strip()
            
            return {
                "success": True,
                "operation": "check_status",
                "status": "running",
                "host": self.host,
                "port": self.port,
                "response": response_text,
                "message": "Word editor GUI is running and accessible"
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "operation": "check_status",
                "status": "timeout",
                "host": self.host,
                "port": self.port,
                "error": "Connection timeout - GUI may be unresponsive",
                "message": "Word editor GUI connection timed out"
            }
            
        except ConnectionRefusedError:
            return {
                "success": False,
                "operation": "check_status",
                "status": "not_running",
                "host": self.host,
                "port": self.port,
                "error": "Connection refused - GUI is not running",
                "message": "Word editor GUI is not running. Start it with: python python_gui/main.py"
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "check_status",
                "status": "error",
                "host": self.host,
                "port": self.port,
                "error": str(e),
                "message": f"Error checking word editor GUI status: {e}"
            }
    
    async def get_available_commands(self) -> Dict[str, Any]:
        """Get list of available CLI commands."""
        # Send help command to get available commands
        result = await self._send_command("help")
        result["operation"] = "get_available_commands"
        
        if result["success"]:
            # Parse the help response to extract commands
            help_text = result.get("response", "")
            
            # Basic command list based on the word editor CLI
            commands = [
                "set_text <text>",
                "insert_text <position> <text>", 
                "append_text <text>",
                "get_text",
                "open <file_path>",
                "save [file_path]",
                "status",
                "help"
            ]
            
            result["available_commands"] = commands
            result["help_text"] = help_text
        
        return result