import os
import threading
import time
from typing import Optional, Callable, Dict, Any
from pathlib import Path

try:
    from PySide6.QtCore import QObject, Signal, QTimer, QApplication
    from PySide6.QtWidgets import QApplication as QWidgetsApplication
    from PySide6.QtGui import QFontDatabase
except ImportError:
    QObject = object
    Signal = None
    QTimer = None
    QApplication = None
    QWidgetsApplication = None
    QFontDatabase = None

from .system_theme_detector import SystemThemeDetector, ThemeMode


class AdaptiveThemeManager(QObject if QObject != object else object):
    """Manages adaptive theming based on system theme detection."""
    
    # Signals for theme changes (only available if PySide6 is imported)
    if Signal is not None:
        theme_changed = Signal(str)  # Emits 'light' or 'dark'
        theme_applied = Signal(str)  # Emits theme name after successful application
    
    def __init__(self, base_dir: Optional[str] = None):
        if QObject != object:
            super().__init__()
        
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.current_theme: Optional[ThemeMode] = None
        self.theme_mode: ThemeMode = ThemeMode.AUTO
        self.monitoring_enabled = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        self.app: Optional[QWidgetsApplication] = None  # Store app reference for monitoring
        
        # Theme change callbacks
        self.theme_callbacks: Dict[str, Callable[[str], None]] = {}
        
        # Cache for loaded themes
        self._theme_cache: Dict[str, str] = {}
    
    def set_theme_mode(self, mode: ThemeMode) -> None:
        """Set the theme mode (AUTO, LIGHT, or DARK).
        
        Args:
            mode: The theme mode to set
        """
        self.theme_mode = mode
        self.apply_theme()
    
    def get_current_theme(self) -> ThemeMode:
        """Get the currently active theme.
        
        Returns:
            ThemeMode: The current theme (LIGHT or DARK)
        """
        if self.theme_mode == ThemeMode.AUTO:
            return SystemThemeDetector.get_system_theme()
        return self.theme_mode
    
    def apply_theme(self, app: Optional[QWidgetsApplication] = None) -> bool:
        """Apply the appropriate theme based on current settings.
        
        Args:
            app: Optional QApplication instance. If None, tries to get current app.
            
        Returns:
            bool: True if theme was applied successfully, False otherwise
        """
        target_theme = self.get_current_theme()
        
        # Don't reapply if theme hasn't changed
        if self.current_theme == target_theme:
            return True
        
        # Get the application instance
        if app is None and QWidgetsApplication is not None:
            app = QWidgetsApplication.instance()
        
        # Store app reference for monitoring
        if app is not None:
            self.app = app
        
        if app is None:
            return False
        
        # Load and apply the theme
        theme_content = self._load_theme(target_theme)
        if theme_content:
            # Load fonts before applying theme
            self._load_fonts()
            
            # Apply the stylesheet
            app.setStyleSheet(theme_content)
            
            # Update current theme
            old_theme = self.current_theme
            self.current_theme = target_theme
            
            # Emit signals and call callbacks
            theme_name = target_theme.value
            if hasattr(self, 'theme_changed') and self.theme_changed is not None:
                self.theme_changed.emit(theme_name)
            if hasattr(self, 'theme_applied') and self.theme_applied is not None:
                self.theme_applied.emit(theme_name)
            
            # Call registered callbacks
            for callback in self.theme_callbacks.values():
                try:
                    callback(theme_name)
                except Exception as e:
                    print(f"Error in theme callback: {e}")
            
            return True
        
        return False
    
    def set_theme(self, app: Optional[QWidgetsApplication], theme_mode: ThemeMode) -> bool:
        """Manually set a specific theme mode.
        
        Args:
            app: QApplication instance
            theme_mode: The theme mode to apply (DARK or LIGHT)
            
        Returns:
            bool: True if theme was applied successfully
        """
        # Temporarily disable monitoring to prevent conflicts
        was_monitoring = self.monitoring_enabled
        if was_monitoring:
            self.stop_monitoring_themes()
        
        # Force the theme change
        old_theme = self.current_theme
        self.current_theme = theme_mode
        
        # Apply the theme
        success = self.apply_theme(app)
        
        # Re-enable monitoring if it was enabled
        if was_monitoring:
            self.start_monitoring()
        
        return success
    
    def _load_theme(self, theme: ThemeMode) -> Optional[str]:
        """Load theme content from file.
        
        Args:
            theme: The theme to load
            
        Returns:
            Optional[str]: The theme content or None if loading failed
        """
        theme_name = theme.value
        
        # Check cache first
        if theme_name in self._theme_cache:
            return self._theme_cache[theme_name]
        
        # Determine theme file path
        if theme == ThemeMode.DARK:
            theme_file = self.base_dir / "theme_dark.qss"
        else:  # ThemeMode.LIGHT
            theme_file = self.base_dir / "theme_light.qss"
        
        # Fallback to original theme.qss if specific theme file doesn't exist
        if not theme_file.exists():
            theme_file = self.base_dir / "theme.qss"
        
        if not theme_file.exists():
            return None
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Cache the content
                self._theme_cache[theme_name] = content
                return content
        except (IOError, OSError) as e:
            print(f"Error loading theme file {theme_file}: {e}")
            return None
    
    def _load_fonts(self) -> None:
        """Load application fonts."""
        if QFontDatabase is None:
            return
        
        fonts_root = self.base_dir / "utils" / "fonts" / "Mozilla_Headline"
        if not fonts_root.exists():
            return
        
        # Load variable font if available
        variable_font = fonts_root / "MozillaHeadline-VariableFont_wdth,wght.ttf"
        if variable_font.exists():
            try:
                QFontDatabase.addApplicationFont(str(variable_font))
            except Exception:
                pass
        
        # Load static fonts
        static_dir = fonts_root / "static"
        if static_dir.exists():
            for font_file in static_dir.glob("*.ttf"):
                try:
                    QFontDatabase.addApplicationFont(str(font_file))
                except Exception:
                    pass
    
    def start_monitoring(self, interval: float = 2.0) -> None:
        """Start monitoring system theme changes.
        
        Args:
            interval: Check interval in seconds
        """
        if self.monitoring_enabled:
            return
        
        self.monitoring_enabled = True
        self.stop_monitoring.clear()
        
        # Always use threading instead of Qt timer to avoid threading issues
        self.monitor_thread = threading.Thread(
            target=self._monitor_theme_changes,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring_themes(self) -> None:
        """Stop monitoring system theme changes."""
        if not self.monitoring_enabled:
            return
        
        self.monitoring_enabled = False
        self.stop_monitoring.set()
        
        # Wait for thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_theme_changes(self, interval: float) -> None:
        """Monitor system theme changes in a separate thread.
        
        Args:
            interval: Check interval in seconds
        """
        while not self.stop_monitoring.is_set():
            try:
                self._check_theme_change()
                time.sleep(interval)
            except Exception as e:
                print(f"Error in theme monitoring: {e}")
                time.sleep(interval)
    
    def _check_theme_change(self) -> None:
        """Check if system theme has changed and apply if necessary."""
        if self.theme_mode != ThemeMode.AUTO:
            return
        
        current_system_theme = SystemThemeDetector.get_system_theme()
        if current_system_theme != self.current_theme:
            self.apply_theme(self.app)
    
    def register_theme_callback(self, name: str, callback: Callable[[str], None]) -> None:
        """Register a callback to be called when theme changes.
        
        Args:
            name: Unique name for the callback
            callback: Function to call with theme name ('light' or 'dark')
        """
        self.theme_callbacks[name] = callback
    
    def unregister_theme_callback(self, name: str) -> None:
        """Unregister a theme callback.
        
        Args:
            name: Name of the callback to remove
        """
        self.theme_callbacks.pop(name, None)
    
    def clear_theme_cache(self) -> None:
        """Clear the theme content cache."""
        self._theme_cache.clear()
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get information about current theme state.
        
        Returns:
            Dict containing theme information
        """
        return {
            'current_theme': self.current_theme.value if self.current_theme else None,
            'theme_mode': self.theme_mode.value,
            'system_theme': SystemThemeDetector.get_system_theme().value,
            'monitoring_enabled': self.monitoring_enabled,
            'available_themes': ['light', 'dark'],
            'cached_themes': list(self._theme_cache.keys())
        }
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop_monitoring_themes()


# Global theme manager instance
_theme_manager: Optional[AdaptiveThemeManager] = None


def get_theme_manager(base_dir: Optional[str] = None) -> AdaptiveThemeManager:
    """Get the global theme manager instance.
    
    Args:
        base_dir: Base directory for theme files (only used on first call)
        
    Returns:
        AdaptiveThemeManager: The global theme manager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = AdaptiveThemeManager(base_dir)
    return _theme_manager


def apply_adaptive_theme(app: Optional[QWidgetsApplication] = None, 
                        base_dir: Optional[str] = None,
                        enable_monitoring: bool = True) -> bool:
    """Apply adaptive theme to the application.
    
    Args:
        app: QApplication instance
        base_dir: Base directory for theme files
        enable_monitoring: Whether to enable automatic theme monitoring
        
    Returns:
        bool: True if theme was applied successfully
    """
    manager = get_theme_manager(base_dir)
    
    # Apply initial theme
    success = manager.apply_theme(app)
    
    # Start monitoring if requested
    if enable_monitoring and success:
        manager.start_monitoring()
    
    return success