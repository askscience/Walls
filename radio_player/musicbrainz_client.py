import musicbrainzngs
import requests
from typing import Optional, Dict, List, Any
import logging
import time
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class MusicBrainzClient:
    """Client for interacting with MusicBrainz database and Cover Art Archive."""
    
    def __init__(self, app_name: str = "RadioPlayer", app_version: str = "1.0", contact: str = "user@example.com"):
        """
        Initialize the MusicBrainz client.
        
        Args:
            app_name: Name of your application
            app_version: Version of your application
            contact: Contact information (required by MusicBrainz)
        """
        # Set user agent for MusicBrainz API (required)
        musicbrainzngs.set_useragent(app_name, app_version, contact)
        
        # Rate limiting to respect MusicBrainz API guidelines (1 request per second)
        self._last_request_time = 0
        self._min_request_interval = 1.0  # seconds
        
        # Session for Cover Art Archive requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'{app_name}/{app_version} ({contact})'
        })
    
    def _rate_limit(self):
        """Ensure we don't exceed MusicBrainz rate limits."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def search_recordings(self, artist: str, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for recordings in MusicBrainz database.
        
        Args:
            artist: Artist name
            title: Track title
            limit: Maximum number of results to return
            
        Returns:
            List of recording dictionaries
        """
        try:
            self._rate_limit()
            
            # Build search query
            query = f'artist:"{artist}" AND recording:"{title}"'
            
            logger.info(f"Searching MusicBrainz for: {query}")
            
            result = musicbrainzngs.search_recordings(
                query=query,
                limit=limit,
                offset=0
            )
            
            recordings = result.get('recording-list', [])
            logger.info(f"Found {len(recordings)} recordings")
            
            return recordings
            
        except musicbrainzngs.WebServiceError as e:
            logger.error(f"MusicBrainz API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching recordings: {e}")
            return []
    
    def get_recording_details(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific recording.
        
        Args:
            recording_id: MusicBrainz recording ID (MBID)
            
        Returns:
            Recording details dictionary or None if not found
        """
        try:
            self._rate_limit()
            
            result = musicbrainzngs.get_recording_by_id(
                recording_id,
                includes=['artists', 'releases', 'tags', 'ratings']
            )
            
            return result.get('recording')
            
        except musicbrainzngs.WebServiceError as e:
            logger.error(f"MusicBrainz API error getting recording details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting recording details: {e}")
            return None
    
    def get_release_cover_art(self, release_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cover art information for a release from Cover Art Archive.
        
        Args:
            release_id: MusicBrainz release ID (MBID)
            
        Returns:
            Cover art information dictionary or None if not found
        """
        try:
            # Cover Art Archive URL
            url = f"https://coverartarchive.org/release/{release_id}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                cover_data = response.json()
                return cover_data
            elif response.status_code == 404:
                logger.info(f"No cover art found for release {release_id}")
                return None
            else:
                logger.warning(f"Cover Art Archive returned status {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error fetching cover art: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching cover art: {e}")
            return None
    
    def get_best_cover_art_url(self, cover_data: Dict[str, Any], size: str = "large") -> Optional[str]:
        """
        Extract the best cover art URL from cover art data.
        
        Args:
            cover_data: Cover art data from Cover Art Archive
            size: Preferred image size ('small', 'large', or 'original')
            
        Returns:
            Cover art URL or None if not available
        """
        try:
            images = cover_data.get('images', [])
            
            if not images:
                return None
            
            # Look for front cover first
            front_images = [img for img in images if img.get('front', False)]
            
            # If no front cover, use the first available image
            target_images = front_images if front_images else images
            
            if not target_images:
                return None
            
            # Get the first (usually best) image
            image = target_images[0]
            
            # Try to get the requested size
            thumbnails = image.get('thumbnails', {})
            
            if size in thumbnails:
                return thumbnails[size]
            elif 'large' in thumbnails:
                return thumbnails['large']
            elif 'small' in thumbnails:
                return thumbnails['small']
            else:
                # Fall back to original image
                return image.get('image')
                
        except Exception as e:
            logger.error(f"Error extracting cover art URL: {e}")
            return None
    
    def find_track_info(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """
        Find comprehensive track information including cover art.
        
        Args:
            artist: Artist name
            title: Track title
            
        Returns:
            Dictionary containing track info and cover art URL, or None if not found
        """
        try:
            # Search for recordings
            recordings = self.search_recordings(artist, title)
            
            if not recordings:
                logger.info(f"No recordings found for {artist} - {title}")
                return None
            
            # Try each recording to find one with cover art
            for recording in recordings:
                recording_id = recording['id']
                
                # Get detailed recording info
                details = self.get_recording_details(recording_id)
                if not details:
                    continue
                
                # Look for releases with cover art
                releases = details.get('release-list', [])
                
                for release in releases:
                    release_id = release['id']
                    
                    # Try to get cover art for this release
                    cover_data = self.get_release_cover_art(release_id)
                    
                    if cover_data:
                        cover_url = self.get_best_cover_art_url(cover_data)
                        
                        if cover_url:
                            # Compile track information
                            track_info = {
                                'recording_id': recording_id,
                                'release_id': release_id,
                                'artist': artist,
                                'title': title,
                                'mb_artist': recording.get('artist-credit', [{}])[0].get('name', artist),
                                'mb_title': recording.get('title', title),
                                'release_title': release.get('title', ''),
                                'release_date': release.get('date', ''),
                                'cover_art_url': cover_url,
                                'cover_art_data': cover_data,
                                'recording_data': details
                            }
                            
                            logger.info(f"Found track info with cover art for {artist} - {title}")
                            return track_info
                
                # If we get here, this recording had no cover art
                # But we can still return basic info
                if not releases:  # Only if we haven't found anything better
                    track_info = {
                        'recording_id': recording_id,
                        'artist': artist,
                        'title': title,
                        'mb_artist': recording.get('artist-credit', [{}])[0].get('name', artist),
                        'mb_title': recording.get('title', title),
                        'cover_art_url': None,
                        'recording_data': details
                    }
                    
                    logger.info(f"Found basic track info (no cover art) for {artist} - {title}")
                    return track_info
            
            logger.info(f"No suitable track info found for {artist} - {title}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding track info: {e}")
            return None
    
    def download_cover_art(self, cover_url: str, output_path: str) -> bool:
        """
        Download cover art image to a file.
        
        Args:
            cover_url: URL of the cover art image
            output_path: Path where to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(cover_url, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Cover art downloaded to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading cover art: {e}")
            return False