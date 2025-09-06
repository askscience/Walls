"""Fast version of vector store manager with lazy imports.

This module provides the same functionality as vector_store_manager.py
but with lazy loading to improve startup performance.
"""

from typing import List, Optional
from lazy_imports import (
    chromadb, VectorStoreIndex, Document, Settings, ChromaVectorStore, llama_index_core
)

# Support type checks for nodes if available
try:
    from llama_index.core.schema import BaseNode
except Exception:  # Fallback if import path changes or class unavailable
    BaseNode = None


class VectorStoreManager:
    """
    Fast version of VectorStoreManager with lazy imports.
    Manages the creation, loading, and modification of the vector store and its index.
    """

    def __init__(self, db_path: str, collection_name: str, embedding_model):
        """
        Initializes the VectorStoreManager with lazy loading.

        Args:
            db_path (str): The path to persist the ChromaDB.
            collection_name (str): The name of the collection in ChromaDB.
            embedding_model: The embedding model to use.
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Lazy initialization - these will be created when first accessed
        self._db = None
        self._chroma_collection = None
        self._vector_store = None
        self._settings_configured = False

    @property
    def db(self):
        """Lazy property for ChromaDB client."""
        if self._db is None:
            self._db = chromadb.PersistentClient(path=self.db_path)
        return self._db

    @property
    def chroma_collection(self):
        """Lazy property for ChromaDB collection."""
        if self._chroma_collection is None:
            self._chroma_collection = self.db.get_or_create_collection(self.collection_name)
        return self._chroma_collection

    @property
    def vector_store(self):
        """Lazy property for ChromaVectorStore."""
        if self._vector_store is None:
            self._vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        return self._vector_store

    def _ensure_settings_configured(self):
        """Ensure Settings.embed_model is configured (only once)."""
        if not self._settings_configured:
            Settings.embed_model = self.embedding_model
            self._settings_configured = True

    def create_or_load_index(self, documents: Optional[List[Document]] = None) -> 'VectorStoreIndex':
        """
        Creates a new index from documents or loads an existing one from the vector store.

        Args:
            documents (Optional[List[Document]]): A list of documents or nodes to index.
                                                  If None, loads the existing index.

        Returns:
            VectorStoreIndex: The created or loaded VectorStoreIndex.
        """
        self._ensure_settings_configured()
        storage_context = llama_index_core.StorageContext.from_defaults(vector_store=self.vector_store)

        if documents:
            # Decide based on the type of the first item
            first = documents[0] if len(documents) > 0 else None

            if first is not None and isinstance(first, Document):
                # Build index directly from documents using the shared vector store
                index = VectorStoreIndex.from_documents(
                    documents, storage_context=storage_context, embed_model=self.embedding_model
                )
                print(f"Successfully indexed {len(documents)} document(s).")
            elif BaseNode is not None and first is not None and isinstance(first, BaseNode):
                # Create/load empty index bound to the vector store, then insert nodes
                index = VectorStoreIndex.from_vector_store(self.vector_store, embed_model=self.embedding_model)
                index.insert_nodes(documents)
                print(f"Successfully indexed {len(documents)} node(s).")
            else:
                # Fallback: treat as documents
                index = VectorStoreIndex.from_documents(
                    documents, storage_context=storage_context, embed_model=self.embedding_model
                )
                print("Successfully indexed new documents (generic path).")
        else:
            index = VectorStoreIndex.from_vector_store(self.vector_store, embed_model=self.embedding_model)
            print("Loaded existing index.")
        return index

    def add_documents(self, documents: List[Document]):
        """
        Adds new documents or nodes to the existing index.

        Args:
            documents (List[Document]): A list of new documents or nodes to add.
        """
        index = self.create_or_load_index()

        if len(documents) == 0:
            print("No documents provided to add.")
            return

        first = documents[0]
        if isinstance(first, Document):
            try:
                # Prefer insert_documents if available; otherwise fallback to from_documents recreation
                insert_docs = getattr(index, "insert_documents", None)
                if callable(insert_docs):
                    index.insert_documents(documents)
                else:
                    # Rebuild index from documents against the same vector store
                    storage_context = llama_index_core.StorageContext.from_defaults(vector_store=self.vector_store)
                    VectorStoreIndex.from_documents(documents, storage_context=storage_context)
                print(f"Successfully added {len(documents)} new document(s) to the index.")
            except Exception as e:
                print(f"Error adding documents via insert_documents, falling back to nodes conversion: {e}")
                # Convert documents to nodes and insert
                from llama_index.core.node_parser import SimpleNodeParser
                parser = SimpleNodeParser.from_defaults()
                nodes = parser.get_nodes_from_documents(documents)
                index.insert_nodes(nodes)
                print(f"Successfully added {len(documents)} document(s) as nodes to the index.")
        elif BaseNode is not None and isinstance(first, BaseNode):
            index.insert_nodes(documents)
            print(f"Successfully added {len(documents)} node(s) to the index.")
        else:
            print(f"Warning: Unsupported document type: {type(first)}")

    def delete_documents_by_path(self, file_paths: List[str]):
        """
        Deletes documents from the index by their file paths.

        Args:
            file_paths (List[str]): A list of file paths to delete from the index.
        """
        index = self.create_or_load_index()
        
        for file_path in file_paths:
            try:
                # Try to delete by document ID (file path)
                index.delete_ref_doc(file_path, delete_from_docstore=True)
                print(f"Successfully deleted document: {file_path}")
            except Exception as e:
                print(f"Error deleting document {file_path}: {e}")