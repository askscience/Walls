"""
Main entry point for the RAG application.
Handles command-line arguments for indexing, querying, and managing documents.
"""

import argparse
import sys
import re
import subprocess
import os

from llama_index.core import SimpleDirectoryReader

# Command interception functionality removed - now using MCP servers

import json

def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Convert relative paths to absolute paths
    config['data_dir'] = os.path.join(os.path.dirname(__file__), config['data_dir'])
    config['chroma_db_path'] = os.path.join(os.path.dirname(__file__), config['chroma_db_path'])
    
    return config

# Load configuration
config = load_config()
DATA_DIR = config['data_dir']
CHROMA_DB_PATH = config['chroma_db_path']
CHROMA_COLLECTION_NAME = config['chroma_collection_name']
OLLAMA_LLM_MODEL = config['ollama_llm_model']
OLLAMA_EMBEDDING_MODEL = config['ollama_embedding_model']
OLLAMA_REQUEST_TIMEOUT = config['ollama_request_timeout']
EXCLUDE_LIST = config['exclude_list']
LLM_MODEL_PARAMS = config['llm_model_params']
from data_loader import load_documents
from embedding_llm_setup import setup_ollama_models, setup_mcp_enabled_rag
from vector_store_manager import VectorStoreManager
from rag_pipeline import setup_rag_query_engine
from file_watcher import start_watching

SAFE_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SAFE_RAG_MAIN = os.path.abspath(__file__)


# Command execution is now handled by centralized command_utils.py
# This eliminates code duplication and ensures consistent behavior across all applications


def main():
    """
    Main function to run the RAG application.
    """
    parser = argparse.ArgumentParser(description="RAG Application using LlamaIndex, Ollama, and ChromaDB")
    parser.add_argument("--index", action="store_true", help="Index or re-index all documents in the data directory.")
    parser.add_argument("--query", type=str, help="Run a specific query.")
    parser.add_argument("--add", type=str, help="Add a new file to the index. Provide the file path.")
    parser.add_argument("--delete", type=str, help="Delete a document from the index by its file path.")
    parser.add_argument("--watch", action="store_true", help="Watch the data directory for changes and update the index automatically.")
    parser.add_argument("--health", action="store_true", help="Lightweight health check; exits immediately if CLI is callable.")
    args = parser.parse_args()

    # Fast health check path (avoid heavy initialization)
    if args.health:
        print("OK")
        return

    # Setup Ollama models
    llm, embedding_model = setup_ollama_models(
        OLLAMA_LLM_MODEL, OLLAMA_EMBEDDING_MODEL, OLLAMA_REQUEST_TIMEOUT, LLM_MODEL_PARAMS
    )

    # Initialize VectorStoreManager
    vector_store_manager = VectorStoreManager(
        CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, embedding_model
    )

    if args.watch:
        print("Starting file watcher...")
        start_watching(DATA_DIR, vector_store_manager, EXCLUDE_LIST)

    elif args.index:
        print("Starting indexing process...")
        documents = load_documents(DATA_DIR)
        vector_store_manager.create_or_load_index(documents)
        print("Indexing complete.")

    elif args.add:
        print(f"Adding new file: {args.add}")
        new_docs = SimpleDirectoryReader(input_files=[args.add]).load_data()
        vector_store_manager.add_documents(new_docs)

    elif args.delete:
        print(f"Deleting document: {args.delete}")
        vector_store_manager.delete_documents_by_path([args.delete])

    elif args.query:
        print("Loading MCP-enabled RAG pipeline for querying...")
        index = vector_store_manager.create_or_load_index()
        
        # Use MCP-enabled RAG pipeline for tool calling capabilities
        mcp_pipeline = setup_mcp_enabled_rag(
            index, 
            OLLAMA_LLM_MODEL, 
            OLLAMA_EMBEDDING_MODEL, 
            OLLAMA_REQUEST_TIMEOUT, 
            LLM_MODEL_PARAMS
        )
        
        print(f"Query: {args.query}")
        print("Asking LLM with MCP tool calling...")
        response_text = mcp_pipeline.query_sync(args.query, OLLAMA_LLM_MODEL)
        print(f"Response:\n{response_text}")
        
        # MCP servers now handle all tool calling including radio search

    else:
        print("No specific action requested. Starting interactive query mode.")
        print("Type 'exit' to quit.")
        
        try:
            index = vector_store_manager.create_or_load_index()
            
            # Use MCP-enabled RAG pipeline for interactive mode
            mcp_pipeline = setup_mcp_enabled_rag(
                index, 
                OLLAMA_LLM_MODEL, 
                OLLAMA_EMBEDDING_MODEL, 
                OLLAMA_REQUEST_TIMEOUT, 
                LLM_MODEL_PARAMS
            )
            
            print(f"Available MCP tools: {list(mcp_pipeline.get_available_tools().keys())}")
            
            while True:
                query = input("Enter your query: ")
                if query.lower() == 'exit':
                    break
                print("Asking LLM with MCP tool calling...")
                response_text = mcp_pipeline.query_sync(query, OLLAMA_LLM_MODEL)
                print(f"Response:\n{response_text}")
                
                # MCP servers now handle all tool calling including radio search
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure you have indexed some documents first using the --index flag.")
            sys.exit(1)

if __name__ == "__main__":
    main()
