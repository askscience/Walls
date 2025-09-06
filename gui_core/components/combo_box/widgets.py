from PySide6.QtWidgets import QComboBox

class ComboBox(QComboBox):
    """ComboBox styled by the unified theme."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Match compact sizing
        self.setMinimumHeight(28)