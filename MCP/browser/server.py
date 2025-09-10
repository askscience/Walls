"""Browser MCP server using FastMCP."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from handlers.navigation_handler import NavigationHandler
from handlers.bookmark_handler import BookmarkHandler

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_launcher import ensure_browser_running
from handlers.page_handler import PageHandler
from handlers.adblock_handler import AdblockHandler
from utils.logger import setup_logger
from schemas.tool_schemas import TOOL_SCHEMAS

# Setup logging
logger = setup_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("browser")

# Initialize handlers
navigation_handler = NavigationHandler()
bookmark_handler = BookmarkHandler()
page_handler = PageHandler()
adblock_handler = AdblockHandler()

async def ensure_browser_running_wrapper():
    """Ensure browser is running and return launch result."""
    try:
        launch_result = await ensure_browser_running()
        if not launch_result['success']:
            logger.error(f"Failed to ensure browser is running: {launch_result.get('error')}")
            return {
                "success": False,
                "error": f"Browser application not available: {launch_result.get('error')}"
            }
        
        if launch_result.get('launched'):
            logger.info("Browser launched successfully")
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error ensuring browser is running: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Navigation tools
@mcp.tool()
async def open_url(url: str) -> dict:
    """Open a webpage in the browser."""
    logger.info(f"Opening URL: {url}")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await navigation_handler.open_url(url)
    except Exception as e:
        logger.error(f"Error in open_url: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def navigate_back() -> dict:
    """Navigate back in browser history."""
    logger.info("Navigating back")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await navigation_handler.navigate_back()
    except Exception as e:
        logger.error(f"Error in navigate_back: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def navigate_forward() -> dict:
    """Navigate forward in browser history."""
    logger.info("Navigating forward")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await navigation_handler.navigate_forward()
    except Exception as e:
        logger.error(f"Error in navigate_forward: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def reload_page() -> dict:
    """Reload the current page."""
    logger.info("Reloading page")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await navigation_handler.reload_page()
    except Exception as e:
        logger.error(f"Error in reload_page: {str(e)}")
        return {"success": False, "error": str(e)}

# Bookmark tools
@mcp.tool()
async def add_bookmark(url: Optional[str] = None, name: Optional[str] = None) -> dict:
    """Add a bookmark for the current page or specified URL."""
    logger.info(f"Adding bookmark: {name} -> {url}")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await bookmark_handler.add_bookmark(url, name)
    except Exception as e:
        logger.error(f"Error in add_bookmark: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_bookmarks() -> dict:
    """Get all bookmarks as JSON."""
    logger.info("Getting bookmarks")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await bookmark_handler.get_bookmarks()
    except Exception as e:
        logger.error(f"Error in get_bookmarks: {str(e)}")
        return {"success": False, "error": str(e)}

# Page interaction tools
@mcp.tool()
async def click_element(selector: str) -> dict:
    """Click an element using CSS selector."""
    logger.info(f"Clicking element: {selector}")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await page_handler.click_element(selector)
    except Exception as e:
        logger.error(f"Error in click_element: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def click_text(text: str) -> dict:
    """Click on text content."""
    logger.info(f"Clicking text: {text}")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await page_handler.click_text(text)
    except Exception as e:
        logger.error(f"Error in click_text: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_page_html() -> dict:
    """Get the current page HTML content."""
    logger.info("Getting page HTML")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await page_handler.get_page_html()
    except Exception as e:
        logger.error(f"Error in get_page_html: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def summarize_page() -> dict:
    """Get a JSON summary of the current page with title, content, and links."""
    logger.info("Summarizing page")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await page_handler.summarize_page()
    except Exception as e:
        logger.error(f"Error in summarize_page: {str(e)}")
        return {"success": False, "error": str(e)}

# Adblock tools
@mcp.tool()
async def adblock_enable() -> dict:
    """Enable ad blocking for the current session."""
    logger.info("Enabling adblock")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await adblock_handler.enable_adblock()
    except Exception as e:
        logger.error(f"Error in adblock_enable: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def adblock_disable() -> dict:
    """Disable ad blocking for the current session."""
    logger.info("Disabling adblock")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await adblock_handler.disable_adblock()
    except Exception as e:
        logger.error(f"Error in adblock_disable: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def adblock_toggle() -> dict:
    """Toggle adblock on/off."""
    logger.info("Toggling adblock")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await adblock_handler.toggle_adblock()
    except Exception as e:
        logger.error(f"Error in adblock_toggle: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def adblock_status() -> dict:
    """Get current adblock status."""
    logger.info("Getting adblock status")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await adblock_handler.get_status()
    except Exception as e:
        logger.error(f"Error in adblock_status: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def adblock_load_rules(path: str, is_directory: bool = False) -> dict:
    """Load adblock rules from file or directory."""
    logger.info(f"Loading adblock rules from: {path} (directory: {is_directory})")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await adblock_handler.load_rules(path, is_directory)
    except Exception as e:
        logger.error(f"Error in adblock_load_rules: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def adblock_fetch_easylist(url: Optional[str] = None) -> dict:
    """Fetch EasyList rules from URL."""
    logger.info(f"Fetching EasyList from: {url}")
    browser_check = await ensure_browser_running_wrapper()
    if not browser_check["success"]:
        return browser_check
    try:
        return await adblock_handler.fetch_easylist(url)
    except Exception as e:
        logger.error(f"Error in adblock_fetch_easylist: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    logger.info("Starting Browser MCP Server with FastMCP...")
    mcp.run()