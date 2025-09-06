#!/usr/bin/env python3
"""
Test script for the adaptive theming system.

This script creates a simple GUI application to test:
1. System theme detection across platforms
2. Automatic theme switching based on system settings
3. Manual theme switching for testing
4. Component appearance in both dark and light themes

Usage:
    python test_adaptive_theme.py
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QRadioButton,
    QSlider, QComboBox, QProgressBar, QGroupBox, QTabWidget, QTabBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Add the gui_core directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from system_theme_detector import SystemThemeDetector, ThemeMode
from adaptive_theme_manager import get_theme_manager
from apply_theme import _load_mozilla_headline_font


class ThemeTestWindow(QMainWindow):
    """Test window to demonstrate adaptive theming."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaptive Theme Test - GUI Core Components")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Theme info section
        self.create_theme_info_section(layout)
        
        # Component test sections
        self.create_button_section(layout)
        self.create_input_section(layout)
        self.create_selection_section(layout)
        self.create_display_section(layout)
        
        # Manual theme controls
        self.create_manual_controls(layout)
        
        # Set up theme monitoring
        self.setup_theme_monitoring()
        
    def create_theme_info_section(self, layout):
        """Create section showing current theme information."""
        info_group = QGroupBox("Theme Information")
        info_layout = QVBoxLayout(info_group)
        
        self.system_theme_label = QLabel()
        self.current_theme_label = QLabel()
        self.platform_label = QLabel(f"Platform: {sys.platform}")
        
        info_layout.addWidget(self.platform_label)
        info_layout.addWidget(self.system_theme_label)
        info_layout.addWidget(self.current_theme_label)
        
        layout.addWidget(info_group)
        
    def create_button_section(self, layout):
        """Create section with various button types."""
        button_group = QGroupBox("Buttons")
        button_layout = QHBoxLayout(button_group)
        
        # Standard button
        standard_btn = QPushButton("Standard Button")
        button_layout.addWidget(standard_btn)
        
        # Primary button
        primary_btn = QPushButton("Primary Button")
        primary_btn.setProperty("variant", "primary")
        button_layout.addWidget(primary_btn)
        
        # Outlined button
        outlined_btn = QPushButton("Outlined Button")
        outlined_btn.setProperty("variant", "outlined")
        button_layout.addWidget(outlined_btn)
        
        # Tonal button
        tonal_btn = QPushButton("Tonal Button")
        tonal_btn.setProperty("variant", "tonal")
        button_layout.addWidget(tonal_btn)
        
        # Disabled button
        disabled_btn = QPushButton("Disabled Button")
        disabled_btn.setEnabled(False)
        button_layout.addWidget(disabled_btn)
        
        layout.addWidget(button_group)
        
    def create_input_section(self, layout):
        """Create section with input components."""
        input_group = QGroupBox("Input Components")
        input_layout = QVBoxLayout(input_group)
        
        # Line edit
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter text here...")
        input_layout.addWidget(QLabel("Line Edit:"))
        input_layout.addWidget(line_edit)
        
        # Text edit
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Enter multiline text here...")
        text_edit.setMaximumHeight(80)
        input_layout.addWidget(QLabel("Text Edit:"))
        input_layout.addWidget(text_edit)
        
        # Combo box
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        input_layout.addWidget(QLabel("Combo Box:"))
        input_layout.addWidget(combo)
        
        layout.addWidget(input_group)
        
    def create_selection_section(self, layout):
        """Create section with selection components."""
        selection_group = QGroupBox("Selection Components")
        selection_layout = QVBoxLayout(selection_group)
        
        # Checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox1 = QCheckBox("Checkbox 1")
        checkbox2 = QCheckBox("Checkbox 2 (Checked)")
        checkbox2.setChecked(True)
        checkbox3 = QCheckBox("Checkbox 3 (Disabled)")
        checkbox3.setEnabled(False)
        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        checkbox_layout.addWidget(checkbox3)
        selection_layout.addWidget(QLabel("Checkboxes:"))
        selection_layout.addLayout(checkbox_layout)
        
        # Radio buttons
        radio_layout = QHBoxLayout()
        radio1 = QRadioButton("Radio 1")
        radio2 = QRadioButton("Radio 2 (Selected)")
        radio2.setChecked(True)
        radio3 = QRadioButton("Radio 3")
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addWidget(radio3)
        selection_layout.addWidget(QLabel("Radio Buttons:"))
        selection_layout.addLayout(radio_layout)
        
        # Slider
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        selection_layout.addWidget(QLabel("Slider:"))
        selection_layout.addWidget(slider)
        
        layout.addWidget(selection_group)
        
    def create_display_section(self, layout):
        """Create section with display components."""
        display_group = QGroupBox("Display Components")
        display_layout = QVBoxLayout(display_group)
        
        # Progress bar
        progress = QProgressBar()
        progress.setValue(65)
        display_layout.addWidget(QLabel("Progress Bar:"))
        display_layout.addWidget(progress)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(QLabel("Content of Tab 1"), "Tab 1")
        tabs.addTab(QLabel("Content of Tab 2"), "Tab 2")
        tabs.addTab(QLabel("Content of Tab 3"), "Tab 3")
        display_layout.addWidget(QLabel("Tabs:"))
        display_layout.addWidget(tabs)
        
        layout.addWidget(display_group)
        
    def create_manual_controls(self, layout):
        """Create manual theme control buttons."""
        controls_group = QGroupBox("Manual Theme Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Force dark theme
        dark_btn = QPushButton("Force Dark Theme")
        dark_btn.clicked.connect(lambda: self.force_theme(ThemeMode.DARK))
        controls_layout.addWidget(dark_btn)
        
        # Force light theme
        light_btn = QPushButton("Force Light Theme")
        light_btn.clicked.connect(lambda: self.force_theme(ThemeMode.LIGHT))
        controls_layout.addWidget(light_btn)
        
        # Auto theme (follow system)
        auto_btn = QPushButton("Auto Theme (Follow System)")
        auto_btn.clicked.connect(self.enable_auto_theme)
        controls_layout.addWidget(auto_btn)
        
        # Refresh theme detection
        refresh_btn = QPushButton("Refresh Theme Detection")
        refresh_btn.clicked.connect(self.refresh_theme_info)
        controls_layout.addWidget(refresh_btn)
        
        layout.addWidget(controls_group)
        
    def setup_theme_monitoring(self):
        """Set up automatic theme monitoring."""
        # Update theme info initially
        self.refresh_theme_info()
        
        # Store the last known theme to detect changes
        self.last_known_theme = None
        
        # Set up a simple timer to check for theme changes
        import threading
        import time
        
        def check_theme_periodically():
            while True:
                try:
                    current_theme = get_theme_manager().current_theme
                    if self.last_known_theme != current_theme:
                        self.last_known_theme = current_theme
                        # Schedule UI update in main thread
                        self.refresh_theme_info()
                    time.sleep(1)  # Check every second
                except Exception as e:
                    print(f"Error checking theme: {e}")
                    time.sleep(1)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=check_theme_periodically, daemon=True)
        monitor_thread.start()
        
    def refresh_theme_info(self):
        """Refresh the theme information display."""
        try:
            system_theme = SystemThemeDetector.get_system_theme()
            current_theme = get_theme_manager().current_theme
            
            self.system_theme_label.setText(f"System Theme: {system_theme.value}")
            self.current_theme_label.setText(f"Current Applied Theme: {current_theme.value}")
            
        except Exception as e:
            self.system_theme_label.setText(f"System Theme: Error - {str(e)}")
            self.current_theme_label.setText("Current Applied Theme: Unknown")
            
    def force_theme(self, theme_mode: ThemeMode):
        """Force a specific theme mode."""
        try:
            get_theme_manager().set_theme(QApplication.instance(), theme_mode)
            self.refresh_theme_info()
        except Exception as e:
            print(f"Error forcing theme {theme_mode.value}: {e}")
            
    def enable_auto_theme(self):
        """Enable automatic theme following system settings."""
        try:
            get_theme_manager().start_monitoring(QApplication.instance())
            self.refresh_theme_info()
        except Exception as e:
            print(f"Error enabling auto theme: {e}")


def main():
    """Main function to run the theme test application."""
    app = QApplication(sys.argv)
    
    # Load fonts
    _load_mozilla_headline_font()
    
    # Create and show the test window
    window = ThemeTestWindow()
    window.show()
    
    # Apply initial adaptive theme
    try:
        from adaptive_theme_manager import apply_adaptive_theme
        apply_adaptive_theme(app, enable_monitoring=True)
    except Exception as e:
        print(f"Error applying adaptive theme: {e}")
        # Fallback to basic styling
        app.setStyleSheet("QWidget { font-family: 'Inter', system-ui; }")
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()