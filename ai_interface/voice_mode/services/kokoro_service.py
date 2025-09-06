"""Kokoro Text-to-Speech Service

Handles text-to-speech conversion using the Kokoro TTS model.
"""

import os
import tempfile
import threading
from typing import Optional, Generator, Tuple
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread
import numpy as np

try:
    from kokoro import KPipeline
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    print("Kokoro not installed. Install with: pip install kokoro")


class KokoroTTSThread(QThread):
    """Thread for handling Kokoro TTS generation."""
    
    audio_generated = Signal(np.ndarray, int)  # audio_data, sample_rate
    error_occurred = Signal(str)
    generation_finished = Signal()
    
    def __init__(self, text: str, voice: str = 'af_heart', lang_code: str = 'a', parent=None):
        super().__init__(parent)
        self.text = text
        self.voice = voice
        self.lang_code = lang_code
        self.pipeline = None
    
    def run(self):
        """Generate TTS audio."""
        if not KOKORO_AVAILABLE:
            self.error_occurred.emit("Kokoro TTS is not available. Please install it with: pip install kokoro")
            return
        
        try:
            # Initialize pipeline
            self.pipeline = KPipeline(lang_code=self.lang_code)
            
            # Generate audio
            generator = self.pipeline(self.text, voice=self.voice)
            
            # Process generated audio chunks
            for i, (gs, ps, audio) in enumerate(generator):
                if audio is not None and len(audio) > 0:
                    # Emit audio data with sample rate (Kokoro uses 24kHz)
                    self.audio_generated.emit(audio, 24000)
            
            self.generation_finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"TTS generation error: {e}")


class KokoroService(QObject):
    """Main Kokoro TTS service."""
    
    audio_generated = Signal(np.ndarray, int)  # audio_data, sample_rate
    error_occurred = Signal(str)
    generation_started = Signal()
    generation_finished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tts_thread = None
        self.is_generating = False
        
        # Voice settings
        self.current_voice = 'af_heart'
        self.current_lang_code = 'a'  # American English
        
        # Available voices for different languages
        self.available_voices = {
            'a': ['af_heart', 'af_sky', 'af_bella', 'af_sarah'],  # American English
            'b': ['bf_heart', 'bf_sky', 'bf_bella', 'bf_sarah'],  # British English
            'e': ['ef_heart', 'ef_sky', 'ef_bella', 'ef_sarah'],  # Spanish
            'f': ['ff_heart', 'ff_sky', 'ff_bella', 'ff_sarah'],  # French
            'i': ['if_heart', 'if_sky', 'if_bella', 'if_sarah'],  # Italian
            'p': ['pf_heart', 'pf_sky', 'pf_bella', 'pf_sarah'],  # Portuguese
        }
    
    def generate_speech(self, text: str, voice: Optional[str] = None, lang_code: Optional[str] = None) -> bool:
        """Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (optional, uses current voice if None)
            lang_code: Language code (optional, uses current lang_code if None)
            
        Returns:
            True if generation started successfully, False otherwise
        """
        if self.is_generating:
            self.error_occurred.emit("TTS generation already in progress")
            return False
        
        if not text.strip():
            self.error_occurred.emit("No text provided for TTS")
            return False
        
        if not KOKORO_AVAILABLE:
            self.error_occurred.emit("Kokoro TTS is not available")
            return False
        
        # Use provided parameters or defaults
        voice = voice or self.current_voice
        lang_code = lang_code or self.current_lang_code
        
        try:
            self.tts_thread = KokoroTTSThread(text, voice, lang_code, self)
            self.tts_thread.audio_generated.connect(self.audio_generated)
            self.tts_thread.error_occurred.connect(self._on_generation_error)
            self.tts_thread.generation_finished.connect(self._on_generation_finished)
            
            self.tts_thread.start()
            self.is_generating = True
            self.generation_started.emit()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to start TTS generation: {e}")
            return False
    
    def stop_generation(self):
        """Stop current TTS generation."""
        if self.is_generating and self.tts_thread:
            self.tts_thread.terminate()
            self.tts_thread.wait()
            self.is_generating = False
    
    def _on_generation_error(self, error: str):
        """Handle TTS generation errors."""
        self.is_generating = False
        self.error_occurred.emit(error)
    
    def _on_generation_finished(self):
        """Handle TTS generation completion."""
        self.is_generating = False
        self.generation_finished.emit()
    
    def set_voice(self, voice: str, lang_code: Optional[str] = None):
        """Set the current voice and optionally language code.
        
        Args:
            voice: Voice name to use
            lang_code: Language code (optional)
        """
        if lang_code:
            self.current_lang_code = lang_code
        
        # Validate voice for current language
        if self.current_lang_code in self.available_voices:
            if voice in self.available_voices[self.current_lang_code]:
                self.current_voice = voice
            else:
                # Use first available voice for the language
                self.current_voice = self.available_voices[self.current_lang_code][0]
        else:
            self.current_voice = voice
    
    def set_language(self, lang_code: str):
        """Set the language code and update voice accordingly.
        
        Args:
            lang_code: Language code ('a' for American English, 'b' for British, etc.)
        """
        self.current_lang_code = lang_code
        
        # Set default voice for the language
        if lang_code in self.available_voices:
            self.current_voice = self.available_voices[lang_code][0]
    
    def get_available_voices(self, lang_code: Optional[str] = None) -> list:
        """Get available voices for a language.
        
        Args:
            lang_code: Language code (uses current if None)
            
        Returns:
            List of available voice names
        """
        lang_code = lang_code or self.current_lang_code
        return self.available_voices.get(lang_code, [])
    
    def is_generation_active(self) -> bool:
        """Check if TTS generation is currently active."""
        return self.is_generating
    
    def get_current_settings(self) -> dict:
        """Get current TTS settings.
        
        Returns:
            Dictionary with current voice and language settings
        """
        return {
            'voice': self.current_voice,
            'lang_code': self.current_lang_code,
            'available_voices': self.get_available_voices()
        }
    
    @staticmethod
    def is_available() -> bool:
        """Check if Kokoro TTS is available.
        
        Returns:
            True if Kokoro is installed and available
        """
        return KOKORO_AVAILABLE