# MCP Servers for Walls Applications

This directory contains Model Context Protocol (MCP) servers for the three main applications in the Walls project:

- **Word Editor** - Text editing and document management
- **Browser** - Web browsing with adblock and bookmark features
- **Radio Player** - Internet radio streaming and station management

## Directory Structure

```
MCP/
├── mcp_config.json          # Global configuration for all MCP servers
├── README.md                 # This file
├── word_editor/             # Word Editor MCP Server
│   ├── server.py            # Main MCP server implementation
│   ├── requirements.txt     # Python dependencies
│   ├── handlers/            # Operation handlers
│   │   ├── __init__.py
│   │   ├── text_handler.py  # Text manipulation operations
│   │   ├── file_handler.py  # File operations
│   │   └── cli_handler.py   # CLI command operations
│   ├── schemas/             # Tool schemas
│   │   ├── __init__.py
│   │   └── tool_schemas.py  # JSON schemas for tools
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── logger.py        # Logging configuration
├── browser/                 # Browser MCP Server
│   ├── server.py            # Main MCP server implementation
│   ├── requirements.txt     # Python dependencies
│   ├── handlers/            # Operation handlers
│   │   ├── __init__.py
│   │   ├── navigation_handler.py    # Navigation operations
│   │   ├── bookmark_handler.py      # Bookmark management
│   │   ├── page_handler.py          # Page interaction
│   │   └── adblock_handler.py       # Adblock controls
│   ├── schemas/             # Tool schemas
│   │   ├── __init__.py
│   │   └── tool_schemas.py  # JSON schemas for tools
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── logger.py        # Logging configuration
└── radio_player/            # Radio Player MCP Server
    ├── server.py            # Main MCP server implementation
    ├── requirements.txt     # Python dependencies
    ├── handlers/            # Operation handlers
    │   ├── __init__.py
    │   ├── playback_handler.py     # Playback control
    │   ├── station_handler.py      # Station management
    │   ├── search_handler.py       # Search functionality
    │   └── volume_handler.py       # Volume control
    ├── schemas/             # Tool schemas
    │   ├── __init__.py
    │   └── tool_schemas.py  # JSON schemas for tools
    └── utils/               # Utilities
        ├── __init__.py
        └── logger.py        # Logging configuration
```

## Prerequisites

Before using these MCP servers, ensure that:

1. **Python 3.8+** is installed
2. The corresponding GUI applications are running:
   - Word Editor: `python -m Words.word_editor.python_gui.main`
   - Browser: `python -m browser.main`
   - Radio Player: `python -m radio_player.modern_gui`

## Installation

### Install Dependencies

For each MCP server, install the required dependencies:

```bash
# Word Editor MCP Server
cd <REPO_ROOT>/MCP/word_editor
pip install -r requirements.txt

# Browser MCP Server
cd <REPO_ROOT>/MCP/browser
pip install -r requirements.txt

# Radio Player MCP Server
cd <REPO_ROOT>/MCP/radio_player
pip install -r requirements.txt
```

### Or install all at once:

```bash
cd <REPO_ROOT>/MCP
pip install -r word_editor/requirements.txt
pip install -r browser/requirements.txt
pip install -r radio_player/requirements.txt
```

## Usage

### Starting MCP Servers

Each MCP server can be started independently:

```bash
# Word Editor MCP Server
cd MCP/word_editor
python server.py

# Browser MCP Server
cd ../browser
python server.py

# Radio Player MCP Server
cd ../radio_player
python server.py
```



### Available Tools

#### Word Editor MCP Server
- **Text Operations**: `set_text`, `insert_text`, `append_text`, `get_text`
- **File Operations**: `open_file`, `save_file`, `get_file_info`
- **CLI Operations**: `send_cli_command`, `check_gui_status`, `get_available_commands`

#### Browser MCP Server
- **Navigation**: `open_url`, `navigate_back`, `navigate_forward`, `reload_page`
- **Bookmarks**: `add_bookmark`, `get_bookmarks`
- **Page Interaction**: `click_element`, `click_text`, `get_page_html`, `summarize_page`
- **Adblock**: `adblock_enable`, `adblock_disable`, `adblock_toggle`, `adblock_status`, `adblock_load_rules`, `adblock_fetch_easylist`

#### Radio Player MCP Server
- **Playback Control**: `play_station`, `stop_playback`, `pause_playback`, `resume_playback`, `get_playback_status`
- **Station Management**: `add_station`, `remove_station`, `list_stations`, `get_station_info`
- **Search**: `search_stations`, `search_by_genre`, `search_by_country`
- **Volume Control**: `set_volume`, `get_volume`, `mute_audio`, `unmute_audio`

## Communication Protocols

### Word Editor
- **Protocol**: TCP Socket
- **Port**: 8888
- **Format**: JSON messages

### Browser
- **Protocol**: CLI via shared_server
- **Command**: `shared_server browser <action> [args]`
- **Base Path**: Dynamically determined from installation directory

### Radio Player
- **Protocol**: CLI via radio_player module
- **Command**: `python -m radio_player.cli <subcommand> [args]`
- **Base Path**: Dynamically determined from installation directory

## Configuration

The `mcp_config.json` file contains global configuration for all MCP servers, including:

- Server paths and ports
- Available capabilities and tools
- Communication settings
- Global settings (logging, timeouts, etc.)

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the corresponding GUI application is running
2. **Command Not Found**: Verify you're in the correct project root directory
3. **Import Errors**: Install the required dependencies using `pip install -r requirements.txt`
4. **Permission Errors**: Ensure the MCP server has appropriate file system permissions

### Logging

Each MCP server includes comprehensive logging. Check the console output for detailed error messages and operation logs.

### Testing Connectivity

#### Word Editor
```bash
# Test TCP connection
telnet localhost 8888
```

#### Browser
```bash
# Test shared_server integration
cd path/to/your/project
shared_server browser status
```

#### Radio Player
```bash
# Test CLI integration
cd path/to/your/project
python -m radio_player.cli control status
```

## Development

### Adding New Tools

1. Define the tool schema in `schemas/tool_schemas.py`
2. Implement the handler method in the appropriate handler class
3. Register the tool in the main `server.py` file
4. Update the configuration in `mcp_config.json`

### Handler Architecture

Each MCP server follows a consistent architecture:

- **Server**: Main MCP server implementation with tool registration
- **Handlers**: Modular handlers for different operation categories
- **Schemas**: JSON schemas for tool validation
- **Utils**: Shared utilities like logging

## License

These MCP servers are part of the Walls project. Please refer to the individual application licenses for more information.