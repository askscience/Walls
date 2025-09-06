"""Page operations handler for Browser MCP server."""

import asyncio
import json
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class PageHandler:
    """Handles page interaction operations for the browser."""
    
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
    
    async def click_element(self, selector: str) -> Dict[str, Any]:
        """Click an element using CSS selector."""
        if not selector:
            return {
                "success": False,
                "error": "CSS selector is required",
                "operation": "click_element"
            }
        
        result = await self._run_command(["click", f"selector={selector}"])
        result["operation"] = "click_element"
        result["selector"] = selector
        
        return result
    
    async def click_text(self, text: str) -> Dict[str, Any]:
        """Click a link/button by visible text."""
        if not text:
            return {
                "success": False,
                "error": "Text is required",
                "operation": "click_text"
            }
        
        result = await self._run_command(["click_text", f"text={text}"])
        result["operation"] = "click_text"
        result["text"] = text
        
        return result
    
    async def get_page_html(self) -> Dict[str, Any]:
        """Get the current page HTML content."""
        result = await self._run_command(["get_html_sync"])
        result["operation"] = "get_page_html"
        
        if result["success"]:
            try:
                # Parse the JSON response to extract HTML
                response_data = json.loads(result["output"])
                if isinstance(response_data, dict) and "data" in response_data:
                    html_content = response_data["data"].get("html", "")
                    result["html"] = html_content
                    result["html_length"] = len(html_content)
                else:
                    result["html"] = result["output"]
                    result["html_length"] = len(result["output"])
            except json.JSONDecodeError:
                # If not JSON, treat as raw HTML
                result["html"] = result["output"]
                result["html_length"] = len(result["output"])
        
        return result
    
    async def summarize_page(self) -> Dict[str, Any]:
        """Get a JSON summary of the current page with title, content, and links."""
        result = await self._run_command(["summarize"])
        result["operation"] = "summarize_page"
        
        if result["success"]:
            try:
                # Parse the JSON summary
                summary_data = json.loads(result["output"])
                result["summary"] = summary_data
                
                # Extract key information
                if isinstance(summary_data, dict):
                    result["title"] = summary_data.get("title", "")
                    result["content_excerpt"] = summary_data.get("content", "")
                    result["links"] = summary_data.get("links", [])
                    result["link_count"] = len(result["links"])
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse page summary JSON: {e}")
                result["raw_output"] = result["output"]
                result["parse_error"] = str(e)
        
        return result
    
    async def get_page_title(self) -> Dict[str, Any]:
        """Get the current page title."""
        # Use summarize to get title information
        summary_result = await self.summarize_page()
        
        if summary_result["success"] and "title" in summary_result:
            return {
                "success": True,
                "operation": "get_page_title",
                "title": summary_result["title"]
            }
        else:
            return {
                "success": False,
                "error": "Failed to get page title",
                "operation": "get_page_title",
                "details": summary_result.get("error", "Unknown error")
            }
    
    async def find_elements(self, selector: str) -> Dict[str, Any]:
        """Find elements by CSS selector (would need browser app support)."""
        return {
            "success": False,
            "error": "find_elements not implemented in browser app",
            "operation": "find_elements",
            "selector": selector,
            "message": "This feature would need to be added to the browser shared_server integration"
        }
    
    async def get_page_links(self) -> Dict[str, Any]:
        """Get all links from the current page."""
        # Use summarize to get links information
        summary_result = await self.summarize_page()
        
        if summary_result["success"] and "links" in summary_result:
            return {
                "success": True,
                "operation": "get_page_links",
                "links": summary_result["links"],
                "link_count": summary_result.get("link_count", 0)
            }
        else:
            return {
                "success": False,
                "error": "Failed to get page links",
                "operation": "get_page_links",
                "details": summary_result.get("error", "Unknown error")
            }