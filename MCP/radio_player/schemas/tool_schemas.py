"""Tool schemas for Radio Player MCP server."""

TOOL_SCHEMAS = {
    # Playback control tools
    "play_station": {
        "type": "object",
        "properties": {
            "station_url": {
                "type": "string",
                "description": "The URL of the radio station to play (optional)"
            },
            "station_name": {
                "type": "string",
                "description": "The name of the station to search and play (optional)"
            }
        },
        "description": "Play a radio station by URL or search and play by name"
    },
    
    "stop_playback": {
        "type": "object",
        "properties": {},
        "description": "Stop current radio playback"
    },
    
    "pause_playback": {
        "type": "object",
        "properties": {},
        "description": "Pause current radio playback"
    },
    
    "resume_playback": {
        "type": "object",
        "properties": {},
        "description": "Resume paused radio playback"
    },
    
    "get_playback_status": {
        "type": "object",
        "properties": {},
        "description": "Get current playback status and information"
    },
    
    # Station management tools
    "add_station": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name for the radio station"
            },
            "url": {
                "type": "string",
                "description": "The URL of the radio station stream"
            },
            "genre": {
                "type": "string",
                "description": "The genre/tag of the station (optional)"
            },
            "country": {
                "type": "string",
                "description": "The country of the station (optional)"
            }
        },
        "required": ["name", "url"]
    },
    
    "remove_station": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the station to remove"
            }
        },
        "required": ["name"]
    },
    
    "list_stations": {
        "type": "object",
        "properties": {},
        "description": "List all favorite radio stations"
    },
    
    "get_station_info": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the station to get info for"
            }
        },
        "required": ["name"]
    },
    
    # Search tools
    "search_stations": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for station name or general search"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "minimum": 1,
                "maximum": 50
            }
        },
        "required": ["query"]
    },
    
    "search_by_genre": {
        "type": "object",
        "properties": {
            "genre": {
                "type": "string",
                "description": "Genre/tag to search for (e.g., 'rock', 'jazz', 'reggae')"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "minimum": 1,
                "maximum": 50
            }
        },
        "required": ["genre"]
    },
    
    "search_by_country": {
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Country code to search for (e.g., 'US', 'GB', 'DE')"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "minimum": 1,
                "maximum": 50
            }
        },
        "required": ["country"]
    },
    
    # Volume control tools
    "set_volume": {
        "type": "object",
        "properties": {
            "level": {
                "type": "integer",
                "description": "Volume level (0-100)",
                "minimum": 0,
                "maximum": 100
            }
        },
        "required": ["level"]
    },
    
    "get_volume": {
        "type": "object",
        "properties": {},
        "description": "Get current volume level"
    },
    
    "mute_audio": {
        "type": "object",
        "properties": {},
        "description": "Mute audio output"
    },
    
    "unmute_audio": {
        "type": "object",
        "properties": {},
        "description": "Unmute audio output"
    }
}