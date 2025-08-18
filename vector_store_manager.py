"""
Manages the ChromaDB vector store and the LlamaIndex VectorStoreIndex.
"""

from typing import List, Optional
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Document, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore

class VectorStoreManager:
    """
    Manages the creation, loading, and modification of the vector store and its index.
    """

    def __init__(self, db_path: str, collection_name: str, embedding_model):
        """
        Initializes the VectorStoreManager.

        Args:
            db_path (str): The path to persist the ChromaDB.
            collection_name (str): The name of the collection in ChromaDB.
            embedding_model: The embedding model to use.
        """
        self.db = chromadb.PersistentClient(path=db_path)
        self.chroma_collection = self.db.get_or_create_collection(collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        Settings.embed_model = embedding_model

    def create_or_load_index(self, documents: Optional[List[Document]] = None) -> VectorStoreIndex:
        """
        Creates a new index from documents or loads an existing one from the vector store.

        Args:
            documents (Optional[List[Document]]): A list of documents to index.
                                                  If None, loads the existing index.

        Returns:
            VectorStoreIndex: The created or loaded VectorStoreIndex.
        """
        if documents:
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context
            )
            print("Successfully indexed new documents.")
        else:
            index = VectorStoreIndex.from_vector_store(
                self.vector_store
            )
            print("Loaded existing index.")
        return index

    def add_documents(self, documents: List[Document]):
        """
        Adds new documents to the existing index.

        Args:
            documents (List[Document]): A list of new documents to add.
        """
        index = self.create_or_load_index()
        index.insert_nodes(documents)
        print(f"Successfully added {len(documents)} new document(s) to the index.")

    def delete_documents_by_path(self, file_paths: List[str]):
        """
        Deletes documents from the index by their file paths.

        Args:
            file_paths (List[str]): A list of file paths to delete.
        """
        for file_path in file_paths:
            self.chroma_collection.delete(where={"file_path": file_path})
        print(f"Successfully deleted {len(file_paths)} document(s) from the index.")
