#!/usr/bin/env python3
"""
AntennaForge — GUI Launcher
====================================
Double-click this file or run:  python AntennaForge.py
For a console-free launch, use:  AntennaForge.pyw
"""

import sys, os

# Hide the console window on Windows when launched via double-click
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0)   # SW_HIDE
    except Exception:
        pass

# Ensure the tool's package directory is importable
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

# Also allow importing the parent so 'antenna_tool.xxx' works
_parent = os.path.dirname(_here)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from gui.app import launch

if __name__ == "__main__":
    launch()
