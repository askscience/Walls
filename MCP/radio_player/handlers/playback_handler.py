"""Playback handler for Radio Player MCP server."""

import asyncio
import subprocess
from typing import Dict, Any, Optional

from utils import setup_logger

logger = setup_logger(__name__)

class PlaybackHandler:
    """Handler for radio player playback operations."""
    
    def __init__(self):
        # Get the base path dynamically - go up 3 levels from MCP/radio_player/handlers/
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    async def _run_cli_command(self, command: list) -> str:
        """Run a CLI command and return the output."""
        try:
            # Change to the correct directory and run the command
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=self.base_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else "Command failed"
                logger.error(f"CLI command failed: {error_msg}")
                return f"Error: {error_msg}"
            
            return stdout.decode().strip()
            
        except Exception as e:
            logger.error(f"Error running CLI command: {e}")
            return f"Error: {str(e)}"
    
    async def play_station(self, station_url: Optional[str] = None, station_name: Optional[str] = None) -> str:
        """Play a radio station by URL or search and play by name."""
        try:
            if station_url:
                # If URL is provided, add it as a station and play
                name = station_name or "Custom Station"
                add_result = await self._run_cli_command([
                    "python", "-m", "radio_player.cli", "control", "add",
                    "--url", station_url, "--name", name
                ])
                logger.info(f"Added station: {add_result}")
                
                # Start playback
                play_result = await self._run_cli_command([
                    "python", "-m", "radio_player.cli", "control", "play"
                ])
                return f"Added and playing station '{name}': {play_result}"
            
            elif station_name:
                # Search and play by name
                search_result = await self._run_cli_command([
                    "python", "-m", "radio_player.cli", "search-play",
                    "--name", station_name
                ])
                return f"Searched and playing station '{station_name}': {search_result}"
            
            else:
                # Just resume/start playback
                play_result = await self._run_cli_command([
                    "python", "-m", "radio_player.cli", "control", "play"
                ])
                return f"Started playback: {play_result}"
                
        except Exception as e:
            logger.error(f"Error playing station: {e}")
            return f"Error playing station: {str(e)}"
    
    async def stop_playback(self) -> str:
        """Stop radio playback."""
        try:
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "stop"
            ])
            return f"Stopped playback: {result}"
            
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
            return f"Error stopping playback: {str(e)}"
    
    async def pause_playback(self) -> str:
        """Pause radio playback."""
        try:
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "pause"
            ])
            return f"Paused playback: {result}"
            
        except Exception as e:
            logger.error(f"Error pausing playback: {e}")
            return f"Error pausing playback: {str(e)}"
    
    async def resume_playback(self) -> str:
        """Resume radio playback."""
        try:
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "play"
            ])
            return f"Resumed playback: {result}"
            
        except Exception as e:
            logger.error(f"Error resuming playback: {e}")
            return f"Error resuming playback: {str(e)}"
    
    async def get_playback_status(self) -> str:
        """Get current playback status and information."""
        try:
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "status"
            ])
            return f"Playback status: {result}"
            
        except Exception as e:
            logger.error(f"Error getting playback status: {e}")
            return f"Error getting playback status: {str(e)}"
    
    async def next_station(self) -> str:
        """Skip to next station."""
        try:
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "next"
            ])
            return f"Next station: {result}"
            
        except Exception as e:
            logger.error(f"Error skipping to next station: {e}")
            return f"Error skipping to next station: {str(e)}"
    
    async def previous_station(self) -> str:
        """Skip to previous station."""
        try:
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "prev"
            ])
            return f"Previous station: {result}"
            
        except Exception as e:
            logger.error(f"Error skipping to previous station: {e}")
            return f"Error skipping to previous station: {str(e)}"