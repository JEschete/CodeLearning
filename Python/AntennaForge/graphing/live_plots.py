"""
In-memory plot functions for the live preview panel.

Each function takes a matplotlib Figure and raw data arrays,
clears the figure, renders the plot, and returns.  No disk I/O,
no pyplot — uses the OO API only to avoid backend conflicts with
the Agg backend set by graphing/__init__.py.
"""

import numpy as np
from matplotlib.figure import Figure


# ── Dark theme colours ────────────────────────────────────────
_BG       = "#0F172A"
_TEXT     = "#F1F5F9"
_GRID     = "#334155"
_AZ_LINE  = "#60A5FA"   # blue-400
_EL_LINE  = "#F87171"   # red-400
_REF_LINE = "#FBBF24"   # amber-400


def _apply_dark_style(ax, xlabel="", ylabel="", title=""):
    """Apply dark theme styling to an axes."""
    ax.set_facecolor(_BG)
    ax.tick_params(colors=_TEXT, labelsize=8)
    ax.xaxis.label.set_color(_TEXT)
    ax.yaxis.label.set_color(_TEXT)
    ax.title.set_color(_TEXT)
    for spine in ax.spines.values():
        spine.set_color(_GRID)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    if title:
        ax.set_title(title, fontsize=10, pad=6)


def live_heatmap(
    fig: Figure,
    az: list[float],
    el: list[float],
    data_2d: list[list[float]],
    title: str = "",
    vmin_override: float | None = None,
    vmax_override: float | None = None,
) -> None:
    """Render a heatmap onto *fig* from raw data arrays.

    Args:
        vmin_override: If provided, use as colour-scale minimum (dBi).
        vmax_override: If provided, use as colour-scale maximum (dBi).
    """
    fig.clf()
    fig.set_facecolor(_BG)

    ax = fig.add_subplot(111)
    arr = np.array(data_2d)

    vmax = vmax_override if vmax_override is not None else arr.max()
    vmin = vmin_override if vmin_override is not None else max(arr.min(), vmax - 60)

    AZ, EL = np.meshgrid(az, el)
    im = ax.pcolormesh(
        AZ, EL, arr,
        shading="gouraud", cmap="jet",
        vmin=vmin, vmax=vmax,
    )
    ax.set_xlim(az[0], az[-1])
    ax.set_ylim(el[-1], el[0])

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Gain (dBi)", fontsize=9, color=_TEXT)
    cbar.ax.tick_params(colors=_TEXT, labelsize=8)

    ax.axhline(y=0, color="white", linewidth=0.5, alpha=0.4)
    ax.axvline(x=0, color="white", linewidth=0.5, alpha=0.4)

    # Mark peak
    peak_val = arr.max()
    peak_idx = np.unravel_index(arr.argmax(), arr.shape)
    peak_az = az[peak_idx[1]]
    peak_el = el[peak_idx[0]]
    ax.plot(peak_az, peak_el, "w+", markersize=12, markeredgewidth=2)
    ax.annotate(
        f"{peak_val:.1f} dBi",
        xy=(peak_az, peak_el),
        xytext=(peak_az + 15, peak_el + 15),
        color="white", fontsize=8,
        arrowprops=dict(arrowstyle="->", color="white"),
    )

    _apply_dark_style(ax, "Azimuth (deg)", "Elevation (deg)", title)
    fig.tight_layout(pad=0.5)


def live_cuts(
    fig: Figure,
    az: list[float],
    el: list[float],
    data_2d: list[list[float]],
    title: str = "",
) -> None:
    """Render azimuth + elevation cuts onto *fig*."""
    fig.clf()
    fig.set_facecolor(_BG)

    arr = np.array(data_2d)
    az0 = len(az) // 2
    el0 = len(el) // 2

    az_cut = arr[el0, :]
    el_cut = arr[:, az0]

    # Azimuth cut
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(az, az_cut, color=_AZ_LINE, linewidth=1.5)
    ax1.axhline(
        y=az_cut.max() - 3, color=_REF_LINE,
        linestyle="--", alpha=0.7, label="-3 dB",
    )
    ax1.set_xlim(min(az), max(az))
    ax1.grid(True, alpha=0.2, color=_GRID)
    ax1.legend(fontsize=7, facecolor=_BG, edgecolor=_GRID, labelcolor=_TEXT)
    _apply_dark_style(ax1, "Azimuth (deg)", "Gain (dBi)",
                      f"Az Cut (el=0)  {title}")

    # Elevation cut
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(el, el_cut, color=_EL_LINE, linewidth=1.5)
    ax2.axhline(
        y=el_cut.max() - 3, color=_REF_LINE,
        linestyle="--", alpha=0.7, label="-3 dB",
    )
    ax2.set_xlim(min(el), max(el))
    ax2.grid(True, alpha=0.2, color=_GRID)
    ax2.legend(fontsize=7, facecolor=_BG, edgecolor=_GRID, labelcolor=_TEXT)
    _apply_dark_style(ax2, "Elevation (deg)", "Gain (dBi)",
                      f"El Cut (az=0)  {title}")

    fig.tight_layout(pad=0.5)


def live_polar(
    fig: Figure,
    az: list[float],
    el: list[float],
    data_2d: list[list[float]],
    title: str = "",
) -> None:
    """Render polar az/el cuts onto *fig*."""
    fig.clf()
    fig.set_facecolor(_BG)

    arr = np.array(data_2d)
    az0 = len(az) // 2
    el0 = len(el) // 2

    az_cut = arr[el0, :]
    el_cut = arr[:, az0]

    az_rad = np.radians(az)
    el_rad = np.radians(el)

    peak = max(az_cut.max(), el_cut.max())
    floor = peak - 40

    az_norm = np.clip(az_cut, floor, peak)
    az_norm = (az_norm - floor) / (peak - floor)
    el_norm = np.clip(el_cut, floor, peak)
    el_norm = (el_norm - floor) / (peak - floor)

    # Azimuth polar
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax1.plot(az_rad, az_norm, color=_AZ_LINE, linewidth=1.5)
    ax1.set_title(f"Az Cut (el=0)\n{title}", pad=12, fontsize=9, color=_TEXT)
    ax1.set_theta_zero_location("N")
    ax1.set_theta_direction(-1)
    ax1.set_facecolor(_BG)
    ax1.tick_params(colors=_TEXT, labelsize=7)
    ax1.grid(True, alpha=0.2, color=_GRID)

    # Elevation polar
    ax2 = fig.add_subplot(1, 2, 2, projection="polar")
    ax2.plot(el_rad, el_norm, color=_EL_LINE, linewidth=1.5)
    ax2.set_title(f"El Cut (az=0)\n{title}", pad=12, fontsize=9, color=_TEXT)
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)
    ax2.set_facecolor(_BG)
    ax2.tick_params(colors=_TEXT, labelsize=7)
    ax2.grid(True, alpha=0.2, color=_GRID)

    fig.tight_layout(pad=0.5)
