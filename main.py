"""
Main entry point for the RAG application.
Handles command-line arguments for indexing, querying, and managing documents.
"""

import argparse
import sys
from llama_index.core import SimpleDirectoryReader

from config import (
    DATA_DIR,
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
    OLLAMA_LLM_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_REQUEST_TIMEOUT,
    EXCLUDE_LIST,
)
from data_loader import load_documents
from embedding_llm_setup import setup_ollama_models
from vector_store_manager import VectorStoreManager
from rag_pipeline import setup_rag_query_engine
from file_watcher import start_watching

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
    args = parser.parse_args()

    # Setup Ollama models
    llm, embedding_model = setup_ollama_models(
        OLLAMA_LLM_MODEL, OLLAMA_EMBEDDING_MODEL, OLLAMA_REQUEST_TIMEOUT
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
        print("Loading index for querying...")
        index = vector_store_manager.create_or_load_index()
        query_engine = setup_rag_query_engine(index, llm)
        
        print(f"Query: {args.query}")
        print("Asking LLM...")
        response = query_engine.query(args.query)
        print(f"Response: {response}")

    else:
        print("No specific action requested. Starting interactive query mode.")
        print("Type 'exit' to quit.")
        
        try:
            index = vector_store_manager.create_or_load_index()
            query_engine = setup_rag_query_engine(index, llm)
            
            while True:
                query = input("Enter your query: ")
                if query.lower() == 'exit':
                    break
                print("Asking LLM...")
                response = query_engine.query(query)
                print(f"Response: {response}")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure you have indexed some documents first using the --index flag.")
            sys.exit(1)

if __name__ == "__main__":
    main()
