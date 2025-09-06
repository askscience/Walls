import sys
import argparse
import subprocess
import shutil
import socket
import json
import time
import os
import tempfile
from typing import List, Dict, Optional

# Add the parent directory to the path to import shared_server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_server.client import send_command_to_app

from .radio_browser import RadioBrowserClient


PLAYER_CANDIDATES = [
    ["ffplay", "-nodisp", "-autoexit"],
    ["mpv"],
    ["vlc"],
]


def choose_player() -> List[str]:
    for cand in PLAYER_CANDIDATES:
        if shutil.which(cand[0]):
            return cand
    raise RuntimeError("No supported CLI player found (ffplay/mpv/vlc). Install one to use CLI playback.")


def cmd_search(args):
    client = RadioBrowserClient()
    stations = client.search(name=args.name, tag=args.tag, countrycode=args.country, language=args.language, limit=args.limit)
    for i, st in enumerate(stations, start=1):
        name = st.get("name")
        cc = st.get("countrycode")
        codec = st.get("codec")
        br = st.get("bitrate")
        print(f"{i:3}. {name} [{cc}] {codec} {br}kbps | uuid={st.get('stationuuid')}")
    print(f"Total: {len(stations)}")


def cmd_play(args):
    client = RadioBrowserClient()
    if args.uuid:
        # Search by uuid needs a single item; we can use search with name=None but filter not supported directly
        # So do a generic search and pick by uuid using a big limit
        results = client._request("/json/stations/byuuid/" + args.uuid)
        stations = results if isinstance(results, list) else [results]
    else:
        stations = client.search(name=args.name, tag=args.tag, countrycode=args.country, language=args.language, limit=args.limit)

    if not stations:
        print("No stations found", file=sys.stderr)
        sys.exit(2)

    st = stations[0]
    url = client.resolved_url(st)
    if not url:
        print("Selected station has no stream URL", file=sys.stderr)
        sys.exit(3)

    # Count click
    try:
        if st.get("stationuuid"):
            client.count_click(st["stationuuid"])
    except Exception:
        pass

    cmd = choose_player() + [url]
    print(f"Playing: {st.get('name')}\n{url}")
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        pass


def send_command_to_gui(command: str, data: Dict = None) -> Optional[Dict]:
    """Send command to running GUI application via shared server."""
    try:
        return send_command_to_app('radio_player', command, data or {})
    except Exception as e:
        print(f"Failed to send command to GUI: {e}", file=sys.stderr)
        return None


def cmd_gui_control(args):
    """Control the running GUI application."""
    if args.action == 'play':
        result = send_command_to_gui('play')
    elif args.action == 'pause':
        result = send_command_to_gui('pause')
    elif args.action == 'stop':
        result = send_command_to_gui('stop')
    elif args.action == 'next':
        result = send_command_to_gui('next')
    elif args.action == 'prev':
        result = send_command_to_gui('prev')
    elif args.action == 'volume':
        result = send_command_to_gui('volume', {'level': args.level})
    elif args.action == 'status':
        result = send_command_to_gui('status')
    elif args.action == 'add':
        result = send_command_to_gui('add', {'url': args.url, 'name': args.name})
    
    if result:
        if result.get('status') == 'success':
            print(f"✓ {result.get('message', 'Command executed successfully')}")
            if 'data' in result:
                for key, value in result['data'].items():
                    print(f"  {key}: {value}")
        else:
            print(f"✗ {result.get('message', 'Command failed')}")
    else:
        print("✗ Failed to communicate with GUI application")


def cmd_gui_search(args):
    """Search and add stations via GUI."""
    result = send_command_to_gui('search', {
        'name': args.name,
        'tag': args.tag,
        'country': args.country,
        'language': args.language,
        'limit': args.limit
    })
    
    if result and result.get('status') == 'success':
        stations = result.get('data', {}).get('stations', [])
        print(f"Found {len(stations)} stations:")
        for i, station in enumerate(stations, 1):
            name = station.get('name', 'Unknown')
            country = station.get('countrycode', 'N/A')
            codec = station.get('codec', 'N/A')
            bitrate = station.get('bitrate', 'N/A')
            print(f"{i:3}. {name} [{country}] {codec} {bitrate}kbps")
        
        # Store search results for potential playback
        _save_search_results(stations)
    else:
        print("✗ Search failed or no results")


def cmd_play_from_search(args):
    """Play a station from the last search results by index."""
    search_results = _load_search_results()
    
    if not search_results:
        print("✗ No search results available. Please search for stations first.")
        return
    
    try:
        index = int(args.index) - 1  # Convert to 0-based index
        if 0 <= index < len(search_results):
            station = search_results[index]
            station_name = station.get('name', 'Unknown Station')
            station_url = station.get('url_resolved') or station.get('url')
            
            if station_url:
                # Add station to GUI and play it
                add_result = send_command_to_gui('add', {
                    'url': station_url,
                    'name': station_name
                })
                
                if add_result and add_result.get('status') == 'success':
                    # Now play it
                    play_result = send_command_to_gui('play')
                    if play_result and play_result.get('status') == 'success':
                        print(f"✓ Now playing: {station_name}")
                    else:
                        print(f"✓ Added {station_name} but failed to start playback")
                else:
                    print(f"✗ Failed to add station: {station_name}")
            else:
                print(f"✗ No valid URL found for station: {station_name}")
        else:
            print(f"✗ Invalid index. Please choose between 1 and {len(search_results)}")
    except ValueError:
        print("✗ Invalid index. Please provide a number.")


def cmd_search_and_play(args):
    """Search for stations and immediately play the first result."""
    result = send_command_to_gui('search', {
        'name': args.name,
        'tag': args.tag,
        'country': args.country,
        'language': args.language,
        'limit': args.limit or 1
    })
    
    if result and result.get('status') == 'success':
        stations = result.get('data', {}).get('stations', [])
        if stations:
            station = stations[0]
            station_name = station.get('name', 'Unknown Station')
            station_url = station.get('url_resolved') or station.get('url')
            
            if station_url:
                # First stop any current playback
                send_command_to_gui('stop')
                
                # Add station to GUI and play it
                add_result = send_command_to_gui('add', {
                    'url': station_url,
                    'name': station_name
                })
                
                if add_result and add_result.get('status') == 'success':
                    # Now play it
                    play_result = send_command_to_gui('play')
                    if play_result and play_result.get('status') == 'success':
                        print(f"✓ Now playing: {station_name}")
                        print(f"  Country: {station.get('countrycode', 'N/A')}")
                        print(f"  Codec: {station.get('codec', 'N/A')} {station.get('bitrate', 'N/A')}kbps")
                    else:
                        print(f"✓ Added {station_name} but failed to start playback")
                else:
                    print(f"✗ Failed to add station: {station_name}")
            else:
                print(f"✗ No valid URL found for station: {station_name}")
        else:
            print("✗ No stations found matching your criteria")
    else:
        print("✗ Search failed")


# Global variable to store last search results
_last_search_results = []

# File to persist search results between CLI calls
_SEARCH_RESULTS_FILE = os.path.join(tempfile.gettempdir(), 'radio_player_search_results.json')


def _save_search_results(stations):
    """Save search results to temporary file."""
    try:
        with open(_SEARCH_RESULTS_FILE, 'w') as f:
            json.dump(stations, f)
    except Exception:
        pass  # Silently ignore file errors


def _load_search_results():
    """Load search results from temporary file."""
    try:
        if os.path.exists(_SEARCH_RESULTS_FILE):
            with open(_SEARCH_RESULTS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass  # Silently ignore file errors
    return []


def main(argv: List[str] | None = None):
    parser = argparse.ArgumentParser(prog="radio-cli", description="Radio Browser CLI player and GUI controller")
    sub = parser.add_subparsers(dest="command", required=True)

    # Original standalone commands
    p_search = sub.add_parser("search", help="Search stations (standalone)")
    p_search.add_argument("--name", help="Search by name")
    p_search.add_argument("--tag", help="Search by tag")
    p_search.add_argument("--language", help="Search by language code (eng, spa)")
    p_search.add_argument("--country", help="Search by country code (US, DE)")
    p_search.add_argument("--limit", type=int, default=50)
    p_search.set_defaults(func=cmd_search)

    p_play = sub.add_parser("play", help="Play first matching station (standalone)")
    p_play.add_argument("--uuid", help="Station UUID to play")
    p_play.add_argument("--name", help="Search by name")
    p_play.add_argument("--tag", help="Search by tag")
    p_play.add_argument("--language", help="Search by language code (eng, spa)")
    p_play.add_argument("--country", help="Search by country code (US, DE)")
    p_play.add_argument("--limit", type=int, default=10)
    p_play.set_defaults(func=cmd_play)

    # GUI control commands
    p_control = sub.add_parser("control", help="Control running GUI application")
    p_control.add_argument("action", choices=['play', 'pause', 'stop', 'next', 'prev', 'status', 'add', 'volume'],
                          help="Control action")
    p_control.add_argument("--level", type=int, help="Volume level (0-100) for volume action")
    p_control.add_argument("--url", help="Stream URL for add action")
    p_control.add_argument("--name", help="Station name for add action")
    p_control.set_defaults(func=cmd_gui_control)

    p_gui_search = sub.add_parser("gui-search", help="Search stations via GUI")
    p_gui_search.add_argument("--name", help="Search by name")
    p_gui_search.add_argument("--tag", help="Search by tag")
    p_gui_search.add_argument("--language", help="Search by language code (eng, spa)")
    p_gui_search.add_argument("--country", help="Search by country code (US, DE)")
    p_gui_search.add_argument("--limit", type=int, default=20)
    p_gui_search.set_defaults(func=cmd_gui_search)

    # Play from search results command
    p_play_index = sub.add_parser("play-index", help="Play a station from last search results by index")
    p_play_index.add_argument("index", help="Index number of the station to play (1-based)")
    p_play_index.set_defaults(func=cmd_play_from_search)

    # Search and play immediately command
    p_search_play = sub.add_parser("search-play", help="Search and immediately play the first result")
    p_search_play.add_argument("--name", help="Search by name")
    p_search_play.add_argument("--tag", help="Search by tag")
    p_search_play.add_argument("--language", help="Search by language code (eng, spa)")
    p_search_play.add_argument("--country", help="Search by country code (US, DE)")
    p_search_play.add_argument("--limit", type=int, default=1)
    p_search_play.set_defaults(func=cmd_search_and_play)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()