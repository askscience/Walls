from PySide6.QtWidgets import QLineEdit

class LineEdit(QLineEdit):
    """LineEdit with unified theme (rounded, minimal)."""
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)