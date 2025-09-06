"""Card Widgets for Radio Player"""

from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QSize, QUrl, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QLinearGradient, QPen, QPixmap, QPaintEvent
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class GlassCard(QFrame):
    """Glass morphism card widget with blur effect."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        # Styling is now handled by theme.qss


class StationCard(QWidget):
    """Card widget for displaying radio station information."""
    clicked = Signal(dict)
    
    def __init__(self, station_data: dict, parent=None):
        super().__init__(parent)
        self.station_data = station_data
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_image_downloaded)
        self.setFixedSize(200, 250)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("StationCard")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create glass card container
        self.card = GlassCard()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # Thumbnail container
        self.thumbnail_container = QWidget()
        self.thumbnail_container.setFixedSize(170, 170)
        self.thumbnail_container.setObjectName("ThumbnailContainer")
        
        # Thumbnail label
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(170, 170)
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.thumbnail.setObjectName("Thumbnail")
        
        # Play overlay
        self.play_overlay = QLabel()
        self.play_overlay.setFixedSize(170, 170)
        self.play_overlay.setAlignment(Qt.AlignCenter)
        self.play_overlay.setObjectName("PlayOverlay")
        self.play_overlay.hide()
        
        # Layout for thumbnail container
        thumb_layout = QVBoxLayout(self.thumbnail_container)
        thumb_layout.setContentsMargins(0, 0, 0, 0)
        thumb_layout.addWidget(self.thumbnail)
        
        # Position play overlay absolutely over the thumbnail
        self.play_overlay.setParent(self.thumbnail_container)
        self.play_overlay.move(0, 0)  # Position at top-left of container
        
        # Station name
        self.name_label = QLabel(station_data.get('name', 'Unknown Station'))
        self.name_label.setObjectName("StationName")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignCenter)
        
        # Station info
        country = station_data.get('country', '')
        genre = station_data.get('tags', '')
        info_text = f"{country} • {genre}" if country and genre else country or genre or 'Unknown'
        self.info_label = QLabel(info_text)
        self.info_label.setObjectName("StationInfo")
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to card layout
        card_layout.addWidget(self.thumbnail_container)
        card_layout.addWidget(self.name_label)
        card_layout.addWidget(self.info_label)
        card_layout.addStretch()
        
        # Add card to main layout
        layout.addWidget(self.card)
        
        # Load thumbnail
        self._load_thumbnail()
        
        # Set static play overlay style
        self.play_overlay.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 120);
                border-radius: 15px;
                color: white;
                font-size: 48px;
                font-weight: bold;
            }
        """)
        self.play_overlay.setText("▶")
    
    def _load_thumbnail(self):
        """Load station thumbnail from favicon URL."""
        favicon_url = self.station_data.get('favicon')
        if favicon_url:
            request = QNetworkRequest(QUrl(favicon_url))
            request.setRawHeader(b'User-Agent', b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            self.network_manager.get(request)
        else:
            self._set_default_thumbnail()
    
    def _on_image_downloaded(self, reply: QNetworkReply):
        """Handle downloaded image data."""
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                # Scale and set pixmap
                scaled_pixmap = pixmap.scaled(170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.thumbnail.setPixmap(scaled_pixmap)
            else:
                self._set_default_thumbnail()
        else:
            self._set_default_thumbnail()
        reply.deleteLater()
    
    def _set_default_thumbnail(self):
        """Set default thumbnail with gradient background."""
        pixmap = QPixmap(170, 170)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient
        gradient = QLinearGradient(0, 0, 170, 170)
        gradient.setColorAt(0, QColor(100, 100, 255, 100))
        gradient.setColorAt(1, QColor(255, 100, 100, 100))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 170, 170, 15, 15)
        
        # Draw music note icon (simple representation)
        painter.setPen(QPen(QColor(255, 255, 255, 150), 3))
        painter.drawEllipse(60, 80, 20, 20)
        painter.drawLine(80, 90, 80, 50)
        painter.drawLine(80, 50, 100, 45)
        painter.drawLine(100, 45, 100, 75)
        
        painter.end()
        self.thumbnail.setPixmap(pixmap)
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        self.play_overlay.show()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self.play_overlay.hide()
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.station_data)