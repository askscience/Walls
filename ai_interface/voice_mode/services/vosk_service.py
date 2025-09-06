"""Vosk Speech Recognition Service

Handles speech recognition using Vosk models with automatic model downloading and management.
"""

import os
import re
import json
import pyaudio
import vosk
import tempfile
import requests
import zipfile
from pathlib import Path
from typing import Dict, Optional
from PySide6.QtCore import QObject, QThread, Signal


class VoskModelManager:
    """Manages Vosk model downloading and caching."""
    
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Load model information from CSV
        self.available_models = self._load_model_info()
    
    def _load_model_info(self) -> Dict[str, Dict[str, str]]:
        """Load model information from vosk_models.csv."""
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vosk_models.csv")
        models = {}
        models_by_name = {}
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[1:]  # Skip header
                for line in lines:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        language, model_name, size, url = parts[:4]
                        model_info = {
                            'name': model_name,
                            'size': size,
                            'url': url,
                            'language': language
                        }
                        # Store by language (for backward compatibility)
                        models[language.lower()] = model_info
                        # Store by model name (for direct lookup)
                        models_by_name[model_name] = model_info
        except FileNotFoundError:
            # Default English model if CSV not found
            default_model = {
                'name': 'vosk-model-small-en-us-0.15',
                'size': '40M',
                'url': 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
                'language': 'English'
            }
            models['english'] = default_model
            models_by_name['vosk-model-small-en-us-0.15'] = default_model
        
        # Store both lookups
        self.models_by_name = models_by_name
        return models
    
    def get_model_path(self, language: str = 'english', model_name: str = None) -> Optional[str]:
        """Get the path to a model, downloading if necessary.
        
        Args:
            language: Language for model selection (used if model_name not provided)
            model_name: Specific model name to use (overrides language-based selection)
        """
        # If specific model name is provided, use it directly
        if model_name:
            model_path = self.models_dir / model_name
            if model_path.exists():
                print(f"Using specified model: {model_name}")
                return str(model_path)
            else:
                # Look for the model by name in models_by_name lookup
                if model_name in self.models_by_name:
                    model_info = self.models_by_name[model_name]
                    print(f"Downloading specified model '{model_name}' from {model_info['url']}")
                    return self._download_model(model_info['url'], model_name)
                
                print(f"Specified model '{model_name}' not found in CSV or local directory")
                print(f"Available models in CSV:")
                for model_name_key, model_info in self.models_by_name.items():
                    print(f"  - {model_name_key} ({model_info['language']}, {model_info['size']})")
                return None
        
        # Fall back to language-based selection
        language = language.lower()
        
        if language not in self.available_models:
            print(f"Language '{language}' not available. Using English.")
            language = 'english'
        
        model_info = self.available_models[language]
        model_name = model_info['name']
        model_path = self.models_dir / model_name
        
        if model_path.exists():
            return str(model_path)
        
        # Download model
        print(f"Downloading {model_name} ({model_info['size']})...")
        return self._download_model(model_info['url'], model_name)
    
    def _download_model(self, url: str, model_name: str) -> Optional[str]:
        """Download and extract a Vosk model."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, f"{model_name}.zip")
                
                # Download
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.models_dir)
                
                model_path = self.models_dir / model_name
                if model_path.exists():
                    print(f"Model {model_name} downloaded successfully.")
                    return str(model_path)
                
        except Exception as e:
            print(f"Error downloading model: {e}")
        
        return None


class VoskRecognitionThread(QThread):
    """Thread for handling Vosk speech recognition with wake word detection."""
    
    text_recognized = Signal(str)
    error_occurred = Signal(str)
    wake_word_detected = Signal(str)  # Emitted when wake word is detected with following text
    
    def __init__(self, model_path: str, wake_word_mode: bool = False, parent=None):
        super().__init__(parent)
        self.model_path = model_path
        self.is_running = False
        self.model = None
        self.rec = None
        self.wake_word_mode = wake_word_mode
        self.config = self.load_config()
        
        # Wake word patterns from config
        self.wake_words = self.config.get('wake_words', {}).get('patterns', [
            r'hey\s+walls?',
            r'hi\s+walls?',
            r'hello\s+walls?',
            r'hey\s+world?s?',
            r'hey\s+word?s?'
        ])
        self.wake_word_pattern = re.compile('|'.join(self.wake_words), re.IGNORECASE)
        
        # Audio settings from config
        audio_config = self.config.get('audio', {})
        self.sample_rate = audio_config.get('sample_rate', 16000)
        self.chunk_size = audio_config.get('chunk_size', 4096)
        self.channels = audio_config.get('channels', 1)
        self.format = pyaudio.paInt16
        self.volume_threshold = audio_config.get('volume_threshold', 20.0)
        self.preferred_device_keywords = audio_config.get('preferred_device_keywords', ["macbook", "built-in", "internal", "micrófono", "microphone"])
    
    def load_config(self):
         """Load configuration from config file."""
         try:
             config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "voice_config.json")
             print(f"[CONFIG DEBUG] Looking for config at: {config_path}")
             if os.path.exists(config_path):
                 with open(config_path, 'r', encoding='utf-8') as f:
                     config = json.load(f)
                     print(f"[CONFIG DEBUG] Config loaded successfully")
                     return config
             else:
                 print(f"[CONFIG DEBUG] Config file not found at {config_path}")
         except Exception as e:
             print(f"[CONFIG DEBUG] Error loading config: {e}")
         
         # Return default config if loading fails
         print(f"[CONFIG DEBUG] Using default config")
         return {
             'wake_words': {
                 'patterns': [
                     r'hey\s+walls?',
                     r'hi\s+walls?',
                     r'hello\s+walls?',
                     r'hey\s+world?s?',
                     r'hey\s+word?s?'
                 ]
             },
             'audio': {
                 'sample_rate': 16000,
                 'chunk_size': 4096,
                 'channels': 1,
                 'volume_threshold': 20.0,
                 'preferred_device_keywords': ["macbook", "built-in", "internal", "micrófono", "microphone"]
             }
         }
    
    def run(self):
        """Main recognition loop."""
        try:
            # Initialize Vosk
            print(f"[VOSK DEBUG] Initializing Vosk model from: {self.model_path}")
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
            print(f"[VOSK DEBUG] Vosk initialized successfully. Wake word mode: {self.wake_word_mode}")
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            print(f"[VOSK DEBUG] PyAudio initialized")
            
            # List available audio devices for debugging
            print(f"[VOSK DEBUG] Available audio devices:")
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    print(f"[VOSK DEBUG]   Device {i}: {device_info['name']} (inputs: {device_info['maxInputChannels']})")
            
            # Get default input device
            default_device = audio.get_default_input_device_info()
            print(f"[VOSK DEBUG] Default input device: {default_device['name']} (index: {default_device['index']})")
            
            # Find preferred microphone device using config
            input_device_index = self.config.get('audio', {}).get('input_device_index')
            
            if input_device_index is None:
                # Auto-detect preferred device
                microphone_device_index = None
                for i in range(audio.get_device_count()):
                    device_info = audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        device_name = device_info['name'].lower()
                        # Look for built-in microphone keywords from config
                        if any(keyword in device_name for keyword in self.preferred_device_keywords):
                            microphone_device_index = i
                            print(f"[VOSK DEBUG] Found built-in microphone: {device_info['name']} (index: {i})")
                            break
                
                # Use found microphone or fall back to default
                input_device_index = microphone_device_index if microphone_device_index is not None else default_device['index']
            else:
                print(f"[VOSK DEBUG] Using configured input device index: {input_device_index}")
            
            selected_device = audio.get_device_info_by_index(input_device_index)
            print(f"[VOSK DEBUG] Using input device: {selected_device['name']} (index: {input_device_index})")
            
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=self.chunk_size
            )
            print(f"[VOSK DEBUG] Audio stream opened. Sample rate: {self.sample_rate}, Chunk size: {self.chunk_size}")
            print(f"[VOSK DEBUG] Stream is active: {stream.is_active()}, Stream is stopped: {stream.is_stopped()}")
            
            self.is_running = True
            print(f"[VOSK DEBUG] Starting recognition loop...")
            
            audio_chunk_count = 0
            while self.is_running:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_chunk_count += 1
                    
                    # Check audio data volume to verify microphone input
                    import numpy as np
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    volume = np.sqrt(np.mean(audio_data**2))
                    
                    # Log audio volume every 50 chunks (about every 3 seconds at 16kHz)
                    if audio_chunk_count % 50 == 0:
                        print(f"[VOSK DEBUG] Audio chunk #{audio_chunk_count}, Volume level: {volume:.2f} (threshold: {self.volume_threshold})")
                    
                    # Only process if volume is above threshold
                    if volume > self.volume_threshold:
                        if self.rec.AcceptWaveform(data):
                            result = json.loads(self.rec.Result())
                            text = result.get('text', '').strip()
                            print(f"[VOSK DEBUG] Recognized text: '{text}' (volume: {volume:.2f})")
                            if text:
                                if self.wake_word_mode:
                                    print(f"[VOSK DEBUG] Processing for wake words: '{text}'")
                                    self._process_wake_word_text(text)
                                else:
                                    self.text_recognized.emit(text)
                        else:
                            # Also check partial results for debugging
                            partial = json.loads(self.rec.PartialResult())
                            partial_text = partial.get('partial', '').strip()
                            if partial_text:
                                print(f"[VOSK DEBUG] Partial text: '{partial_text}' (volume: {volume:.2f})")
                    else:
                        # Low volume, just log occasionally
                        if hasattr(self, '_low_volume_counter'):
                            self._low_volume_counter += 1
                        else:
                            self._low_volume_counter = 1
                        
                        if self._low_volume_counter % 100 == 0:  # Log every 100 low volume chunks
                            print(f"[VOSK DEBUG] Low volume: {volume:.2f} (threshold: {self.volume_threshold})")
                    
                except Exception as e:
                    if self.is_running:  # Only emit error if we're still supposed to be running
                        print(f"[VOSK DEBUG] Audio processing error: {e}")
                        self.error_occurred.emit(f"Audio processing error: {e}")
                        break
            
            # Cleanup
            print(f"[VOSK DEBUG] Stopping recognition, cleaning up...")
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
        except Exception as e:
            print(f"[VOSK DEBUG] Recognition initialization error: {e}")
            self.error_occurred.emit(f"Recognition initialization error: {e}")
    
    def _process_wake_word_text(self, text: str):
        """Process text for wake word detection and extract command after wake word."""
        text_lower = text.lower().strip()
        print(f"[WAKE WORD DEBUG] Checking text: '{text_lower}'")
        print(f"[WAKE WORD DEBUG] Wake word patterns: {self.wake_words}")
        
        # Check each pattern individually for better debugging
        for pattern in self.wake_words:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                print(f"[WAKE WORD DEBUG] MATCH FOUND! Pattern '{pattern}' matched: '{match.group()}'")
                # Extract text after the wake word
                wake_word_end = match.end()
                command_text = text[wake_word_end:].strip()
                
                # Remove common punctuation and clean up
                command_text = re.sub(r'^[,\s]+', '', command_text)
                
                if command_text:
                    print(f"[WAKE WORD DEBUG] Wake word detected! Command: '{command_text}'")
                    self.wake_word_detected.emit(command_text)
                else:
                    print(f"[WAKE WORD DEBUG] Wake word detected but no command found")
                    # Still emit signal even without command
                    self.wake_word_detected.emit("")
                return
        
        print(f"[WAKE WORD DEBUG] No wake word match found in: '{text_lower}'")
        # Show what we're looking for
        print(f"[WAKE WORD DEBUG] Expected patterns: {', '.join(self.wake_words)}")
    
    def stop_recognition(self):
        """Stop the recognition thread."""
        self.is_running = False
        self.wait()  # Wait for thread to finish


class VoskService(QObject):
    """Main Vosk speech recognition service with wake word support."""
    
    text_recognized = Signal(str)
    error_occurred = Signal(str)
    recognition_started = Signal()
    recognition_stopped = Signal()
    wake_word_detected = Signal(str)  # Emitted when wake word is detected with command
    
    def __init__(self, language: str = 'english', model_name: str = None, wake_word_mode: bool = False, parent=None):
        super().__init__(parent)
        self.language = language
        self.model_name = model_name
        self.wake_word_mode = wake_word_mode
        self.model_manager = VoskModelManager()
        self.recognition_thread = None
        self.is_listening = False
    
    def start_recognition(self) -> bool:
        """Start speech recognition."""
        if self.is_listening:
            return True
        
        model_path = self.model_manager.get_model_path(self.language, self.model_name)
        if not model_path:
            self.error_occurred.emit("Failed to load speech recognition model")
            return False
        
        try:
            self.recognition_thread = VoskRecognitionThread(model_path, self.wake_word_mode, self)
            self.recognition_thread.text_recognized.connect(self.text_recognized)
            self.recognition_thread.error_occurred.connect(self._on_recognition_error)
            self.recognition_thread.finished.connect(self._on_recognition_finished)
            
            # Connect wake word signal if in wake word mode
            if self.wake_word_mode:
                self.recognition_thread.wake_word_detected.connect(self.wake_word_detected)
            
            self.recognition_thread.start()
            self.is_listening = True
            self.recognition_started.emit()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to start recognition: {e}")
            return False
    
    def stop_recognition(self):
        """Stop speech recognition."""
        if not self.is_listening or not self.recognition_thread:
            return
        
        self.recognition_thread.stop_recognition()
        self.is_listening = False
    
    def _on_recognition_error(self, error: str):
        """Handle recognition errors."""
        self.is_listening = False
        self.error_occurred.emit(error)
    
    def _on_recognition_finished(self):
        """Handle recognition thread completion."""
        self.is_listening = False
        self.recognition_stopped.emit()
    
    def is_recognition_active(self) -> bool:
        """Check if recognition is currently active."""
        return self.is_listening
    
    def set_language(self, language: str):
        """Change the recognition language."""
        if self.is_listening:
            self.stop_recognition()
        self.language = language
    
    def set_wake_word_mode(self, enabled: bool):
        """Enable or disable wake word mode."""
        if self.is_listening:
            self.stop_recognition()
        self.wake_word_mode = enabled
    
    def is_wake_word_mode(self) -> bool:
        """Check if wake word mode is enabled."""
        return self.wake_word_mode