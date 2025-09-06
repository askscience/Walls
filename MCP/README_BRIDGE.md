# Ollama MCP Bridge Usage Guide

This simplified bridge uses the `ollama-mcp-bridge` library to automatically integrate MCP tools with Ollama.

## How It Works

The bridge:
1. Reads your shared server's MCP configuration
2. Generates a compatible configuration for `ollama-mcp-bridge`
3. Starts a proxy server that sits between your Ollama client and Ollama server
4. Automatically injects MCP tools into chat completions

## Usage

### 1. Start the Bridge

```bash
# From the project root
cd ollama-mcp-bridge && uv run ollama-mcp-bridge
```

This will:
- Read your shared server's MCP configuration
- Generate a temporary bridge configuration (no files saved)
- Start the bridge on `http://localhost:8000`

### 2. Use with Ollama Client

Instead of connecting to Ollama directly at `http://localhost:11434`, point your client to the bridge at `http://localhost:8000`.

#### Example with curl:

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {
        "role": "user",
        "content": "Can you help me edit a document using the word editor?"
      }
    ],
    "stream": false
  }'
```

#### Example with Python:

```python
import requests

response = requests.post('http://localhost:8000/api/chat', json={
    "model": "llama3.2:1b",
    "messages": [
        {
            "role": "user",
            "content": "Search for reggaeton radio stations"
        }
    ],
    "stream": False
})

print(response.json())
```

## Available MCP Tools

The bridge automatically exposes tools from all enabled MCP servers:

- **word_editor**: Text editing, file operations, CLI commands
- **browser**: Web navigation, bookmarks, page interaction
- **radio_player**: Radio station search, playback control
- **rag**: Document search, knowledge retrieval

## Configuration

The bridge automatically reads configuration from `shared_server/MCP_config.json` - the single source of truth for all MCP servers. No duplicate configs or manual setup needed!

## Troubleshooting

### Bridge won't start
- Ensure `ollama-mcp-bridge` is installed: `pip install ollama-mcp-bridge`
- Check that Ollama is running on `http://localhost:11434`
- Verify shared server config exists at `shared_server/MCP_config.json`

### MCP tools not working
- The bridge starts its own MCP server instances
- You don't need the shared server running for the bridge to work
- Each tool call will be automatically handled by the bridge

### Port conflicts
- Default bridge port is 8000
- You can modify the port in the `start_bridge()` function call
- Make sure no other services are using the same port