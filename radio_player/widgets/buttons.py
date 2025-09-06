"""Button Widgets for Radio Player"""

from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QIcon, QPaintEvent, QPalette
from PySide6.QtSvgWidgets import QSvgWidget
import os
import re


class ModernButton(QPushButton):
    """Modern button with hover effects and custom styling."""
    def __init__(self, text="", icon=None, parent=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("ModernButton")
        # Styling is now handled by theme.qss


class IconButton(QWidget):
    """Custom icon button with hover effects and theme-aware icon coloring."""
    clicked = Signal()
    
    def __init__(self, icon_path: str, size: int = 40, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.hovered = False
        
        # Create SVG widget if the icon is SVG
        if os.path.exists(icon_path) and icon_path.endswith('.svg'):
            self.svg_widget = QSvgWidget(icon_path, self)
            self.svg_widget.setFixedSize(24, 24)
            self.svg_widget.move((size - 24) // 2, (size - 24) // 2)  # Center the SVG
            self._update_svg_color()
        else:
            self.svg_widget = None
        
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
    
    def changeEvent(self, event):
        """Handle theme changes."""
        super().changeEvent(event)
        if event.type() == event.Type.PaletteChange:
            self._update_svg_color()
    
    def paintEvent(self, e: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hover effect
        if self.hovered:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 20))
    
    def enterEvent(self, event):
        self.hovered = True
        self.update()
    
    def leaveEvent(self, event):
        self.hovered = False
        self.update()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()