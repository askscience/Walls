"""Blur Widgets

Custom transparent widgets with blur effects for the AI interface.
"""

from PySide6.QtWidgets import QWidget, QGraphicsBlurEffect, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPalette


class BlurPanel(QWidget):
    """A bubble-style panel with dark semi-transparent background."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the basic UI properties."""
        # Make the widget transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Reduce window flags, use only frameless to avoid always-on-top issues
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set up layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)
        self.layout.setSpacing(15)
    
    def paintEvent(self, event):
        """Custom paint event for dark bubble background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw dark semi-transparent rounded rectangle
        painter.setBrush(QColor(20, 20, 20, 200))  # Dark with semi-transparency
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)
        
        super().paintEvent(event)


class BlurResponseWidget(QWidget):
    """A bubble-style widget for displaying AI responses."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the basic UI properties."""
        # Make the widget transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Reduce window flags, use only frameless to avoid always-on-top issues
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set up layout with padding
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(8)
    
    def paintEvent(self, event):
        """Custom paint event for dark bubble background."""
        if not self.isVisible():
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw dark semi-transparent rounded rectangle
        painter.setBrush(QColor(20, 20, 20, 200))  # Dark with semi-transparency
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)
        
        super().paintEvent(event)
