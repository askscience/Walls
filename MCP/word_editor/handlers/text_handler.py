"""Text operations handler for Word Editor MCP server."""

import asyncio
import socket
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TextHandler:
    """Handles text operations for the word editor."""
    
    def __init__(self, host: str = "localhost", port: int = 9998):
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
    
    async def set_text(self, text: str) -> Dict[str, Any]:
        """Set the entire text content in the word editor."""
        # Escape quotes and newlines for command
        escaped_text = text.replace('"', '\\"').replace('\n', '\\n')
        command = f'set_text "{escaped_text}"'
        
        result = await self._send_command(command)
        result["operation"] = "set_text"
        result["text_length"] = len(text)
        
        return result
    
    async def insert_text(self, position: int, text: str) -> Dict[str, Any]:
        """Insert text at a specific position in the word editor."""
        # Escape quotes and newlines for command
        escaped_text = text.replace('"', '\\"').replace('\n', '\\n')
        command = f'insert_text {position} "{escaped_text}"'
        
        result = await self._send_command(command)
        result["operation"] = "insert_text"
        result["position"] = position
        result["text_length"] = len(text)
        
        return result
    
    async def append_text(self, text: str) -> Dict[str, Any]:
        """Append text to the end of the current content."""
        # Escape quotes and newlines for command
        escaped_text = text.replace('"', '\\"').replace('\n', '\\n')
        command = f'append_text "{escaped_text}"'
        
        result = await self._send_command(command)
        result["operation"] = "append_text"
        result["text_length"] = len(text)
        
        return result
    
    async def get_text(self) -> Dict[str, Any]:
        """Get the current text content from the word editor."""
        command = "get_text"
        
        result = await self._send_command(command)
        result["operation"] = "get_text"
        
        if result["success"]:
            # The response should contain the current text
            result["text"] = result.get("response", "")
            result["text_length"] = len(result["text"])
        
        return result