from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt

class Breadcrumbs(QWidget):
    """Simple breadcrumb navigation composed of buttons and separators.
    Emits crumbClicked(index) when a segment is clicked.
    """
    crumbClicked = Signal(int)

    def __init__(self, parts: list[str] | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("breadcrumbs")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._parts: list[str] = []
        if parts:
            self.setPath(parts)

    def clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def setPath(self, parts: list[str]):
        self._parts = parts[:]
        self._rebuild()

    def _rebuild(self):
        self.clear()
        for i, text in enumerate(self._parts):
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFlat(True)
            btn.clicked.connect(lambda _, idx=i: self.crumbClicked.emit(idx))
            self._layout.addWidget(btn)
            if i < len(self._parts) - 1:
                sep = QLabel("›")
                sep.setObjectName("separator")
                sep.setAlignment(Qt.AlignCenter)
                sep.setContentsMargins(6, 0, 6, 0)
                self._layout.addWidget(sep)
        self._layout.addStretch()