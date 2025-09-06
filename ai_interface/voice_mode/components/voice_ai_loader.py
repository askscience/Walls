"""Voice-enabled AI Loader Component

Extends the standard AI loader for voice mode interface.
"""

import os
import sys
from PySide6.QtWidgets import QWidget

# Import gui_core components
gui_core_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'gui_core')
if gui_core_path not in sys.path:
    sys.path.insert(0, gui_core_path)

from gui_core.components.ai_loader.widgets import AiLoaderBig


class VoiceAiLoader(AiLoaderBig):
    """AI Loader for voice mode interface."""
    
    def __init__(self, animated: bool = False, active: bool = True, parent=None):
        super().__init__(animated=animated, active=active, parent=parent)
    
    def set_voice_mode_active(self, active: bool):
        """Set visual state to indicate voice mode is active."""
        if active:
            # Make loader more active/animated when voice mode is on
            self.setActive(True)
            self.start()
        else:
            # Return to normal state
            self.setActive(False)
            self.stop()
    
    def pulse_for_voice_activity(self):
        """Create a visual pulse effect for voice activity."""
        from PySide6.QtCore import QTimer
        # Temporarily increase activity
        self.setActive(True)
        
        # Reset after a short delay
        QTimer.singleShot(500, lambda: self.setActive(False))