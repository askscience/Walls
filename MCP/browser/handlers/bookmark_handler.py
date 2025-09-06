"""Bookmark operations handler for Browser MCP server."""

import asyncio
import json
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BookmarkHandler:
    """Handles bookmark operations for the browser."""
    
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
    
    async def add_bookmark(self, url: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Add a bookmark for the current page or specified URL."""
        command_args = ["bookmark_add"]
        
        if url:
            command_args.append(f"url={url}")
        
        if name:
            command_args.append(f"name={name}")
        
        result = await self._run_command(command_args)
        result["operation"] = "add_bookmark"
        
        if url:
            result["url"] = url
        if name:
            result["name"] = name
        
        return result
    
    async def get_bookmarks(self) -> Dict[str, Any]:
        """Get all bookmarks as JSON."""
        result = await self._run_command(["bookmarks_json"])
        result["operation"] = "get_bookmarks"
        
        if result["success"]:
            try:
                # Parse the JSON output to validate it
                bookmarks_data = json.loads(result["output"])
                result["bookmarks"] = bookmarks_data
                result["bookmark_count"] = len(bookmarks_data) if isinstance(bookmarks_data, list) else 0
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse bookmarks JSON: {e}")
                result["raw_output"] = result["output"]
                result["parse_error"] = str(e)
        
        return result
    
    async def remove_bookmark(self, url: str) -> Dict[str, Any]:
        """Remove a bookmark by URL."""
        # This functionality would need to be implemented in the browser app
        return {
            "success": False,
            "error": "remove_bookmark not implemented in browser app",
            "operation": "remove_bookmark",
            "url": url,
            "message": "This feature would need to be added to the browser shared_server integration"
        }
    
    async def search_bookmarks(self, query: str) -> Dict[str, Any]:
        """Search bookmarks by name or URL."""
        # Get all bookmarks first
        bookmarks_result = await self.get_bookmarks()
        
        if not bookmarks_result["success"]:
            return {
                "success": False,
                "error": "Failed to retrieve bookmarks for search",
                "operation": "search_bookmarks",
                "query": query
            }
        
        try:
            bookmarks = bookmarks_result.get("bookmarks", [])
            
            # Filter bookmarks based on query
            matching_bookmarks = []
            query_lower = query.lower()
            
            for bookmark in bookmarks:
                if isinstance(bookmark, dict):
                    name = bookmark.get("name", "").lower()
                    url = bookmark.get("url", "").lower()
                    
                    if query_lower in name or query_lower in url:
                        matching_bookmarks.append(bookmark)
            
            return {
                "success": True,
                "operation": "search_bookmarks",
                "query": query,
                "results": matching_bookmarks,
                "result_count": len(matching_bookmarks)
            }
            
        except Exception as e:
            logger.error(f"Error searching bookmarks: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "search_bookmarks",
                "query": query
            }