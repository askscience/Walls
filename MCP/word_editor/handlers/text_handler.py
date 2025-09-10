"""Text operations handler for Word Editor MCP server."""

import asyncio
import socket
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TextHandler:
    """Handles text operations for the word editor."""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        self.host = host
        self.port = port
    
    async def _send_command(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to the word editor GUI via TCP."""
        import json
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            
            # Send command in JSON format expected by shared server
            command_data = {
                "cmd": command,
                "args": args or {}
            }
            command_json = json.dumps(command_data) + "\n"
            writer.write(command_json.encode())
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
        args = {"text": text}
        result = await self._send_command("set_text", args)
        result.update({
            "operation": "set_text",
            "text_length": len(text)
        })
        return result
    
    async def insert_text(self, position: int, text: str) -> Dict[str, Any]:
        """Insert text at a specific position in the word editor."""
        args = {"position": position, "text": text}
        result = await self._send_command("insert_text", args)
        result.update({
            "operation": "insert_text",
            "position": position,
            "text_length": len(text)
        })
        return result
    
    async def append_text(self, text: str) -> Dict[str, Any]:
        """Append text to the end of the document."""
        args = {"text": text}
        result = await self._send_command("append_text", args)
        result.update({
            "operation": "append_text",
            "text_length": len(text)
        })
        return result
    
    async def get_text(self) -> Dict[str, Any]:
        """Get the current text content from the word editor."""
        result = await self._send_command("get_text")
        result["operation"] = "get_text"
        
        if result["success"]:
            # The response should contain the current text
            result["text"] = result.get("response", "")
            result["text_length"] = len(result["text"])
        
        return result