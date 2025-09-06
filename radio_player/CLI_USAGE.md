# Radio Player CLI Usage Guide

This guide explains how to use the command-line interface (CLI) to control and interact with the Radio Player application.

## Prerequisites

- The GUI application must be running for CLI commands to work
- Start the GUI app with:
```bash
cd <REPO_ROOT>
python -m radio_player.modern_gui
```
- The CLI communicates with the GUI via TCP socket (port 9999)

## Quick Start

- Open the Radio Player GUI:
```bash
cd <REPO_ROOT>
python -m radio_player.modern_gui
```
- Verify status (from another terminal):
```bash
cd <REPO_ROOT>
python -m radio_player.cli control status
```

## Available Commands

### 1. Control GUI Application

```bash
cd <REPO_ROOT>
# Control playback
python -m radio_player.cli control play     # Start/resume playback
python -m radio_player.cli control pause    # Pause playback
python -m radio_player.cli control stop     # Stop playback
python -m radio_player.cli control next     # Next station
python -m radio_player.cli control prev     # Previous station

# Volume control
python -m radio_player.cli control volume --level 75  # Set volume to 75%

# Get status
python -m radio_player.cli control status   # Show current status

# Add stations
python -m radio_player.cli control add --url "http://stream.url" --name "Station Name"
```

### 2. Search and Play Radio Stations

#### Quick Search and Play (Immediate Playback)
```bash
cd <REPO_ROOT>
# Search and immediately play the first result
python -m radio_player.cli search-play --tag "reggae"        # Play first reggae station
python -m radio_player.cli search-play --name "BBC"         # Play first BBC station
python -m radio_player.cli search-play --country "US" --tag "rock"  # Play first US rock station
```

#### Search Then Select (Two-Step Process)
```bash
cd <REPO_ROOT>
# Step 1: Search for stations
python -m radio_player.cli gui-search --tag "reggae" --limit 5
# Output shows numbered list:
#   1. Station A
#   2. Station B
#   3. Station C
#   ...

# Step 2: Play selected station by index number
python -m radio_player.cli play-index 2     # Play station #2 from search results
```

#### Advanced Search Options
```bash
cd <REPO_ROOT>
# Search by various criteria
python -m radio_player.cli gui-search --name "BBC"           # Search by name
python -m radio_player.cli gui-search --tag "rock"          # Search by tag/genre
python -m radio_player.cli gui-search --country "US"        # Search by country
python -m radio_player.cli gui-search --language "english"  # Search by language
python -m radio_player.cli gui-search --limit 5             # Limit results

# Combine multiple criteria
python -m radio_player.cli gui-search --tag "jazz" --country "US" --limit 10
```

### 3. Search Radio Stations (Standalone)

```bash
cd <REPO_ROOT>
# Search without GUI (original functionality)
python -m radio_player.cli search --name "BBC" --limit 5
python -m radio_player.cli search --tag "rock" --country "DE"

# Play directly (original functionality)
python -m radio_player.cli play --name "BBC Radio 1"
python -m radio_player.cli play --uuid "station-uuid-here"
```

## Example Workflows

### Workflow 1: Quick Play
```bash
cd <REPO_ROOT>
# Start GUI app (in one terminal)
python -m radio_player.modern_gui

# Search and play immediately (in another terminal)
python -m radio_player.cli search-play --tag "jazz"
```

### Workflow 2: Browse and Select
```bash
cd <REPO_ROOT>
# Search for options
python -m radio_player.cli gui-search --name "BBC" --limit 5

# Review the list and pick one
python -m radio_player.cli play-index 3

# Check what's playing
python -m radio_player.cli control status
```

### Workflow 3: Station Management
```bash
cd <REPO_ROOT>
# Add a custom station
python -m radio_player.cli control add --url "http://example.com/stream" --name "My Station"

# Control playback
python -m radio_player.cli control play
python -m radio_player.cli control volume --level 80

# Navigate stations
python -m radio_player.cli control next
python -m radio_player.cli control prev
```

## Command Reference

### Available Subcommands
- control - Control GUI application (play, pause, stop, volume, etc.)
- gui-search - Search stations via GUI and store results
- play-index - Play a station from last search results by index
- search-play - Search and immediately play the first result
- search - Standalone search (original functionality)
- play - Standalone play (original functionality)

### Search Criteria
- --name - Station name (partial match)
- --tag - Genre/tag (e.g., "rock", "jazz", "reggae")
- --country - Country code (e.g., "US", "GB", "DE")
- --language - Language code (e.g., "english", "spanish")
- --limit - Maximum number of results (default: 10)

### Control Actions
- play - Start/resume playback
- pause - Pause playback
- stop - Stop playback
- next - Next station
- prev - Previous station
- volume --level N - Set volume (0-100)
- status - Show current status
- add --url URL --name NAME - Add station

## Tips

1. Search Results Persistence: Search results from gui-search are saved temporarily and can be used with play-index until you perform a new search.
2. Quick Discovery: Use search-play for instant gratification when you want to quickly find and play something.
3. Browse Mode: Use gui-search + play-index when you want to see options before deciding.
4. Status Monitoring: Use control status to check what's currently playing and the playback state.
5. Volume Control: Volume changes are immediate and persistent across station changes.