"""Word Editor MCP server using FastMCP."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from handlers.text_handler import TextHandler
from handlers.file_handler import FileHandler
from handlers.cli_handler import CLIHandler

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_launcher import ensure_word_editor_running
from utils.logger import setup_logger
from schemas.tool_schemas import TOOL_SCHEMAS

# Setup logging
logger = setup_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("word-editor")

# Initialize handlers
text_handler = TextHandler()
file_handler = FileHandler()
cli_handler = CLIHandler()

async def ensure_word_editor_available():
    """Check if word editor is available."""
    try:
        launch_result = await ensure_word_editor_running()
        if not launch_result['success']:
            logger.error(f"Failed to ensure word editor is running: {launch_result.get('error')}")
            return [{"type": "text", "text": f"Word editor application not available: {launch_result.get('error')}"}]
        
        if launch_result.get('launched'):
            logger.info("Word editor launched successfully")
        
        return None  # No error, word editor is available
        
    except Exception as e:
        logger.error(f"Error checking word editor availability: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# Text operation tools
@mcp.tool()
async def set_text(text: str) -> List[Dict[str, Any]]:
    """Set the entire text content in the word editor."""
    logger.info(f"Setting text: {text[:50]}...")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await text_handler.set_text(text)
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in set_text: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
async def insert_text(position: int, text: str) -> List[Dict[str, Any]]:
    """Insert text at a specific position in the word editor."""
    logger.info(f"Inserting text at position {position}: {text[:50]}...")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await text_handler.insert_text(position, text)
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in insert_text: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
async def append_text(text: str) -> List[Dict[str, Any]]:
    """Append text to the end of the current content."""
    logger.info(f"Appending text: {text[:50]}...")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await text_handler.append_text(text)
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in append_text: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
async def get_text() -> List[Dict[str, Any]]:
    """Get the current text content from the word editor."""
    logger.info("Getting text content")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await text_handler.get_text()
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in get_text: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# File operation tools
@mcp.tool()
async def open_file(file_path: str) -> List[Dict[str, Any]]:
    """Open a file in the word editor."""
    logger.info(f"Opening file: {file_path}")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await file_handler.open_file(file_path)
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in open_file: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
async def save_file(file_path: Optional[str] = None, content: Optional[str] = None) -> List[Dict[str, Any]]:
    """Save the current content to a file."""
    logger.info(f"Saving file: {file_path}")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await file_handler.save_file(file_path, content)
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in save_file: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# CLI operation tools
@mcp.tool()
async def send_cli_command(command: str, args: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Send a command to the word editor CLI."""
    if args is None:
        args = []
    logger.info(f"Sending CLI command: {command} with args: {args}")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await cli_handler.send_command(command, args)
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in send_cli_command: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
async def check_gui_status() -> List[Dict[str, Any]]:
    """Check if the word editor GUI is running and accessible."""
    logger.info("Checking GUI status")
    check_result = await ensure_word_editor_available()
    if check_result:
        return check_result
    try:
        result = await cli_handler.check_status()
        return [{"type": "text", "text": str(result)}]
    except Exception as e:
        logger.error(f"Error in check_gui_status: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

if __name__ == "__main__":
    logger.info("Starting Word Editor MCP Server with FastMCP...")
    mcp.run()