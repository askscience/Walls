"""Settings UI Package for configuration management."""

from .services import ConfigManager
from .settings_window import SettingsWindow

__version__ = "1.0.0"
__all__ = ["ConfigManager", "SettingsWindow"]