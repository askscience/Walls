from __future__ import annotations
import sys
from typing import Dict, Any
import threading

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject, Signal, Slot, Qt
from gui_core.apply_theme import apply_theme

from shared_server.server import get_shared_server
from browser.ui.window import BrowserWindow
from browser.app.controller import BrowserController
from browser.app.summarizer import summarize_html
from browser.app.bookmarks import BookmarksManager


APP_NAME = "browser"


class UiCommandBridge(QObject):
    """Bridge to execute commands on the UI thread and return results."""
    
    # Signal used to queue execution onto the UI thread
    runRequested = Signal(str, object)
    
    def __init__(self, app_instance: 'BrowserApp'):
        super().__init__()
        self.app_instance = app_instance
        self.result = None
        self.finished = False
        # Threading event for synchronization
        import threading as _th
        self._event = _th.Event()
        # Ensure queued connection into the UI thread
        try:
            # Explicitly set queued connection type
            self.runRequested.connect(self._on_run, Qt.QueuedConnection)
        except Exception:
            self.runRequested.connect(self._on_run)

    # Define a slot that will run on the UI thread
    @Slot(str, object)
    def _on_run(self, cmd: str, args: Dict[str, Any]):
        try:
            res = self.app_instance._handle_command_ui(cmd, args)
        except Exception as e:
            res = {"status": "error", "message": str(e)}
        self.result = res
        self.finished = True
        self._event.set()

    def execute_command(self, cmd: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command on UI thread using signal/slot queued connection."""
        # Reset state
        self.result = None
        self.finished = False
        self._event.clear()
        # Emit the call into UI thread
        self.runRequested.emit(cmd, args)
        # Wait for completion
        if not self._event.wait(timeout=10.0):
            return {"status": "error", "message": "UI command timeout"}
        return self.result or {"status": "error", "message": "No result"}


class BrowserApp:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        apply_theme(self.app)
        self.window = BrowserWindow()
        self.controller: BrowserController = self.window.controller
        self.bookmarks = BookmarksManager()
        # Bridge for UI-thread execution - will be created on UI thread
        self.bridge = None

    def start(self):
        # Create bridge on UI thread
        self.bridge = UiCommandBridge(self)
        # Move bridge to UI thread to ensure signals work properly
        self.bridge.moveToThread(self.app.thread())
        self.window.show()

    def handle_command(self, cmd: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command from shared server."""
        # Fast path for readiness probes
        if cmd == 'ping':
            return {"status": "success", "message": "pong"}

        # Route commands through the UI-thread bridge when available to avoid cross-thread UI calls
        try:
            if getattr(self, 'bridge', None) is not None:
                return self.bridge.execute_command(cmd, args or {})
            # Fallback (should be rare): direct call
            return self._handle_command_ui(cmd, args or {})
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_command_ui(self, cmd: str, args: Dict[str, Any]) -> Dict[str, Any]:
        # All code here runs on the UI thread
        try:
            if cmd == 'ui_ping':
                # UI-thread readiness probe
                return {"status": "success", "message": "ui_pong"}

            if cmd == 'open':
                url = args.get('url') or args.get('arg0')
                if not url:
                    return {"status": "error", "message": "url is required"}
                return self.controller.open_url(url)

            if cmd == 'back':
                return self.controller.back()

            if cmd == 'forward':
                return self.controller.forward()

            if cmd == 'reload':
                return self.controller.reload()

            if cmd == 'bookmark_add':
                url = args.get('url') or self.controller.current_url()
                name = args.get('name') or url
                if not url:
                    return {"status": "error", "message": "No URL available"}
                self.bookmarks.add(name=name, url=url)
                return {"status": "success", "message": f"Bookmarked {name}"}

            if cmd == 'bookmarks_json':
                data = [b.__dict__ for b in self.bookmarks.list()]
                return {"status": "success", "message": "Bookmarks JSON", "data": {"bookmarks": data}}

            if cmd == 'get_html':
                # Note: async retrieval; we return pending
                self.controller.webview.page().toHtml(lambda h: None)
                return {"status": "pending", "message": "Retrieving HTML"}

            if cmd == 'get_html_sync':
                # Fetch synchronously with simple event processing loop
                html_container = {'html': ''}
                done = {'flag': False}

                def cb(html: str):
                    html_container['html'] = html
                    done['flag'] = True

                self.controller.webview.page().toHtml(cb)
                import time
                timeout = time.time() + 5
                while not done['flag'] and time.time() < timeout:
                    self.app.processEvents()
                    time.sleep(0.01)
                return {"status": "success", "message": "HTML retrieved", "data": {"html": html_container['html']}}

            if cmd == 'summarize':
                html_resp = self._handle_command_ui('get_html_sync', {})
                html = (html_resp.get('data') or {}).get('html', '')
                summ = summarize_html(html, base_url=self.controller.current_url())
                return {"status": "success", "message": "Summary ready", "data": summ}

            if cmd == 'click':
                selector = args.get('selector') or args.get('arg0')
                if not selector:
                    return {"status": "error", "message": "selector is required"}
                return self.controller.click_selector(selector)

            if cmd == 'click_text':
                text = args.get('text') or args.get('arg0')
                if not text:
                    return {"status": "error", "message": "text is required"}
                return self.controller.click_text(text)

            # Adblock commands
            if cmd == 'adblock_enable':
                return self.controller.adblock_enable()
            if cmd == 'adblock_disable':
                return self.controller.adblock_disable()
            if cmd == 'adblock_toggle':
                return self.controller.adblock_toggle()
            if cmd == 'adblock_status':
                return self.controller.adblock_status()
            if cmd == 'adblock_load':
                path = args.get('path') or args.get('arg0')
                if not path:
                    return {"status": "error", "message": "path is required"}
                return self.controller.adblock_load(path)
            if cmd == 'adblock_load_dir':
                path = args.get('path') or args.get('arg0')
                if not path:
                    return {"status": "error", "message": "path is required"}
                return self.controller.adblock_load_dir(path)
            if cmd == 'adblock_fetch_easylist':
                url = args.get('url') or args.get('arg0')  # optional override
                return self.controller.adblock_fetch_easylist(url)

            if cmd == 'help':
                return {
                    "status": "success",
                    "message": "Commands listed",
                    "data": {
                        "commands": [
                            "open url=<url>",
                            "back",
                            "forward",
                            "reload",
                            "bookmark_add [url=<url>] [name=<name>]",
                            "bookmarks_json",
                            "click selector=<css>",
                            "click_text text=<text>",
                            "get_html_sync",
                            "summarize",
                            "adblock_enable",
                            "adblock_disable",
                            "adblock_toggle",
                            "adblock_status",
                            "adblock_load path=<easylist.txt>",
                            "adblock_load_dir path=<easylist_repo_dir>",
                            "adblock_fetch_easylist [url=<zip_url>]",
                            "ping",
                            "ui_ping"
                        ]
                    }
                }

            return {"status": "error", "message": f"Unknown command: {cmd}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def run():
    app_instance = BrowserApp()

    # Register with shared server
    server = get_shared_server()
    server.register_app(APP_NAME, app_instance.handle_command, description="Browser CLI Interface")
    # Note: Don't call server.start() here - the shared server should already be running

    app_instance.start()
    sys.exit(app_instance.app.exec())


if __name__ == '__main__':
    run()