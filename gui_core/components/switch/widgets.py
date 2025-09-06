from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFontMetrics, QPalette
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, Property, QSize

class Switch(QCheckBox):
    """An animated on/off switch with smooth transitions.
    Replaces the static SVG-based approach with custom painting
    and animation for a more responsive UI experience.
    """
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        # Visual constants
        self._indicator_w = 38
        self._indicator_h = 20
        self._text_spacing = 8
        
        # Ensure reasonable default size; final size provided by sizeHint
        self.setMinimumSize(self._indicator_w, self._indicator_h)
        
        # Animation property for smooth transitions
        self._knob_position = 1.0 if self.isChecked() else 0.0
        self._animation = QPropertyAnimation(self, b"knobPosition")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Connect state changes to animation
        self.toggled.connect(self._animate_knob)

    @Property(float)
    def knobPosition(self):
        return self._knob_position

    @knobPosition.setter
    def knobPosition(self, position: float):
        self._knob_position = float(max(0.0, min(1.0, position)))
        self.update()

    def sizeHint(self):
        metrics = QFontMetrics(self.font())
        text = self.text()
        text_w = metrics.horizontalAdvance(text) if text else 0
        w = self._indicator_w + (self._text_spacing + text_w if text_w else 0)
        h = max(self._indicator_h, metrics.height())
        return super().sizeHint().expandedTo(QSize(w, h))

    def minimumSizeHint(self):
        return self.sizeHint()

    def _animate_knob(self, checked: bool):
        start_pos = self._knob_position
        end_pos = 1.0 if checked else 0.0
        self._animation.stop()
        self._animation.setStartValue(start_pos)
        self._animation.setEndValue(end_pos)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dimensions
        width = self._indicator_w
        height = self._indicator_h
        track_height = 12
        knob_size = 16
        
        # Indicator area at the left
        track_rect = QRect(0, (self.height() - track_height) // 2, width, track_height)
        knob_x = int(self._knob_position * (width - knob_size))
        knob_rect = QRect(knob_x, (self.height() - knob_size) // 2, knob_size, knob_size)

        # Colors
        if self.isEnabled():
            if self.isChecked():
                track_color = QColor("#333333")
                knob_color = QColor("#FFFFFF")
            else:
                track_color = QColor("#E5E7EB")
                knob_color = QColor("#FFFFFF")
        else:
            track_color = QColor("#E5E7EB")
            knob_color = QColor(255, 255, 255, 200)

        # Draw track
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(track_rect, track_height // 2, track_height // 2)

        # Draw knob shadow
        shadow_rect = knob_rect.adjusted(1, 1, 1, 1)
        painter.setBrush(QBrush(QColor(0, 0, 0, 20)))
        painter.drawEllipse(shadow_rect)

        # Draw knob
        painter.setBrush(QBrush(knob_color))
        painter.setPen(QPen(QColor("#D1D5DB"), 0.5))
        painter.drawEllipse(knob_rect)

        # Draw text to the right (if any)
        if self.text():
            text_rect = QRect(width + self._text_spacing, 0, self.width() - (width + self._text_spacing), self.height())
            pen_color = self.palette().color(QPalette.WindowText)
            painter.setPen(pen_color)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())
        
    def mousePressEvent(self, event):
        """Handle mouse press to ensure animation triggers on user interaction."""
        super().mousePressEvent(event)
        
    def keyPressEvent(self, event):
        """Handle keyboard activation (Space/Enter) with animation."""
        super().keyPressEvent(event)