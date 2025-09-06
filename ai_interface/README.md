# AI Interface

A modern, transparent AI interface with blur effects that connects to the RAG (Retrieval-Augmented Generation) system for intelligent document querying.

## Features

- **Transparent Design**: Beautiful transparent panels with blur effects
- **Bottom Input Panel**: Fixed position at bottom of screen with AI loader and text input
- **Streaming Responses**: Real-time streaming AI responses with large, readable text
- **Mozilla Headline Font**: Uses the Mozilla Headline font for elegant typography
- **RAG Integration**: Seamlessly connects to the existing RAG pipeline
- **Responsive UI**: Animated AI loader during processing

## Architecture

The AI interface is organized into logical components:

```
ai_interface/
├── main.py                 # Main launcher script
├── requirements.txt        # Dependencies
├── README.md              # This file
├── components/            # UI components
│   ├── __init__.py
│   ├── blur_widgets.py    # Transparent blur effect widgets
│   ├── unified_panel.py   # Main unified interface panel
│   ├── chat_bubble.py     # Chat bubble components
│   └── accordion_widget.py # Accordion widget for expandable sections
├── services/              # Service layer
│   ├── __init__.py
│   ├── rag_integration.py # RAG pipeline wrapper
│   └── chat_manager.py    # Chat session management
└── main/                  # Main application
    └── interface.py       # Main interface coordinator
```

## Components

### Unified Panel
- Single integrated panel combining input, chat history, and response display
- Transparent design with blur effects
- Real-time streaming responses with chat bubble interface
- Built-in chat session management and history
- Responsive layout with accordion-style expandable sections

### RAG Service
- Wrapper around the existing RAG pipeline
- Handles asynchronous queries and streaming responses
- Thread-safe implementation with Qt signals

## Usage

### Prerequisites

1. Ensure the RAG system is properly set up and working:
   ```bash
   cd ../rag
   python main.py --index  # Index your documents first
   ```

2. Make sure gui_core is available:
   ```bash
   cd ../gui_core
   python demo.py  # Test that gui_core works
   ```

### Running the Interface

```bash
# From the ai_interface directory
python main.py
```

Or run it as a module:
```bash
# From the parent directory (Walls)
python -m ai_interface.main
```

### Using the Interface

1. **Start the application**: The input panel will appear at the bottom of your screen
2. **Ask questions**: Type your question in the transparent input field
3. **Submit**: Press Enter to submit your query
4. **Watch the AI work**: The AI loader will animate while processing
5. **Read responses**: Streaming responses appear in the center panel with large text
6. **Continue conversation**: Ask follow-up questions as needed

## Keyboard Shortcuts

- **Enter**: Submit query
- **Ctrl+C**: Exit application (in terminal)

## Customization

### Font Size
To change the response text size, modify the font settings in `components/unified_panel.py`:
```python
font-size: 100px;  # Change this value
```

### Panel Positioning
To adjust panel positions, modify the coordinates in `main/interface.py`:
```python
# Input panel position
input_y = screen_geometry.height() - input_height - 50  # Distance from bottom

# Response panel position  
response_y = 100  # Distance from top
```

### Blur Effects
To adjust blur intensity, modify the `setBlurRadius()` values in `components/blur_widgets.py`:
```python
blur_effect.setBlurRadius(15)  # Input panel blur
blur_effect.setBlurRadius(20)  # Response panel blur
```

## Dependencies

The AI interface depends on:
- **PySide6**: Qt6 GUI framework
- **gui_core**: UI components and theming
- **rag**: RAG pipeline for AI responses
- **Mozilla Headline Font**: Typography (included in gui_core/utils/fonts)

## Troubleshooting

### RAG Service Not Ready
If you see "RAG service is not ready":
1. Check that the RAG system is properly installed
2. Ensure documents are indexed: `cd ../rag && python main.py --index`
3. Verify Ollama is running with the required models

### Font Not Loading
If the Mozilla Headline font doesn't load:
1. Check that the font file exists in `../gui_core/utils/fonts/`
2. The system will fall back to Arial if the font is missing

### Panels Not Visible
If the panels don't appear:
1. Check that you're running on a system with a desktop environment
2. Try running the gui_core demo first to test Qt functionality
3. Ensure proper permissions for creating transparent windows

## Development

### Adding New Features
1. **New Components**: Add to `components/` directory
2. **New Services**: Add to `services/` directory  
3. **UI Changes**: Modify the main interface in `main/interface.py`

### Testing
Test individual components:
```python
# Test unified panel
from components.unified_panel import UnifiedPanel
# Test chat components
from components.chat_bubble import ChatBubbleContainer
# Test RAG service
from services.rag_integration import RAGIntegrationService
# Test chat manager
from services.chat_manager import ChatManager
```

## License

This AI interface inherits the same license as the parent project.