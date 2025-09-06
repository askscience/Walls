# Radio Player MCP Server Documentation

The Radio Player MCP Server provides comprehensive internet radio streaming capabilities through a set of powerful tools. This server enables AI assistants to control radio playback, search for stations, manage station collections, and adjust audio settings.

## Server Configuration

- **Name**: radio_player
- **Description**: Internet radio streaming and station management server
- **Port**: 8002
- **Capabilities**: tools

## Available Tools

### Playback Control Tools

#### 1. play_station
Starts playing a radio station by name or URL.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "station": {
      "type": "string",
      "description": "Station name or direct stream URL"
    }
  },
  "required": ["station"]
}
```

**Example Usage:**
```json
{
  "name": "play_station",
  "arguments": {
    "station": "BBC Radio 1"
  }
}
```

#### 2. stop_playback
Stops the currently playing radio stream.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "stop_playback",
  "arguments": {}
}
```

#### 3. pause_playback
Pauses the currently playing radio stream.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "pause_playback",
  "arguments": {}
}
```

#### 4. resume_playback
Resumes a paused radio stream.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "resume_playback",
  "arguments": {}
}
```

#### 5. get_playback_status
Retrieves the current playback status and information.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "get_playback_status",
  "arguments": {}
}
```

### Station Search Tools

#### 6. search_stations_by_name
Searches for radio stations by name.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Station name to search for"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return (optional)",
      "default": 10
    }
  },
  "required": ["name"]
}
```

**Example Usage:**
```json
{
  "name": "search_stations_by_name",
  "arguments": {
    "name": "BBC",
    "limit": 5
  }
}
```

#### 7. search_stations_by_genre
Searches for radio stations by music genre or content type.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "genre": {
      "type": "string",
      "description": "Genre to search for (e.g., rock, jazz, news, classical)"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return (optional)",
      "default": 10
    }
  },
  "required": ["genre"]
}
```

**Example Usage:**
```json
{
  "name": "search_stations_by_genre",
  "arguments": {
    "genre": "jazz",
    "limit": 8
  }
}
```

#### 8. search_stations_by_country
Searches for radio stations by country or region.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "country": {
      "type": "string",
      "description": "Country name or code to search for"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return (optional)",
      "default": 10
    }
  },
  "required": ["country"]
}
```

**Example Usage:**
```json
{
  "name": "search_stations_by_country",
  "arguments": {
    "country": "United Kingdom",
    "limit": 12
  }
}
```

#### 9. search_stations_by_language
Searches for radio stations by broadcast language.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "language": {
      "type": "string",
      "description": "Language to search for (e.g., English, Spanish, French)"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return (optional)",
      "default": 10
    }
  },
  "required": ["language"]
}
```

**Example Usage:**
```json
{
  "name": "search_stations_by_language",
  "arguments": {
    "language": "Spanish",
    "limit": 6
  }
}
```

### Station Management Tools

#### 10. add_favorite_station
Adds a station to the favorites list.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "station_name": {
      "type": "string",
      "description": "Name of the station to add to favorites"
    },
    "station_url": {
      "type": "string",
      "description": "Stream URL of the station"
    }
  },
  "required": ["station_name", "station_url"]
}
```

**Example Usage:**
```json
{
  "name": "add_favorite_station",
  "arguments": {
    "station_name": "Smooth Jazz 24/7",
    "station_url": "http://stream.smoothjazz.com/live"
  }
}
```

#### 11. remove_favorite_station
Removes a station from the favorites list.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "station_name": {
      "type": "string",
      "description": "Name of the station to remove from favorites"
    }
  },
  "required": ["station_name"]
}
```

**Example Usage:**
```json
{
  "name": "remove_favorite_station",
  "arguments": {
    "station_name": "Old Station Name"
  }
}
```

#### 12. list_favorite_stations
Retrieves a list of all favorite stations.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "list_favorite_stations",
  "arguments": {}
}
```

#### 13. get_station_info
Retrieves detailed information about a specific station.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "station_name": {
      "type": "string",
      "description": "Name of the station to get information about"
    }
  },
  "required": ["station_name"]
}
```

**Example Usage:**
```json
{
  "name": "get_station_info",
  "arguments": {
    "station_name": "BBC Radio 1"
  }
}
```

### Volume Control Tools

#### 14. set_volume
Sets the playback volume level.

**Schema:**
```json
{
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
}
```

**Example Usage:**
```json
{
  "name": "set_volume",
  "arguments": {
    "level": 75
  }
}
```

#### 15. get_volume
Retrieves the current volume level.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "get_volume",
  "arguments": {}
}
```

#### 16. mute_audio
Mutes the audio output.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "mute_audio",
  "arguments": {}
}
```

#### 17. unmute_audio
Unmutes the audio output.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "unmute_audio",
  "arguments": {}
}
```

## Implementation Details

The Radio Player MCP Server is implemented with the following handler classes:

- **PlaybackHandler**: Manages radio stream playback, pause, resume, and stop functionality
- **SearchHandler**: Handles station searches by name, genre, country, and language
- **StationHandler**: Manages favorite stations, station information, and collections

## Common Workflows

### Discovery and Playback Workflow
1. Use `search_stations_by_genre` to find stations by music type
2. Use `get_station_info` to learn about interesting stations
3. Use `play_station` to start listening
4. Use `add_favorite_station` to save good stations

### Daily Listening Workflow
1. Use `list_favorite_stations` to see saved stations
2. Use `play_station` to start a favorite
3. Use `set_volume` to adjust audio level
4. Use `get_playback_status` to monitor current playing

### International Radio Exploration
1. Use `search_stations_by_country` to find regional stations
2. Use `search_stations_by_language` for specific languages
3. Use `play_station` to sample different stations
4. Use `add_favorite_station` to save discoveries

This comprehensive radio player server enables rich audio streaming experiences with extensive station discovery and management capabilities.