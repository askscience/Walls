# Walls Debug Output Guide

This guide explains how to use the enhanced debug and verbose logging features in the Walls system to monitor RAG database queries, user inputs, AI outputs, and MCP server usage.

## Quick Start

### Enable Debug Mode
```bash
# Enable comprehensive debug logging
python start_all.py --debug

# Enable verbose output (same as debug)
python start_all.py --verbose

# Combine with Ollama MCP bridge
python start_all.py --debug --with-ollama
```

## What Debug Mode Shows

### 🚀 Startup Information
- Environment variable setup (RAG_DEBUG, AI_IFACE_DEBUG, MCP_DEBUG, VOICE_DEBUG)
- Component initialization details
- MCP server descriptions and capabilities
- Port allocations and process IDs

### 👤 User Input Tracking
```
============================================================
👤 USER INPUT RECEIVED
============================================================
📝 Query: How do I configure the radio player?
🕒 Timestamp: 14:07:42
📊 Query Length: 35 characters
🔄 Processing through RAG system...
============================================================
```

### 🔍 RAG Database Queries
```
------------------------------------------------------------
🔍 RAG DATABASE QUERY
------------------------------------------------------------
📝 User Query: How do I configure the radio player?
🔍 Searching knowledge base...
📚 Found 3 relevant documents:
   1. 📄 radio_player_config.md
      📁 /docs/radio_player/
      📖 Preview: Configuration options for the radio player...
   
   2. 📄 main_window.py
      📁 /radio_player/
      📖 Preview: The main window class handles UI interactions...
   
   3. 📄 README.md
      📁 /radio_player/
      📖 Preview: Radio Player component provides internet radio...

🤖 AI Response Generated: 1247 characters
📤 Response Preview: To configure the radio player, you can modify...
------------------------------------------------------------
```

### 🤖 AI Response Completion
```
============================================================
🤖 AI RESPONSE COMPLETED
============================================================
📤 Response Length: 1247 characters
🕒 Completion Time: 14:07:42
📖 Response Preview: To configure the radio player, you can modify...
🔧 Potential MCP Server Usage: RADIO
============================================================
```

### 🔧 MCP Server Usage Detection
The system automatically detects when AI responses might trigger MCP server usage:
- **SEARCH** - Document search and knowledge retrieval
- **BROWSE** - Web browsing and URL operations
- **RADIO** - Radio station management and playback
- **EDIT** - Document editing and file operations

## Environment Variables Set

When debug mode is enabled, these environment variables are automatically set:

- `RAG_DEBUG=1` - Shows database queries and document retrieval
- `AI_IFACE_DEBUG=1` - Shows user inputs and AI response processing
- `MCP_DEBUG=1` - Shows MCP server communications
- `VOICE_DEBUG=1` - Shows voice processing details

## MCP Server Details

Debug mode shows detailed information about each MCP server:

### RAG MCP Server
- **Purpose**: Document search, knowledge retrieval, and AI query processing
- **Debug Output**: Database queries, document matches, response generation

### Browser MCP Server
- **Purpose**: Web browsing, page navigation, and content extraction
- **Debug Output**: URL requests, page content extraction, navigation commands

### Radio Player MCP Server
- **Purpose**: Internet radio streaming and station management
- **Debug Output**: Station searches, playback commands, metadata extraction

### Word Editor MCP Server
- **Purpose**: Document editing and text processing
- **Debug Output**: File operations, text modifications, document management

## Usage Examples

### Monitor RAG Database Activity
```bash
# Start with debug mode
python start_all.py --debug

# Ask a question in the AI interface
# Watch terminal for:
# - User input logging
# - Database search details
# - Document retrieval information
# - AI response generation
```

### Track MCP Server Usage
```bash
# Enable debug mode
python start_all.py --verbose

# Use commands that trigger MCP servers:
# - "Search for Python tutorials" (triggers RAG)
# - "Browse to example.com" (triggers Browser)
# - "Play jazz radio" (triggers Radio Player)
# - "Edit my document" (triggers Word Editor)
```

### Monitor Voice Processing
```bash
# Start with debug and voice support
python start_all.py --debug

# Enable voice mode in the AI interface
# Watch terminal for:
# - Voice recognition details
# - Wake word detection
# - Audio processing information
```

## Troubleshooting

### No Debug Output Appearing
1. Ensure you're using `--debug` or `--verbose` flag
2. Check that the AI interface is receiving queries
3. Verify environment variables are set in the process

### Too Much Output
- Debug mode is comprehensive by design
- Use `grep` to filter specific components:
  ```bash
  python start_all.py --debug 2>&1 | grep "RAG"
  python start_all.py --debug 2>&1 | grep "👤 USER"
  ```

### Performance Impact
- Debug logging has minimal performance impact
- Most logging is conditional and only active when needed
- Can be disabled by restarting without debug flags

## Integration with Existing Logs

Debug output complements existing log files:
- Shared server logs: `./logs/shared_server.log`
- MCP server logs: `./logs/mcp_servers.log`
- Component-specific logs in respective directories

## Advanced Usage

### Custom Debug Filtering
```bash
# Filter for specific components
python start_all.py --debug 2>&1 | grep -E "(RAG|USER|MCP)"

# Save debug output to file
python start_all.py --debug > debug_output.log 2>&1

# Monitor in real-time
python start_all.py --debug | tee debug_output.log
```

### Environment Variable Override
```bash
# Enable specific debug components only
RAG_DEBUG=1 python start_all.py
AI_IFACE_DEBUG=1 python start_all.py
MCP_DEBUG=1 python start_all.py
```

This comprehensive debug system provides full visibility into the Walls system's operation, making it easy to understand how user queries are processed, what information is retrieved from the database, how AI responses are generated, and when MCP servers are utilized.