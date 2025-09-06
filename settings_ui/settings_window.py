"""Modern Settings Window with flat design and gui_core components."""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStatusBar,
    QSplitter, QListWidget, QListWidgetItem, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

# Import gui_core components
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from gui_core.components.cards.widgets import Card
from gui_core.components.tab_widget.widgets import TabWidget
from gui_core.components.button.widgets import PrimaryButton
from gui_core.components.toolbar.widgets import ToolBar

# Import panels
from settings_ui.panels.server_panel import ServerPanel
from settings_ui.panels.mcp_panel import MCPPanel
from settings_ui.panels.rag_panel import RAGPanel
from settings_ui.panels.voice_panel import VoicePanel

# Import services
from settings_ui.services.config_manager import ConfigManager


class SettingsWindow(QMainWindow):
    """Modern flat settings window with sidebar navigation."""
    
    config_changed = Signal(str, dict)  # panel_name, config_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        
        # Status timer for temporary messages
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_status)
        
        self.setup_ui()
        self.setup_connections()
        self.load_configurations()
    
    def setup_ui(self):
        """Setup the modern flat user interface."""
        self.setWindowTitle("Settings - Walls Configuration Manager")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set window icon
        icon_path = Path(__file__).parent.parent / "gui_core" / "utils" / "icons" / "gear.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Create central widget with modern layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        main_layout.addWidget(splitter)
        
        # Left sidebar with navigation
        self.sidebar = self.create_sidebar()
        splitter.addWidget(self.sidebar)
        
        # Right content area
        self.content_area = self.create_content_area()
        splitter.addWidget(self.content_area)
        
        # Set splitter proportions (sidebar:content = 1:3)
        splitter.setSizes([300, 900])
        
        # Create status bar
        self.setup_status_bar()
    
    def create_sidebar(self):
        """Create modern sidebar with navigation cards."""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(320)
        sidebar.setMinimumWidth(280)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header card
        header_card = Card("Configuration Manager", "Manage all Walls settings")
        header_card.setObjectName("headerCard")
        layout.addWidget(header_card)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self.nav_list.setFrameStyle(0)
        self.nav_list.setSpacing(4)
        
        # Add navigation items with icons
        nav_items = [
            ("Server Configuration", "server.svg", "Configure shared server settings"),
            ("MCP Servers", "plug.svg", "Manage MCP server connections"),
            ("RAG System", "search.svg", "Configure retrieval and indexing"),
            ("Voice Interface", "radio.svg", "Setup voice interaction settings")
        ]
        
        for title, icon_name, description in nav_items:
            item = QListWidgetItem()
            item.setText(title)
            item.setData(Qt.ItemDataRole.UserRole, description)
            
            # Set icon if available
            icon_path = Path(__file__).parent.parent / "gui_core" / "utils" / "icons" / icon_name
            if icon_path.exists():
                item.setIcon(QIcon(str(icon_path)))
            
            item.setSizeHint(QSize(260, 48))
            self.nav_list.addItem(item)
        
        layout.addWidget(self.nav_list)
        layout.addStretch()
        
        # Footer with version info
        version_label = QLabel("Walls Settings v2.0")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        return sidebar
    
    def create_content_area(self):
        """Create the main content area with stacked panels."""
        content = QWidget()
        content.setObjectName("contentArea")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Content header
        self.content_header = QLabel("Server Configuration")
        self.content_header.setObjectName("contentHeader")
        layout.addWidget(self.content_header)
        
        self.content_description = QLabel("Configure shared server settings and connections")
        self.content_description.setObjectName("contentDescription")
        layout.addWidget(self.content_description)
        
        # Stacked widget for panels
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")
        
        # Create and add panels
        self.server_panel = ServerPanel()
        self.mcp_panel = MCPPanel()
        self.rag_panel = RAGPanel()
        self.voice_panel = VoicePanel()
        
        self.stacked_widget.addWidget(self.server_panel)
        self.stacked_widget.addWidget(self.mcp_panel)
        self.stacked_widget.addWidget(self.rag_panel)
        self.stacked_widget.addWidget(self.voice_panel)
        
        layout.addWidget(self.stacked_widget)
        
        return content
    
    def setup_status_bar(self):
        """Setup modern status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("modernStatusBar")
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Connection status indicator
        self.connection_status = QLabel("● Connected")
        self.connection_status.setObjectName("connectionStatus")
        self.status_bar.addPermanentWidget(self.connection_status)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Navigation
        self.nav_list.currentRowChanged.connect(self.on_navigation_changed)
        
        # Panel configuration changes
        self.server_panel.config_changed.connect(
            lambda config: self.config_changed.emit("server", config)
        )
        self.mcp_panel.config_changed.connect(
            lambda config: self.config_changed.emit("mcp", config)
        )
        self.rag_panel.config_changed.connect(
            lambda config: self.config_changed.emit("rag", config)
        )
        self.voice_panel.config_changed.connect(
            lambda config: self.config_changed.emit("voice", config)
        )
        
        # Configuration changes
        self.config_changed.connect(self.on_config_changed)
    
    def on_navigation_changed(self, index):
        """Handle navigation selection changes."""
        if index < 0:
            return
        
        # Update content area
        self.stacked_widget.setCurrentIndex(index)
        
        # Update header based on selection
        headers = [
            ("Server Configuration", "Configure shared server settings and connections"),
            ("MCP Servers", "Manage Model Context Protocol server connections"),
            ("RAG System", "Configure retrieval-augmented generation and indexing"),
            ("Voice Interface", "Setup voice interaction and speech settings")
        ]
        
        if index < len(headers):
            title, description = headers[index]
            self.content_header.setText(title)
            self.content_description.setText(description)
    
    def load_configurations(self):
        """Load all configuration data into panels."""
        try:
            # Load configurations for each panel
            server_config = self.config_manager.load_config("server")
            if server_config:
                self.server_panel.load_config(server_config)
            
            mcp_config = self.config_manager.load_config("mcp")
            if mcp_config:
                self.mcp_panel.load_config(mcp_config)
            
            rag_config = self.config_manager.load_config("rag")
            if rag_config:
                self.rag_panel.load_config(rag_config)
            
            voice_config = self.config_manager.load_config("voice")
            if voice_config:
                self.voice_panel.load_config(voice_config)
            
            self.show_status("Configurations loaded successfully", 3000)
            
        except Exception as e:
            self.show_status(f"Error loading configurations: {str(e)}", 5000)
    
    def on_config_changed(self, panel_name, config_data):
        """Handle configuration changes from panels."""
        try:
            self.config_manager.save_config(panel_name, config_data)
            self.show_status(f"{panel_name.title()} configuration saved", 2000)
            
        except Exception as e:
            self.show_status(f"Error saving {panel_name} config: {str(e)}", 5000)
    
    def show_status(self, message, timeout=0):
        """Show status message with optional timeout."""
        self.status_label.setText(message)
        
        if timeout > 0:
            self.status_timer.start(timeout)
    
    def clear_status(self):
        """Clear status message."""
        self.status_label.setText("Ready")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save any pending changes
        try:
            # Ensure all configurations are saved
            self.show_status("Saving configurations...", 1000)
            event.accept()
            
        except Exception as e:
            self.show_status(f"Error during shutdown: {str(e)}", 3000)
            event.accept()