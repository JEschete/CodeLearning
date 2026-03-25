"""
Multi-pattern report generation with configurable sections.
Given a directory of pattern CSVs from one generation run,
produces a single PDF report.  Every section is controlled by
 a ReportConfig dict so the user can toggle what they want.
Uses matplotlib's PdfPages backend -- no additional dependencies
beyond what the graphing module already requires.
"""
from __future__ import annotations
import glob
import logging
import math
import os
import re
from collections import OrderedDict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from types import ModuleType
    from matplotlib.backends.backend_pdf import PdfPages
logger = logging.getLogger(__name__)
def _sanitise_filename(name: str) -> str:
    """Turn a report title into a safe filename stem."""
    s = re.sub(r'[<>:"/\\|?*]', '_', name)
    s = s.strip('. ').replace(' ', '_')
    return s[:120] or 'pattern_report'
from core.io import (
    read_pattern_file, extract_freq_from_filename,
)
from analysis.analyzer import (
    measure_beamwidth, find_first_sidelobe,
    check_symmetry_az, check_symmetry_el,
)
# ===================================================================
#  REPORT CONFIGURATION
# ===================================================================
# Ordered so the menu prints nicely.
# key → (default_enabled, label, group)
REPORT_SECTIONS = OrderedDict([
    # ── Global pages ──────────────────────────────────────────────
    ("cover_page",           (True,  "Cover page",
                              "global")),
    ("table_of_contents",    (True,  "Table of contents",
                              "global")),
    ("summary_table",        (True,  "Summary table"
                              " (freq / gain / BW / F-B / SLL)",
                              "global")),
    ("gain_vs_freq",         (True,  "Gain vs Frequency chart",
                              "global")),
    ("bw_vs_freq",           (True,  "3 dB Beamwidth vs Frequency chart",
                              "global")),
    ("overlay_cuts",         (True,  "Overlay cuts"
                              " (all freqs on one plot)",
                              "global")),
    # ── Per-frequency pages ───────────────────────────────────────
    ("per_freq_heatmap",     (True,  "Per-freq heatmap"
                              " + az/el cuts combo",
                              "per_freq")),
    ("per_freq_polar",       (True,  "Per-freq polar plot",
                              "per_freq")),
    ("per_freq_3d",          (False, "Per-freq 3-D surface"
                              " (slower)",
                              "per_freq")),
    ("per_freq_stats",       (True,  "Per-freq statistics box",
                              "per_freq")),
    ("per_freq_detailed",    (True,  "Per-freq detailed analysis"
                              " (hemispheric, symmetry, coverage)",
                              "per_freq")),
    ("per_freq_sidelobe",    (True,  "Per-freq sidelobe detail",
                              "per_freq")),
    # ── Options ───────────────────────────────────────────────────
    ("generation_config",    (True,  "Generation configuration page",
                              "global")),
    ("include_xpol",         (False, "Include cross-pol patterns"
                              " (if _xpol.csv exist)",
                              "option")),
])
# Extra numeric options
REPORT_OPTIONS = OrderedDict([
    ("dynamic_range_db",   (60,  "Heatmap dynamic range (dB)")),
    ("polar_range_db",     (40,  "Polar plot range (dB)")),
    ("extra_cut_angles",   ([],  "Extra cut angles (deg list)")),
])
# Classification marking levels (common standard markings)
CLASSIFICATION_LEVELS = [
    "UNCLASSIFIED",
    "CUI",
    "CONFIDENTIAL",
    "SECRET",
    "TOP SECRET",
    "TOP SECRET//SCI",
]
# Colour mapping for classification banners
_CLASSIFICATION_COLORS = {
    "UNCLASSIFIED":    ("#007A33", "white"),   # green / white
    "CUI":             ("#502B85", "white"),   # purple / white
    "CONFIDENTIAL":    ("#0033A0", "white"),   # blue / white
    "SECRET":          ("#C8102E", "white"),   # red / white
    "TOP SECRET":      ("#FF8C00", "black"),   # orange / black
    "TOP SECRET//SCI": ("#FFD700", "black"),   # gold / black
}
def default_report_config() -> dict:
    """Return a fresh default config dict."""
    cfg = {}
    for key, (default, _label, _group) in REPORT_SECTIONS.items():
        cfg[key] = default
    for key, (default, _label) in REPORT_OPTIONS.items():
        import copy
        cfg[key] = copy.deepcopy(default)
    # Cover page fields
    cfg["cover_title"]        = ""     # overrides auto title
    cfg["cover_subtitle"]     = "Antenna Pattern Report"
    cfg["cover_author"]       = ""
    cfg["cover_organisation"] = ""
    cfg["cover_project"]      = ""
    cfg["cover_document_id"]  = ""
    cfg["cover_revision"]     = ""
    cfg["cover_date"]         = ""     # blank = auto
    # Classification markings
    cfg["classification"]     = "UNCLASSIFIED"   # banner text
    cfg["classification_caveats"] = ""            # e.g. "//NOFORN"
    cfg["figure_classification"]  = ""            # blank = same as classification
    return cfg
# Convenience presets
def _preset_full() -> dict:
    """Preset with every report section enabled."""
    cfg = default_report_config()
    for key in REPORT_SECTIONS:
        cfg[key] = True
    return cfg
def _preset_minimal() -> dict:
    """Preset with summary + basic per-frequency sections only."""
    cfg = default_report_config()
    for key in REPORT_SECTIONS:
        if REPORT_SECTIONS[key][2] == "per_freq":
            cfg[key] = False
    cfg["per_freq_heatmap"] = True
    cfg["per_freq_stats"] = True
    return cfg
def _preset_quick() -> dict:
    """Only global summary pages, no per-frequency detail."""
    cfg = default_report_config()
    for key in REPORT_SECTIONS:
        if REPORT_SECTIONS[key][2] == "per_freq":
            cfg[key] = False
    return cfg
PRESETS = OrderedDict([
    ("default",  ("Default -- recommended sections",
                  default_report_config)),
    ("full",     ("Full -- every section enabled",
                  _preset_full)),
    ("minimal",  ("Minimal -- summary + basic per-freq",
                  _preset_minimal)),
    ("quick",    ("Quick -- global pages only, no per-freq",
                  _preset_quick)),
])
# ===================================================================
#  HELPERS
# ===================================================================
def _find_xpol(copol_path: str) -> str | None:
    """Return matching _xpol file path if it exists, else None."""
    base, ext = os.path.splitext(copol_path)
    xpol = base.replace("_copol", "_xpol") + ext
    if os.path.isfile(xpol):
        return xpol
    return None
def _compute_summary(fp: str, az: list[float], el: list[float],
                     data: list[list[float]], arr: "np.ndarray",
                     np: "ModuleType") -> dict:
    """Compute one-frequency summary dict."""
    freq = extract_freq_from_filename(fp)
    n_az = len(az)
    n_el = len(el)
    az0 = n_az // 2
    el0 = n_el // 2
    for idx, a in enumerate(az):
        if abs(a) < 0.01:
            az0 = idx
            break
    for idx, e in enumerate(el):
        if abs(e) < 0.01:
            el0 = idx
            break
    peak_gain = float(arr.max())
    bore_gain = data[el0][az0]
    az_cut = data[el0]
    el_cut = [data[i][az0] for i in range(n_el)]
    az_bw = measure_beamwidth(az, az_cut, bore_gain)
    # Omni patterns never drop 3 dB in azimuth → measure_beamwidth
    # returns 0.  Report the true 360° beamwidth instead.
    if az_bw == 0 and (max(az_cut) - min(az_cut)) < 3.0:
        az_bw = 360
    el_bw = measure_beamwidth(el, el_cut, bore_gain)
    # Front-to-back
    ftb = None
    if 180.0 in az:
        back_idx = az.index(180.0)
        back_gain = data[el0][back_idx]
        ftb = bore_gain - back_gain
    sl = find_first_sidelobe(az, az_cut, bore_gain, az_bw)
    # Peak location
    peak_flat = int(arr.argmax())
    peak_row, peak_col = divmod(peak_flat, n_az)
    peak_az = az[peak_col]
    peak_el = el[peak_row]
    # Min / mean
    min_gain = float(arr.min())
    avg_gain = float(arr.mean())
    # Hemispheric
    front_mask = np.array([(-90 <= a <= 90) for a in az])
    front_vals = arr[:, front_mask]
    back_vals  = arr[:, ~front_mask]
    front_avg = float(front_vals.mean()) if front_vals.size else None
    back_avg  = float(back_vals.mean()) if back_vals.size else None
    # Symmetry
    asym_az = check_symmetry_az(az, data, el0)
    asym_el = check_symmetry_el(el, data, az0)
    # Coverage
    total = arr.size
    above_0   = int((arr >= 0).sum())
    above_m3  = int((arr >= peak_gain - 3).sum())
    above_m10 = int((arr >= peak_gain - 10).sum())
    # El sidelobe
    el_sl = find_first_sidelobe(el, el_cut, bore_gain, el_bw)
    return {
        'file': fp,
        'freq': freq,
        'peak_gain': peak_gain,
        'bore_gain': bore_gain,
        'az_bw': az_bw,
        'el_bw': el_bw,
        'ftb': ftb,
        'first_sll': sl,
        'el_first_sll': el_sl,
        'peak_az': peak_az,
        'peak_el': peak_el,
        'min_gain': min_gain,
        'avg_gain': avg_gain,
        'dynamic_range': peak_gain - min_gain,
        'front_avg': front_avg,
        'back_avg': back_avg,
        'asym_az': asym_az,
        'asym_el': asym_el,
        'total_pts': total,
        'above_0': above_0,
        'above_m3': above_m3,
        'above_m10': above_m10,
        'az': az,
        'el': el,
        'data': data,
        'arr': arr,
        'az0': az0,
        'el0': el0,
    }
# ===================================================================
#  CLASSIFICATION MARKING HELPERS
# ===================================================================
def _get_classification_text(report_cfg: dict) -> str:
    """Build the full classification banner string.
    Combines the base classification with any caveats, e.g.
    ``SECRET//NOFORN``.
    """
    base = report_cfg.get("classification", "UNCLASSIFIED") or "UNCLASSIFIED"
    caveats = report_cfg.get("classification_caveats", "").strip()
    if caveats:
        return f"{base}//{caveats}"
    return base
def _get_figure_classification(report_cfg: dict) -> str:
    """Return figure-level classification string.
    Falls back to the overall classification when
    ``figure_classification`` is empty.
    """
    fig_cls = report_cfg.get("figure_classification", "").strip()
    if fig_cls:
        return fig_cls
    return _get_classification_text(report_cfg)
def _get_cls_colors(report_cfg: dict) -> tuple[str, str]:
    """Return ``(bg_color, text_color)`` for the classification level."""
    base = report_cfg.get("classification", "UNCLASSIFIED") or "UNCLASSIFIED"
    return _CLASSIFICATION_COLORS.get(base, ("#007A33", "white"))
def _draw_pdf_classification_banners(
    fig,
    report_cfg: dict,
    *,
    page_number: str = "",
) -> None:
    """Draw top and bottom classification banners on a matplotlib figure.
    Adds coloured bars at the very top and bottom of the page with
    the classification marking centred in white (or black) text.
    Optionally includes a page number on the bottom-right.
    Args:
        fig:         Matplotlib figure.
        report_cfg:  Report configuration dict.
        page_number: Optional page number string for the footer.
    """
    cls_text = _get_classification_text(report_cfg)
    bg, fg = _get_cls_colors(report_cfg)
    # Top banner
    fig.text(0.5, 0.995, cls_text,
             ha='center', va='top', fontsize=9, fontweight='bold',
             color=fg,
             bbox=dict(boxstyle='square,pad=0.3',
                       facecolor=bg, edgecolor=bg,
                       alpha=1.0),
             transform=fig.transFigure, zorder=100)
    # Bottom banner
    fig.text(0.5, 0.005, cls_text,
             ha='center', va='bottom', fontsize=9, fontweight='bold',
             color=fg,
             bbox=dict(boxstyle='square,pad=0.3',
                       facecolor=bg, edgecolor=bg,
                       alpha=1.0),
             transform=fig.transFigure, zorder=100)
def _add_figure_classification(
    fig,
    report_cfg: dict,
) -> None:
    """Add a small classification label below the figure content area.
    This marks each figure/plot with its classification level.
    Args:
        fig:         Matplotlib figure.
        report_cfg:  Report configuration dict.
    """
    fig_cls = _get_figure_classification(report_cfg)
    bg, fg = _get_cls_colors(report_cfg)
    fig.text(0.5, 0.015, fig_cls,
             ha='center', va='bottom', fontsize=7,
             fontstyle='italic', color=fg,
             bbox=dict(boxstyle='round,pad=0.2',
                       facecolor=bg, edgecolor=bg,
                       alpha=0.85),
             transform=fig.transFigure, zorder=100)


def _add_axes_classification(
    ax,
    report_cfg: dict,
) -> None:
    """Stamp classification markings on an individual axes/subplot.

    Places the classification text at the **top-left** and
    **bottom-right** corners of the axes so that any single plot
    retains its marking when extracted from a composite figure.

    Works with Cartesian, polar, and 3-D projections.

    Args:
        ax:          Matplotlib Axes (any projection).
        report_cfg:  Report configuration dict.
    """
    fig_cls = _get_figure_classification(report_cfg)
    if not fig_cls:
        return
    bg, fg = _get_cls_colors(report_cfg)

    common = dict(
        fontsize=5.5, fontweight='bold',
        color=fg,
        bbox=dict(boxstyle='round,pad=0.15',
                  facecolor=bg, edgecolor='none',
                  alpha=0.75),
        zorder=200,
        clip_on=False,
    )

    # For 3-D axes use text2D; for all others use text on transAxes
    is_3d = hasattr(ax, 'text2D')
    _text = ax.text2D if is_3d else ax.text

    # Top-left
    _text(0.01, 0.99, fig_cls,
          transform=ax.transAxes,
          ha='left', va='top',
          **common)
    # Bottom-right
    _text(0.99, 0.01, fig_cls,
          transform=ax.transAxes,
          ha='right', va='bottom',
          **common)


# ===================================================================
#  MAIN REPORT GENERATOR
# ===================================================================
def generate_report(input_dir: str, output_path: str | None = None,
                    title: str | None = None,
                    report_cfg: dict | None = None) -> str | None:
    """Generate a PDF report from a directory of pattern CSVs.

    Args:
        input_dir:   Directory containing pattern CSV files.
        output_path: Destination PDF path.  ``None`` → auto-named
                     in *input_dir*.
        title:       Report title for cover page.  ``None`` → derived
                     from the directory name.
        report_cfg:  Report configuration dict (see
                     :func:`default_report_config`).  ``None`` → defaults.

    Returns:
        The output PDF path on success, or ``None`` on failure.
    """
    # ── Lazy imports ──────────────────────────────────────────────
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    # ── Defaults ──────────────────────────────────────────────────
    if report_cfg is None:
        report_cfg = default_report_config()
    if title is None:
        title = report_cfg.get("cover_title", "").strip()
        if not title:
            title = os.path.basename(os.path.normpath(input_dir))
    if output_path is None:
        stem = _sanitise_filename(title)
        output_path = os.path.join(input_dir, f"{stem}.pdf")

    # ── Discover CSV files ────────────────────────────────────────
    csv_files = sorted([
        *glob.glob(os.path.join(input_dir, '*.csv')),
        *glob.glob(os.path.join(input_dir, '*.dat'))
    ])
    # Exclude cross-pol files from the main list
    csv_files = [f for f in csv_files if '_xpol' not in os.path.basename(f)]
    if not csv_files:
        logger.warning("No pattern CSVs found in %s", input_dir)
        return None

    # ── Build summaries ───────────────────────────────────────────
    summaries: list[dict] = []
    for fp in csv_files:
        try:
            az, el, data = read_pattern_file(fp)
            arr = np.array(data)
            s = _compute_summary(fp, az, el, data, arr, np)
            summaries.append(s)
        except Exception:
            logger.exception("Failed to read %s — skipping", fp)
    if not summaries:
        logger.warning("All CSVs failed to load; aborting report.")
        return None

    # Sort by frequency when available
    summaries.sort(key=lambda s: s['freq'] if s['freq'] is not None else 0)

    # ── Cross-pol summaries (optional) ────────────────────────────
    xpol_summaries: list[dict] = []
    if report_cfg.get("include_xpol", False):
        for fp in csv_files:
            xp = _find_xpol(fp)
            if xp:
                try:
                    az, el, data = read_pattern_file(xp)
                    arr = np.array(data)
                    xs = _compute_summary(xp, az, el, data, arr, np)
                    xpol_summaries.append(xs)
                except Exception:
                    logger.exception("Failed to read xpol %s", xp)

    # ── Detect omni antenna (no 3 dB concept in azimuth) ─────────
    _gen_cfg_path = os.path.join(input_dir, "generation_config.json")
    if os.path.isfile(_gen_cfg_path):
        try:
            import json as _json
            with open(_gen_cfg_path, 'r', encoding='utf-8') as _f:
                _gen_cfg = _json.load(_f)
            report_cfg["_antenna_type"] = _gen_cfg.get("antenna_type", "")
        except Exception:
            pass
    is_omni = str(report_cfg.get("_antenna_type", "")).lower() == "omni"

    # ── Report options ────────────────────────────────────────────
    dyn_range = report_cfg.get("dynamic_range_db", 60)
    polar_range = report_cfg.get("polar_range_db", 40)
    extra_cuts = report_cfg.get("extra_cut_angles", [])

    # ── Pre-compute page count & TOC entries ──────────────────────
    toc_entries: list[tuple[int, str]] = []
    page = 1  # cover is page 1

    if report_cfg.get("cover_page", True):
        toc_entries.append((page, "Cover Page"))
        page += 1
    if report_cfg.get("table_of_contents", True):
        toc_entries.append((page, "Table of Contents"))
        page += 1
    if report_cfg.get("summary_table", True):
        n_sum_pages = max(1, math.ceil(len(summaries) / 30))
        toc_entries.append((page, "Pattern Summary"))
        page += n_sum_pages
    if report_cfg.get("gain_vs_freq", True):
        toc_entries.append((page, "Gain vs Frequency"))
        page += 1
    if report_cfg.get("bw_vs_freq", True):
        _az_bw_label = ("Az Beamwidth" if is_omni
                         else "Azimuth 3 dB Beamwidth")
        toc_entries.append((page, f"{_az_bw_label} vs Frequency"))
        page += 1
        toc_entries.append((page, "Elevation 3 dB Beamwidth vs Frequency"))
        page += 1
    if report_cfg.get("overlay_cuts", True):
        toc_entries.append((page, "Cartesian Cut Overlay"))
        page += 1
        toc_entries.append((page, "Polar Azimuth Cut Overlay"))
        page += 1
        toc_entries.append((page, "Polar Elevation Cut Overlay"))
        page += 1
    for s in summaries:
        freq_str = (f"{s['freq']:.2f} MHz"
                    if s['freq'] else
                    os.path.basename(s['file']))
        if report_cfg.get("per_freq_heatmap"):
            toc_entries.append((page, f"Heatmap @ {freq_str}"))
            page += 1
        if report_cfg.get("per_freq_polar"):
            toc_entries.append((page, f"Polar Azimuth @ {freq_str}"))
            page += 1
            toc_entries.append((page, f"Polar Elevation @ {freq_str}"))
            page += 1
        if report_cfg.get("per_freq_3d"):
            toc_entries.append((page, f"3-D Surface @ {freq_str}"))
            page += 1
        if (report_cfg.get("per_freq_stats")
                or report_cfg.get("per_freq_detailed")
                or report_cfg.get("per_freq_sidelobe")):
            toc_entries.append((page, f"Analysis @ {freq_str}"))
            page += 1
    if xpol_summaries:
        toc_entries.append((page, "Cross-Pol Summary"))
        page += 1 + len(xpol_summaries)

    total_pages = page - 1

    # ── Generate PDF ──────────────────────────────────────────────
    logger.info("Generating report: %s  (%d pages)", output_path, total_pages)

    with PdfPages(output_path) as pdf:
        # ==============================================
        #  COVER PAGE
        # ==============================================
        if report_cfg.get("cover_page", True):
            fig = plt.figure(figsize=(11, 8.5))
            fig.patch.set_facecolor('white')
            # Classification banners
            _draw_pdf_classification_banners(fig, report_cfg)

            # Cover page fields
            subtitle = report_cfg.get("cover_subtitle", "") or "Antenna Pattern Report"
            author   = report_cfg.get("cover_author", "").strip()
            org      = report_cfg.get("cover_organisation", "").strip()
            project  = report_cfg.get("cover_project", "").strip()
            doc_id   = report_cfg.get("cover_document_id", "").strip()
            revision = report_cfg.get("cover_revision", "").strip()
            date_str = report_cfg.get("cover_date", "").strip()

            y = 0.72
            fig.text(0.5, y, title,
                     ha='center', va='center',
                     fontsize=28, fontweight='bold')
            y -= 0.08
            fig.text(0.5, y, subtitle,
                     ha='center', va='center',
                     fontsize=18, color='gray')
            y -= 0.06
            fig.text(0.5, y,
                     f"{len(csv_files)} frequency slice"
                     f"{'s' if len(csv_files) > 1 else ''}   "
                     f"|   {total_pages} pages",
                     ha='center', va='center',
                     fontsize=13, color='gray')

            if summaries and summaries[0]['freq'] is not None:
                freqs = [ss['freq'] for ss in summaries
                         if ss['freq'] is not None]
                f_lo, f_hi = min(freqs), max(freqs)
                y -= 0.05
                fig.text(0.5, y,
                         f"{f_lo:.1f} - {f_hi:.1f} MHz",
                         ha='center', va='center',
                         fontsize=14, color='gray')
                pk = max(ss['peak_gain'] for ss in summaries)
                y -= 0.05
                fig.text(0.5, y,
                         f"Peak gain: {pk:.1f} dBi",
                         ha='center', va='center',
                         fontsize=12, color='#555')

            # Author / organisation / project block
            info_lines = []
            if author:
                info_lines.append(f"Author: {author}")
            if org:
                info_lines.append(f"Organisation: {org}")
            if project:
                info_lines.append(f"Project: {project}")
            if doc_id:
                info_lines.append(f"Document ID: {doc_id}")
            if revision:
                info_lines.append(f"Revision: {revision}")
            if info_lines:
                y -= 0.06
                fig.text(0.5, y, '\n'.join(info_lines),
                         ha='center', va='top',
                         fontsize=11, color='#555',
                         linespacing=1.6)

            # Date
            if date_str:
                fig.text(0.5, 0.10, date_str,
                         ha='center', va='center',
                         fontsize=11, color='gray')
            else:
                fig.text(0.5, 0.10,
                         "Generated by Antenna Pattern Tool v1.0",
                         ha='center', va='center',
                         fontsize=9, color='#888')

            pdf.savefig(fig)
            plt.close(fig)

        # ==============================================
        #  TABLE OF CONTENTS
        # ==============================================
        if report_cfg.get("table_of_contents", True):
            _render_toc(plt, pdf, toc_entries, title, report_cfg)

        # ==============================================
        #  SUMMARY TABLE
        # ==============================================
        if report_cfg.get("summary_table", True):
            _render_summary_table(plt, pdf, summaries, report_cfg)

        # ==============================================
        #  GAIN vs FREQUENCY
        # ==============================================
        if report_cfg.get("gain_vs_freq", True):
            _render_gain_vs_freq(plt, pdf, summaries, np, report_cfg)

        # ==============================================
        #  BEAMWIDTH vs FREQUENCY
        # ==============================================
        if report_cfg.get("bw_vs_freq", True):
            _render_bw_vs_freq_az(plt, pdf, summaries, np, report_cfg)
            _render_bw_vs_freq_el(plt, pdf, summaries, np, report_cfg)

        # ==============================================
        #  OVERLAY CUTS
        # ==============================================
        if report_cfg.get("overlay_cuts", True):
            _render_overlay_cuts_cartesian(plt, pdf, summaries, np, report_cfg)
            _render_overlay_cuts_polar(
                plt, pdf, summaries, np, "Azimuth", report_cfg)
            _render_overlay_cuts_polar(
                plt, pdf, summaries, np, "Elevation", report_cfg)

        # ==============================================
        #  PER-FREQUENCY PAGES
        # ==============================================
        for idx, s in enumerate(summaries):
            freq_str = (f"{s['freq']:.2f} MHz"
                        if s['freq'] else
                        os.path.basename(s['file']))
            logger.info("[%d/%d] %s", idx+1, len(summaries), freq_str)

            if report_cfg.get("per_freq_heatmap"):
                _render_per_freq_heatmap(
                    plt, pdf, s, np,
                    dyn_range, extra_cuts, report_cfg
                )
            if report_cfg.get("per_freq_polar"):
                _render_per_freq_polar_az(
                    plt, pdf, s, np, polar_range, report_cfg
                )
                _render_per_freq_polar_el(
                    plt, pdf, s, np, polar_range, report_cfg
                )
            if report_cfg.get("per_freq_3d"):
                _render_per_freq_3d(
                    plt, pdf, s, np, dyn_range, report_cfg
                )
            if (report_cfg.get("per_freq_stats")
                    or report_cfg.get("per_freq_detailed")
                    or report_cfg.get("per_freq_sidelobe")):
                _render_per_freq_analysis(
                    plt, pdf, s, report_cfg
                )

        # ==============================================
        #  CROSS-POL PAGES
        # ==============================================
        if xpol_summaries:
            _render_xpol_pages(plt, pdf, xpol_summaries,
                               np, dyn_range, report_cfg)

        # ==============================================
        #  CONFIGURATION PAGE (always last)
        # ==============================================
        if report_cfg.get("generation_config", True):
            _render_config_page(plt, pdf, input_dir, report_cfg)

    logger.info("Report saved: %s", output_path)
    logger.info("  %d pages total", total_pages)
    return output_path


# ===================================================================
#  SECTION RENDERERS
# ===================================================================
def _render_toc(plt: "ModuleType", pdf: "PdfPages",
                toc_entries: list[tuple[int, str]],
                title: str,
                report_cfg: dict | None = None) -> None:
    # Table-of-contents page(s). Auto-paginates when needed.
    if report_cfg is None:
        report_cfg = {}
    # Layout constants
    n_cols = 2
    y_start = 0.92
    y_step = 0.018          # fixed step ⇒ readable text
    usable_h = 0.88         # vertical space below title
    rows_per_col = int(usable_h / y_step)
    entries_per_page = rows_per_col * n_cols
    n = len(toc_entries)
    total_toc_pages = max(1, math.ceil(n / entries_per_page))
    for page_idx in range(total_toc_pages):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        suffix = (f" ({page_idx + 1}/{total_toc_pages})"
                  if total_toc_pages > 1 else "")
        fig.suptitle(f'Table of Contents{suffix}',
                     fontsize=16, fontweight='bold', y=0.95)
        fig.subplots_adjust(top=0.90, bottom=0.05)
        start = page_idx * entries_per_page
        end = min(start + entries_per_page, n)
        chunk = toc_entries[start:end]
        per_col = (len(chunk) + n_cols - 1) // n_cols
        for i, (pg, label) in enumerate(chunk):
            col = i // per_col if per_col else 0
            row = i % per_col if per_col else i
            x = 0.05 + col * 0.50
            y = y_start - row * y_step
            short = label[:62]
            dots = '.' * max(1, 64 - len(short))
            ax.text(x, y,
                    f"{short} {dots} {pg}",
                    transform=ax.transAxes,
                    fontsize=7, fontfamily='monospace',
                    verticalalignment='top')
        _draw_pdf_classification_banners(fig, report_cfg)
        pdf.savefig(fig)
        plt.close(fig)
def _render_summary_table(plt: "ModuleType", pdf: "PdfPages",
                          summaries: list[dict],
                          report_cfg: dict | None = None) -> None:
    """Summary table page(s) with per-frequency stats.
    Automatically paginates when there are many frequency slices.
    """
    if report_cfg is None:
        report_cfg = {}
    ROWS_PER_PAGE = 30          # comfortable fit at fontsize 8
    _is_omni = str(report_cfg.get("_antenna_type", "")).lower() == "omni"
    _az_hdr = 'Az BW\n(deg)' if _is_omni else 'Az 3 dB BW\n(deg)'
    headers = ['Freq\n(MHz)', 'Peak\n(dBi)',
               'Bore\n(dBi)', _az_hdr,
               'El 3 dB BW\n(deg)', 'F/B\n(dB)',
               '1st SLL\n(dB)', 'Peak At\n(az, el)',
               'Min\n(dBi)', 'Dyn Rng\n(dB)']
    # Pre-build all row data
    all_rows = []
    for s in summaries:
        freq_str = (f"{s['freq']:.1f}"
                    if s['freq'] else "?")
        ftb_str = (f"{s['ftb']:.1f}"
                   if s['ftb'] is not None else "-")
        sll_str = (
            f"-{s['first_sll']['relative']:.1f}"
            if s['first_sll'] else "-"
        )
        all_rows.append([
            freq_str,
            f"{s['peak_gain']:.1f}",
            f"{s['bore_gain']:.1f}",
            str(s['az_bw']),
            str(s['el_bw']),
            ftb_str,
            sll_str,
            f"({s['peak_az']:.0f}, {s['peak_el']:.0f})",
            f"{s['min_gain']:.1f}",
            f"{s['dynamic_range']:.1f}",
        ])
    if not all_rows:
        return
    total_pages = max(1, math.ceil(len(all_rows) / ROWS_PER_PAGE))
    for page_idx in range(total_pages):
        start = page_idx * ROWS_PER_PAGE
        end = min(start + ROWS_PER_PAGE, len(all_rows))
        chunk = all_rows[start:end]
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        suffix = (f" ({page_idx + 1}/{total_pages})"
                  if total_pages > 1 else "")
        fig.suptitle(f'Pattern Summary{suffix}',
                     fontsize=16, fontweight='bold', y=0.95)
        fig.subplots_adjust(top=0.90, bottom=0.05)
        table = ax.table(
            cellText=chunk,
            colLabels=headers,
            cellLoc='center',
            loc='upper center',
            bbox=[0.0, 0.0, 1.0, 0.95],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.0, 1.4)
        for j in range(len(headers)):
            cell = table[0, j]
            cell.set_facecolor('#4472C4')
            cell.set_text_props(
                color='white', fontweight='bold'
            )
        for i in range(len(chunk)):
            for j in range(len(headers)):
                cell = table[i + 1, j]
                if i % 2 == 0:
                    cell.set_facecolor('#D9E2F3')
        _draw_pdf_classification_banners(fig, report_cfg)
        pdf.savefig(fig)
        plt.close(fig)
def _render_gain_vs_freq(plt: "ModuleType", pdf: "PdfPages",
                         summaries: list[dict],
                         np: "ModuleType",
                         report_cfg: dict | None = None) -> None:
    """Gain-vs-frequency trend page."""
    if report_cfg is None:
        report_cfg = {}
    fig, ax = plt.subplots(figsize=(11, 8.5))
    freqs = [s['freq'] for s in summaries
             if s['freq'] is not None]
    peaks = [s['peak_gain'] for s in summaries
             if s['freq'] is not None]
    bores = [s['bore_gain'] for s in summaries
             if s['freq'] is not None]
    if not freqs:
        plt.close(fig)
        return
    ax.plot(freqs, peaks, 'b-o',
            label='Peak Gain', linewidth=2,
            markersize=6)
    ax.plot(freqs, bores, 'r--s',
            label='Boresight Gain', linewidth=2,
            markersize=6)
    # Gain variation band
    if len(peaks) > 1:
        pk_mean = sum(peaks) / len(peaks)
        pk_std  = (sum((p - pk_mean)**2
                       for p in peaks) / len(peaks)) ** 0.5
        ax.axhspan(pk_mean - pk_std, pk_mean + pk_std,
                   color='blue', alpha=0.07,
                   label=f'Peak \u00b11\u03c3 ({pk_std:.2f} dB)')
    ax.set_xlabel('Frequency (MHz)', fontsize=12)
    ax.set_ylabel('Gain (dBi)', fontsize=12)
    ax.set_title('Gain vs Frequency', fontsize=14,
                 fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.92])
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
def _render_bw_vs_freq_az(plt: "ModuleType", pdf: "PdfPages",
                            summaries: list[dict],
                            np: "ModuleType",
                            report_cfg: dict | None = None) -> None:
    """Azimuth Beamwidth-vs-frequency trend page."""
    if report_cfg is None:
        report_cfg = {}
    fig, ax = plt.subplots(figsize=(11, 8.5))
    freqs = [s['freq'] for s in summaries if s['freq'] is not None]
    az_bws = [s['az_bw'] for s in summaries if s['freq'] is not None]
    if not freqs:
        plt.close(fig)
        return

    _is_omni = str(report_cfg.get("_antenna_type", "")).lower() == "omni"
    _az_label = "Az Beamwidth" if _is_omni else "Azimuth 3 dB Beamwidth"

    ax.plot(freqs, az_bws, 'b-o', linewidth=2, markersize=6)
    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('Az BW (deg)' if _is_omni else 'Az 3 dB BW (deg)')
    ax.set_title(f'{_az_label} vs Frequency',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add F/B on a twin axis
    ftbs = [(s['freq'], s['ftb']) for s in summaries
            if s['freq'] is not None and s['ftb'] is not None]
    if ftbs:
        ax2 = ax.twinx()
        f_ftb = [x[0] for x in ftbs]
        v_ftb = [x[1] for x in ftbs]
        ax2.plot(f_ftb, v_ftb, 'g--^', linewidth=1.5,
                 markersize=5, alpha=0.7, label='F/B (dB)')
        ax2.set_ylabel('Front-to-Back (dB)', color='green')
        ax2.legend(loc='lower left', fontsize=8)

    fig.suptitle(f'{_az_label} & F/B Trend',
                 fontsize=14, fontweight='bold', y=0.95)
    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.92])
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)

def _render_bw_vs_freq_el(plt: "ModuleType", pdf: "PdfPages",
                          summaries: list[dict],
                          np: "ModuleType",
                          report_cfg: dict | None = None) -> None:
    """Elevation Beamwidth-vs-frequency trend page."""
    if report_cfg is None:
        report_cfg = {}
    fig, ax = plt.subplots(figsize=(11, 8.5))
    freqs = [s['freq'] for s in summaries if s['freq'] is not None]
    el_bws = [s['el_bw'] for s in summaries if s['freq'] is not None]
    if not freqs:
        plt.close(fig)
        return

    ax.plot(freqs, el_bws, 'r-s', linewidth=2, markersize=6)
    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('El 3 dB BW (deg)')
    ax.set_title('Elevation 3 dB Beamwidth vs Frequency',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    fig.suptitle('Elevation 3 dB Beamwidth Trend',
                 fontsize=14, fontweight='bold', y=0.95)
    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.92])
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
def _render_overlay_cuts_cartesian(plt: "ModuleType", pdf: "PdfPages",
                                     summaries: list[dict],
                                     np: "ModuleType",
                                     report_cfg: dict | None = None) -> None:
    """Overlay all frequency cuts on one page (Cartesian)."""
    if report_cfg is None:
        report_cfg = {}
    import matplotlib.colors as mcolors
    fig, (ax_az, ax_el) = plt.subplots(1, 2, figsize=(11, 8.5))
    fig.suptitle('Cartesian Cut Overlay - All Frequencies',
                 fontsize=14, fontweight='bold', y=0.95)
    n_curves = len(summaries)
    use_colorbar = n_curves > 20
    lw = max(0.3, 1.5 - n_curves * 0.01)
    colors = plt.cm.turbo(np.linspace(0, 1, max(n_curves, 1)))

    for i, s in enumerate(summaries):
        lbl = (f"{s['freq']:.0f}" if s['freq']
               else os.path.basename(s['file'])[:12])
        c = colors[i]
        # Cartesian plots
        ax_az.plot(s['az'], s['arr'][s['el0'], :], color=c,
                   linewidth=lw, label=lbl if not use_colorbar else None)
        ax_el.plot(s['el'], s['arr'][:, s['az0']], color=c,
                   linewidth=lw, label=lbl if not use_colorbar else None)

    ax_az.set_xlabel('Azimuth (deg)')
    ax_az.set_ylabel('Gain (dBi)')
    ax_az.set_title('Az Cuts (el=0)', fontsize=10)
    ax_az.grid(True, alpha=0.3)
    ax_el.set_xlabel('Elevation (deg)')
    ax_el.set_ylabel('Gain (dBi)')
    ax_el.set_title('El Cuts (az=0)', fontsize=10)
    ax_el.grid(True, alpha=0.3)

    if use_colorbar:
        freqs = [s['freq'] for s in summaries if s['freq'] is not None]
        if freqs:
            f_lo, f_hi = min(freqs), max(freqs)
            norm = mcolors.Normalize(vmin=f_lo, vmax=f_hi)
            sm = plt.cm.ScalarMappable(cmap='turbo', norm=norm)
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=[ax_az, ax_el],
                                orientation='vertical', fraction=0.03, pad=0.04)
            cbar.set_label('Freq (MHz)', fontsize=9)
    else:
        ax_az.legend(fontsize=5, ncol=2)
        ax_el.legend(fontsize=5, ncol=2)

    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.92])
    _add_axes_classification(ax_az, report_cfg)
    _add_axes_classification(ax_el, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)

def _render_overlay_cuts_polar(plt: "ModuleType", pdf: "PdfPages",
                               summaries: list[dict],
                               np: "ModuleType",
                               plane: str,
                               report_cfg: dict | None = None) -> None:
    """Overlay all frequency cuts on one page (Polar)."""
    if report_cfg is None:
        report_cfg = {}
    import matplotlib.colors as mcolors
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_subplot(111, projection='polar')
    fig.suptitle(f'Polar {plane} Cut Overlay - All Frequencies',
                 fontsize=14, fontweight='bold', y=0.95)
    n_curves = len(summaries)
    use_colorbar = n_curves > 20
    lw = max(0.3, 1.5 - n_curves * 0.01)
    colors = plt.cm.turbo(np.linspace(0, 1, max(n_curves, 1)))

    for i, s in enumerate(summaries):
        lbl = (f"{s['freq']:.0f}" if s['freq']
               else os.path.basename(s['file'])[:12])
        c = colors[i]
        arr = s['arr']
        peak = float(arr.max())
        floor = peak - 40
        
        if plane == "Azimuth":
            cut = arr[s['el0'], :]
            angles = s['az']
        else:
            cut = arr[:, s['az0']]
            angles = s['el']

        norm = np.clip(cut, floor, peak)
        norm = (norm - floor) / max(peak - floor, 1)
        ax.plot(np.radians(angles), norm, color=c,
                linewidth=lw * 0.8, label=lbl if not use_colorbar else None)

    ax.set_title(f'{plane} Cuts', fontsize=10, pad=15)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    if use_colorbar:
        freqs = [s['freq'] for s in summaries if s['freq'] is not None]
        if freqs:
            f_lo, f_hi = min(freqs), max(freqs)
            norm = mcolors.Normalize(vmin=f_lo, vmax=f_hi)
            sm = plt.cm.ScalarMappable(cmap='turbo', norm=norm)
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, orientation='vertical',
                                fraction=0.08, pad=0.1)
            cbar.set_label('Freq (MHz)', fontsize=9)
    else:
        ax.legend(fontsize=6, ncol=2)

    fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
# ── Per-frequency renderers ──────────────────────────────────
def _render_per_freq_heatmap(plt: "ModuleType", pdf: "PdfPages",
                              s: dict, np: "ModuleType",
                              dyn_range: float,
                              extra_cuts: list[float],
                              report_cfg: dict | None = None) -> None:
    """Heatmap + az/el cuts combo page (2x2)."""
    if report_cfg is None:
        report_cfg = {}
    az = s['az']
    el = s['el']
    arr = s['arr']
    freq_str = (f"{s['freq']:.2f} MHz"
                if s['freq'] else
                os.path.basename(s['file']))
    fig = plt.figure(figsize=(11, 8.5))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
    fig.suptitle(f'Pattern @ {freq_str}',
                 fontsize=14, fontweight='bold', y=0.95)
    # ── Heatmap (top-left) ───────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    vmin = max(arr.min(), arr.max() - dyn_range)
    AZ, EL = np.meshgrid(az, el)
    im = ax1.pcolormesh(
        AZ, EL, arr,
        shading='gouraud', cmap='jet',
        vmin=vmin, vmax=arr.max()
    )
    ax1.set_xlim(az[0], az[-1])
    ax1.set_ylim(el[-1], el[0])
    fig.colorbar(im, ax=ax1, shrink=0.8, label='dBi')
    ax1.set_xlabel('Az (deg)', fontsize=9)
    ax1.set_ylabel('El (deg)', fontsize=9)
    ax1.set_title('Heatmap', fontsize=10)
    # Mark peak
    ax1.plot(s['peak_az'], s['peak_el'], 'w+',
             markersize=12, markeredgewidth=2)
    # ── Az cut (top-right) ───────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    el0 = s['el0']
    az_cut = arr[el0, :]
    ax2.plot(az, az_cut, 'b-', linewidth=1.2,
             label='el=0\u00b0')
    ax2.axhline(y=az_cut.max() - 3,
                color='r', linestyle='--',
                alpha=0.7, label='-3 dB')
    # Extra cut angles
    for ea in extra_cuts:
        dists = [abs(e - ea) for e in el]
        eidx = dists.index(min(dists))
        ax2.plot(az, arr[eidx, :], '--',
                 linewidth=0.9, alpha=0.7,
                 label=f'el={el[eidx]:.0f}\u00b0')
    ax2.set_xlabel('Az (deg)', fontsize=9)
    ax2.set_ylabel('Gain (dBi)', fontsize=9)
    ax2.set_title('Azimuth Cuts', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=7)
    ax2.set_xlim(az[0], az[-1])
    # ── El cut (bottom-left) ─────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    az0 = s['az0']
    el_cut = arr[:, az0]
    ax3.plot(el, el_cut, 'r-', linewidth=1.2,
             label='az=0\u00b0')
    ax3.axhline(y=el_cut.max() - 3,
                color='b', linestyle='--',
                alpha=0.7, label='-3 dB')
    for ea in extra_cuts:
        dists = [abs(a - ea) for a in az]
        aidx = dists.index(min(dists))
        ax3.plot(el, arr[:, aidx], '--',
                 linewidth=0.9, alpha=0.7,
                 label=f'az={az[aidx]:.0f}\u00b0')
    ax3.set_xlabel('El (deg)', fontsize=9)
    ax3.set_ylabel('Gain (dBi)', fontsize=9)
    ax3.set_title('Elevation Cuts', fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=7)
    ax3.set_xlim(el[0], el[-1])
    # ── Quick stats (bottom-right) ───────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')
    lines = [
        f"Peak Gain:  {s['peak_gain']:.2f} dBi",
        f"Boresight:  {s['bore_gain']:.2f} dBi",
        f"Peak at:    az={s['peak_az']:.0f}\u00b0  "
        f"el={s['peak_el']:.0f}\u00b0",
        f"Az 3 dB BW: ~{s['az_bw']}\u00b0",
        f"El 3 dB BW: ~{s['el_bw']}\u00b0",
    ]
    if s['ftb'] is not None:
        lines.append(f"F/B Ratio:  {s['ftb']:.1f} dB")
    if s['first_sll']:
        lines.append(
            f"1st SLL:    -{s['first_sll']['relative']:.1f}"
            f" dB @ {s['first_sll']['angle']:.0f}\u00b0"
        )
    ax4.text(0.08, 0.78, '\n'.join(lines),
             transform=ax4.transAxes,
             fontsize=10, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round',
                       facecolor='#f0f0f0', alpha=0.8))
    _add_axes_classification(ax1, report_cfg)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.90, bottom=0.08)
    _add_axes_classification(ax2, report_cfg)
    _add_axes_classification(ax3, report_cfg)
    _add_axes_classification(ax4, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
def _render_per_freq_polar_az(plt: "ModuleType", pdf: "PdfPages",
                                s: dict, np: "ModuleType",
                                polar_range: float,
                                report_cfg: dict | None = None) -> None:
    """Full-page polar plot for Azimuth."""
    if report_cfg is None:
        report_cfg = {}
    az = s['az']
    arr = s['arr']
    freq_str = (f"{s['freq']:.2f} MHz"
                if s['freq'] else
                os.path.basename(s['file']))
    fig, ax = plt.subplots(figsize=(11, 8.5), subplot_kw={'projection': 'polar'})
    fig.suptitle(f'Azimuth Polar Pattern @ {freq_str}',
                 fontsize=14, fontweight='bold', y=0.95)
    az_cut = arr[s['el0'], :]
    peak = float(arr.max())
    floor = peak - polar_range
    
    az_rad = np.radians(az)
    az_norm = np.clip(az_cut, floor, peak)
    az_plot = az_norm - floor
    ax.plot(az_rad, az_plot, 'b-', linewidth=1.5)
    ax.fill(az_rad, az_plot, alpha=0.15, color='blue')
    ax.set_title('Azimuth (el=0\u00b0)', pad=20,
                  fontsize=11)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ring_vals = np.linspace(0, peak - floor, 5)
    ring_labels = [f"{v + floor:.0f}" for v in ring_vals]
    ax.set_rticks(ring_vals)
    ax.set_yticklabels(ring_labels, fontsize=7)

    thresh = peak - 3 - floor
    if thresh > 0:
        theta_ring = np.linspace(0, 2 * np.pi, 200)
        ax.plot(theta_ring, [thresh] * 200, 'g--',
                 linewidth=0.8, alpha=0.6, label='-3 dB')
        ax.legend(fontsize=7, loc='lower right')

    fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)

def _render_per_freq_polar_el(plt: "ModuleType", pdf: "PdfPages",
                              s: dict, np: "ModuleType",
                              polar_range: float,
                              report_cfg: dict | None = None) -> None:
    """Full-page polar plot for Elevation."""
    if report_cfg is None:
        report_cfg = {}
    el = s['el']
    arr = s['arr']
    freq_str = (f"{s['freq']:.2f} MHz"
                if s['freq'] else
                os.path.basename(s['file']))
    fig, ax = plt.subplots(figsize=(11, 8.5), subplot_kw={'projection': 'polar'})
    fig.suptitle(f'Elevation Polar Pattern @ {freq_str}',
                 fontsize=14, fontweight='bold', y=0.95)
    el_cut = arr[:, s['az0']]
    peak = float(arr.max())
    floor = peak - polar_range
    
    el_rad = np.radians(el)
    el_norm = np.clip(el_cut, floor, peak)
    el_plot = el_norm - floor
    ax.plot(el_rad, el_plot, 'r-', linewidth=1.5)
    ax.fill(el_rad, el_plot, alpha=0.15, color='red')
    ax.set_title('Elevation (az=0\u00b0)', pad=20,
                  fontsize=11)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ring_vals = np.linspace(0, peak - floor, 5)
    ring_labels = [f"{v + floor:.0f}" for v in ring_vals]
    ax.set_rticks(ring_vals)
    ax.set_yticklabels(ring_labels, fontsize=7)

    thresh = peak - 3 - floor
    if thresh > 0:
        theta_ring = np.linspace(0, 2 * np.pi, 200)
        ax.plot(theta_ring, [thresh] * 200, 'g--',
                 linewidth=0.8, alpha=0.6, label='-3 dB')
        ax.legend(fontsize=7, loc='lower right')

    fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
def _render_per_freq_3d(plt: "ModuleType", pdf: "PdfPages",
                        s: dict, np: "ModuleType",
                        dyn_range: float,
                        report_cfg: dict | None = None) -> None:
    """Full-page 3-D surface plot."""
    if report_cfg is None:
        report_cfg = {}
    az = s['az']
    el = s['el']
    arr = s['arr']
    freq_str = (f"{s['freq']:.2f} MHz"
                if s['freq'] else
                os.path.basename(s['file']))
    # Subsample for speed
    step = max(1, len(az) // 90)
    az_sub = az[::step]
    el_sub = el[::step]
    arr_sub = arr[::step, ::step]
    AZ, EL = np.meshgrid(az_sub, el_sub)
    vmin = max(arr_sub.min(), arr_sub.max() - dyn_range)
    arr_clipped = np.clip(arr_sub, vmin, arr_sub.max())
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(
        AZ, EL, arr_clipped,
        cmap='jet', alpha=0.85,
        rstride=1, cstride=1
    )
    fig.colorbar(surf, shrink=0.45, label='Gain (dBi)')
    ax.set_xlabel('Azimuth (deg)')
    ax.set_ylabel('Elevation (deg)')
    ax.set_zlabel('Gain (dBi)')
    ax.set_title(f'3-D Surface @ {freq_str}',
                 fontsize=14, fontweight='bold')
    # tight_layout is incompatible with 3D axes; use manual spacing
    fig.subplots_adjust(left=0.05, right=0.92,
                        top=0.88, bottom=0.08)
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
def _render_per_freq_analysis(plt: "ModuleType", pdf: "PdfPages",
                              s: dict,
                              report_cfg: dict) -> None:
    """Full-page detailed analysis for one frequency."""
    freq_str = (f"{s['freq']:.2f} MHz"
                if s['freq'] else
                os.path.basename(s['file']))
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    fig.suptitle(f'Detailed Analysis @ {freq_str}',
                 fontsize=14, fontweight='bold', y=0.95)
    fig.subplots_adjust(top=0.90, bottom=0.05)
    blocks = []
    if report_cfg.get("per_freq_stats"):
        block = [
            "PATTERN STATISTICS",
            "\u2500" * 50,
            f"  Peak Gain ............. {s['peak_gain']:.2f} dBi",
            f"  Boresight Gain ........ {s['bore_gain']:.2f} dBi",
            f"  Peak Location ......... "
            f"az={s['peak_az']:.0f}\u00b0  "
            f"el={s['peak_el']:.0f}\u00b0",
            f"  Min Gain .............. {s['min_gain']:.2f} dBi",
            f"  Mean Gain ............. {s['avg_gain']:.2f} dBi",
            f"  Dynamic Range ......... {s['dynamic_range']:.1f} dB",
            f"  {'Az Beamwidth' if str(report_cfg.get('_antenna_type', '')).lower() == 'omni' else 'Az 3 dB Beamwidth'}"
            f" ..... ~{s['az_bw']}\u00b0",
            f"  El 3 dB Beamwidth ..... ~{s['el_bw']}\u00b0",
        ]
        if s['ftb'] is not None:
            block.append(
                f"  Front-to-Back ......... {s['ftb']:.1f} dB"
            )
        blocks.append('\n'.join(block))
    if report_cfg.get("per_freq_sidelobe"):
        block = [
            "",
            "SIDELOBE ANALYSIS",
            "\u2500" * 50,
        ]
        if s['first_sll']:
            sl = s['first_sll']
            block.append(
                f"  Az 1st Sidelobe ....... {sl['level']:.1f} dBi"
                f"  @ {sl['angle']:.0f}\u00b0"
            )
            block.append(
                f"  Az SLL below peak ..... -{sl['relative']:.1f} dB"
            )
        else:
            block.append(
                "  Az 1st Sidelobe ....... not detected"
            )
        if s.get('el_first_sll'):
            sl = s['el_first_sll']
            block.append(
                f"  El 1st Sidelobe ....... {sl['level']:.1f} dBi"
                f"  @ {sl['angle']:.0f}\u00b0"
            )
            block.append(
                f"  El SLL below peak ..... -{sl['relative']:.1f} dB"
            )
        else:
            block.append(
                "  El 1st Sidelobe ....... not detected"
            )
        blocks.append('\n'.join(block))
    if report_cfg.get("per_freq_detailed"):
        block = [
            "",
            "HEMISPHERIC ANALYSIS",
            "\u2500" * 50,
        ]
        if s['front_avg'] is not None:
            block.append(
                f"  Front hemisphere avg .. "
                f"{s['front_avg']:.2f} dBi"
            )
        if s['back_avg'] is not None:
            block.append(
                f"  Back hemisphere avg ... "
                f"{s['back_avg']:.2f} dBi"
            )
        if (s['front_avg'] is not None
                and s['back_avg'] is not None):
            diff = s['front_avg'] - s['back_avg']
            block.append(
                f"  F/B avg difference .... {diff:.1f} dB"
            )
        block.append("")
        block.append("SYMMETRY")
        block.append("\u2500" * 50)
        block.append(
            f"  Az RMS asymmetry ...... {s['asym_az']:.2f} dB"
        )
        block.append(
            f"  El RMS asymmetry ...... {s['asym_el']:.2f} dB"
        )
        total = s['total_pts']
        block.append("")
        block.append("COVERAGE")
        block.append("\u2500" * 50)
        block.append(
            f"  \u2265 0 dBi .............. "
            f"{s['above_0']}/{total}"
            f"  ({100 * s['above_0'] / total:.1f}%)"
        )
        block.append(
            f"  Within 3 dB of peak .. "
            f"{s['above_m3']}/{total}"
            f"  ({100 * s['above_m3'] / total:.1f}%)"
        )
        block.append(
            f"  Within 10 dB of peak . "
            f"{s['above_m10']}/{total}"
            f"  ({100 * s['above_m10'] / total:.1f}%)"
        )
        blocks.append('\n'.join(block))
    full_text = '\n'.join(blocks)
    ax.text(0.05, 0.92, full_text,
            transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            fontfamily='monospace',
            bbox=dict(boxstyle='round',
                      facecolor='#f8f8f8', alpha=0.9))
    _add_axes_classification(ax, report_cfg)
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
def _render_xpol_pages(plt: "ModuleType", pdf: "PdfPages",
                        xpol_summaries: list[dict],
                        np: "ModuleType",
                        dyn_range: float,
                        report_cfg: dict | None = None) -> None:
    """Cross-pol summary + per-freq heatmaps."""
    if report_cfg is None:
        report_cfg = {}
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    fig.suptitle('Cross-Polarisation Summary',
                 fontsize=16, fontweight='bold', y=0.95)
    fig.subplots_adjust(top=0.90, bottom=0.05)
    headers = ['Freq\n(MHz)', 'Peak XP\n(dBi)',
               'Bore XP\n(dBi)']
    table_data = []
    for xs in xpol_summaries:
        freq_str = (f"{xs['freq']:.1f}"
                    if xs['freq'] else "?")
        table_data.append([
            freq_str,
            f"{xs['peak_gain']:.1f}",
            f"{xs['bore_gain']:.1f}",
        ])
    if table_data:
        table = ax.table(
            cellText=table_data, colLabels=headers,
            cellLoc='center', loc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.0, 1.4)
        for j in range(len(headers)):
            cell = table[0, j]
            cell.set_facecolor('#C44472')
            cell.set_text_props(
                color='white', fontweight='bold'
            )
    _draw_pdf_classification_banners(fig, report_cfg)
    pdf.savefig(fig)
    plt.close(fig)
    for xs in xpol_summaries:
        az = xs['az']
        el = xs['el']
        arr = xs['arr']
        freq_str = (f"{xs['freq']:.2f} MHz"
                    if xs['freq'] else "?")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        vmin = max(arr.min(), arr.max() - dyn_range)
        AZ, EL = np.meshgrid(az, el)
        im = ax.pcolormesh(
            AZ, EL, arr,
            shading='gouraud', cmap='jet',
            vmin=vmin, vmax=arr.max()
        )
        ax.set_xlim(az[0], az[-1])
        ax.set_ylim(el[-1], el[0])
        fig.colorbar(im, ax=ax, shrink=0.8, label='dBi')
        ax.set_xlabel('Az (deg)')
        ax.set_ylabel('El (deg)')
        ax.set_title(f'Cross-Pol @ {freq_str}',
                     fontsize=14, fontweight='bold')
        fig.subplots_adjust(left=0.1, right=0.9, top=0.88, bottom=0.1)
        _add_axes_classification(ax, report_cfg)
        _draw_pdf_classification_banners(fig, report_cfg)
        pdf.savefig(fig)
        plt.close(fig)


def _render_config_page(plt: "ModuleType", pdf: "PdfPages",
                        input_dir: str,
                        report_cfg: dict | None = None) -> None:
    """Render the generation configuration as the final report page.

    Reads ``generation_config.json`` from *input_dir* and renders it
    as formatted monospace text.  Silently skipped if the file is
    missing (e.g. for legacy pattern directories).
    """
    import json

    if report_cfg is None:
        report_cfg = {}
    config_path = os.path.join(input_dir, "generation_config.json")
    if not os.path.isfile(config_path):
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception:
        logger.warning("Could not read %s — skipping config page",
                       config_path)
        return

    # ── Format config into readable sections ──────────────
    lines = []

    # Core parameters
    lines.append("GENERATION CONFIGURATION")
    lines.append("\u2500" * 55)
    _kv = [
        ("Antenna Type",     cfg.get("antenna_type", "?")),
        ("Peak Gain",        f"{cfg.get('max_gain_dbi', '?')} dBi"),
        ("Az Beamwidth" if str(cfg.get('antenna_type', '')).lower() == 'omni'
         else "Az 3 dB Beamwidth", f"{cfg.get('az_beamwidth_deg', '?')}\u00b0"),
        ("El 3 dB Beamwidth", f"{cfg.get('el_beamwidth_deg', '?')}\u00b0"),
        ("F/B Ratio",        f"{cfg.get('ftb_ratio_db', '?')} dB"),
        ("Freq Range",       f"{cfg.get('f_min_mhz', '?')} \u2013 "
                             f"{cfg.get('f_max_mhz', '?')} MHz"),
        ("Slices",           f"{cfg.get('n_slices', '?')} "
                             f"({cfg.get('freq_spacing', '?')})"),
        ("Ref Frequency",    f"{cfg.get('ref_frequency_mhz') or 'auto'}"
                             f" MHz"),
        ("Polarization",     cfg.get("polarization", "?")),
        ("Az Step",          f"{cfg.get('az_step_deg', '?')}\u00b0"),
        ("El Step",          f"{cfg.get('el_step_deg', '?')}\u00b0"),
        ("Noise",            f"{cfg.get('noise_range_db', 0)} dB"),
        ("Sigmoid k",        f"{cfg.get('sigmoid_k', '?')}"),
    ]
    for label, val in _kv:
        lines.append(f"  {label:<22s} {val}")

    # Features
    features = cfg.get("features", {})
    if features:
        lines.append("")
        lines.append("FEATURES")
        lines.append("\u2500" * 55)
        for feat_name, feat_cfg in features.items():
            if not isinstance(feat_cfg, dict):
                continue
            enabled = feat_cfg.get("enabled", False)
            tag = "\u2713" if enabled else "\u2717"
            label = feat_name.replace("_", " ").title()
            lines.append(f"  {tag} {label}")
            if enabled:
                for k, v in feat_cfg.items():
                    if k in ("enabled", "description"):
                        continue
                    k_fmt = k.replace("_", " ")
                    lines.append(f"      {k_fmt:<28s} {v}")

    # Type-specific params
    extras = []
    for key in ("panel_downtilt_deg", "dish_efficiency",
                "element_length_wavelengths",
                "array_geometry", "array_n_elements_x",
                "array_n_elements_y", "array_spacing_x_lambda",
                "array_weighting", "array_mutual_coupling"):
        if key in cfg:
            extras.append((key.replace("_", " ").title(), cfg[key]))
    if extras:
        lines.append("")
        lines.append("TYPE-SPECIFIC PARAMETERS")
        lines.append("\u2500" * 55)
        for label, val in extras:
            lines.append(f"  {label:<28s} {val}")

    full_text = '\n'.join(lines)

    # ── Paginate into two-column pages if text is tall ────
    # Each page can hold ~MAX_LINES_PER_COL lines per column,
    # two columns side-by-side.
    MAX_LINES_PER_COL = 52
    all_lines = full_text.split('\n')
    lines_per_page = MAX_LINES_PER_COL * 2  # two columns

    page_chunks: list[tuple[str, str]] = []
    for start in range(0, len(all_lines), lines_per_page):
        page_lines = all_lines[start:start + lines_per_page]
        col1 = page_lines[:MAX_LINES_PER_COL]
        col2 = page_lines[MAX_LINES_PER_COL:]
        page_chunks.append(('\n'.join(col1), '\n'.join(col2)))

    for page_idx, (col1_text, col2_text) in enumerate(page_chunks):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        suffix = (f' ({page_idx + 1}/{len(page_chunks)})'
                  if len(page_chunks) > 1 else '')
        fig.suptitle(f'Generation Configuration{suffix}',
                     fontsize=14, fontweight='bold', y=0.95)
        fig.subplots_adjust(top=0.90, bottom=0.05)
        # Left column
        ax.text(0.02, 0.92, col1_text,
                transform=ax.transAxes,
                fontsize=7.5, verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round',
                          facecolor='#f8f8f8', alpha=0.9))
        # Right column (if any content)
        if col2_text.strip():
            ax.text(0.52, 0.92, col2_text,
                    transform=ax.transAxes,
                    fontsize=7.5, verticalalignment='top',
                    fontfamily='monospace',
                    bbox=dict(boxstyle='round',
                              facecolor='#f8f8f8', alpha=0.9))
        _add_axes_classification(ax, report_cfg)
        _draw_pdf_classification_banners(fig, report_cfg)
        pdf.savefig(fig)
        plt.close(fig)