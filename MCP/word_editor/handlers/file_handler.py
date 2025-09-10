"""File operations handler for Word Editor MCP server."""

import asyncio
import os
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FileHandler:
    """Handles file operations for the word editor."""
    
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
    
    async def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open a file in the word editor."""
        # Validate file path
        if not file_path:
            return {
                "success": False,
                "error": "File path is required",
                "operation": "open_file"
            }
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File does not exist: {file_path}",
                "operation": "open_file",
                "file_path": file_path
            }
        
        # Send open command
        command = f'open "{file_path}"'
        result = await self._send_command(command)
        result["operation"] = "open_file"
        result["file_path"] = file_path
        
        if result["success"]:
            try:
                # Get file info
                stat = os.stat(file_path)
                result["file_info"] = {
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "readable": os.access(file_path, os.R_OK),
                    "writable": os.access(file_path, os.W_OK)
                }
            except Exception as e:
                logger.warning(f"Could not get file info for {file_path}: {e}")
        
        return result
    
    async def save_file(self, file_path: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """Save the current content to a file."""
        if file_path:
            # Save to specific file
            command = f'save "{file_path}"'
            operation_type = "save_as"
        else:
            # Save to current file
            command = "save"
            operation_type = "save"
        
        result = await self._send_command(command)
        result["operation"] = operation_type
        
        if file_path:
            result["file_path"] = file_path
            
            # If save was successful and we have the file path, get file info
            if result["success"] and os.path.exists(file_path):
                try:
                    stat = os.stat(file_path)
                    result["file_info"] = {
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "readable": os.access(file_path, os.R_OK),
                        "writable": os.access(file_path, os.W_OK)
                    }
                except Exception as e:
                    logger.warning(f"Could not get file info for {file_path}: {e}")
        
        return result
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file."""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}",
                    "operation": "get_file_info",
                    "file_path": file_path
                }
            
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "operation": "get_file_info",
                "file_path": file_path,
                "file_info": {
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "readable": os.access(file_path, os.R_OK),
                    "writable": os.access(file_path, os.W_OK),
                    "is_file": os.path.isfile(file_path),
                    "is_directory": os.path.isdir(file_path)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "get_file_info",
                "file_path": file_path
            }