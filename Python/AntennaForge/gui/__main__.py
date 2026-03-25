"""
Launch the AntennaForge GUI.

Usage:
    python -m antenna_tool.gui
    python AntennaForge.py
"""

import sys, os

# Ensure the package root is on sys.path
_here = os.path.dirname(os.path.abspath(__file__))
_pkg_root = os.path.dirname(_here)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from gui.app import launch

if __name__ == "__main__":
    launch()
