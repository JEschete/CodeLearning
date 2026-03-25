"""
Multi-file graph functions.

Each takes a list of file paths and produces one comparison PNG.
Plots are organized into subfolders by plot type.
"""

import logging
import os

logger = logging.getLogger(__name__)

from graphing import check_plot_deps
from core.io import read_pattern_csv, extract_freq_from_filename
from analysis.analyzer import measure_beamwidth


def _multi_output_path(
    file_list: list[str],
    subfolder: str,
    stem: str,
    output_path: str | None = None,
) -> str:
    """Build output path for multi-file plots in a type-specific subfolder.

    Args:
        file_list: Source CSV paths (directory of first is used).
        subfolder: Target subfolder name.
        stem: Output filename stem (without extension).
        output_path: Explicit override, if any.

    Returns:
        Resolved output PNG path.
    """
    if output_path is not None:
        return output_path
    # Use the directory of the first file as base
    if file_list:
        base_dir = os.path.dirname(file_list[0]) or "."
    else:
        base_dir = "."
    sub = os.path.join(base_dir, subfolder)
    os.makedirs(sub, exist_ok=True)
    return os.path.join(sub, f"{stem}.png")


def graph_gain_vs_freq(file_list: list[str], output_path: str | None = None) -> None:
    """Plot peak gain vs frequency across files."""
    if not check_plot_deps():
        return
    import numpy as np
    import matplotlib.pyplot as plt

    freqs = []
    peaks = []
    bores = []

    for fp in sorted(file_list):
        freq = extract_freq_from_filename(fp)
        if freq is None:
            logger.warning("Can't extract freq from %s, skipping", fp)
            continue
        az, el, data = read_pattern_csv(fp)
        arr = np.array(data)
        peak = arr.max()
        az0 = len(az) // 2
        el0 = len(el) // 2
        bore = data[el0][az0]

        freqs.append(freq)
        peaks.append(peak)
        bores.append(bore)

    if not freqs:
        logger.error("No valid files found")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(freqs, peaks, 'b-o',
            label='Peak Gain', linewidth=2,
            markersize=6)
    ax.plot(freqs, bores, 'r--s',
            label='Boresight Gain', linewidth=2,
            markersize=6)

    ax.set_xlabel('Frequency (MHz)', fontsize=12)
    ax.set_ylabel('Gain (dBi)', fontsize=12)
    ax.set_title('Gain vs Frequency', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)

    plt.tight_layout()
    output_path = _multi_output_path(file_list, 'gain_vs_freq', 'gain_vs_freq', output_path)
    plt.savefig(output_path, dpi=150,
                bbox_inches='tight')
    plt.close()
    logger.info("Saved: %s", output_path)
    return output_path


def graph_bw_vs_freq(file_list: list[str], output_path: str | None = None) -> None:
    """Plot beamwidth vs frequency."""
    if not check_plot_deps():
        return
    import numpy as np
    import matplotlib.pyplot as plt

    freqs = []
    az_bws = []
    el_bws = []

    for fp in sorted(file_list):
        freq = extract_freq_from_filename(fp)
        if freq is None:
            continue
        az, el, data = read_pattern_csv(fp)
        el0 = len(el) // 2
        az0 = len(az) // 2

        bore = data[el0][az0]
        az_cut = data[el0]
        el_cut = [data[i][az0] for i in range(len(el))]

        az_bw = measure_beamwidth(az, az_cut, bore)
        el_bw = measure_beamwidth(el, el_cut, bore)

        freqs.append(freq)
        az_bws.append(az_bw)
        el_bws.append(el_bw)

    if not freqs:
        logger.error("No valid files found")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(freqs, az_bws, 'b-o',
            label='Az 3dB Beamwidth', linewidth=2,
            markersize=6)
    ax.plot(freqs, el_bws, 'r--s',
            label='El 3dB Beamwidth', linewidth=2,
            markersize=6)

    ax.set_xlabel('Frequency (MHz)', fontsize=12)
    ax.set_ylabel('Beamwidth (deg)', fontsize=12)
    ax.set_title('Beamwidth vs Frequency', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)

    plt.tight_layout()
    output_path = _multi_output_path(file_list, 'bw_vs_freq', 'bw_vs_freq', output_path)
    plt.savefig(output_path, dpi=150,
                bbox_inches='tight')
    plt.close()
    logger.info("Saved: %s", output_path)
    return output_path


def graph_overlay_cuts(file_list: list[str], output_path: str | None = None) -> None:
    """Overlay az cuts from multiple files on one plot."""
    if not check_plot_deps():
        return
    import numpy as np
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for fp in sorted(file_list):
        az, el, data = read_pattern_csv(fp)
        arr = np.array(data)
        el0 = len(el) // 2
        az0 = len(az) // 2

        az_cut = arr[el0, :]
        el_cut = arr[:, az0]

        freq = extract_freq_from_filename(fp)
        if freq is not None:
            label = f"{freq:.1f} MHz"
        else:
            label = os.path.basename(fp)[:20]

        axes[0].plot(az, az_cut,
                     linewidth=1.2, label=label)
        axes[1].plot(el, el_cut,
                     linewidth=1.2, label=label)

    axes[0].set_xlabel('Azimuth (deg)')
    axes[0].set_ylabel('Gain (dBi)')
    axes[0].set_title('Azimuth Cuts Overlay (el=0)')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=8)

    axes[1].set_xlabel('Elevation (deg)')
    axes[1].set_ylabel('Gain (dBi)')
    axes[1].set_title('Elevation Cuts Overlay (az=0)')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    output_path = _multi_output_path(file_list, 'overlay_cuts', 'overlay_cuts', output_path)
    plt.savefig(output_path, dpi=150,
                bbox_inches='tight')
    plt.close()
    logger.info("Saved: %s", output_path)
    return output_path
