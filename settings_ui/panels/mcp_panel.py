"""Modern MCP Panel with flat design and gui_core components."""

import sys
import os
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy, QGroupBox
)
from PySide6.QtCore import Signal, Qt
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


class MCPPanel(QWidget):
    """Modern MCP server configuration panel for MCP_config.json."""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = {}
        self.widgets = {}
        self.setup_ui()
    
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
        
        # MCP Servers card
        servers_card = self.create_servers_card()
        content_layout.addWidget(servers_card)
        
        # Logging settings card
        logging_card = self.create_logging_card()
        content_layout.addWidget(logging_card)
        
        # Monitoring settings card
        monitoring_card = self.create_monitoring_card()
        content_layout.addWidget(monitoring_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def create_servers_card(self):
        """Create MCP servers configuration card matching MCP_config.json structure."""
        card = Card("MCP Servers Configuration", "Configure individual MCP servers")
        
        servers_layout = QVBoxLayout()
        servers_layout.setSpacing(16)
        
        # Word Editor Server
        word_frame = QFrame()
        word_frame.setFrameStyle(QFrame.Shape.Box)
        word_layout = QGridLayout(word_frame)
        
        word_layout.addWidget(QLabel("Word Editor MCP Server"), 0, 0, 1, 2)
        
        word_layout.addWidget(QLabel("Port:"), 1, 0)
        self.widgets['word_port'] = LineEdit()
        self.widgets['word_port'].setPlaceholderText("8888")
        self.widgets['word_port'].textChanged.connect(self.on_config_changed)
        word_layout.addWidget(self.widgets['word_port'], 1, 1)
        
        word_layout.addWidget(QLabel("Enabled:"), 2, 0)
        self.widgets['word_enabled'] = Switch()
        self.widgets['word_enabled'].toggled.connect(self.on_config_changed)
        word_layout.addWidget(self.widgets['word_enabled'], 2, 1)
        
        word_layout.addWidget(QLabel("Auto Start:"), 3, 0)
        self.widgets['word_auto_start'] = Switch()
        self.widgets['word_auto_start'].toggled.connect(self.on_config_changed)
        word_layout.addWidget(self.widgets['word_auto_start'], 3, 1)
        
        word_layout.addWidget(QLabel("Restart on Failure:"), 4, 0)
        self.widgets['word_restart_on_failure'] = Switch()
        self.widgets['word_restart_on_failure'].toggled.connect(self.on_config_changed)
        word_layout.addWidget(self.widgets['word_restart_on_failure'], 4, 1)
        
        word_layout.addWidget(QLabel("Max Restart Attempts:"), 5, 0)
        self.widgets['word_max_restart'] = LineEdit()
        self.widgets['word_max_restart'].setPlaceholderText("3")
        self.widgets['word_max_restart'].textChanged.connect(self.on_config_changed)
        word_layout.addWidget(self.widgets['word_max_restart'], 5, 1)
        
        servers_layout.addWidget(word_frame)
        
        # Browser Server
        browser_frame = QFrame()
        browser_frame.setFrameStyle(QFrame.Shape.Box)
        browser_layout = QGridLayout(browser_frame)
        
        browser_layout.addWidget(QLabel("Browser MCP Server"), 0, 0, 1, 2)
        
        browser_layout.addWidget(QLabel("Port:"), 1, 0)
        self.widgets['browser_port'] = LineEdit()
        self.widgets['browser_port'].setPlaceholderText("8889")
        self.widgets['browser_port'].textChanged.connect(self.on_config_changed)
        browser_layout.addWidget(self.widgets['browser_port'], 1, 1)
        
        browser_layout.addWidget(QLabel("Enabled:"), 2, 0)
        self.widgets['browser_enabled'] = Switch()
        self.widgets['browser_enabled'].toggled.connect(self.on_config_changed)
        browser_layout.addWidget(self.widgets['browser_enabled'], 2, 1)
        
        browser_layout.addWidget(QLabel("Auto Start:"), 3, 0)
        self.widgets['browser_auto_start'] = Switch()
        self.widgets['browser_auto_start'].toggled.connect(self.on_config_changed)
        browser_layout.addWidget(self.widgets['browser_auto_start'], 3, 1)
        
        browser_layout.addWidget(QLabel("Restart on Failure:"), 4, 0)
        self.widgets['browser_restart_on_failure'] = Switch()
        self.widgets['browser_restart_on_failure'].toggled.connect(self.on_config_changed)
        browser_layout.addWidget(self.widgets['browser_restart_on_failure'], 4, 1)
        
        browser_layout.addWidget(QLabel("Max Restart Attempts:"), 5, 0)
        self.widgets['browser_max_restart'] = LineEdit()
        self.widgets['browser_max_restart'].setPlaceholderText("3")
        self.widgets['browser_max_restart'].textChanged.connect(self.on_config_changed)
        browser_layout.addWidget(self.widgets['browser_max_restart'], 5, 1)
        
        servers_layout.addWidget(browser_frame)
        
        # Radio Player Server
        radio_frame = QFrame()
        radio_frame.setFrameStyle(QFrame.Shape.Box)
        radio_layout = QGridLayout(radio_frame)
        
        radio_layout.addWidget(QLabel("Radio Player MCP Server"), 0, 0, 1, 2)
        
        radio_layout.addWidget(QLabel("Port:"), 1, 0)
        self.widgets['radio_port'] = LineEdit()
        self.widgets['radio_port'].setPlaceholderText("8890")
        self.widgets['radio_port'].textChanged.connect(self.on_config_changed)
        radio_layout.addWidget(self.widgets['radio_port'], 1, 1)
        
        radio_layout.addWidget(QLabel("Enabled:"), 2, 0)
        self.widgets['radio_enabled'] = Switch()
        self.widgets['radio_enabled'].toggled.connect(self.on_config_changed)
        radio_layout.addWidget(self.widgets['radio_enabled'], 2, 1)
        
        radio_layout.addWidget(QLabel("Auto Start:"), 3, 0)
        self.widgets['radio_auto_start'] = Switch()
        self.widgets['radio_auto_start'].toggled.connect(self.on_config_changed)
        radio_layout.addWidget(self.widgets['radio_auto_start'], 3, 1)
        
        radio_layout.addWidget(QLabel("Restart on Failure:"), 4, 0)
        self.widgets['radio_restart_on_failure'] = Switch()
        self.widgets['radio_restart_on_failure'].toggled.connect(self.on_config_changed)
        radio_layout.addWidget(self.widgets['radio_restart_on_failure'], 4, 1)
        
        radio_layout.addWidget(QLabel("Max Restart Attempts:"), 5, 0)
        self.widgets['radio_max_restart'] = LineEdit()
        self.widgets['radio_max_restart'].setPlaceholderText("3")
        self.widgets['radio_max_restart'].textChanged.connect(self.on_config_changed)
        radio_layout.addWidget(self.widgets['radio_max_restart'], 5, 1)
        
        servers_layout.addWidget(radio_frame)
        
        # RAG Server
        rag_frame = QFrame()
        rag_frame.setFrameStyle(QFrame.Shape.Box)
        rag_layout = QGridLayout(rag_frame)
        
        rag_layout.addWidget(QLabel("RAG MCP Server"), 0, 0, 1, 2)
        
        rag_layout.addWidget(QLabel("Port:"), 1, 0)
        self.widgets['rag_port'] = LineEdit()
        self.widgets['rag_port'].setPlaceholderText("8891")
        self.widgets['rag_port'].textChanged.connect(self.on_config_changed)
        rag_layout.addWidget(self.widgets['rag_port'], 1, 1)
        
        rag_layout.addWidget(QLabel("Enabled:"), 2, 0)
        self.widgets['rag_enabled'] = Switch()
        self.widgets['rag_enabled'].toggled.connect(self.on_config_changed)
        rag_layout.addWidget(self.widgets['rag_enabled'], 2, 1)
        
        rag_layout.addWidget(QLabel("Auto Start:"), 3, 0)
        self.widgets['rag_auto_start'] = Switch()
        self.widgets['rag_auto_start'].toggled.connect(self.on_config_changed)
        rag_layout.addWidget(self.widgets['rag_auto_start'], 3, 1)
        
        rag_layout.addWidget(QLabel("Restart on Failure:"), 4, 0)
        self.widgets['rag_restart_on_failure'] = Switch()
        self.widgets['rag_restart_on_failure'].toggled.connect(self.on_config_changed)
        rag_layout.addWidget(self.widgets['rag_restart_on_failure'], 4, 1)
        
        rag_layout.addWidget(QLabel("Max Restart Attempts:"), 5, 0)
        self.widgets['rag_max_restart'] = LineEdit()
        self.widgets['rag_max_restart'].setPlaceholderText("3")
        self.widgets['rag_max_restart'].textChanged.connect(self.on_config_changed)
        rag_layout.addWidget(self.widgets['rag_max_restart'], 5, 1)
        
        servers_layout.addWidget(rag_frame)
        
        servers_widget = QWidget()
        servers_widget.setLayout(servers_layout)
        card.addWidget(servers_widget)
        return card
    
    def create_logging_card(self):
        """Create logging settings card matching MCP_config.json structure."""
        card = Card("Logging Configuration", "Configure MCP servers logging settings")
        
        logging_layout = QGridLayout()
        logging_layout.setSpacing(12)
        
        # Log level
        logging_layout.addWidget(QLabel("Log Level:"), 0, 0)
        self.widgets['log_level'] = ComboBox()
        self.widgets['log_level'].addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.widgets['log_level'].currentTextChanged.connect(self.on_config_changed)
        logging_layout.addWidget(self.widgets['log_level'], 0, 1)
        
        # Log file
        logging_layout.addWidget(QLabel("Log File:"), 1, 0)
        self.widgets['log_file'] = LineEdit()
        self.widgets['log_file'].setPlaceholderText("./logs/mcp_servers.log")
        self.widgets['log_file'].textChanged.connect(self.on_config_changed)
        logging_layout.addWidget(self.widgets['log_file'], 1, 1)
        
        # Max file size
        logging_layout.addWidget(QLabel("Max File Size:"), 2, 0)
        self.widgets['max_file_size'] = LineEdit()
        self.widgets['max_file_size'].setPlaceholderText("10MB")
        self.widgets['max_file_size'].textChanged.connect(self.on_config_changed)
        logging_layout.addWidget(self.widgets['max_file_size'], 2, 1)
        
        # Backup count
        logging_layout.addWidget(QLabel("Backup Count:"), 3, 0)
        self.widgets['backup_count'] = LineEdit()
        self.widgets['backup_count'].setPlaceholderText("5")
        self.widgets['backup_count'].textChanged.connect(self.on_config_changed)
        logging_layout.addWidget(self.widgets['backup_count'], 3, 1)
        
        # Console output
        logging_layout.addWidget(QLabel("Console Output:"), 4, 0)
        self.widgets['console_output'] = Switch()
        self.widgets['console_output'].toggled.connect(self.on_config_changed)
        logging_layout.addWidget(self.widgets['console_output'], 4, 1)
        
        logging_widget = QWidget()
        logging_widget.setLayout(logging_layout)
        card.addWidget(logging_widget)
        return card
    
    def create_monitoring_card(self):
        """Create monitoring settings card matching MCP_config.json structure."""
        card = Card("Monitoring Configuration", "Configure MCP servers monitoring settings")
        
        monitoring_layout = QGridLayout()
        monitoring_layout.setSpacing(12)
        
        # Health check interval
        monitoring_layout.addWidget(QLabel("Health Check Interval (seconds):"), 0, 0)
        self.widgets['health_check_interval'] = LineEdit()
        self.widgets['health_check_interval'].setPlaceholderText("30")
        self.widgets['health_check_interval'].textChanged.connect(self.on_config_changed)
        monitoring_layout.addWidget(self.widgets['health_check_interval'], 0, 1)
        
        # Enable metrics
        monitoring_layout.addWidget(QLabel("Enable Metrics:"), 1, 0)
        self.widgets['enable_metrics'] = Switch()
        self.widgets['enable_metrics'].toggled.connect(self.on_config_changed)
        monitoring_layout.addWidget(self.widgets['enable_metrics'], 1, 1)
        
        # Metrics port
        monitoring_layout.addWidget(QLabel("Metrics Port:"), 2, 0)
        self.widgets['metrics_port'] = LineEdit()
        self.widgets['metrics_port'].setPlaceholderText("9001")
        self.widgets['metrics_port'].textChanged.connect(self.on_config_changed)
        monitoring_layout.addWidget(self.widgets['metrics_port'], 2, 1)
        
        monitoring_widget = QWidget()
        monitoring_widget.setLayout(monitoring_layout)
        card.addWidget(monitoring_widget)
        return card
    
    def on_config_changed(self):
        """Handle configuration changes and emit signal."""
        # Collect all configuration data matching MCP_config.json structure
        config = {
            "mcp_servers": {
                "word_editor": {
                    "name": "Word Editor MCP Server",
                    "description": "MCP server for controlling the word editor application",
                    "path": "./MCP/word_editor/server.py",
                    "port": int(self.widgets['word_port'].text() or "8888"),
                    "enabled": self.widgets['word_enabled'].isChecked(),
                    "auto_start": self.widgets['word_auto_start'].isChecked(),
                    "capabilities": ["text_operations", "file_operations", "cli_commands"],
                    "tools": ["set_text", "insert_text", "append_text", "get_text", "open_file", "save_file", "get_file_info", "send_cli_command", "check_gui_status", "get_available_commands"],
                    "restart_on_failure": self.widgets['word_restart_on_failure'].isChecked(),
                    "max_restart_attempts": int(self.widgets['word_max_restart'].text() or "3")
                },
                "browser": {
                    "name": "Browser MCP Server",
                    "description": "MCP server for controlling the browser application",
                    "path": "./MCP/browser/server.py",
                    "port": int(self.widgets['browser_port'].text() or "8889"),
                    "enabled": self.widgets['browser_enabled'].isChecked(),
                    "auto_start": self.widgets['browser_auto_start'].isChecked(),
                    "capabilities": ["navigation", "bookmarks", "page_interaction", "adblock_control"],
                    "tools": ["open_url", "navigate_back", "navigate_forward", "reload_page", "add_bookmark", "get_bookmarks", "click_element", "click_text", "get_page_html", "summarize_page", "adblock_enable", "adblock_disable", "adblock_toggle", "adblock_load_rules"],
                    "restart_on_failure": self.widgets['browser_restart_on_failure'].isChecked(),
                    "max_restart_attempts": int(self.widgets['browser_max_restart'].text() or "3")
                },
                "radio_player": {
                    "name": "Radio Player MCP Server",
                    "description": "MCP server for controlling the radio player application",
                    "path": "./MCP/radio_player/server.py",
                    "port": int(self.widgets['radio_port'].text() or "8890"),
                    "enabled": self.widgets['radio_enabled'].isChecked(),
                    "auto_start": self.widgets['radio_auto_start'].isChecked(),
                    "capabilities": ["playback_control", "search", "station_management", "volume_control"],
                    "tools": ["play_station", "stop_playback", "pause_playback", "resume_playback", "search_stations", "get_current_station", "get_favorites", "add_favorite", "remove_favorite", "set_volume", "get_volume", "get_playback_status"],
                    "restart_on_failure": self.widgets['radio_restart_on_failure'].isChecked(),
                    "max_restart_attempts": int(self.widgets['radio_max_restart'].text() or "3")
                },
                "rag": {
                    "name": "RAG MCP Server",
                    "description": "MCP server for controlling the RAG (Retrieval-Augmented Generation) application",
                    "path": "./MCP/rag/server.py",
                    "port": int(self.widgets['rag_port'].text() or "8891"),
                    "enabled": self.widgets['rag_enabled'].isChecked(),
                    "auto_start": self.widgets['rag_auto_start'].isChecked(),
                    "capabilities": ["document_indexing", "query_processing", "file_watching", "document_management"],
                    "tools": ["rag_index_all", "rag_add_document", "rag_delete_document", "rag_query", "rag_interactive_query", "rag_start_watching", "rag_stop_watching", "rag_health_check", "rag_get_status"],
                    "restart_on_failure": self.widgets['rag_restart_on_failure'].isChecked(),
                    "max_restart_attempts": int(self.widgets['rag_max_restart'].text() or "3")
                }
            },
            "logging": {
                "level": self.widgets['log_level'].currentText(),
                "file": self.widgets['log_file'].text() or "./logs/mcp_servers.log",
                "max_file_size": self.widgets['max_file_size'].text() or "10MB",
                "backup_count": int(self.widgets['backup_count'].text() or "5"),
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "console_output": self.widgets['console_output'].isChecked()
            },
            "monitoring": {
                "health_check_interval": int(self.widgets['health_check_interval'].text() or "30"),
                "enable_metrics": self.widgets['enable_metrics'].isChecked(),
                "metrics_port": int(self.widgets['metrics_port'].text() or "9001")
            }
        }
        
        self.config_data = config
        self.config_changed.emit(config)
    
    def load_config(self, config_data: Dict[str, Any]):
        """Load configuration data into the panel."""
        self.config_data = config_data.copy()
        
        # Load MCP servers settings
        mcp_servers = config_data.get("mcp_servers", {})
        
        # Word Editor
        word = mcp_servers.get("word_editor", {})
        self.widgets['word_port'].setText(str(word.get("port", 8888)))
        self.widgets['word_enabled'].setChecked(word.get("enabled", True))
        self.widgets['word_auto_start'].setChecked(word.get("auto_start", True))
        self.widgets['word_restart_on_failure'].setChecked(word.get("restart_on_failure", True))
        self.widgets['word_max_restart'].setText(str(word.get("max_restart_attempts", 3)))
        
        # Browser
        browser = mcp_servers.get("browser", {})
        self.widgets['browser_port'].setText(str(browser.get("port", 8889)))
        self.widgets['browser_enabled'].setChecked(browser.get("enabled", True))
        self.widgets['browser_auto_start'].setChecked(browser.get("auto_start", True))
        self.widgets['browser_restart_on_failure'].setChecked(browser.get("restart_on_failure", True))
        self.widgets['browser_max_restart'].setText(str(browser.get("max_restart_attempts", 3)))
        
        # Radio Player
        radio = mcp_servers.get("radio_player", {})
        self.widgets['radio_port'].setText(str(radio.get("port", 8890)))
        self.widgets['radio_enabled'].setChecked(radio.get("enabled", True))
        self.widgets['radio_auto_start'].setChecked(radio.get("auto_start", True))
        self.widgets['radio_restart_on_failure'].setChecked(radio.get("restart_on_failure", True))
        self.widgets['radio_max_restart'].setText(str(radio.get("max_restart_attempts", 3)))
        
        # RAG
        rag = mcp_servers.get("rag", {})
        self.widgets['rag_port'].setText(str(rag.get("port", 8891)))
        self.widgets['rag_enabled'].setChecked(rag.get("enabled", True))
        self.widgets['rag_auto_start'].setChecked(rag.get("auto_start", True))
        self.widgets['rag_restart_on_failure'].setChecked(rag.get("restart_on_failure", True))
        self.widgets['rag_max_restart'].setText(str(rag.get("max_restart_attempts", 3)))
        
        # Load logging settings
        logging = config_data.get("logging", {})
        self.widgets['log_level'].setCurrentText(logging.get("level", "INFO"))
        self.widgets['log_file'].setText(logging.get("file", "./logs/mcp_servers.log"))
        self.widgets['max_file_size'].setText(logging.get("max_file_size", "10MB"))
        self.widgets['backup_count'].setText(str(logging.get("backup_count", 5)))
        self.widgets['console_output'].setChecked(logging.get("console_output", True))
        
        # Load monitoring settings
        monitoring = config_data.get("monitoring", {})
        self.widgets['health_check_interval'].setText(str(monitoring.get("health_check_interval", 30)))
        self.widgets['enable_metrics'].setChecked(monitoring.get("enable_metrics", False))
        self.widgets['metrics_port'].setText(str(monitoring.get("metrics_port", 9001)))