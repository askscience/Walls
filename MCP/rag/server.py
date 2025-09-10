#!/usr/bin/env python3
"""
RAG MCP Server using FastMCP

Provides MCP tools for controlling the RAG application including:
- Document indexing operations (index, add, delete)
- Query operations (query, interactive)
- File watching and management
- Health checks and status
"""

import json
import logging
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from mcp.types import TextContent, Tool

from handlers.index_handler import IndexHandler
from handlers.query_handler import QueryHandler
from handlers.document_handler import DocumentHandler
from handlers.watch_handler import WatchHandler
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Initialize FastMCP
mcp = FastMCP("RAG")

# Initialize handlers
index_handler = IndexHandler()
query_handler = QueryHandler()
document_handler = DocumentHandler()
watch_handler = WatchHandler()

def handle_rag_operation(handler_method, *args, **kwargs):
    """Execute RAG operation and format result."""
    try:
        result = handler_method(*args, **kwargs)
        return [{"type": "text", "text": json.dumps(result, indent=2)}]
    except Exception as e:
        logger.error(f"Error in RAG operation: {e}")
        error_result = {
            "success": False,
            "error": str(e)
        }
        return [{"type": "text", "text": json.dumps(error_result, indent=2)}]

# Index operation tools
@mcp.tool()
def rag_index_all() -> List[Dict[str, Any]]:
    """Index or re-index all documents in the data directory."""
    return handle_rag_operation(index_handler.index_all_documents)

@mcp.tool()
def rag_add_document(file_path: str) -> List[Dict[str, Any]]:
    """Add a new document to the index."""
    return handle_rag_operation(document_handler.add_document, file_path)

@mcp.tool()
def rag_delete_document(file_path: str) -> List[Dict[str, Any]]:
    """Delete a document from the index."""
    return handle_rag_operation(document_handler.delete_document, file_path)

# Query operation tools
@mcp.tool()
def rag_query(query: str) -> List[Dict[str, Any]]:
    """Run a query against the indexed documents."""
    return handle_rag_operation(query_handler.run_query, query)

@mcp.tool()
def rag_interactive_query() -> List[Dict[str, Any]]:
    """Start interactive query mode."""
    return handle_rag_operation(query_handler.start_interactive_mode)

# File watching tools
@mcp.tool()
def rag_start_watching() -> List[Dict[str, Any]]:
    """Start watching the data directory for changes."""
    return handle_rag_operation(watch_handler.start_watching)

@mcp.tool()
def rag_stop_watching() -> List[Dict[str, Any]]:
    """Stop watching the data directory."""
    return handle_rag_operation(watch_handler.stop_watching)

# Status and health tools
@mcp.tool()
def rag_health_check() -> List[Dict[str, Any]]:
    """Perform a health check on the RAG system."""
    return handle_rag_operation(index_handler.health_check)

@mcp.tool()
def rag_get_status() -> List[Dict[str, Any]]:
    """Get current status of the RAG system."""
    return handle_rag_operation(index_handler.get_status)

if __name__ == "__main__":
    logger.info("Starting RAG MCP Server with FastMCP...")
    mcp.run()