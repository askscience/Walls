from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
import os

class MessageBox(QMessageBox):
    """Themed message box helper inheriting QMessageBox.
    Use static methods like MessageBox.information(parent, title, text) as usual.
    This subclass exists to ensure theme consistency and to use project icons.
    """
    # Keep references to modeless instances to prevent Python GC from dropping signal connections
    _modeless_refs: list["MessageBox"] = []

    # --- Icon resolution helpers (shared with notifications approach) ---
    @classmethod
    def _icons_dir(cls) -> str:
        # widgets.py -> message_boxes -> components -> gui_core
        pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(pkg_root, "utils", "icons")

    @classmethod
    def _resolve_icon_path(cls, icon_name: str | None) -> str | None:
        if not icon_name:
            return None
        # Absolute path supported
        if os.path.isabs(icon_name) and os.path.exists(icon_name):
            return icon_name
        candidate = os.path.join(cls._icons_dir(), icon_name)
        if os.path.exists(candidate):
            return candidate
        return None

    @classmethod
    def _map_icon_file(cls, kind: str) -> str:
        mapping = {
            "information": "information.svg",
            "warning": "exclamation.svg",
            "critical": "circle-xmark.svg",
            "question": "question.svg",
        }
        return mapping.get(kind, "information.svg")

    @classmethod
    def _apply_kind_icon(cls, box: "MessageBox", kind: str) -> None:
        icon_path = cls._resolve_icon_path(cls._map_icon_file(kind))
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            # Use a reasonably large pixmap for message box icon
            box.setIconPixmap(icon.pixmap(48, 48))
            # Also set window icon for consistency
            box.setWindowIcon(icon)
        else:
            # Fallback to standard icons
            fallback = {
                "information": QMessageBox.Icon.Information,
                "warning": QMessageBox.Icon.Warning,
                "critical": QMessageBox.Icon.Critical,
                "question": QMessageBox.Icon.Question,
            }.get(kind, QMessageBox.Icon.Information)
            box.setIcon(fallback)

    @classmethod
    def _create(
        cls,
        kind: str,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> "MessageBox":
        box = cls(parent)
        box.setWindowTitle(title)
        box.setText(text)
        cls._apply_kind_icon(box, kind)
        box.setStandardButtons(buttons)
        if defaultButton != QMessageBox.StandardButton.NoButton:
            box.setDefaultButton(defaultButton)
        return box

    @classmethod
    def _retain_modeless(cls, box: "MessageBox") -> None:
        """Keep Python references for modeless dialogs so signal connections remain alive."""
        cls._modeless_refs.append(box)
        box.finished.connect(lambda: cls._release_modeless(box))

    @classmethod
    def _release_modeless(cls, box: "MessageBox") -> None:
        """Remove reference to modeless dialog when it's closed."""
        try:
            if box in cls._modeless_refs:
                cls._modeless_refs.remove(box)
        except (ValueError, RuntimeError):
            # Ignore if box is already gone or list is being modified
            pass

    # --- Public static-like API matching QMessageBox convenience functions ---
    @classmethod
    def information(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> QMessageBox.StandardButton:
        box = cls._create("information", parent, title, text, buttons, defaultButton)
        return QMessageBox.StandardButton(box.exec())

    @classmethod
    def warning(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> QMessageBox.StandardButton:
        box = cls._create("warning", parent, title, text, buttons, defaultButton)
        return QMessageBox.StandardButton(box.exec())

    @classmethod
    def critical(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> QMessageBox.StandardButton:
        box = cls._create("critical", parent, title, text, buttons, defaultButton)
        return QMessageBox.StandardButton(box.exec())

    @classmethod
    def question(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> QMessageBox.StandardButton:
        box = cls._create("question", parent, title, text, buttons, defaultButton)
        return QMessageBox.StandardButton(box.exec())

    # --- Modeless versions ---
    @classmethod
    def show_information(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> None:
        box = cls._create("information", parent, title, text, buttons, defaultButton)
        cls._retain_modeless(box)
        box.show()

    @classmethod
    def show_warning(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> None:
        box = cls._create("warning", parent, title, text, buttons, defaultButton)
        cls._retain_modeless(box)
        box.show()

    @classmethod
    def show_critical(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> None:
        box = cls._create("critical", parent, title, text, buttons, defaultButton)
        cls._retain_modeless(box)
        box.show()

    @classmethod
    def show_question(
        cls,
        parent,
        title: str,
        text: str,
        buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton,
    ) -> None:
        box = cls._create("question", parent, title, text, buttons, defaultButton)
        cls._retain_modeless(box)
        box.show()