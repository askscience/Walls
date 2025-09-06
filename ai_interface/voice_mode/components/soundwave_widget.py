"""Soundwave Animation Widget

Animated soundwave visualization for voice mode with pastel colors.
"""

import math
import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QLinearGradient


class SoundwaveWidget(QWidget):
    """Animated soundwave visualization widget with pastel colors."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Widget properties
        self.setFixedSize(120, 50)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Animation properties - optimized for performance
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(100)  # Reduced to 10 FPS for better performance
        
        # Soundwave properties - reduced complexity
        self.wave_count = 3  # Reduced from 5 to 3 waves
        self.wave_heights = [0.4, 0.8, 0.6]  # Relative heights
        self.wave_phases = [0.0] * self.wave_count
        self.wave_speeds = [0.1, 0.15, 0.12]  # Slower speeds for smoother animation
        
        # Animation state
        self.is_animating = False
        self.animation_intensity = 1.0  # 0.0 to 1.0
        
        # Performance optimization: cache calculated values
        self._cached_bars = []
        self._cache_valid = False
        self._frame_counter = 0
        
        # Pastel colors for soundwaves
        self.wave_colors = [
            QColor(255, 182, 193, 180),  # Light pink
            QColor(173, 216, 230, 180),  # Light blue
            QColor(144, 238, 144, 180),  # Light green
            QColor(255, 218, 185, 180),  # Peach
            QColor(221, 160, 221, 180),  # Plum
        ]
        
        # Start animation by default
        self.start_animation()
    
    def start_animation(self, intensity: float = 1.0):
        """Start the soundwave animation."""
        self.animation_intensity = max(0.1, min(1.0, intensity))
        if not self.is_animating:
            self.is_animating = True
            self.animation_timer.start()
    
    def stop_animation(self):
        """Stop the soundwave animation."""
        self.is_animating = False
        self.animation_timer.stop()
        self.update()
    
    def set_intensity(self, intensity: float):
        """Set animation intensity (0.0 to 1.0)."""
        self.animation_intensity = max(0.1, min(1.0, intensity))
    
    def update_animation(self):
        """Update animation frame - optimized for performance."""
        self._frame_counter += 1
        
        # Update wave phases
        for i in range(self.wave_count):
            self.wave_phases[i] += self.wave_speeds[i]
            if self.wave_phases[i] > 2 * math.pi:
                self.wave_phases[i] -= 2 * math.pi
        
        # Add randomness less frequently for better performance
        if self._frame_counter % 10 == 0:  # Only every 10th frame (1 second at 10 FPS)
            for i in range(self.wave_count):
                self.wave_heights[i] += random.uniform(-0.05, 0.05)  # Smaller variations
                self.wave_heights[i] = max(0.3, min(1.0, self.wave_heights[i]))
        
        # Invalidate cache when animation updates
        self._cache_valid = False
        self.update()
    
    def paintEvent(self, event):
        """Paint the soundwave visualization - optimized for performance."""
        painter = QPainter(self)
        # Disable antialiasing for better performance
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        if not self.is_animating:
            # Draw static minimal waves when not animating
            self._draw_static_waves(painter)
            return
        
        # Use cached bars if available and valid
        if self._cache_valid and self._cached_bars:
            self._draw_cached_bars(painter)
        else:
            # Calculate and cache new bars
            self._calculate_and_cache_bars()
            self._draw_cached_bars(painter)
    
    def _draw_static_waves(self, painter: QPainter):
        """Draw static minimal soundwaves."""
        width = self.width()
        height = self.height()
        center_y = height // 2
        
        # Draw minimal static bars
        bar_width = 4
        bar_spacing = 8
        bar_count = width // (bar_width + bar_spacing)
        
        for i in range(bar_count):
            x = i * (bar_width + bar_spacing) + bar_spacing
            bar_height = 10 + (i % 3) * 5  # Vary height slightly
            
            # Use muted colors for static state
            color = self.wave_colors[i % len(self.wave_colors)]
            color.setAlpha(80)  # More transparent
            
            painter.setPen(QPen(color, bar_width, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(x, center_y - bar_height // 2, x, center_y + bar_height // 2)
    
    def _calculate_and_cache_bars(self):
        """Calculate and cache bar properties for optimized rendering."""
        width = self.width()
        height = self.height()
        center_y = height // 2
        
        # Optimized bar properties
        bar_width = 6
        bar_spacing = 4
        bar_count = min(12, width // (bar_width + bar_spacing))  # Limit bar count for performance
        
        self._cached_bars = []
        
        for i in range(bar_count):
            x = i * (bar_width + bar_spacing) + bar_spacing
            
            # Simplified wave calculation - use only primary wave
            primary_wave = 0
            wave_pos = (i / bar_count) * 2 * math.pi + self.wave_phases[0]
            primary_wave = math.sin(wave_pos) * self.wave_heights[0] * self.animation_intensity
            
            # Add secondary wave for variety (reduced complexity)
            if len(self.wave_phases) > 1:
                secondary_pos = (i / bar_count) * math.pi + self.wave_phases[1]
                primary_wave += math.sin(secondary_pos) * self.wave_heights[1] * 0.5
            
            # Normalize and scale wave height
            wave_height = abs(primary_wave) * 0.7  # Reduced multiplier
            bar_height = int(12 + wave_height * (height - 24))
            bar_height = max(10, min(height - 6, bar_height))
            
            # Simplified color selection
            color_index = i % len(self.wave_colors)
            color = QColor(self.wave_colors[color_index])
            
            # Fixed alpha for better performance
            alpha = int(140 + wave_height * 60)
            color.setAlpha(min(220, alpha))
            
            # Cache bar properties
            self._cached_bars.append({
                'x': x,
                'y1': center_y - bar_height // 2,
                'y2': center_y + bar_height // 2,
                'color': color,
                'width': bar_width
            })
        
        self._cache_valid = True
    
    def _draw_cached_bars(self, painter: QPainter):
        """Draw bars using cached properties for optimal performance."""
        for bar in self._cached_bars:
            painter.setPen(QPen(bar['color'], bar['width'], Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(bar['x'], bar['y1'], bar['x'], bar['y2'])
    
    def set_listening_mode(self, is_listening: bool):
        """Set visual state for listening mode."""
        if is_listening:
            self.start_animation(1.0)
        else:
            self.start_animation(0.3)
    
    def set_speaking_mode(self, is_speaking: bool):
        """Set visual state for speaking mode."""
        if is_speaking:
            self.start_animation(1.5)  # More intense animation
        else:
            self.start_animation(0.5)
    
    def set_processing_mode(self, is_processing: bool):
        """Set visual state for processing mode."""
        if is_processing:
            self.start_animation(0.8)
        else:
            self.start_animation(0.3)