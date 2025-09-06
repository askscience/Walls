from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class Modal(QDialog):
    """A simple modal dialog with a title, body content slot, and actions row."""
    def __init__(self, title: str = "", body: str = "", parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setObjectName("modal")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("modalTitle")
        layout.addWidget(self.title_label)

        self.body_label = QLabel(body)
        self.body_label.setWordWrap(True)
        layout.addWidget(self.body_label)

        # Actions
        actions = QHBoxLayout()
        actions.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn = QPushButton("OK")
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)
        actions.addWidget(self.cancel_btn)
        actions.addWidget(self.ok_btn)
        layout.addLayout(actions)