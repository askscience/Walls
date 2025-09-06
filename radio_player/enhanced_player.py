from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from .player import RadioPlayer
from .metadata_parser import StreamMetadataParser
from .musicbrainz_client import MusicBrainzClient
import logging

logger = logging.getLogger(__name__)

class MetadataWorker(QThread):
    """Worker thread for fetching metadata and MusicBrainz data."""
    
    metadataFound = Signal(dict)  # Emits track info with cover art
    metadataError = Signal(str)   # Emits error message
    
    def __init__(self, stream_url: str, mb_client: MusicBrainzClient, parent=None):
        super().__init__(parent)
        self.stream_url = stream_url
        self.mb_client = mb_client
        self.metadata_parser = StreamMetadataParser()
        self._should_stop = False
    
    def stop(self):
        """Stop the worker thread."""
        self._should_stop = True
        self.quit()
        self.wait()
    
    def run(self):
        """Main worker thread execution."""
        try:
            if self._should_stop:
                return
            
            # Get stream metadata
            metadata = self.metadata_parser.get_stream_metadata(self.stream_url)
            
            if self._should_stop:
                return
            
            if not metadata:
                self.metadataError.emit("Could not get stream metadata")
                return
            
            stream_title = metadata.get('StreamTitle', '')
            icy_name = metadata.get('station', '')
            icy_genre = metadata.get('genre', '')
            
            if stream_title and stream_title.strip():
                # Parse artist and title from stream title
                artist, title = self.metadata_parser.extract_artist_title(stream_title)
                
                if self._should_stop:
                    return
                
                logger.info(f"Found track: {artist} - {title}")
                
                # Search MusicBrainz for track info
                track_info = self.mb_client.find_track_info(artist, title)
                
                if self._should_stop:
                    return
                
                if track_info:
                    # Add ICY metadata to MusicBrainz info
                    track_info['stream_title'] = stream_title
                    track_info['icy_name'] = icy_name
                    track_info['icy_genre'] = icy_genre
                    self.metadataFound.emit(track_info)
                else:
                    # Emit basic info even if no MusicBrainz data found
                    basic_info = {
                        'artist': artist or 'Unknown Artist',
                        'title': title,
                        'stream_title': stream_title,
                        'icy_name': icy_name,
                        'icy_genre': icy_genre,
                        'cover_art_url': None
                    }
                    self.metadataFound.emit(basic_info)
            elif icy_name:
                # Fallback to station info if no track title
                basic_info = {
                    'artist': '',
                    'title': icy_name,
                    'stream_title': '',
                    'icy_name': icy_name,
                    'icy_genre': icy_genre,
                    'cover_art_url': None
                }
                self.metadataFound.emit(basic_info)
            else:
                self.metadataError.emit("No metadata available from stream")
                
        except Exception as e:
            logger.error(f"Error in metadata worker: {e}")
            self.metadataError.emit(str(e))

class EnhancedRadioPlayer(RadioPlayer):
    """Enhanced radio player with metadata parsing and MusicBrainz integration."""
    
    # New signals for metadata
    trackChanged = Signal(dict)      # Emits track info when song changes
    coverArtFound = Signal(str)      # Emits cover art URL when found
    metadataError = Signal(str)      # Emits metadata-related errors
    
    def __init__(self, parent=None, mb_contact: str = "user@example.com"):
        super().__init__(parent)
        
        # Initialize metadata components
        self.metadata_parser = StreamMetadataParser()
        self.mb_client = MusicBrainzClient(
            app_name="EnhancedRadioPlayer",
            app_version="1.0",
            contact=mb_contact
        )
        
        # Metadata polling timer
        self.metadata_timer = QTimer(self)
        self.metadata_timer.timeout.connect(self._check_metadata)
        self.metadata_poll_interval = 5000  # 5 seconds
        
        # Current track info
        self.current_track_info: Optional[Dict[str, Any]] = None
        self.last_stream_title = ""
        
        # Worker thread for metadata fetching
        self.metadata_worker: Optional[MetadataWorker] = None
        
        # Connect to player state changes
        self.stateChanged.connect(self._on_player_state_changed)
    
    def _on_player_state_changed(self, state: str):
        """Handle player state changes to manage metadata polling."""
        if state == "playing":
            self._start_metadata_polling()
        else:
            self._stop_metadata_polling()
    
    def _start_metadata_polling(self):
        """Start polling for metadata updates."""
        if not self.metadata_timer.isActive():
            self.metadata_timer.start(self.metadata_poll_interval)
            # Check metadata immediately
            self._check_metadata()
    
    def _stop_metadata_polling(self):
        """Stop polling for metadata updates."""
        self.metadata_timer.stop()
        self._stop_metadata_worker()
    
    def _stop_metadata_worker(self):
        """Stop the current metadata worker thread."""
        if self.metadata_worker and self.metadata_worker.isRunning():
            self.metadata_worker.stop()
            self.metadata_worker = None
    
    def _check_metadata(self):
        """Check for metadata updates from the current stream."""
        current_url = self.current_source()
        if not current_url:
            return
        
        try:
            # Get basic metadata from stream
            metadata = self.metadata_parser.get_stream_metadata(current_url)
            if not metadata or 'StreamTitle' not in metadata:
                return
            
            stream_title = metadata['StreamTitle']
            
            # Check if the track has changed
            if stream_title != self.last_stream_title:
                self.last_stream_title = stream_title
                logger.info(f"New track detected: {stream_title}")
                
                # Stop any existing worker
                self._stop_metadata_worker()
                
                # Start new worker to fetch detailed info
                self.metadata_worker = MetadataWorker(current_url, self.mb_client, self)
                self.metadata_worker.metadataFound.connect(self._on_metadata_found)
                self.metadata_worker.metadataError.connect(self._on_metadata_error)
                self.metadata_worker.start()
                
        except Exception as e:
            logger.error(f"Error checking metadata: {e}")
            self.metadataError.emit(str(e))
    
    def _on_metadata_found(self, track_info: Dict[str, Any]):
        """Handle metadata found by worker thread."""
        self.current_track_info = track_info
        self.trackChanged.emit(track_info)
        
        # Emit cover art signal if available
        if track_info.get('cover_art_url'):
            self.coverArtFound.emit(track_info['cover_art_url'])
        
        logger.info(f"Track info updated: {track_info.get('artist', 'Unknown')} - {track_info.get('title', 'Unknown')}")
    
    def _on_metadata_error(self, error_msg: str):
        """Handle metadata errors from worker thread."""
        logger.error(f"Metadata error: {error_msg}")
        self.metadataError.emit(error_msg)
    
    def play(self, url: str, volume: int = 60):
        """Override play method to reset metadata state."""
        # Reset metadata state
        self.current_track_info = None
        self.last_stream_title = ""
        self._stop_metadata_worker()
        
        # Call parent play method
        super().play(url, volume)
    
    def stop(self):
        """Override stop method to clean up metadata polling."""
        self._stop_metadata_polling()
        super().stop()
    
    def get_current_track_info(self) -> Optional[Dict[str, Any]]:
        """Get the current track information."""
        return self.current_track_info
    
    def set_metadata_poll_interval(self, interval_ms: int):
        """Set the metadata polling interval in milliseconds."""
        self.metadata_poll_interval = max(5000, interval_ms)  # Minimum 5 seconds
        if self.metadata_timer.isActive():
            self.metadata_timer.setInterval(self.metadata_poll_interval)
    
    def force_metadata_update(self):
        """Force an immediate metadata update."""
        if self.is_playing():
            self._check_metadata()
    
    def download_current_cover_art(self, output_path: str) -> bool:
        """Download the cover art of the current track."""
        if not self.current_track_info or not self.current_track_info.get('cover_art_url'):
            return False
        
        return self.mb_client.download_cover_art(
            self.current_track_info['cover_art_url'],
            output_path
        )