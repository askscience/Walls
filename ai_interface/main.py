#!/usr/bin/env python3
"""AI Interface Launcher

Main entry point for the AI interface application.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from main.interface import create_ai_interface_app


def main():
    """Main entry point for the AI interface."""
    try:
        # Create the application and interface
        app, interface = create_ai_interface_app()
        
        # Show the interface
        interface.show_interface()
        
        print("AI Interface started successfully!")
        print("- Input panel positioned at bottom of screen")
        print("- Type your questions and press Enter")
        print("- AI responses will appear in the center panel")
        print("- Press Ctrl+C to exit")
        
        # Run the application
        return app.exec()
        
    except KeyboardInterrupt:
        print("\nShutting down AI Interface...")
        return 0
    except Exception as e:
        print(f"Error starting AI Interface: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())