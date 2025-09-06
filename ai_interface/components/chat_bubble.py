from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QFontDatabase, QPainter, QPainterPath
import os


class ChatBubble(QFrame):
    """Individual chat bubble for user or AI messages."""
    
    def __init__(self, message: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the bubble UI."""
        self.setMaximumWidth(400)
        self.setMinimumHeight(40)
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 8)
        layout.setSpacing(0)
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Set font: prefer Mozilla Headline variable font at weight 200 (ExtraLight)
        font_db = QFontDatabase()
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            font_path = os.path.join(base_dir, "gui_core", "utils", "fonts", "Mozilla_Headline", "MozillaHeadline-VariableFont_wdth,wght.ttf")
            if font_path and font_path.endswith(".ttf"):
                font_db.addApplicationFont(font_path)
            # Use loaded family if present; otherwise fallback
            families = QFontDatabase.families()
            preferred_family = "Mozilla Headline" if "Mozilla Headline" in families else (families[0] if families else "Arial")
            font = QFont(preferred_family, 13)
            # Weight 200 ~ ExtraLight
            try:
                font.setWeight(QFont.Weight.ExtraLight)
            except Exception:
                font.setWeight(200)
        except Exception:
            font = QFont("Arial", 13)
            try:
                font.setWeight(QFont.Weight.ExtraLight)
            except Exception:
                font.setWeight(200)
        self.message_label.setFont(font)
        
        layout.addWidget(self.message_label)
        
        # Style based on sender
        if self.is_user:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: rgba(100, 150, 255, 0.2);
                    border: 1px solid rgba(100, 150, 255, 0.3);
                    border-radius: 18px;
                    margin-left: 60px;
                    margin-right: 10px;
                }
                QLabel {
                    color: white;
                    background: transparent;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: rgba(40, 40, 40, 0.8);
                    border: 1px solid rgba(80, 80, 80, 0.6);
                    border-radius: 18px;
                    margin-left: 10px;
                    margin-right: 60px;
                }
                QLabel {
                    color: white;
                    background: transparent;
                    border: none;
                }
            """)


class ChatBubbleContainer(QScrollArea):
    """Container for chat bubbles with scrolling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the container UI."""
        # Main widget and layout
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(8)
        self.content_layout.addStretch()
        
        # Configure scroll area
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Style the scroll area with dark semi-transparent background
        self.setStyleSheet("""
            QScrollArea {
                background-color: rgba(0, 0, 0, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
            QScrollArea > QWidget > QWidget {
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 15px;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
    def add_message(self, message: str, is_user: bool = False):
        """Add a new message bubble."""
        bubble = ChatBubble(message, is_user)
        
        # Create container for alignment
        bubble_container = QWidget()
        bubble_container.setStyleSheet("QWidget { background-color: transparent; }")
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_user:
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
        else:
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch()
            
        # Insert before the stretch
        self.content_layout.insertWidget(self.content_layout.count() - 1, bubble_container)
        
    def clear_messages(self):
        """Clear all messages."""
        # Remove all widgets except the stretch
        while self.content_layout.count() > 1:
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def load_messages(self, messages: list):
        """Load a list of messages."""
        self.clear_messages()
        for msg in messages:
            is_user = msg.get('role') == 'user'
            content = msg.get('content', '')
            self.add_message(content, is_user)
        
        QApplication.processEvents() # Process events to ensure UI updates
        
        # Scroll to bottom after loading all messages
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())