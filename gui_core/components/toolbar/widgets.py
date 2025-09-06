from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize

class ToolBar(QToolBar):
    """Simple wrapper around QToolBar with sensible defaults matching the theme.
    - Non-movable, non-floatable
    - Small icon size, text beside icon
    """
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(18, 18))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    def add_button(self, text: str, icon=None, triggered=None) -> QAction:
        act = QAction(text, self)
        if icon is not None:
            act.setIcon(icon)
        if triggered is not None:
            act.triggered.connect(triggered)
        self.addAction(act)
        return act