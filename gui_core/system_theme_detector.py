import os
import sys
import platform
from typing import Literal, Optional
from enum import Enum

try:
    from PySide6.QtCore import QSettings
except ImportError:
    QSettings = None


class ThemeMode(Enum):
    """Enumeration for theme modes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class SystemThemeDetector:
    """Cross-platform system theme detection."""
    
    @staticmethod
    def get_system_theme() -> ThemeMode:
        """Detect the current system theme across platforms.
        
        Returns:
            ThemeMode: The detected system theme (LIGHT or DARK)
        """
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return SystemThemeDetector._get_macos_theme()
        elif system == "windows":
            return SystemThemeDetector._get_windows_theme()
        elif system == "linux":
            return SystemThemeDetector._get_linux_theme()
        else:
            # Fallback to light theme for unknown systems
            return ThemeMode.LIGHT
    
    @staticmethod
    def _get_macos_theme() -> ThemeMode:
        """Detect macOS system theme using AppleScript."""
        try:
            import subprocess
            result = subprocess.run([
                "osascript", "-e", 
                "tell application \"System Events\" to tell appearance preferences to get dark mode"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                is_dark = result.stdout.strip().lower() == "true"
                return ThemeMode.DARK if is_dark else ThemeMode.LIGHT
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Fallback: Check NSUserDefaults if available
        try:
            import subprocess
            result = subprocess.run([
                "defaults", "read", "-g", "AppleInterfaceStyle"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and "Dark" in result.stdout:
                return ThemeMode.DARK
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return ThemeMode.LIGHT
    
    @staticmethod
    def _get_windows_theme() -> ThemeMode:
        """Detect Windows system theme using registry."""
        try:
            import winreg
            
            # Check Windows 10/11 theme setting
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    # AppsUseLightTheme: 0 = dark, 1 = light
                    apps_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return ThemeMode.LIGHT if apps_light_theme else ThemeMode.DARK
            except (FileNotFoundError, OSError):
                pass
            
            # Fallback: Check system theme
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    system_light_theme, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                    return ThemeMode.LIGHT if system_light_theme else ThemeMode.DARK
            except (FileNotFoundError, OSError):
                pass
                
        except ImportError:
            # winreg not available (not on Windows)
            pass
        except Exception:
            # Any other registry access error
            pass
        
        return ThemeMode.LIGHT
    
    @staticmethod
    def _get_linux_theme() -> ThemeMode:
        """Detect Linux system theme using various methods."""
        # Method 1: Check GNOME/GTK settings
        theme = SystemThemeDetector._get_gtk_theme()
        if theme != ThemeMode.LIGHT:
            return theme
        
        # Method 2: Check KDE Plasma settings
        theme = SystemThemeDetector._get_kde_theme()
        if theme != ThemeMode.LIGHT:
            return theme
        
        # Method 3: Check environment variables
        theme = SystemThemeDetector._get_env_theme()
        if theme != ThemeMode.LIGHT:
            return theme
        
        # Method 4: Check freedesktop.org color scheme preference
        theme = SystemThemeDetector._get_freedesktop_theme()
        if theme != ThemeMode.LIGHT:
            return theme
        
        return ThemeMode.LIGHT
    
    @staticmethod
    def _get_gtk_theme() -> ThemeMode:
        """Check GTK theme settings."""
        try:
            import subprocess
            
            # Try gsettings first (GNOME)
            try:
                result = subprocess.run([
                    "gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    theme_name = result.stdout.strip().strip("'\"")
                    if any(dark_indicator in theme_name.lower() for dark_indicator in 
                           ["dark", "adwaita-dark", "yaru-dark", "breeze-dark"]):
                        return ThemeMode.DARK
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Try checking color-scheme preference (newer GNOME)
            try:
                result = subprocess.run([
                    "gsettings", "get", "org.gnome.desktop.interface", "color-scheme"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    color_scheme = result.stdout.strip().strip("'\"")
                    if "dark" in color_scheme.lower():
                        return ThemeMode.DARK
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                pass
                
        except Exception:
            pass
        
        return ThemeMode.LIGHT
    
    @staticmethod
    def _get_kde_theme() -> ThemeMode:
        """Check KDE Plasma theme settings."""
        try:
            # Check KDE config files
            kde_config_paths = [
                os.path.expanduser("~/.config/kdeglobals"),
                os.path.expanduser("~/.kde4/share/config/kdeglobals"),
                os.path.expanduser("~/.kde/share/config/kdeglobals")
            ]
            
            for config_path in kde_config_paths:
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            content = f.read()
                            # Look for dark theme indicators
                            if any(indicator in content.lower() for indicator in 
                                   ["breeze dark", "breezedark", "colorscheme=breezedark"]):
                                return ThemeMode.DARK
                    except (IOError, OSError):
                        continue
        except Exception:
            pass
        
        return ThemeMode.LIGHT
    
    @staticmethod
    def _get_env_theme() -> ThemeMode:
        """Check environment variables for theme hints."""
        # Check common environment variables
        env_vars = [
            "GTK_THEME",
            "QT_STYLE_OVERRIDE",
            "DESKTOP_SESSION"
        ]
        
        for var in env_vars:
            value = os.environ.get(var, "").lower()
            if any(dark_indicator in value for dark_indicator in ["dark", "breeze-dark"]):
                return ThemeMode.DARK
        
        return ThemeMode.LIGHT
    
    @staticmethod
    def _get_freedesktop_theme() -> ThemeMode:
        """Check freedesktop.org color scheme preference."""
        try:
            import subprocess
            
            # Check for portal settings
            try:
                result = subprocess.run([
                    "dbus-send", "--session", "--print-reply", "--dest=org.freedesktop.portal.Desktop",
                    "/org/freedesktop/portal/desktop", "org.freedesktop.portal.Settings.Read",
                    "string:org.freedesktop.appearance", "string:color-scheme"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and "uint32 1" in result.stdout:
                    return ThemeMode.DARK
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                pass
                
        except Exception:
            pass
        
        return ThemeMode.LIGHT
    
    @staticmethod
    def is_dark_theme() -> bool:
        """Check if the current system theme is dark.
        
        Returns:
            bool: True if dark theme is detected, False otherwise
        """
        return SystemThemeDetector.get_system_theme() == ThemeMode.DARK
    
    @staticmethod
    def is_light_theme() -> bool:
        """Check if the current system theme is light.
        
        Returns:
            bool: True if light theme is detected, False otherwise
        """
        return SystemThemeDetector.get_system_theme() == ThemeMode.LIGHT