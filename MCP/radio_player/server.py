#!/usr/bin/env python3
"""Radio Player MCP Server.

This server provides MCP (Model Context Protocol) interface for the radio player application.
It handles playback control, station management, search functionality, and volume control.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.types import Tool, TextContent

from handlers import PlaybackHandler, StationHandler, SearchHandler, VolumeHandler
from schemas import TOOL_SCHEMAS
from utils import setup_logger

# Import app launcher for auto-starting radio player
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_launcher import ensure_radio_player_running

# Setup logging
logger = setup_logger(__name__)

# Initialize server
server = Server("radio-player")

# Initialize handlers
playback_handler = PlaybackHandler()
station_handler = StationHandler()
search_handler = SearchHandler()
volume_handler = VolumeHandler()

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for radio player operations."""
    tools = [
        # Playback control tools
        Tool(
            name="play_station",
            description="Play a specific radio station by URL or name",
            inputSchema=TOOL_SCHEMAS["play_station"]
        ),
        Tool(
            name="stop_playback",
            description="Stop current radio playback",
            inputSchema=TOOL_SCHEMAS["stop_playback"]
        ),
        Tool(
            name="pause_playback",
            description="Pause current radio playback",
            inputSchema=TOOL_SCHEMAS["pause_playback"]
        ),
        Tool(
            name="resume_playback",
            description="Resume paused radio playback",
            inputSchema=TOOL_SCHEMAS["resume_playback"]
        ),
        Tool(
            name="get_playback_status",
            description="Get current playback status and information",
            inputSchema=TOOL_SCHEMAS["get_playback_status"]
        ),
        
        # Station management tools
        Tool(
            name="add_station",
            description="Add a new radio station to favorites",
            inputSchema=TOOL_SCHEMAS["add_station"]
        ),
        Tool(
            name="remove_station",
            description="Remove a station from favorites",
            inputSchema=TOOL_SCHEMAS["remove_station"]
        ),
        Tool(
            name="list_stations",
            description="List all favorite radio stations",
            inputSchema=TOOL_SCHEMAS["list_stations"]
        ),
        Tool(
            name="get_station_info",
            description="Get detailed information about a specific station",
            inputSchema=TOOL_SCHEMAS["get_station_info"]
        ),
        
        # Search tools
        Tool(
            name="search_stations",
            description="Search for radio stations by name, genre, or country",
            inputSchema=TOOL_SCHEMAS["search_stations"]
        ),
        Tool(
            name="search_by_genre",
            description="Search stations by specific genre",
            inputSchema=TOOL_SCHEMAS["search_by_genre"]
        ),
        Tool(
            name="search_by_country",
            description="Search stations by country",
            inputSchema=TOOL_SCHEMAS["search_by_country"]
        ),
        
        # Volume control tools
        Tool(
            name="set_volume",
            description="Set playback volume (0-100)",
            inputSchema=TOOL_SCHEMAS["set_volume"]
        ),
        Tool(
            name="get_volume",
            description="Get current volume level",
            inputSchema=TOOL_SCHEMAS["get_volume"]
        ),
        Tool(
            name="mute_audio",
            description="Mute audio output",
            inputSchema=TOOL_SCHEMAS["mute_audio"]
        ),
        Tool(
            name="unmute_audio",
            description="Unmute audio output",
            inputSchema=TOOL_SCHEMAS["unmute_audio"]
        )
    ]
    
    logger.info(f"Listed {len(tools)} available tools")
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for radio player operations."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    # Ensure radio player application is running before executing any tool
    launch_result = await ensure_radio_player_running()
    if not launch_result['success']:
        logger.error(f"Failed to ensure radio player is running: {launch_result.get('error')}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Radio player application not available: {launch_result.get('error')}",
                "tool": name
            }, indent=2)
        )]
    
    if launch_result.get('launched'):
        logger.info(f"Radio player launched successfully for tool: {name}")
    
    try:
        # Playback control operations
        if name == "play_station":
            result = await playback_handler.play_station(
                arguments.get("station_url"),
                arguments.get("station_name")
            )
        elif name == "stop_playback":
            result = await playback_handler.stop_playback()
        elif name == "pause_playback":
            result = await playback_handler.pause_playback()
        elif name == "resume_playback":
            result = await playback_handler.resume_playback()
        elif name == "get_playback_status":
            result = await playback_handler.get_playback_status()
            
        # Station management operations
        elif name == "add_station":
            result = await station_handler.add_station(
                arguments["name"],
                arguments["url"],
                arguments.get("genre"),
                arguments.get("country")
            )
        elif name == "remove_station":
            result = await station_handler.remove_station(arguments["name"])
        elif name == "list_stations":
            result = await station_handler.list_stations()
        elif name == "get_station_info":
            result = await station_handler.get_station_info(arguments["name"])
            
        # Search operations
        elif name == "search_stations":
            result = await search_handler.search_stations(
                arguments["query"],
                arguments.get("limit", 10)
            )
        elif name == "search_by_genre":
            result = await search_handler.search_by_genre(
                arguments["genre"],
                arguments.get("limit", 10)
            )
        elif name == "search_by_country":
            result = await search_handler.search_by_country(
                arguments["country"],
                arguments.get("limit", 10)
            )
            
        # Volume control operations
        elif name == "set_volume":
            result = await volume_handler.set_volume(arguments["level"])
        elif name == "get_volume":
            result = await volume_handler.get_volume()
        elif name == "mute_audio":
            result = await volume_handler.mute_audio()
        elif name == "unmute_audio":
            result = await volume_handler.unmute_audio()
            
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
        
        logger.info(f"Tool {name} executed successfully")
        return [TextContent(type="text", text=str(result))]
        
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Main entry point for the radio player MCP server."""
    logger.info("Starting Radio Player MCP Server...")
    
    # Import and run the server using MCP's standard approach
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="radio-player",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())