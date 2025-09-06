"""Main AI Interface

Main window that coordinates the AI interface components and handles user interactions.
"""

import sys
import os
import re
import subprocess
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QWidget
)

# Add ai_interface to path
ai_interface_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ai_interface_path)

from PySide6.QtCore import Qt, QTimer, Signal, QThread, QObject
from PySide6.QtGui import QGuiApplication, QCursor

# Add gui_core to path for theme application
gui_core_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gui_core')
sys.path.insert(0, gui_core_path)

from apply_theme import apply_theme
from components.unified_panel import UnifiedPanel
from services.rag_integration import RAGIntegrationService
from shared_server.client import is_app_running
# Command interception functionality removed - now using MCP servers

# Safe workspace and command interception logic so execution happens from the AI interface
SAFE_WORKSPACE = os.path.dirname(ai_interface_path)
SAFE_RAG_MAIN = os.path.join(SAFE_WORKSPACE, "rag", "main.py")
# Make workspace root importable so 'shared_server' (sibling to ai_interface) can be imported
if SAFE_WORKSPACE not in sys.path:
    sys.path.insert(0, SAFE_WORKSPACE)

# Command interception removed - responses are now handled by MCP servers


def _is_radio_search_command(cmd: str) -> bool:
    """Check if the command is a radio search command (not search-play)."""
    # Check for radio search commands but exclude search-play
    if "radio_player.cli" in cmd and "search" in cmd:
        # Exclude search-play commands
        if "search-play" not in cmd:
            return True
    return False


def _handle_radio_search_output(output: str) -> str:
    """Handle radio search output by formatting it for AI processing.
    Returns a formatted response that includes the command output and user prompt."""
    try:
        # Load prompts.json to get the radio search handling instruction
        import json
        prompts_path = os.path.join(SAFE_WORKSPACE, "rag", "prompts.json")
        with open(prompts_path, "r", encoding="utf-8") as f:
            prompts_data = json.load(f)
        
        # Prefer the dedicated radio_search_prompt, fallback to radio_search_handling for compatibility
        radio_prompt = (
            prompts_data.get("system_prompts", {})
                        .get("default", {})
                        .get("tool_specific_responses", {})
                        .get("radio_player", {})
                        .get("radio_search_prompt", "")
        ) or (
            prompts_data.get("system_prompts", {})
                        .get("default", {})
                        .get("tool_specific_responses", {})
                        .get("radio_player", {})
                        .get("radio_search_handling", "")
        )
        
        # Build a concise, trimmed list of results for the AI (avoid flooding the UI)
        try:
            import re
            lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
            # Prefer lines that look like numbered results (e.g., "1. Station ...")
            numbered = [ln for ln in lines if re.match(r"^\d+\.\s", ln)]
            # Load max options from prompts if provided, default to 10
            max_opts = (
                prompts_data.get("system_prompts", {})
                            .get("default", {})
                            .get("tool_specific_responses", {})
                            .get("radio_player", {})
                            .get("max_options", 10)
            )
            selected = (numbered or lines)[:max_opts]
            concise_list = "\n".join(selected)
        except Exception:
            concise_list = "\n".join(output.splitlines()[:10])

        # Format the prompt for the AI: only provide the concise list and radio instruction
        response_parts = []
        response_parts.append(concise_list)
        response_parts.append("")  # blank line
        if radio_prompt:
            response_parts.append(radio_prompt)
        else:
            response_parts.append("Please choose a station number from the list above.")
        
        return "\n".join([part for part in response_parts if part is not None])
            
    except Exception as e:
        print(f"Error handling radio search output: {e}")
        return f"--- Radio Search Results ---\n{output.strip()}\n\nWhich radio station would you like to listen to from the search results above?"





class AIInterface(QObject):
    """Main AI Interface coordinator for standalone widgets."""
    
    def __init__(self):
        super().__init__()
        self.setup_widgets()
        self.setup_rag_service()
        
        # Show the widgets
        self.show_widgets()
        
    def setup_widgets(self):
        """Setup the unified panel with proper screen-bounded geometry."""
        # Determine the target screen based on current cursor position; fallback to primary
        screen = QGuiApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        screen_geo = screen.geometry()
        screen_x, screen_y = screen_geo.x(), screen_geo.y()
        screen_width, screen_height = screen_geo.width(), screen_geo.height()

        # Create unified panel - positioned on left side of screen with reasonable size
        self.unified_panel = UnifiedPanel()
        self.unified_panel.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.unified_panel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set panel size and position - bottom left corner with good proportions
        panel_width = min(800, max(600, screen_width * 0.6))
        panel_height = min(600, max(400, screen_height * 0.7))
        panel_x = screen_x + 50  # 50px from left edge
        panel_y = screen_y + screen_height - panel_height - 50  # 50px from bottom edge
        
        self.unified_panel.setGeometry(panel_x, panel_y, panel_width, panel_height)
        
    def show_widgets(self):
        """Show the unified panel."""
        self.unified_panel.show()
        
    def connect_signals(self):
        """Connect component signals."""
        # Unified panel signals
        self.unified_panel.query_submitted.connect(self.handle_query)
        self.unified_panel.new_chat_requested.connect(self.handle_new_chat)
        self.unified_panel.chat_selected.connect(self.handle_chat_selected)

        # RAG service signals
        if self.rag_service:
            self.rag_service.response_chunk.connect(self.handle_response_chunk)
            self.rag_service.response_finished.connect(self.handle_response_finished)
            self.rag_service.error_occurred.connect(self.handle_rag_error)
        
    def handle_query(self, query: str):
        """Handle user query submission."""
        # Debug logging for user input
        if os.getenv("AI_IFACE_DEBUG") == "1":
            print(f"\n{'='*60}")
            print(f"👤 USER INPUT RECEIVED")
            print(f"{'='*60}")
            print(f"📝 Query: {query}")
            print(f"🕒 Timestamp: {time.strftime('%H:%M:%S')}")
            print(f"📊 Query Length: {len(query)} characters")
            print(f"🔄 Processing through RAG system...")
            print(f"{'='*60}\n")
            
        # Start response in the unified panel
        self.unified_panel.start_response()
    
        # If RAG is not ready, inform user directly in the panel and stop here
        if not self.rag_service or not self.rag_service.is_ready():
            self.unified_panel.finish_response("RAG service is not ready. Please wait a moment and try again.")
            return
    
        # Start loading state
        self.unified_panel.start_loading()
    
        # Get conversation context from current chat
        context = self.unified_panel.get_current_chat_context()
        
        # Submit query to RAG service with context
        if context:
            # Format context for RAG service
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
            full_query = f"Previous conversation:\n{context_str}\n\nCurrent question: {query}"
            self.rag_service.query(full_query)
        else:
            self.rag_service.query(query)
        
    def handle_response_chunk(self, chunk: str):
        """Handle streaming response chunks."""
        if os.getenv("AI_IFACE_DEBUG") == "1" and chunk.strip():
            # Only log substantial chunks to avoid spam
            if len(chunk) > 10:
                print(f"🤖 AI Response Chunk: {len(chunk)} chars - {chunk[:50].replace(chr(10), ' ')}...")
        self.unified_panel.add_response_chunk(chunk)
        
    def handle_response_finished(self, complete_response: str):
        """Handle when response is complete."""
        # Debug logging for AI output
        if os.getenv("AI_IFACE_DEBUG") == "1":
            print(f"\n{'='*60}")
            print(f"🤖 AI RESPONSE COMPLETED")
            print(f"{'='*60}")
            print(f"📤 Response Length: {len(complete_response)} characters")
            print(f"🕒 Completion Time: {time.strftime('%H:%M:%S')}")
            print(f"📖 Response Preview: {complete_response[:200].replace(chr(10), ' ')}...")
            
            # Check for MCP server usage indicators
            mcp_indicators = {
                'search': ['search', 'find', 'query', 'lookup'],
                'browse': ['http', 'website', 'url', 'browse'],
                'radio': ['radio', 'station', 'music', 'play'],
                'edit': ['edit', 'write', 'document', 'file']
            }
            
            detected_mcp = []
            response_lower = complete_response.lower()
            for mcp_type, keywords in mcp_indicators.items():
                if any(keyword in response_lower for keyword in keywords):
                    detected_mcp.append(mcp_type)
            
            if detected_mcp:
                print(f"🔧 Potential MCP Server Usage: {', '.join(detected_mcp).upper()}")
            else:
                print(f"🔧 MCP Server Usage: None detected")
            print(f"{'='*60}\n")
        
        # Stop loading state
        self.unified_panel.stop_loading()

        # Finish response display
        self.unified_panel.finish_response(complete_response)

        # Focus back to input
        self.unified_panel.focus_input()

        # Intercept and execute fenced bash code block commands asynchronously (safe allowlist)
        if os.getenv("AI_IFACE_DEBUG") == "1":
            print("[AIInterface] Response finished; checking for executable commands...")
        
        # Define callback for radio search results
        def radio_search_callback(radio_response: str):
            """Handle radio search results by triggering a new AI query.
            Includes safeguards to prevent recursive queries on failed searches."""
            # Check if this is a failed search to prevent recursive callbacks
            if not radio_response or "✗ Search failed" in radio_response or "no results" in radio_response.lower():
                if os.getenv("AI_IFACE_DEBUG") == "1":
                    print("[AIInterface] Skipping radio callback for failed search to prevent recursion", file=sys.stderr)
                return
            
            if os.getenv("AI_IFACE_DEBUG") == "1":
                print("[AIInterface] Processing radio search results with AI...")
            if self.rag_service:
                self.rag_service.query(radio_response)
        
        # Command interception removed - responses are now handled by MCP servers
        if os.getenv("AI_IFACE_DEBUG") == "1":
            print("[AIInterface] Response processing completed - commands handled by MCP servers")
        
    def handle_rag_error(self, error_message: str):
        """Handle RAG service errors."""
        # Stop loading state
        self.unified_panel.stop_loading()

        # Show error
        self.show_error(f"RAG Error: {error_message}")

        # Focus back to input
        self.unified_panel.focus_input()

    def handle_new_chat(self):
        """Handle new chat creation."""
        # Clear the response display for new chat
        self.unified_panel.clear_response()
        
    def handle_chat_selected(self, chat_id: str):
        """Handle chat selection from history."""
        # The unified panel will handle loading the chat messages

    def setup_rag_service(self):
        """Initialize the RAG service with fast loading and progress updates."""
        self.rag_service = RAGIntegrationService()
        
        # Make sure we receive raw text including <think> blocks for UI rendering
        try:
            self.rag_service.set_hide_think(False)
        except Exception:
            # Backward compatible: if setter not present, set attribute directly
            try:
                self.rag_service.hide_think = False
            except Exception:
                pass
        
        # Connect to initialization progress signal
        self.rag_service.initialization_progress.connect(self.on_rag_progress)
        
        # Start async initialization (no need for separate thread)
        self.rag_service.initialize_async()

    def on_rag_progress(self, progress_message: str):
        """Handle RAG initialization progress updates."""
        if progress_message == "RAG service ready!":
            # RAG is ready now. Clear any "not ready" messages.
            try:
                current_text = self.unified_panel.get_response_text().strip()
                if current_text.startswith("RAG service is not ready"):
                    self.unified_panel.clear_response()
            except Exception:
                pass
            # Ensure input is focused so the user can ask again immediately
            self.unified_panel.focus_input()
        else:
            # Show progress in the response area if it's empty or showing "not ready"
            try:
                current_text = self.unified_panel.get_response_text().strip()
                if not current_text or current_text.startswith("RAG service is not ready") or "Loading" in current_text:
                    self.unified_panel.finish_response(progress_message)
            except Exception:
                pass



    def show_error(self, message: str):
        """Show error message to user."""
        print(f"Error: {message}")  # For now, just print to console
        # Could implement a proper error display widget later

    def show_interface(self):
        """Show the AI interface."""
        self.unified_panel.show()
        # Ensure it is brought to front and receives focus
        self.unified_panel.raise_()
        self.unified_panel.activateWindow()
        self.unified_panel.focus_input()
        self.connect_signals()



    def closeEvent(self, event):
        """Handle application close event."""
        # Clean up RAG service
        if self.rag_service:
            self.rag_service.cleanup_worker()
            # Clean up initialization thread if it exists
            if hasattr(self.rag_service, 'init_thread') and self.rag_service.init_thread and self.rag_service.init_thread.isRunning():
                self.rag_service.init_thread.quit()
                self.rag_service.init_thread.wait()

        # Close all windows
        if self.unified_panel:
            self.unified_panel.close()

        event.accept()


def create_ai_interface_app():
    """Create and configure the AI interface application."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Apply gui_core theme
    apply_theme(app)

    # Create AI interface
    interface = AIInterface()

    return app, interface


if __name__ == "__main__":
    app, interface = create_ai_interface_app()
    interface.show_interface()
    sys.exit(app.exec())