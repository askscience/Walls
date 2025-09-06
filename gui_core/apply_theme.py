import os
from typing import List

from PySide6.QtGui import QFontDatabase
from .adaptive_theme_manager import apply_adaptive_theme

BASE_DIR = os.path.dirname(__file__)


def _load_mozilla_headline_font() -> None:
    """Load Mozilla Headline font files so QSS can reference the family.
    Attempts to load the variable font and all static TTFs if present.
    Safe to call multiple times.
    """
    fonts_root = os.path.join(BASE_DIR, "utils", "fonts", "Mozilla_Headline")
    if not os.path.isdir(fonts_root):
        return

    # Collect candidate font files
    candidates: List[str] = []
    variable_font = os.path.join(fonts_root, "MozillaHeadline-VariableFont_wdth,wght.ttf")
    if os.path.exists(variable_font):
        candidates.append(variable_font)

    static_dir = os.path.join(fonts_root, "static")
    if os.path.isdir(static_dir):
        for name in os.listdir(static_dir):
            if name.lower().endswith(".ttf"):
                candidates.append(os.path.join(static_dir, name))

    # Load fonts
    for path in candidates:
        try:
            QFontDatabase.addApplicationFont(path)
        except Exception:
            # Best effort: ignore individual font load failures
            pass


def load_all_qss() -> str:
    """Load a single, unified QSS theme for the entire app.
    
    Deprecated: Use apply_adaptive_theme() instead for system theme support.
    This function is kept for backward compatibility.
    """
    root_qss = os.path.join(BASE_DIR, "theme.qss")
    if os.path.exists(root_qss):
        with open(root_qss, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def apply_theme(app) -> None:
    """Apply adaptive theme that responds to system theme changes.
    
    This function now uses the adaptive theme manager to automatically
    detect and apply the appropriate theme (dark/light) based on the
    system settings across Linux, Windows, and macOS.
    """
    # Ensure Mozilla Headline is available to the application so QSS can use it
    _load_mozilla_headline_font()
    
    # Use the new adaptive theming system
    apply_adaptive_theme(app)