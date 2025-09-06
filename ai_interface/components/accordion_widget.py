"""Accordion Widget

Widget for displaying collapsible content sections, specifically for thinking tags.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QSize
from PySide6.QtGui import QFont, QPalette, QColor


class AccordionWidget(QWidget):
    """A collapsible accordion widget for displaying thinking content."""
    
    def __init__(self, title="Thinking Process", parent=None):
        super().__init__(parent)
        self.title = title
        self.is_expanded = False
        self.content_widget = None
        self.animation = None
        # Initialize content_height to ensure availability before any content is set
        self.content_height = 0
        # Override global theme background to prevent grey square
        self.setStyleSheet("AccordionWidget { background-color: transparent; }")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the accordion UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create toggle button
        self.toggle_button = QPushButton(f"▶ {self.title}")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_content)
        self.toggle_button.setMinimumWidth(80)  # Ensure enough width for text
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #555555;
                border: none;
                padding: 2px 4px;
                text-align: left;
                font-size: 9px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                border-radius: 0px;
                min-width: 80px;
            }
            QPushButton:hover {
                color: #777777;
            }
            QPushButton:checked {
                color: #888888;
            }
        """)
        
        # Create content container
        self.content_container = QFrame()
        self.content_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                margin-top: 0px;
            }
        """)
        self.content_container.setMaximumHeight(0)
        self.content_container.setMinimumHeight(0)
        
        # Create content text widget
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(2, 2, 2, 2)
        
        self.content_widget = QTextEdit()
        self.content_widget.setReadOnly(True)
        self.content_widget.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #555555;
                font-size: 8px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                padding: 0px;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(60, 60, 60, 0.2);
                border-radius: 1px;
                min-height: 10px;
            }
        """)
        
        content_layout.addWidget(self.content_widget)
        
        # Add to main layout
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_container)
        layout.addStretch()
        
        # Setup animation
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
    
    def set_content(self, text: str, auto_scroll=True):
        """Set the content of the accordion."""
        self.content_widget.setPlainText(text)
        # Calculate appropriate height based on content
        document = self.content_widget.document()
        document.setTextWidth(self.content_widget.viewport().width())
        height = int(document.size().height()) + 4  # Add minimal padding
        self.content_height = min(height, 80)  # Max height of 80px
        
        # If currently expanded, update the container height immediately
        if self.is_expanded:
            self.content_container.setMaximumHeight(self.content_height)
        
        # Auto-scroll to bottom if requested
        if auto_scroll:
            scrollbar = self.content_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def append_content(self, text: str):
        """Append text to the existing content (for streaming)."""
        current_text = self.content_widget.toPlainText()
        self.content_widget.setPlainText(current_text + text)
        # Recalculate height
        document = self.content_widget.document()
        document.setTextWidth(self.content_widget.viewport().width())
        height = int(document.size().height()) + 4  # Add minimal padding
        self.content_height = min(height, 80)  # Max height of 80px
        # Update height if expanded
        if self.is_expanded:
            self.content_container.setMaximumHeight(self.content_height)
        
        # Auto-scroll to bottom during streaming
        scrollbar = self.content_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def toggle_content(self):
        """Toggle the accordion open/closed."""
        self.is_expanded = self.toggle_button.isChecked()
        
        # Ensure content_height is initialized based on current content if not already set
        if not getattr(self, "content_height", None) or self.content_height <= 0:
            document = self.content_widget.document()
            document.setTextWidth(self.content_widget.viewport().width())
            height = int(document.size().height()) + 4  # Add minimal padding
            self.content_height = min(height, 80)  # Max height of 80px
        
        if self.is_expanded:
            self.toggle_button.setText(f"▼ {self.title}")
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.content_height)
        else:
            self.toggle_button.setText(f"▶ {self.title}")
            self.animation.setStartValue(self.content_height)
            self.animation.setEndValue(0)
        
        self.animation.start()
    
    def expand(self):
        """Expand the accordion."""
        if not self.is_expanded:
            self.toggle_button.setChecked(True)
            self.toggle_content()
    
    def collapse(self):
        """Collapse the accordion."""
        if self.is_expanded:
            self.toggle_button.setChecked(False)
            self.toggle_content()
