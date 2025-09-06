#!/usr/bin/env python3
"""
Browser MCP Server

Provides MCP tools for controlling the Browser application including:
- Navigation operations (open, back, forward, reload)
- Bookmark management (add, list, get JSON)
- Page operations (click, get HTML, summarize)
- Adblock controls (enable, disable, load rules)
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
# stdio_server will be imported in main()
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from handlers.navigation_handler import NavigationHandler
from handlers.bookmark_handler import BookmarkHandler
from handlers.page_handler import PageHandler
from handlers.adblock_handler import AdblockHandler
from utils.logger import setup_logger
from schemas.tool_schemas import TOOL_SCHEMAS

# Setup logging
logger = setup_logger(__name__)

# Initialize server
server = Server("browser")

# Initialize handlers
navigation_handler = NavigationHandler()
bookmark_handler = BookmarkHandler()
page_handler = PageHandler()
adblock_handler = AdblockHandler()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for browser operations."""
    tools = [
        # Navigation tools
        Tool(
            name="open_url",
            description="Open a webpage in the browser",
            inputSchema=TOOL_SCHEMAS["open_url"]
        ),
        Tool(
            name="navigate_back",
            description="Navigate back in browser history",
            inputSchema=TOOL_SCHEMAS["navigate_back"]
        ),
        Tool(
            name="navigate_forward",
            description="Navigate forward in browser history",
            inputSchema=TOOL_SCHEMAS["navigate_forward"]
        ),
        Tool(
            name="reload_page",
            description="Reload the current page",
            inputSchema=TOOL_SCHEMAS["reload_page"]
        ),
        
        # Bookmark tools
        Tool(
            name="add_bookmark",
            description="Add a bookmark for the current page or specified URL",
            inputSchema=TOOL_SCHEMAS["add_bookmark"]
        ),
        Tool(
            name="get_bookmarks",
            description="Get all bookmarks as JSON",
            inputSchema=TOOL_SCHEMAS["get_bookmarks"]
        ),
        
        # Page interaction tools
        Tool(
            name="click_element",
            description="Click an element using CSS selector",
            inputSchema=TOOL_SCHEMAS["click_element"]
        ),
        Tool(
            name="click_text",
            description="Click on text content",
            inputSchema=TOOL_SCHEMAS["click_text"]
        ),
        Tool(
            name="fill_form",
            description="Fill form fields with provided data",
            inputSchema=TOOL_SCHEMAS["fill_form"]
        ),
        Tool(
            name="get_page_content",
            description="Get the current page content as text or HTML",
            inputSchema=TOOL_SCHEMAS["get_page_content"]
        ),
        Tool(
            name="take_screenshot",
            description="Take a screenshot of the current page",
            inputSchema=TOOL_SCHEMAS["take_screenshot"]
        ),
        
        # Ad blocking tools
        Tool(
            name="enable_adblock",
            description="Enable ad blocking for the current session",
            inputSchema=TOOL_SCHEMAS["enable_adblock"]
        ),
        Tool(
            name="disable_adblock",
            description="Disable ad blocking for the current session",
            inputSchema=TOOL_SCHEMAS["disable_adblock"]
        ),
        Tool(
            name="get_adblock_status",
            description="Get current ad blocking status",
            inputSchema=TOOL_SCHEMAS["get_adblock_status"]
        )
    ]
    
    logger.info(f"Listed {len(tools)} available tools")
    return tools

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls for browser operations."""
    try:
        tool_name = request.params.name
        arguments = request.params.arguments or {}
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        # Navigation operations
        if tool_name == "open_url":
            result = await navigation_handler.open_url(arguments.get("url", ""))
        elif tool_name == "navigate_back":
            result = await navigation_handler.navigate_back()
        elif tool_name == "navigate_forward":
            result = await navigation_handler.navigate_forward()
        elif tool_name == "reload_page":
            result = await navigation_handler.reload_page()
            
        # Bookmark operations
        elif tool_name == "add_bookmark":
            result = await bookmark_handler.add_bookmark(
                arguments.get("url"),
                arguments.get("name")
            )
        elif tool_name == "get_bookmarks":
            result = await bookmark_handler.get_bookmarks()
            
        # Page operations
        elif tool_name == "click_element":
            result = await page_handler.click_element(arguments.get("selector", ""))
        elif tool_name == "click_text":
            result = await page_handler.click_text(arguments.get("text", ""))
        elif tool_name == "get_page_html":
            result = await page_handler.get_page_html()
        elif tool_name == "summarize_page":
            result = await page_handler.summarize_page()
            
        # Adblock operations
        elif tool_name == "adblock_enable":
            result = await adblock_handler.enable_adblock()
        elif tool_name == "adblock_disable":
            result = await adblock_handler.disable_adblock()
        elif tool_name == "adblock_toggle":
            result = await adblock_handler.toggle_adblock()
        elif tool_name == "adblock_status":
            result = await adblock_handler.get_status()
        elif tool_name == "adblock_load_rules":
            result = await adblock_handler.load_rules(
                arguments.get("path", ""),
                arguments.get("is_directory", False)
            )
        elif tool_name == "adblock_fetch_easylist":
            result = await adblock_handler.fetch_easylist(
                arguments.get("url")
            )
            
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Error calling tool {request.params.name}: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "success": False
                    }, indent=2)
                )
            ],
            isError=True
        )

async def main():
    """Main entry point for the browser MCP server."""
    logger.info("Starting Browser MCP Server...")
    
    # Import and run the server using MCP's standard approach
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())