"""
Loads documents from the specified data directory, processes them, and adds metadata.
"""

import os
import time
from typing import List, Dict
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PDFReader
import json
import os

def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

# Load configuration
config = load_config()
EXCLUDE_LIST = config['exclude_list']

def load_documents(data_dir: str) -> List[Document]:
    """
    Loads all documents from the given directory, splits them into chunks,
    and adds metadata.

    Args:
        data_dir (str): The path to the directory containing the documents.

    Returns:
        List[Document]: A list of LlamaIndex Document objects with metadata.
    """
    print(f"Loading documents from: {data_dir}")
    
    file_extractor_map: Dict[str, PDFReader] = {".pdf": PDFReader()}

    reader = SimpleDirectoryReader(
        data_dir, 
        recursive=True, 
        exclude=EXCLUDE_LIST,
        exclude_hidden=True,
        file_extractor=file_extractor_map
    )
    documents = reader.load_data()
    print(f"Loaded {len(documents)} document(s).")

    # Add metadata and chunking
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=100)
    
    all_nodes = []
    for doc in documents:
        print(f"Processing file: {doc.metadata.get('file_path')}")
        start_time = time.time()
        
        nodes = node_parser.get_nodes_from_documents([doc])
        for node in nodes:
            node.metadata["creation_date"] = os.path.getctime(node.metadata["file_path"])
            print(f"  - Added metadata to node. Creation date: {node.metadata['creation_date']}")
        
        all_nodes.extend(nodes)
        end_time = time.time()
        print(f"  - Finished processing in {end_time - start_time:.2f} seconds.")

    print(f"Processed documents into {len(all_nodes)} nodes.")
    return all_nodes
