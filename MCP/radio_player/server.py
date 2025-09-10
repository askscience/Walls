#!/usr/bin/env python3
"""
Radio Player MCP Server using FastMCP

Provides tools for controlling radio playback, managing stations,
searching for stations, and controlling volume.
"""

import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool

# Import handlers
from handlers.playback_handler import PlaybackHandler
from handlers.station_handler import StationHandler
from handlers.search_handler import SearchHandler
from handlers.volume_handler import VolumeHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("Radio Player")

# Initialize handlers
playback_handler = PlaybackHandler()
station_handler = StationHandler()
search_handler = SearchHandler()
volume_handler = VolumeHandler()

def ensure_radio_player_available():
    """Check if radio player is available."""
    try:
        if not playback_handler.is_radio_player_available():
            return [{"type": "text", "text": "Radio player application not available. Please start the radio player first."}]
        return None
    except Exception as e:
        logger.error(f"Error checking radio player availability: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# Playback control tools
@mcp.tool()
def play_station(station_name: str) -> List[Dict[str, Any]]:
    """Play a specific radio station by name."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = playback_handler.play_station(station_name)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in play_station: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def stop_playback() -> List[Dict[str, Any]]:
    """Stop the current radio playback."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = playback_handler.stop_playback()
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in stop_playback: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def pause_playback() -> List[Dict[str, Any]]:
    """Pause the current radio playback."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = playback_handler.pause_playback()
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in pause_playback: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def resume_playback() -> List[Dict[str, Any]]:
    """Resume the paused radio playback."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = playback_handler.resume_playback()
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in resume_playback: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def get_playback_status() -> List[Dict[str, Any]]:
    """Get the current playback status and information."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = playback_handler.get_playback_status()
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in get_playback_status: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def get_current_station() -> List[Dict[str, Any]]:
    """Get information about the currently playing station."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = playback_handler.get_current_station()
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in get_current_station: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# Station management tools
@mcp.tool()
def add_favorite_station(station_name: str, station_url: str) -> List[Dict[str, Any]]:
    """Add a station to favorites."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = station_handler.add_favorite_station(station_name, station_url)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in add_favorite_station: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def remove_favorite_station(station_name: str) -> List[Dict[str, Any]]:
    """Remove a station from favorites."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = station_handler.remove_favorite_station(station_name)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in remove_favorite_station: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def list_favorite_stations() -> List[Dict[str, Any]]:
    """List all favorite stations."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = station_handler.list_favorite_stations()
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in list_favorite_stations: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def get_station_info(station_name: str) -> List[Dict[str, Any]]:
    """Get detailed information about a specific station."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = station_handler.get_station_info(station_name)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in get_station_info: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# Search tools
@mcp.tool()
def search_stations(query: str, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """Search for radio stations by name, genre, or country."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = search_handler.search_stations(query, limit)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in search_stations: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def search_by_genre(genre: str, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """Search for radio stations by genre."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = search_handler.search_by_genre(genre, limit)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in search_by_genre: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def search_by_country(country: str, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """Search for radio stations by country."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = search_handler.search_by_country(country, limit)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in search_by_country: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def get_popular_stations(limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """Get a list of popular radio stations."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = search_handler.get_popular_stations(limit)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in get_popular_stations: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# Volume control tools
@mcp.tool()
def set_volume(volume: int) -> List[Dict[str, Any]]:
    """Set the playback volume (0-100)."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = volume_handler.set_volume(volume)
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in set_volume: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

@mcp.tool()
def get_volume() -> List[Dict[str, Any]]:
    """Get the current playback volume."""
    check_result = ensure_radio_player_available()
    if check_result:
        return check_result
    try:
        result = volume_handler.get_volume()
        return [{"type": "text", "text": result}]
    except Exception as e:
        logger.error(f"Error in get_volume: {e}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

if __name__ == "__main__":
    logger.info("Starting Radio Player MCP Server with FastMCP...")
    mcp.run()