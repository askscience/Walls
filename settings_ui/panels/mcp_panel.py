"""Modern MCP Panel with flat design and gui_core components."""

import sys
import os
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy
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
from gui_core.components.accordion.widgets import Accordion
from gui_core.components.checkbox.widgets import CheckBox


class MCPPanel(QWidget):
    """Modern MCP servers configuration panel."""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = {}
        self.server_widgets = {}
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
        
        # Overview card
        overview_card = self.create_overview_card()
        content_layout.addWidget(overview_card)
        
        # MCP Servers configuration
        servers_card = self.create_servers_card()
        content_layout.addWidget(servers_card)
        
        # Global settings card
        global_card = self.create_global_settings_card()
        content_layout.addWidget(global_card)
        
        # Actions card
        actions_card = self.create_actions_card()
        content_layout.addWidget(actions_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def create_overview_card(self):
        """Create overview information card."""
        card = Card("MCP Server Configuration", "Manage Model Context Protocol server connections")
        
        # Add status indicators
        status_layout = QHBoxLayout()
        
        # Active servers count
        self.active_count_label = QLabel("0 Active Servers")
        self.active_count_label.setObjectName("statusLabel")
        status_layout.addWidget(self.active_count_label)
        
        status_layout.addStretch()
        
        # Connection status
        self.connection_status = QLabel("● Disconnected")
        self.connection_status.setObjectName("connectionIndicator")
        status_layout.addWidget(self.connection_status)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        card.addWidget(status_widget)
        return card
    
    def create_servers_card(self):
        """Create servers configuration card with accordion."""
        card = Card("Server Configurations")
        
        # Create accordion for server configurations
        self.servers_accordion = Accordion()
        
        # Add default server configurations
        self.add_server_section("Browser MCP", "browser", {
            "command": "python",
            "args": ["server.py"],
            "cwd": "MCP/browser",
            "enabled": True,
            "auto_start": True
        })
        
        self.add_server_section("Word Editor MCP", "word_editor", {
            "command": "python",
            "args": ["server.py"],
            "cwd": "MCP/word_editor",
            "enabled": True,
            "auto_start": False
        })
        
        self.add_server_section("RAG MCP", "rag", {
            "command": "python",
            "args": ["server.py"],
            "cwd": "MCP/rag",
            "enabled": False,
            "auto_start": False
        })
        
        self.add_server_section("Radio Player MCP", "radio_player", {
            "command": "python",
            "args": ["server.py"],
            "cwd": "MCP/radio_player",
            "enabled": False,
            "auto_start": False
        })
        
        card.addWidget(self.servers_accordion)
        
        # Add new server button
        add_button = PrimaryButton("Add New Server")
        add_button.clicked.connect(self.add_new_server)
        card.addWidget(add_button)
        
        return card
    
    def add_server_section(self, title, server_id, config):
        """Add a server configuration section to the accordion."""
        section_widget = QWidget()
        layout = QVBoxLayout(section_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Server enabled switch
        enabled_layout = QHBoxLayout()
        enabled_switch = Switch("Enable Server")
        enabled_switch.setChecked(config.get("enabled", False))
        enabled_switch.toggled.connect(lambda checked: self.update_server_config(server_id, "enabled", checked))
        enabled_layout.addWidget(enabled_switch)
        enabled_layout.addStretch()
        layout.addLayout(enabled_layout)
        
        # Auto-start switch
        autostart_layout = QHBoxLayout()
        autostart_switch = Switch("Auto-start with application")
        autostart_switch.setChecked(config.get("auto_start", False))
        autostart_switch.toggled.connect(lambda checked: self.update_server_config(server_id, "auto_start", checked))
        autostart_layout.addWidget(autostart_switch)
        autostart_layout.addStretch()
        layout.addLayout(autostart_layout)
        
        # Command configuration
        cmd_label = QLabel("Command:")
        cmd_label.setObjectName("fieldLabel")
        layout.addWidget(cmd_label)
        
        command_edit = LineEdit(config.get("command", ""))
        command_edit.textChanged.connect(lambda text: self.update_server_config(server_id, "command", text))
        layout.addWidget(command_edit)
        
        # Arguments configuration
        args_label = QLabel("Arguments (one per line):")
        args_label.setObjectName("fieldLabel")
        layout.addWidget(args_label)
        
        args_edit = LineEdit(", ".join(config.get("args", [])))
        args_edit.textChanged.connect(lambda text: self.update_server_config(server_id, "args", text.split(", ") if text else []))
        layout.addWidget(args_edit)
        
        # Working directory
        cwd_label = QLabel("Working Directory:")
        cwd_label.setObjectName("fieldLabel")
        layout.addWidget(cwd_label)
        
        cwd_edit = LineEdit(config.get("cwd", ""))
        cwd_edit.textChanged.connect(lambda text: self.update_server_config(server_id, "cwd", text))
        layout.addWidget(cwd_edit)
        
        # Environment variables section
        env_label = QLabel("Environment Variables:")
        env_label.setObjectName("fieldLabel")
        layout.addWidget(env_label)
        
        env_frame = QFrame()
        env_frame.setObjectName("envFrame")
        env_layout = QVBoxLayout(env_frame)
        env_layout.setContentsMargins(8, 8, 8, 8)
        
        # Add environment variable inputs
        env_vars = config.get("env", {})
        for key, value in env_vars.items():
            env_row = QHBoxLayout()
            key_edit = LineEdit(key)
            key_edit.setPlaceholderText("Variable name")
            value_edit = LineEdit(str(value))
            value_edit.setPlaceholderText("Variable value")
            
            env_row.addWidget(key_edit)
            env_row.addWidget(QLabel("="))
            env_row.addWidget(value_edit)
            env_layout.addLayout(env_row)
        
        layout.addWidget(env_frame)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        test_button = PrimaryButton("Test Connection")
        test_button.clicked.connect(lambda: self.test_server_connection(server_id))
        button_layout.addWidget(test_button)
        
        restart_button = PrimaryButton("Restart Server")
        restart_button.clicked.connect(lambda: self.restart_server(server_id))
        button_layout.addWidget(restart_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Store widgets for later access
        self.server_widgets[server_id] = {
            "enabled": enabled_switch,
            "auto_start": autostart_switch,
            "command": command_edit,
            "args": args_edit,
            "cwd": cwd_edit
        }
        
        # Add to accordion
        self.servers_accordion.addSection(title, section_widget)
    
    def create_global_settings_card(self):
        """Create global MCP settings card."""
        card = Card("Global Settings", "Configuration that applies to all MCP servers")
        
        layout = QVBoxLayout()
        
        # Connection timeout
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Connection Timeout (seconds):")
        self.timeout_edit = LineEdit("30")
        self.timeout_edit.textChanged.connect(self.on_global_setting_changed)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_edit)
        layout.addLayout(timeout_layout)
        
        # Max retries
        retries_layout = QHBoxLayout()
        retries_label = QLabel("Max Connection Retries:")
        self.retries_edit = LineEdit("3")
        self.retries_edit.textChanged.connect(self.on_global_setting_changed)
        retries_layout.addWidget(retries_label)
        retries_layout.addWidget(self.retries_edit)
        layout.addLayout(retries_layout)
        
        # Debug mode
        debug_layout = QHBoxLayout()
        self.debug_switch = Switch("Enable Debug Logging")
        self.debug_switch.toggled.connect(self.on_global_setting_changed)
        debug_layout.addWidget(self.debug_switch)
        debug_layout.addStretch()
        layout.addLayout(debug_layout)
        
        settings_widget = QWidget()
        settings_widget.setLayout(layout)
        card.addWidget(settings_widget)
        return card
    
    def create_actions_card(self):
        """Create actions card with control buttons."""
        card = Card("Actions", "Control all MCP servers")
        
        button_layout = QHBoxLayout()
        
        start_all_button = PrimaryButton("Start All Servers")
        start_all_button.clicked.connect(self.start_all_servers)
        button_layout.addWidget(start_all_button)
        
        stop_all_button = PrimaryButton("Stop All Servers")
        stop_all_button.clicked.connect(self.stop_all_servers)
        button_layout.addWidget(stop_all_button)
        
        restart_all_button = PrimaryButton("Restart All Servers")
        restart_all_button.clicked.connect(self.restart_all_servers)
        button_layout.addWidget(restart_all_button)
        
        button_layout.addStretch()
        
        refresh_button = PrimaryButton("Refresh Status")
        refresh_button.clicked.connect(self.refresh_server_status)
        button_layout.addWidget(refresh_button)
        
        actions_widget = QWidget()
        actions_widget.setLayout(button_layout)
        card.addWidget(actions_widget)
        return card
    
    def update_server_config(self, server_id, key, value):
        """Update server configuration and emit change signal."""
        if server_id not in self.config_data:
            self.config_data[server_id] = {}
        
        self.config_data[server_id][key] = value
        self.config_changed.emit(self.config_data)
    
    def on_global_setting_changed(self):
        """Handle global setting changes."""
        global_settings = {
            "timeout": int(self.timeout_edit.text() or "30"),
            "max_retries": int(self.retries_edit.text() or "3"),
            "debug_mode": self.debug_switch.isChecked()
        }
        
        self.config_data["global"] = global_settings
        self.config_changed.emit(self.config_data)
    
    def add_new_server(self):
        """Add a new server configuration."""
        # This would open a dialog to configure a new server
        # For now, just add a placeholder
        server_id = f"custom_server_{len(self.server_widgets)}"
        self.add_server_section(f"Custom Server {len(self.server_widgets)}", server_id, {
            "command": "python",
            "args": ["server.py"],
            "cwd": "",
            "enabled": False,
            "auto_start": False
        })
    
    def test_server_connection(self, server_id):
        """Test connection to a specific server."""
        # Implement server connection testing
        pass
    
    def restart_server(self, server_id):
        """Restart a specific server."""
        # Implement server restart logic
        pass
    
    def start_all_servers(self):
        """Start all enabled servers."""
        # Implement start all logic
        pass
    
    def stop_all_servers(self):
        """Stop all running servers."""
        # Implement stop all logic
        pass
    
    def restart_all_servers(self):
        """Restart all servers."""
        # Implement restart all logic
        pass
    
    def refresh_server_status(self):
        """Refresh the status of all servers."""
        # Implement status refresh logic
        active_count = sum(1 for config in self.config_data.values() 
                          if isinstance(config, dict) and config.get("enabled", False))
        self.active_count_label.setText(f"{active_count} Active Servers")
    
    def load_config(self, config_data: Dict[str, Any]):
        """Load configuration data into the panel."""
        self.config_data = config_data.copy()
        
        # Update global settings
        global_settings = config_data.get("global", {})
        self.timeout_edit.setText(str(global_settings.get("timeout", 30)))
        self.retries_edit.setText(str(global_settings.get("max_retries", 3)))
        self.debug_switch.setChecked(global_settings.get("debug_mode", False))
        
        # Update server configurations
        for server_id, widgets in self.server_widgets.items():
            server_config = config_data.get(server_id, {})
            widgets["enabled"].setChecked(server_config.get("enabled", False))
            widgets["auto_start"].setChecked(server_config.get("auto_start", False))
            widgets["command"].setText(server_config.get("command", ""))
            widgets["args"].setText(", ".join(server_config.get("args", [])))
            widgets["cwd"].setText(server_config.get("cwd", ""))
        
        self.refresh_server_status()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration data."""
        return self.config_data.copy()