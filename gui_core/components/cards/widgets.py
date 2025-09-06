from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

class Card(QWidget):
    """Versatile card to display text, optional media, and actions.
    Sections: media (optional), title, subtitle/body, actions (optional).
    """
    clicked = Signal()

    def __init__(self, title: str = "", subtitle: str = "", media: QPixmap | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")

        self.container = QFrame(self)
        self.container.setObjectName("cardContainer")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.container)

        lay = QVBoxLayout(self.container)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Media
        self.media_label = QLabel()
        self.media_label.setObjectName("cardMedia")
        self.media_label.setVisible(False)
        self.media_label.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.media_label)
        if media is not None:
            self.setMedia(media)

        # Title and subtitle
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("cardTitle")
            lay.addWidget(self.title_label)
        else:
            self.title_label = None
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("cardSubtitle")
            self.subtitle_label.setWordWrap(True)
            lay.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None

        # Body placeholder (user can add more widgets via addWidget)
        self.body = QWidget()
        self.body.setObjectName("cardBody")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(6)
        lay.addWidget(self.body)

        # Actions row
        self.actions = QWidget()
        self.actions.setObjectName("cardActions")
        self.actions_layout = QHBoxLayout(self.actions)
        self.actions_layout.setContentsMargins(0, 8, 0, 0)
        self.actions_layout.setSpacing(6)
        self.actions.setVisible(False)
        lay.addWidget(self.actions)

        # Mouse tracking for click effect (optional)
        self.setAttribute(Qt.WA_Hover)

    def setMedia(self, pixmap: QPixmap):
        self.media_label.setPixmap(pixmap)
        self.media_label.setVisible(True)

    def clearMedia(self):
        self.media_label.clear()
        self.media_label.setVisible(False)

    def addActionButton(self, btn: QPushButton):
        self.actions.setVisible(True)
        self.actions_layout.addWidget(btn)

    def addWidget(self, w: QWidget):
        self.body_layout.addWidget(w)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)