"""Audio Utilities

Utilities for audio playback and processing in voice mode.
"""

import os
import tempfile
import threading
from typing import Optional
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread
import numpy as np

try:
    import pyaudio
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio libraries not available. Install with: pip install pyaudio soundfile")


class AudioPlaybackThread(QThread):
    """Thread for handling audio playback."""
    
    playback_finished = Signal()
    playback_error = Signal(str)
    
    def __init__(self, audio_data: np.ndarray, sample_rate: int, parent=None):
        super().__init__(parent)
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.is_playing = False
        self.should_stop = False
    
    def run(self):
        """Play audio data."""
        if not AUDIO_AVAILABLE:
            self.playback_error.emit("Audio libraries not available")
            return
        
        try:
            print(f"[AUDIO DEBUG] Starting audio playback...")
            print(f"[AUDIO DEBUG] Original audio shape: {self.audio_data.shape}")
            print(f"[AUDIO DEBUG] Original audio dtype: {self.audio_data.dtype}")
            print(f"[AUDIO DEBUG] Sample rate: {self.sample_rate}")
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            print(f"[AUDIO DEBUG] PyAudio initialized successfully")
            
            # Convert PyTorch tensor to NumPy array if needed
            if hasattr(self.audio_data, 'detach'):
                print(f"[AUDIO DEBUG] Converting PyTorch tensor to NumPy array")
                audio_data = self.audio_data.detach().cpu().numpy()
            else:
                audio_data = self.audio_data
            
            # Convert audio data to the right format
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            else:
                audio_data = audio_data
            
            # Ensure audio is in the right range
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Convert mono to stereo if needed
            if len(audio_data.shape) == 1:
                print(f"[AUDIO DEBUG] Converting mono to stereo")
                # Mono audio - duplicate to stereo
                audio_data = np.column_stack((audio_data, audio_data))
                channels = 2
            else:
                channels = audio_data.shape[1] if len(audio_data.shape) > 1 else 1
            
            print(f"[AUDIO DEBUG] Final audio shape: {audio_data.shape}")
            print(f"[AUDIO DEBUG] Channels: {channels}")
            
            # Open stream
            print(f"[AUDIO DEBUG] Opening PyAudio stream...")
            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024
            )
            print(f"[AUDIO DEBUG] PyAudio stream opened successfully")
            
            self.is_playing = True
            
            # Play audio in chunks
            chunk_size = 1024
            chunks_played = 0
            for i in range(0, len(audio_data), chunk_size):
                if self.should_stop:
                    break
                
                chunk = audio_data[i:i + chunk_size]
                
                # Pad chunk if necessary
                if len(chunk) < chunk_size:
                    if len(audio_data.shape) == 1:
                        chunk = np.pad(chunk, (0, chunk_size - len(chunk)), 'constant')
                    else:
                        chunk = np.pad(chunk, ((0, chunk_size - len(chunk)), (0, 0)), 'constant')
                
                stream.write(chunk.tobytes())
                chunks_played += 1
            
            print(f"[AUDIO DEBUG] Played {chunks_played} audio chunks")
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print(f"[AUDIO DEBUG] Audio playback completed successfully")
            
            self.is_playing = False
            self.playback_finished.emit()
            
        except Exception as e:
            print(f"[AUDIO DEBUG] Audio playback error: {str(e)}")
            self.is_playing = False
            self.playback_error.emit(f"Audio playback error: {e}")
    
    def stop_playback(self):
        """Stop audio playback."""
        self.should_stop = True


class AudioUtils(QObject):
    """Utility class for audio operations."""
    
    playback_started = Signal()
    playback_finished = Signal()
    playback_error = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.playback_thread = None
        self.is_playing = False
    
    def play_audio(self, audio_data: np.ndarray, sample_rate: int) -> bool:
        """Play audio data.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            True if playback started successfully, False otherwise
        """
        print(f"[AUDIO DEBUG] AudioUtils.play_audio called")
        print(f"[AUDIO DEBUG] Audio data shape: {audio_data.shape}")
        print(f"[AUDIO DEBUG] Sample rate: {sample_rate}")
        print(f"[AUDIO DEBUG] Currently playing: {self.is_playing}")
        
        if self.is_playing:
            print(f"[AUDIO DEBUG] Stopping current playback")
            self.stop_playback()
        
        if not AUDIO_AVAILABLE:
            print(f"[AUDIO DEBUG] Audio libraries not available")
            self.playback_error.emit("Audio libraries not available")
            return False
        
        try:
            print(f"[AUDIO DEBUG] Creating AudioPlaybackThread")
            self.playback_thread = AudioPlaybackThread(audio_data, sample_rate, self)
            self.playback_thread.playback_finished.connect(self._on_playback_finished)
            self.playback_thread.playback_error.connect(self._on_playback_error)
            
            print(f"[AUDIO DEBUG] Starting playback thread")
            self.playback_thread.start()
            self.is_playing = True
            self.playback_started.emit()
            print(f"[AUDIO DEBUG] Playback thread started successfully")
            return True
            
        except Exception as e:
            print(f"[AUDIO DEBUG] Failed to start audio playback: {e}")
            self.playback_error.emit(f"Failed to start audio playback: {e}")
            return False
    
    def stop_playback(self):
        """Stop current audio playback."""
        if self.is_playing and self.playback_thread:
            self.playback_thread.stop_playback()
            self.playback_thread.wait()
            self.is_playing = False
    
    def _on_playback_finished(self):
        """Handle playback completion."""
        self.is_playing = False
        self.playback_finished.emit()
    
    def _on_playback_error(self, error: str):
        """Handle playback errors."""
        self.is_playing = False
        self.playback_error.emit(error)
    
    def is_playback_active(self) -> bool:
        """Check if audio playback is currently active."""
        return self.is_playing
    
    @staticmethod
    def save_audio_to_file(audio_data: np.ndarray, sample_rate: int, filename: str) -> bool:
        """Save audio data to a file.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            filename: Output filename
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            sf.write(filename, audio_data, sample_rate)
            return True
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return False
    
    @staticmethod
    def load_audio_from_file(filename: str) -> tuple:
        """Load audio data from a file.
        
        Args:
            filename: Input filename
            
        Returns:
            Tuple of (audio_data, sample_rate) or (None, None) if failed
        """
        try:
            audio_data, sample_rate = sf.read(filename)
            return audio_data, sample_rate
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return None, None
    
    @staticmethod
    def get_audio_info() -> dict:
        """Get information about available audio devices.
        
        Returns:
            Dictionary with audio device information
        """
        if not AUDIO_AVAILABLE:
            return {'error': 'Audio libraries not available'}
        
        try:
            audio = pyaudio.PyAudio()
            info = {
                'device_count': audio.get_device_count(),
                'default_input_device': audio.get_default_input_device_info(),
                'default_output_device': audio.get_default_output_device_info(),
                'devices': []
            }
            
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                info['devices'].append({
                    'index': i,
                    'name': device_info['name'],
                    'max_input_channels': device_info['maxInputChannels'],
                    'max_output_channels': device_info['maxOutputChannels'],
                    'default_sample_rate': device_info['defaultSampleRate']
                })
            
            audio.terminate()
            return info
            
        except Exception as e:
            return {'error': f'Failed to get audio info: {e}'}
    
    @staticmethod
    def is_available() -> bool:
        """Check if audio utilities are available.
        
        Returns:
            True if audio libraries are installed and available
        """
        return AUDIO_AVAILABLE