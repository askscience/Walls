# Walls - AI Assistant Ecosystem

> **A modular AI assistant ecosystem with voice/text interfaces, RAG capabilities, command execution, and integrated applications for radio streaming, web browsing, and document editing.**

A comprehensive AI assistant system with voice and text interfaces, featuring RAG (Retrieval-Augmented Generation), command execution, and integrated applications.

## 🌟 Overview

Walls is a modular AI assistant ecosystem that combines multiple applications and services to provide a seamless AI-powered experience. The system features both voice and text-based interactions, intelligent command execution, and integrated applications for radio streaming, web browsing, and document editing.

## 🏗️ Architecture

### Core Components

- **AI Interface** (`ai_interface/`) - Main GUI application with text and voice modes
- **RAG System** (`rag/`) - Retrieval-Augmented Generation for intelligent responses
- **Shared Server** (`shared_server/`) - Inter-application communication hub
- **GUI Core** (`gui_core/`) - Reusable UI components and theming

### Integrated Applications

- **Radio Player** (`radio_player/`) - Internet radio streaming with modern GUI
- **Browser** (`browser/`) - Web browser with AI integration
- **Words** (`Words/`) - Document editor with Python GUI and Rust core

## 🚀 Features

### AI Interface
- **Dual Mode Operation**: Text-based chat interface and voice interaction
- **Command Execution**: Automatic detection and execution of bash commands from AI responses
- **RAG Integration**: Context-aware responses using document retrieval
- **Real-time Streaming**: Live AI response streaming with loading indicators
- **Chat Management**: Persistent chat sessions with history

### Voice Mode
- **Wake Word Detection**: "Hey Assistant" activation
- **Speech Recognition**: Vosk-powered offline speech-to-text
- **Text-to-Speech**: Kokoro TTS for natural voice responses
- **Audio Processing**: Real-time audio capture and processing

### Command Interception
- **Smart Detection**: Automatic bash code block recognition in AI responses
- **Safety Policies**: Blacklist-based command filtering for security
- **Application Auto-start**: Automatic launching of required services
- **Command Corrections**: Intelligent error correction for common mistakes

### Radio Player
- **Internet Radio**: Stream thousands of radio stations worldwide
- **Modern GUI**: Beautiful, responsive interface with visualizations
- **CLI Interface**: Command-line control for automation
- **Search & Discovery**: Find stations by genre, country, or name
- **Metadata Display**: Real-time song information and station details

### Browser Integration
- **AI-Powered Browsing**: Intelligent web navigation
- **Content Summarization**: AI-powered page summaries
- **Bookmark Management**: Organized bookmark system
- **Headless Mode**: Background web operations

### Document Editor (Words)
- **Hybrid Architecture**: Python GUI with Rust core for performance
- **Rich Text Editing**: Advanced document editing capabilities
- **AI Integration**: Smart writing assistance

## 📦 Installation

### Prerequisites
- Python 3.8+
- Virtual environment support
- macOS (primary platform)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/askscience/Walls.git
   cd Walls
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Kokoro TTS** (for voice mode):
   ```bash
   ./install_kokoro.sh
   ```

5. **Start all services**:
   ```bash
   python start_all.py
   ```

## 🎯 Usage

### Starting the System

**All Services**:
```bash
python start_all.py
```

**Individual Components**:
```bash
# AI Interface (Text Mode)
python ai_interface/main.py

# Voice Mode
python ai_interface/voice_mode/voice_manager.py

# Radio Player
python -m radio_player.modern_gui

# Browser
python -m browser.main

# Shared Server
python shared_server/start_server.py
```

### AI Interface Usage

1. **Text Mode**: Type questions and receive AI responses with automatic command execution
2. **Voice Mode**: Say "Hey Assistant" followed by your question
3. **Command Execution**: AI responses containing bash code blocks are automatically executed
4. **Radio Control**: Ask for music and the system will search and play radio stations

### Voice Commands Examples

- "Hey Assistant, play some jazz music"
- "Hey Assistant, search for news radio stations"
- "Hey Assistant, open the browser"
- "Hey Assistant, what's the weather like?"

### Text Interface Examples

- "Find and play classical music stations"
- "Search for radio stations in France"
- "Open the word editor"
- "Browse to wikipedia.com"

## 🔧 Configuration

### Environment Variables

- `AI_IFACE_DEBUG=1` - Enable debug logging for command interception
- `RAG_DEBUG=1` - Enable RAG system debug output
- `VOICE_DEBUG=1` - Enable voice processing debug logs

### Configuration Files

- `rag/config.py` - RAG system configuration
- `rag/prompts.json` - AI prompt templates
- `shared_server/config.py` - Inter-service communication settings

## 🛠️ Development

### Project Structure

```
Walls/
├── ai_interface/          # Main AI interface application
│   ├── components/        # UI components
│   ├── main/             # Main interface logic
│   ├── services/         # Background services
│   ├── utils/            # Utilities and command handling
│   └── voice_mode/       # Voice interaction components
├── rag/                  # RAG system
├── shared_server/        # Inter-application communication
├── gui_core/            # Reusable UI components
├── radio_player/        # Internet radio application
├── browser/             # Web browser integration
├── Words/               # Document editor
└── requirements.txt     # Python dependencies
```

### Key Technologies

- **GUI Framework**: PySide6 (Qt)
- **AI/ML**: Transformers, sentence-transformers, FAISS
- **Voice Processing**: Vosk (STT), Kokoro (TTS)
- **Web**: Requests, BeautifulSoup
- **Audio**: PyAudio, sounddevice
- **Database**: Vector stores for RAG

### Adding New Features

1. **New Commands**: Add patterns to `ai_interface/utils/command_corrections.py`
2. **UI Components**: Extend `gui_core/components/`
3. **Voice Commands**: Modify voice processing in `ai_interface/voice_mode/`
4. **RAG Data**: Add documents to `rag/data/`

## 🔒 Security

### Command Execution Safety

- **Blacklist Filtering**: Dangerous commands are automatically blocked
- **Sandboxed Execution**: Commands run in controlled environment
- **User Confirmation**: Critical operations require confirmation
- **Audit Logging**: All command executions are logged

### Safe Commands

- Application launches (radio_player, browser, etc.)
- File operations within project directory
- Network requests to known APIs
- System information queries

### Blocked Commands

- System modification commands (`rm -rf`, `sudo`, etc.)
- Network security bypasses
- Privilege escalation attempts
- Destructive file operations

## 🐛 Troubleshooting

### Common Issues

**Voice Recognition Not Working**:
- Check microphone permissions
- Verify Vosk models are installed
- Enable voice debug logging

**Commands Not Executing**:
- Enable `AI_IFACE_DEBUG=1`
- Check command safety policies
- Verify virtual environment activation

**Radio Player Issues**:
- Check internet connection
- Verify shared server is running
- Try restarting the radio player service

**Import Errors**:
- Ensure virtual environment is activated
- Check all dependencies are installed
- Verify Python path configuration

## 📝 License

This project is licensed under the MIT License. See individual component LICENSE files for specific details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Enable debug logging for detailed error information
3. Review component-specific README files
4. Submit issues with detailed logs and reproduction steps

---

**Walls** - Your intelligent AI assistant ecosystem, bringing together voice, text, and application integration in one powerful platform.