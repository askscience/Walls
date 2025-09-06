"""Watch handler for RAG MCP server operations."""

import os
import sys
import subprocess
import asyncio
import signal
from typing import Dict, Any, Optional
from pathlib import Path

# Add the rag directory to Python path
RAG_DIR = Path(__file__).parent.parent.parent.parent / "rag"
sys.path.insert(0, str(RAG_DIR))

from utils.logger import setup_logger

logger = setup_logger(__name__)

class WatchHandler:
    """Handles file watching operations for RAG."""
    
    def __init__(self):
        self.rag_main_path = RAG_DIR / "main.py"
        self.data_dir = RAG_DIR / "data"
        self.watch_process: Optional[asyncio.subprocess.Process] = None
        self.is_watching = False
    
    async def start_watching(self, watch_directory: Optional[str] = None) -> Dict[str, Any]:
        """Start watching the data directory for changes.
        
        Args:
            watch_directory: Directory to watch (defaults to data directory)
            
        Returns:
            Dict containing operation result
        """
        try:
            logger.info("Starting file watching")
            
            # Check if already watching
            if self.is_watching and self.watch_process:
                return {
                    "success": False,
                    "error": "File watching is already active",
                    "suggestion": "Use rag_stop_watching to stop current watching before starting new one"
                }
            
            # Determine watch directory
            if watch_directory:
                watch_path = Path(watch_directory)
                if not watch_path.exists():
                    return {
                        "success": False,
                        "error": f"Watch directory does not exist: {watch_directory}"
                    }
            else:
                watch_path = self.data_dir
            
            # Ensure data directory exists
            if not watch_path.exists():
                watch_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created watch directory: {watch_path}")
            
            # Start the watch command
            cmd = [sys.executable, str(self.rag_main_path), "--watch"]
            logger.info(f"Starting watch command: {' '.join(cmd)}")
            
            self.watch_process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(RAG_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            self.is_watching = True
            
            # Give the process a moment to start
            await asyncio.sleep(1)
            
            # Check if process is still running
            if self.watch_process.returncode is not None:
                # Process has already terminated
                stdout, stderr = await self.watch_process.communicate()
                self.is_watching = False
                self.watch_process = None
                
                return {
                    "success": False,
                    "error": f"Watch process terminated immediately (return code {self.watch_process.returncode})",
                    "stderr": stderr.decode('utf-8'),
                    "stdout": stdout.decode('utf-8')
                }
            
            return {
                "success": True,
                "message": "File watching started successfully",
                "watch_directory": str(watch_path),
                "process_id": self.watch_process.pid,
                "instructions": [
                    "The system is now monitoring the data directory for changes",
                    "Files added, modified, or deleted will automatically update the index",
                    "Use rag_stop_watching to stop the file watcher"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error starting file watching: {str(e)}")
            self.is_watching = False
            self.watch_process = None
            return {
                "success": False,
                "error": f"Failed to start file watching: {str(e)}"
            }
    
    async def stop_watching(self) -> Dict[str, Any]:
        """Stop watching the data directory.
        
        Returns:
            Dict containing operation result
        """
        try:
            logger.info("Stopping file watching")
            
            if not self.is_watching or not self.watch_process:
                return {
                    "success": False,
                    "error": "File watching is not currently active",
                    "suggestion": "Use rag_start_watching to start file watching"
                }
            
            # Try to terminate the process gracefully
            try:
                if hasattr(os, 'killpg'):
                    # Kill the entire process group (Unix-like systems)
                    os.killpg(os.getpgid(self.watch_process.pid), signal.SIGTERM)
                else:
                    # Fallback for systems without process groups
                    self.watch_process.terminate()
                
                # Wait for process to terminate
                try:
                    await asyncio.wait_for(self.watch_process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Force kill if it doesn't terminate gracefully
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(self.watch_process.pid), signal.SIGKILL)
                    else:
                        self.watch_process.kill()
                    await self.watch_process.wait()
                
                return_code = self.watch_process.returncode
                
            except ProcessLookupError:
                # Process was already terminated
                return_code = 0
            except Exception as e:
                logger.warning(f"Error terminating watch process: {str(e)}")
                return_code = -1
            
            finally:
                self.is_watching = False
                self.watch_process = None
            
            return {
                "success": True,
                "message": "File watching stopped successfully",
                "return_code": return_code
            }
            
        except Exception as e:
            logger.error(f"Error stopping file watching: {str(e)}")
            # Reset state even if there was an error
            self.is_watching = False
            self.watch_process = None
            return {
                "success": False,
                "error": f"Failed to stop file watching: {str(e)}"
            }
    
    def get_watch_status(self) -> Dict[str, Any]:
        """Get current file watching status.
        
        Returns:
            Dict containing watch status
        """
        return {
            "is_watching": self.is_watching,
            "process_id": self.watch_process.pid if self.watch_process else None,
            "watch_directory": str(self.data_dir)
        }
    
    async def cleanup(self):
        """Cleanup method to ensure watch process is stopped."""
        if self.is_watching and self.watch_process:
            await self.stop_watching()