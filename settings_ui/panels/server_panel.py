"""Modern Server Panel with flat design and gui_core components."""

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
from gui_core.components.checkbox.widgets import CheckBox
from gui_core.components.combo_box.widgets import ComboBox
from gui_core.components.slider.widgets import Slider


class ServerPanel(QWidget):
    """Modern shared server configuration panel for APP_config.json."""
    
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
        
        # Server settings card
        server_card = self.create_server_settings_card()
        content_layout.addWidget(server_card)
        
        # Apps configuration card
        apps_card = self.create_apps_card()
        content_layout.addWidget(apps_card)
        
        # Logging settings card
        logging_card = self.create_logging_card()
        content_layout.addWidget(logging_card)
        
        # Security settings card
        security_card = self.create_security_card()
        content_layout.addWidget(security_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def create_server_settings_card(self):
        """Create server configuration card matching APP_config.json structure."""
        card = Card("Server Configuration", "Basic server settings from APP_config.json")
        
        server_layout = QGridLayout()
        server_layout.setSpacing(12)
        
        # Base port
        server_layout.addWidget(QLabel("Base Port:"), 0, 0)
        self.widgets['base_port'] = LineEdit()
        self.widgets['base_port'].setPlaceholderText("9000")
        server_layout.addWidget(self.widgets['base_port'], 0, 1)
        
        # Host
        server_layout.addWidget(QLabel("Host:"), 1, 0)
        self.widgets['host'] = LineEdit()
        self.widgets['host'].setPlaceholderText("localhost")
        server_layout.addWidget(self.widgets['host'], 1, 1)
        
        # Max apps
        server_layout.addWidget(QLabel("Max Apps:"), 2, 0)
        self.widgets['max_apps'] = LineEdit()
        self.widgets['max_apps'].setPlaceholderText("10")
        server_layout.addWidget(self.widgets['max_apps'], 2, 1)
        
        # Timeout
        server_layout.addWidget(QLabel("Timeout (seconds):"), 3, 0)
        self.widgets['timeout'] = LineEdit()
        self.widgets['timeout'].setPlaceholderText("600.0")
        server_layout.addWidget(self.widgets['timeout'], 3, 1)
        
        # Auto start MCP
        server_layout.addWidget(QLabel("Auto Start MCP:"), 4, 0)
        self.widgets['auto_start_mcp'] = Switch()
        self.widgets['auto_start_mcp'].toggled.connect(self.on_config_changed)
        server_layout.addWidget(self.widgets['auto_start_mcp'], 4, 1)
        
        server_widget = QWidget()
        server_widget.setLayout(server_layout)
        card.addWidget(server_widget)
        return card
    
    def create_apps_card(self):
        """Create apps configuration card matching APP_config.json structure."""
        card = Card("Apps Configuration", "Configure application settings from APP_config.json")
        
        apps_layout = QGridLayout()
        apps_layout.setSpacing(12)
        
        # Max apps
        apps_layout.addWidget(QLabel("Max Apps:"), 0, 0)
        self.widgets['max_apps'] = LineEdit()
        self.widgets['max_apps'].setPlaceholderText("10")
        self.widgets['max_apps'].textChanged.connect(self.on_config_changed)
        apps_layout.addWidget(self.widgets['max_apps'], 0, 1)
        
        # Default timeout
        apps_layout.addWidget(QLabel("Default Timeout (seconds):"), 1, 0)
        self.widgets['default_timeout'] = LineEdit()
        self.widgets['default_timeout'].setPlaceholderText("30")
        self.widgets['default_timeout'].textChanged.connect(self.on_config_changed)
        apps_layout.addWidget(self.widgets['default_timeout'], 1, 1)
        
        # Enable auto restart
        apps_layout.addWidget(QLabel("Enable Auto Restart:"), 2, 0)
        self.widgets['enable_auto_restart'] = Switch()
        self.widgets['enable_auto_restart'].toggled.connect(self.on_config_changed)
        apps_layout.addWidget(self.widgets['enable_auto_restart'], 2, 1)
        
        apps_widget = QWidget()
        apps_widget.setLayout(apps_layout)
        card.addWidget(apps_widget)
        return card
    
    def create_connection_card(self):
        """Create connection settings card."""
        card = Card("Connection Settings", "Configure server network and connection parameters")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Host and port settings
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host:"))
        self.host_edit = LineEdit("localhost")
        self.host_edit.textChanged.connect(self.on_config_changed)
        host_layout.addWidget(self.host_edit)
        
        host_layout.addWidget(QLabel("Port:"))
        self.port_edit = LineEdit("8000")
        self.port_edit.textChanged.connect(self.on_config_changed)
        host_layout.addWidget(self.port_edit)
        layout.addLayout(host_layout)
        
        # Auto-start setting
        autostart_layout = QHBoxLayout()
        self.autostart_switch = Switch("Auto-start server with application")
        self.autostart_switch.toggled.connect(self.on_config_changed)
        autostart_layout.addWidget(self.autostart_switch)
        autostart_layout.addStretch()
        layout.addLayout(autostart_layout)
        
        # CORS settings
        cors_layout = QHBoxLayout()
        self.cors_switch = Switch("Enable CORS (Cross-Origin Resource Sharing)")
        self.cors_switch.toggled.connect(self.on_config_changed)
        cors_layout.addWidget(self.cors_switch)
        cors_layout.addStretch()
        layout.addLayout(cors_layout)
        
        # Allowed origins
        origins_layout = QVBoxLayout()
        origins_layout.addWidget(QLabel("Allowed Origins (comma-separated):"))
        self.origins_edit = LineEdit("*")
        self.origins_edit.textChanged.connect(self.on_config_changed)
        origins_layout.addWidget(self.origins_edit)
        layout.addLayout(origins_layout)
        
        security_widget = QWidget()
        security_widget.setLayout(layout)
        card.addWidget(security_widget)
        return card
    
    def create_performance_card(self):
        """Create performance settings card."""
        card = Card("Performance Settings", "Configure server performance and resource limits")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Worker processes
        workers_layout = QHBoxLayout()
        workers_layout.addWidget(QLabel("Worker Processes:"))
        self.workers_slider = Slider()
        self.workers_slider.setMinimum(1)
        self.workers_slider.setMaximum(16)
        self.workers_slider.setValue(4)
        self.workers_slider.valueChanged.connect(self.on_config_changed)
        workers_layout.addWidget(self.workers_slider)
        self.workers_value_label = QLabel("4")
        workers_layout.addWidget(self.workers_value_label)
        layout.addLayout(workers_layout)
        
        # Max connections
        connections_layout = QHBoxLayout()
        connections_layout.addWidget(QLabel("Max Connections:"))
        self.max_connections_edit = LineEdit("100")
        self.max_connections_edit.textChanged.connect(self.on_config_changed)
        connections_layout.addWidget(self.max_connections_edit)
        layout.addLayout(connections_layout)
        
        # Request timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Request Timeout (seconds):"))
        self.timeout_edit = LineEdit("30")
        self.timeout_edit.textChanged.connect(self.on_config_changed)
        timeout_layout.addWidget(self.timeout_edit)
        layout.addLayout(timeout_layout)
        
        # Keep-alive timeout
        keepalive_layout = QHBoxLayout()
        keepalive_layout.addWidget(QLabel("Keep-Alive Timeout (seconds):"))
        self.keepalive_edit = LineEdit("5")
        self.keepalive_edit.textChanged.connect(self.on_config_changed)
        keepalive_layout.addWidget(self.keepalive_edit)
        layout.addLayout(keepalive_layout)
        
        # Enable compression
        compression_layout = QHBoxLayout()
        self.compression_switch = Switch("Enable Response Compression")
        self.compression_switch.toggled.connect(self.on_config_changed)
        compression_layout.addWidget(self.compression_switch)
        compression_layout.addStretch()
        layout.addLayout(compression_layout)
        
        connection_widget = QWidget()
        connection_widget.setLayout(layout)
        card.addWidget(connection_widget)
        return card
    
    def create_security_card(self):
        """Create security settings card."""
        card = Card("Security Settings", "Configure authentication and security features")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Enable authentication
        auth_layout = QHBoxLayout()
        self.auth_switch = Switch("Enable Authentication")
        self.auth_switch.toggled.connect(self.on_config_changed)
        auth_layout.addWidget(self.auth_switch)
        auth_layout.addStretch()
        layout.addLayout(auth_layout)
        
        # API key
        key_layout = QVBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_edit = LineEdit()
        self.api_key_edit.setEchoMode(LineEdit.EchoMode.Password)
        self.api_key_edit.textChanged.connect(self.on_config_changed)
        key_layout.addWidget(self.api_key_edit)
        layout.addLayout(key_layout)
        
        # Rate limiting
        rate_limit_layout = QHBoxLayout()
        self.rate_limit_switch = Switch("Enable Rate Limiting")
        self.rate_limit_switch.toggled.connect(self.on_config_changed)
        rate_limit_layout.addWidget(self.rate_limit_switch)
        rate_limit_layout.addStretch()
        layout.addLayout(rate_limit_layout)
        
        # Rate limit values
        rate_values_layout = QHBoxLayout()
        rate_values_layout.addWidget(QLabel("Requests per minute:"))
        self.rate_limit_edit = LineEdit("60")
        self.rate_limit_edit.textChanged.connect(self.on_config_changed)
        rate_values_layout.addWidget(self.rate_limit_edit)
        layout.addLayout(rate_values_layout)
        
        # SSL/TLS settings
        ssl_layout = QHBoxLayout()
        self.ssl_switch = Switch("Enable SSL/TLS")
        self.ssl_switch.toggled.connect(self.on_config_changed)
        ssl_layout.addWidget(self.ssl_switch)
        ssl_layout.addStretch()
        layout.addLayout(ssl_layout)
        
        performance_widget = QWidget()
        performance_widget.setLayout(layout)
        card.addWidget(performance_widget)
        return card
    
    def create_logging_card(self):
        """Create logging settings card."""
        card = Card("Logging Settings", "Configure server logging and monitoring")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Log level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Log Level:"))
        self.log_level_combo = ComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        self.log_level_combo.currentTextChanged.connect(self.on_config_changed)
        level_layout.addWidget(self.log_level_combo)
        level_layout.addStretch()
        layout.addLayout(level_layout)
        
        # Log file path
        file_layout = QVBoxLayout()
        file_layout.addWidget(QLabel("Log File Path:"))
        self.log_file_edit = LineEdit("logs/server.log")
        self.log_file_edit.textChanged.connect(self.on_config_changed)
        file_layout.addWidget(self.log_file_edit)
        layout.addLayout(file_layout)
        
        # Log rotation
        rotation_layout = QHBoxLayout()
        self.rotation_switch = Switch("Enable Log Rotation")
        self.rotation_switch.toggled.connect(self.on_config_changed)
        rotation_layout.addWidget(self.rotation_switch)
        rotation_layout.addStretch()
        layout.addLayout(rotation_layout)
        
        # Max log size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Max Log Size (MB):"))
        self.max_log_size_edit = LineEdit("10")
        self.max_log_size_edit.textChanged.connect(self.on_config_changed)
        size_layout.addWidget(self.max_log_size_edit)
        layout.addLayout(size_layout)
        
        logging_widget = QWidget()
        logging_widget.setLayout(layout)
        card.addWidget(logging_widget)
        return card
    
    def create_actions_card(self):
        """Create server control actions card."""
        card = Card("Server Control", "Start, stop, and manage the shared server")
        
        button_layout = QHBoxLayout()
        
        self.start_button = PrimaryButton("Start Server")
        self.start_button.clicked.connect(self.start_server)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = PrimaryButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_server)
        button_layout.addWidget(self.stop_button)
        
        self.restart_button = PrimaryButton("Restart Server")
        self.restart_button.clicked.connect(self.restart_server)
        button_layout.addWidget(self.restart_button)
        
        button_layout.addStretch()
        
        self.refresh_button = PrimaryButton("Refresh Status")
        self.refresh_button.clicked.connect(self.refresh_status)
        button_layout.addWidget(self.refresh_button)
        
        actions_widget = QWidget()
        actions_widget.setLayout(button_layout)
        card.addWidget(actions_widget)
        return card
    
    def on_config_changed(self):
        """Handle configuration changes and emit signal."""
        # Update workers value label
        if hasattr(self, 'workers_slider'):
            self.workers_value_label.setText(str(self.workers_slider.value()))
        
        # Collect all configuration data
        config = {
            "connection": {
                "host": self.host_edit.text(),
                "port": int(self.port_edit.text() or "8000"),
                "auto_start": self.autostart_switch.isChecked(),
                "cors_enabled": self.cors_switch.isChecked(),
                "allowed_origins": [origin.strip() for origin in self.origins_edit.text().split(",") if origin.strip()]
            },
            "performance": {
                "workers": self.workers_slider.value(),
                "max_connections": int(self.max_connections_edit.text() or "100"),
                "request_timeout": int(self.timeout_edit.text() or "30"),
                "keepalive_timeout": int(self.keepalive_edit.text() or "5"),
                "compression_enabled": self.compression_switch.isChecked()
            },
            "security": {
                "auth_enabled": self.auth_switch.isChecked(),
                "api_key": self.api_key_edit.text(),
                "rate_limit_enabled": self.rate_limit_switch.isChecked(),
                "rate_limit_per_minute": int(self.rate_limit_edit.text() or "60"),
                "ssl_enabled": self.ssl_switch.isChecked()
            },
            "logging": {
                "level": self.log_level_combo.currentText(),
                "file_path": self.log_file_edit.text(),
                "rotation_enabled": self.rotation_switch.isChecked(),
                "max_size_mb": int(self.max_log_size_edit.text() or "10")
            }
        }
        
        self.config_data = config
        self.config_changed.emit(config)
    
    def start_server(self):
        """Start the shared server."""
        # Implement server start logic
        self.status_indicator.setText("● Starting...")
        # This would typically call the actual server start method
        pass
    
    def stop_server(self):
        """Stop the shared server."""
        # Implement server stop logic
        self.status_indicator.setText("● Stopped")
        self.uptime_label.setText("Not running")
        self.connections_label.setText("0")
        pass
    
    def restart_server(self):
        """Restart the shared server."""
        # Implement server restart logic
        self.stop_server()
        self.start_server()
        pass
    
    def refresh_status(self):
        """Refresh server status information."""
        # Implement status refresh logic
        # This would query the actual server for current status
        pass
    
    def load_config(self, config_data: Dict[str, Any]):
        """Load configuration data into the panel."""
        self.config_data = config_data.copy()
        
        # Load connection settings
        connection = config_data.get("connection", {})
        self.host_edit.setText(connection.get("host", "localhost"))
        self.port_edit.setText(str(connection.get("port", 8000)))
        self.autostart_switch.setChecked(connection.get("auto_start", False))
        self.cors_switch.setChecked(connection.get("cors_enabled", False))
        self.origins_edit.setText(", ".join(connection.get("allowed_origins", ["*"])))
        
        # Load performance settings
        performance = config_data.get("performance", {})
        self.workers_slider.setValue(performance.get("workers", 4))
        self.workers_value_label.setText(str(performance.get("workers", 4)))
        self.max_connections_edit.setText(str(performance.get("max_connections", 100)))
        self.timeout_edit.setText(str(performance.get("request_timeout", 30)))
        self.keepalive_edit.setText(str(performance.get("keepalive_timeout", 5)))
        self.compression_switch.setChecked(performance.get("compression_enabled", False))
        
        # Load security settings
        security = config_data.get("security", {})
        self.auth_switch.setChecked(security.get("auth_enabled", False))
        self.api_key_edit.setText(security.get("api_key", ""))
        self.rate_limit_switch.setChecked(security.get("rate_limit_enabled", False))
        self.rate_limit_edit.setText(str(security.get("rate_limit_per_minute", 60)))
        self.ssl_switch.setChecked(security.get("ssl_enabled", False))
        
        # Load logging settings
        logging = config_data.get("logging", {})
        self.log_level_combo.setCurrentText(logging.get("level", "INFO"))
        self.log_file_edit.setText(logging.get("file_path", "logs/server.log"))
        self.rotation_switch.setChecked(logging.get("rotation_enabled", False))
        self.max_log_size_edit.setText(str(logging.get("max_size_mb", 10)))
        
        # Update address label
        host = connection.get("host", "localhost")
        port = connection.get("port", 8000)
        self.address_label.setText(f"{host}:{port}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration data."""
        return self.config_data.copy()