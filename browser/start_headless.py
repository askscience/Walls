#!/usr/bin/env python3
"""Headless browser server startup for CLI testing."""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_server.server import get_shared_server

APP_NAME = "browser"

class MockBrowserApp:
    """Mock browser app for testing CLI integration."""
    
    def __init__(self):
        self.current_url_value = "about:blank"
        self.html_content = "<html><head><title>Mock Browser</title></head><body><h1>Mock Browser</h1><p>This is a test browser instance.</p></body></html>"
        
    def handle_command(self, cmd: str, args: dict) -> dict:
        """Handle CLI commands."""
        print(f"[MockBrowser] Received command: {cmd} with args: {args}")
        
        try:
            if cmd == 'ui_ping' or cmd == 'ping':
                return {"status": "success", "message": "ui_pong"}
            
            elif cmd == 'open':
                url = args.get('url', '')
                if not url:
                    return {"status": "error", "message": "URL is required"}
                self.current_url_value = url
                return {"status": "success", "message": f"Opened {url}"}
            
            elif cmd == 'get_html_sync':
                return {
                    "status": "success", 
                    "message": "HTML retrieved", 
                    "data": {"html": self.html_content}
                }
            
            elif cmd == 'back':
                return {"status": "success", "message": "Back"}
            
            elif cmd == 'forward':
                return {"status": "success", "message": "Forward"}
            
            elif cmd == 'reload':
                return {"status": "success", "message": "Reload"}
            
            elif cmd == 'help':
                return {
                    "status": "success",
                    "message": "Mock browser commands available",
                    "data": {
                        "commands": ["ui_ping", "open", "get_html_sync", "back", "forward", "reload"]
                    }
                }
            
            else:
                return {"status": "error", "message": f"Unknown command: {cmd}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    print("Starting mock browser server for CLI testing...")
    
    app = MockBrowserApp()
    
    # Register with shared server
    server = get_shared_server()
    port = server.register_app(APP_NAME, app.handle_command, "Mock Browser CLI Interface")
    
    print(f"Mock browser registered on port {port}")
    print("Server ready for CLI commands. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down mock browser server...")
        server.unregister_app(APP_NAME)

if __name__ == '__main__':
    main()