"""Voice-enabled AI Loader Component

Extends the standard AI loader with double-click functionality to trigger voice mode.
"""

import os
import sys
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

# Import gui_core components
gui_core_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'gui_core')
if gui_core_path not in sys.path:
    sys.path.insert(0, gui_core_path)

from gui_core.components.ai_loader.widgets import AiLoaderBig


class VoiceAiLoader(AiLoaderBig):
    """AI Loader with double-click functionality for voice mode activation."""
    
    # Signals
    voice_mode_requested = Signal()  # Emitted on double-click
    voice_mode_toggle_requested = Signal()  # Emitted on double-click for toggle
    
    def __init__(self, animated: bool = False, active: bool = True, parent=None):
        super().__init__(animated=animated, active=active, parent=parent)
        
        # Double-click detection
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._on_single_click_timeout)
        self._click_count = 0
        self._double_click_interval = 400  # milliseconds
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Visual feedback state
        self._is_hovered = False
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for click detection."""
        if event.button() == event.button().LeftButton:
            self._click_count += 1
            
            if self._click_count == 1:
                # Start timer for single click detection
                self._click_timer.start(self._double_click_interval)
            elif self._click_count == 2:
                # Double-click detected
                self._click_timer.stop()
                self._click_count = 0
                self._on_double_click()
        
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double-click events (Qt's built-in detection)."""
        if event.button() == event.button().LeftButton:
            self._click_timer.stop()
            self._click_count = 0
            self._on_double_click()
        
        super().mouseDoubleClickEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter for visual feedback."""
        self._is_hovered = True
        self._update_hover_state()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave for visual feedback."""
        self._is_hovered = False
        self._update_hover_state()
        super().leaveEvent(event)
    
    def _on_single_click_timeout(self):
        """Handle single click timeout (no double-click detected)."""
        if self._click_count == 1:
            self._on_single_click()
        self._click_count = 0
    
    def _on_single_click(self):
        """Handle single click action."""
        # Single click could be used for other functionality if needed
        # For now, we don't do anything special on single click
        pass
    
    def _on_double_click(self):
        """Handle double-click action - toggle voice mode."""
        print("Voice mode toggle requested via double-click")  # Debug
        self.voice_mode_toggle_requested.emit()
    
    def _update_hover_state(self):
        """Update visual state based on hover."""
        if self._is_hovered:
            # Slightly increase activity when hovered
            self.setActive(True)
            # Could add visual feedback here if needed
        else:
            # Return to normal state
            pass
    
    def set_voice_mode_active(self, active: bool):
        """Set visual state to indicate voice mode is active."""
        if active:
            # Make loader more active/animated when voice mode is on
            self.setActive(True)
            self.start()
        else:
            # Return to normal state
            self.setActive(False)
            self.stop()
    
    def pulse_for_voice_activity(self):
        """Create a visual pulse effect for voice activity."""
        # Temporarily increase activity
        self.setActive(True)
        
        # Reset after a short delay
        QTimer.singleShot(500, lambda: self.setActive(False))