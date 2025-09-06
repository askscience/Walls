"""Audio Visualizer Widget for Radio Player"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPaintEvent


class VisualizerWidget(QWidget):
    """Static audio visualizer widget with fixed bars."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 60)
        self.setObjectName("VisualizerWidget")
        
        # Static visualizer data - fixed heights for bars
        self.bars = [0.3, 0.5, 0.2, 0.7, 0.4, 0.6, 0.3, 0.8, 0.2, 0.5,
                    0.4, 0.6, 0.3, 0.7, 0.5, 0.4, 0.6, 0.3, 0.5, 0.2]  # 20 bars
    
    def set_playing(self, playing: bool):
        """Set the playing state (no-op for static visualizer)."""
        pass
    
    def set_levels(self, levels):
        """Set audio levels (no-op for static visualizer)."""
        pass
    
    def paintEvent(self, e: QPaintEvent):
        """Paint nothing - empty visualizer."""
        pass