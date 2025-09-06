"""Voice settings panel for configuring voice interface."""

import json
import os
from typing import Dict, Any
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGridLayout
from PySide6.QtCore import Signal
from gui_core.components.cards import Card
from gui_core.components.switch.widgets import Switch


class VoicePanel(QWidget):
    """Panel for voice interface settings."""
    
    config_changed = Signal(str, dict)  # (panel_name, config_data)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = {}
        self.widgets = {}
        self.setup_ui()
        self.load_default_config()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Voice Interface")
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        
        subtitle = QLabel("Setup voice interaction and speech settings")
        subtitle.setObjectName("panelSubtitle")
        layout.addWidget(subtitle)
        
        # Audio Devices Card
        layout.addWidget(self.create_audio_devices_card())
        
        # Speech Recognition Card
        layout.addWidget(self.create_speech_recognition_card())
        
        # Text-to-Speech Card
        layout.addWidget(self.create_text_to_speech_card())
        
        # UI Settings Card
        layout.addWidget(self.create_ui_settings_card())
        
        layout.addStretch()
    
    def create_audio_devices_card(self):
        """Create audio devices settings card."""
        card = Card("Audio Devices")
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Input Device
        layout.addWidget(QLabel("Input Device:"), 0, 0)
        self.widgets['input_device'] = QComboBox()
        self.widgets['input_device'].addItems(["Default Microphone", "Built-in Microphone", "External Microphone"])
        self.widgets['input_device'].setCurrentText("Default Microphone")
        self.widgets['input_device'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['input_device'], 0, 1)
        
        # Output Device
        layout.addWidget(QLabel("Output Device:"), 1, 0)
        self.widgets['output_device'] = QComboBox()
        self.widgets['output_device'].addItems(["Default Speaker", "Built-in Speakers", "Headphones"])
        self.widgets['output_device'].setCurrentText("Default Speaker")
        self.widgets['output_device'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['output_device'], 1, 1)
        
        card.setLayout(layout)
        return card
    
    def create_speech_recognition_card(self):
        """Create speech recognition settings card."""
        card = Card("Speech Recognition", "Configure speech-to-text settings")
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Enable Speech Recognition
        layout.addWidget(QLabel("Enable speech recognition:"), 0, 0)
        self.widgets['speech_enabled'] = Switch()
        self.widgets['speech_enabled'].setChecked(False)
        self.widgets['speech_enabled'].toggled.connect(self.on_config_changed)
        layout.addWidget(self.widgets['speech_enabled'], 0, 1)
        
        # Engine
        layout.addWidget(QLabel("Engine:"), 1, 0)
        self.widgets['speech_engine'] = QComboBox()
        self.widgets['speech_engine'].addItems(["vosk", "whisper"])
        self.widgets['speech_engine'].setCurrentText("vosk")
        self.widgets['speech_engine'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['speech_engine'], 1, 1)
        
        # Vosk Model
        layout.addWidget(QLabel("Vosk Model:"), 2, 0)
        self.widgets['vosk_model'] = QComboBox()
        self.widgets['vosk_model'].addItems([
            "vosk-model-small-en-us-0.15",
            "vosk-model-en-us-0.22",
            "vosk-model-en-us-0.22-lgraph"
        ])
        self.widgets['vosk_model'].setCurrentText("vosk-model-small-en-us-0.15")
        self.widgets['vosk_model'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['vosk_model'], 2, 1)
        
        # Language
        layout.addWidget(QLabel("Language:"), 3, 0)
        self.widgets['speech_language'] = QComboBox()
        self.widgets['speech_language'].addItems(["English", "Spanish", "French", "German"])
        self.widgets['speech_language'].setCurrentText("English")
        self.widgets['speech_language'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['speech_language'], 3, 1)
        
        card.setLayout(layout)
        return card
    
    def create_text_to_speech_card(self):
        """Create text-to-speech settings card."""
        card = Card("Text-to-Speech", "Configure text-to-speech settings")
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Enable TTS
        layout.addWidget(QLabel("Enable text-to-speech:"), 0, 0)
        self.widgets['tts_enabled'] = Switch()
        self.widgets['tts_enabled'].setChecked(False)
        self.widgets['tts_enabled'].toggled.connect(self.on_config_changed)
        layout.addWidget(self.widgets['tts_enabled'], 0, 1)
        
        # Engine
        layout.addWidget(QLabel("Engine:"), 1, 0)
        self.widgets['tts_engine'] = QComboBox()
        self.widgets['tts_engine'].addItems(["kokoro", "pyttsx3", "azure", "google"])
        self.widgets['tts_engine'].setCurrentText("kokoro")
        self.widgets['tts_engine'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['tts_engine'], 1, 1)
        
        # Voice
        layout.addWidget(QLabel("Voice:"), 2, 0)
        self.widgets['tts_voice'] = QComboBox()
        self.widgets['tts_voice'].setEditable(True)
        self.widgets['tts_voice'].addItems(["af_heart", "af_bella", "af_sarah", "am_adam"])
        self.widgets['tts_voice'].setCurrentText("af_heart")
        self.widgets['tts_voice'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['tts_voice'], 2, 1)
        
        # Language Code
        layout.addWidget(QLabel("Language Code:"), 3, 0)
        self.widgets['tts_lang_code'] = QComboBox()
        self.widgets['tts_lang_code'].setEditable(True)
        self.widgets['tts_lang_code'].addItems(["a", "en", "es", "fr", "de"])
        self.widgets['tts_lang_code'].setCurrentText("a")
        self.widgets['tts_lang_code'].currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.widgets['tts_lang_code'], 3, 1)
        
        card.setLayout(layout)
        return card
    
    def create_ui_settings_card(self):
        """Create UI settings card."""
        card = Card("UI Settings", "Configure voice interface settings")
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Show Waveform
        layout.addWidget(QLabel("Show Waveform:"), 0, 0)
        self.widgets['show_waveform'] = Switch()
        self.widgets['show_waveform'].setChecked(True)
        self.widgets['show_waveform'].toggled.connect(self.on_config_changed)
        layout.addWidget(self.widgets['show_waveform'], 0, 1)
        
        # Auto Start Listening
        layout.addWidget(QLabel("Auto Start Listening:"), 1, 0)
        self.widgets['auto_start_listening'] = Switch()
        self.widgets['auto_start_listening'].setChecked(False)
        self.widgets['auto_start_listening'].toggled.connect(self.on_config_changed)
        layout.addWidget(self.widgets['auto_start_listening'], 1, 1)
        
        card.setLayout(layout)
        return card
    
    def on_config_changed(self):
        """Handle configuration changes and emit signal."""
        config = {
            "audio_devices": {
                "input_device": self.widgets['input_device'].currentText(),
                "output_device": self.widgets['output_device'].currentText()
            },
            "speech_recognition": {
                "enabled": self.widgets['speech_enabled'].isChecked(),
                "engine": self.widgets['speech_engine'].currentText(),
                "vosk_model": self.widgets['vosk_model'].currentText(),
                "language": self.widgets['speech_language'].currentText()
            },
            "text_to_speech": {
                "enabled": self.widgets['tts_enabled'].isChecked(),
                "engine": self.widgets['tts_engine'].currentText(),
                "voice": self.widgets['tts_voice'].currentText(),
                "lang_code": self.widgets['tts_lang_code'].currentText()
            },
            "ui": {
                "show_waveform": self.widgets['show_waveform'].isChecked(),
                "auto_start_listening": self.widgets['auto_start_listening'].isChecked()
            }
        }
        
        self.config_data = config
        self.config_changed.emit("voice", config)
    
    def load_config(self, config_data: Dict[str, Any]):
        """Load configuration data into the UI."""
        self.config_data = config_data
        
        # Load audio devices settings
        audio_devices = config_data.get("audio_devices", {})
        if 'input_device' in self.widgets:
            self.widgets['input_device'].setCurrentText(audio_devices.get("input_device", "Default Microphone"))
        if 'output_device' in self.widgets:
            self.widgets['output_device'].setCurrentText(audio_devices.get("output_device", "Default Speaker"))
        
        # Load speech recognition settings
        speech_recognition = config_data.get("speech_recognition", {})
        if 'speech_enabled' in self.widgets:
            self.widgets['speech_enabled'].setChecked(speech_recognition.get("enabled", False))
        if 'speech_engine' in self.widgets:
            self.widgets['speech_engine'].setCurrentText(speech_recognition.get("engine", "vosk"))
        if 'vosk_model' in self.widgets:
            self.widgets['vosk_model'].setCurrentText(speech_recognition.get("vosk_model", "vosk-model-small-en-us-0.15"))
        if 'speech_language' in self.widgets:
            self.widgets['speech_language'].setCurrentText(speech_recognition.get("language", "English"))
        
        # Load text-to-speech settings
        text_to_speech = config_data.get("text_to_speech", {})
        if 'tts_enabled' in self.widgets:
            self.widgets['tts_enabled'].setChecked(text_to_speech.get("enabled", False))
        if 'tts_engine' in self.widgets:
            self.widgets['tts_engine'].setCurrentText(text_to_speech.get("engine", "kokoro"))
        if 'tts_voice' in self.widgets:
            self.widgets['tts_voice'].setCurrentText(text_to_speech.get("voice", "af_heart"))
        if 'tts_lang_code' in self.widgets:
            self.widgets['tts_lang_code'].setCurrentText(text_to_speech.get("lang_code", "a"))
        
        # Load UI settings
        ui_settings = config_data.get("ui", {})
        if 'show_waveform' in self.widgets:
            self.widgets['show_waveform'].setChecked(ui_settings.get("show_waveform", True))
        if 'auto_start_listening' in self.widgets:
            self.widgets['auto_start_listening'].setChecked(ui_settings.get("auto_start_listening", False))
    
    def load_default_config(self):
        """Load the default configuration from voice_config.json."""
        # Get the project root directory (3 levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = Path(os.path.join(project_root, 'ai_interface', 'voice_mode', 'config', 'voice_config.json'))
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                self.load_config(config_data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading voice config: {e}")
                # Load with default values if file doesn't exist or is invalid
                self.load_config({})
        else:
            # Load with default values if file doesn't exist
            self.load_config({})