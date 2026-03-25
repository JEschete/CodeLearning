"""
Persistent user preferences for AntennaForge.

Reads / writes a simple JSON file stored next to AntennaForge.py
(or in the gui/ directory when running as ``python -m gui``).
"""

import json
import os

_PREFS_FILENAME = "antennaforge_prefs.json"

# Resolve to the project root (one level above gui/)
_PREFS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFS_PATH = os.path.join(_PREFS_DIR, _PREFS_FILENAME)


def load_prefs() -> dict:
    """Load preferences from disk.  Returns {} on any error."""
    try:
        with open(PREFS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_prefs(prefs: dict) -> str:
    """Write preferences to disk.  Returns the path written."""
    with open(PREFS_PATH, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)
    return PREFS_PATH
