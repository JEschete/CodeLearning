"""
Antenna type registry.

Sub-packages (lpda/, omni/, etc.) register themselves on import.
Call discover() once at startup to import all sub-packages.
"""

import importlib
import pathlib
import pkgutil

from .base import AntennaBase

REGISTRY: dict = {}


def register(antenna: AntennaBase) -> None:
    """Register an antenna type instance."""
    REGISTRY[antenna.name] = antenna


def get_antenna(name: str) -> AntennaBase:
    """Look up a registered antenna by name."""
    if name not in REGISTRY:
        raise KeyError(
            f"Unknown antenna type '{name}'. "
            f"Available: {list(REGISTRY.keys())}"
        )
    return REGISTRY[name]


def available_names() -> list[str]:
    """Return list of registered antenna type names."""
    return list(REGISTRY.keys())


def discover() -> None:
    """Import all antenna sub-packages so they auto-register.

    Each sub-package's __init__.py is expected to call
    register() with an instance of its antenna class.
    """
    pkg_dir = pathlib.Path(__file__).parent
    for info in pkgutil.iter_modules([str(pkg_dir)]):
        if info.ispkg:
            importlib.import_module(
                f".{info.name}", __package__
            )


# Auto-discover on first import of this package
discover()
