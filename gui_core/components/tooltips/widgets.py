from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class ToolTip(QLabel):
    """A simple tooltip widget that can be shown programmatically near a point.
    Styling is driven by global QToolTip rules; this class is for custom/inline tooltips.
    """
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.ToolTip)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setMargin(6)
        # Keep background transparent; theme applies QToolTip styling when used via QToolTip
        # For this inline label, we mimic the look via palette; users can also style via objectName
        self.setObjectName("inlineToolTip")

    def showAt(self, global_pos):
        self.move(global_pos)
        self.show()