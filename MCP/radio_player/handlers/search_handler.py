"""Search handler for Radio Player MCP server."""

import asyncio
import json
from typing import Dict, Any, Optional, List

from utils import setup_logger

logger = setup_logger(__name__)

class SearchHandler:
    """Handler for radio station search operations."""
    
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
    
    async def search_stations(self, query: str, limit: int = 10) -> str:
        """Search for radio stations by name, genre, or general query."""
        try:
            # Use gui-search to search and store results for later use
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "gui-search",
                "--name", query, "--limit", str(limit)
            ])
            
            logger.info(f"Searched for stations with query '{query}', limit {limit}")
            return f"Search results for '{query}': {result}"
            
        except Exception as e:
            logger.error(f"Error searching stations: {e}")
            return f"Error searching stations: {str(e)}"
    
    async def search_by_genre(self, genre: str, limit: int = 10) -> str:
        """Search stations by specific genre/tag."""
        try:
            # Use gui-search with tag parameter
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "gui-search",
                "--tag", genre, "--limit", str(limit)
            ])
            
            logger.info(f"Searched for stations by genre '{genre}', limit {limit}")
            return f"Search results for genre '{genre}': {result}"
            
        except Exception as e:
            logger.error(f"Error searching by genre: {e}")
            return f"Error searching by genre: {str(e)}"
    
    async def search_by_country(self, country: str, limit: int = 10) -> str:
        """Search stations by country."""
        try:
            # Use gui-search with country parameter
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "gui-search",
                "--country", country, "--limit", str(limit)
            ])
            
            logger.info(f"Searched for stations by country '{country}', limit {limit}")
            return f"Search results for country '{country}': {result}"
            
        except Exception as e:
            logger.error(f"Error searching by country: {e}")
            return f"Error searching by country: {str(e)}"
    
    async def search_by_language(self, language: str, limit: int = 10) -> str:
        """Search stations by language."""
        try:
            # Use gui-search with language parameter
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "gui-search",
                "--language", language, "--limit", str(limit)
            ])
            
            logger.info(f"Searched for stations by language '{language}', limit {limit}")
            return f"Search results for language '{language}': {result}"
            
        except Exception as e:
            logger.error(f"Error searching by language: {e}")
            return f"Error searching by language: {str(e)}"
    
    async def search_and_play(self, query: Optional[str] = None, genre: Optional[str] = None, 
                             country: Optional[str] = None, language: Optional[str] = None) -> str:
        """Search for stations and immediately play the first result."""
        try:
            command = ["python", "-m", "radio_player.cli", "search-play"]
            
            # Add search parameters
            if query:
                command.extend(["--name", query])
            if genre:
                command.extend(["--tag", genre])
            if country:
                command.extend(["--country", country])
            if language:
                command.extend(["--language", language])
            
            # If no parameters provided, default to a general search
            if not any([query, genre, country, language]):
                logger.warning("No search parameters provided for search_and_play")
                return "Error: No search parameters provided. Please specify at least one of: query, genre, country, or language."
            
            result = await self._run_cli_command(command)
            
            search_params = f"query='{query}', genre='{genre}', country='{country}', language='{language}'"
            logger.info(f"Searched and played station with parameters: {search_params}")
            return f"Searched and playing station ({search_params}): {result}"
            
        except Exception as e:
            logger.error(f"Error in search and play: {e}")
            return f"Error in search and play: {str(e)}"
    
    async def advanced_search(self, name: Optional[str] = None, genre: Optional[str] = None,
                             country: Optional[str] = None, language: Optional[str] = None,
                             limit: int = 10) -> str:
        """Advanced search with multiple criteria."""
        try:
            command = ["python", "-m", "radio_player.cli", "gui-search"]
            
            # Add search parameters
            if name:
                command.extend(["--name", name])
            if genre:
                command.extend(["--tag", genre])
            if country:
                command.extend(["--country", country])
            if language:
                command.extend(["--language", language])
            
            command.extend(["--limit", str(limit)])
            
            # If no parameters provided, return error
            if not any([name, genre, country, language]):
                logger.warning("No search parameters provided for advanced_search")
                return "Error: No search parameters provided. Please specify at least one search criterion."
            
            result = await self._run_cli_command(command)
            
            search_params = f"name='{name}', genre='{genre}', country='{country}', language='{language}', limit={limit}"
            logger.info(f"Advanced search with parameters: {search_params}")
            return f"Advanced search results ({search_params}): {result}"
            
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return f"Error in advanced search: {str(e)}"