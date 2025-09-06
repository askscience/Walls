from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QGraphicsDropShadowEffect, QFrame, QGraphicsOpacityEffect
)
from PySide6.QtCore import QTimer, Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QColor, QIcon
import os

class Notification(QWidget):
    closed = Signal()
    actionTriggered = Signal(str)  # Action button clicked with action name

    def __init__(self, title: str = "", subtitle: str = "", 
                 kind: str = "info", timeout_ms: int = 5000, 
                 app_icon: str = None, actions: list = None, parent=None):
        super().__init__(parent)
        self.setObjectName("notification")
        self.setProperty("kind", kind)
        # Remove top-level window flags so layout can stack them normally
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        # Translucent background not required for child widgets, keep harmless
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(380)  # macOS-like width
        
        # Main container with shadow
        self.container = QFrame(self)
        self.container.setObjectName("notificationContainer")
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(4, 4, 4, 4)  # Space for shadow
        container_layout.addWidget(self.container)
        
        # Add drop shadow effect (soft blur-like)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.container.setGraphicsEffect(shadow)

        # Opacity effect for fade-in/out
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)
        
        self._setup_layout(title, subtitle, app_icon, actions)
        
        # Auto-close timer
        if timeout_ms > 0:
            self.close_timer = QTimer()
            self.close_timer.timeout.connect(self.close)
            self.close_timer.start(timeout_ms)
        
        # Prepare animations
        self.fade_in_anim = None
        self.fade_out_anim = None

    def _icons_dir(self) -> str:
        # widgets.py -> notifications -> components -> gui_core
        pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(pkg_root, "utils", "icons")

    def _resolve_icon_path(self, icon_name: str | None) -> str | None:
        if not icon_name:
            return None
        # Absolute path
        if os.path.isabs(icon_name) and os.path.exists(icon_name):
            return icon_name
        # Try relative to icons dir
        candidate = os.path.join(self._icons_dir(), icon_name)
        if os.path.exists(candidate):
            return candidate
        return None

    def _get_default_icon_path(self) -> str | None:
        kind = self.property("kind") or "info"
        mapping = {
            "info": "information.svg",
            "success": "circle-check.svg",
            "warning": "exclamation.svg",
            "error": "circle-xmark.svg",
        }
        icon_name = mapping.get(kind, "information.svg")
        return self._resolve_icon_path(icon_name)
        
    def _setup_layout(self, title: str, subtitle: str, app_icon: str, actions: list):
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(16, 12, 12, 12)
        layout.setSpacing(12)
        
        # App icon (left side)
        self.icon_label = QLabel()
        self.icon_label.setObjectName("notificationIcon")
        self.icon_label.setFixedSize(32, 32)
        resolved_icon = self._resolve_icon_path(app_icon) if app_icon else self._get_default_icon_path()
        if resolved_icon:
            pixmap = QIcon(resolved_icon).pixmap(32, 32)
            self.icon_label.setPixmap(pixmap)
        else:
            # Fallback emoji if icon not found
            self.icon_label.setText(self._get_default_icon_emoji())
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.icon_label)
        
        # Content area (title + subtitle)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("notificationTitle")
            self.title_label.setWordWrap(False)
            content_layout.addWidget(self.title_label)
        
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("notificationSubtitle")
            self.subtitle_label.setWordWrap(True)
            content_layout.addWidget(self.subtitle_label)
        
        content_layout.addStretch()
        layout.addLayout(content_layout, 1)
        
        # Actions and close button (right side)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)
        
        # Close button (top-right)
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("notificationCloseBtn")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.close)
        right_layout.addWidget(self.close_btn, 0, Qt.AlignRight)
        
        # Action buttons
        if actions:
            for action in actions:
                btn = QPushButton(action)
                btn.setObjectName("notificationActionBtn")
                btn.clicked.connect(lambda checked, a=action: self.actionTriggered.emit(a))
                right_layout.addWidget(btn)
        
        right_layout.addStretch()
        layout.addLayout(right_layout)
    
    def _get_default_icon_emoji(self):
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌"
        }
        return icons.get(self.property("kind"), "ℹ️")
    
    def showAnimated(self, target_pos=None):
        """Show notification with fade-in; avoid moving widgets managed by layouts."""
        self._opacity_effect.setOpacity(0.0)
        self.show()
        self.fade_in_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(220)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in_anim.start()
    
    def hideAnimated(self):
        """Hide notification with fade-out then close."""
        self.fade_out_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(180)
        self.fade_out_anim.setStartValue(self._opacity_effect.opacity())
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_out_anim.finished.connect(self.close)
        self.fade_out_anim.start()
    
    def enterEvent(self, event):
        """Pause auto-close timer on hover"""
        if hasattr(self, 'close_timer') and self.close_timer.isActive():
            self.close_timer.stop()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Resume auto-close timer on leave"""
        if hasattr(self, 'close_timer'):
            self.close_timer.start(2000)  # Extended time after hover
        super().leaveEvent(event)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

class NotificationCenter(QWidget):
    """Top-right stacked notifications container with vertical layout (newest on top)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Keep frameless but as child overlay window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("notificationCenter")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        self._margin = 16
        self._fixed_width = 380 + 8  # align with notification width + margins
        self.setFixedWidth(self._fixed_width)
        
        # Track notifications
        self._notifications = []

    def _reposition(self):
        # Anchor at top-right of parent
        if self.parent() and isinstance(self.parent(), QWidget):
            parent = self.parent()
            geo = parent.rect()
            x = geo.width() - self.width() - self._margin
            y = self._margin
            self.move(x, y)
        else:
            # If no parent, keep at top-right of primary screen
            screen = self.screen().geometry()
            self.move(screen.width() - self.width() - self._margin, self._margin)

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            self.parent().installEventFilter(self)
        self._reposition()

    def eventFilter(self, watched, event):
        if watched is self.parent():
            et = event.type()
            if et in (12, 14):  # Move, Resize
                self._reposition()
        return super().eventFilter(watched, event)

    def showNotification(self, title_or_text: str, kind: str = "info", timeout_ms: int = 5000, subtitle: str = "", app_icon: str = None, actions: list = None):
        # Create new notification
        n = Notification(title=title_or_text, subtitle=subtitle, kind=kind, timeout_ms=timeout_ms, app_icon=app_icon, actions=actions, parent=self)
        n.closed.connect(lambda: self._on_closed(n))
        n.actionTriggered.connect(lambda a: self._on_action(n, a))

        n.setMaximumHeight(0)  # start collapsed
        self._layout.insertWidget(0, n)  # newest on top
        self._notifications.insert(0, n)
        self.adjustSize()
        self._reposition()

        n.showAnimated()

        target_h = n.sizeHint().height()
        expand_anim = QPropertyAnimation(n, b"maximumHeight")
        expand_anim.setDuration(220)
        expand_anim.setStartValue(0)
        expand_anim.setEndValue(target_h)
        expand_anim.setEasingCurve(QEasingCurve.OutCubic)
        expand_anim.start()
        n._expand_anim = expand_anim

        self.show()

    def _on_closed(self, n: 'Notification'):
        try:
            self._layout.removeWidget(n)
        except Exception:
            pass
        if n in self._notifications:
            self._notifications.remove(n)
        n.deleteLater()
        self.adjustSize()
        self._reposition()

    def _on_action(self, n: 'Notification', action: str):
        pass