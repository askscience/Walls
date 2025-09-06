# RAG Service Performance Optimization

This document outlines the performance improvements made to the RAG service startup time and provides usage guidelines for the optimized components.

## Performance Results

### Benchmark Summary

| Version | Total Time | Improvement | CPU Usage | Wall Clock |
|---------|------------|-------------|-----------|------------|
| Original | ~2.91s | Baseline | 39% | 7.7s |
| Fast (Lazy) | ~2.13s | 27% faster | 94% | 3.4s |
| Pooled | ~1.88s | 35% faster | 99% | 3.2s |

### Key Improvements

1. **Lazy Loading**: Reduced initial import overhead by deferring heavy dependencies
2. **Connection Pooling**: Optimized ChromaDB client management and reuse
3. **Progressive Initialization**: Better CPU utilization and faster wall-clock time

## Optimized Components

### 1. Lazy Import System (`lazy_imports.py`)

**Purpose**: Defer loading of heavy dependencies until first access

**Key Features**:
- `LazyImporter` class for module-level lazy loading
- `LazyModule` class for attribute-level lazy loading
- Thread-safe caching mechanism

**Usage**:
```python
from lazy_imports import LazyImporter

# Lazy import heavy modules
chromadb = LazyImporter('chromadb')
VectorStoreIndex = LazyImporter('llama_index.core', 'VectorStoreIndex')
```

### 2. Fast Embedding Setup (`embedding_llm_setup_fast.py`)

**Purpose**: Optimized model initialization with lazy imports

**Improvements**:
- Lazy loading of Ollama components
- Reduced initial memory footprint
- Faster startup when models are cached

**Usage**:
```python
from embedding_llm_setup_fast import setup_ollama_models

llm, embedding = setup_ollama_models(
    llm_model="gemma2:2b",
    embedding_model="nomic-embed-text",
    request_timeout=120,
    model_params={"temperature": 0.7}
)
```

### 3. Connection Pooled Vector Store (`vector_store_manager_pooled.py`)

**Purpose**: Optimize ChromaDB connections and resource management

**Key Features**:
- Singleton connection pool for ChromaDB clients
- Thread-safe client caching
- Automatic connection reuse
- Pool statistics and management

**Usage**:
```python
from vector_store_manager_pooled import VectorStoreManagerPooled

vsm = VectorStoreManagerPooled(
    db_path="/path/to/chroma_db",
    collection_name="documents",
    embedding_model=embedding_model
)

index = vsm.create_or_load_index()
print(vsm.get_pool_stats())  # View connection statistics
```

### 4. ChromaDB Connection Pool (`chroma_pool.py`)

**Purpose**: Centralized ChromaDB client management

**Features**:
- Singleton pattern for global connection management
- Context managers for collection access
- Connection statistics and cache management

**Usage**:
```python
from chroma_pool import chroma_pool

# Get cached client
client = chroma_pool.get_client("/path/to/db")

# Use context manager for collections
with chroma_pool.get_collection("/path/to/db", "collection_name") as collection:
    # Work with collection
    pass

# View statistics
stats = chroma_pool.get_stats()
print(f"Active clients: {stats['total_clients']}")
```

## Migration Guide

### From Original to Optimized Components

1. **Replace imports**:
   ```python
   # Before
   from embedding_llm_setup import setup_ollama_models
   from vector_store_manager import VectorStoreManager
   
   # After
   from embedding_llm_setup_fast import setup_ollama_models
   from vector_store_manager_pooled import VectorStoreManagerPooled
   ```

2. **Update initialization**:
   ```python
   # Before
   vsm = VectorStoreManager(db_path, collection_name, embedding_model)
   
   # After
   vsm = VectorStoreManagerPooled(db_path, collection_name, embedding_model)
   ```

3. **Optional: Monitor performance**:
   ```python
   # Check connection pool statistics
   stats = vsm.get_pool_stats()
   print(f"Pool efficiency: {stats}")
   ```

## Best Practices

### 1. Connection Management
- Use the pooled version for production deployments
- Monitor pool statistics to optimize connection usage
- Clear pool cache when changing database configurations

### 2. Memory Optimization
- Lazy imports reduce initial memory footprint
- Connection pooling prevents duplicate client creation
- Use context managers for temporary collection access

### 3. Development vs Production
- **Development**: Use fast versions for quicker iteration
- **Production**: Use pooled versions for better resource management
- **Testing**: Original versions for baseline comparisons

## Troubleshooting

### Common Issues

1. **Import Errors with Lazy Loading**:
   - Ensure all required packages are installed
   - Check module paths in lazy import declarations

2. **Connection Pool Issues**:
   - Clear cache if database path changes: `chroma_pool.clear_cache()`
   - Monitor pool statistics for connection leaks

3. **Performance Regression**:
   - Compare with baseline using original components
   - Check system resources and ChromaDB configuration

### Debugging

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check pool status
from chroma_pool import chroma_pool
print(chroma_pool.get_stats())

# Time individual components
import time
start = time.time()
# ... component initialization
print(f"Component took: {time.time() - start:.2f}s")
```

## Future Improvements

1. **Async Support**: Implement async versions for better concurrency
2. **Caching Layer**: Add result caching for frequent queries
3. **Health Monitoring**: Add connection health checks and auto-recovery
4. **Configuration Tuning**: Dynamic pool size based on usage patterns

## Performance Monitoring

### Metrics to Track
- Startup time (total and per component)
- Memory usage (initial and peak)
- Connection pool efficiency
- Query response times

### Benchmarking Script

```python
import time
from embedding_llm_setup_fast import setup_ollama_models
from vector_store_manager_pooled import VectorStoreManagerPooled
from config import *

def benchmark_startup():
    start = time.time()
    
    # Model setup
    llm, emb = setup_ollama_models(
        OLLAMA_LLM_MODEL, OLLAMA_EMBEDDING_MODEL, 
        OLLAMA_REQUEST_TIMEOUT, LLM_MODEL_PARAMS
    )
    model_time = time.time() - start
    
    # Vector store setup
    vsm = VectorStoreManagerPooled(
        CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, emb
    )
    vs_time = time.time() - start
    
    # Index loading
    idx = vsm.create_or_load_index()
    total_time = time.time() - start
    
    return {
        'model_setup': model_time,
        'vector_store': vs_time - model_time,
        'index_loading': total_time - vs_time,
        'total': total_time,
        'pool_stats': vsm.get_pool_stats()
    }

if __name__ == "__main__":
    results = benchmark_startup()
    for key, value in results.items():
        print(f"{key}: {value}")
```