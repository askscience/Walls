"""Modern Voice Panel with flat design and gui_core components."""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy, QTextEdit, QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QIcon

# Import gui_core components
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from gui_core.components.cards.widgets import Card
from gui_core.components.line_edit.widgets import LineEdit
from gui_core.components.button.widgets import PrimaryButton
from gui_core.components.switch.widgets import Switch
from gui_core.components.checkbox.widgets import CheckBox
from gui_core.components.combo_box.widgets import ComboBox
from gui_core.components.slider.widgets import Slider
from gui_core.components.progress_bar.widgets import ProgressBar


class VoicePanel(QWidget):
    """Modern Voice configuration panel for speech recognition and synthesis."""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = {}
        self.audio_devices = []
        self.setup_ui()
        self.refresh_audio_devices()
    
    def setup_ui(self):
        """Setup the modern flat user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameStyle(0)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 16, 0)  # Right margin for scrollbar
        content_layout.setSpacing(20)
        
        # Voice system status card
        status_card = self.create_status_card()
        content_layout.addWidget(status_card)
        
        # Audio devices card
        devices_card = self.create_audio_devices_card()
        content_layout.addWidget(devices_card)
        
        # Speech recognition card
        recognition_card = self.create_recognition_card()
        content_layout.addWidget(recognition_card)
        
        # Text-to-speech card
        tts_card = self.create_tts_card()
        content_layout.addWidget(tts_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def create_status_card(self):
        """Create voice system status card."""
        card = Card("Voice System Status", "Current status of speech recognition and synthesis")
        
        status_layout = QGridLayout()
        status_layout.setSpacing(12)
        
        # System status
        status_layout.addWidget(QLabel("Status:"), 0, 0)
        self.status_indicator = QLabel("● Inactive")
        self.status_indicator.setObjectName("statusIndicator")
        status_layout.addWidget(self.status_indicator, 0, 1)
        
        # Recognition engine status
        status_layout.addWidget(QLabel("Recognition:"), 1, 0)
        self.recognition_status = QLabel("Not initialized")
        status_layout.addWidget(self.recognition_status, 1, 1)
        
        # TTS engine status
        status_layout.addWidget(QLabel("Text-to-Speech:"), 2, 0)
        self.tts_status = QLabel("Not initialized")
        status_layout.addWidget(self.tts_status, 2, 1)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        card.addWidget(status_widget)
        return card
    
    def create_audio_devices_card(self):
        """Create audio devices configuration card."""
        card = Card("Audio Devices", "Configure microphone and speaker settings")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Input device
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("Microphone:"))
        self.input_device_combo = ComboBox()
        self.input_device_combo.currentTextChanged.connect(self.on_config_changed)
        input_layout.addWidget(self.input_device_combo)
        layout.addLayout(input_layout)
        
        # Output device
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Speaker:"))
        self.output_device_combo = ComboBox()
        self.output_device_combo.currentTextChanged.connect(self.on_config_changed)
        output_layout.addWidget(self.output_device_combo)
        layout.addLayout(output_layout)
        
        devices_widget = QWidget()
        devices_widget.setLayout(layout)
        card.addWidget(devices_widget)
        return card
    
    def create_recognition_card(self):
        """Create speech recognition configuration card."""
        card = Card("Speech Recognition", "Configure speech-to-text settings")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Enable recognition
        enable_layout = QHBoxLayout()
        self.recognition_switch = Switch("Enable Speech Recognition")
        self.recognition_switch.toggled.connect(self.on_config_changed)
        enable_layout.addWidget(self.recognition_switch)
        enable_layout.addStretch()
        layout.addLayout(enable_layout)
        
        # Recognition engine
        engine_layout = QHBoxLayout()
        engine_layout.addWidget(QLabel("Recognition Engine:"))
        self.recognition_engine_combo = ComboBox()
        self.recognition_engine_combo.addItems([
            "Google Speech Recognition",
            "OpenAI Whisper",
            "Azure Speech"
        ])
        self.recognition_engine_combo.currentTextChanged.connect(self.on_config_changed)
        engine_layout.addWidget(self.recognition_engine_combo)
        layout.addLayout(engine_layout)
        
        recognition_widget = QWidget()
        recognition_widget.setLayout(layout)
        card.addWidget(recognition_widget)
        return card
    
    def create_tts_card(self):
        """Create text-to-speech configuration card."""
        card = Card("Text-to-Speech", "Configure speech synthesis settings")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Enable TTS
        enable_layout = QHBoxLayout()
        self.tts_switch = Switch("Enable Text-to-Speech")
        self.tts_switch.toggled.connect(self.on_config_changed)
        enable_layout.addWidget(self.tts_switch)
        enable_layout.addStretch()
        layout.addLayout(enable_layout)
        
        # TTS engine
        engine_layout = QHBoxLayout()
        engine_layout.addWidget(QLabel("TTS Engine:"))
        self.tts_engine_combo = ComboBox()
        self.tts_engine_combo.addItems([
            "System Default",
            "OpenAI TTS",
            "Azure Speech"
        ])
        self.tts_engine_combo.currentTextChanged.connect(self.on_config_changed)
        engine_layout.addWidget(self.tts_engine_combo)
        layout.addLayout(engine_layout)
        
        tts_widget = QWidget()
        tts_widget.setLayout(layout)
        card.addWidget(tts_widget)
        return card
    
    def on_config_changed(self):
        """Handle configuration changes and emit signal."""
        config = {
            "audio_devices": {
                "input_device": self.input_device_combo.currentText(),
                "output_device": self.output_device_combo.currentText()
            },
            "speech_recognition": {
                "enabled": self.recognition_switch.isChecked(),
                "engine": self.recognition_engine_combo.currentText()
            },
            "text_to_speech": {
                "enabled": self.tts_switch.isChecked(),
                "engine": self.tts_engine_combo.currentText()
            }
        }
        
        self.config_data = config
        self.config_changed.emit(config)
    
    def refresh_audio_devices(self):
        """Refresh the list of available audio devices."""
        input_devices = [
            "Default Microphone",
            "Built-in Microphone",
            "USB Microphone"
        ]
        
        output_devices = [
            "Default Speaker",
            "Built-in Speakers",
            "USB Headphones"
        ]
        
        self.input_device_combo.clear()
        self.input_device_combo.addItems(input_devices)
        
        self.output_device_combo.clear()
        self.output_device_combo.addItems(output_devices)
    
    def load_config(self, config_data: Dict[str, Any]):
        """Load configuration data into the panel."""
        self.config_data = config_data.copy()
        
        # Load audio devices
        audio_devices = config_data.get("audio_devices", {})
        self.input_device_combo.setCurrentText(audio_devices.get("input_device", "Default Microphone"))
        self.output_device_combo.setCurrentText(audio_devices.get("output_device", "Default Speaker"))
        
        # Load speech recognition
        recognition = config_data.get("speech_recognition", {})
        self.recognition_switch.setChecked(recognition.get("enabled", False))
        self.recognition_engine_combo.setCurrentText(recognition.get("engine", "Google Speech Recognition"))
        
        # Load TTS
        tts = config_data.get("text_to_speech", {})
        self.tts_switch.setChecked(tts.get("enabled", False))
        self.tts_engine_combo.setCurrentText(tts.get("engine", "System Default"))
        
        # Update configuration
        self.on_config_changed()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration data."""
        return self.config_data.copy()