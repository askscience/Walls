"""Station handler for Radio Player MCP server."""

import asyncio
import json
from typing import Dict, Any, Optional, List

from utils import setup_logger

logger = setup_logger(__name__)

class StationHandler:
    """Handler for radio station management operations."""
    
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
    
    async def add_station(self, name: str, url: str, genre: Optional[str] = None, country: Optional[str] = None) -> str:
        """Add a new radio station to favorites."""
        try:
            # Use the control add command to add station
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "add",
                "--url", url, "--name", name
            ])
            
            logger.info(f"Added station '{name}' with URL '{url}'")
            return f"Added station '{name}': {result}"
            
        except Exception as e:
            logger.error(f"Error adding station: {e}")
            return f"Error adding station: {str(e)}"
    
    async def remove_station(self, name: str) -> str:
        """Remove a station from favorites.
        
        Note: The CLI doesn't currently support removing stations directly.
        This would need to be implemented in the radio player application.
        """
        try:
            # This functionality is not available in the current CLI
            # Would need to be added to the radio player application
            logger.warning(f"Remove station functionality not implemented in CLI for '{name}'")
            return f"Remove station functionality not yet available in the radio player CLI. Station '{name}' cannot be removed via MCP."
            
        except Exception as e:
            logger.error(f"Error removing station: {e}")
            return f"Error removing station: {str(e)}"
    
    async def list_stations(self) -> str:
        """List all favorite radio stations.
        
        Note: The CLI doesn't currently support listing saved stations directly.
        This would need to be implemented in the radio player application.
        """
        try:
            # This functionality is not available in the current CLI
            # Would need to be added to the radio player application
            logger.warning("List stations functionality not implemented in CLI")
            return "List stations functionality not yet available in the radio player CLI. Use the GUI to view saved stations."
            
        except Exception as e:
            logger.error(f"Error listing stations: {e}")
            return f"Error listing stations: {str(e)}"
    
    async def get_station_info(self, name: str) -> str:
        """Get detailed information about a specific station.
        
        Note: The CLI doesn't currently support getting station info directly.
        This would need to be implemented in the radio player application.
        """
        try:
            # This functionality is not available in the current CLI
            # Would need to be added to the radio player application
            logger.warning(f"Get station info functionality not implemented in CLI for '{name}'")
            return f"Get station info functionality not yet available in the radio player CLI. Station '{name}' info cannot be retrieved via MCP."
            
        except Exception as e:
            logger.error(f"Error getting station info: {e}")
            return f"Error getting station info: {str(e)}"
    
    async def play_station_by_index(self, index: int) -> str:
        """Play a station from the last search results by index."""
        try:
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "play-index", str(index)
            ])
            
            logger.info(f"Playing station at index {index}")
            return f"Playing station at index {index}: {result}"
            
        except Exception as e:
            logger.error(f"Error playing station by index: {e}")
            return f"Error playing station by index: {str(e)}"