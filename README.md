# RAG Application

This is a command-line application that uses a Retrieval-Augmented Generation (RAG) pipeline to answer questions based on a collection of documents.

It uses LlamaIndex for the RAG implementation, Ollama for running local LLMs and embedding models, and ChromaDB for the vector store.

## Features

- Index documents from a specified directory.
- Query the indexed documents.
- Add or delete documents from the index.
- Watch a directory for file changes and automatically update the index.
- Interactive query mode.

## Usage

```bash
# Index all documents in the data directory
python main.py --index

# Run a specific query
python main.py --query "Your question here"

# Add a new file to the index
python main.py --add /path/to/your/file.txt

# Delete a document from the index
python main.py --delete /path/to/your/file.txt

# Watch the data directory for changes
python main.py --watch

# Start interactive query mode
python main.py
```
