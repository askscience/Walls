"""Sidebar Widgets for Radio Player"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPaintEvent, QPainter, QColor, QPalette
from PySide6.QtSvgWidgets import QSvgWidget
import os
import re


class SidebarItem(QWidget):
    """Clickable sidebar navigation item with icon and text."""
    clicked = Signal(str)
    
    def __init__(self, icon_path: str, text: str, item_id: str, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.is_active = False
        self.hovered = False
        self.icon_path = icon_path
        
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("SidebarItem")
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # Icon - use SVG widget if available
        if os.path.exists(icon_path) and icon_path.endswith('.svg'):
            self.svg_widget = QSvgWidget(icon_path, self)
            self.svg_widget.setFixedSize(20, 20)
            self._update_svg_color()
            layout.addWidget(self.svg_widget)
        else:
            # Fallback to QLabel with QIcon
            self.icon_label = QLabel()
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.icon_label.setPixmap(icon.pixmap(20, 20))
            self.icon_label.setFixedSize(20, 20)
            layout.addWidget(self.icon_label)
            self.svg_widget = None
        
        # Text
        self.text_label = QLabel(text)
        self.text_label.setObjectName("SidebarItemText")
        
        layout.addWidget(self.text_label)
        layout.addStretch()
    
    def _update_svg_color(self):
        """Update SVG color based on current theme."""
        if not self.svg_widget:
            return
            
        # Get current theme color
        palette = self.palette()
        text_color = palette.color(QPalette.WindowText)
        
        # Read SVG content and modify color
        if os.path.exists(self.icon_path):
            with open(self.icon_path, 'r') as f:
                svg_content = f.read()
            
            # Replace fill and stroke colors with current theme color
            # Replace any fill="..." with current color
            svg_content = re.sub(r'fill="[^"]*"', f'fill="{text_color.name()}"', svg_content)
            # Replace any stroke="..." with current color  
            svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{text_color.name()}"', svg_content)
            # Add default fill if none exists
            if 'fill=' not in svg_content and '<path' in svg_content:
                svg_content = svg_content.replace('<path', f'<path fill="{text_color.name()}"')
            
            # Load the modified SVG
            self.svg_widget.load(svg_content.encode())
    
    def set_active(self, active: bool):
        """Set the active state of the sidebar item."""
        self.is_active = active
        if active:
            self.setObjectName("SidebarItemActive")
        else:
            self.setObjectName("SidebarItem")
        self.style().unpolish(self)
        self.style().polish(self)
        if self.svg_widget:
            self._update_svg_color()  # Update SVG color when state changes
        self.update()
    
    def changeEvent(self, event):
        """Handle theme changes."""
        super().changeEvent(event)
        if event.type() == event.Type.PaletteChange:
            if self.svg_widget:
                self._update_svg_color()
    
    def paintEvent(self, e: QPaintEvent):
        """Custom paint event for hover and active states."""
        super().paintEvent(e)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.is_active:
            # Active state background
            painter.fillRect(self.rect(), QColor(255, 255, 255, 30))
            # Active indicator line
            painter.fillRect(0, 0, 3, self.height(), QColor(100, 150, 255))
        elif self.hovered:
            # Hover state background
            painter.fillRect(self.rect(), QColor(255, 255, 255, 15))
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        self.hovered = True
        self.update()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self.hovered = False
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item_id)