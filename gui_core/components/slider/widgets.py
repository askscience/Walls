from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt

class Slider(QSlider):
    """Horizontal slider styled by the unified theme."""
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMinimumHeight(24)