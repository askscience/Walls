# RAG MCP Server Documentation

The RAG (Retrieval-Augmented Generation) MCP Server provides powerful document indexing, search, and knowledge management capabilities. This server enables AI assistants to build and query knowledge bases from various document sources, supporting intelligent information retrieval and context-aware responses.

## Server Configuration

- **Name**: rag
- **Description**: Document indexing and retrieval-augmented generation server
- **Port**: 8003
- **Capabilities**: tools

## Available Tools

### Document Management Tools

#### 1. index_documents
Indexes documents from a specified directory into the vector database.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "directory_path": {
      "type": "string",
      "description": "Path to the directory containing documents to index"
    },
    "file_extensions": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of file extensions to include (optional, defaults to common document types)"
    },
    "chunk_size": {
      "type": "integer",
      "description": "Size of text chunks for indexing (optional, default: 1000)",
      "default": 1000
    },
    "chunk_overlap": {
      "type": "integer",
      "description": "Overlap between chunks (optional, default: 200)",
      "default": 200
    }
  },
  "required": ["directory_path"]
}
```

**Example Usage:**
```json
{
  "name": "index_documents",
  "arguments": {
    "directory_path": "/path/to/documents",
    "file_extensions": [".txt", ".md", ".pdf"],
    "chunk_size": 800,
    "chunk_overlap": 150
  }
}
```

**Use Cases:**
- Building knowledge bases from document collections
- Indexing research papers and articles
- Creating searchable documentation repositories
- Processing large text corpora

#### 2. add_document
Adds a single document to the vector database.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to the document file to add"
    },
    "document_id": {
      "type": "string",
      "description": "Optional custom ID for the document"
    },
    "metadata": {
      "type": "object",
      "description": "Optional metadata to associate with the document"
    }
  },
  "required": ["file_path"]
}
```

**Example Usage:**
```json
{
  "name": "add_document",
  "arguments": {
    "file_path": "/path/to/important_document.pdf",
    "document_id": "doc_001",
    "metadata": {
      "author": "John Doe",
      "category": "research",
      "date": "2024-01-15"
    }
  }
}
```

**Use Cases:**
- Adding individual documents to existing indexes
- Incorporating new research papers
- Adding documents with specific metadata
- Selective document inclusion

#### 3. delete_document
Removes a document from the vector database.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "document_id": {
      "type": "string",
      "description": "ID of the document to delete"
    }
  },
  "required": ["document_id"]
}
```

**Example Usage:**
```json
{
  "name": "delete_document",
  "arguments": {
    "document_id": "doc_001"
  }
}
```

**Use Cases:**
- Removing outdated documents
- Cleaning up test data
- Managing document lifecycle
- Correcting indexing mistakes

### Query and Search Tools

#### 4. query_documents
Performs a semantic search query against the indexed documents.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The search query or question"
    },
    "top_k": {
      "type": "integer",
      "description": "Number of top results to return (optional, default: 5)",
      "default": 5
    },
    "include_metadata": {
      "type": "boolean",
      "description": "Whether to include document metadata in results (optional, default: true)",
      "default": true
    },
    "similarity_threshold": {
      "type": "number",
      "description": "Minimum similarity score for results (optional, default: 0.0)",
      "default": 0.0
    }
  },
  "required": ["query"]
}
```

**Example Usage:**
```json
{
  "name": "query_documents",
  "arguments": {
    "query": "What are the benefits of machine learning in healthcare?",
    "top_k": 10,
    "include_metadata": true,
    "similarity_threshold": 0.7
  }
}
```

**Use Cases:**
- Answering questions from knowledge base
- Finding relevant research papers
- Semantic document search
- Information retrieval for content generation

#### 5. interactive_query
Performs an interactive query with follow-up capabilities and conversation context.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The search query or question"
    },
    "conversation_id": {
      "type": "string",
      "description": "Optional conversation ID for maintaining context"
    },
    "max_tokens": {
      "type": "integer",
      "description": "Maximum tokens for the response (optional, default: 1000)",
      "default": 1000
    },
    "temperature": {
      "type": "number",
      "description": "Temperature for response generation (optional, default: 0.7)",
      "default": 0.7
    }
  },
  "required": ["query"]
}
```

**Example Usage:**
```json
{
  "name": "interactive_query",
  "arguments": {
    "query": "Explain the concept of neural networks",
    "conversation_id": "conv_123",
    "max_tokens": 800,
    "temperature": 0.5
  }
}
```

**Use Cases:**
- Conversational AI with document context
- Multi-turn question answering
- Educational tutoring systems
- Interactive research assistance

### System Management Tools

#### 6. watch_directory
Sets up automatic monitoring of a directory for new documents to index.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "directory_path": {
      "type": "string",
      "description": "Path to the directory to monitor"
    },
    "file_extensions": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of file extensions to monitor (optional)"
    },
    "auto_index": {
      "type": "boolean",
      "description": "Whether to automatically index new files (optional, default: true)",
      "default": true
    }
  },
  "required": ["directory_path"]
}
```

**Example Usage:**
```json
{
  "name": "watch_directory",
  "arguments": {
    "directory_path": "/path/to/documents",
    "file_extensions": [".pdf", ".docx", ".txt"],
    "auto_index": true
  }
}
```

**Use Cases:**
- Automatic knowledge base updates
- Real-time document processing
- Continuous learning systems
- Dynamic content management

#### 7. health_check
Checks the health and status of the RAG system components.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "include_stats": {
      "type": "boolean",
      "description": "Whether to include detailed statistics (optional, default: false)",
      "default": false
    }
  },
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "health_check",
  "arguments": {
    "include_stats": true
  }
}
```

**Use Cases:**
- System monitoring and diagnostics
- Performance optimization
- Troubleshooting issues
- Capacity planning

#### 8. get_status
Retrieves detailed status information about the RAG system.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "detailed": {
      "type": "boolean",
      "description": "Whether to return detailed status information (optional, default: false)",
      "default": false
    }
  },
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "get_status",
  "arguments": {
    "detailed": true
  }
}
```

**Use Cases:**
- Monitoring system performance
- Checking index statistics
- Verifying system configuration
- Debugging and maintenance

## Implementation Details

The RAG MCP Server is implemented with the following handler classes:

- **DocumentHandler**: Manages document indexing, addition, deletion, and file processing
- **QueryHandler**: Handles search queries, semantic retrieval, and interactive conversations
- **SystemHandler**: Manages system health, status monitoring, and directory watching

## Common Workflows

### Knowledge Base Creation Workflow
1. Use `index_documents` to build initial knowledge base from document collection
2. Use `add_document` to include additional specific documents
3. Use `watch_directory` to monitor for new documents
4. Use `health_check` to verify successful indexing

### Research and Query Workflow
1. Use `query_documents` to find relevant information
2. Use `interactive_query` for conversational follow-ups
3. Refine queries based on results
4. Use `get_status` to monitor system performance

### Document Management Workflow
1. Use `add_document` to include new documents with metadata
2. Use `delete_document` to remove outdated content
3. Use `index_documents` to rebuild indexes when needed
4. Use `watch_directory` for automated updates

### System Maintenance Workflow
1. Use `health_check` to monitor system health
2. Use `get_status` to review performance metrics
3. Use `delete_document` to clean up unnecessary documents
4. Use `index_documents` to refresh indexes periodically

## Supported File Types

The RAG server supports various document formats:

- **Text Files**: .txt, .md, .rst
- **Documents**: .pdf, .docx, .doc, .odt
- **Web Content**: .html, .htm
- **Data Files**: .csv, .json, .xml
- **Code Files**: .py, .js, .java, .cpp, .c

## Vector Database Features

- **Semantic Search**: Uses advanced embedding models for semantic similarity
- **Metadata Filtering**: Supports filtering by document metadata
- **Chunking Strategies**: Configurable text chunking for optimal retrieval
- **Similarity Scoring**: Provides relevance scores for search results
- **Incremental Updates**: Supports adding/removing documents without full reindexing

## Query Optimization Tips

### Effective Query Strategies
- Use specific, well-formed questions rather than keywords
- Include context in queries for better results
- Experiment with different `top_k` values
- Use similarity thresholds to filter low-quality results

### Performance Considerations
- Larger `chunk_size` may improve context but reduce precision
- Smaller `chunk_overlap` improves performance but may miss connections
- Regular health checks help identify performance issues
- Monitor index size and query response times

## Error Handling

The RAG server includes robust error handling for:
- Invalid file paths and formats
- Corrupted or unreadable documents
- Vector database connection issues
- Embedding model failures
- Memory and storage constraints

## Security and Privacy

- Documents are processed locally without external API calls
- Sensitive information remains within the local system
- Access control through file system permissions
- No data transmission to external services
- Configurable data retention policies

## Integration Examples

### Research Assistant Integration
```json
{
  "workflow": [
    {
      "name": "index_documents",
      "arguments": {
        "directory_path": "/research/papers",
        "file_extensions": [".pdf"]
      }
    },
    {
      "name": "interactive_query",
      "arguments": {
        "query": "What are the latest developments in quantum computing?",
        "conversation_id": "research_session_1"
      }
    }
  ]
}
```

### Documentation System Integration
```json
{
  "workflow": [
    {
      "name": "watch_directory",
      "arguments": {
        "directory_path": "/docs",
        "file_extensions": [".md", ".rst"],
        "auto_index": true
      }
    },
    {
      "name": "query_documents",
      "arguments": {
        "query": "How to configure the authentication system?",
        "top_k": 5
      }
    }
  ]
}
```

This comprehensive RAG server enables powerful knowledge management and intelligent information retrieval capabilities for AI-assisted applications.