from PySide6.QtWidgets import QProgressBar

class ProgressBar(QProgressBar):
    """ProgressBar styled by the unified theme."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(18)
        self.setTextVisible(False)