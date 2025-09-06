# Word Editor MCP Server Documentation

The Word Editor MCP Server provides comprehensive text editing and document manipulation capabilities through a TCP-based communication system. This server enables AI assistants to interact with a GUI-based word processor, performing text operations, file management, and system integration tasks.

## Server Configuration

- **Name**: word_editor
- **Description**: Text editing and document manipulation server with GUI integration
- **Port**: 8004
- **Capabilities**: tools
- **Communication**: TCP-based connection to GUI application

## Available Tools

### Text Manipulation Tools

#### 1. set_text
Replaces all text in the current document with new content.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "The text content to set in the document"
    }
  },
  "required": ["text"]
}
```

**Example Usage:**
```json
{
  "name": "set_text",
  "arguments": {
    "text": "This is the new document content.\nIt can contain multiple lines.\n\nAnd paragraphs."
  }
}
```

**Use Cases:**
- Creating new documents from scratch
- Replacing entire document content
- Initializing templates
- Clearing and rewriting documents

#### 2. insert_text
Inserts text at the current cursor position in the document.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "The text to insert at the cursor position"
    },
    "position": {
      "type": "integer",
      "description": "Optional position to insert text (character index)"
    }
  },
  "required": ["text"]
}
```

**Example Usage:**
```json
{
  "name": "insert_text",
  "arguments": {
    "text": "This text will be inserted at the cursor.",
    "position": 150
  }
}
```

**Use Cases:**
- Adding content to existing documents
- Inserting text at specific positions
- Building documents incrementally
- Adding annotations or comments

#### 3. append_text
Appends text to the end of the current document.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "The text to append to the document"
    }
  },
  "required": ["text"]
}
```

**Example Usage:**
```json
{
  "name": "append_text",
  "arguments": {
    "text": "\n\nThis text is added to the end of the document."
  }
}
```

**Use Cases:**
- Adding content to document endings
- Building documents sequentially
- Appending signatures or footers
- Continuous content generation

#### 4. get_text
Retrieves the current text content from the document.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "start_position": {
      "type": "integer",
      "description": "Optional start position for text extraction (character index)"
    },
    "end_position": {
      "type": "integer",
      "description": "Optional end position for text extraction (character index)"
    }
  },
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "get_text",
  "arguments": {
    "start_position": 0,
    "end_position": 100
  }
}
```

**Use Cases:**
- Reading document content
- Extracting specific text sections
- Content analysis and processing
- Backup and synchronization

### File Management Tools

#### 5. open_file
Opens a document file in the word editor.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to the file to open"
    },
    "encoding": {
      "type": "string",
      "description": "File encoding (optional, default: utf-8)",
      "default": "utf-8"
    }
  },
  "required": ["file_path"]
}
```

**Example Usage:**
```json
{
  "name": "open_file",
  "arguments": {
    "file_path": "/path/to/document.txt",
    "encoding": "utf-8"
  }
}
```

**Use Cases:**
- Loading existing documents for editing
- Opening templates
- Accessing saved work
- File-based document management

#### 6. save_file
Saves the current document to a file.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path where to save the file"
    },
    "encoding": {
      "type": "string",
      "description": "File encoding (optional, default: utf-8)",
      "default": "utf-8"
    },
    "backup": {
      "type": "boolean",
      "description": "Whether to create a backup of existing file (optional, default: false)",
      "default": false
    }
  },
  "required": ["file_path"]
}
```

**Example Usage:**
```json
{
  "name": "save_file",
  "arguments": {
    "file_path": "/path/to/save/document.txt",
    "encoding": "utf-8",
    "backup": true
  }
}
```

**Use Cases:**
- Saving work in progress
- Creating document backups
- Exporting content to files
- Document persistence

### System Integration Tools

#### 7. send_cli_command
Executes a command-line instruction through the word editor system.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "The CLI command to execute"
    },
    "working_directory": {
      "type": "string",
      "description": "Optional working directory for the command"
    },
    "timeout": {
      "type": "integer",
      "description": "Command timeout in seconds (optional, default: 30)",
      "default": 30
    }
  },
  "required": ["command"]
}
```

**Example Usage:**
```json
{
  "name": "send_cli_command",
  "arguments": {
    "command": "ls -la",
    "working_directory": "/home/user/documents",
    "timeout": 10
  }
}
```

**Use Cases:**
- File system operations
- External tool integration
- System administration tasks
- Automated workflows

#### 8. check_gui_status
Checks the status and availability of the GUI word editor application.

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
  "name": "check_gui_status",
  "arguments": {
    "detailed": true
  }
}
```

**Use Cases:**
- Verifying GUI application connectivity
- Troubleshooting connection issues
- System health monitoring
- Application state verification

## Implementation Details

The Word Editor MCP Server is implemented with the following components:

- **TextHandler**: Manages all text manipulation operations through TCP communication
- **TCP Client**: Handles communication with the GUI word editor application
- **Command Parser**: Processes and formats commands for the GUI application
- **Response Handler**: Manages responses and error handling from the GUI

## TCP Communication Protocol

The server communicates with a GUI word editor application through TCP sockets:

- **Host**: localhost (127.0.0.1)
- **Port**: Configurable (default: 12345)
- **Protocol**: Text-based command/response
- **Encoding**: UTF-8
- **Connection**: Persistent with automatic reconnection

## Common Workflows

### Document Creation Workflow
1. Use `check_gui_status` to verify GUI availability
2. Use `set_text` to create initial document content
3. Use `append_text` or `insert_text` to add more content
4. Use `save_file` to persist the document

### Document Editing Workflow
1. Use `open_file` to load an existing document
2. Use `get_text` to read current content
3. Use `insert_text` or `append_text` to modify content
4. Use `save_file` to save changes

### Collaborative Editing Workflow
1. Use `open_file` to load shared document
2. Use `get_text` to check current state
3. Use `insert_text` to add contributions
4. Use `save_file` with backup option

### System Integration Workflow
1. Use `send_cli_command` to perform file operations
2. Use `open_file` to load processed files
3. Use text manipulation tools to edit content
4. Use `send_cli_command` for additional processing

## Supported File Formats

The Word Editor server supports various text-based formats:

- **Plain Text**: .txt, .text
- **Markdown**: .md, .markdown
- **Rich Text**: .rtf
- **Code Files**: .py, .js, .html, .css, .json
- **Configuration**: .ini, .conf, .cfg
- **Documentation**: .rst, .org

## Advanced Features

### Text Processing Capabilities
- Unicode support for international text
- Large file handling with efficient memory usage
- Real-time text manipulation
- Position-based text operations

### File Management Features
- Automatic backup creation
- Multiple encoding support
- Path validation and error handling
- Concurrent file access management

### System Integration
- Command-line tool execution
- Working directory management
- Timeout handling for long operations
- Error reporting and logging

## Error Handling

The Word Editor server includes comprehensive error handling for:

- TCP connection failures
- GUI application unavailability
- File access permissions
- Invalid file paths
- Encoding issues
- Command execution failures
- Network timeouts

## Performance Considerations

### Optimization Tips
- Use `append_text` for sequential content addition
- Batch multiple operations when possible
- Monitor GUI status for connection health
- Use appropriate timeouts for CLI commands

### Memory Management
- Efficient handling of large documents
- Streaming for very large files
- Automatic cleanup of temporary resources
- Connection pooling for multiple operations

## Security Features

- Local-only TCP communication
- Command validation and sanitization
- File path validation
- Access control through file system permissions
- Secure handling of sensitive content

## Integration Examples

### Automated Report Generation
```json
{
  "workflow": [
    {
      "name": "set_text",
      "arguments": {
        "text": "# Monthly Report\n\n## Executive Summary\n"
      }
    },
    {
      "name": "append_text",
      "arguments": {
        "text": "This report covers the key metrics for the month.\n\n"
      }
    },
    {
      "name": "save_file",
      "arguments": {
        "file_path": "/reports/monthly_report.md",
        "backup": true
      }
    }
  ]
}
```

### Document Processing Pipeline
```json
{
  "workflow": [
    {
      "name": "open_file",
      "arguments": {
        "file_path": "/input/raw_document.txt"
      }
    },
    {
      "name": "get_text",
      "arguments": {}
    },
    {
      "name": "set_text",
      "arguments": {
        "text": "[Processed content would be inserted here]"
      }
    },
    {
      "name": "save_file",
      "arguments": {
        "file_path": "/output/processed_document.txt"
      }
    }
  ]
}
```

## Troubleshooting

### Common Issues
- **Connection Refused**: Ensure GUI application is running
- **File Not Found**: Verify file paths and permissions
- **Encoding Errors**: Check file encoding settings
- **Timeout Issues**: Adjust timeout values for long operations

### Diagnostic Commands
- Use `check_gui_status` to verify connectivity
- Use `get_text` to test basic functionality
- Use `send_cli_command` with simple commands to test system integration

This comprehensive Word Editor server enables powerful text editing and document management capabilities with seamless GUI integration and system-level operations.