"""Volume handler for Radio Player MCP server."""

import asyncio
from typing import Dict, Any, Optional

from utils import setup_logger

logger = setup_logger(__name__)

class VolumeHandler:
    """Handler for radio player volume control operations."""
    
    def __init__(self):
        # Get the base path dynamically - go up 3 levels from MCP/radio_player/handlers/
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self._current_volume = None
        self._is_muted = False
        self._volume_before_mute = None
    
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
    
    async def set_volume(self, level: int) -> str:
        """Set playback volume (0-100)."""
        try:
            # Validate volume level
            if not 0 <= level <= 100:
                error_msg = f"Volume level must be between 0 and 100, got {level}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
            
            # Use the control volume command
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "volume",
                "--level", str(level)
            ])
            
            # Update internal state
            self._current_volume = level
            if level > 0:
                self._is_muted = False
            
            logger.info(f"Set volume to {level}%")
            return f"Volume set to {level}%: {result}"
            
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return f"Error setting volume: {str(e)}"
    
    async def get_volume(self) -> str:
        """Get current volume level.
        
        Note: The CLI doesn't currently support getting volume directly.
        This returns the last known volume level from this session.
        """
        try:
            if self._current_volume is not None:
                status = "muted" if self._is_muted else "active"
                return f"Current volume: {self._current_volume}% ({status})"
            else:
                # Try to get status which might include volume info
                status_result = await self._run_cli_command([
                    "python", "-m", "radio_player.cli", "control", "status"
                ])
                return f"Volume info not available directly. Status: {status_result}"
            
        except Exception as e:
            logger.error(f"Error getting volume: {e}")
            return f"Error getting volume: {str(e)}"
    
    async def mute_audio(self) -> str:
        """Mute audio output.
        
        Note: The CLI doesn't have a direct mute command, so we set volume to 0.
        """
        try:
            # Store current volume before muting
            if self._current_volume is not None and self._current_volume > 0:
                self._volume_before_mute = self._current_volume
            elif self._volume_before_mute is None:
                # Default to 50% if we don't know the previous volume
                self._volume_before_mute = 50
            
            # Set volume to 0
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "volume",
                "--level", "0"
            ])
            
            # Update internal state
            self._current_volume = 0
            self._is_muted = True
            
            logger.info("Audio muted (volume set to 0)")
            return f"Audio muted: {result}"
            
        except Exception as e:
            logger.error(f"Error muting audio: {e}")
            return f"Error muting audio: {str(e)}"
    
    async def unmute_audio(self) -> str:
        """Unmute audio output.
        
        Note: This restores the volume to the level before muting.
        """
        try:
            if not self._is_muted:
                return "Audio is not currently muted"
            
            # Restore previous volume or default to 50%
            restore_volume = self._volume_before_mute or 50
            
            result = await self._run_cli_command([
                "python", "-m", "radio_player.cli", "control", "volume",
                "--level", str(restore_volume)
            ])
            
            # Update internal state
            self._current_volume = restore_volume
            self._is_muted = False
            
            logger.info(f"Audio unmuted (volume restored to {restore_volume}%)")
            return f"Audio unmuted, volume restored to {restore_volume}%: {result}"
            
        except Exception as e:
            logger.error(f"Error unmuting audio: {e}")
            return f"Error unmuting audio: {str(e)}"
    
    async def toggle_mute(self) -> str:
        """Toggle mute state."""
        try:
            if self._is_muted:
                return await self.unmute_audio()
            else:
                return await self.mute_audio()
                
        except Exception as e:
            logger.error(f"Error toggling mute: {e}")
            return f"Error toggling mute: {str(e)}"
    
    async def get_mute_status(self) -> str:
        """Get current mute status."""
        try:
            status = "muted" if self._is_muted else "unmuted"
            volume_info = f" (volume: {self._current_volume}%)" if self._current_volume is not None else ""
            return f"Audio is currently {status}{volume_info}"
            
        except Exception as e:
            logger.error(f"Error getting mute status: {e}")
            return f"Error getting mute status: {str(e)}"