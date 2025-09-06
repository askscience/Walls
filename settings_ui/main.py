#!/usr/bin/env python3
"""Modern Settings UI Application - Entry Point."""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

# Import gui_core theme
from gui_core.apply_theme import apply_theme
from settings_ui.settings_window import SettingsWindow


def setup_application(app):
    """Setup modern application styling and metadata."""
    # Set application metadata
    app.setApplicationName("Walls Settings")
    app.setApplicationDisplayName("Walls Configuration Manager")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Walls Project")
    app.setOrganizationDomain("walls.ai")
    
    # Enable high DPI support
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Set modern system font
    font = QFont("Inter", 13)
    if not font.exactMatch():
        font = QFont("SF Pro Display", 13)  # macOS
    if not font.exactMatch():
        font = QFont("Segoe UI", 13)  # Windows
    if not font.exactMatch():
        font = QFont("Ubuntu", 13)  # Linux
    
    app.setFont(font)
    
    # Apply gui_core theme
    apply_theme(app)
    
    # Set application icon if available
    icon_path = parent_dir / "gui_core" / "utils" / "icons" / "gear.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))


def main():
    """Main application entry point."""
    # Create QApplication with modern styling
    app = QApplication(sys.argv)
    
    # Setup application
    setup_application(app)
    
    try:
        # Create and show the main settings window
        window = SettingsWindow()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error starting Settings UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()