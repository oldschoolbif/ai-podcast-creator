#!/usr/bin/env python3
"""
Launch Web GUI for AI Podcast Creator
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.web_interface import launch_web_interface

if __name__ == "__main__":
    print("""
============================================================
       AI PODCAST CREATOR - WEB INTERFACE
============================================================

Starting web interface...

Local URL: http://localhost:7860
To access from other devices: Use --share flag
GPU Status: Checking...
Press Ctrl+C to stop

""")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Launch AI Podcast Creator Web GUI")
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    parser.add_argument("--port", type=int, default=7860, help="Port number (default: 7860)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (0.0.0.0 for external access)")
    parser.add_argument("--auth", type=str, help="Username:password for authentication")
    
    args = parser.parse_args()
    
    # Parse auth
    auth = None
    if args.auth:
        username, password = args.auth.split(":")
        auth = (username, password)
    
    # Launch
    launch_web_interface(
        share=args.share,
        server_name=args.host,
        server_port=args.port,
        auth=auth
    )

