"""Adblock operations handler for Browser MCP server."""

import asyncio
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AdblockHandler:
    """Handles adblock operations for the browser."""
    
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
    
    async def enable_adblock(self) -> Dict[str, Any]:
        """Enable adblock functionality."""
        result = await self._run_command(["adblock_enable"])
        result["operation"] = "enable_adblock"
        
        return result
    
    async def disable_adblock(self) -> Dict[str, Any]:
        """Disable adblock functionality."""
        result = await self._run_command(["adblock_disable"])
        result["operation"] = "disable_adblock"
        
        return result
    
    async def toggle_adblock(self) -> Dict[str, Any]:
        """Toggle adblock on/off."""
        result = await self._run_command(["adblock_toggle"])
        result["operation"] = "toggle_adblock"
        
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current adblock status."""
        result = await self._run_command(["adblock_status"])
        result["operation"] = "get_adblock_status"
        
        if result["success"]:
            # Parse status from output
            output = result["output"].lower()
            if "enabled" in output:
                result["adblock_enabled"] = True
                result["status"] = "enabled"
            elif "disabled" in output:
                result["adblock_enabled"] = False
                result["status"] = "disabled"
            else:
                result["status"] = "unknown"
                result["adblock_enabled"] = None
        
        return result
    
    async def load_rules(self, path: str, is_directory: bool = False) -> Dict[str, Any]:
        """Load adblock rules from file or directory."""
        if not path:
            return {
                "success": False,
                "error": "Path is required",
                "operation": "load_adblock_rules"
            }
        
        if is_directory:
            command_args = ["adblock_load_dir", f"path={path}"]
        else:
            command_args = ["adblock_load", f"path={path}"]
        
        result = await self._run_command(command_args)
        result["operation"] = "load_adblock_rules"
        result["path"] = path
        result["is_directory"] = is_directory
        
        return result
    
    async def fetch_easylist(self, url: Optional[str] = None) -> Dict[str, Any]:
        """Download and load EasyList rules."""
        command_args = ["adblock_fetch_easylist"]
        
        if url:
            command_args.append(f"url={url}")
        
        result = await self._run_command(command_args)
        result["operation"] = "fetch_easylist"
        
        if url:
            result["url"] = url
        else:
            result["url"] = "default (EasyList GitHub master)"
        
        return result
    
    async def clear_rules(self) -> Dict[str, Any]:
        """Clear all loaded adblock rules."""
        # This functionality would need to be implemented in the browser app
        return {
            "success": False,
            "error": "clear_rules not implemented in browser app",
            "operation": "clear_adblock_rules",
            "message": "This feature would need to be added to the browser shared_server integration"
        }
    
    async def get_rule_count(self) -> Dict[str, Any]:
        """Get the number of loaded adblock rules."""
        # This functionality would need to be implemented in the browser app
        return {
            "success": False,
            "error": "get_rule_count not implemented in browser app",
            "operation": "get_rule_count",
            "message": "This feature would need to be added to the browser shared_server integration"
        }
    
    async def test_url(self, url: str) -> Dict[str, Any]:
        """Test if a URL would be blocked by current adblock rules."""
        # This functionality would need to be implemented in the browser app
        return {
            "success": False,
            "error": "test_url not implemented in browser app",
            "operation": "test_url",
            "url": url,
            "message": "This feature would need to be added to the browser shared_server integration"
        }