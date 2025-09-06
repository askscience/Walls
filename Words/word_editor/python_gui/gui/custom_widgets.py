from __future__ import annotations
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QIcon


def find_walls_root(start: Optional[Path] = None) -> Optional[Path]:
    p = (start or Path(__file__).resolve()).parent
    for _ in range(8):
        if p.name == "Walls" and p.is_dir():
            return p
        p = p.parent
    return None


def icon(name: str) -> QIcon:
    """Load an icon by filename from Walls/gui_core/utils/icons.

    Example: icon("floppy-disk.svg")
    """
    walls = find_walls_root()
    if walls is None:
        return QIcon()
    icon_path = walls / "gui_core" / "utils" / "icons" / name
    return QIcon(str(icon_path))