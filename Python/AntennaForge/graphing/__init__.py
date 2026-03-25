"""Pattern visualization — heatmaps, cuts, polar, 3D, overlays."""

import logging

logger = logging.getLogger(__name__)

HAS_MATPLOTLIB = False
HAS_NUMPY = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt       # noqa: F401
    import matplotlib.colors as mcolors   # noqa: F401
    from matplotlib.gridspec import GridSpec  # noqa: F401
    HAS_MATPLOTLIB = True
except ImportError:
    pass

try:
    import numpy as np   # noqa: F401
    HAS_NUMPY = True
except ImportError:
    pass


def check_plot_deps() -> bool:
    """Return ``True`` if matplotlib + numpy are available."""
    if not HAS_MATPLOTLIB:
        logger.error("matplotlib required. Install with: pip install matplotlib")
        return False
    if not HAS_NUMPY:
        logger.error("numpy required. Install with: pip install numpy")
        return False
    return True
