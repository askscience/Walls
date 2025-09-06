# Walls Shared Server

A centralized TCP server system that allows multiple Walls applications to register and receive CLI commands through a unified interface.

## Overview

The shared server system eliminates the need for each application to implement its own TCP server for CLI communication. Instead, applications register with the shared server, which manages port allocation and command routing.

## Features

- **Centralized Management**: Single server handles multiple applications
- **MCP Server Integration**: Built-in Model Context Protocol (MCP) server management
- **Preallocated Port System**: Reserve ports before application startup
- **Automatic Port Allocation**: No port conflicts between applications
- **Configuration Management**: Persistent configuration with defaults
- **CLI Interface**: Command-line tools for server and MCP management
- **Thread-Safe**: Concurrent handling of multiple clients
- **Backward Compatibility**: Maintains existing CLI interfaces

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │   CLI Client    │    │   CLI Client    │
│  (radio_player) │    │    (words)      │    │   (future app)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ Port 9999           │ Port 8765           │ Port 9001
          │                      │                      │
    ┌─────▼──────────────────────▼──────────────────────▼─────┐
    │                Shared Server                            │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
    │  │ App Server  │  │ App Server  │  │ App Server  │     │
    │  │(radio_player│  │   (words)   │  │(future app) │     │
    │  └─────────────┘  └─────────────┘  └─────────────┘     │
    └─────┬──────────────────┬──────────────────┬─────────────┘
          │                  │                  │
    ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
    │Radio Player│      │Words Editor│      │Future App │
    │    GUI     │      │    GUI     │      │    GUI    │
    └───────────┘      └───────────┘      └───────────┘
```

## Components

### Core Components

- **`server.py`**: Main shared server implementation
- **`config.py`**: Configuration management system
- **`client.py`**: Client utilities for connecting to the server
- **`cli.py`**: Command-line interface for server management

### Key Classes

- **`SharedServer`**: Main server class that manages app registrations
- **`AppRegistration`**: Data class for app registration information
- **`ServerConfig`**: Configuration management
- **`ServerClient`**: Client for sending commands to apps

## Usage

### For Application Developers

#### Registering an Application

```python
from shared_server.server import get_shared_server

def my_command_handler(command: str, args: dict) -> dict:
    """Handle commands for your app."""
    if command == 'hello':
        return {'status': 'success', 'message': 'Hello from my app!'}
    return {'status': 'error', 'message': 'Unknown command'}

# Register your app
server = get_shared_server()
port = server.register_app('my_app', my_command_handler, 'My Application')
server.start()

print(f"My app registered on port {port}")
```

#### Sending Commands from CLI

```python
from shared_server.client import send_command_to_app

# Send a command to an app
response = send_command_to_app('my_app', 'hello', {'name': 'World'})
print(response)
```

### CLI Management

#### Check Status
```bash
python -m shared_server.cli status
```

#### Send Commands
```bash
# Send command to radio player
python -m shared_server.cli send radio_player play

# Send command with arguments
python -m shared_server.cli send radio_player volume level=75

# Send command to words editor
python -m shared_server.cli send words set_text text="Hello World"
```

#### Configuration Management
```bash
# Show configuration
python -m shared_server.cli config show

# Show app-specific config
python -m shared_server.cli config show --app radio_player

# Set app port
python -m shared_server.cli config set --app my_app --port 9001

# Enable/disable app
python -m shared_server.cli config set --app my_app --enabled true
```

#### List Available Commands
```bash
python -m shared_server.cli commands radio_player
python -m shared_server.cli commands words
```

#### MCP Server Management
```bash
# List all configured MCP servers
python -m shared_server.cli mcp list

# Check status of all MCP servers
python -m shared_server.cli mcp status

# Check status of specific MCP server
python -m shared_server.cli mcp status word_editor

# Start individual MCP server
python -m shared_server.cli mcp start word_editor
python -m shared_server.cli mcp start browser
python -m shared_server.cli mcp start radio_player

# Start all enabled MCP servers
python -m shared_server.cli mcp start all

# Stop individual MCP server
python -m shared_server.cli mcp stop word_editor

# Stop all running MCP servers
python -m shared_server.cli mcp stop all

# Restart individual MCP server
python -m shared_server.cli mcp restart word_editor

# Restart all enabled MCP servers
python -m shared_server.cli mcp restart all

# Enable/disable MCP servers
python -m shared_server.cli mcp enable word_editor
python -m shared_server.cli mcp disable browser
```

## Configuration

The server uses a JSON configuration file stored in the system temp directory:
`/tmp/walls_shared_server/config.json`

### MCP Server Configuration

MCP servers are configured in the `mcp_servers` section of `config.json`:

```json
{
  "mcp_servers": {
    "word_editor": {
      "enabled": true,
      "port": 8888,
      "script_path": "<REPO_ROOT>/mcp_servers/word_editor/server.py",
      "process_id": null
    },
    "browser": {
      "enabled": true,
      "port": 8889,
      "script_path": "<REPO_ROOT>/mcp_servers/browser/server.py",
      "process_id": null
    },
    "radio_player": {
      "enabled": true,
      "port": 8890,
      "script_path": "<REPO_ROOT>/mcp_servers/radio_player/server.py",
      "process_id": null
    }
  }
}
```

**Configuration Options:**
- `enabled`: Whether the MCP server should be available for starting
- `port`: The port number the MCP server will listen on
- `script_path`: Absolute path to the MCP server script
- `process_id`: Runtime field storing the process ID when running (managed automatically)

### Default Configuration

```json
{
  "server": {
    "base_port": 9000,
    "max_apps": 10,
    "timeout": 5.0
  },
  "apps": {
    "radio_player": {
      "port": 9001,
      "description": "Radio Player Application",
      "enabled": true
    },
    "browser": {
      "port": 9002,
      "description": "Browser Application",
      "enabled": true
    },
    "word_editor": {
      "port": 9003,
      "description": "Word Editor Application",
      "enabled": true
    }
  },
  "logging": {
    "level": "INFO",
    "file": null
  }
}```

## Port Management

The shared server provides two port allocation methods:

### Preallocated Port Method (Recommended)

The preallocated port system reserves ports before applications start, ensuring immediate availability and preventing race conditions:

1. **Port Reservation**: Ports are reserved in `/tmp/walls_shared_server/{app_name}_port` files
2. **Immediate Availability**: Applications can detect their assigned port instantly
3. **Configuration Persistence**: Port assignments are saved to configuration
4. **Startup Coordination**: Enables coordinated application launches

**Use Cases:**
- **System Startup**: Launch multiple applications simultaneously without conflicts
- **Development Environment**: Consistent port assignments across restarts
- **CI/CD Pipelines**: Predictable port allocation for automated testing
- **Docker Deployments**: Pre-defined port mappings for containerized apps

### Dynamic Allocation Method (Legacy)

1. **Configured Ports**: Apps can have predefined ports in the configuration
2. **Dynamic Allocation**: New apps get ports starting from `base_port`
3. **Port Files**: Port numbers are written to temp files for CLI clients
4. **Conflict Resolution**: Automatically finds available ports if conflicts occur

## Startup Methods

### Method 1: Coordinated Startup (Recommended)

Start all applications together with preallocated ports:

```bash
# Start shared server and all applications
python -m shared_server.start_server
```

This method:
- Pre-allocates ports for all known applications
- Launches applications in the correct order
- Ensures no port conflicts
- Provides immediate port availability

### Method 2: Individual Startup (Legacy)

Start applications individually:

```bash
# Start shared server first
python -m shared_server.server

# Then start individual applications
python -m radio_player.modern_gui
python -m browser.main
python -m Words.word_editor.python_gui.main
```

## Backward Compatibility

The shared server maintains backward compatibility with existing CLI interfaces:

- **Legacy Port Support**: Fallback to original ports if port files don't exist
- **Existing CLIs**: Continue to work without modification
- **Gradual Migration**: Apps can be migrated one at a time

## Implementation Guide

### Using Preallocated Ports (Recommended)

#### Step 1: Add Your App to the Preallocated List

Edit `/shared_server/start_server.py` and add your app to the `app_ports` dictionary:

```python
def pre_allocate_ports():
    # Pre-defined app ports
    app_ports = {
        "radio_player": 9001,
        "browser": 9002, 
        "word_editor": 9003,
        "your_app": 9004  # Add your app here
    }
```

#### Step 2: Implement Port Detection in Your App

```python
import tempfile
from pathlib import Path

def get_preallocated_port(app_name: str) -> int:
    """Get the preallocated port for this app."""
    temp_dir = Path(tempfile.gettempdir()) / "walls_shared_server"
    port_file = temp_dir / f"{app_name}_port"
    
    if not port_file.exists():
        raise RuntimeError(f"Port file for {app_name} not found. Start shared server first.")
    
    return int(port_file.read_text().strip())

# In your app's main function:
def main():
    try:
        port = get_preallocated_port("your_app")
        print(f"Using preallocated port: {port}")
        
        # Register with shared server
        from shared_server.server import get_shared_server
        server = get_shared_server()
        server.register_app("your_app", your_command_handler, "Your App Description")
        
        # Start your application logic
        start_your_app(port)
        
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Make sure to start the shared server first with: python -m shared_server.start_server")
```

#### Step 3: Add Launch Command (Optional)

Add your app to the launch sequence in `start_server.py`:

```python
def launch_applications(app_ports):
    apps = [
        ("radio_player", f"{venv_python} -m radio_player.modern_gui"),
        ("browser", f"{venv_python} -m browser.main"),
        ("word_editor", f"{venv_python} -m Words.word_editor.python_gui.main"),
        ("your_app", f"{venv_python} -m your_app.main")  # Add your app
    ]
```

### Using Dynamic Allocation (Legacy)

#### For Radio Player

1. Replace `QTcpServer` initialization with shared server registration
2. Move command handling logic to a handler function
3. Register with shared server on startup

#### For Words Editor

1. Replace custom socket server with shared server registration
2. Move command handling logic to a handler function
3. Register with shared server on startup

### Command Handler Implementation

```python
def your_command_handler(command: str, args: dict) -> dict:
    """Handle CLI commands for your application."""
    try:
        if command == "status":
            return {"status": "success", "message": "App is running"}
        elif command == "action":
            # Perform some action with args
            result = perform_action(args)
            return {"status": "success", "result": result}
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## Error Handling

The shared server includes comprehensive error handling:

- **Connection Errors**: Graceful handling of client disconnections
- **Port Conflicts**: Automatic port resolution
- **Invalid Commands**: Proper error responses
- **App Failures**: Isolated error handling per app

## Security Considerations

- **Local Only**: Server binds to 127.0.0.1 (localhost only)
- **No Authentication**: Suitable for local development only
- **Command Validation**: Apps should validate incoming commands
- **Resource Limits**: Connection timeouts prevent resource exhaustion

## Future Enhancements

- **Authentication**: Add token-based authentication
- **Remote Access**: Support for remote connections
- **Load Balancing**: Distribute load across multiple server instances
- **Monitoring**: Built-in monitoring and metrics
- **Plugin System**: Dynamic app loading and unloading

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Check for existing server instances
   - Use `lsof -i :PORT` to find conflicting processes

2. **App Not Responding**
   - Check if app is registered: `python -m shared_server.cli status`
   - Verify app is running and listening

3. **Configuration Issues**
   - Reset config: `python -m shared_server.cli config reset`
   - Check config file permissions

### Debug Mode

Enable debug logging by setting the log level in configuration:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## Best Practices

### For New Applications

1. **Use Preallocated Ports**: Always implement port detection for new apps
2. **Error Handling**: Handle missing port files gracefully
3. **Command Validation**: Validate all incoming CLI commands
4. **Status Endpoints**: Implement basic status/health check commands
5. **Documentation**: Document all available CLI commands

### For System Integration

1. **Start Order**: Always start shared server before individual applications
2. **Port Range**: Keep preallocated ports in the 9001-9010 range
3. **Configuration**: Update both code and configuration when adding apps
4. **Testing**: Test both coordinated and individual startup methods

## Contributing

When adding new applications to the Walls ecosystem:

1. Add your app to the preallocated ports list in `start_server.py`
2. Implement port detection and shared server registration
3. Create proper command handlers with error handling
4. Add app configuration to the default config
5. Update CLI command lists and documentation
6. Test with existing applications using both startup methods