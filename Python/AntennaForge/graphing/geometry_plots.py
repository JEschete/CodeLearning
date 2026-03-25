"""
LPDA geometry diagram renderer.

Renders a side-view schematic of the LPDA element layout onto a
matplotlib Figure using the OO API (no pyplot).  Follows the same
dark-theme conventions as graphing/live_plots.py.
"""

import numpy as np
from matplotlib.figure import Figure

# ── Dark theme colours (shared with live_plots.py) ────────────
_BG       = "#0F172A"
_TEXT     = "#F1F5F9"
_GRID     = "#334155"
_BOOM_CLR = "#94A3B8"       # slate-400
_ELEM_CM  = "coolwarm_r"    # longest = warm, shortest = cool


def live_lpda_geometry(
    fig: Figure,
    geometry: dict,
    title: str = "",
) -> None:
    """Render a side-view LPDA element diagram onto *fig*.

    Args:
        fig: Matplotlib Figure to draw on (cleared first).
        geometry: Output from ``core.lpda_geometry.compute_lpda_geometry()``.
        title: Optional title string.
    """
    fig.clf()
    fig.set_facecolor(_BG)

    ax = fig.add_subplot(111)
    ax.set_facecolor(_BG)

    n = geometry["n_elements"]
    lengths = geometry["lengths_m"]
    positions = geometry["positions_m"]
    boom = geometry["boom_length_m"]

    if n == 0 or boom <= 0:
        ax.text(0.5, 0.5, "No valid geometry", ha="center", va="center",
                color=_TEXT, fontsize=14, transform=ax.transAxes)
        _style_axes(ax, title)
        fig.tight_layout(pad=0.5)
        return

    # ── Colour map for elements (longest=warm → shortest=cool) ─
    cmap = fig.get_cmap(_ELEM_CM) if hasattr(fig, 'get_cmap') else None
    try:
        from matplotlib import colormaps
        cmap = colormaps[_ELEM_CM]
    except Exception:
        import matplotlib.cm as cm
        cmap = cm.get_cmap(_ELEM_CM)

    # ── Draw boom (horizontal line) ───────────────────────────
    ax.plot([0, boom], [0, 0], color=_BOOM_CLR, linewidth=3,
            solid_capstyle="round", zorder=1)

    # ── Draw elements (vertical lines, symmetric about boom) ──
    max_len = max(lengths)
    label_every = max(1, n // 15)  # adaptive labelling for crowded arrays

    for i in range(n):
        x = positions[i]
        half = lengths[i] / 2.0
        t = i / max(n - 1, 1)  # 0 = longest, 1 = shortest
        color = cmap(t)
        lw = 2.5 - 1.0 * t  # thicker for longer elements

        ax.plot([x, x], [-half, half], color=color,
                linewidth=lw, solid_capstyle="round", zorder=2)

        # Small circle at boom junction
        ax.plot(x, 0, "o", color=color, markersize=3, zorder=3)

        # Label (element number + length)
        if i % label_every == 0 or i == n - 1:
            ax.text(x, half + max_len * 0.04,
                    f"{i+1}", ha="center", va="bottom",
                    fontsize=7, color=_TEXT, fontweight="bold")
            ax.text(x, -(half + max_len * 0.04),
                    f"{lengths[i]:.3f}m", ha="center", va="top",
                    fontsize=6, color=cmap(t), alpha=0.85)

    # ── Boom length dimension ─────────────────────────────────
    y_dim = -(max_len * 0.6 + max_len * 0.08)
    ax.annotate(
        "", xy=(boom, y_dim), xytext=(0, y_dim),
        arrowprops=dict(arrowstyle="<->", color=_TEXT, lw=1.2),
    )
    ax.text(boom / 2, y_dim - max_len * 0.05,
            f"Boom: {boom:.3f} m",
            ha="center", va="top", fontsize=9, color=_TEXT)

    # ── Feed point indicator ──────────────────────────────────
    # Feed is at the shortest element (front)
    ax.plot(positions[-1], 0, "s", color="#FBBF24", markersize=8,
            zorder=4, label="Feed point")
    ax.text(positions[-1], max_len * 0.52 + max_len * 0.06,
            "Feed", ha="center", va="bottom",
            fontsize=8, color="#FBBF24", fontweight="bold")

    # ── Direction arrow ───────────────────────────────────────
    arr_y = max_len * 0.55
    ax.annotate(
        "Direction of\nmax radiation",
        xy=(-boom * 0.05, arr_y),
        xytext=(boom * 0.25, arr_y),
        fontsize=8, color="#60A5FA",
        ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color="#60A5FA", lw=1.5),
    )

    # ── Axis styling ──────────────────────────────────────────
    margin_x = boom * 0.12
    margin_y = max_len * 0.25
    ax.set_xlim(-margin_x, boom + margin_x)
    ax.set_ylim(-(max_len * 0.6 + margin_y), max_len * 0.6 + margin_y)

    # Let matplotlib auto-scale axes to fill the full figure canvas.
    # The figure/canvas pixel size stays fixed; the plot content
    # zooms in or out to fit the available space.
    ax.set_aspect("auto")

    _style_axes(ax, title, xlabel="Position along boom (m)",
                ylabel="Element extent (m)")
    ax.grid(True, alpha=0.15, color=_GRID)
    fig.tight_layout(pad=0.5)


def _style_axes(ax, title="", xlabel="", ylabel=""):
    """Apply dark theme styling (mirrors live_plots._apply_dark_style)."""
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
