"""MCP Server Management"""
import json
from typing import List, Dict
from contextlib import AsyncExitStack
import os
import httpx
import asyncio
from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import timedelta


class MCPManager:
    """Manager for MCP servers, handling tool definitions and session management."""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize MCP Manager

        Args:
            ollama_url: URL of the Ollama server
        """
        self.sessions: Dict[str, ClientSession] = {}
        self.all_tools: List[dict] = []
        self.exit_stack = AsyncExitStack()
        self.ollama_url = ollama_url
        self.http_client = httpx.AsyncClient()

    async def load_servers(self, config_path: str):
        """Load and connect to all MCP servers from config"""
        config_dir = os.path.dirname(os.path.abspath(config_path))
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        
        successful_connections = 0
        total_servers = len(config['mcpServers'])
        
        for name, server_config in config['mcpServers'].items():
            resolved_config = dict(server_config)
            resolved_config['cwd'] = config_dir
            success = await self._connect_server(name, resolved_config)
            if success:
                successful_connections += 1
        
        logger.info(f"Successfully connected to {successful_connections}/{total_servers} MCP servers")
        if successful_connections == 0:
            raise RuntimeError("Failed to connect to any MCP servers")

    async def _connect_server(self, name: str, config: dict):
        """Connect to a single MCP server"""
        try:
            params = StdioServerParameters(
                command=config['command'],
                args=config['args'],
                env=config.get('env'),
                cwd=config.get('cwd')
            )
            
            # Create a new task to handle the connection in its own context
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(params))
            stdio, write = stdio_transport
            # Set MCP timeout to 600 seconds (10 minutes)
            session = await self.exit_stack.enter_async_context(
                ClientSession(stdio, write, read_timeout_seconds=timedelta(seconds=600))
            )
            await session.initialize()
            self.sessions[name] = session
            
            meta = await session.list_tools()
            for tool in meta.tools:
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": f"{name}.{tool.name}",
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    },
                    "server": name,
                    "original_name": tool.name
                }
                self.all_tools.append(tool_def)
            logger.info(f"Connected to '{name}' with {len(meta.tools)} tools")
        except Exception as e:
            logger.error(f"Failed to connect to server '{name}': {e}")
            # Don't re-raise to allow other servers to connect
            return False
        return True

    async def call_tool(self, tool_name: str, arguments: dict):
        """Call a specific tool by name with provided arguments."""
        tool_info = next((t for t in self.all_tools if t["function"]["name"] == tool_name), None)
        if not tool_info:
            raise ValueError(f"Tool {tool_name} not found")
        server_name = tool_info["server"]
        original_name = tool_info["original_name"]
        session = self.sessions[server_name]
        result = await session.call_tool(original_name, arguments)
        return result.content[0].text

    async def cleanup(self):
        """Cleanup all sessions and close HTTP client."""
        logger.info("Starting cleanup process...")
        
        # Close HTTP client first
        try:
            await self.http_client.aclose()
            logger.debug("HTTP client closed successfully")
        except Exception as e:
            logger.warning(f"Error closing HTTP client: {e}")
        
        # Clear sessions reference to help with cleanup
        self.sessions.clear()
        self.all_tools.clear()
        
        # Handle exit stack cleanup with better error handling
        try:
            # Use asyncio.shield to protect the cleanup from cancellation
            await asyncio.shield(self.exit_stack.aclose())
            logger.debug("Exit stack closed successfully")
        except asyncio.CancelledError:
            logger.warning("Cleanup was cancelled, but this is expected during shutdown")
        except RuntimeError as e:
            if "cancel scope" in str(e) or "different task" in str(e):
                logger.warning(f"AsyncIO context issue during cleanup (this is expected during shutdown): {e}")
            else:
                logger.error(f"Runtime error during cleanup: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during cleanup: {e}")
        
        logger.info("Cleanup process completed")
