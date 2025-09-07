#!/usr/bin/env python3
"""
Application Launcher Utility for MCP Servers

Provides functionality to automatically launch GUI applications
when MCP tools are called, ensuring the target application is
running before executing commands.
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for shared_server imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_server.client import is_app_running

logger = logging.getLogger(__name__)

class AppLauncher:
    """Utility class for launching GUI applications when needed."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent  # repository root
        
        # Application configurations
        self.app_configs = {
            'browser': {
                'name': 'Browser',
                'script': 'browser/main.py',
                'check_delay': 2.0,  # seconds to wait after launch
                'max_retries': 3
            },
            'radio_player': {
                'name': 'Radio Player',
                'script': 'radio_player/main.py',
                'check_delay': 2.0,
                'max_retries': 3
            },
            'word_editor': {
                'name': 'Word Editor',
                'script': 'Words/word_editor/python_gui/main.py',
                'check_delay': 2.0,
                'max_retries': 3
            }
        }
    
    async def ensure_app_running(self, app_name: str) -> Dict[str, Any]:
        """Ensure the specified application is running, launching it if necessary.
        
        Args:
            app_name: Name of the application ('browser', 'radio_player', 'word_editor')
            
        Returns:
            Dict with success status and relevant information
        """
        if app_name not in self.app_configs:
            return {
                'success': False,
                'error': f'Unknown application: {app_name}',
                'app_name': app_name
            }
        
        config = self.app_configs[app_name]
        
        # Check if app is already running
        if is_app_running(app_name):
            logger.info(f"{config['name']} is already running")
            return {
                'success': True,
                'message': f"{config['name']} is already running",
                'app_name': app_name,
                'launched': False
            }
        
        # Launch the application
        logger.info(f"Launching {config['name']}...")
        try:
            result = await self._launch_app(app_name, config)
            return result
        except Exception as e:
            logger.error(f"Failed to launch {config['name']}: {e}")
            return {
                'success': False,
                'error': f"Failed to launch {config['name']}: {str(e)}",
                'app_name': app_name,
                'launched': False
            }
    
    async def _launch_app(self, app_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Launch the specified application.
        
        Args:
            app_name: Name of the application
            config: Application configuration
            
        Returns:
            Dict with launch result
        """
        script_path = self.base_dir / config['script']
        
        if not script_path.exists():
            return {
                'success': False,
                'error': f"Application script not found: {script_path}",
                'app_name': app_name,
                'launched': False
            }
        
        # Launch the application in the background
        try:
            # Use subprocess.Popen to launch without blocking
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(script_path.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent process
            )
            
            logger.info(f"Launched {config['name']} with PID {process.pid}")
            
            # Wait for the application to start and register with shared server
            await asyncio.sleep(config['check_delay'])
            
            # Check if the application is now running
            retries = 0
            max_retries = config['max_retries']
            
            while retries < max_retries:
                if is_app_running(app_name):
                    logger.info(f"{config['name']} successfully started and registered")
                    return {
                        'success': True,
                        'message': f"{config['name']} launched successfully",
                        'app_name': app_name,
                        'launched': True,
                        'pid': process.pid
                    }
                
                retries += 1
                if retries < max_retries:
                    logger.info(f"Waiting for {config['name']} to register... (attempt {retries + 1}/{max_retries})")
                    await asyncio.sleep(1.0)
            
            # Application launched but didn't register properly
            return {
                'success': False,
                'error': f"{config['name']} launched but failed to register with shared server",
                'app_name': app_name,
                'launched': True,
                'pid': process.pid
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to launch {config['name']}: {str(e)}",
                'app_name': app_name,
                'launched': False
            }

# Global instance for easy access
app_launcher = AppLauncher()

# Convenience functions
async def ensure_browser_running() -> Dict[str, Any]:
    """Ensure browser application is running."""
    return await app_launcher.ensure_app_running('browser')

async def ensure_radio_player_running() -> Dict[str, Any]:
    """Ensure radio player application is running."""
    return await app_launcher.ensure_app_running('radio_player')

async def ensure_word_editor_running() -> Dict[str, Any]:
    """Ensure word editor application is running."""
    return await app_launcher.ensure_app_running('word_editor')