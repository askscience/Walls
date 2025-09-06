from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QSize, Signal

class AccordionSection(QWidget):
    """Single collapsible section with a header and a content area.
    Exposes toggled(bool) when expanded/collapsed.
    """
    toggled = Signal(bool)

    def __init__(self, title: str = "Section", content: QWidget | None = None, expanded: bool = False, parent=None):
        super().__init__(parent)
        self._expanded = expanded

        self.container = QFrame(self)
        self.container.setObjectName("accordionSection")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.container)

        lay = QVBoxLayout(self.container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("accordionHeader")
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        self.toggle_btn = QPushButton("▸")
        self.toggle_btn.setObjectName("accordionChevron")
        self.toggle_btn.setFixedSize(QSize(20, 20))
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._on_toggle_clicked)
        h.addWidget(self.toggle_btn)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("accordionTitle")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        h.addWidget(self.title_label, 1)

        lay.addWidget(header)

        # Body
        self.body = QWidget()
        self.body.setObjectName("accordionBody")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(12, 8, 12, 12)
        self.body_layout.setSpacing(8)

        if content is not None:
            self.body_layout.addWidget(content)
        lay.addWidget(self.body)

        self.setExpanded(self._expanded)

    def setContent(self, widget: QWidget):
        # Clear old
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        self.body_layout.addWidget(widget)

    def isExpanded(self) -> bool:
        return self._expanded

    def setExpanded(self, expanded: bool):
        self._expanded = bool(expanded)
        self.body.setVisible(self._expanded)
        self.toggle_btn.setText("▾" if self._expanded else "▸")
        self.toggled.emit(self._expanded)

    def _on_toggle_clicked(self):
        self.setExpanded(not self._expanded)

class Accordion(QWidget):
    """Accordion composed of multiple AccordionSection widgets.
    Usage:
        acc = Accordion()
        acc.addSection("Title", custom_widget)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("accordion")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

    def addSection(self, title: str, content: QWidget, expanded: bool = False) -> AccordionSection:
        section = AccordionSection(title, content, expanded, self)
        self._layout.addWidget(section)
        return section

    def clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()