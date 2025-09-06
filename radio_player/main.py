#!/usr/bin/env python3
"""
Radio Player - Main Entry Point
Launches the modern GUI interface by default.
"""

import sys
import os

# Add parent directory to path for shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from radio_player.modern_gui import main

if __name__ == "__main__":
    main()