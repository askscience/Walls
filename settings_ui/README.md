# Settings UI - Configuration Manager

A modern, minimalist settings interface for the Walls AI assistant ecosystem. Built with PySide6 and gui_core components.

## Features

- **Tabbed Interface**: Organized configuration panels for different components
- **Modern UI**: Built with gui_core components following minimalist design principles
- **Real-time Validation**: Input validation and error handling
- **Auto-save**: Automatic configuration saving with backup support
- **Cross-platform**: Works on macOS, Windows, and Linux

## Configuration Panels

### 🖥️ Server Settings
Manages `shared_server/APP_config.json`:
- Server configuration (ports, timeouts, limits)
- Application settings (radio, browser, word editor)
- Logging configuration
- Security settings (authentication, API keys)

### 🔌 MCP Servers
Manages `shared_server/MCP_config.json`:
- MCP server configurations
- Server capabilities and tools
- Process management settings
- Monitoring and logging

### 🧠 RAG Settings
Manages `rag/config.json`:
- Data directory and Chroma DB settings
- Ollama model configurations
- LLM parameters (temperature, max tokens)
- File exclusion patterns

### 🎤 Voice Settings
Manages `ai_interface/voice_mode/config/voice_config.json`:
- Audio configuration (sample rate, devices)
- Wake word settings
- Speech recognition parameters
- Text-to-speech settings
- UI display options

## Project Structure

```
settings_ui/
├── __init__.py              # Package initialization
├── main.py                  # Entry point script
├── settings_window.py       # Main window with tabbed interface
├── README.md               # This documentation
├── panels/                 # Configuration panels
│   ├── __init__.py
│   ├── server_panel.py     # Server settings panel
│   ├── mcp_panel.py        # MCP servers panel
│   ├── rag_panel.py        # RAG settings panel
│   └── voice_panel.py      # Voice settings panel
└── services/               # Backend services
    ├── __init__.py
    └── config_manager.py    # Configuration management
```

## Usage

### Running the Settings UI

```bash
# From the settings_ui directory
python main.py

# Or from the project root
python -m settings_ui.main
```

### Programmatic Usage

```python
from settings_ui import SettingsWindow, ConfigManager
from PySide6.QtWidgets import QApplication

app = QApplication([])
window = SettingsWindow()
window.show()
app.exec()
```

### Configuration Manager

```python
from settings_ui import ConfigManager

config_manager = ConfigManager()

# Load configuration
app_config = config_manager.load_config('app')

# Save configuration
config_manager.save_config('app', updated_config)

# Validate configuration
is_valid = config_manager.validate_config('app', config_data)
```

## Dependencies

- **PySide6**: Qt6 bindings for Python
- **gui_core**: Custom UI components (cards, buttons, switches, etc.)
- **Python 3.8+**: Required Python version

## Configuration Files

The settings UI manages these configuration files:

1. `shared_server/APP_config.json` - Server and application settings
2. `shared_server/MCP_config.json` - MCP server configurations
3. `rag/config.json` - RAG system settings
4. `ai_interface/voice_mode/config/voice_config.json` - Voice interface settings

## Design Principles

- **Minimalist**: Clean, uncluttered interface
- **Responsive**: Adapts to different screen sizes
- **Accessible**: Clear labels and logical grouping
- **Consistent**: Uniform styling across all panels
- **Efficient**: Fast loading and saving of configurations

## Error Handling

- Input validation with real-time feedback
- Automatic backup creation before saving
- Graceful error recovery
- User-friendly error messages
- Status bar notifications

## Customization

The UI can be customized by:
- Modifying gui_core component styles
- Adding new configuration panels
- Extending the ConfigManager for new file types
- Customizing validation rules

## Contributing

When adding new configuration panels:
1. Create a new panel class inheriting from QWidget
2. Implement `load_config()` and `get_config()` methods
3. Add the panel to the main settings window
4. Update the ConfigManager if needed
5. Follow the existing code style and patterns