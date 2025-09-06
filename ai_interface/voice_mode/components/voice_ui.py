"""Voice Mode UI Component

UI component for voice interaction mode that displays only the AI loader.
"""

import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QFontDatabase, QColor, QPalette

# Import gui_core components
gui_core_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'gui_core')
if gui_core_path not in sys.path:
    sys.path.insert(0, gui_core_path)

# Import voice services
from voice_mode.services.vosk_service import VoskService
from voice_mode.services.kokoro_service import KokoroService
from voice_mode.utils.audio_utils import AudioUtils

# Import chat manager and command execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.chat_manager import ChatManager
from services.rag_integration import RAGIntegrationService
# Import centralized command interception from RAG to avoid duplication
# Command interception functionality removed - now using MCP servers



class VoiceStatusLabel(QLabel):
    """Status label for voice mode with Mozilla font."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setup_ui()
        self.load_mozilla_font()
    
    def setup_ui(self):
        """Setup the label UI."""
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            """
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                background-color: transparent;
                font-family: 'Mozilla Headline', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                font-size: 18px;
                font-weight: 200;
                padding: 10px;
            }
            """
        )
    
    def load_mozilla_font(self):
        """Load Mozilla Headline font."""
        try:
            font_path = os.path.join(gui_core_path, "utils", "fonts", "MozillaHeadline-Regular.ttf")
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    font = QFont(font_family, 18, QFont.Weight.Light)
                    self.setFont(font)
        except Exception as e:
            print(f"Could not load Mozilla font: {e}")


class VoiceUI(QWidget):
    """Voice mode UI that shows only AI loader and status during voice interaction."""
    
    # Signals
    voice_mode_exit_requested = Signal()
    text_input_received = Signal(str)  # When user speaks
    
    def __init__(self, chat_manager: ChatManager, rag_service: RAGIntegrationService, parent=None):
        super().__init__(parent)
        self.chat_manager = chat_manager
        self.rag_service = rag_service
        
        # Load voice configuration
        self.config = self.load_voice_config()
        
        # Get model name from config
        model_name = self.config.get('recognition', {}).get('model_name')
        
        # Initialize services
        self.vosk_service = VoskService(model_name=model_name, wake_word_mode=True, parent=self)
        self.kokoro_service = KokoroService(parent=self)
        self.audio_utils = AudioUtils(parent=self)
        
        # State
        self.is_listening = False
        self.is_processing = False
        self.is_speaking = False
        self._pending_command = None  # Store command to retry when RAG is ready
        
        # UI setup
        self.setup_ui()
        self.setup_connections()
        
        # Auto-start listening when voice mode is activated
        QTimer.singleShot(500, self.start_listening)
    
    def load_voice_config(self):
        """Load voice configuration from config file."""
        import json
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "voice_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading voice config: {e}")
        
        # Return default config if loading fails
        return {
            'recognition': {
                'model_name': None
            }
        }
    
    def setup_ui(self):
        """Setup the voice mode UI."""
        self.setWindowTitle("Voice Mode")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Main layout - position container in bottom left
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 0, 0, 20)
        main_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        
        # Voice container - smaller, more black translucent rectangle
        self.voice_container = QFrame()
        self.voice_container.setFixedSize(280, 120)
        self.voice_container.setStyleSheet(
            """
            QFrame {
                background-color: rgba(10, 10, 10, 0.9);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            """
        )
        
        # Container layout - center everything
        container_layout = QHBoxLayout(self.voice_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(30)
        container_layout.setAlignment(Qt.AlignCenter)
        
        # Left side - AI Loader
        loader_widget = QWidget()
        loader_widget.setStyleSheet("background: transparent;")
        loader_layout = QVBoxLayout(loader_widget)
        loader_layout.setAlignment(Qt.AlignCenter)
        loader_layout.setSpacing(10)
        
        # Use VoiceAiLoader for double-click functionality
        from .voice_ai_loader import VoiceAiLoader
        self.ai_loader = VoiceAiLoader(animated=True, parent=self)
        self.ai_loader.setFixedSize(60, 60)
        # Remove any background styling from AI loader
        self.ai_loader.setStyleSheet("background: transparent; border: none;")
        # Connect double-click to exit voice mode
        self.ai_loader.voice_mode_toggle_requested.connect(self.exit_voice_mode)
        loader_layout.addWidget(self.ai_loader, alignment=Qt.AlignCenter)
        
        # Remove status label completely - no text needed
        
        container_layout.addWidget(loader_widget)
        
        # Right side - Soundwave visualization
        from .soundwave_widget import SoundwaveWidget
        self.soundwave_widget = SoundwaveWidget(self)
        container_layout.addWidget(self.soundwave_widget, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(self.voice_container)
        
        # Instructions label (hidden by default, shown when needed)
        self.instructions_label = VoiceStatusLabel("", self)
        self.instructions_label.setStyleSheet(
            """
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                background-color: transparent;
                font-family: 'Mozilla Headline', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                font-size: 12px;
                font-weight: 200;
                padding: 10px;
            }
            """
        )
        self.instructions_label.hide()
        main_layout.addWidget(self.instructions_label, alignment=Qt.AlignCenter)
        
        # Exit button (initially hidden)
        self.exit_button = QPushButton("Exit Voice Mode")
        self.exit_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                font-family: 'Mozilla Headline', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                font-size: 14px;
                font-weight: 200;
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
        self.exit_button.clicked.connect(self.exit_voice_mode)
        self.exit_button.hide()
        main_layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)
        
        # Set transparent background for main widget
        self.setStyleSheet(
            """
            VoiceUI {
                background-color: transparent;
            }
            """
        )
    
    def setup_connections(self):
        """Setup signal connections for voice services."""
        # Vosk service connections
        self.vosk_service.text_recognized.connect(self.on_text_recognized)
        self.vosk_service.wake_word_detected.connect(self.on_wake_word_detected)
        self.vosk_service.error_occurred.connect(self.on_vosk_error)
        self.vosk_service.recognition_started.connect(self.on_recognition_started)
        self.vosk_service.recognition_stopped.connect(self.on_recognition_stopped)
        
        # Kokoro service connections
        self.kokoro_service.audio_generated.connect(self.on_audio_generated)
        self.kokoro_service.error_occurred.connect(self.on_kokoro_error)
        self.kokoro_service.generation_started.connect(self.on_tts_started)
        self.kokoro_service.generation_finished.connect(self.on_tts_finished)
        
        # Audio utils connections
        self.audio_utils.playback_started.connect(self.on_playback_started)
        self.audio_utils.playback_finished.connect(self.on_playback_finished)
        self.audio_utils.playback_error.connect(self.on_audio_error)
        
        # RAG service signals for asynchronous responses
        self.rag_service.response_finished.connect(self.on_rag_response_finished)
        self.rag_service.error_occurred.connect(self.on_rag_error)
        self.rag_service.initialization_progress.connect(self.on_rag_initialization_progress)
    
    def start_listening(self):
        """Start voice recognition."""
        if self.vosk_service.start_recognition():
            self.is_listening = True
            self.ai_loader.setActive(True)
            self.soundwave_widget.set_listening_mode(True)
        else:
            self.soundwave_widget.stop_animation()
            self.show_exit_button()
    
    def stop_listening(self):
        """Stop voice recognition."""
        if self.is_listening:
            self.vosk_service.stop_recognition()
            self.is_listening = False
    
    def on_wake_word_detected(self, command_text: str):
        """Handle wake word detection with command text."""
        print(f"[VOICE UI DEBUG] Wake word signal received! Command: '{command_text}'")
        
        # Play wake word acknowledgment sound even if no command
        print(f"[VOICE UI DEBUG] Playing wake word sound...")
        self._play_wake_word_sound()
        
        if not command_text.strip():
            print(f"[VOICE UI DEBUG] No command text, just wake word detected")
            return
        
        print(f"[VOICE UI DEBUG] Processing wake word command: '{command_text}'")
        
        # Don't stop listening in wake word mode - keep continuous listening
        self.is_processing = True
        
        self.ai_loader.setActive(True)
        self.soundwave_widget.set_processing_mode(True)
        
        # Process command through RAG system
        self._process_rag_command(command_text)
    
    def on_text_recognized(self, text: str):
        """Handle recognized speech text (for non-wake-word mode)."""
        if not text.strip():
            return
        
        self.stop_listening()
        self.is_processing = True
        
        self.ai_loader.setActive(True)
        self.soundwave_widget.set_processing_mode(True)
        
        # Emit signal for parent to handle AI processing
        self.text_input_received.emit(text)
    
    def _process_rag_command(self, command_text: str):
        """Process command through RAG system and generate TTS response."""
        try:
            # Check if RAG service is ready
            if not self.rag_service.is_ready():
                if not self.rag_service.is_initializing():
                    print("[RAG DEBUG] RAG service not initialized, starting initialization...")
                    self.rag_service.initialize_async()
                print("[RAG DEBUG] RAG service not ready, will retry when ready")
                # Store command to retry when RAG is ready
                self._pending_command = command_text
                return
            
            print(f"[RAG DEBUG] RAG service is ready, processing command: '{command_text}'")
            
            # Add user message to chat session (same as non-voice mode)
            if not self.chat_manager.current_session:
                self.chat_manager.create_new_chat()
                print(f"[RAG DEBUG] Created new chat session")
            
            # Add user message using the correct ChatManager method
            self.chat_manager.add_message('user', command_text)
            print(f"[RAG DEBUG] User message saved to chat session")
            
            # Get conversation context for AI processing (same as non-voice mode)
            context = self.chat_manager.get_conversation_context()
            if context:
                # Format context for RAG service
                context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
                full_query = f"Previous conversation:\n{context_str}\n\nCurrent question: {command_text}"
                self.rag_service.query(full_query)
            else:
                self.rag_service.query(command_text)
            # Response will be handled by on_rag_response_finished signal
                
        except Exception as e:
            print(f"Error processing RAG command: {e}")
            self._reset_to_listening_state()
    
    def _reset_to_listening_state(self):
        """Reset UI to listening state for continuous wake word detection."""
        self.is_processing = False
        self.ai_loader.setActive(True)  # Keep active for continuous listening
        self.soundwave_widget.set_listening_mode(True)
    
    def _play_wake_word_sound(self):
        """Play the wake word acknowledgment sound."""
        print(f"[SOUND DEBUG] _play_wake_word_sound called")
        try:
            import os
            import soundfile as sf
            
            # Get the path to the sound file
            sound_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'sounds', 'getup.ogg')
            sound_path = os.path.abspath(sound_path)
            print(f"[SOUND DEBUG] Sound file path: {sound_path}")
            
            if os.path.exists(sound_path):
                print(f"[SOUND DEBUG] Sound file exists, loading...")
                # Load the sound file
                audio_data, sample_rate = sf.read(sound_path)
                print(f"[SOUND DEBUG] Sound loaded - sample rate: {sample_rate}, data shape: {audio_data.shape}")
                
                # Play using existing AudioUtils
                print(f"[SOUND DEBUG] Playing sound via AudioUtils...")
                self.audio_utils.play_audio(audio_data, sample_rate)
                print(f"[SOUND DEBUG] Wake word sound playback initiated: {sound_path}")
            else:
                print(f"[SOUND DEBUG] ERROR: Wake word sound file not found: {sound_path}")
                
        except Exception as e:
            print(f"[SOUND DEBUG] ERROR: Exception playing wake word sound: {e}")
            import traceback
            traceback.print_exc()
    
    def on_ai_response_ready(self, response_text: str):
        """Handle AI response and convert to speech."""
        if not response_text.strip():
            self.restart_listening()
            return
        
        self.soundwave_widget.set_processing_mode(True)
        
        # Generate TTS
        if not self.kokoro_service.generate_speech(response_text):
            self.status_label.setText("Failed to generate speech")
            self.restart_listening()
    
    def on_audio_generated(self, audio_data, sample_rate):
        """Handle generated TTS audio."""
        self.soundwave_widget.set_speaking_mode(True)
        self.audio_utils.play_audio(audio_data, sample_rate)
    
    def on_playback_finished(self):
        """Handle audio playback completion."""
        self.is_speaking = False
        self.soundwave_widget.set_speaking_mode(False)
        
        # In wake word mode, return to continuous listening state
        if self.vosk_service.is_wake_word_mode():
            self._reset_to_listening_state()
        else:
            self.restart_listening()
    
    def restart_listening(self):
        """Restart voice recognition after AI response."""
        QTimer.singleShot(1000, self.start_listening)
    
    def on_recognition_started(self):
        """Handle recognition start."""
        self.ai_loader.start()
    
    def on_recognition_stopped(self):
        """Handle recognition stop."""
        if not self.is_processing and not self.is_speaking:
            self.ai_loader.stop()
    
    def on_tts_started(self):
        """Handle TTS generation start."""
        pass
    
    def on_tts_finished(self):
        """Handle TTS generation completion."""
        pass
    
    def on_playback_started(self):
        """Handle audio playback start."""
        self.is_speaking = True
    
    def on_vosk_error(self, error: str):
        """Handle Vosk service errors."""
        self.instructions_label.setText("")
        self.show_exit_button()
    
    def on_kokoro_error(self, error: str):
        """Handle Kokoro service errors."""
        self.instructions_label.setText("")
        
        # In wake word mode, return to continuous listening state
        if self.vosk_service.is_wake_word_mode():
            self._reset_to_listening_state()
        else:
            self.restart_listening()
    
    def on_audio_error(self, error: str):
        """Handle audio playback errors."""
        self.instructions_label.setText("")
        
        # In wake word mode, return to continuous listening state
        if self.vosk_service.is_wake_word_mode():
            self._reset_to_listening_state()
        else:
            self.restart_listening()
    
    def on_rag_response_finished(self, response: str):
        """Handle RAG service response completion."""
        if response and response.strip():
            print(f"RAG response: {response}")
            
            # Add AI response to chat session (same as non-voice mode)
            if self.chat_manager.current_session:
                self.chat_manager.add_message('assistant', response)
                print(f"[RAG DEBUG] AI response saved to chat session")
            
            # Execute bash commands if present (same as text mode)
            print("[VOICE UI DEBUG] Checking for bash commands in AI response...")
            
            # Define callback for radio search results (same as text mode)
            def radio_search_callback(radio_response: str):
                """Handle radio search results by triggering a new AI query.
                Includes safeguards to prevent recursive queries on failed searches."""
                # Check if this is a failed search to prevent recursive callbacks
                if not radio_response or "✗ Search failed" in radio_response or "no results" in radio_response.lower():
                    if os.getenv("AI_IFACE_DEBUG") == "1":
                        print("[VOICE UI DEBUG] Skipping radio callback for failed search to prevent recursion", file=sys.stderr)
                    return
                
                print("[VOICE UI DEBUG] Processing radio search results with AI...")
                if self.rag_service:
                    self.rag_service.query(radio_response)
            
            # Command interception removed - responses are now handled by MCP servers
            print("[VOICE UI DEBUG] Response processing completed - commands handled by MCP servers")
            
            # Generate TTS for the response
            self.on_ai_response_ready(response)
        else:
            print("No response from RAG system")
            self._reset_to_listening_state()
    
    def on_rag_error(self, error: str):
        """Handle RAG service errors."""
        print(f"RAG error: {error}")
        self._reset_to_listening_state()
    
    def on_rag_initialization_progress(self, progress_message: str):
        """Handle RAG initialization progress updates."""
        print(f"[RAG DEBUG] Initialization progress: {progress_message}")
        if progress_message == "RAG service ready!" and self._pending_command:
            print(f"[RAG DEBUG] RAG is ready, processing pending command: '{self._pending_command}'")
            # Retry the pending command
            command = self._pending_command
            self._pending_command = None
            self._process_rag_command(command)
    
    def show_exit_button(self):
        """Show the exit button."""
        self.exit_button.show()
    
    def exit_voice_mode(self):
        """Exit voice mode and return to normal interface."""
        self.stop_listening()
        self.kokoro_service.stop_generation()
        self.audio_utils.stop_playback()
        self.voice_mode_exit_requested.emit()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.exit_voice_mode()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle widget close event."""
        self.exit_voice_mode()
        super().closeEvent(event)