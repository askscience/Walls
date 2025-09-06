"""Main Window for Radio Player Application"""

import sys
from typing import List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QSlider, QGraphicsDropShadowEffect, QApplication
)
from PySide6.QtCore import Qt, QTimer, QUrl, QRectF
from PySide6.QtGui import QColor, QPixmap, QPainter, QPainterPath, QFontDatabase
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Import our custom widgets
from .widgets import (
    FlowLayout, ModernButton, IconButton, GlassCard, StationCard,
    SidebarItem, VisualizerWidget
)

# Import backend components
from .radio_browser import RadioBrowserClient
from .enhanced_player import EnhancedRadioPlayer

# Add parent directory for shared server
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_server.server import get_shared_server
# Define icons directory relative to repository root
ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gui_core', 'utils', 'icons')


class ModernRadioPlayer(QWidget):
    """Modern Radio Player main window with glass morphism design."""
    
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("Radio Player")
        self.setGeometry(100, 100, 1200, 700)
        
        # Player backend
        self.client = RadioBrowserClient()
        self.player = EnhancedRadioPlayer()
        self.current_station = None
        
        # Network manager for async requests
        self.network_manager = QNetworkAccessManager()
        
        # Track previous metadata to prevent redundant updates
        self.previous_track_info = None
        
        # Seeking state
        self._seeking = False
        
        # Setup UI
        self._setup_ui()
        self._wire_signals()
        
        # Defer server registration and initial station loading to improve startup time
        QTimer.singleShot(50, self._register_with_shared_server)
        QTimer.singleShot(100, self._load_initial_stations)
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main gradient background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Background widget
        self.bg_widget = QWidget()
        self.bg_widget.setObjectName("BackgroundWidget")
        
        bg_layout = QHBoxLayout(self.bg_widget)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)
        
        # Left sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setObjectName("Sidebar")
        # Also set as ID for CSS
        self.sidebar.setProperty("id", "Sidebar")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 30, 0, 30)
        sidebar_layout.setSpacing(0)
        
        # Logo/Title with visualizer
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 0, 20, 0)
        
        self.mini_viz = VisualizerWidget()
        self.mini_viz.setFixedSize(60, 40)
        logo_layout.addWidget(self.mini_viz)
        logo_layout.addStretch()
        
        sidebar_layout.addWidget(logo_widget)
        sidebar_layout.addSpacing(40)
        
        # Menu section
        menu_label = QLabel("Menu")
        menu_label.setObjectName("MenuLabel")
        sidebar_layout.addWidget(menu_label)
        sidebar_layout.addSpacing(10)
        
        # Navigation items
        self.nav_items = []
        nav_data = [
            ("radio.svg", "Radio"),
            ("music-note.svg", "Songs"),
            ("album.svg", "Albums"),
            ("user.svg", "Artists"),
            ("heart.svg", "Liked"),
        ]
        
        for icon, text in nav_data:
            icon_path = os.path.join(ICONS_DIR, icon)
            item = SidebarItem(icon_path, text, text.lower())
            item.clicked.connect(self.on_nav_clicked)
            self.nav_items.append(item)
            sidebar_layout.addWidget(item)
        
        # Set Radio as selected by default
        self.nav_items[0].set_active(True)
        
        sidebar_layout.addSpacing(30)
        
        # Playlists section
        playlist_label = QLabel("PLAYLISTS")
        playlist_label.setObjectName("PlaylistLabel")
        sidebar_layout.addWidget(playlist_label)
        sidebar_layout.addSpacing(10)
        
        # Playlist items
        playlist_names = ["Classic", "Romantic", "Sad Song"]
        for name in playlist_names:
            icon_path = os.path.join(ICONS_DIR, 'list.svg')
            item = SidebarItem(icon_path, name, name.lower())
            sidebar_layout.addWidget(item)
        
        # Add button
        add_icon_path = os.path.join(ICONS_DIR, 'plus.svg')
        add_btn = SidebarItem(add_icon_path, "+Add", "add")
        sidebar_layout.addWidget(add_btn)
        
        sidebar_layout.addStretch()
        
        bg_layout.addWidget(self.sidebar)
        
        # Main content area
        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(30, 30, 30, 100)
        content_layout.setSpacing(20)
        
        # Top bar with search and profile
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        self.title_label = QLabel("NEW COLLECTION\nFOR YOU")
        self.title_label.setObjectName("TitleLabel")
        top_layout.addWidget(self.title_label)
        
        top_layout.addStretch()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.setObjectName("SearchBar")
        top_layout.addWidget(self.search_bar)
        
        # Profile
        profile = QLabel()
        profile.setFixedSize(40, 40)
        profile.setObjectName("ProfileAvatar")
        top_layout.addWidget(profile)
        
        content_layout.addWidget(top_bar)
        
        # Station cards scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("StationScrollArea")
        
        self.cards_widget = QWidget()
        self.cards_layout = FlowLayout(self.cards_widget, margin=0, spacing=5)
        
        scroll.setWidget(self.cards_widget)
        content_layout.addWidget(scroll)
        
        bg_layout.addWidget(self.content_area)
        
        # Player bar at bottom
        self.player_bar = QWidget()
        self.player_bar.setFixedHeight(80)
        self.player_bar.setObjectName("PlayerBar")
        # Also set as ID for CSS
        self.player_bar.setProperty("id", "PlayerBar")
        
        player_layout = QHBoxLayout(self.player_bar)
        player_layout.setContentsMargins(20, 0, 20, 0)
        player_layout.setSpacing(20)
        player_layout.setAlignment(Qt.AlignVCenter)
        
        # Now playing info
        now_playing = QWidget()
        now_layout = QHBoxLayout(now_playing)
        now_layout.setContentsMargins(0, 0, 0, 0)
        now_layout.setSpacing(12)
        
        # Album art
        self.album_art = QLabel()
        self.album_art.setFixedSize(50, 50)
        self.album_art.setObjectName("AlbumArt")
        now_layout.addWidget(self.album_art)
        
        # Track info
        track_info = QWidget()
        track_layout = QVBoxLayout(track_info)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(2)
        
        self.track_name = QLabel("Select a station")
        self.track_name.setObjectName("TrackName")
        track_layout.addWidget(self.track_name)
        
        self.artist_name = QLabel("Radio Player")
        self.artist_name.setObjectName("ArtistName")
        track_layout.addWidget(self.artist_name)
        
        now_layout.addWidget(track_info)
        now_layout.addStretch()
        
        player_layout.addWidget(now_playing, 1)
        
        # Player controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(15)
        controls_layout.setAlignment(Qt.AlignVCenter)
        
        # Control buttons
        self.btn_prev = IconButton(os.path.join(ICONS_DIR, 'backward-step.svg'))
        self.btn_play = IconButton(os.path.join(ICONS_DIR, 'play.svg'), 48)
        self.btn_next = IconButton(os.path.join(ICONS_DIR, 'forward-step.svg'))
        
        controls_layout.addWidget(self.btn_prev)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_next)
        
        player_layout.addWidget(controls)
        
        # Progress bar and time
        progress_widget = QWidget()
        progress_widget.setFixedWidth(300)
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(5)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setObjectName("ProgressSlider")
        progress_layout.addWidget(self.progress_slider)
        
        # Time labels
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.time_current = QLabel("2:30")
        self.time_current.setObjectName("TimeLabel")
        time_layout.addWidget(self.time_current)
        time_layout.addStretch()
        
        self.time_total = QLabel("4:30")
        self.time_total.setObjectName("TimeLabel")
        time_layout.addWidget(self.time_total)
        
        progress_layout.addWidget(time_widget)
        
        # Store reference to progress widget and hide by default (for radio streams)
        self.progress_widget = progress_widget
        self.progress_widget.hide()  # Hidden by default for radio streams
        
        player_layout.addWidget(progress_widget)
        
        # Volume control
        volume_widget = QWidget()
        volume_layout = QHBoxLayout(volume_widget)
        volume_layout.setSpacing(10)
        volume_layout.setAlignment(Qt.AlignVCenter)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setObjectName("VolumeSlider")
        volume_layout.addWidget(self.volume_slider)
        
        player_layout.addWidget(volume_widget)
        
        # Stack player bar on top of content
        main_widget = QWidget()
        main_widget_layout = QVBoxLayout(main_widget)
        main_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_widget_layout.setSpacing(0)
        main_widget_layout.addWidget(self.bg_widget, 1)
        main_widget_layout.addWidget(self.player_bar, 0)
        
        main_layout.addWidget(main_widget)
        
        # Apply shadow to main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        main_widget.setGraphicsEffect(shadow)
    
    def _wire_signals(self):
        """Connect all signals."""
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_prev.clicked.connect(self.play_previous)
        self.btn_next.clicked.connect(self.play_next)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.search_bar.returnPressed.connect(self.on_search)
        
        # Player signals
        self.player.stateChanged.connect(self.on_player_state_changed)
        self.player.errorOccurred.connect(self.on_player_error)
        self.player.metadataError.connect(self.on_metadata_error)
        self.player.trackChanged.connect(self.on_track_changed)
        self.player.coverArtFound.connect(self.on_cover_art_found)
        self.player.levelsUpdated.connect(self.mini_viz.set_levels)
        
        # Progress bar signals
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.positionChanged.connect(self.on_position_changed)
        self.progress_slider.sliderPressed.connect(self.on_seek_start)
        self.progress_slider.sliderReleased.connect(self.on_seek_end)
        self.progress_slider.valueChanged.connect(self.on_seek_changed)
    
    def _load_initial_stations(self):
        """Load some initial radio stations."""
        try:
            # Get popular stations
            stations = self.client.search(limit=12)
            self.display_stations(stations)
        except Exception as e:
            print(f"Failed to load stations: {e}")
    
    def _load_songs(self):
        """Load songs (placeholder functionality)"""
        # Placeholder for songs functionality
        self._show_placeholder_message("Songs feature coming soon")
    
    def display_stations(self, stations: List[Dict]):
        """Display station cards in flow layout."""
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.takeAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Add new cards to flow layout
        for station in stations[:12]:  # Limit to 12 stations
            card = StationCard(station)
            card.clicked.connect(self.play_station)
            self.cards_layout.addWidget(card)
    
    def on_nav_clicked(self, item_id: str):
        """Handle navigation item clicks."""
        # Update selection
        for item in self.nav_items:
            item.set_active(item.item_id == item_id)
        
        # Update title based on selection
        title_map = {
            "radio": "NEW COLLECTION\nFOR YOU",
            "songs": "MUSIC\nSONGS",
            "albums": "DISCOVER\nALBUMS",
            "artists": "TOP\nARTISTS",
            "liked": "LIKED\nTRACKS"
        }
        
        if item_id in title_map:
            self.title_label.setText(title_map[item_id])
        
        # Load appropriate content
        if item_id == "radio":
            self._load_initial_stations()
        elif item_id == "songs":
            self._load_songs()
        else:
            # Clear current content for other sections
            self._clear_content()
            # Show placeholder message for non-radio sections
            self._show_placeholder_message(f"Coming soon: {item_id.title()} section")
    
    def _clear_content(self):
        """Clear all content from the cards area."""
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.takeAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def _show_placeholder_message(self, message: str):
        """Show a placeholder message in the content area."""
        placeholder = QLabel(message)
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setObjectName("PlaceholderMessage")
        self.cards_layout.addWidget(placeholder)
    
    def on_search(self):
        """Handle search."""
        query = self.search_bar.text().strip()
        if query:
            try:
                stations = self.client.search(name=query, limit=12)
                self.display_stations(stations)
            except Exception as e:
                print(f"Search failed: {e}")
    
    def play_station(self, station: Dict):
        """Play selected station."""
        try:
            self.current_station = station
            # Reset previous track info when changing stations
            self.previous_track_info = None
            # Reset album art to favicon fallback
            self._reset_album_art_placeholder()
            
            url = self.client.resolved_url(station)
            if url:
                self.player.play(url, volume=self.volume_slider.value())
                self.track_name.setText(station.get('name', 'Unknown'))
                self.artist_name.setText(station.get('countrycode', 'Radio'))
                # Update visualizer state
                self.mini_viz.set_playing(True)
            else:
                self.on_player_error("No valid stream URL found")
        except Exception as e:
            self.on_player_error(f"Failed to start playback: {str(e)}")
    
    def toggle_play(self):
        """Toggle play/pause."""
        try:
            if self.player.is_playing():
                self.player.pause()
                self.mini_viz.set_playing(False)
            elif self.current_station:
                self.play_station(self.current_station)
            else:
                self.on_player_error("No station selected")
        except Exception as e:
            self.on_player_error(f"Toggle play failed: {str(e)}")
    
    def play_previous(self):
        """Play previous station (placeholder)."""
        pass
    
    def play_next(self):
        """Play next station (placeholder)."""
        pass
    
    def on_volume_changed(self, value: int):
        """Handle volume changes."""
        self.player.set_volume(value)
    
    def on_player_state_changed(self, state: str):
        """Update UI based on player state."""
        if state == "playing":
            icon_path = os.path.join(ICONS_DIR, 'pause.svg')
            self.mini_viz.set_playing(True)
        else:
            icon_path = os.path.join(ICONS_DIR, 'play.svg')
            self.mini_viz.set_playing(False)
        self.btn_play.icon_path = icon_path
        self.btn_play.update()
    
    def on_player_error(self, error_msg: str):
        """Handle player errors gracefully."""
        print(f"Player error: {error_msg}")
        # Update UI to show error state
        self.track_name.setText("Playback Error")
        self.artist_name.setText(f"Error: {error_msg}")
        # Reset play button to play state
        icon_path = os.path.join(ICONS_DIR, 'play.svg')
        self.btn_play.icon_path = icon_path
        self.btn_play.update()
        self.mini_viz.set_playing(False)
    
    def on_metadata_error(self, error_msg: str):
        """Handle metadata errors gracefully without stopping playback."""
        print(f"Metadata error: {error_msg}")
        # Don't update UI for metadata errors as they shouldn't affect playback
    
    def on_track_changed(self, track_info: Dict):
        """Update track information only if it has changed."""
        # Check if track info has actually changed
        if self.previous_track_info == track_info:
            return  # No change, skip update
        
        self.previous_track_info = track_info.copy()
        
        if track_info.get('title'):
            self.track_name.setText(track_info['title'])
        if track_info.get('artist'):
            self.artist_name.setText(track_info['artist'])
    
    def on_duration_changed(self, duration: int):
        """Handle duration changes - show/hide progress based on content type."""
        # Radio streams typically have duration 0 or very large values
        # Real songs have meaningful durations (usually < 10 minutes)
        is_song = 0 < duration < 600000  # 0 to 10 minutes in milliseconds
        
        if is_song:
            # Show progress widget for real songs
            self.progress_widget.show()
            self.progress_slider.setMaximum(duration)
            # Update time labels
            total_time = self._format_time(duration)
            self.time_total.setText(total_time)
        else:
            # Hide progress widget for radio streams
            self.progress_widget.hide()
    
    def on_position_changed(self, position: int):
        """Handle position changes for real songs."""
        if self.progress_widget.isVisible() and not getattr(self, '_seeking', False):
            self.progress_slider.setValue(position)
            current_time = self._format_time(position)
            self.time_current.setText(current_time)
    
    def on_seek_start(self):
        """Handle seek start."""
        self._seeking = True
    
    def on_seek_end(self):
        """Handle seek end."""
        self._seeking = False
        # Apply the seek position
        position = self.progress_slider.value()
        self.player.set_position(position)
    
    def on_seek_changed(self, value: int):
        """Handle seek slider changes during dragging."""
        if getattr(self, '_seeking', False):
            current_time = self._format_time(value)
            self.time_current.setText(current_time)
    
    def _format_time(self, milliseconds: int) -> str:
        """Format time from milliseconds to MM:SS format."""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def on_cover_art_found(self, cover_url: str):
        """Download and display cover art asynchronously."""
        try:
            # Use QNetworkAccessManager for async download
            request = QNetworkRequest(cover_url)
            request.setRawHeader(b"User-Agent", b"RadioPlayer/1.0")
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda: self._on_cover_art_downloaded(reply))
        except Exception as e:
            print(f"Error requesting cover art: {e}")
            # Fallback to favicon or placeholder
            self._reset_album_art_placeholder()
    
    def _on_cover_art_downloaded(self, reply):
        """Handle downloaded cover art data."""
        try:
            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                
                if not pixmap.isNull():
                    # Scale the image to fit the album art widget
                    scaled_pixmap = pixmap.scaled(
                        self.album_art.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    
                    # Create rounded corners for the pixmap
                    rounded_pixmap = self._create_rounded_pixmap(scaled_pixmap, 8)
                    self.album_art.setPixmap(rounded_pixmap)
                    
                    # Remove background styling when we have cover art
                    self.album_art.setStyleSheet("""
                        QLabel {
                            background: transparent;
                        }
                    """)
                else:
                    # Cover art failed, try favicon fallback
                    self._reset_album_art_placeholder()
            else:
                # MusicBrainz cover art failed, try favicon fallback
                self._reset_album_art_placeholder()
        except Exception as e:
            print(f"Error loading cover art: {e}")
            # MusicBrainz cover art failed, try favicon fallback
            self._reset_album_art_placeholder()
        finally:
            reply.deleteLater()
    
    def _create_rounded_pixmap(self, pixmap: QPixmap, radius: int) -> QPixmap:
        """Create a pixmap with rounded corners."""
        size = pixmap.size()
        rounded_pixmap = QPixmap(size)
        rounded_pixmap.fill(Qt.transparent)
        
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(rounded_pixmap.rect()), radius, radius)
        
        # Clip to the rounded rectangle and draw the original pixmap
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return rounded_pixmap
    
    def _reset_album_art_placeholder(self):
        """Reset album art to station favicon or default gradient placeholder."""
        self.album_art.clear()
        
        # Try to use station favicon as fallback
        if self.current_station and self.current_station.get('favicon'):
            favicon_url = self.current_station.get('favicon')
            if favicon_url and favicon_url.strip():
                # Load favicon as fallback
                self._load_favicon_fallback(favicon_url)
                return
        
        # Default gradient fallback if no favicon
        self._set_default_album_art_gradient()
    
    def _set_default_album_art_gradient(self):
        """Set default gradient background for album art."""
        self.album_art.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 8px;
            }
        """)
    
    def _load_favicon_fallback(self, favicon_url: str):
        """Load station favicon as fallback for album art asynchronously."""
        try:
            # Use QNetworkAccessManager for async download
            request = QNetworkRequest(favicon_url)
            request.setRawHeader(b"User-Agent", b"RadioPlayer/1.0")
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda: self._on_favicon_downloaded(reply))
        except Exception as e:
            print(f"Error requesting favicon: {e}")
            # Use default gradient fallback
            self._set_default_album_art_gradient()
    
    def _on_favicon_downloaded(self, reply):
        """Handle downloaded favicon data."""
        try:
            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                
                if not pixmap.isNull():
                    # Scale the image to fit the album art widget
                    scaled_pixmap = pixmap.scaled(
                        self.album_art.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    
                    # Create rounded corners for the pixmap
                    rounded_pixmap = self._create_rounded_pixmap(scaled_pixmap, 8)
                    self.album_art.setPixmap(rounded_pixmap)
                    
                    # Remove background styling when we have favicon
                    self.album_art.setStyleSheet("""
                        QLabel {
                            background: transparent;
                        }
                    """)
                    return
            
            # Fallback to default gradient if favicon fails
            self._set_default_album_art_gradient()
            
        except Exception as e:
            print(f"Error processing favicon: {e}")
            self._set_default_album_art_gradient()
        finally:
            reply.deleteLater()
    
    def _register_with_shared_server(self):
        """Register this application with the shared server for CLI commands."""
        try:
            server = get_shared_server()
            port = server.register_app('radio_player', self._handle_cli_command, 'Radio Player GUI')
            server.start()
            print(f"Radio Player registered with shared server on port {port}")
        except Exception as e:
            print(f"Failed to register with shared server: {e}")
    
    def _handle_cli_command(self, command: str, args: dict) -> dict:
        """Handle CLI commands sent to the radio player."""
        try:
            if command == 'play':
                if self.current_station:
                    url = self.current_station.get('url_resolved') or self.current_station.get('url')
                    if url:
                        self.player.play(url)
                        return {'status': 'success', 'message': 'Playback started'}
                    else:
                        return {'status': 'error', 'message': 'No valid URL for current station'}
                else:
                    return {'status': 'error', 'message': 'No station selected'}
            
            elif command == 'pause':
                self.player.pause()
                return {'status': 'success', 'message': 'Playback paused'}
            
            elif command == 'stop':
                self.player.stop()
                return {'status': 'success', 'message': 'Playback stopped'}
            
            elif command == 'volume':
                level = args.get('level')
                if level is not None:
                    try:
                        volume = int(level)
                        if 0 <= volume <= 100:
                            self.player.set_volume(volume)
                            self.volume_slider.setValue(volume)
                            return {'status': 'success', 'message': f'Volume set to {volume}%'}
                        else:
                            return {'status': 'error', 'message': 'Volume must be between 0 and 100'}
                    except ValueError:
                        return {'status': 'error', 'message': 'Invalid volume level'}
                else:
                    current_volume = self.volume_slider.value()
                    return {'status': 'success', 'volume': current_volume}
            
            elif command == 'status':
                state = 'playing' if self.player.is_playing() else 'stopped'
                station_name = self.current_station.get('name', 'Unknown') if self.current_station else 'None'
                volume = self.volume_slider.value()
                return {
                    'status': 'success',
                    'state': state,
                    'station': station_name,
                    'volume': volume
                }
            
            elif command == 'add':
                url = args.get('url')
                name = args.get('name', 'Custom Station')
                if url:
                    # Create a custom station object
                    custom_station = {
                        'name': name,
                        'url': url,
                        'stationuuid': f'custom_{hash(url)}'
                    }
                    self.play_station(custom_station)
                    return {'status': 'success', 'message': f'Added and playing {name}'}
                else:
                    return {'status': 'error', 'message': 'URL is required'}
            
            elif command == 'next':
                self.play_next()
                return {'status': 'success', 'message': 'Switched to next station'}
            
            elif command == 'prev':
                self.play_previous()
                return {'status': 'success', 'message': 'Switched to previous station'}
            
            elif command == 'search':
                # Handle search command from CLI
                name = args.get('name')
                tag = args.get('tag')
                country = args.get('country')
                language = args.get('language')
                limit = args.get('limit', 10)
                
                try:
                    stations = self.client.search(
                        name=name,
                        tag=tag,
                        countrycode=country,
                        language=language,
                        limit=limit
                    )
                    return {
                        'status': 'success',
                        'data': {'stations': stations},
                        'message': f'Found {len(stations)} stations'
                    }
                except Exception as e:
                    return {'status': 'error', 'message': f'Search failed: {str(e)}'}
            

            else:
                return {'status': 'error', 'message': f'Unknown command: {command}'}
        
        except Exception as e:
            return {'status': 'error', 'message': f'Command failed: {str(e)}'}