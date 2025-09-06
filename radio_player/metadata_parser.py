import re
import requests
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class StreamMetadataParser:
    """Parser for extracting metadata from Icecast/SHOUTcast radio streams."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RadioPlayer/1.0',
            'Icy-MetaData': '1'  # Request metadata from stream
        })
    
    def get_stream_metadata(self, stream_url: str, timeout: int = 10) -> Optional[Dict[str, str]]:
        """
        Fetch metadata from an Icecast/SHOUTcast stream.
        
        Args:
            stream_url: The URL of the radio stream
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing stream metadata or None if failed
        """
        try:
            # Make a HEAD request first to get stream info
            response = self.session.head(stream_url, timeout=timeout, allow_redirects=True)
            
            if response.status_code != 200:
                logger.warning(f"Stream returned status {response.status_code}")
                return None
            
            # Check if stream supports metadata
            if 'icy-metaint' not in response.headers:
                logger.info("Stream does not support ICY metadata")
                return self._try_alternative_metadata(stream_url, timeout)
            
            metaint = int(response.headers['icy-metaint'])
            
            # Get stream data with metadata
            response = self.session.get(
                stream_url, 
                timeout=timeout, 
                stream=True,
                headers={'Icy-MetaData': '1'}
            )
            
            if response.status_code != 200:
                return None
            
            # Read audio data up to metadata block
            audio_data = response.raw.read(metaint)
            if len(audio_data) < metaint:
                logger.warning("Insufficient audio data received")
                return None
            
            # Read metadata length (1 byte)
            meta_length_byte = response.raw.read(1)
            if not meta_length_byte:
                return None
            
            meta_length = ord(meta_length_byte) * 16
            
            if meta_length == 0:
                logger.info("No metadata available")
                return None
            
            # Read metadata
            metadata_raw = response.raw.read(meta_length)
            if len(metadata_raw) < meta_length:
                logger.warning("Incomplete metadata received")
                return None
            
            # Parse metadata
            metadata_str = metadata_raw.decode('utf-8', errors='ignore').rstrip('\x00')
            parsed_metadata = self._parse_metadata_string(metadata_str)
            
            # Try to get additional station info from headers
            alt_metadata = self._try_alternative_metadata(stream_url, timeout)
            if alt_metadata:
                parsed_metadata.update(alt_metadata)
            
            return parsed_metadata
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def _try_alternative_metadata(self, stream_url: str, timeout: int) -> Optional[Dict[str, str]]:
        """
        Try alternative methods to get metadata when ICY metadata is not available.
        
        Args:
            stream_url: The URL of the radio stream
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing stream metadata or None if failed
        """
        try:
            # Try to get station info from headers
            response = self.session.head(stream_url, timeout=timeout)
            metadata = {}
            
            # Extract common stream headers
            if 'icy-name' in response.headers:
                metadata['station'] = response.headers['icy-name']
            if 'icy-description' in response.headers:
                metadata['description'] = response.headers['icy-description']
            if 'icy-genre' in response.headers:
                metadata['genre'] = response.headers['icy-genre']
            if 'icy-url' in response.headers:
                metadata['url'] = response.headers['icy-url']
            
            return metadata if metadata else None
            
        except Exception as e:
            logger.error(f"Alternative metadata extraction failed: {e}")
            return None
    
    def _parse_metadata_string(self, metadata_str: str) -> Dict[str, str]:
        """
        Parse the raw metadata string into a dictionary.
        
        Args:
            metadata_str: Raw metadata string from stream
            
        Returns:
            Dictionary containing parsed metadata
        """
        metadata = {}
        
        # Common patterns for metadata parsing
        patterns = [
            r"StreamTitle='([^']*)';",
            r"StreamTitle=\"([^\"]*)\";?",
            r"StreamTitle=([^;]+);",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, metadata_str)
            if match:
                metadata['StreamTitle'] = match.group(1).strip()
                break
        
        # Try to extract StreamUrl if present
        url_patterns = [
            r"StreamUrl='([^']*)';",
            r"StreamUrl=\"([^\"]*)\";?",
            r"StreamUrl=([^;]+);",
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, metadata_str)
            if match:
                metadata['StreamUrl'] = match.group(1).strip()
                break
        
        return metadata
    
    def extract_artist_title(self, stream_title: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract artist and title from StreamTitle metadata.
        
        Args:
            stream_title: The StreamTitle string from metadata
            
        Returns:
            Tuple of (artist, title) or (None, None) if extraction fails
        """
        if not stream_title or not stream_title.strip():
            return None, None
        
        # Clean up the stream title
        title = stream_title.strip()
        
        # Common separators used in radio streams
        separators = [' - ', ' – ', ' — ', ' | ', ': ', ' / ']
        
        for separator in separators:
            if separator in title:
                parts = title.split(separator, 1)
                if len(parts) == 2:
                    artist = parts[0].strip()
                    song_title = parts[1].strip()
                    
                    # Validate that both parts are meaningful
                    if artist and song_title and len(artist) > 0 and len(song_title) > 0:
                        return artist, song_title
        
        # If no separator found, try to detect patterns
        # Pattern: "Artist Name Song Title" (less reliable)
        words = title.split()
        if len(words) >= 4:  # At least 2 words for artist and 2 for title
            # Try splitting in the middle
            mid = len(words) // 2
            artist = ' '.join(words[:mid])
            song_title = ' '.join(words[mid:])
            return artist, song_title
        
        # If all else fails, return the whole string as title
        return None, title
    
    def get_current_track(self, stream_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the currently playing track from a radio stream.
        
        Args:
            stream_url: The URL of the radio stream
            
        Returns:
            Tuple of (artist, title) or (None, None) if extraction fails
        """
        metadata = self.get_stream_metadata(stream_url)
        if not metadata or 'StreamTitle' not in metadata:
            return None, None
        
        return self.extract_artist_title(metadata['StreamTitle'])
