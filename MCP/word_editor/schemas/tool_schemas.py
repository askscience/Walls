"""Tool schemas for Word Editor MCP server."""

TOOL_SCHEMAS = {
    "set_text": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text content to set in the word editor"
            }
        },
        "required": ["text"]
    },
    
    "insert_text": {
        "type": "object",
        "properties": {
            "position": {
                "type": "integer",
                "description": "The position (character index) where to insert the text",
                "minimum": 0
            },
            "text": {
                "type": "string",
                "description": "The text to insert"
            }
        },
        "required": ["position", "text"]
    },
    
    "append_text": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to append to the end of the current content"
            }
        },
        "required": ["text"]
    },
    
    "get_text": {
        "type": "object",
        "properties": {},
        "description": "Get the current text content from the word editor"
    },
    
    "open_file": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to open"
            }
        },
        "required": ["file_path"]
    },
    
    "save_file": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path where to save the file (optional, uses current file if not provided)"
            },
            "content": {
                "type": "string",
                "description": "The content to save (optional, uses current editor content if not provided)"
            }
        }
    },
    
    "send_cli_command": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The CLI command to send to the word editor"
            },
            "args": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Arguments for the command (optional)"
            }
        },
        "required": ["command"]
    },
    
    "check_gui_status": {
        "type": "object",
        "properties": {},
        "description": "Check if the word editor GUI is running and accessible"
    }
}