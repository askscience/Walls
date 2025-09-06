"""Query handler for RAG MCP server operations."""

import os
import sys
import subprocess
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# Add the rag directory to Python path
RAG_DIR = Path(__file__).parent.parent.parent.parent / "rag"
sys.path.insert(0, str(RAG_DIR))

from utils.logger import setup_logger

logger = setup_logger(__name__)

class QueryHandler:
    """Handles query operations for RAG."""
    
    def __init__(self):
        self.rag_main_path = RAG_DIR / "main.py"
        self.chroma_db_path = RAG_DIR / "chroma_db"
    
    async def run_query(self, query: str, max_results: int = 5, include_metadata: bool = True) -> Dict[str, Any]:
        """Run a query against the indexed documents.
        
        Args:
            query: The query string to search for
            max_results: Maximum number of results to return
            include_metadata: Include document metadata in results
            
        Returns:
            Dict containing query results
        """
        try:
            logger.info(f"Running query: {query[:100]}...")
            
            # Check if index exists
            if not self.chroma_db_path.exists():
                return {
                    "success": False,
                    "error": "No index found. Please run indexing first.",
                    "suggestion": "Use rag_index_all to create an index before querying"
                }
            
            # Validate query
            if not query or not query.strip():
                return {
                    "success": False,
                    "error": "Query cannot be empty"
                }
            
            # Run the query command
            cmd = [sys.executable, str(self.rag_main_path), "--query", query.strip()]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(RAG_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode('utf-8')
                
                # Parse the output to extract the answer and sources
                result = {
                    "success": True,
                    "query": query,
                    "answer": output,
                    "max_results_requested": max_results
                }
                
                if include_metadata:
                    # Try to extract source information from the output
                    # This is a simple parsing - could be enhanced based on actual output format
                    if "Source:" in output or "File:" in output:
                        lines = output.split('\n')
                        sources = []
                        for line in lines:
                            if line.strip().startswith(('Source:', 'File:')):
                                sources.append(line.strip())
                        result["sources"] = sources
                
                return result
            else:
                error_output = stderr.decode('utf-8')
                return {
                    "success": False,
                    "error": f"Query failed with return code {process.returncode}",
                    "stderr": error_output,
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"Error during query: {str(e)}")
            return {
                "success": False,
                "error": f"Query operation failed: {str(e)}",
                "query": query
            }
    
    async def start_interactive_mode(self, initial_query: Optional[str] = None) -> Dict[str, Any]:
        """Start interactive query mode.
        
        Args:
            initial_query: Optional initial query to start with
            
        Returns:
            Dict containing interactive mode status
        """
        try:
            logger.info("Starting interactive query mode")
            
            # Check if index exists
            if not self.chroma_db_path.exists():
                return {
                    "success": False,
                    "error": "No index found. Please run indexing first.",
                    "suggestion": "Use rag_index_all to create an index before starting interactive mode"
                }
            
            # For MCP server, we can't really start a true interactive mode
            # Instead, we'll provide information about how to use interactive mode
            result = {
                "success": True,
                "message": "Interactive mode information",
                "instructions": [
                    "Interactive mode allows continuous querying of the RAG system",
                    "To use interactive mode directly, run: python rag/main.py",
                    "For MCP integration, use the rag_query tool for individual queries"
                ],
                "available_commands": [
                    "Type your questions and press Enter",
                    "Type 'quit' or 'exit' to leave interactive mode",
                    "Type 'help' for more information"
                ]
            }
            
            # If an initial query is provided, run it
            if initial_query and initial_query.strip():
                logger.info(f"Running initial query: {initial_query}")
                query_result = await self.run_query(initial_query)
                result["initial_query_result"] = query_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error starting interactive mode: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to start interactive mode: {str(e)}"
            }