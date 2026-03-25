"""
Batch generation from JSON recipe files.

A recipe defines one or more antenna configurations to generate
in sequence with no interactive prompts. Enables scripting from
external tools, CI/CD pipelines, and overnight batch runs.

Recipe format (JSON):
{
  "description": "Overnight LPDA sweep",
  "configs": [
    {
      "antenna_type": "LPDA",
      "max_gain_dbi": 7.0,
      "az_beamwidth_deg": 65,
      "el_beamwidth_deg": 70,
      "f_min_mhz": 30,
      "f_max_mhz": 300,
      "n_slices": 25,
      "freq_spacing": "log",
      "ftb_ratio_db": 15,
      "output_dir": "./batch_lpda"
    },
    {
      "antenna_type": "Omni",
      "max_gain_dbi": 2.0,
      "el_beamwidth_deg": 80,
      "f_min_mhz": 100,
      "f_max_mhz": 500,
      "n_slices": 10,
      "output_dir": "./batch_omni"
    }
  ]
}
"""

import glob
import json
import logging
import os
import time
import threading
from typing import IO, Callable
from copy import deepcopy

from config import (
    DEFAULT_CONFIG, generate_frequencies,
)
from core.engine import run_generation
from antennas import get_antenna

logger = logging.getLogger(__name__)


def generate_batch_images(
    output_dir: str,
    writer: IO[str] | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> int:
    """Generate all plot images for a batch output directory.

    Scans *output_dir* for ``*_copol.csv`` files and produces
    heatmap, cuts, polar, and 3D-surface PNGs in subfolders,
    plus multi-file trend plots (gain-vs-freq, bw-vs-freq,
    overlay cuts) in a ``graphs/`` subfolder.

    Args:
        output_dir: Directory containing generated CSV files.
        writer: File-like object for progress output.
        progress_callback: Optional callable invoked with a single
            string for each plot step (per-file and trend plots).

    Returns:
        Number of images generated.
    """
    import sys
    out = writer or sys.stdout

    all_csv = sorted([
        *glob.glob(os.path.join(output_dir, "*.csv")),
        *glob.glob(os.path.join(output_dir, "*.dat"))
    ])
    if not all_csv:
        logger.warning("No CSV files found in %s — skipping images",
                       output_dir)
        return 0

    # Only generate per-file plots for co-pol CSVs; cross-pol
    # patterns are handled by the report system separately.
    csv_files = [f for f in all_csv if '_xpol' not in
                 os.path.basename(f).lower()]

    try:
        from graphing.plots import (
            graph_heatmap, graph_cuts, graph_polar, graph_3d_surface,
        )
        from graphing.multi_plots import (
            graph_gain_vs_freq, graph_bw_vs_freq, graph_overlay_cuts,
        )
    except Exception as exc:
        logger.warning("Plot dependencies unavailable (%s) — "
                       "skipping image generation", exc)
        return 0

    graphs_dir = os.path.join(output_dir, "graphs")
    sub_dirs = {
        "heatmaps": os.path.join(graphs_dir, "heatmaps"),
        "cuts":     os.path.join(graphs_dir, "cuts"),
        "polar":    os.path.join(graphs_dir, "polar"),
        "3d":       os.path.join(graphs_dir, "3d_surface"),
    }
    for d in sub_dirs.values():
        os.makedirs(d, exist_ok=True)

    count = 0
    n_files = len(csv_files)
    for i, fp in enumerate(csv_files):
        base = os.path.splitext(os.path.basename(fp))[0]
        msg = f"  [{i+1}/{n_files}] Plotting {base}..."
        out.write(f"\r{msg}   ")
        if hasattr(out, 'flush'):
            out.flush()
        if progress_callback is not None:
            progress_callback(msg)
        try:
            graph_heatmap(fp, os.path.join(
                sub_dirs["heatmaps"], f"{base}_heatmap.png"))
            graph_cuts(fp, os.path.join(
                sub_dirs["cuts"], f"{base}_cuts.png"))
            graph_polar(fp, os.path.join(
                sub_dirs["polar"], f"{base}_polar.png"))
            graph_3d_surface(fp, os.path.join(
                sub_dirs["3d"], f"{base}_3d.png"))
            count += 4
        except Exception as exc:
            logger.warning("Plot error for %s: %s", base, exc)

    # Multi-file trend plots (csv_files is already copol-only)
    if len(csv_files) > 1:
        msg = f"  Generating trend plots..."
        if progress_callback is not None:
            progress_callback(msg)
        try:
            graph_gain_vs_freq(
                csv_files, os.path.join(graphs_dir, "gain_vs_freq.png"))
            graph_bw_vs_freq(
                csv_files, os.path.join(graphs_dir, "bw_vs_freq.png"))
            graph_overlay_cuts(
                csv_files, os.path.join(graphs_dir, "overlay_cuts.png"))
            count += 3
        except Exception as exc:
            logger.warning("Multi-plot error: %s", exc)

    out.write(f"\r  {count} images saved to {graphs_dir}/\n")
    if hasattr(out, 'flush'):
        out.flush()
    logger.info("%d images saved to %s/", count, graphs_dir)
    return count


def load_recipe(filepath: str) -> list[dict]:
    """Load a batch recipe from a JSON file.

    Each config in the recipe is merged with ``DEFAULT_CONFIG``
    so all keys have sensible values.

    Args:
        filepath: Path to the JSON recipe file.

    Returns:
        List of fully-merged configuration dicts.
    """
    with open(filepath, 'r') as f:
        recipe = json.load(f)

    configs = recipe.get("configs", [recipe])
    if not isinstance(configs, list):
        configs = [configs]

    merged = []
    for i, cfg_partial in enumerate(configs):
        cfg = deepcopy(DEFAULT_CONFIG)
        for key, val in cfg_partial.items():
            if key == "features" and isinstance(val, dict):
                for fkey, fval in val.items():
                    if fkey in cfg["features"]:
                        if isinstance(fval, dict):
                            cfg["features"][fkey].update(fval)
                        else:
                            cfg["features"][fkey] = fval
                    else:
                        cfg["features"][fkey] = fval
            else:
                cfg[key] = val

        # Merge antenna-specific defaults
        try:
            antenna = get_antenna(cfg["antenna_type"])
            for k, v in antenna.default_params().items():
                if k not in cfg:
                    cfg[k] = v
        except KeyError:
            pass

        # Handle omni special case
        if cfg["antenna_type"] == "Omni":
            cfg["az_beamwidth_deg"] = 360.0

        merged.append(cfg)

    desc = recipe.get("description", "Batch run")
    logger.info("Recipe: %s", desc)
    logger.info("Configs: %d", len(merged))
    return merged


def run_batch(
    recipe_path: str,
    dry_run: bool = False,
    generate_images: bool = False,
    generate_report: bool = False,
    report_format: str = "PDF",
    report_preset: str | None = None,
    output_base: str | None = None,
    writer: IO[str] | None = None,
    progress_callback: Callable[[str], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> list[str]:
    """Execute a batch recipe.

    Args:
        recipe_path: Path to JSON recipe file.
        dry_run: If ``True``, validate configs but don't generate.
        generate_images: If ``True``, generate plot images for each
            completed job (heatmaps, cuts, polar, 3D surface, and
            multi-file trend plots).
        generate_report: If ``True`` (and ``generate_images`` is also
            ``True``), generate a PDF report for each completed job.
        report_format: The output format for the report ("PDF" or "PPTX").
            Defaults to "PDF".
        report_preset: Report section preset name (``"default"``,
            ``"full"``, ``"minimal"``, ``"quick"``).  ``None`` uses
            ``"default"``.
        output_base: Optional base directory for all batch outputs.
            Each job's ``output_dir`` becomes a subfolder under this
            path. If ``None``, jobs use their ``output_dir`` as-is.
        writer: File-like object for progress output.
        progress_callback: Optional callable invoked with a single
            string argument at each progress milestone (job start,
            job completion, image generation).  Useful for pushing
            live updates to a GUI.
        cancel_event: Optional ``threading.Event``.  When set, the
            batch loop aborts before the next job.

    Returns:
        List of output directories created.
    """
    configs = load_recipe(recipe_path)

    def _emit(msg: str) -> None:
        """Send a progress message to both logger and callback."""
        logger.info(msg)
        if progress_callback is not None:
            progress_callback(msg)

    # Rebase output directories if a base directory is specified
    if output_base:
        for cfg in configs:
            original = cfg["output_dir"]
            # Use the last component of the original path as subfolder
            leaf = os.path.basename(original.rstrip("/\\")) or "job"
            cfg["output_dir"] = os.path.join(output_base, leaf)

    _emit(f"Loaded recipe: {len(configs)} jobs")

    outputs = []
    total_start = time.time()

    for i, cfg in enumerate(configs):
        # ── Check for cancellation ────────────────────────
        if cancel_event is not None and cancel_event.is_set():
            _emit(f"\nCANCELLED after {len(outputs)}/{len(configs)} jobs")
            break

        job_num = i + 1
        header = (
            f"\n{'-' * 50}\n"
            f"Job {job_num}/{len(configs)}: {cfg['antenna_type']}\n"
            f"  Gain: {cfg['max_gain_dbi']} dBi  |  "
            f"Freq: {cfg['f_min_mhz']}-{cfg['f_max_mhz']} MHz  |  "
            f"{cfg['n_slices']} slices\n"
            f"  Output: {cfg['output_dir']}"
        )
        _emit(header)

        if dry_run:
            # Just validate
            try:
                antenna = get_antenna(cfg["antenna_type"])
                warnings = antenna.validate_config(cfg)
                if warnings:
                    for w in warnings:
                        _emit(f"  WARNING: {w}")
                else:
                    _emit("  [OK] Config OK")
                freqs = generate_frequencies(
                    cfg["f_min_mhz"], cfg["f_max_mhz"],
                    cfg["n_slices"],
                    cfg.get("freq_spacing", "linear")
                )
                _emit(f"  Would generate {len(freqs)} frequency slices")
            except Exception as e:
                _emit(f"  [FAIL] ERROR: {e}")
            continue

        try:
            job_start = time.time()
            freqs = generate_frequencies(
                cfg["f_min_mhz"], cfg["f_max_mhz"],
                cfg["n_slices"],
                cfg.get("freq_spacing", "linear")
            )
            _emit(f"  Generating {len(freqs)} freq slices...")
            run_generation(cfg, freqs, writer=writer)
            job_elapsed = time.time() - job_start
            outputs.append(cfg["output_dir"])
            _emit(f"  [OK] Job {job_num} done ({job_elapsed:.1f}s)")

            if generate_images:
                _emit(f"  Generating images for job {job_num}...")
                try:
                    n_imgs = generate_batch_images(
                        cfg["output_dir"], writer=writer,
                        progress_callback=progress_callback)
                    _emit(f"  [OK] {n_imgs} images generated")
                except Exception as img_err:
                    _emit(f"  WARNING: Image generation failed: {img_err}")

            if generate_report and generate_images:
                _emit(f"  Generating {report_format} report for job {job_num}...")
                try:
                    if report_format.upper() == "PPTX":
                        from reporting.pptx_report import generate_pptx_report
                        # Note: PPTX report doesn't use presets yet
                        pptx_path = generate_pptx_report(cfg["output_dir"])
                        if pptx_path:
                            _emit(f"  [OK] Report: {pptx_path}")
                        else:
                            _emit("  WARNING: Report generation returned None")
                    else:  # Default to PDF
                        from reporting.report import (
                            generate_report as _gen_report, PRESETS,
                        )
                        preset_name = report_preset or "default"
                        preset_fn = PRESETS.get(
                            preset_name, PRESETS["default"])[1]
                        rcfg = preset_fn()
                        pdf_path = _gen_report(
                            cfg["output_dir"], report_cfg=rcfg)
                        if pdf_path:
                            _emit(f"  [OK] Report: {pdf_path}")
                        else:
                            _emit("  WARNING: Report generation returned None")
                except Exception as rpt_err:
                    _emit(f"  WARNING: Report generation failed: {rpt_err}")
        except Exception as e:
            _emit(f"  [FAIL] ERROR in job {job_num}: {e}")
            continue

    elapsed = time.time() - total_start
    summary = (
        f"\n{'=' * 50}\n"
        f"BATCH COMPLETE: {len(outputs)}/{len(configs)} jobs "
        f"({elapsed:.1f}s)\n"
        f"{'=' * 50}"
    )
    _emit(summary)
    return outputs


def create_sample_recipe(output_path: str = "./sample_recipe.json") -> str:
    """Write a sample recipe JSON file as a starting point.

    Args:
        output_path: Destination file path.

    Returns:
        The written file path.
    """
    sample = {
        "description": "Sample batch recipe",
        "configs": [
            {
                "antenna_type": "LPDA",
                "max_gain_dbi": 7.0,
                "az_beamwidth_deg": 65.0,
                "el_beamwidth_deg": 70.0,
                "f_min_mhz": 30.0,
                "f_max_mhz": 300.0,
                "n_slices": 10,
                "freq_spacing": "log",
                "ftb_ratio_db": 15.0,
                "polarization": "vertical",
                "output_dir": "./batch_lpda"
            },
            {
                "antenna_type": "Omni",
                "max_gain_dbi": 2.15,
                "el_beamwidth_deg": 80.0,
                "f_min_mhz": 100.0,
                "f_max_mhz": 1000.0,
                "n_slices": 20,
                "freq_spacing": "linear",
                "polarization": "vertical",
                "output_dir": "./batch_omni"
            }
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(sample, f, indent=2)
    logger.info("Sample recipe saved: %s", output_path)
    return output_path
