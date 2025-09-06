from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from browser.app.controller import BrowserController


def _icons_dir() -> Path:
    # Project root is two levels up from this file: browser/ui/window.py -> project root
    return Path(__file__).resolve().parents[2] / 'gui_core' / 'utils' / 'icons'


def _load_icon(name: str) -> QIcon:
    p = _icons_dir() / name
    return QIcon(str(p)) if p.exists() else QIcon()


class BrowserWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Walls Browser")

        self.webview = QWebEngineView(self)
        self.controller = BrowserController(self.webview)

        # Top bar
        bar = QHBoxLayout()
        bar.setContentsMargins(0, 5, 0, 5)  # 5px padding top/bottom as requested
        bar.setSpacing(0)
        self.addr = QLineEdit(self)
        self.addr.setPlaceholderText("Enter URL...")

        btn_back = QPushButton()
        btn_back.setIcon(_load_icon('arrow-left.svg'))
        btn_back.setToolTip("Back")

        btn_fwd = QPushButton()
        btn_fwd.setIcon(_load_icon('arrow-right.svg'))
        btn_fwd.setToolTip("Forward")

        btn_go = QPushButton()
        btn_go.setIcon(_load_icon('enter.svg'))  # icon for "Go"
        btn_go.setToolTip("Go")

        btn_reload = QPushButton()
        btn_reload.setIcon(_load_icon('repeat.svg'))  # icon for "Reload"
        btn_reload.setToolTip("Reload")

        # Adblock UI: single shield button toggles on/off
        self.btn_adblock = QPushButton()
        self.btn_adblock.setToolTip("Toggle Adblock")
        self.btn_adblock.setIcon(_load_icon('shield-slash.svg'))  # default off

        btn_back.clicked.connect(lambda: self.controller.back())
        btn_fwd.clicked.connect(lambda: self.controller.forward())
        btn_reload.clicked.connect(lambda: self.controller.reload())
        btn_go.clicked.connect(self.navigate)
        self.addr.returnPressed.connect(self.navigate)

        # Button click toggles adblock and updates icon
        def on_adblock_clicked():
            try:
                res = self.controller.adblock_toggle()
                active = (res.get('data') or {}).get('active', False)
                self._refresh_adblock_icon(bool(active))
            except Exception:
                # If toggle fails, try reading current status to set icon
                try:
                    st = self.controller.adblock_status()
                    active = (st.get('data') or {}).get('active', False)
                    self._refresh_adblock_icon(bool(active))
                except Exception:
                    self._refresh_adblock_icon(False)
        self.btn_adblock.clicked.connect(on_adblock_clicked)

        # Layout order: Back, Forward, Reload, [Adblock Button], Address, Go
        for w in (btn_back, btn_fwd, btn_reload, self.btn_adblock, self.addr, btn_go):
            bar.addWidget(w)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addLayout(bar)
        root.addWidget(self.webview, 1)

        # Remove any widget-level margins or borders
        self.setContentsMargins(0, 0, 0, 0)
        self.webview.setStyleSheet("border: none;")

        self.resize(1100, 800)

        # Initialize adblock icon state from controller
        try:
            st = self.controller.adblock_status()
            active = (st.get('data') or {}).get('active', False)
            self._refresh_adblock_icon(bool(active))
        except Exception:
            self._refresh_adblock_icon(False)

        # Load DuckDuckGo as the first page
        self.addr.setText("duckduckgo.com")
        self.navigate()

    def _refresh_adblock_icon(self, active: bool):
        self.btn_adblock.setIcon(_load_icon('shield-check.svg' if active else 'shield-slash.svg'))

    def navigate(self):
        url = self.addr.text().strip()
        if url:
            self.controller.open_url(url)