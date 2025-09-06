# MCP Servers Overview

This document provides a comprehensive overview of the Model Context Protocol (MCP) server ecosystem, featuring four specialized servers that enable AI assistants to interact with various applications and services.

## Architecture Overview

The MCP server collection consists of four independent servers, each running on different ports and providing specialized capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Ecosystem                    │
├─────────────────┬─────────────────┬─────────────────┬─────┤
│   Browser MCP   │ Radio Player MCP│    RAG MCP      │Word │
│   Port: 8001    │   Port: 8002    │   Port: 8003    │Edit │
│                 │                 │                 │8004 │
│ Web Automation  │ Internet Radio  │ Document Search │Text │
│ & Interaction   │ & Streaming     │ & Retrieval     │Edit │
└─────────────────┴─────────────────┴─────────────────┴─────┘
```

## Server Configurations

### Configuration File
All servers are configured through `MCP/mcp_config.json`:

```json
{
  "mcpServers": {
    "browser": {
      "command": "python",
      "args": ["MCP/browser/server.py"],
      "env": {"PORT": "8001"}
    },
    "radio_player": {
      "command": "python",
      "args": ["MCP/radio_player/server.py"],
      "env": {"PORT": "8002"}
    },
    "rag": {
      "command": "python",
      "args": ["MCP/rag/server.py"],
      "env": {"PORT": "8003"}
    },
    "word_editor": {
      "command": "python",
      "args": ["MCP/word_editor/server.py"],
      "env": {"PORT": "8004"}
    }
  }
}
```

## Individual Server Details

### 1. Browser MCP Server (Port 8001)
**Purpose**: Web automation and browser interaction

**Key Capabilities**:
- Web page navigation and interaction
- Bookmark management
- Element clicking and form filling
- Ad-blocking functionality
- Page content extraction

**Tools Available**: 12 tools
- `navigate_to`, `click_element`, `fill_form_field`
- `add_bookmark`, `remove_bookmark`, `list_bookmarks`
- `get_page_content`, `take_screenshot`
- `enable_adblock`, `disable_adblock`
- `scroll_page`, `wait_for_element`

**Documentation**: [Browser MCP Guide](./browser-mcp-guide.md)

### 2. Radio Player MCP Server (Port 8002)
**Purpose**: Internet radio streaming and station management

**Key Capabilities**:
- Radio playback control (play, pause, stop)
- Station search by name, genre, country, language
- Station management (add, remove, list)
- Volume control
- Metadata retrieval

**Tools Available**: 17 tools
- `play_station`, `pause_playback`, `stop_playback`
- `search_stations_by_name`, `search_by_genre`, `search_by_country`
- `add_station`, `remove_station`, `list_stations`
- `set_volume`, `get_volume`, `mute`, `unmute`
- `get_current_station`, `get_station_info`

**Documentation**: [Radio Player MCP Guide](./radio-player-mcp-guide.md)

### 3. RAG MCP Server (Port 8003)
**Purpose**: Document retrieval and search using vector databases

**Key Capabilities**:
- Document ingestion and indexing
- Semantic search and retrieval
- Query processing with context
- Vector database management
- Multi-format document support

**Tools Available**: 8 tools
- `add_document`, `remove_document`, `list_documents`
- `query_documents`, `search_similar`
- `clear_index`, `get_index_stats`, `rebuild_index`

**Documentation**: [RAG MCP Guide](./rag-mcp-guide.md)

### 4. Word Editor MCP Server (Port 8004)
**Purpose**: Text editing and document manipulation with GUI integration

**Key Capabilities**:
- Text manipulation (set, insert, append, get)
- File operations (open, save)
- CLI command execution
- GUI application integration
- Document workflow automation

**Tools Available**: 8 tools
- `set_text`, `insert_text`, `append_text`, `get_text`
- `open_file`, `save_file`
- `send_cli_command`, `check_gui_status`

**Documentation**: [Word Editor MCP Guide](./word-editor-mcp-guide.md)

## Quick Start Guide

### Starting All Servers
Use the provided startup script:
```bash
cd MCP
./start_all_servers.sh
```

### Starting Individual Servers
```bash
# Browser MCP Server
cd MCP/browser
python server.py

# Radio Player MCP Server
cd MCP/radio_player
python server.py

# RAG MCP Server
cd MCP/rag
python server.py

# Word Editor MCP Server
cd MCP/word_editor
python server.py
```

## Common Use Cases

### 1. Research and Documentation Workflow
**Servers Used**: Browser + RAG + Word Editor

1. **Browser MCP**: Navigate to research websites, extract content
2. **RAG MCP**: Index and search through collected documents
3. **Word Editor MCP**: Compile findings into structured documents

**Example Workflow**:
```json
{
  "research_workflow": [
    {"server": "browser", "action": "navigate_to", "url": "research-site.com"},
    {"server": "browser", "action": "get_page_content"},
    {"server": "rag", "action": "add_document", "content": "extracted_content"},
    {"server": "rag", "action": "query_documents", "query": "key findings"},
    {"server": "word_editor", "action": "set_text", "text": "research_summary"}
  ]
}
```

### 2. Content Creation with Background Audio
**Servers Used**: Radio Player + Word Editor

1. **Radio Player MCP**: Start ambient music or news
2. **Word Editor MCP**: Create and edit documents

**Example Workflow**:
```json
{
  "content_creation": [
    {"server": "radio_player", "action": "search_by_genre", "genre": "ambient"},
    {"server": "radio_player", "action": "play_station", "station_id": "ambient_station"},
    {"server": "word_editor", "action": "open_file", "path": "article.md"},
    {"server": "word_editor", "action": "append_text", "text": "new_content"}
  ]
}
```

### 3. Web Research with Intelligent Bookmarking
**Servers Used**: Browser + RAG

1. **Browser MCP**: Navigate and bookmark relevant pages
2. **RAG MCP**: Index bookmarked content for future retrieval

**Example Workflow**:
```json
{
  "research_bookmarking": [
    {"server": "browser", "action": "navigate_to", "url": "important-article.com"},
    {"server": "browser", "action": "add_bookmark", "title": "Important Research"},
    {"server": "browser", "action": "get_page_content"},
    {"server": "rag", "action": "add_document", "source": "bookmark_content"}
  ]
}
```

### 4. Multimedia Document Processing
**Servers Used**: All Four Servers

1. **Browser MCP**: Gather web-based resources
2. **Radio Player MCP**: Provide background audio
3. **RAG MCP**: Process and index collected materials
4. **Word Editor MCP**: Create comprehensive documents

## Integration Patterns

### Sequential Processing
Servers work in sequence, with output from one feeding into the next:
```
Browser → RAG → Word Editor
(Collect) → (Process) → (Document)
```

### Parallel Operations
Multiple servers work simultaneously:
```
Browser + Radio Player + Word Editor
(Research) + (Audio) + (Writing)
```

### Feedback Loops
Servers interact in cycles for iterative improvement:
```
RAG ↔ Word Editor ↔ Browser
(Query) ↔ (Edit) ↔ (Verify)
```

## Error Handling and Monitoring

### Health Checks
Each server provides status monitoring:
- **Browser**: Connection to browser instance
- **Radio Player**: Audio system availability
- **RAG**: Vector database status
- **Word Editor**: GUI application connectivity

### Common Error Scenarios
1. **Port Conflicts**: Ensure each server uses its designated port
2. **Dependency Issues**: Verify all required packages are installed
3. **Resource Limitations**: Monitor memory and CPU usage
4. **Network Connectivity**: Check internet access for web-based operations

### Troubleshooting Commands
```bash
# Check server status
ps aux | grep "server.py"

# Check port usage
lsof -i :8001-8004

# View server logs
tail -f /path/to/server/logs/*.log
```

## Security Considerations

### Network Security
- All servers run on localhost (127.0.0.1)
- No external network exposure by default
- Port access limited to local machine

### Data Privacy
- **Browser MCP**: Browsing data remains local
- **Radio Player MCP**: No personal data stored
- **RAG MCP**: Documents indexed locally
- **Word Editor MCP**: Files saved to specified locations

### Access Control
- File system permissions control document access
- No authentication required for local connections
- Command validation prevents malicious operations

## Performance Optimization

### Resource Management
- **Memory**: RAG server uses most memory for vector storage
- **CPU**: Browser operations can be CPU-intensive
- **Disk**: Word Editor and RAG require disk space
- **Network**: Browser and Radio Player use network bandwidth

### Scaling Considerations
- Run servers on separate machines for distributed processing
- Use load balancing for high-traffic scenarios
- Implement caching for frequently accessed data
- Monitor resource usage and scale accordingly

## Development and Extension

### Adding New Tools
Each server can be extended with additional tools:
1. Define tool schema in `schemas/` directory
2. Implement handler in `handlers/` directory
3. Register tool in server configuration
4. Update documentation

### Custom Integrations
Servers can be integrated with external systems:
- REST API wrappers
- Database connections
- Third-party service integrations
- Custom protocol implementations

### Testing
Each server includes test suites:
```bash
# Run individual server tests
cd MCP/[server_name]
python -m pytest tests/

# Run integration tests
cd MCP
python -m pytest integration_tests/
```

## Conclusion

The MCP server ecosystem provides a comprehensive platform for AI-assisted automation across web browsing, media consumption, document processing, and text editing. Each server is designed to work independently while offering powerful integration capabilities for complex workflows.

For detailed information about each server, refer to their individual documentation guides linked above. The modular architecture ensures that you can use any combination of servers based on your specific needs while maintaining the flexibility to extend and customize the system as requirements evolve.

## Quick Reference

| Server | Port | Primary Use Case | Key Tools |
|--------|------|------------------|----------|
| Browser | 8001 | Web Automation | navigate_to, click_element, add_bookmark |
| Radio Player | 8002 | Audio Streaming | play_station, search_stations, set_volume |
| RAG | 8003 | Document Search | add_document, query_documents, search_similar |
| Word Editor | 8004 | Text Editing | set_text, open_file, save_file |

**Total Tools Available**: 45 tools across all servers
**Documentation Files**: 5 comprehensive guides
**Supported Workflows**: Research, Content Creation, Data Processing, Automation