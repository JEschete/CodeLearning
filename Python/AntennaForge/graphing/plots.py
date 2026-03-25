"""
Single-file graph functions.

Each takes a filepath (and optional output_path) and produces
one PNG. Depends on matplotlib + numpy (checked at call time).

Plots are organized into subfolders by plot type:
  heatmaps/, cuts/, polar/, 3d_surface/
"""

import logging
import os

logger = logging.getLogger(__name__)

from graphing import check_plot_deps
from core.io import read_pattern_csv


def _build_output_path(
    filepath: str,
    suffix: str,
    subfolder: str,
    output_path: str | None = None,
) -> str:
    """Build the output PNG path in a type-specific subfolder.

    If *output_path* is explicitly given, returns it directly.
    Otherwise:  ``<csv_dir>/<subfolder>/<csv_stem>_<suffix>.png``

    Args:
        filepath: Source CSV path.
        suffix: Filename suffix (e.g. ``'heatmap'``).
        subfolder: Target subfolder name.
        output_path: Explicit override, if any.

    Returns:
        Resolved output PNG path.
    """
    if output_path is not None:
        return output_path
    folder = os.path.dirname(filepath) or "."
    sub = os.path.join(folder, subfolder)
    os.makedirs(sub, exist_ok=True)
    stem = os.path.splitext(os.path.basename(filepath))[0]
    return os.path.join(sub, f"{stem}_{suffix}.png")


def graph_heatmap(filepath: str, output_path: str | None = None) -> None:
    """Generate a heatmap of a pattern file."""
    if not check_plot_deps():
        return
    import numpy as np
    import matplotlib.pyplot as plt

    az, el, data = read_pattern_csv(filepath)
    arr = np.array(data)

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    vmin = max(arr.min(), arr.max() - 60)
    vmax = arr.max()

    AZ, EL = np.meshgrid(az, el)
    im = ax.pcolormesh(
        AZ, EL, arr,
        shading='gouraud', cmap='jet',
        vmin=vmin, vmax=vmax
    )
    ax.set_xlim(az[0], az[-1])
    ax.set_ylim(el[-1], el[0])

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Gain (dBi)', fontsize=12)

    ax.set_xlabel('Azimuth (deg)', fontsize=12)
    ax.set_ylabel('Elevation (deg)', fontsize=12)
    base = os.path.splitext(os.path.basename(filepath))[0]
    ax.set_title(f'Radiation Pattern: {base}',
                 fontsize=14)

    ax.axhline(y=0, color='white',
               linewidth=0.5, alpha=0.5)
    ax.axvline(x=0, color='white',
               linewidth=0.5, alpha=0.5)

    # Mark peak
    peak_val = arr.max()
    peak_idx = np.unravel_index(arr.argmax(), arr.shape)
    peak_az = az[peak_idx[1]]
    peak_el = el[peak_idx[0]]
    ax.plot(peak_az, peak_el, 'w+',
            markersize=15, markeredgewidth=2)
    ax.annotate(
        f'{peak_val:.1f} dBi',
        xy=(peak_az, peak_el),
        xytext=(peak_az + 20, peak_el + 20),
        color='white', fontsize=10,
        arrowprops=dict(arrowstyle='->', color='white')
    )

    plt.tight_layout()
    output_path = _build_output_path(filepath, 'heatmap', 'heatmaps', output_path)
    plt.savefig(output_path, dpi=150,
                bbox_inches='tight')
    plt.close()
    logger.info("Saved: %s", output_path)
    return output_path


def graph_cuts(filepath: str, output_path: str | None = None) -> None:
    """Generate az and el cut plots."""
    if not check_plot_deps():
        return
    import numpy as np
    import matplotlib.pyplot as plt

    az, el, data = read_pattern_csv(filepath)
    arr = np.array(data)

    az0 = len(az) // 2
    el0 = len(el) // 2

    az_cut = arr[el0, :]
    el_cut = arr[:, az0]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    base = os.path.splitext(os.path.basename(filepath))[0]

    # Az cut
    axes[0].plot(az, az_cut, 'b-', linewidth=1.5)
    axes[0].axhline(y=az_cut.max() - 3,
                    color='r', linestyle='--',
                    alpha=0.7, label='-3dB')
    axes[0].set_xlabel('Azimuth (deg)')
    axes[0].set_ylabel('Gain (dBi)')
    axes[0].set_title(f'Azimuth Cut (el=0) - {base}')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].set_xlim(min(az), max(az))

    # El cut
    axes[1].plot(el, el_cut, 'r-', linewidth=1.5)
    axes[1].axhline(y=el_cut.max() - 3,
                    color='b', linestyle='--',
                    alpha=0.7, label='-3dB')
    axes[1].set_xlabel('Elevation (deg)')
    axes[1].set_ylabel('Gain (dBi)')
    axes[1].set_title(f'Elevation Cut (az=0) - {base}')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].set_xlim(min(el), max(el))

    plt.tight_layout()
    output_path = _build_output_path(filepath, 'cuts', 'cuts', output_path)
    plt.savefig(output_path, dpi=150,
                bbox_inches='tight')
    plt.close()
    logger.info("Saved: %s", output_path)
    return output_path


def graph_polar(filepath: str, output_path: str | None = None) -> None:
    """Generate polar plot of az/el cuts."""
    if not check_plot_deps():
        return
    import numpy as np
    import matplotlib.pyplot as plt

    az, el, data = read_pattern_csv(filepath)
    arr = np.array(data)

    az0 = len(az) // 2
    el0 = len(el) // 2

    az_cut = arr[el0, :]
    el_cut = arr[:, az0]

    fig, axes = plt.subplots(
        1, 2, figsize=(14, 6),
        subplot_kw={'projection': 'polar'}
    )
    base = os.path.splitext(os.path.basename(filepath))[0]

    az_rad = np.radians(az)
    el_rad = np.radians(el)

    # Normalize to 0-1 for polar display
    peak = max(az_cut.max(), el_cut.max())
    floor = peak - 40

    az_norm = np.clip(az_cut, floor, peak)
    az_norm = (az_norm - floor) / (peak - floor)
    el_norm = np.clip(el_cut, floor, peak)
    el_norm = (el_norm - floor) / (peak - floor)

    axes[0].plot(az_rad, az_norm, 'b-', linewidth=1.5)
    axes[0].set_title(f'Az Cut (el=0)\n{base}',
                      pad=20, fontsize=10)
    axes[0].set_theta_zero_location('N')
    axes[0].set_theta_direction(-1)

    axes[1].plot(el_rad, el_norm, 'r-', linewidth=1.5)
    axes[1].set_title(f'El Cut (az=0)\n{base}',
                      pad=20, fontsize=10)
    axes[1].set_theta_zero_location('N')
    axes[1].set_theta_direction(-1)

    plt.tight_layout()
    output_path = _build_output_path(filepath, 'polar', 'polar', output_path)
    plt.savefig(output_path, dpi=150,
                bbox_inches='tight')
    plt.close()
    logger.info("Saved: %s", output_path)
    return output_path


def graph_3d_surface(filepath: str, output_path: str | None = None) -> None:
    """Generate a 3D surface plot of the pattern."""
    if not check_plot_deps():
        return
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    az, el, data = read_pattern_csv(filepath)
    arr = np.array(data)

    # Subsample for performance
    step = max(1, len(az) // 90)
    az_sub = az[::step]
    el_sub = el[::step]
    arr_sub = arr[::step, ::step]

    AZ, EL = np.meshgrid(az_sub, el_sub)
    vmin = max(arr_sub.min(), arr_sub.max() - 40)
    arr_clipped = np.clip(arr_sub, vmin, arr_sub.max())

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(
        AZ, EL, arr_clipped,
        cmap='jet', alpha=0.8,
        rstride=1, cstride=1
    )
    fig.colorbar(surf, shrink=0.5,
                 label='Gain (dBi)')

    ax.set_xlabel('Azimuth (deg)')
    ax.set_ylabel('Elevation (deg)')
    ax.set_zlabel('Gain (dBi)')
    base = os.path.splitext(os.path.basename(filepath))[0]
    ax.set_title(f'3D Pattern: {base}')

    plt.tight_layout()
    output_path = _build_output_path(filepath, '3d', '3d_surface', output_path)
    plt.savefig(output_path, dpi=150,
                bbox_inches='tight')
    plt.close()
    logger.info("Saved: %s", output_path)
    return output_path
