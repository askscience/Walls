#!/usr/bin/env python3
"""
Modern Radio Player GUI with glass morphism design
Refactored version that imports from modular components
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QPalette
from PySide6.QtCore import Qt

# Import the main window class
from .main_window import ModernRadioPlayer


def main():
    """Main entry point for the radio player application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Radio Player")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Radio Player")
    
    # Set the application style
    app.setStyle('Fusion')
    
    # Load custom fonts if available
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    if os.path.exists(font_dir):
        for font_file in os.listdir(font_dir):
            if font_file.endswith(('.ttf', '.otf')):
                font_path = os.path.join(font_dir, font_file)
                QFontDatabase.addApplicationFont(font_path)
    
    # Detect system theme (dark/light mode)
    is_dark_theme = is_system_dark_theme(app)
    
    # Load and apply the theme stylesheet with appropriate colors
    theme_path = os.path.join(os.path.dirname(__file__), 'theme.qss')
    if os.path.exists(theme_path):
        with open(theme_path, 'r', encoding='utf-8') as f:
            theme_content = f.read()
            # Apply theme-specific colors
            theme_content = apply_theme_colors(theme_content, is_dark_theme)
            app.setStyleSheet(theme_content)
    
    # Create and show the main window
    window = ModernRadioPlayer()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


def is_system_dark_theme(app):
    """Detect if the system is using dark theme."""
    palette = app.palette()
    window_color = palette.color(QPalette.Window)
    # If the window background is darker, it's likely a dark theme
    return window_color.lightness() < 128


def apply_theme_colors(theme_content, is_dark):
    """Apply dark or light theme colors to the stylesheet."""
    if is_dark:
        # Dark theme colors
        replacements = {
            '/* BACKGROUND_GRADIENT */': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2C2C2E, stop:0.5 #1C1C1E, stop:1 #000000)',
            '/* SIDEBAR_BG */': 'rgba(44, 44, 46, 0.8)',
            '/* PLAYERBAR_BG */': 'rgba(44, 44, 46, 0.9)',
            '/* TEXT_PRIMARY */': '#FFFFFF',
            '/* TEXT_SECONDARY */': '#AEAEB2',
            '/* TEXT_TERTIARY */': '#8E8E93',
            '/* SEARCH_BG */': 'rgba(58, 58, 60, 0.8)',
            '/* BUTTON_HOVER */': 'rgba(255, 255, 255, 0.1)',
            '/* SLIDER_TRACK */': '#48484A',
            '/* BORDER_COLOR */': 'rgba(84, 84, 88, 0.6)'
        }
    else:
        # Light theme colors
        replacements = {
            '/* BACKGROUND_GRADIENT */': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E8E9F3, stop:0.5 #CECDD5, stop:1 #A6A5B8)',
            '/* SIDEBAR_BG */': 'rgba(255, 255, 255, 0.8)',
            '/* PLAYERBAR_BG */': 'rgba(255, 255, 255, 0.9)',
            '/* TEXT_PRIMARY */': '#000000',
            '/* TEXT_SECONDARY */': '#3C3C43',
            '/* TEXT_TERTIARY */': '#666666',
            '/* SEARCH_BG */': 'rgba(255, 255, 255, 0.8)',
            '/* BUTTON_HOVER */': 'rgba(0, 0, 0, 0.1)',
            '/* SLIDER_TRACK */': '#E8E9F3',
            '/* BORDER_COLOR */': 'rgba(255, 255, 255, 0.3)'
        }
    
    # Apply all replacements
    for placeholder, replacement in replacements.items():
        theme_content = theme_content.replace(placeholder, replacement)
    
    return theme_content


if __name__ == '__main__':
    main()
