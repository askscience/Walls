#!/usr/bin/env python3
"""
MCP Server Manager

Manages MCP (Model Context Protocol) servers including:
- Starting and stopping MCP servers
- Port allocation and management
- Process monitoring
- Configuration management
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from .config import ServerConfig

logger = logging.getLogger(__name__)

class MCPManager:
    """Manager for MCP servers."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.base_dir = Path(__file__).parent.parent  # repository root
    
    def get_mcp_servers(self) -> Dict[str, Any]:
        """Get all MCP server configurations."""
        return self.config.get_mcp_servers()
    
    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get the status of an MCP server."""
        server_config = self.config.get_mcp_server_config(server_name)
        if not server_config:
            return {"status": "not_configured", "enabled": False}
        
        process = self.running_processes.get(server_name)
        is_running = False
        process_id = None
        
        if process is not None and process.poll() is None:
            # Process is in memory and running
            is_running = True
            process_id = process.pid
        else:
            # Check if there's a saved PID that's still running
            saved_pid = server_config.get("process_id")
            if saved_pid:
                try:
                    # Check if process with saved PID is still running
                    os.kill(saved_pid, 0)  # Signal 0 just checks if process exists
                    is_running = True
                    process_id = saved_pid
                except (OSError, ProcessLookupError):
                    # Process is not running, clear the saved PID
                    self.config.set_mcp_server_process_id(server_name, None)
        
        return {
            "status": "running" if is_running else "stopped",
            "enabled": server_config.get("enabled", False),
            "port": server_config.get("port"),
            "process_id": process_id,
            "description": server_config.get("description", ""),
            "capabilities": server_config.get("capabilities", [])
        }
    
    def start_server(self, server_name: str) -> bool:
        """Start an MCP server."""
        server_config = self.config.get_mcp_server_config(server_name)
        if not server_config:
            logger.error(f"No configuration found for MCP server: {server_name}")
            return False
        
        if not server_config.get("enabled", False):
            logger.warning(f"MCP server {server_name} is disabled")
            return False
        
        # Check if already running
        if server_name in self.running_processes:
            process = self.running_processes[server_name]
            if process.poll() is None:  # Still running
                logger.info(f"MCP server {server_name} is already running")
                return True
            else:
                # Process died, remove it
                del self.running_processes[server_name]
        
        # Get server path
        server_path = self.base_dir / server_config["path"]
        if not server_path.exists():
            logger.error(f"MCP server script not found: {server_path}")
            return False
        
        try:
            # Start the MCP server process
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.base_dir)
            
            # Convert path to module format (e.g., ./MCP/radio_player/server.py -> MCP.radio_player.server)
            relative_path = server_path.relative_to(self.base_dir)
            module_path = str(relative_path.with_suffix('')).replace('/', '.')
            
            process = subprocess.Popen(
                [sys.executable, '-m', module_path],
                cwd=str(self.base_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_processes[server_name] = process
            logger.info(f"Started MCP server {server_name} with PID {process.pid}")
            
            # Save the PID to config
            logger.info(f"Saving PID {process.pid} for server {server_name}")
            self.config.set_mcp_server_process_id(server_name, process.pid)
            logger.info(f"PID saved successfully for server {server_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server {server_name}: {e}")
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """Stop an MCP server."""
        if server_name not in self.running_processes:
            logger.info(f"MCP server {server_name} is not running")
            return True
        
        process = self.running_processes[server_name]
        
        try:
            # Try graceful shutdown first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                logger.warning(f"Force killing MCP server {server_name}")
                process.kill()
                process.wait()
            
            del self.running_processes[server_name]
            self.config.set_mcp_server_process_id(server_name, None)
            
            logger.info(f"Stopped MCP server {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop MCP server {server_name}: {e}")
            return False
    
    def restart_server(self, server_name: str) -> bool:
        """Restart an MCP server."""
        logger.info(f"Restarting MCP server {server_name}")
        self.stop_server(server_name)
        return self.start_server(server_name)
    
    def start_all_enabled(self) -> Dict[str, bool]:
        """Start all enabled MCP servers."""
        results = {}
        mcp_servers = self.get_mcp_servers()
        
        for server_name, server_config in mcp_servers.items():
            if server_config.get("enabled", False):
                results[server_name] = self.start_server(server_name)
            else:
                results[server_name] = False
        
        return results
    
    def stop_all(self) -> Dict[str, bool]:
        """Stop all running MCP servers."""
        results = {}
        
        for server_name in list(self.running_processes.keys()):
            results[server_name] = self.stop_server(server_name)
        
        return results
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP servers."""
        status = {}
        mcp_servers = self.get_mcp_servers()
        
        for server_name in mcp_servers.keys():
            status[server_name] = self.get_server_status(server_name)
        
        return status
    
    def enable_server(self, server_name: str) -> bool:
        """Enable an MCP server."""
        server_config = self.config.get_mcp_server_config(server_name)
        if not server_config:
            logger.error(f"No configuration found for MCP server: {server_name}")
            return False
        
        self.config.enable_mcp_server(server_name)
        logger.info(f"Enabled MCP server {server_name}")
        return True
    
    def disable_server(self, server_name: str) -> bool:
        """Disable an MCP server."""
        server_config = self.config.get_mcp_server_config(server_name)
        if not server_config:
            logger.error(f"No configuration found for MCP server: {server_name}")
            return False
        
        # Stop the server if it's running
        if server_name in self.running_processes:
            self.stop_server(server_name)
        
        self.config.disable_mcp_server(server_name)
        logger.info(f"Disabled MCP server {server_name}")
        return True
    
    def cleanup(self):
        """Clean up all running processes."""
        logger.info("Cleaning up MCP servers...")
        self.stop_all()