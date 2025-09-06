"""Document handler for RAG MCP server operations."""

import os
import sys
import subprocess
import asyncio
import shutil
from typing import Dict, Any
from pathlib import Path

# Add the rag directory to Python path
RAG_DIR = Path(__file__).parent.parent.parent.parent / "rag"
sys.path.insert(0, str(RAG_DIR))

from utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentHandler:
    """Handles individual document operations for RAG."""
    
    def __init__(self):
        self.rag_main_path = RAG_DIR / "main.py"
        self.data_dir = RAG_DIR / "data"
        self.chroma_db_path = RAG_DIR / "chroma_db"
    
    async def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a new document to the index.
        
        Args:
            file_path: Path to the document file to add
            
        Returns:
            Dict containing operation result
        """
        try:
            logger.info(f"Adding document: {file_path}")
            
            # Validate file path
            if not file_path:
                return {
                    "success": False,
                    "error": "File path cannot be empty"
                }
            
            source_path = Path(file_path)
            
            # Check if source file exists
            if not source_path.exists():
                return {
                    "success": False,
                    "error": f"Source file does not exist: {file_path}"
                }
            
            # Check if it's a file (not a directory)
            if not source_path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}"
                }
            
            # Ensure data directory exists
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine destination path in data directory
            dest_path = self.data_dir / source_path.name
            
            # Check if file already exists in data directory
            if dest_path.exists():
                return {
                    "success": False,
                    "error": f"File already exists in data directory: {dest_path}",
                    "suggestion": "Use a different filename or delete the existing file first"
                }
            
            # Copy file to data directory
            try:
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied file to: {dest_path}")
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to copy file to data directory: {str(e)}"
                }
            
            # Run the add command
            cmd = [sys.executable, str(self.rag_main_path), "--add", str(dest_path)]
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
                    "message": "Document added successfully",
                    "source_path": str(source_path),
                    "dest_path": str(dest_path),
                    "output": stdout.decode('utf-8')
                }
            else:
                # If indexing failed, remove the copied file
                if dest_path.exists():
                    dest_path.unlink()
                
                return {
                    "success": False,
                    "error": f"Failed to add document to index (return code {process.returncode})",
                    "stderr": stderr.decode('utf-8'),
                    "stdout": stdout.decode('utf-8')
                }
                
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return {
                "success": False,
                "error": f"Document add operation failed: {str(e)}"
            }
    
    async def delete_document(self, file_path: str) -> Dict[str, Any]:
        """Delete a document from the index.
        
        Args:
            file_path: Path to the document file to delete
            
        Returns:
            Dict containing operation result
        """
        try:
            logger.info(f"Deleting document: {file_path}")
            
            # Validate file path
            if not file_path:
                return {
                    "success": False,
                    "error": "File path cannot be empty"
                }
            
            # Check if index exists
            if not self.chroma_db_path.exists():
                return {
                    "success": False,
                    "error": "No index found. Cannot delete document from non-existent index.",
                    "suggestion": "Create an index first using rag_index_all"
                }
            
            # Convert to Path object
            target_path = Path(file_path)
            
            # If it's a relative path, assume it's relative to data directory
            if not target_path.is_absolute():
                target_path = self.data_dir / target_path
            
            # Run the delete command
            cmd = [sys.executable, str(self.rag_main_path), "--delete", str(target_path)]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(RAG_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "file_path": str(target_path),
                "output": stdout.decode('utf-8')
            }
            
            if process.returncode == 0:
                result.update({
                    "success": True,
                    "message": "Document deleted from index successfully"
                })
                
                # Also remove the file from data directory if it exists there
                if target_path.exists() and target_path.parent == self.data_dir:
                    try:
                        target_path.unlink()
                        result["file_removed"] = True
                        result["message"] += " and file removed from data directory"
                    except Exception as e:
                        result["file_removal_warning"] = f"Could not remove file from data directory: {str(e)}"
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"Failed to delete document from index (return code {process.returncode})",
                    "stderr": stderr.decode('utf-8'),
                    "stdout": stdout.decode('utf-8'),
                    "file_path": str(target_path)
                }
                
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return {
                "success": False,
                "error": f"Document delete operation failed: {str(e)}"
            }