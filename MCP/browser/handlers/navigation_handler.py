"""Navigation operations handler for Browser MCP server."""

import asyncio
import subprocess
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class NavigationHandler:
    """Handles navigation operations for the browser."""
    
    def __init__(self):
        self.base_command = [
            "python", "-m", "shared_server.cli", "send", "browser"
        ]
    
    def _get_base_path(self):
        """Get the base path dynamically - go up 3 levels from MCP/browser/handlers/"""
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    async def _run_command(self, command_args: list) -> Dict[str, Any]:
        """Run a shared_server CLI command for browser operations."""
        try:
            full_command = self.base_command + command_args
            logger.info(f"Running command: {' '.join(full_command)}")
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self._get_base_path()
            )
            
            stdout, stderr = await process.communicate()
            
            stdout_text = stdout.decode().strip()
            stderr_text = stderr.decode().strip()
            
            if process.returncode == 0:
                logger.info(f"Command successful: {stdout_text}")
                return {
                    "success": True,
                    "output": stdout_text,
                    "command": command_args
                }
            else:
                logger.error(f"Command failed: {stderr_text}")
                return {
                    "success": False,
                    "error": stderr_text,
                    "output": stdout_text,
                    "command": command_args,
                    "return_code": process.returncode
                }
                
        except Exception as e:
            logger.error(f"Failed to run command {command_args}: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command_args
            }
    
    async def open_url(self, url: str) -> Dict[str, Any]:
        """Open a webpage in the browser."""
        if not url:
            return {
                "success": False,
                "error": "URL is required",
                "operation": "open_url"
            }
        
        # Add https:// if no scheme provided
        if not url.startswith(("http://", "https://", "file://")):
            url = f"https://{url}"
        
        result = await self._run_command(["open", f"url={url}"])
        result["operation"] = "open_url"
        result["url"] = url
        
        return result
    
    async def navigate_back(self) -> Dict[str, Any]:
        """Navigate back in browser history."""
        result = await self._run_command(["back"])
        result["operation"] = "navigate_back"
        
        return result
    
    async def navigate_forward(self) -> Dict[str, Any]:
        """Navigate forward in browser history."""
        result = await self._run_command(["forward"])
        result["operation"] = "navigate_forward"
        
        return result
    
    async def reload_page(self) -> Dict[str, Any]:
        """Reload the current page."""
        result = await self._run_command(["reload"])
        result["operation"] = "reload_page"
        
        return result
    
    async def get_current_url(self) -> Dict[str, Any]:
        """Get the current page URL (if supported by browser)."""
        # This would need to be implemented in the browser app
        # For now, return a placeholder
        return {
            "success": False,
            "error": "get_current_url not implemented in browser app",
            "operation": "get_current_url",
            "message": "This feature would need to be added to the browser shared_server integration"
        }