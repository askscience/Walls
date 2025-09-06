"""Index handler for RAG MCP server operations."""

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

class IndexHandler:
    """Handles document indexing operations for RAG."""
    
    def __init__(self):
        self.rag_main_path = RAG_DIR / "main.py"
        self.data_dir = RAG_DIR / "data"
        self.chroma_db_path = RAG_DIR / "chroma_db"
    
    async def index_all_documents(self, force_reindex: bool = False) -> Dict[str, Any]:
        """Index or re-index all documents in the data directory.
        
        Args:
            force_reindex: Force re-indexing even if index exists
            
        Returns:
            Dict containing operation result and details
        """
        try:
            logger.info(f"Starting document indexing (force_reindex={force_reindex})")
            
            # Check if data directory exists
            if not self.data_dir.exists():
                return {
                    "success": False,
                    "error": f"Data directory does not exist: {self.data_dir}",
                    "suggestion": "Create the data directory and add documents to index"
                }
            
            # Check if there are documents to index
            doc_count = sum(1 for f in self.data_dir.rglob('*') if f.is_file())
            if doc_count == 0:
                return {
                    "success": False,
                    "error": "No documents found in data directory",
                    "data_dir": str(self.data_dir),
                    "suggestion": "Add documents to the data directory before indexing"
                }
            
            # Remove existing index if force_reindex is True
            if force_reindex and self.chroma_db_path.exists():
                logger.info("Removing existing index for re-indexing")
                import shutil
                shutil.rmtree(self.chroma_db_path)
            
            # Run the indexing command
            cmd = [sys.executable, str(self.rag_main_path), "--index"]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(RAG_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": "Documents indexed successfully",
                    "documents_found": doc_count,
                    "output": stdout.decode('utf-8'),
                    "index_path": str(self.chroma_db_path)
                }
            else:
                return {
                    "success": False,
                    "error": f"Indexing failed with return code {process.returncode}",
                    "stderr": stderr.decode('utf-8'),
                    "stdout": stdout.decode('utf-8')
                }
                
        except Exception as e:
            logger.error(f"Error during indexing: {str(e)}")
            return {
                "success": False,
                "error": f"Indexing operation failed: {str(e)}"
            }
    
    async def health_check(self, detailed: bool = False) -> Dict[str, Any]:
        """Perform a health check on the RAG system.
        
        Args:
            detailed: Return detailed health information
            
        Returns:
            Dict containing health status
        """
        try:
            logger.info("Performing RAG health check")
            
            # Run health check command
            cmd = [sys.executable, str(self.rag_main_path), "--health"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(RAG_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            health_status = {
                "success": process.returncode == 0,
                "rag_executable": process.returncode == 0,
                "data_dir_exists": self.data_dir.exists(),
                "index_exists": self.chroma_db_path.exists()
            }
            
            if detailed:
                health_status.update({
                    "data_dir_path": str(self.data_dir),
                    "index_path": str(self.chroma_db_path),
                    "rag_main_path": str(self.rag_main_path),
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8')
                })
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error during health check: {str(e)}")
            return {
                "success": False,
                "error": f"Health check failed: {str(e)}"
            }
    
    async def get_status(self, include_stats: bool = True) -> Dict[str, Any]:
        """Get current status of the RAG system.
        
        Args:
            include_stats: Include indexing statistics
            
        Returns:
            Dict containing system status
        """
        try:
            logger.info("Getting RAG system status")
            
            status = {
                "data_directory": str(self.data_dir),
                "data_dir_exists": self.data_dir.exists(),
                "index_directory": str(self.chroma_db_path),
                "index_exists": self.chroma_db_path.exists()
            }
            
            if include_stats:
                # Count documents in data directory
                if self.data_dir.exists():
                    doc_files = list(self.data_dir.rglob('*'))
                    status["total_files"] = len([f for f in doc_files if f.is_file()])
                    status["total_directories"] = len([f for f in doc_files if f.is_dir()])
                else:
                    status["total_files"] = 0
                    status["total_directories"] = 0
                
                # Get index size if it exists
                if self.chroma_db_path.exists():
                    try:
                        index_size = sum(f.stat().st_size for f in self.chroma_db_path.rglob('*') if f.is_file())
                        status["index_size_bytes"] = index_size
                        status["index_size_mb"] = round(index_size / (1024 * 1024), 2)
                    except Exception as e:
                        status["index_size_error"] = str(e)
            
            return {
                "success": True,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get status: {str(e)}"
            }