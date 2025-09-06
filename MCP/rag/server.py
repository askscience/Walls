#!/usr/bin/env python3
"""
RAG MCP Server

Provides MCP tools for controlling the RAG application including:
- Document indexing operations (index, add, delete)
- Query operations (query, interactive)
- File watching and management
- Health checks and status
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
# stdio_server will be imported in main()
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from handlers.index_handler import IndexHandler
from handlers.query_handler import QueryHandler
from handlers.document_handler import DocumentHandler
from handlers.watch_handler import WatchHandler
from utils.logger import setup_logger
from schemas.tool_schemas import TOOL_SCHEMAS

# Setup logging
logger = setup_logger(__name__)

# Initialize server
server = Server("rag")

# Initialize handlers
index_handler = IndexHandler()
query_handler = QueryHandler()
document_handler = DocumentHandler()
watch_handler = WatchHandler()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for RAG operations."""
    tools = [
        # Index operation tools
        Tool(
            name="rag_index_all",
            description="Index or re-index all documents in the data directory",
            inputSchema=TOOL_SCHEMAS["rag_index_all"]
        ),
        Tool(
            name="rag_add_document",
            description="Add a new document to the index",
            inputSchema=TOOL_SCHEMAS["rag_add_document"]
        ),
        Tool(
            name="rag_delete_document",
            description="Delete a document from the index",
            inputSchema=TOOL_SCHEMAS["rag_delete_document"]
        ),
        
        # Query operation tools
        Tool(
            name="rag_query",
            description="Run a query against the indexed documents",
            inputSchema=TOOL_SCHEMAS["rag_query"]
        ),
        Tool(
            name="rag_interactive_query",
            description="Start interactive query mode",
            inputSchema=TOOL_SCHEMAS["rag_interactive_query"]
        ),
        
        # File watching tools
        Tool(
            name="rag_start_watching",
            description="Start watching the data directory for changes",
            inputSchema=TOOL_SCHEMAS["rag_start_watching"]
        ),
        Tool(
            name="rag_stop_watching",
            description="Stop watching the data directory",
            inputSchema=TOOL_SCHEMAS["rag_stop_watching"]
        ),
        
        # Status and health tools
        Tool(
            name="rag_health_check",
            description="Perform a health check on the RAG system",
            inputSchema=TOOL_SCHEMAS["rag_health_check"]
        ),
        Tool(
            name="rag_get_status",
            description="Get current status of the RAG system",
            inputSchema=TOOL_SCHEMAS["rag_get_status"]
        )
    ]
    
    logger.info(f"Listed {len(tools)} available tools")
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for RAG operations."""
    try:
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        
        # Index operations
        if name == "rag_index_all":
            result = await index_handler.index_all_documents()
        elif name == "rag_add_document":
            result = await document_handler.add_document(arguments.get("file_path"))
        elif name == "rag_delete_document":
            result = await document_handler.delete_document(arguments.get("file_path"))
        
        # Query operations
        elif name == "rag_query":
            result = await query_handler.run_query(arguments.get("query"))
        elif name == "rag_interactive_query":
            result = await query_handler.start_interactive_mode()
        
        # File watching operations
        elif name == "rag_start_watching":
            result = await watch_handler.start_watching()
        elif name == "rag_stop_watching":
            result = await watch_handler.stop_watching()
        
        # Status operations
        elif name == "rag_health_check":
            result = await index_handler.health_check()
        elif name == "rag_get_status":
            result = await index_handler.get_status()
        
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    }, indent=2)
                )
            ],
            isError=True
        )

async def main():
    """Main function to run the RAG MCP server."""
    logger.info("Starting RAG MCP Server...")
    
    # Import and run the server using MCP's standard approach
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rag",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())