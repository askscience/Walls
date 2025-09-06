"""Lazy import utilities to improve startup performance.

This module provides lazy loading for heavy dependencies like ChromaDB and LlamaIndex
to reduce initial import time from ~2.5s to near-instant.
"""

import importlib
from typing import Any, Dict, Optional


class LazyImporter:
    """Lazy importer that defers module loading until first access."""
    
    def __init__(self, module_name: str, attribute: Optional[str] = None):
        self.module_name = module_name
        self.attribute = attribute
        self._cached_module = None
        self._cached_attribute = None
    
    def __call__(self, *args, **kwargs):
        """Load and call the target function/class."""
        if self._cached_attribute is None:
            self._load()
        return self._cached_attribute(*args, **kwargs)
    
    def __getattr__(self, name):
        """Load and access class/module attributes and methods."""
        if self._cached_attribute is None:
            self._load()
        return getattr(self._cached_attribute, name)
    
    def _load(self):
        """Actually import the module and cache it."""
        self._cached_module = importlib.import_module(self.module_name)
        if self.attribute:
            self._cached_attribute = getattr(self._cached_module, self.attribute)
        else:
            self._cached_attribute = self._cached_module


# Lazy imports for heavy dependencies
class LazyModule:
    """Lazy module loader that supports both attributes and class methods."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._cached_module = None
    
    def __getattr__(self, name):
        if self._cached_module is None:
            import importlib
            self._cached_module = importlib.import_module(self.module_name)
        return getattr(self._cached_module, name)

# Lazy imports for heavy dependencies
chromadb = LazyImporter('chromadb')
VectorStoreIndex = LazyImporter('llama_index.core', 'VectorStoreIndex')
StorageContext = LazyImporter('llama_index.core', 'StorageContext')
Document = LazyImporter('llama_index.core', 'Document')
Settings = LazyImporter('llama_index.core', 'Settings')
Ollama = LazyImporter('llama_index.llms.ollama', 'Ollama')
OllamaEmbedding = LazyImporter('llama_index.embeddings.ollama', 'OllamaEmbedding')
ChromaVectorStore = LazyImporter('llama_index.vector_stores.chroma', 'ChromaVectorStore')
VectorIndexRetriever = LazyImporter('llama_index.core.retrievers', 'VectorIndexRetriever')
RetrieverQueryEngine = LazyImporter('llama_index.core.query_engine', 'RetrieverQueryEngine')
SentenceTransformerRerank = LazyImporter('llama_index.core.postprocessor', 'SentenceTransformerRerank')

# Lazy modules for accessing class methods
llama_index_core = LazyModule('llama_index.core')


def get_lazy_imports() -> Dict[str, Any]:
    """Get a dictionary of all lazy imports for easy access."""
    return {
        'chromadb': chromadb,
        'VectorStoreIndex': VectorStoreIndex,
        'StorageContext': StorageContext,
        'Document': Document,
        'Settings': Settings,
        'Ollama': Ollama,
        'OllamaEmbedding': OllamaEmbedding,
        'ChromaVectorStore': ChromaVectorStore,
        'VectorIndexRetriever': VectorIndexRetriever,
        'RetrieverQueryEngine': RetrieverQueryEngine,
        'SentenceTransformerRerank': SentenceTransformerRerank,
    }