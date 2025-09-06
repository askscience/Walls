from PySide6.QtWidgets import QCheckBox

class CheckBox(QCheckBox):
    """CheckBox styled by the global unified theme."""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)