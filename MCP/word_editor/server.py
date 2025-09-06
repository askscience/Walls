#!/usr/bin/env python3
"""
Word Editor MCP Server

Provides MCP tools for controlling the Word Editor application including:
- Text operations (set, insert, append)
- File operations (open, save)
- Real-time CLI commands
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from handlers.text_handler import TextHandler
from handlers.file_handler import FileHandler
from handlers.cli_handler import CLIHandler
from utils.logger import setup_logger
from schemas.tool_schemas import TOOL_SCHEMAS

# Setup logging
logger = setup_logger(__name__)

# Initialize server
server = Server("word-editor")

# Initialize handlers
text_handler = TextHandler()
file_handler = FileHandler()
cli_handler = CLIHandler()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for word editor operations."""
    tools = [
        # Text operation tools
        Tool(
            name="set_text",
            description="Set the entire text content in the word editor",
            inputSchema=TOOL_SCHEMAS["set_text"]
        ),
        Tool(
            name="insert_text",
            description="Insert text at a specific position in the word editor",
            inputSchema=TOOL_SCHEMAS["insert_text"]
        ),
        Tool(
            name="append_text",
            description="Append text to the end of the current content",
            inputSchema=TOOL_SCHEMAS["append_text"]
        ),
        Tool(
            name="get_text",
            description="Get the current text content from the word editor",
            inputSchema=TOOL_SCHEMAS["get_text"]
        ),
        
        # File operation tools
        Tool(
            name="open_file",
            description="Open a file in the word editor",
            inputSchema=TOOL_SCHEMAS["open_file"]
        ),
        Tool(
            name="save_file",
            description="Save the current content to a file",
            inputSchema=TOOL_SCHEMAS["save_file"]
        ),
        
        # CLI operation tools
        Tool(
            name="send_cli_command",
            description="Send a command to the word editor CLI",
            inputSchema=TOOL_SCHEMAS["send_cli_command"]
        ),
        Tool(
            name="check_gui_status",
            description="Check if the word editor GUI is running and accessible",
            inputSchema=TOOL_SCHEMAS["check_gui_status"]
        )
    ]
    
    logger.info(f"Listed {len(tools)} available tools")
    return tools

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls for word editor operations."""
    try:
        tool_name = request.params.name
        arguments = request.params.arguments or {}
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        # Text operations
        if tool_name == "set_text":
            result = await text_handler.set_text(arguments.get("text", ""))
        elif tool_name == "insert_text":
            result = await text_handler.insert_text(
                arguments.get("position", 0),
                arguments.get("text", "")
            )
        elif tool_name == "append_text":
            result = await text_handler.append_text(arguments.get("text", ""))
        elif tool_name == "get_text":
            result = await text_handler.get_text()
            
        # File operations
        elif tool_name == "open_file":
            result = await file_handler.open_file(arguments.get("file_path", ""))
        elif tool_name == "save_file":
            result = await file_handler.save_file(
                arguments.get("file_path"),
                arguments.get("content")
            )
            
        # CLI operations
        elif tool_name == "send_cli_command":
            result = await cli_handler.send_command(
                arguments.get("command", ""),
                arguments.get("args", [])
            )
        elif tool_name == "check_gui_status":
            result = await cli_handler.check_status()
            
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
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="word-editor",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())