"""MCP Server Management"""
import json
from typing import List, Dict, Optional
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
        self.ollama_url = ollama_url
        self.http_client = httpx.AsyncClient()

        # Internal task-runner to own AsyncExitStack and manage enter/exit in the same task
        self._runner_task: Optional[asyncio.Task] = None
        self._actions: Optional[asyncio.Queue] = None
        self._stack_ready: Optional[asyncio.Event] = None
        self._shutdown_complete: Optional[asyncio.Event] = None

    async def _ensure_runner(self):
        if self._runner_task is None or self._runner_task.done():
            self._actions = asyncio.Queue()
            self._stack_ready = asyncio.Event()
            self._shutdown_complete = asyncio.Event()
            self._runner_task = asyncio.create_task(self._stack_runner(), name="MCPManagerStackRunner")
            await self._stack_ready.wait()

    async def _stack_runner(self):
        """Background task that owns the AsyncExitStack and manages server connections."""
        stack = AsyncExitStack()
        try:
            # Signal that stack is ready to accept actions
            self._stack_ready.set()
            while True:
                action = await self._actions.get()
                if action["type"] == "connect":
                    name: str = action["name"]
                    config: dict = action["config"]
                    fut: asyncio.Future = action["future"]
                    try:
                        params = StdioServerParameters(
                            command=config['command'],
                            args=config['args'],
                            env=config.get('env'),
                            cwd=config.get('cwd')
                        )
                        # Enter stdio_client and ClientSession in the SAME task that will later close them
                        stdio_transport = await stack.enter_async_context(stdio_client(params))
                        stdio, write = stdio_transport
                        session = await stack.enter_async_context(
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
                        fut.set_result(True)
                    except Exception as e:
                        logger.error(f"Failed to connect to server '{name}': {e}")
                        fut.set_result(False)
                elif action["type"] == "shutdown":
                    break
                else:
                    logger.warning(f"Unknown action type: {action['type']}")
        except Exception as e:
            logger.error(f"Stack runner encountered an error: {e}")
        finally:
            # Always close the stack in the SAME task to avoid anyio cancel scope issues
            try:
                await stack.aclose()
                logger.debug("Exit stack closed successfully (runner)")
            except asyncio.CancelledError:
                logger.warning("Runner cleanup was cancelled (expected during shutdown)")
            except RuntimeError as e:
                if "cancel scope" in str(e) or "different task" in str(e):
                    logger.warning(f"AsyncIO context issue during runner cleanup (expected): {e}")
                else:
                    logger.error(f"Runtime error during runner cleanup: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during runner cleanup: {e}")
            finally:
                if self._shutdown_complete:
                    self._shutdown_complete.set()

    async def load_servers(self, config_path: str):
        """Load and connect to all MCP servers from config"""
        await self._ensure_runner()
        config_dir = os.path.dirname(os.path.abspath(config_path))
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        
        successful_connections = 0
        total_servers = len(config['mcpServers'])
        
        for name, server_config in config['mcpServers'].items():
            resolved_config = dict(server_config)
            resolved_config['cwd'] = config_dir
            # Ask runner to connect so that enter happens in the runner task
            loop = asyncio.get_running_loop()
            fut: asyncio.Future = loop.create_future()
            await self._actions.put({
                "type": "connect",
                "name": name,
                "config": resolved_config,
                "future": fut,
            })
            success = await fut
            if success:
                successful_connections += 1
        
        logger.info(f"Successfully connected to {successful_connections}/{total_servers} MCP servers")
        if successful_connections == 0:
            raise RuntimeError("Failed to connect to any MCP servers")

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
        
        # Signal runner to shutdown so it can close the AsyncExitStack in the same task
        if self._actions and self._runner_task and not self._runner_task.done():
            try:
                await self._actions.put({"type": "shutdown"})
                # Wait for stack to close
                if self._shutdown_complete:
                    await self._shutdown_complete.wait()
                # Ensure task completes
                await self._runner_task
            except Exception as e:
                logger.warning(f"Error while waiting for runner to shutdown: {e}")
        
        logger.info("Cleanup process completed")
