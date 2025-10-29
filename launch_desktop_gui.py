#!/usr/bin/env python3
"""
Launch Desktop GUI for AI Podcast Creator
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.desktop_gui import launch_desktop_gui

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      🎙️  AI PODCAST CREATOR - DESKTOP GUI  🎙️           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Launching desktop application...
""")
    
    launch_desktop_gui()

