from typing import Optional, List
from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# Optional waveform support: QAudioProbe may not be available on some PySide6 builds
try:
    from PySide6.QtMultimedia import QAudioProbe, QAudioBuffer  # type: ignore
except Exception:  # pragma: no cover - platform dependent
    QAudioProbe = None  # type: ignore
    QAudioBuffer = None  # type: ignore

class RadioPlayer(QObject):
    stateChanged = Signal(str)
    errorOccurred = Signal(str)
    positionChanged = Signal(int)
    durationChanged = Signal(int)
    levelsUpdated = Signal(list)  # list[float] normalized 0..1 for waveform bars

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize audio output first
        try:
            self._audio = QAudioOutput()
            print(f"QAudioOutput initialized successfully")
        except Exception as e:
            print(f"Failed to initialize QAudioOutput: {e}")
            raise
        
        # Initialize media player
        try:
            self._player = QMediaPlayer()
            print(f"QMediaPlayer initialized successfully")
        except Exception as e:
            print(f"Failed to initialize QMediaPlayer: {e}")
            raise
            
        # Set audio output
        try:
            self._player.setAudioOutput(self._audio)
            print(f"Audio output set successfully")
        except Exception as e:
            print(f"Failed to set audio output: {e}")
            
        # Connect error signal with better error handling
        try:
            self._player.errorOccurred.connect(self._on_error)
            self._player.playbackStateChanged.connect(self._on_state)
            self._player.positionChanged.connect(self._on_position)
            self._player.durationChanged.connect(self._on_duration)
            print(f"Player signals connected successfully")
        except Exception as e:
            print(f"Failed to connect player signals: {e}")

        # Probe audio to compute simple amplitude levels for visualization
        self._probe = None
        if QAudioProbe is not None:
            try:
                self._probe = QAudioProbe(self)  # type: ignore
                probe_set = self._probe.setSource(self._player)  # type: ignore
                self._probe.audioBufferProbed.connect(self._on_buffer)  # type: ignore
                print(f"Audio probe initialized - Source set: {probe_set}, Probe: {self._probe is not None}")
            except Exception as e:
                print(f"Audio probe initialization failed: {e}")
                self._probe = None  # Visualization not supported
        else:
            print("QAudioProbe not available - using fallback visualization")
            # Since QAudioProbe is not available, we'll use a timer-based fallback
            from PySide6.QtCore import QTimer
            self._viz_timer = QTimer()
            self._viz_timer.moveToThread(self.thread())  # Ensure timer runs on main thread
            self._viz_timer.timeout.connect(self._generate_fallback_levels)
            self._is_playing_audio = False

    def _on_error(self, error, error_string: str = ""):
        msg = error_string or self._player.errorString() or str(error)
        self.errorOccurred.emit(msg)

    def _on_state(self, state):
        mapping = {
            QMediaPlayer.PlayingState: "playing",
            QMediaPlayer.PausedState: "paused",
            QMediaPlayer.StoppedState: "stopped",
        }
        self.stateChanged.emit(mapping.get(state, "unknown"))

    def _on_position(self, pos: int):
        try:
            self.positionChanged.emit(int(pos))
        except Exception:
            self.positionChanged.emit(0)

    def _on_duration(self, dur: int):
        try:
            self.durationChanged.emit(int(dur))
        except Exception:
            self.durationChanged.emit(0)

    def _on_buffer(self, buf):  # buf: QAudioBuffer | object
        # Compute a coarse amplitude level from the audio buffer
        try:
            # If QAudioBuffer type isn't available, try duck-typing
            fmt = buf.format()
            bytes_per_sample = fmt.bytesPerSample()
            ch = fmt.channelCount()
            data = buf.data()
            if not data:
                return
            mv = memoryview(data)
            step = bytes_per_sample * ch
            # Sample up to 100 frames evenly to reduce cost
            frame_count = buf.frameCount() if hasattr(buf, 'frameCount') else int(len(mv) / step)
            if frame_count <= 0:
                return
            take = min(100, frame_count)
            inc = max(1, frame_count // take)
            levels: List[float] = []
            for i in range(0, frame_count, inc):
                base = i * step
                if base + step > len(mv):
                    break
                # Take first channel
                if bytes_per_sample == 2:
                    # int16
                    s = int.from_bytes(mv[base:base+2], byteorder='little', signed=True)
                    amp = abs(s) / 32768.0
                elif bytes_per_sample == 4:
                    # Try float32 little-endian
                    import struct
                    try:
                        f = struct.unpack('<f', mv[base:base+4])[0]
                        amp = min(1.0, abs(f))
                    except Exception:
                        # treat as int32
                        s = int.from_bytes(mv[base:base+4], byteorder='little', signed=True)
                        amp = min(1.0, abs(s) / 2147483648.0)
                else:
                    # Fallback normalize by max int for given bytes
                    s = int.from_bytes(mv[base:base+bytes_per_sample], byteorder='little', signed=True)
                    maxv = float(1 << (8*bytes_per_sample - 1))
                    amp = min(1.0, abs(s) / maxv)
                levels.append(amp)
            # Normalize to 20 bars
            if levels:
                n = 20
                bucket = max(1, len(levels) // n)
                bars = [sum(levels[i:i+bucket]) / max(1, len(levels[i:i+bucket])) for i in range(0, len(levels), bucket)]
                bars = bars[:n]
                final_bars = [max(0.0, min(1.0, v)) for v in bars]
                self.levelsUpdated.emit(final_bars)
        except Exception as e:
            print(f"Audio buffer processing error: {e}")
            pass
    
    def _generate_fallback_levels(self):
        """Generate pseudo-random audio levels when real audio probe is not available."""
        if self._is_playing_audio:
            import random
            import math
            import time
            
            # Generate more realistic audio levels with some rhythm
            t = time.time()
            base_rhythm = math.sin(t * 2) * 0.3 + 0.4  # Slow rhythm base
            beat_rhythm = math.sin(t * 8) * 0.2  # Faster beat
            
            levels = []
            for i in range(20):
                # Create variation across frequency bands
                freq_factor = 1.0 - (i / 20.0) * 0.6  # Lower frequencies stronger
                noise = random.random() * 0.3
                level = (base_rhythm + beat_rhythm + noise) * freq_factor
                level = max(0.05, min(0.9, level))  # Clamp between 5% and 90%
                levels.append(level)
            
            self.levelsUpdated.emit(levels)

    def play(self, url: str, volume: int = 60):
        try:
            print(f"Setting volume to {volume}%")
            self._audio.setVolume(volume / 100.0)
            
            print(f"Setting source URL: {url}")
            qurl = QUrl(url)
            if not qurl.isValid():
                print(f"Invalid URL: {url}")
                self.errorOccurred.emit(f"Invalid URL: {url}")
                return
                
            self._player.setSource(qurl)
            print(f"Source set, current state: {self._player.playbackState()}")
            
            print(f"Starting playback...")
            self._player.play()
            print(f"Play called, new state: {self._player.playbackState()}")
            
            # Check for immediate errors
            error_string = self._player.errorString()
            if error_string:
                print(f"Player error after play(): {error_string}")
                self.errorOccurred.emit(error_string)
            
            # Start fallback visualization if probe is not available
            if self._probe is None and hasattr(self, '_viz_timer'):
                self._is_playing_audio = True
                # Use QTimer.singleShot to ensure timer operations happen on main thread
                from PySide6.QtCore import QTimer as QtTimer
                QtTimer.singleShot(0, lambda: self._viz_timer.start(50))
                
        except Exception as e:
            error_msg = f"Failed to play URL {url}: {e}"
            print(error_msg)
            self.errorOccurred.emit(error_msg)

    def pause(self):
        self._player.pause()
        # Pause fallback visualization
        if hasattr(self, '_viz_timer'):
            self._is_playing_audio = False
            from PySide6.QtCore import QTimer as QtTimer
            QtTimer.singleShot(0, lambda: self._viz_timer.stop())

    def stop(self):
        self._player.stop()
        # Stop fallback visualization
        if hasattr(self, '_viz_timer'):
            self._is_playing_audio = False
            from PySide6.QtCore import QTimer as QtTimer
            QtTimer.singleShot(0, lambda: self._viz_timer.stop())

    def set_volume(self, volume: int):
        self._audio.setVolume(max(0, min(100, volume)) / 100.0)

    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlayingState

    def current_source(self) -> Optional[str]:
        url = self._player.source()
        return url.toString() if url.isValid() else None

    # Seek support for progress control
    def set_position(self, ms: int):
        try:
            self._player.setPosition(int(ms))
        except Exception:
            pass