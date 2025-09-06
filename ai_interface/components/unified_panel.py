"""Unified Panel Component

A single panel that combines user input, send button, AI loader, and response display
with smaller, thinner fonts for a simple and flat design.
"""

import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QTextEdit, QScrollArea, QSizePolicy, QFrame, QListWidget, 
    QListWidgetItem, QSplitter, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QFontDatabase, QTextCursor, QTextCharFormat, QColor, QIcon

# Import gui_core components
import sys
gui_core_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gui_core')
if gui_core_path not in sys.path:
    sys.path.insert(0, gui_core_path)

# Add parent directory to path for gui_core import
parent_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Define icons directory relative to repository root
ICONS_DIR = os.path.join(parent_path, 'gui_core', 'utils', 'icons')

# Import AiLoaderBig directly from gui_core
from gui_core.components.ai_loader.widgets import AiLoaderBig

# Import voice mode components
from voice_mode.components.voice_ai_loader import VoiceAiLoader
from voice_mode.voice_manager import VoiceManager

from .blur_widgets import BlurPanel
from .accordion_widget import AccordionWidget

# Import chat manager
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.chat_manager import ChatManager, ChatSession, ChatMessage


class UnifiedLineEdit(QLineEdit):
    """A line edit with smaller, thinner font for the unified panel."""
    
    def __init__(self, placeholder_text: str = "Ask me anything...", parent=None):
        super().__init__(parent)
        self.original_placeholder = placeholder_text
        self.setup_ui(placeholder_text)
        self.load_mozilla_font()
        # Clear placeholder when user starts typing
        self.textChanged.connect(self.on_text_changed)

    def on_text_changed(self, text: str):
        """Clear placeholder when user types anything."""
        if text:
            self.setPlaceholderText("")
        else:
            self.setPlaceholderText(self.original_placeholder)

    def setup_ui(self, placeholder_text: str):
        """Setup the line edit UI with smaller, thinner styling."""
        self.setPlaceholderText(placeholder_text)
        
        # Simple, flat styling with smaller font
        self.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                color: white;
                padding: 12px 16px;
                selection-background-color: rgba(255, 255, 255, 0.3);
                selection-color: black;
                font-family: 'Mozilla Headline', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                font-size: 16px;
                font-weight: 100;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            QLineEdit:focus {
                border: 1px solid rgba(255, 255, 255, 0.4);
                background-color: rgba(255, 255, 255, 0.15);
            }
            QLineEdit:disabled {
                background-color: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.4);
            }
            """
        )
        
        self.setFixedHeight(44)
    
    def load_mozilla_font(self):
        """Load and apply the Mozilla Headline font with thin weight."""
        try:
            font_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'gui_core', 'utils', 'fonts', 'Mozilla_Headline', 'MozillaHeadline-VariableFont_wdth,wght.ttf'
            )
            
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        family = font_families[0]
                        font = QFont(family, 16)
                        font.setWeight(QFont.Weight.Thin)  # Thin weight
                        self.setFont(font)
                        return
            
            # Fallback to system font
            font = QFont("Arial", 16)
            try:
                font.setWeight(QFont.Weight.ExtraLight)
            except Exception:
                font.setWeight(200)
            self.setFont(font)
            
        except Exception as e:
            print(f"Error loading Mozilla font: {e}")
            font = QFont("Arial", 16)
            try:
                font.setWeight(QFont.Weight.ExtraLight)
            except Exception:
                font.setWeight(200)
            self.setFont(font)


class UnifiedTextDisplay(QTextEdit):
    """A text display widget with smaller, thinner font for responses."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_mozilla_font()
        self.current_text = ""
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.show_next_chunk)
        self.text_queue = []
        self.current_chunk_index = 0
        
        # Code block tracking
        self.code_blocks = []
        self.current_code_block = ""
        self.in_code_block = False
        
        # Thinking tag processing
        self.thinking_content = ""
        self.in_thinking_tag = False
        self.processed_text = ""
    
    def setup_ui(self):
        """Setup the text display UI with simple, flat styling."""
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.viewport().setAttribute(Qt.WA_TranslucentBackground)
        
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 100;
                line-height: 1.4;
                padding: 16px;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
            """
        )
        
        self.setReadOnly(True)
        self.setMinimumHeight(200)
    
    def load_mozilla_font(self):
        """Load and apply the Mozilla Headline font with thin weight."""
        try:
            font_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'gui_core', 'utils', 'fonts', 'Mozilla_Headline', 'MozillaHeadline-VariableFont_wdth,wght.ttf'
            )
            
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        family = font_families[0]
                        self.mozilla_font_family = family
                        font = QFont(family, 14)
                        font.setWeight(QFont.Weight.Thin)  # Thin weight
                        self.setFont(font)
                        return
            
            # Fallback to system font
            self.mozilla_font_family = "Arial"
            font = QFont("Arial", 14)
            font.setWeight(QFont.Weight.Thin)
            self.setFont(font)
            
        except Exception as e:
            print(f"Error loading Mozilla font: {e}")
            self.mozilla_font_family = "Arial"
            font = QFont("Arial", 14)
            font.setWeight(QFont.Weight.Thin)
            self.setFont(font)
    
    def _update_display_with_styling(self, text=None):
        """Update display with proper styling for thinking vs regular text."""
        if text is None:
            text = self.current_text
            if self.in_thinking_tag and self.thinking_content:
                text += self.thinking_content
        
        # Clear current content
        self.clear()
        
        # Process text and apply styling
        cursor = self.textCursor()
        
        # Split text by thinking tags
        parts = []
        current_pos = 0
        
        while current_pos < len(text):
            think_start = text.find('<think>', current_pos)
            if think_start == -1:
                # No more thinking tags, add remaining text as regular
                if current_pos < len(text):
                    parts.append(('regular', text[current_pos:]))
                break
            
            # Add text before thinking tag as regular
            if think_start > current_pos:
                parts.append(('regular', text[current_pos:think_start]))
            
            # Find end of thinking tag
            think_end = text.find('</think>', think_start)
            if think_end == -1:
                # Unclosed thinking tag, treat rest as thinking content
                thinking_content = text[think_start + 7:]
                if thinking_content:
                    parts.append(('thinking', thinking_content))
                break
            
            # Add thinking content
            thinking_content = text[think_start + 7:think_end]
            if thinking_content:
                parts.append(('thinking', thinking_content))
            
            current_pos = think_end + 8
        
        # Apply styling to each part
        for part_type, content in parts:
            if not content.strip():
                continue
                
            if part_type == 'thinking':
                # Small default font for thinking content
                char_format = QTextCharFormat()
                char_format.setForeground(QColor(200, 200, 200))  # Slightly dimmed
                default_font = QFont()
                default_font.setPointSize(10)  # Small size
                char_format.setFont(default_font)
            else:
                # Mozilla font with weight 200 for regular content
                 char_format = QTextCharFormat()
                 char_format.setForeground(QColor(255, 255, 255))  # White
                 mozilla_font = QFont(self.mozilla_font_family)
                 mozilla_font.setPointSize(14)
                 mozilla_font.setWeight(QFont.Weight.ExtraLight)  # Equivalent to weight 200
                 char_format.setFont(mozilla_font)
            
            cursor.insertText(content, char_format)
        
        # Move cursor to end
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
    
    def add_text_chunk(self, chunk: str):
        """Add a chunk of text with streaming effect, processing thinking tags inline."""
        if chunk.strip():
            # Process chunk character by character for proper streaming
            for char in chunk:
                if not self.in_thinking_tag:
                    # Check if we're starting a thinking tag
                    self.current_text += char
                    if self.current_text.endswith('<think>'):
                        # Remove the <think> tag from current text
                        self.current_text = self.current_text[:-7]
                        self.in_thinking_tag = True
                        self.thinking_content = ""
                        # Immediately create a closed think tag in current_text for display
                        self.current_text += "<think></think>"
                        # Update display to show the closed tag
                        self._update_display_with_styling()
                    else:
                        # Regular text - update main display
                        self._update_display_with_styling()
                else:
                    # We're inside a thinking tag
                    self.thinking_content += char
                    if self.thinking_content.endswith('</think>'):
                        # Remove the closing tag and finalize thinking content
                        final_content = self.thinking_content[:-8]
                        if final_content.strip():
                            # Replace the empty think tag with content-filled one
                            self.current_text = self.current_text.replace("<think></think>", f"<think>{final_content.strip()}</think>")
                        else:
                            # Remove empty think tag if no content
                            self.current_text = self.current_text.replace("<think></think>", "")
                        
                        self.in_thinking_tag = False
                        self.thinking_content = ""
                        # Update display with final content
                        self._update_display_with_styling()
                    else:
                        # Stream thinking content by updating the placeholder
                        if self.thinking_content and not self.thinking_content.endswith('</think>'):
                            # Update display with current thinking content in the placeholder
                            temp_text = self.current_text.replace("<think></think>", f"<think>{self.thinking_content}</think>")
                            self._update_display_with_styling(temp_text)
            
            # Auto-scroll to bottom
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
            

    
    def set_complete_text(self, text: str):
        """Set the complete text immediately, processing thinking tags inline."""
        self.current_text = text
        
        # Process all code blocks in the complete text
        self._process_complete_text(text)
        
        # Update display with styled text
        self._update_display_with_styling(text)
        
        # Auto-scroll to bottom
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        

    
    def clear_text(self):
        """Clear all text and reset state."""
        self.clear()
        self.code_blocks = []
        self.thinking_content = ""
        self.in_thinking_tag = False
        self.current_text = ""
    
    def show_next_chunk(self):
        """Show the next chunk of text with typing animation."""
        # This method is called by the typing timer but we handle text display
        # differently in this unified implementation, so we can leave it empty
        # or implement custom logic if needed
        pass
    

    







    def _process_code_blocks(self, chunk: str):
        """Process incoming text chunks to detect code blocks."""
        lines = chunk.split('\n')
        
        for line in lines:
            if line.strip().startswith('```'):
                if not self.in_code_block:
                    # Starting a new code block
                    self.in_code_block = True
                    self.current_code_block = ""
                    # Extract language from ```python, ```javascript, etc.
                    lang_match = re.match(r'```(\w+)', line.strip())
                    self.current_language = lang_match.group(1) if lang_match else "text"
                else:
                    # Ending current code block
                    self.in_code_block = False
                    if self.current_code_block.strip():
                        self.code_blocks.append({
                            'code': self.current_code_block.strip(),
                            'language': getattr(self, 'current_language', 'text')
                        })
                    self.current_code_block = ""
            elif self.in_code_block:
                self.current_code_block += line + "\n"
    
    def _process_complete_text(self, text: str):
        """Process complete text to extract all code blocks."""
        self.code_blocks = []
        self.in_code_block = False
        self.current_code_block = ""
        
        # Find all code blocks using regex
        code_pattern = r'```(\w+)?\n([\s\S]*?)```'
        matches = re.finditer(code_pattern, text)
        
        for match in matches:
            language = match.group(1) if match.group(1) else "text"
            code = match.group(2).strip()
            if code:
                self.code_blocks.append({
                    'code': code,
                    'language': language
                })
    



class UnifiedPanel(QWidget):
    """Unified panel with input, send button, AI loader, response display, and chat management."""
    
    query_submitted = Signal(str)  # Signal when user submits a query
    new_chat_requested = Signal()  # Signal when user requests new chat
    chat_selected = Signal(str)  # Signal when user selects a chat (session_id)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Initialize chat manager
        self.chat_manager = ChatManager()
        
        # Initialize RAG service (placeholder - replace with actual service)
        from services.rag_integration import RAGIntegrationService
        self.rag_service = RAGIntegrationService()
        
        # Initialize voice manager
        self.voice_manager = VoiceManager(self.chat_manager, self.rag_service, parent=self)
        self.voice_manager.set_parent_widget(self)
        
        self.setup_components()
        self.connect_signals()
        self.is_streaming = False
        self.show_chat_history = False
        self._current_response = ""
        
        # Load existing chats
        self.refresh_chat_list()
    
    def setup_components(self):
        """Setup the unified panel components."""
        # Main layout with transparent background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main splitter for chat history and main chat
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.1);
                width: 2px;
            }
            """
        )
        
        # Chat history panel (initially hidden)
        self.setup_chat_history_panel()
        
        # Main chat bubble container
        self.bubble_container = QWidget()
        self.bubble_container.setObjectName("bubbleContainer")
        
        # Bubble layout
        bubble_layout = QVBoxLayout(self.bubble_container)
        bubble_layout.setContentsMargins(20, 20, 20, 20)
        bubble_layout.setSpacing(16)
        
        # Top bar with new chat button and chat history toggle
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setSpacing(8)
        
        # New chat button with plus icon
        self.new_chat_button = QPushButton()
        self.new_chat_button.setFixedSize(32, 32)
        plus_icon = QIcon(os.path.join(ICONS_DIR, "plus.svg"))
        self.new_chat_button.setIcon(plus_icon)
        self.new_chat_button.setIconSize(QSize(16, 16))
        self.new_chat_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
            """
        )
        top_bar_layout.addWidget(self.new_chat_button)
        
        # Chat history toggle button with menu icon
        self.history_toggle_button = QPushButton()
        self.history_toggle_button.setFixedSize(32, 32)
        menu_icon = QIcon(os.path.join(ICONS_DIR, "menu.svg"))
        self.history_toggle_button.setIcon(menu_icon)
        self.history_toggle_button.setIconSize(QSize(16, 16))
        self.history_toggle_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
            """
        )
        top_bar_layout.addWidget(self.history_toggle_button)
        
        top_bar_layout.addStretch()
        bubble_layout.addLayout(top_bar_layout)
        
        # Response display area - using chat bubble container
        from .chat_bubble import ChatBubbleContainer
        self.response_display = ChatBubbleContainer()
        bubble_layout.addWidget(self.response_display, 1)
        
        # Input section at the bottom
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        
        # Voice-enabled AI loader (smaller size)
        self.ai_loader = VoiceAiLoader(animated=False, active=True, parent=self)
        self.ai_loader.setFixedSize(32, 32)
        # Ensure transparent background to prevent grey square appearance
        self.ai_loader.setStyleSheet("background-color: transparent; border: none;")
        # Connect voice mode toggle signal
        self.ai_loader.voice_mode_toggle_requested.connect(self.toggle_voice_mode)
        input_layout.addWidget(self.ai_loader, 0, Qt.AlignVCenter)
        
        # Text input
        self.text_input = UnifiedLineEdit("Ask me anything...")
        self.text_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.text_input, 1)
        
        # Send button with send icon
        self.send_button = QPushButton()
        self.send_button.setFixedSize(44, 44)
        send_icon = QIcon(os.path.join(ICONS_DIR, "send.svg"))
        self.send_button.setIcon(send_icon)
        self.send_button.setIconSize(QSize(18, 18))
        self.send_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.35);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            """
        )
        input_layout.addWidget(self.send_button, 0, Qt.AlignVCenter)
        
        bubble_layout.addLayout(input_layout)
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.chat_history_panel)
        self.main_splitter.addWidget(self.bubble_container)
        
        # Set splitter proportions (history panel hidden initially)
        self.main_splitter.setSizes([0, 800])
        self.chat_history_panel.hide()
        
        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)
        
        # Panel styling - transparent main panel with bubble container
        self.setStyleSheet(
            """
            UnifiedPanel {
                background-color: transparent;
                color: white;
                font-family: 'SF Pro Display', 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QWidget#bubbleContainer {
                background-color: rgba(0, 0, 0, 230);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
                color: white;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px;
                color: white;
            }
            QPushButton {
                background-color: rgba(70, 130, 180, 0.8);
                border: none;
                border-radius: 20px;
                width: 40px;
                height: 40px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
                padding: 0px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 1.0);
            }
            QPushButton:pressed {
                background-color: rgba(50, 110, 160, 1.0);
            }
            """
        )
    
    def setup_chat_history_panel(self):
        """Setup the chat history panel."""
        self.chat_history_panel = QWidget()
        self.chat_history_panel.setObjectName("chatHistoryPanel")
        self.chat_history_panel.setFixedWidth(250)
        
        history_layout = QVBoxLayout(self.chat_history_panel)
        history_layout.setContentsMargins(15, 15, 15, 15)
        history_layout.setSpacing(10)
        
        # Chat history title
        history_title = QLabel("Chat History")
        history_title.setStyleSheet(
            """
            QLabel {
                color: white;
                font-family: 'Mozilla Headline', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                font-size: 16px;
                font-weight: 200;
                margin-bottom: 10px;
            }
            """
        )
        history_layout.addWidget(history_title)
        
        # Chat list
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
                font-family: 'Mozilla Headline', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                font-size: 12px;
                font-weight: 100;
                padding: 5px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
                margin: 2px 0px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(255, 255, 255, 0.2);
            }
            """
        )
        history_layout.addWidget(self.chat_list, 1)
        
        # Apply panel styling
        self.chat_history_panel.setStyleSheet(
            """
            QWidget#chatHistoryPanel {
                background-color: rgba(0, 0, 0, 200);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            """
        )
    
    def connect_signals(self):
        """Connect component signals."""
        self.text_input.returnPressed.connect(self.handle_query_submit)
        self.send_button.clicked.connect(self.handle_query_submit)
        self.new_chat_button.clicked.connect(self.handle_new_chat)
        self.history_toggle_button.clicked.connect(self.toggle_chat_history)
        self.chat_list.itemClicked.connect(self.handle_chat_selection)
    
    def handle_query_submit(self):
        """Handle when user submits a query."""
        query = self.text_input.text().strip()
        if query and not self.is_streaming:
            # Add user message to current chat
            if not self.chat_manager.current_session:
                self.chat_manager.create_new_chat()
                self.refresh_chat_list()
            
            # Add user message bubble
            self.response_display.add_message(query, is_user=True)
            
            self.chat_manager.add_message('user', query)
            self.query_submitted.emit(query)
            self.text_input.clear()
    
    def handle_new_chat(self):
        """Handle new chat button click."""
        self.chat_manager.create_new_chat()
        self.clear_response()
        self.refresh_chat_list()
        self.new_chat_requested.emit()
        self.focus_input()
    
    def handle_chat_selection(self, item):
        """Handle chat selection from history."""
        session_id = item.data(Qt.UserRole)
        if session_id:
            session = self.chat_manager.get_session(session_id)
            if session:
                self.chat_manager.set_current_session(session_id)
                self.load_chat_messages(session)
                self.chat_selected.emit(session_id)
    
    def toggle_chat_history(self):
        """Toggle chat history panel visibility."""
        self.show_chat_history = not self.show_chat_history
        
        if self.show_chat_history:
            self.chat_history_panel.show()
            self.main_splitter.setSizes([250, 550])
            close_icon = QIcon(os.path.join(ICONS_DIR, "xmark.svg"))
            self.history_toggle_button.setIcon(close_icon)
        else:
            self.chat_history_panel.hide()
            self.main_splitter.setSizes([0, 800])
            menu_icon = QIcon(os.path.join(ICONS_DIR, "menu.svg"))
            self.history_toggle_button.setIcon(menu_icon)
    
    def refresh_chat_list(self):
        """Refresh the chat history list."""
        self.chat_list.clear()
        sessions = self.chat_manager.list_sessions()
        
        for session_info in sessions:
            item = QListWidgetItem()
            item.setText(session_info['title'])
            item.setData(Qt.UserRole, session_info['session_id'])
            item.setToolTip(f"Created: {session_info['created_at'][:16]}\nMessages: {session_info['message_count']}")
            self.chat_list.addItem(item)
    
    def load_chat_messages(self, session: ChatSession):
        """Load and display messages from a chat session."""
        messages_data = [{'role': msg.role, 'content': msg.content} for msg in session.messages]
        self.response_display.load_messages(messages_data)
        
        # Force UI update
        self.response_display.update()
        self.response_display.repaint()
    
    def get_current_chat_context(self) -> list:
        """Get the current chat context for AI processing."""
        if self.chat_manager.current_session:
            return self.chat_manager.get_conversation_context()
        return []
    
    def toggle_voice_mode(self):
        """Toggle between voice mode and normal interface."""
        print(f"[VOICE MODE DEBUG] toggle_voice_mode called")
        try:
            if self.voice_manager.is_voice_mode_active:
                print(f"[VOICE MODE DEBUG] Voice mode is active, stopping...")
                self.stop_voice_mode()
            else:
                print(f"[VOICE MODE DEBUG] Voice mode is inactive, starting...")
                self.start_voice_mode()
        except Exception as e:
            print(f"[VOICE MODE DEBUG] Error toggling voice mode: {e}")
            import traceback
            traceback.print_exc()
    
    def start_voice_mode(self):
        """Start voice mode when AI loader is double-clicked."""
        print(f"[VOICE MODE DEBUG] start_voice_mode called")
        try:
            print(f"[VOICE MODE DEBUG] Calling voice_manager.start_voice_mode()")
            self.voice_manager.start_voice_mode()
            print(f"[VOICE MODE DEBUG] Voice manager started, updating AI loader visual state")
            # Update AI loader visual state
            self.ai_loader.set_voice_mode_active(True)
            print(f"[VOICE MODE DEBUG] Voice mode started successfully")
        except Exception as e:
            print(f"[VOICE MODE DEBUG] Error starting voice mode: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_voice_mode(self):
        """Stop voice mode and return to normal interface."""
        print(f"[VOICE MODE DEBUG] stop_voice_mode called")
        try:
            self.voice_manager.stop_voice_mode()
            # Update AI loader visual state
            self.ai_loader.set_voice_mode_active(False)
            print(f"[VOICE MODE DEBUG] Voice mode stopped successfully")
        except Exception as e:
            print(f"[VOICE MODE DEBUG] Error stopping voice mode: {e}")
            import traceback
            traceback.print_exc()
    
    def is_voice_mode_available(self) -> bool:
        """Check if voice mode is available."""
        return self.voice_manager.is_voice_mode_available()
    
    def start_loading(self):
        """Start the AI loader animation and disable input."""
        self.ai_loader.start()
        self.text_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.text_input.setPlaceholderText("AI is thinking...")
        self.is_streaming = True
    
    def stop_loading(self):
        """Stop the AI loader animation and enable input."""
        self.ai_loader.stop()
        self.text_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.text_input.setPlaceholderText("Ask me anything...")
        self.is_streaming = False
    
    def start_response(self):
        """Start a new response stream."""
        self._current_response = ""  # visible (non-think) text only
        self._streaming_bubble = None
        self._inside_think = False
        self._think_buffer = ""
        self._current_think_accordion = None
        
        # Create a new streaming bubble for AI response
        from .chat_bubble import ChatBubble
        self._streaming_bubble = ChatBubble("", is_user=False)
        
        # Create container for alignment
        bubble_container = QWidget()
        bubble_container.setStyleSheet("QWidget { background-color: transparent; }")
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addWidget(self._streaming_bubble)
        bubble_layout.addStretch()
        
        # Insert before the stretch in response display
        self.response_display.content_layout.insertWidget(
            self.response_display.content_layout.count() - 1, bubble_container
        )
        
    def _create_think_accordion(self, title: str = "Thinking") -> AccordionWidget:
        """Create and insert a new accordion above the current AI response bubble."""
        accordion = AccordionWidget(title=title)
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: transparent; margin-bottom: 5px; }")
        lay = QHBoxLayout(container)
        lay.setContentsMargins(10, 0, 60, 0)  # Match bubble alignment with 5px spacing
        lay.addWidget(accordion)
        lay.addStretch()
        
        # Find the position of the current streaming bubble and insert accordion above it
        if self._streaming_bubble:
            bubble_parent = self._streaming_bubble.parent()
            if bubble_parent:
                # Find the index of the bubble container in the layout
                layout = self.response_display.content_layout
                for i in range(layout.count()):
                    if layout.itemAt(i).widget() == bubble_parent:
                        # Insert accordion just before the bubble
                        layout.insertWidget(i, container)
                        return accordion
        
        # Fallback: insert before the stretch
        self.response_display.content_layout.insertWidget(
            self.response_display.content_layout.count() - 1, container
        )
        return accordion
        
    def add_response_chunk(self, chunk: str):
        """Add a chunk to the response stream, routing <think> content to accordions."""
        if not chunk:
            return
        for ch in chunk:
            if not self._inside_think:
                # Append and watch for opening tag
                self._current_response += ch
                if self._current_response.endswith('<think>'):
                    # Remove the tag from visible text and switch mode
                    self._current_response = self._current_response[:-7]
                    if self._streaming_bubble:
                        self._streaming_bubble.message_label.setText(self._current_response)
                    self._inside_think = True
                    self._think_buffer = ""
                    # Create a new accordion for this think block
                    self._current_think_accordion = self._create_think_accordion("Thinking")
                else:
                    if self._streaming_bubble:
                        self._streaming_bubble.message_label.setText(self._current_response)
            else:
                # Inside a think block; stream into accordion
                self._think_buffer += ch
                if self._think_buffer.endswith('</think>'):
                    # Finalize this think block (strip closing tag)
                    content = self._think_buffer[:-8]
                    if self._current_think_accordion:
                        if content:
                            # Set full content once stabilized
                            self._current_think_accordion.set_content(content)
                    # Reset state
                    self._inside_think = False
                    self._think_buffer = ""
                    self._current_think_accordion = None
                else:
                    # Append progressively to current accordion
                    if self._current_think_accordion:
                        self._current_think_accordion.append_content(ch)
        
        # Auto-scroll to bottom to show new content
        QTimer.singleShot(10, lambda: self.response_display.verticalScrollBar().setValue(
            self.response_display.verticalScrollBar().maximum()
        ))
        
    def finish_response(self, complete_text: str = None):
        """Finish the response stream."""
        if complete_text:
            # Strip think content from complete_text if provided
            import re
            final_text = re.sub(r'<think>.*?</think>', '', complete_text, flags=re.DOTALL)
        else:
            final_text = self._current_response
        
        if final_text:
            # Update the streaming bubble with final content
            if self._streaming_bubble:
                self._streaming_bubble.message_label.setText(final_text)
            
            # Filter out process messages before saving to chat
            filtered_text = self._filter_process_messages(final_text)
            
            # Save AI response to current chat
            if self.chat_manager.current_session and filtered_text:
                self.chat_manager.add_message('assistant', filtered_text)
                self.refresh_chat_list()  # Update chat list with new message count
        
        # Clean up streaming state
        self._current_response = ""
        self._streaming_bubble = None
    
    def _filter_process_messages(self, text: str) -> str:
        """Filter out process messages from the response text."""
        lines = text.split('\n')
        filtered_lines = []
        response_started = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip process messages
            if (line_stripped.startswith("Loading index for querying...") or
                line_stripped.startswith("Query: ") or
                line_stripped.startswith("Asking LLM...")):
                continue
            
            # Start capturing after "Response:" marker
            if line_stripped == "Response:":
                response_started = True
                continue
            
            # If we haven't seen "Response:" marker, capture everything
            # (for cases where there's no explicit marker)
            if not response_started and not any(line_stripped.startswith(prefix) for prefix in 
                ["Loading index for querying...", "Query: ", "Asking LLM..."]):
                response_started = True
            
            if response_started:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines).strip()
        
    def clear_response(self):
        """Clear the response display."""
        self.response_display.clear_messages()
    
    def focus_input(self):
        """Set focus to the input field."""
        self.activateWindow()
        self.raise_()
        self.text_input.setFocus()
    
    def get_query_text(self) -> str:
        """Get the current text in the input field."""
        return self.text_input.text()
    
    def get_response_text(self) -> str:
        """Get the current response text."""
        return self.response_display.toPlainText()
