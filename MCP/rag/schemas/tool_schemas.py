"""Tool schemas for RAG MCP server operations."""

TOOL_SCHEMAS = {
    "rag_index_all": {
        "type": "object",
        "properties": {
            "force_reindex": {
                "type": "boolean",
                "description": "Force re-indexing even if index exists",
                "default": False
            }
        },
        "additionalProperties": False
    },
    
    "rag_add_document": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the document file to add to the index"
            }
        },
        "required": ["file_path"],
        "additionalProperties": False
    },
    
    "rag_delete_document": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the document file to delete from the index"
            }
        },
        "required": ["file_path"],
        "additionalProperties": False
    },
    
    "rag_query": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query string to search for in the indexed documents"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5,
                "minimum": 1,
                "maximum": 20
            },
            "include_metadata": {
                "type": "boolean",
                "description": "Include document metadata in results",
                "default": True
            }
        },
        "required": ["query"],
        "additionalProperties": False
    },
    
    "rag_interactive_query": {
        "type": "object",
        "properties": {
            "initial_query": {
                "type": "string",
                "description": "Optional initial query to start with"
            }
        },
        "additionalProperties": False
    },
    
    "rag_start_watching": {
        "type": "object",
        "properties": {
            "watch_directory": {
                "type": "string",
                "description": "Directory to watch for changes (defaults to data directory)"
            }
        },
        "additionalProperties": False
    },
    
    "rag_stop_watching": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },
    
    "rag_health_check": {
        "type": "object",
        "properties": {
            "detailed": {
                "type": "boolean",
                "description": "Return detailed health information",
                "default": False
            }
        },
        "additionalProperties": False
    },
    
    "rag_get_status": {
        "type": "object",
        "properties": {
            "include_stats": {
                "type": "boolean",
                "description": "Include indexing statistics",
                "default": True
            }
        },
        "additionalProperties": False
    }
}