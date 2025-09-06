from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class PrimaryButton(QPushButton):
    """Rounded primary button following the unified theme."""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("variant", "primary")
        # Make buttons smaller to match compact theme
        self.setMinimumHeight(26)
        self.setCursor(Qt.PointingHandCursor)