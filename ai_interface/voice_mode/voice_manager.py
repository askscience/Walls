"""Voice Mode Manager

Coordinates voice recognition, TTS, chat integration, and UI management.
"""

import os
import sys
from typing import Optional
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QWidget

# Add current directory to path for voice_mode imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import voice components
from voice_mode.components.voice_ui import VoiceUI
from voice_mode.services.vosk_service import VoskService
from voice_mode.services.kokoro_service import KokoroService
from voice_mode.utils.audio_utils import AudioUtils

# Import chat manager and RAG service
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.chat_manager import ChatManager, ChatMessage
from services.rag_integration import RAGIntegrationService


class VoiceManager(QObject):
    """Manages voice mode functionality and coordinates all voice components."""
    
    # Signals
    voice_mode_started = Signal()
    voice_mode_stopped = Signal()
    ai_response_ready = Signal(str)  # AI response text ready for TTS
    error_occurred = Signal(str)  # Error message
    
    def __init__(self, chat_manager: ChatManager, rag_service: RAGIntegrationService, parent=None):
        super().__init__(parent)
        
        # Core services
        self.chat_manager = chat_manager
        self.rag_service = rag_service
        
        # Voice components
        self.voice_ui: Optional[VoiceUI] = None
        self.vosk_service: Optional[VoskService] = None
        self.kokoro_service: Optional[KokoroService] = None
        self.audio_utils: Optional[AudioUtils] = None
        
        # State
        self.is_voice_mode_active = False
        self.is_processing_request = False
        
        # Parent widget reference for UI management
        self.parent_widget: Optional[QWidget] = None
    
    def set_parent_widget(self, parent_widget: QWidget):
        """Set the parent widget for UI management."""
        self.parent_widget = parent_widget
    
    def start_voice_mode(self):
        """Start voice mode - initialize components and show voice UI."""
        print(f"[VOICE MANAGER DEBUG] start_voice_mode called, is_voice_mode_active: {self.is_voice_mode_active}")
        if self.is_voice_mode_active:
            print(f"[VOICE MANAGER DEBUG] Voice mode already active, returning")
            return
        
        try:
            print(f"[VOICE MANAGER DEBUG] Initializing VoiceUI...")
            # Initialize voice UI
            self.voice_ui = VoiceUI(self.chat_manager, self.rag_service, parent=self.parent_widget)
            print(f"[VOICE MANAGER DEBUG] VoiceUI initialized successfully")
            
            # Connect voice UI signals
            print(f"[VOICE MANAGER DEBUG] Connecting voice UI signals...")
            self.voice_ui.voice_mode_exit_requested.connect(self.stop_voice_mode)
            self.voice_ui.text_input_received.connect(self.process_voice_input)
            print(f"[VOICE MANAGER DEBUG] Voice UI signals connected")
            
            # Show voice UI and hide parent content
            if self.parent_widget:
                print(f"[VOICE MANAGER DEBUG] Parent widget exists, hiding parent content...")
                # Hide all parent widget content
                self._hide_parent_content()
                
                # Show voice UI in fullscreen overlay
                print(f"[VOICE MANAGER DEBUG] Setting up voice UI overlay...")
                self.voice_ui.setParent(self.parent_widget)
                self.voice_ui.resize(self.parent_widget.size())
                self.voice_ui.show()
                self.voice_ui.raise_()
                print(f"[VOICE MANAGER DEBUG] Voice UI overlay displayed")
            else:
                print(f"[VOICE MANAGER DEBUG] No parent widget available")
            
            self.is_voice_mode_active = True
            print(f"[VOICE MANAGER DEBUG] Emitting voice_mode_started signal")
            self.voice_mode_started.emit()
            
            print(f"[VOICE MANAGER DEBUG] Voice mode started successfully")
            
        except Exception as e:
            error_msg = f"Failed to start voice mode: {str(e)}"
            print(f"[VOICE MANAGER DEBUG] Error starting voice mode: {error_msg}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
    
    def stop_voice_mode(self):
        """Stop voice mode and return to normal interface."""
        if not self.is_voice_mode_active:
            return
        
        try:
            # Clean up voice UI - properly stop all voice services first
            if self.voice_ui:
                # Call exit_voice_mode to properly stop VOSK service and other components
                self.voice_ui.stop_listening()
                self.voice_ui.kokoro_service.stop_generation()
                self.voice_ui.audio_utils.stop_playback()
                
                # Now hide and delete the UI
                self.voice_ui.hide()
                self.voice_ui.deleteLater()
                self.voice_ui = None
            
            # Restore parent widget content
            if self.parent_widget:
                self._show_parent_content()
            
            self.is_voice_mode_active = False
            self.is_processing_request = False
            self.voice_mode_stopped.emit()
            
            print("Voice mode stopped - VOSK service and all components properly terminated")
            
        except Exception as e:
            error_msg = f"Error stopping voice mode: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
    
    def process_voice_input(self, user_text: str):
        """Process voice input from the user."""
        if self.is_processing_request:
            return
        
        self.is_processing_request = True
        
        try:
            # Add user message to current chat session
            if not self.chat_manager.current_session:
                # Create new session if none exists
                self.chat_manager.create_new_session()
            
            # Add user message
            user_message = ChatMessage(
                role="user",
                content=user_text
            )
            self.chat_manager.add_message_to_current_session(user_message)
            
            # Get conversation context for AI processing
            context = self.chat_manager.get_conversation_context()
            
            # Process with RAG service (simulate AI processing)
            # In a real implementation, this would call your AI service
            self._simulate_ai_processing(user_text, context)
            
        except Exception as e:
            error_msg = f"Error processing voice input: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            self.is_processing_request = False
    
    def _simulate_ai_processing(self, user_text: str, context: list):
        """Simulate AI processing (replace with actual AI service call)."""
        # This is a placeholder - replace with actual AI service integration
        # For now, create a simple response
        
        def generate_response():
            try:
                # Simple response generation (replace with actual AI call)
                response_text = f"I heard you say: '{user_text}'. This is a simulated AI response in voice mode."
                
                # Add AI response to chat session
                ai_message = ChatMessage(
                    role="assistant",
                    content=response_text
                )
                self.chat_manager.add_message_to_current_session(ai_message)
                
                # Send response to voice UI for TTS
                if self.voice_ui:
                    self.voice_ui.on_ai_response_ready(response_text)
                
                self.ai_response_ready.emit(response_text)
                self.is_processing_request = False
                
            except Exception as e:
                error_msg = f"Error generating AI response: {str(e)}"
                print(error_msg)
                self.error_occurred.emit(error_msg)
                self.is_processing_request = False
        
        # Simulate processing delay
        QTimer.singleShot(1000, generate_response)
    
    def _hide_parent_content(self):
        """Hide parent widget content when entering voice mode."""
        if self.parent_widget:
            # Hide all child widgets except the voice UI
            for child in self.parent_widget.findChildren(QWidget):
                if child != self.voice_ui and child.parent() == self.parent_widget:
                    child.hide()
    
    def _show_parent_content(self):
        """Show parent widget content when exiting voice mode."""
        if self.parent_widget:
            # Show all child widgets
            for child in self.parent_widget.findChildren(QWidget):
                if child != self.voice_ui and child.parent() == self.parent_widget:
                    child.show()
    
    def is_voice_mode_available(self) -> bool:
        """Check if voice mode is available (all dependencies installed)."""
        try:
            # Check Vosk availability
            import vosk
            
            # Check PyAudio availability
            import pyaudio
            
            # Check if Kokoro is available (this would need actual Kokoro check)
            # For now, assume it's available
            
            return True
            
        except ImportError as e:
            print(f"Voice mode not available: {e}")
            return False
    
    def get_voice_mode_status(self) -> dict:
        """Get current voice mode status information."""
        return {
            "active": self.is_voice_mode_active,
            "processing": self.is_processing_request,
            "available": self.is_voice_mode_available(),
            "current_session": self.chat_manager.current_session.session_id if self.chat_manager.current_session else None
        }