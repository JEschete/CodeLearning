"""
Dependency availability checker for AntennaForge.

Reports which optional libraries are installed so the application
can gracefully degrade on standalone / air-gapped systems.

Usage:
    from core.deps import HAS_NUMPY, HAS_SCIPY, HAS_MATPLOTLIB, HAS_PIL
    from core.deps import check_all, missing_summary
"""

import importlib
import logging

logger = logging.getLogger(__name__)

# ── Probe optional packages ─────────────────────────────────────

HAS_NUMPY = False
HAS_SCIPY = False
HAS_MATPLOTLIB = False
HAS_PIL = False
HAS_PPTX = False

try:
    import numpy  # noqa: F401
    HAS_NUMPY = True
except ImportError:
    pass

try:
    import scipy  # noqa: F401
    HAS_SCIPY = True
except ImportError:
    pass

try:
    import matplotlib  # noqa: F401
    HAS_MATPLOTLIB = True
except ImportError:
    pass

try:
    from PIL import Image  # noqa: F401
    HAS_PIL = True
except ImportError:
    pass

try:
    import pptx  # noqa: F401
    HAS_PPTX = True
except ImportError:
    pass

# ── Summary helpers ─────────────────────────────────────────────

_PACKAGES = {
    "numpy":      {"flag": "HAS_NUMPY",      "pip": "numpy",      "required_for": "Vectorized computation (50–100× faster)"},
    "scipy":      {"flag": "HAS_SCIPY",       "pip": "scipy",      "required_for": "Dish antenna Bessel patterns, bicubic interpolation"},
    "matplotlib": {"flag": "HAS_MATPLOTLIB",  "pip": "matplotlib", "required_for": "All graphing / plot generation"},
    "pillow":     {"flag": "HAS_PIL",         "pip": "Pillow",     "required_for": "Embedded plot preview in GUI"},
    "python-pptx":{"flag": "HAS_PPTX",        "pip": "python-pptx","required_for": "PowerPoint report generation"},
}


def check_all() -> dict[str, bool]:
    """Return dict of {package_name: is_installed}."""
    return {
        "numpy":      HAS_NUMPY,
        "scipy":      HAS_SCIPY,
        "matplotlib": HAS_MATPLOTLIB,
        "pillow":     HAS_PIL,
        "python-pptx":HAS_PPTX,
    }


def missing_packages() -> list[str]:
    """Return list of missing optional package names."""
    return [name for name, avail in check_all().items() if not avail]


def missing_summary() -> str:
    """Human-readable summary of missing dependencies."""
    missing = missing_packages()
    if not missing:
        return "All optional dependencies are installed."
    lines = ["Missing optional dependencies:\n"]
    for name in missing:
        info = _PACKAGES[name]
        lines.append(f"  • {name} — {info['required_for']}")
        lines.append(f"    Install: pip install {info['pip']}")
    lines.append("\nCore functionality (pattern generation, CSV I/O) works without these.")
    return "\n".join(lines)


def require(package_name: str, feature: str = "this feature") -> bool:
    """Check if a package is available; log an error if not.

    Returns True if available, False if missing.
    """
    status = check_all()
    pkg_key = package_name.lower()
    if pkg_key == "pil":
        pkg_key = "pillow"
    if pkg_key not in status:
        logger.warning("Unknown dependency: %s", package_name)
        return False
    if not status[pkg_key]:
        info = _PACKAGES.get(pkg_key, {})
        pip_name = info.get("pip", package_name)
        logger.error(
            "%s requires '%s'. Install with: pip install %s",
            feature, package_name, pip_name,
        )
        return False
    return True


def install_command() -> str:
    """Return pip command to install all optional dependencies."""
    return "pip install numpy scipy matplotlib Pillow"


def print_status():
    """Print dependency status to stdout."""
    status = check_all()
    print("\nAntennaForge Dependency Status:")
    print("=" * 50)
    for name, available in status.items():
        info = _PACKAGES[name]
        mark = "✓" if available else "✗"
        print(f"  {mark}  {name:<14} — {info['required_for']}")
    missing = missing_packages()
    if missing:
        print(f"\nInstall missing: pip install {' '.join(_PACKAGES[m]['pip'] for m in missing)}")
    else:
        print("\nAll dependencies satisfied.")
    print()
