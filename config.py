"""
Configuration settings for the RAG application.
"""

import os

# Directory for source documents
DATA_DIR = os.path.expanduser('~')

# Path for the ChromaDB persistent storage
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')

# Name of the collection in ChromaDB
CHROMA_COLLECTION_NAME = 'rag_documents'

# Ollama embedding model
OLLAMA_EMBEDDING_MODEL = 'nomic-embed-text'

# Ollama LLM
OLLAMA_LLM_MODEL = 'deepseek-r1:1.5b'

# Timeout for Ollama requests
OLLAMA_REQUEST_TIMEOUT = 600.0

# List of glob patterns to exclude from indexing and watching
EXCLUDE_LIST = [
    "venv", "__pycache__", "node_modules", "build", "dist", "*.egg-info",
    "*.pyc", "*.pyo", "*.so", "*.a", "*.o", "chroma_db", "*.tmp", "*.temp",
    "*.bak", "*~", "*.log", "*.swp", "*.part", "*.crdownload", "*.download",
    "prefs-*.js"
]
