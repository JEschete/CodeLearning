"""
LaTeX report generation with configurable sections.

Produces a standalone .tex file (compilable with pdflatex) that
mirrors the PDF report structure: cover, TOC, summary table,
gain/BW trend plots, overlay cuts, per-frequency heatmap + cuts
combos, polar plots, 3-D surfaces, and detailed analysis pages.

Plot images are saved alongside the .tex file and referenced via
\\includegraphics.  The user can then edit the .tex freely before
compiling.

Requires matplotlib + numpy for plot generation. The .tex itself
needs only a standard TeX Live or MiKTeX installation.
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
    from matplotlib.figure import Figure as _Figure

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
from reporting.report import (
    REPORT_SECTIONS, REPORT_OPTIONS,
    default_report_config, _compute_summary, _find_xpol,
    CLASSIFICATION_LEVELS, _CLASSIFICATION_COLORS,
    _get_classification_text, _get_figure_classification,
    _add_axes_classification,
)


# ===================================================================
#  LaTeX HELPERS
# ===================================================================

# Mapping classification level -> LaTeX \colorbox colour definition
_LATEX_CLS_COLORS: dict[str, tuple[str, str]] = {
    "UNCLASSIFIED":    ("0.0, 0.5, 0.0",   "white"),  # green bg
    "CUI":             ("0.33, 0.10, 0.55", "white"),  # purple bg
    "CONFIDENTIAL":    ("0.0, 0.0, 1.0",   "white"),  # blue bg
    "SECRET":          ("1.0, 0.0, 0.0",   "white"),  # red bg
    "TOP SECRET":      ("1.0, 0.55, 0.0",  "black"),  # orange bg
    "TOP SECRET//SCI": ("1.0, 0.84, 0.0",  "black"),  # gold bg
}

def _tex_escape(text: str) -> str:
    """Escape special LaTeX characters in plain text."""
    replacements = {
        '&': r'\&', '%': r'\%', '$': r'\$',
        '#': r'\#', '_': r'\_', '{': r'\{',
        '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _save_figure(plt: "ModuleType", fig: _Figure,
                 img_dir: str, name: str,
                 *, tex_dir: str | None = None) -> str:
    """Save a matplotlib figure as PNG and return relative path.

    When *tex_dir* is provided the returned path is computed via
    ``os.path.relpath`` so that images stored in subdirectories
    (e.g. ``images/heatmaps/``) get a correct LaTeX reference.
    """
    path = os.path.join(img_dir, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    # Return path relative to the .tex file
    if tex_dir:
        return os.path.relpath(path, tex_dir).replace('\\', '/')
    return f"images/{name}"


def _cls_caption(base_caption: str, fig_cls: str) -> str:
    """Wrap a caption string, appending the classification marking.

    Returns e.g.  ``\\caption{Some caption. (UNCLASSIFIED)}``
    """
    if fig_cls and fig_cls != "UNCLASSIFIED":
        return (r"\caption{" + base_caption
                + " (" + _tex_escape(fig_cls) + r")}")
    # Still include UNCLASSIFIED if set
    if fig_cls:
        return (r"\caption{" + base_caption
                + " (" + _tex_escape(fig_cls) + r")}")
    return r"\caption{" + base_caption + "}"


def _render_latex_config_page(lines: list[str],
                              input_dir: str,
                              report_cfg: dict | None = None) -> None:
    """Append a generation-configuration page to the LaTeX body.

    Reads ``generation_config.json`` from *input_dir* and renders it
    as a verbatim listing.  Silently skipped if the file is missing.
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

    fig_cls = report_cfg.get("classification", "")

    lines.append(r"\clearpage")
    lines.append(r"\section*{Generation Configuration}")
    if fig_cls:
        lines.append(r"\begin{center}\textbf{"
                      + _tex_escape(fig_cls) + r"}\end{center}")

    # Core parameters table
    kv = [
        ("Antenna Type",  str(cfg.get("antenna_type", "?"))),
        ("Peak Gain",     f"{cfg.get('max_gain_dbi', '?')} dBi"),
        ("Az Beamwidth",  f"{cfg.get('az_beamwidth_deg', '?')}°"),
        ("El Beamwidth",  f"{cfg.get('el_beamwidth_deg', '?')}°"),
        ("F/B Ratio",     f"{cfg.get('ftb_ratio_db', '?')} dB"),
        ("Freq Range",    f"{cfg.get('f_min_mhz', '?')} -- "
                          f"{cfg.get('f_max_mhz', '?')} MHz"),
        ("Slices",        f"{cfg.get('n_slices', '?')} "
                          f"({cfg.get('freq_spacing', '?')})"),
        ("Ref Frequency", f"{cfg.get('ref_frequency_mhz') or 'auto'}"
                          f" MHz"),
        ("Polarization",  str(cfg.get("polarization", "?"))),
        ("Az Step",       f"{cfg.get('az_step_deg', '?')}°"),
        ("El Step",       f"{cfg.get('el_step_deg', '?')}°"),
        ("Noise",         f"{cfg.get('noise_range_db', 0)} dB"),
        ("Sigmoid k",     str(cfg.get("sigmoid_k", "?"))),
    ]

    lines.append(r"\subsection*{Core Parameters}")
    lines.append(r"\begin{tabular}{ll}")
    lines.append(r"\hline")
    for label, val in kv:
        lines.append(
            _tex_escape(label) + r" & "
            + _tex_escape(val) + r" \\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\vspace{1em}")

    # Features
    features = cfg.get("features", {})
    if features:
        lines.append(r"\subsection*{Features}")
        lines.append(r"\begin{tabular}{lll}")
        lines.append(r"\hline")
        lines.append(r"\textbf{Feature} & \textbf{Enabled}"
                      r" & \textbf{Parameters} \\")
        lines.append(r"\hline")
        for feat_name, feat_cfg in features.items():
            if not isinstance(feat_cfg, dict):
                continue
            enabled = feat_cfg.get("enabled", False)
            label = _tex_escape(
                feat_name.replace("_", " ").title())
            status = "Yes" if enabled else "No"
            params = []
            if enabled:
                for k, v in feat_cfg.items():
                    if k in ("enabled", "description"):
                        continue
                    params.append(
                        f"{k.replace('_', ' ')}: {v}")
            param_str = _tex_escape(", ".join(params)) if params else ""
            lines.append(
                label + " & " + status
                + " & " + param_str + r" \\")
        lines.append(r"\hline")
        lines.append(r"\end{tabular}")

    lines.append("")


# ===================================================================
#  MAIN LaTeX GENERATOR
# ===================================================================

def generate_latex_report(input_dir: str,
                          output_path: str | None = None,
                          title: str | None = None,
                          report_cfg: dict | None = None) -> str | None:
    """Generate a .tex report from a directory of pattern CSVs.

    Args:
        input_dir:   directory containing pattern CSV files
        output_path: output .tex path (auto if None)
        title:       report title (auto-generated if None)
        report_cfg:  dict from default_report_config(); None -> defaults

    Returns:
        output_path
    """
    try:
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        logger.error("matplotlib and numpy required for report generation.")
        logger.error("Install: pip install matplotlib numpy")
        return None

    if report_cfg is None:
        report_cfg = default_report_config()

    # ── Locate CSV files ─────────────────────────────────
    csv_files = sorted(
        [*glob.glob(os.path.join(input_dir, "*_copol.csv")),
         *glob.glob(os.path.join(input_dir, "*_copol.dat"))],
        key=lambda f: extract_freq_from_filename(f) or 0.0
    )
    if not csv_files:
        csv_files = sorted(
            [*glob.glob(os.path.join(input_dir, "*.csv")),
             *glob.glob(os.path.join(input_dir, "*.dat"))],
            key=lambda f: extract_freq_from_filename(f) or 0.0
        )
    if not csv_files:
        logger.error("No CSV/DAT files found in %s", input_dir)
        return None

    if output_path is None:
        if title:
            safe = _sanitise_filename(title)
        else:
            safe = "pattern_report"
        output_path = os.path.join(
            input_dir, f"{safe}.tex"
        )

    if title is None:
        title = os.path.basename(input_dir.rstrip('/\\'))

    # Create images directory next to .tex file, with plot type subfolders
    tex_dir = os.path.dirname(output_path) or "."
    images_root = os.path.join(tex_dir, "images")
    os.makedirs(images_root, exist_ok=True)

    logger.info("Generating LaTeX report for %d pattern files...",
                len(csv_files))

    dyn_range = report_cfg.get("dynamic_range_db", 60)
    polar_range = report_cfg.get("polar_range_db", 40)
    extra_cuts = report_cfg.get("extra_cut_angles", [])

    # ── Collect summary data ─────────────────────────────
    summaries = []
    for fp in csv_files:
        az, el, data = read_pattern_file(fp)
        arr = np.array(data)
        summaries.append(
            _compute_summary(fp, az, el, data, arr, np)
        )

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

    # Optional cross-pol
    xpol_summaries = []
    if report_cfg.get("include_xpol"):
        for s in summaries:
            xp = _find_xpol(s['file'])
            if xp:
                az, el, data = read_pattern_file(xp)
                arr = np.array(data)
                xpol_summaries.append(
                    _compute_summary(xp, az, el, data, arr, np)
                )

    # ── Build the .tex document ──────────────────────────
    lines = []

    # Create plot-type subdirectories under images/
    heatmap_dir  = os.path.join(images_root, 'heatmaps')
    polar_dir    = os.path.join(images_root, 'polar')
    surface_dir  = os.path.join(images_root, '3d_surface')
    xpol_dir     = os.path.join(images_root, 'xpol')
    for d in (heatmap_dir, polar_dir, surface_dir, xpol_dir):
        os.makedirs(d, exist_ok=True)

    # ── Classification text ───────────────────────────
    cls_text = _get_classification_text(report_cfg)
    fig_cls = _get_figure_classification(report_cfg)
    cls_base = report_cfg.get("classification", "UNCLASSIFIED").upper()
    cls_rgb, cls_fg = _LATEX_CLS_COLORS.get(
        cls_base, ("0.0, 0.5, 0.0", "white")
    )

    # Preamble
    lines.append(r"\documentclass[11pt,a4paper,landscape]{article}")
    lines.append(r"\usepackage[margin=1.5cm,top=2.2cm,bottom=2.2cm]{geometry}")
    lines.append(r"\usepackage{graphicx}")
    lines.append(r"\usepackage{booktabs}")
    lines.append(r"\usepackage{longtable}")
    lines.append(r"\usepackage{float}")
    lines.append(r"\usepackage{xcolor}")
    lines.append(r"\usepackage{hyperref}")
    lines.append(r"\usepackage{fancyhdr}")
    lines.append(r"\usepackage{titlesec}")
    lines.append(r"\usepackage{parskip}")
    lines.append(r"\usepackage{caption}")
    lines.append(r"\usepackage{subcaption}")
    lines.append(r"\usepackage{multicol}")
    lines.append("")
    lines.append(r"\hypersetup{colorlinks=true,"
                 r"linkcolor=blue,urlcolor=blue}")
    lines.append("")
    # Define classification colour
    lines.append(r"\definecolor{clsbg}{rgb}{" + cls_rgb + "}")
    lines.append("")
    lines.append(r"\pagestyle{fancy}")
    lines.append(r"\fancyhf{}")
    # Classification banner in header (centred, full-width coloured box)
    lines.append(
        r"\fancyhead[C]{\colorbox{clsbg}"
        r"{\makebox[\textwidth]{\textcolor{"
        + cls_fg + r"}{\textbf{" + _tex_escape(cls_text)
        + r"}}}}}"
    )
    # Footer: classification banner centre, page number right
    lines.append(
        r"\fancyfoot[C]{\colorbox{clsbg}"
        r"{\makebox[\textwidth]{\textcolor{"
        + cls_fg + r"}{\textbf{" + _tex_escape(cls_text)
        + r"}}}}}"
    )
    lines.append(
        r"\fancyfoot[R]{\textcolor{" + cls_fg
        + r"}{\thepage}}"
    )
    lines.append(r"\renewcommand{\headrulewidth}{0pt}")
    lines.append(r"\renewcommand{\footrulewidth}{0pt}")
    lines.append("")
    # Apply same style to plain pages (first page of chapters etc.)
    lines.append(r"\fancypagestyle{plain}{%")
    lines.append(r"  \fancyhf{}%")
    lines.append(
        r"  \fancyhead[C]{\colorbox{clsbg}"
        r"{\makebox[\textwidth]{\textcolor{"
        + cls_fg + r"}{\textbf{" + _tex_escape(cls_text)
        + r"}}}}}"
    )
    lines.append(
        r"  \fancyfoot[C]{\colorbox{clsbg}"
        r"{\makebox[\textwidth]{\textcolor{"
        + cls_fg + r"}{\textbf{" + _tex_escape(cls_text)
        + r"}}}}}"
    )
    lines.append(
        r"  \fancyfoot[R]{\textcolor{" + cls_fg
        + r"}{\thepage}}"
    )
    lines.append(r"}")
    lines.append("")
    lines.append(r"\title{\textbf{" +
                 _tex_escape(title) + r"} \\ "
                 r"\large Antenna Pattern Report}")
    lines.append(r"\author{Generated by AntennaForge}")
    lines.append(r"\date{\today}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append("")

    # ==================================================
    #  COVER PAGE
    # ==================================================
    if report_cfg.get("cover_page", True):
        cover_subtitle = report_cfg.get(
            "cover_subtitle", "Antenna Pattern Report")
        cover_author = report_cfg.get("cover_author", "")
        cover_org = report_cfg.get("cover_organisation", "")
        cover_project = report_cfg.get("cover_project", "")
        cover_doc_id = report_cfg.get("cover_document_id", "")
        cover_rev = report_cfg.get("cover_revision", "")
        cover_date = report_cfg.get("cover_date", "")

        lines.append(r"\begin{titlepage}")
        lines.append(r"\centering")
        # Classification banner at top of cover
        lines.append(
            r"\colorbox{clsbg}{\makebox[\textwidth]"
            r"{\textcolor{" + cls_fg + r"}{\textbf{"
            + _tex_escape(cls_text) + r"}}}}")
        lines.append(r"\vspace*{3cm}")
        lines.append(r"{\Huge\bfseries " +
                     _tex_escape(title) + r"}\par")
        if cover_subtitle:
            lines.append(r"\vspace{0.8cm}")
            lines.append(r"{\Large " +
                         _tex_escape(cover_subtitle) + r"}\par")
        lines.append(r"\vspace{1.5cm}")

        n_files = len(csv_files)
        lines.append(r"{\large " +
                     f"{n_files} frequency slice"
                     f"{'s' if n_files > 1 else ''}"
                     r"}\par")

        if summaries and summaries[0]['freq'] is not None:
            freqs = [s['freq'] for s in summaries
                     if s['freq'] is not None]
            f_lo, f_hi = min(freqs), max(freqs)
            pk = max(s['peak_gain'] for s in summaries)
            lines.append(r"\vspace{0.3cm}")
            lines.append(r"{\large " +
                         f"{f_lo:.1f} -- {f_hi:.1f} MHz"
                         r"}\par")
            lines.append(r"\vspace{0.3cm}")
            lines.append(r"{\large Peak gain: " +
                         f"{pk:.1f} dBi" + r"}\par")

        # Cover page info fields
        info_items = []
        if cover_author:
            info_items.append(("Author", cover_author))
        if cover_org:
            info_items.append(("Organisation", cover_org))
        if cover_project:
            info_items.append(("Project", cover_project))
        if cover_doc_id:
            info_items.append(("Document ID", cover_doc_id))
        if cover_rev:
            info_items.append(("Revision", cover_rev))
        if cover_date:
            info_items.append(("Date", cover_date))

        if info_items:
            lines.append(r"\vspace{1.5cm}")
            lines.append(r"\begin{tabular}{rl}")
            for label, value in info_items:
                lines.append(
                    r"  \textbf{" + _tex_escape(label)
                    + r":} & " + _tex_escape(value) + r" \\")
            lines.append(r"\end{tabular}")

        lines.append(r"\vfill")
        lines.append(r"{\small Generated by AntennaForge "
                     r"--- \today}\par")
        # Classification banner at bottom of cover
        lines.append(
            r"\colorbox{clsbg}{\makebox[\textwidth]"
            r"{\textcolor{" + cls_fg + r"}{\textbf{"
            + _tex_escape(cls_text) + r"}}}}")
        lines.append(r"\end{titlepage}")
        lines.append("")

    # ==================================================
    #  TABLE OF CONTENTS
    # ==================================================
    if report_cfg.get("table_of_contents", True):
        lines.append(r"\setcounter{tocdepth}{1}")
        lines.append(r"{\small")
        lines.append(r"\begin{multicols}{2}")
        lines.append(r"\tableofcontents")
        lines.append(r"\end{multicols}}")
        lines.append(r"\newpage")
        lines.append("")

    # ==================================================
    #  SUMMARY TABLE
    # ==================================================
    if report_cfg.get("summary_table", True):
        lines.append(r"\section{Pattern Summary}")
        lines.append("")
        lines.append(r"{\small")
        lines.append(r"\setlength{\tabcolsep}{4pt}")
        lines.append(r"\begin{longtable}{r r r r r r r c r r}")
        lines.append(r"\toprule")
        lines.append(r"\textbf{Freq} & \textbf{Peak} & "
                     r"\textbf{Bore} & \textbf{Az BW} & "
                     r"\textbf{El BW} & \textbf{F/B} & "
                     r"\textbf{1st SLL} & \textbf{Peak At} & "
                     r"\textbf{Min} & \textbf{Dyn Rng} \\")
        lines.append(r"\textbf{(MHz)} & \textbf{(dBi)} & "
                     r"\textbf{(dBi)} & \textbf{(deg)} & "
                     r"\textbf{(deg)} & \textbf{(dB)} & "
                     r"\textbf{(dB)} & \textbf{(az, el)} & "
                     r"\textbf{(dBi)} & \textbf{(dB)} \\")
        lines.append(r"\midrule")
        lines.append(r"\endhead")

        for s in summaries:
            freq_str = (f"{s['freq']:.1f}"
                        if s['freq'] else "?")
            ftb_str = (f"{s['ftb']:.1f}"
                       if s['ftb'] is not None else "---")
            sll_str = (
                f"$-${s['first_sll']['relative']:.1f}"
                if s['first_sll'] else "---"
            )
            line = (f"  {freq_str} & "
                    f"{s['peak_gain']:.1f} & "
                    f"{s['bore_gain']:.1f} & "
                    f"{s['az_bw']} & "
                    f"{s['el_bw']} & "
                    f"{ftb_str} & "
                    f"{sll_str} & "
                    f"({s['peak_az']:.0f}, {s['peak_el']:.0f}) & "
                    f"{s['min_gain']:.1f} & "
                    f"{s['dynamic_range']:.1f} \\\\")
            lines.append(line)

        lines.append(r"\bottomrule")
        lines.append(r"\end{longtable}}")
        lines.append(r"\newpage")
        lines.append("")

    # ==================================================
    #  GAIN vs FREQUENCY
    # ==================================================
    if report_cfg.get("gain_vs_freq", True):
        freqs = [s['freq'] for s in summaries
                 if s['freq'] is not None]
        if freqs:
            fig, ax = plt.subplots(figsize=(10, 5))
            peaks = [s['peak_gain'] for s in summaries
                     if s['freq'] is not None]
            bores = [s['bore_gain'] for s in summaries
                     if s['freq'] is not None]
            ax.plot(freqs, peaks, 'b-o', label='Peak Gain',
                    linewidth=2, markersize=5)
            ax.plot(freqs, bores, 'r--s', label='Boresight',
                    linewidth=2, markersize=5)
            if len(peaks) > 1:
                pk_mean = sum(peaks) / len(peaks)
                pk_std = (sum((p - pk_mean)**2
                              for p in peaks) / len(peaks)) ** 0.5
                ax.axhspan(pk_mean - pk_std, pk_mean + pk_std,
                           color='blue', alpha=0.07,
                           label=f'Peak $\\pm 1\\sigma$ '
                           f'({pk_std:.2f} dB)')
            ax.set_xlabel('Frequency (MHz)')
            ax.set_ylabel('Gain (dBi)')
            ax.set_title('Gain vs Frequency')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            _add_axes_classification(ax, report_cfg)
            img = _save_figure(plt, fig, images_root,
                               "gain_vs_freq.png",
                               tex_dir=tex_dir)

            lines.append(r"\section{Gain vs Frequency}")
            lines.append(r"\begin{figure}[H]")
            lines.append(r"\centering")
            lines.append(r"\includegraphics[width=0.80"
                         r"\textwidth]{" + img + "}")
            lines.append(_cls_caption(
                "Peak and boresight gain across the operating band.",
                fig_cls))
            lines.append(r"\end{figure}")
            lines.append(r"\newpage")
            lines.append("")

    # ==================================================
    #  BEAMWIDTH vs FREQUENCY
    # ==================================================
    if report_cfg.get("bw_vs_freq", True):
        freqs_bw = [s['freq'] for s in summaries
                    if s['freq'] is not None]
        if freqs_bw:
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            az_bws = [s['az_bw'] for s in summaries
                      if s['freq'] is not None]
            el_bws = [s['el_bw'] for s in summaries
                      if s['freq'] is not None]

            axes[0].plot(freqs_bw, az_bws, 'b-o',
                         linewidth=2, markersize=5)
            _is_omni = str(report_cfg.get('_antenna_type', '')).lower() == 'omni'
            _az_bw_title = 'Az Beamwidth' if _is_omni else 'Azimuth 3 dB Beamwidth'
            axes[0].set_xlabel('Frequency (MHz)')
            axes[0].set_ylabel('Az BW (deg)' if _is_omni else 'Az 3 dB BW (deg)')
            axes[0].set_title(_az_bw_title)
            axes[0].grid(True, alpha=0.3)

            axes[1].plot(freqs_bw, el_bws, 'r-s',
                         linewidth=2, markersize=5)
            axes[1].set_xlabel('Frequency (MHz)')
            axes[1].set_ylabel('El 3 dB BW (deg)')
            axes[1].set_title('Elevation Beamwidth')
            axes[1].grid(True, alpha=0.3)

            # F/B trend
            ftbs = [(s['freq'], s['ftb']) for s in summaries
                    if s['freq'] and s['ftb'] is not None]
            if ftbs:
                ax2 = axes[0].twinx()
                ax2.plot([x[0] for x in ftbs],
                         [x[1] for x in ftbs],
                         'g--^', linewidth=1.5, markersize=4,
                         alpha=0.7, label='F/B (dB)')
                ax2.set_ylabel('F/B (dB)', color='green')
                ax2.legend(loc='lower left', fontsize=8)

            fig.suptitle('Beamwidth \\& F/B Trends',
                         fontsize=13, fontweight='bold')
            plt.tight_layout()
            _add_axes_classification(axes[0], report_cfg)
            _add_axes_classification(axes[1], report_cfg)
            img = _save_figure(plt, fig, images_root,
                               "bw_vs_freq.png",
                               tex_dir=tex_dir)

            lines.append(r"\section{Beamwidth vs Frequency}")
            lines.append(r"\begin{figure}[H]")
            lines.append(r"\centering")
            lines.append(r"\includegraphics[width=0.90"
                         r"\textwidth]{" + img + "}")
            _bw_cap = ("Beamwidth and front-to-back ratio vs frequency."
                       if _is_omni else
                       "3~dB beamwidth and front-to-back ratio vs frequency.")
            lines.append(_cls_caption(_bw_cap, fig_cls))
            lines.append(r"\end{figure}")
            lines.append(r"\newpage")
            lines.append("")

    # ==================================================
    #  OVERLAY CUTS
    # ==================================================
    if report_cfg.get("overlay_cuts", True) and summaries:
        fig = plt.figure(figsize=(12, 8))
        ax_az = fig.add_subplot(2, 2, 1)
        ax_el = fig.add_subplot(2, 2, 2)
        ax_paz = fig.add_subplot(2, 2, 3, projection='polar')
        ax_pel = fig.add_subplot(2, 2, 4, projection='polar')

        colors = plt.cm.turbo(
            np.linspace(0, 1, max(len(summaries), 1))
        )
        for i, s in enumerate(summaries):
            az = s['az']; el = s['el']; arr = s['arr']
            el0 = s['el0']; az0 = s['az0']
            lbl = (f"{s['freq']:.0f}" if s['freq'] else "?")
            c = colors[i]
            az_cut = arr[el0, :]; el_cut = arr[:, az0]
            ax_az.plot(az, az_cut, color=c, lw=1, label=lbl)
            ax_el.plot(el, el_cut, color=c, lw=1, label=lbl)

            peak = float(arr.max()); floor = peak - 40
            az_n = np.clip(az_cut, floor, peak)
            az_n = (az_n - floor) / max(peak - floor, 1)
            el_n = np.clip(el_cut, floor, peak)
            el_n = (el_n - floor) / max(peak - floor, 1)
            ax_paz.plot(np.radians(az), az_n, color=c, lw=0.8)
            ax_pel.plot(np.radians(el), el_n, color=c, lw=0.8)

        ax_az.set_xlabel('Azimuth (deg)')
        ax_az.set_ylabel('Gain (dBi)')
        ax_az.set_title('Az Cuts (el=0)')
        ax_az.grid(True, alpha=0.3)
        ax_az.legend(fontsize=5, ncol=2)
        ax_el.set_xlabel('Elevation (deg)')
        ax_el.set_ylabel('Gain (dBi)')
        ax_el.set_title('El Cuts (az=0)')
        ax_el.grid(True, alpha=0.3)
        ax_el.legend(fontsize=5, ncol=2)
        ax_paz.set_title('Polar Az', fontsize=10, pad=15)
        ax_paz.set_theta_zero_location('N')
        ax_paz.set_theta_direction(-1)
        ax_pel.set_title('Polar El', fontsize=10, pad=15)
        ax_pel.set_theta_zero_location('N')
        ax_pel.set_theta_direction(-1)
        fig.suptitle('Cut Overlay --- All Frequencies',
                     fontsize=13, fontweight='bold')
        plt.tight_layout()
        _add_axes_classification(ax_az, report_cfg)
        _add_axes_classification(ax_el, report_cfg)
        _add_axes_classification(ax_paz, report_cfg)
        _add_axes_classification(ax_pel, report_cfg)
        img = _save_figure(plt, fig, images_root,
                           "overlay_cuts.png",
                           tex_dir=tex_dir)

        lines.append(r"\section{Overlay Cuts --- "
                     r"All Frequencies}")
        lines.append(r"\begin{figure}[H]")
        lines.append(r"\centering")
        lines.append(r"\includegraphics[width=0.90"
                     r"\textwidth]{" + img + "}")
        lines.append(_cls_caption(
            "Azimuth and elevation cuts overlaid for all frequency slices.",
            fig_cls))
        lines.append(r"\end{figure}")
        lines.append(r"\newpage")
        lines.append("")

    # ==================================================
    #  PER-FREQUENCY PAGES
    # ==================================================
    # Add a single parent section for all per-frequency pages
    if summaries:
        lines.append(r"\section{Per-Frequency Analysis}")
        lines.append("")

    for idx, s in enumerate(summaries):
        freq_str = (f"{s['freq']:.2f} MHz"
                    if s['freq'] else
                    os.path.basename(s['file']))
        freq_safe = freq_str.replace(' ', '_').replace('.', 'p')
        logger.info("[%d/%d] %s", idx+1, len(summaries), freq_str)

        section_label = _tex_escape(freq_str)
        lines.append(r"\subsection{" + section_label + "}")
        lines.append("")

        # ── Heatmap + cuts combo ─────────────────────
        if report_cfg.get("per_freq_heatmap"):
            az = s['az']; el = s['el']; arr = s['arr']

            fig = plt.figure(figsize=(12, 8))
            gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
            fig.suptitle(f'Pattern @ {freq_str}',
                         fontsize=13, fontweight='bold')

            # Heatmap
            ax1 = fig.add_subplot(gs[0, 0])
            vmin = max(arr.min(), arr.max() - dyn_range)
            AZ, EL = np.meshgrid(az, el)
            im = ax1.pcolormesh(AZ, EL, arr, shading='gouraud',
                                cmap='jet', vmin=vmin,
                                vmax=arr.max())
            ax1.set_xlim(az[0], az[-1])
            ax1.set_ylim(el[-1], el[0])
            fig.colorbar(im, ax=ax1, shrink=0.8, label='dBi')
            ax1.set_xlabel('Az (deg)', fontsize=9)
            ax1.set_ylabel('El (deg)', fontsize=9)
            ax1.set_title('Heatmap', fontsize=10)
            ax1.plot(s['peak_az'], s['peak_el'], 'w+',
                     markersize=12, markeredgewidth=2)

            # Az cut
            ax2 = fig.add_subplot(gs[0, 1])
            az_cut = arr[s['el0'], :]
            ax2.plot(az, az_cut, 'b-', lw=1.2, label='el=0')
            ax2.axhline(y=az_cut.max() - 3, color='r',
                        ls='--', alpha=0.7, label='-3 dB')
            for ea in extra_cuts:
                dists = [abs(e - ea) for e in el]
                eidx = dists.index(min(dists))
                ax2.plot(az, arr[eidx, :], '--', lw=0.9,
                         alpha=0.7,
                         label=f'el={el[eidx]:.0f}')
            ax2.set_xlabel('Az (deg)', fontsize=9)
            ax2.set_ylabel('Gain (dBi)', fontsize=9)
            ax2.set_title('Azimuth Cuts', fontsize=10)
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=7)
            ax2.set_xlim(az[0], az[-1])

            # El cut
            ax3 = fig.add_subplot(gs[1, 0])
            el_cut = arr[:, s['az0']]
            ax3.plot(el, el_cut, 'r-', lw=1.2, label='az=0')
            ax3.axhline(y=el_cut.max() - 3, color='b',
                        ls='--', alpha=0.7, label='-3 dB')
            for ea in extra_cuts:
                dists = [abs(a - ea) for a in az]
                aidx = dists.index(min(dists))
                ax3.plot(el, arr[:, aidx], '--', lw=0.9,
                         alpha=0.7,
                         label=f'az={az[aidx]:.0f}')
            ax3.set_xlabel('El (deg)', fontsize=9)
            ax3.set_ylabel('Gain (dBi)', fontsize=9)
            ax3.set_title('Elevation Cuts', fontsize=10)
            ax3.grid(True, alpha=0.3)
            ax3.legend(fontsize=7)
            ax3.set_xlim(el[0], el[-1])

            # Stats box
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.axis('off')
            stat_lines = [
                f"Peak Gain:  {s['peak_gain']:.2f} dBi",
                f"Boresight:  {s['bore_gain']:.2f} dBi",
                f"Peak at:    az={s['peak_az']:.0f}  "
                f"el={s['peak_el']:.0f}",
                f"Az BW:      ~{s['az_bw']}",
                f"El BW:      ~{s['el_bw']}",
            ]
            if s['ftb'] is not None:
                stat_lines.append(
                    f"F/B Ratio:  {s['ftb']:.1f} dB")
            if s['first_sll']:
                stat_lines.append(
                    f"1st SLL:    -{s['first_sll']['relative']:.1f}"
                    f" dB @ {s['first_sll']['angle']:.0f}")
            ax4.text(0.08, 0.78, '\n'.join(stat_lines),
                     transform=ax4.transAxes, fontsize=10,
                     va='top', fontfamily='monospace',
                     bbox=dict(boxstyle='round',
                               facecolor='#f0f0f0', alpha=0.8))

            plt.tight_layout()
            _add_axes_classification(ax1, report_cfg)
            _add_axes_classification(ax2, report_cfg)
            _add_axes_classification(ax3, report_cfg)
            _add_axes_classification(ax4, report_cfg)
            img = _save_figure(plt, fig, heatmap_dir,
                               f"heatmap_{freq_safe}.png",
                               tex_dir=tex_dir)

            lines.append(r"\begin{figure}[H]")
            lines.append(r"\centering")
            lines.append(r"\includegraphics[width=0.90"
                         r"\textwidth]{" + img + "}")
            lines.append(_cls_caption(
                "Heatmap and principal cuts at " + section_label + ".",
                fig_cls))
            lines.append(r"\end{figure}")
            lines.append("")

        # ── Polar plot ───────────────────────────────
        if report_cfg.get("per_freq_polar"):
            lines.append(r"\newpage")
            az = s['az']; el = s['el']; arr = s['arr']

            fig = plt.figure(figsize=(12, 5))
            fig.suptitle(f'Polar @ {freq_str}',
                         fontsize=13, fontweight='bold')
            ax1 = fig.add_subplot(121, projection='polar')
            ax2 = fig.add_subplot(122, projection='polar')

            az_cut = arr[s['el0'], :]
            el_cut = arr[:, s['az0']]
            peak = float(arr.max())
            floor = peak - polar_range

            az_plot = np.clip(az_cut, floor, peak) - floor
            ax1.plot(np.radians(az), az_plot, 'b-', lw=1.5)
            ax1.fill(np.radians(az), az_plot,
                     alpha=0.15, color='blue')
            ax1.set_title('Azimuth (el=0)', pad=20, fontsize=11)
            ax1.set_theta_zero_location('N')
            ax1.set_theta_direction(-1)
            r_vals = np.linspace(0, peak - floor, 5)
            ax1.set_rticks(r_vals)
            ax1.set_yticklabels(
                [f"{v + floor:.0f}" for v in r_vals], fontsize=7)

            el_plot = np.clip(el_cut, floor, peak) - floor
            ax2.plot(np.radians(el), el_plot, 'r-', lw=1.5)
            ax2.fill(np.radians(el), el_plot,
                     alpha=0.15, color='red')
            ax2.set_title('Elevation (az=0)', pad=20, fontsize=11)
            ax2.set_theta_zero_location('N')
            ax2.set_theta_direction(-1)
            ax2.set_rticks(r_vals)
            ax2.set_yticklabels(
                [f"{v + floor:.0f}" for v in r_vals], fontsize=7)

            thresh = peak - 3 - floor
            if thresh > 0:
                ring = np.linspace(0, 2 * np.pi, 200)
                ax1.plot(ring, [thresh]*200, 'g--', lw=0.8,
                         alpha=0.6, label='-3 dB')
                ax2.plot(ring, [thresh]*200, 'g--', lw=0.8,
                         alpha=0.6, label='-3 dB')
                ax1.legend(fontsize=7, loc='lower right')
                ax2.legend(fontsize=7, loc='lower right')

            plt.tight_layout()
            _add_axes_classification(ax1, report_cfg)
            _add_axes_classification(ax2, report_cfg)
            img = _save_figure(plt, fig, polar_dir,
                               f"polar_{freq_safe}.png",
                               tex_dir=tex_dir)

            lines.append(r"\begin{figure}[H]")
            lines.append(r"\centering")
            lines.append(r"\includegraphics[width=0.75"
                         r"\textwidth]{" + img + "}")
            lines.append(_cls_caption(
                "Polar patterns at " + section_label + ".",
                fig_cls))
            lines.append(r"\end{figure}")
            lines.append("")

        # ── 3-D surface ──────────────────────────────
        if report_cfg.get("per_freq_3d"):
            lines.append(r"\newpage")
            az = s['az']; el = s['el']; arr = s['arr']
            step = max(1, len(az) // 90)
            az_sub = az[::step]; el_sub = el[::step]
            arr_sub = arr[::step, ::step]
            AZ, EL = np.meshgrid(az_sub, el_sub)
            vmin = max(arr_sub.min(), arr_sub.max() - dyn_range)
            arr_c = np.clip(arr_sub, vmin, arr_sub.max())

            fig = plt.figure(figsize=(8, 5.5))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(AZ, EL, arr_c, cmap='jet',
                            alpha=0.85, rstride=1, cstride=1)
            ax.set_xlabel('Az (deg)')
            ax.set_ylabel('El (deg)')
            ax.set_zlabel('Gain (dBi)')
            ax.set_title(f'3-D Surface @ {freq_str}',
                         fontsize=13, fontweight='bold')
            plt.tight_layout()
            _add_axes_classification(ax, report_cfg)
            img = _save_figure(plt, fig, surface_dir,
                               f"3d_{freq_safe}.png",
                               tex_dir=tex_dir)

            lines.append(r"\begin{figure}[H]")
            lines.append(r"\centering")
            lines.append(r"\includegraphics[width=0.52"
                         r"\textwidth]{" + img + "}")
            lines.append(_cls_caption(
                "3-D surface at " + section_label + ".",
                fig_cls))
            lines.append(r"\end{figure}")
            lines.append("")

        # ── Detailed analysis text ───────────────────
        if (report_cfg.get("per_freq_stats")
                or report_cfg.get("per_freq_detailed")
                or report_cfg.get("per_freq_sidelobe")):

            lines.append(r"\subsection*{Detailed Analysis "
                         r"--- " + section_label + "}")
            lines.append(r"\begin{verbatim}")

            if report_cfg.get("per_freq_stats"):
                lines.append("PATTERN STATISTICS")
                lines.append("-" * 50)
                lines.append(f"  Peak Gain ............. "
                             f"{s['peak_gain']:.2f} dBi")
                lines.append(f"  Boresight Gain ........ "
                             f"{s['bore_gain']:.2f} dBi")
                lines.append(f"  Peak Location ......... "
                             f"az={s['peak_az']:.0f} "
                             f"el={s['peak_el']:.0f}")
                lines.append(f"  Min Gain .............. "
                             f"{s['min_gain']:.2f} dBi")
                lines.append(f"  Mean Gain ............. "
                             f"{s['avg_gain']:.2f} dBi")
                lines.append(f"  Dynamic Range ......... "
                             f"{s['dynamic_range']:.1f} dB")
                _is_omni = str(report_cfg.get('_antenna_type', '')).lower() == 'omni'
                _az_bw_lbl = "Az Beamwidth" if _is_omni else "Az 3 dB Beamwidth"
                lines.append(f"  {_az_bw_lbl} ..... "
                             f"~{s['az_bw']} deg")
                lines.append(f"  El 3 dB Beamwidth ..... "
                             f"~{s['el_bw']} deg")
                if s['ftb'] is not None:
                    lines.append(f"  Front-to-Back ......... "
                                 f"{s['ftb']:.1f} dB")
                lines.append("")

            if report_cfg.get("per_freq_sidelobe"):
                lines.append("SIDELOBE ANALYSIS")
                lines.append("-" * 50)
                if s['first_sll']:
                    sl = s['first_sll']
                    lines.append(f"  Az 1st Sidelobe ....... "
                                 f"{sl['level']:.1f} dBi "
                                 f"@ {sl['angle']:.0f} deg")
                    lines.append(f"  Az SLL below peak ..... "
                                 f"-{sl['relative']:.1f} dB")
                else:
                    lines.append("  Az 1st Sidelobe ....... "
                                 "not detected")
                if s.get('el_first_sll'):
                    sl = s['el_first_sll']
                    lines.append(f"  El 1st Sidelobe ....... "
                                 f"{sl['level']:.1f} dBi "
                                 f"@ {sl['angle']:.0f} deg")
                    lines.append(f"  El SLL below peak ..... "
                                 f"-{sl['relative']:.1f} dB")
                else:
                    lines.append("  El 1st Sidelobe ....... "
                                 "not detected")
                lines.append("")

            if report_cfg.get("per_freq_detailed"):
                lines.append("HEMISPHERIC ANALYSIS")
                lines.append("-" * 50)
                if s['front_avg'] is not None:
                    lines.append(f"  Front hemisphere avg .. "
                                 f"{s['front_avg']:.2f} dBi")
                if s['back_avg'] is not None:
                    lines.append(f"  Back hemisphere avg ... "
                                 f"{s['back_avg']:.2f} dBi")
                if (s['front_avg'] is not None
                        and s['back_avg'] is not None):
                    diff = s['front_avg'] - s['back_avg']
                    lines.append(f"  F/B avg difference .... "
                                 f"{diff:.1f} dB")
                lines.append("")
                lines.append("SYMMETRY")
                lines.append("-" * 50)
                lines.append(f"  Az RMS asymmetry ...... "
                             f"{s['asym_az']:.2f} dB")
                lines.append(f"  El RMS asymmetry ...... "
                             f"{s['asym_el']:.2f} dB")
                lines.append("")
                lines.append("COVERAGE")
                lines.append("-" * 50)
                total = s['total_pts']
                lines.append(
                    f"  >= 0 dBi .............. "
                    f"{s['above_0']}/{total} "
                    f"({100*s['above_0']/total:.1f}%)")
                lines.append(
                    f"  Within 3 dB of peak .. "
                    f"{s['above_m3']}/{total} "
                    f"({100*s['above_m3']/total:.1f}%)")
                lines.append(
                    f"  Within 10 dB of peak . "
                    f"{s['above_m10']}/{total} "
                    f"({100*s['above_m10']/total:.1f}%)")

            lines.append(r"\end{verbatim}")
            lines.append(r"\newpage")
            lines.append("")

    # ==================================================
    #  CROSS-POL PAGES
    # ==================================================
    if xpol_summaries:
        lines.append(r"\section{Cross-Polarisation}")
        lines.append("")
        lines.append(r"\begin{longtable}{r r r}")
        lines.append(r"\toprule")
        lines.append(r"\textbf{Freq (MHz)} & "
                     r"\textbf{Peak XP (dBi)} & "
                     r"\textbf{Bore XP (dBi)} \\")
        lines.append(r"\midrule")
        for xs in xpol_summaries:
            freq_s = (f"{xs['freq']:.1f}"
                      if xs['freq'] else "?")
            lines.append(f"  {freq_s} & "
                         f"{xs['peak_gain']:.1f} & "
                         f"{xs['bore_gain']:.1f} \\\\")
        lines.append(r"\bottomrule")
        lines.append(r"\end{longtable}")

        for xs in xpol_summaries:
            az = xs['az']; el = xs['el']; arr = xs['arr']
            freq_s = (f"{xs['freq']:.2f} MHz"
                      if xs['freq'] else "?")
            freq_safe = freq_s.replace(' ', '_').replace('.', 'p')

            fig, ax = plt.subplots(figsize=(10, 7))
            vmin = max(arr.min(), arr.max() - dyn_range)
            AZ, EL = np.meshgrid(az, el)
            im = ax.pcolormesh(AZ, EL, arr, shading='gouraud',
                               cmap='jet', vmin=vmin,
                               vmax=arr.max())
            ax.set_xlim(az[0], az[-1])
            ax.set_ylim(el[-1], el[0])
            fig.colorbar(im, ax=ax, shrink=0.8, label='dBi')
            ax.set_xlabel('Az (deg)')
            ax.set_ylabel('El (deg)')
            ax.set_title(f'Cross-Pol @ {freq_s}')
            plt.tight_layout()
            _add_axes_classification(ax, report_cfg)
            img = _save_figure(plt, fig, xpol_dir,
                               f"xpol_{freq_safe}.png",
                               tex_dir=tex_dir)

            lines.append(r"\begin{figure}[H]")
            lines.append(r"\centering")
            lines.append(r"\includegraphics[width=0.76"
                         r"\textwidth]{" + img + "}")
            lines.append(_cls_caption(
                "Cross-pol heatmap at " + _tex_escape(freq_s) + ".",
                fig_cls))
            lines.append(r"\end{figure}")
            lines.append("")

    # ── Configuration page ────────────────────────────
    if report_cfg.get("generation_config", True):
        _render_latex_config_page(lines, input_dir, report_cfg)

    # ── End document ─────────────────────────────────
    lines.append(r"\end{document}")

    # ── Write .tex file ──────────────────────────────
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    logger.info("LaTeX report saved: %s", output_path)
    logger.info("  Images saved to: %s/", images_root)
    logger.info("  Compile with: pdflatex %s",
                os.path.basename(output_path))
    return output_path
