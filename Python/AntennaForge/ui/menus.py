"""
Interactive menu system.

Orchestrates prompts, feature config, and calls into the engine,
analysis, and graphing modules.
"""

import glob
import os
from copy import deepcopy

from config import (
    DEFAULT_CONFIG, load_config, save_config,
    generate_frequencies, VERSION,
)
from core.engine import run_generation
from core.pattern_math import (
    compute_freq_dependent_bw,
)
from core.io import make_graph_output_dir
from antennas import available_names, get_antenna
from analysis.analyzer import (
    analyze_single, compare_patterns,
)
from graphing.plots import (
    graph_heatmap, graph_cuts, graph_polar, graph_3d_surface,
)
from graphing.multi_plots import (
    graph_gain_vs_freq, graph_bw_vs_freq, graph_overlay_cuts,
)
from graphing import check_plot_deps
from ui.prompts import (
    prompt_choice, prompt_float, prompt_int, prompt_yn,
    prompt_file, prompt_dir_files, prompt_dir, prompt_save_file,
    pick_file, pick_directory, GoBack,
)
from ui.feature_config import (
    display_feature_status, configure_feature,
    _configure_bw_decay,
    _select_bw_decay_mode,
)


# ===================================================================
#  MENU 1: GENERATE PATTERNS
# ===================================================================

# Section labels for the progress breadcrumb
_GEN_SECTIONS = [
    "Core", "Beamwidth", "Frequency", "Angular",
    "Polarization", "Features", "Output", "Summary",
]

def _gen_breadcrumb(step_idx: int) -> None:
    """Print a breadcrumb showing Generate flow position."""
    parts = []
    for i, name in enumerate(_GEN_SECTIONS):
        if i < step_idx:
            parts.append(f"  {name} ✓")
        elif i == step_idx:
            parts.append(f" [{name}]")
        else:
            parts.append(f"  {name}")
    print("  " + " → ".join(parts))
    print("  (type 'b' at any prompt to go back)\n")


def menu_generate() -> None:
    """Interactive antenna pattern generation wizard."""
    print("\n" + "=" * 60)
    print("   GENERATE ANTENNA PATTERNS")
    print("=" * 60)

    cfg = deepcopy(DEFAULT_CONFIG)
    if prompt_yn("Load settings from JSON file?",
                 default=False):
        path = prompt_file("  JSON config file",
                           must_exist=True,
                           pattern="*.json")
        if path and os.path.exists(path):
            cfg = load_config(path)
            print(f"  Loaded: {path}")
        else:
            print("  File not found, using defaults.")

    # Track antenna object (set in step 0, used later)
    antenna = [None]

    # ── Step functions ────────────────────────────────────
    # Each returns nothing and mutates cfg.
    # Raising GoBack causes the loop to step back.

    def step_core():
        """Section 0: Core — antenna type, gain, antenna-specific."""
        print("\n--- CORE PARAMETERS ---")
        _gen_breadcrumb(0)
        cfg["antenna_type"] = prompt_choice(
            "Antenna type:", available_names(),
            default=cfg["antenna_type"],
            allow_back=True
        )
        antenna[0] = get_antenna(cfg["antenna_type"])
        cfg["max_gain_dbi"] = prompt_float(
            "Peak gain (dBi)", default=cfg["max_gain_dbi"],
            allow_back=True
        )
        # Antenna-specific config (e.g. FTB)
        # GoBack inside configure() will propagate up
        antenna[0].configure(cfg)

    def step_beamwidth():
        """Section 1: Beamwidth decay mode + values."""
        print("\n--- BEAMWIDTH CONFIGURATION ---")
        _gen_breadcrumb(1)
        print("  Select how beamwidth changes across the band,")
        print("  then configure the parameters for that mode.")
        feat_az = cfg["features"]["freq_dependent_bw_az"]
        feat_el = cfg["features"]["freq_dependent_bw_el"]

        if antenna[0].has_az_pattern:
            feat_az["enabled"] = True
            _select_bw_decay_mode(feat_az, "Az")

        feat_el["enabled"] = True
        _select_bw_decay_mode(feat_el, "El")

        if antenna[0].has_az_pattern:
            _configure_bw_decay(cfg, feat_az, "Az",
                                ask_mode=False)
        _configure_bw_decay(cfg, feat_el, "El",
                            ask_mode=False)

    def step_frequency():
        """Section 2: Frequency range."""
        print("\n--- FREQUENCY RANGE ---")
        _gen_breadcrumb(2)
        cfg["f_min_mhz"] = prompt_float(
            "Start frequency (MHz)",
            default=cfg["f_min_mhz"], min_val=0.001,
            allow_back=True
        )
        cfg["f_max_mhz"] = prompt_float(
            "End frequency (MHz)",
            default=cfg["f_max_mhz"],
            min_val=cfg["f_min_mhz"],
            allow_back=True
        )
        cfg["n_slices"] = prompt_int(
            "Number of frequency slices",
            default=cfg["n_slices"],
            min_val=1, max_val=1000,
            allow_back=True
        )
        cfg["freq_spacing"] = prompt_choice(
            "Spacing:", ["linear", "log"],
            default=cfg["freq_spacing"],
            allow_back=True
        )
        ref_def = round(
            (cfg["f_min_mhz"] + cfg["f_max_mhz"]) / 2.0, 2
        )
        print("\n  The reference frequency is the frequency at")
        print("  which the specified beamwidth values are exact.")
        print("  At other frequencies, beamwidth will scale")
        print("  according to the selected decay mode.")
        print(f"  (Typically the center or design frequency)")
        cfg["ref_frequency_mhz"] = prompt_float(
            "Reference freq for beamwidth spec (MHz)",
            default=ref_def,
            min_val=cfg["f_min_mhz"],
            max_val=cfg["f_max_mhz"],
            allow_back=True
        )

    def step_angular():
        """Section 3: Angular resolution."""
        print("\n--- ANGULAR RESOLUTION ---")
        _gen_breadcrumb(3)
        print("  Fine resolution = better quality but slower.")
        print("  Coarse resolution = fast iteration.")
        cfg["az_step_deg"] = prompt_float(
            "Azimuth step size (deg)",
            default=cfg.get("az_step_deg", 1.0),
            min_val=0.1, max_val=5.0,
            allow_back=True
        )
        cfg["el_step_deg"] = prompt_float(
            "Elevation step size (deg)",
            default=cfg.get("el_step_deg", 1.0),
            min_val=0.1, max_val=5.0,
            allow_back=True
        )
        n_az = int(360 / cfg["az_step_deg"]) + 1
        n_el = int(180 / cfg["el_step_deg"]) + 1
        print(f"  Grid: {n_el} el x {n_az} az "
              f"= {n_el * n_az:,} points per slice")

    def step_polarization():
        """Section 4: Polarization + noise."""
        print("\n--- POLARIZATION ---")
        _gen_breadcrumb(4)
        cfg["polarization"] = prompt_choice(
            "Polarization:",
            ["vertical", "horizontal", "custom"],
            default=cfg["polarization"],
            allow_back=True
        )
        if cfg["polarization"] == "custom":
            cfg["pol_angle_deg"] = prompt_float(
                "Angle (0=V, 90=H)",
                default=cfg["pol_angle_deg"],
                allow_back=True
            )
        cfg["noise_range_db"] = prompt_float(
            "Random noise (dB, 0=none)",
            default=cfg["noise_range_db"], min_val=0,
            allow_back=True
        )

    def step_features():
        """Section 5: Feature toggles."""
        print("\n--- FEATURE CONFIGURATION ---")
        _gen_breadcrumb(5)
        display_feature_status(cfg)

        while True:
            action = prompt_choice(
                "Feature menu:",
                ["Toggle/configure a feature",
                 "Enable all", "Disable all",
                 "Continue to output"],
                default="Continue to output",
                allow_back=True
            )
            if action == "Continue to output":
                break
            elif action == "Enable all":
                for f in cfg["features"].values():
                    f["enabled"] = True
                display_feature_status(cfg)
            elif action == "Disable all":
                for f in cfg["features"].values():
                    f["enabled"] = False
                display_feature_status(cfg)
            else:
                feature_keys = list(cfg["features"].keys())
                print("\n  Select feature:")
                for i, k in enumerate(feature_keys, 1):
                    s = ("ON" if cfg["features"][k]["enabled"]
                         else "OFF")
                    print(f"  [{i}] {k} ({s})")
                while True:
                    raw = input("> ").strip()
                    try:
                        idx = int(raw) - 1
                        if 0 <= idx < len(feature_keys):
                            configure_feature(
                                cfg, feature_keys[idx]
                            )
                            break
                    except ValueError:
                        pass
                    print(f"  Enter 1-{len(feature_keys)}")
                display_feature_status(cfg)

    def step_output():
        """Section 6: Output directory + save config."""
        print("\n--- OUTPUT ---")
        _gen_breadcrumb(6)
        cfg["output_dir"] = prompt_dir(
            "Output directory",
            default=cfg["output_dir"]
        )
        if prompt_yn("Save settings to JSON?", default=False):
            save_path = prompt_save_file(
                "Save config as",
                default_name="antenna_config.json",
                ext=".json"
            )
            save_config(cfg, save_path)

    def step_summary():
        """Section 7: Summary + confirm + generate."""
        freqs = generate_frequencies(
            cfg["f_min_mhz"], cfg["f_max_mhz"],
            cfg["n_slices"], cfg["freq_spacing"]
        )
        ref_freq = cfg.get("ref_frequency_mhz")
        if not ref_freq:
            ref_freq = (
                cfg["f_min_mhz"] + cfg["f_max_mhz"]
            ) / 2

        ant = antenna[0]

        print("\n" + "=" * 60)
        print("   CONFIGURATION SUMMARY")
        _gen_breadcrumb(7)
        print("=" * 60)
        print(f"  Antenna type       : {cfg['antenna_type']}")
        print(f"  Max gain           : "
              f"{cfg['max_gain_dbi']} dBi")

        if ant.has_az_pattern:
            print(f"  Az 3dB Beamwidth @ ref : "
                  f"{cfg['az_beamwidth_deg']} deg")
        else:
            print(f"  Az Beamwidth           : "
                  f"360 deg (omni)")
        print(f"  El 3dB Beamwidth @ ref : "
              f"{cfg['el_beamwidth_deg']} deg")
        print(f"  Reference freq     : {ref_freq} MHz")
        print(f"  Freq range         : {cfg['f_min_mhz']} "
              f"- {cfg['f_max_mhz']} MHz "
              f"({cfg['n_slices']} slices, "
              f"{cfg['freq_spacing']})")

        feat_bw_el = cfg["features"].get(
            "freq_dependent_bw_el",
            cfg["features"].get("freq_dependent_bw", {})
        )
        feat_bw_az = cfg["features"].get(
            "freq_dependent_bw_az",
            cfg["features"].get("freq_dependent_bw", {})
        )
        if feat_bw_el.get("enabled") and len(freqs) > 1:
            bw_lo = compute_freq_dependent_bw(
                cfg["el_beamwidth_deg"],
                freqs[0], ref_freq, cfg, plane="el"
            )
            bw_hi = compute_freq_dependent_bw(
                cfg["el_beamwidth_deg"],
                freqs[-1], ref_freq, cfg, plane="el"
            )
            print(f"  El BW @ {freqs[0]:.1f} MHz "
                  f": {bw_lo:.1f} deg")
            print(f"  El BW @ {freqs[-1]:.1f} MHz"
                  f": {bw_hi:.1f} deg")
        if (ant.has_az_pattern
                and feat_bw_az.get("enabled")
                and len(freqs) > 1):
            bw_az_lo = compute_freq_dependent_bw(
                cfg["az_beamwidth_deg"],
                freqs[0], ref_freq, cfg, plane="az"
            )
            bw_az_hi = compute_freq_dependent_bw(
                cfg["az_beamwidth_deg"],
                freqs[-1], ref_freq, cfg, plane="az"
            )
            print(f"  Az BW @ {freqs[0]:.1f} MHz "
                  f": {bw_az_lo:.1f} deg")
            print(f"  Az BW @ {freqs[-1]:.1f} MHz"
                  f": {bw_az_hi:.1f} deg")

        freq_strs = [f'{f:.2f}' for f in freqs[:5]]
        freq_disp = ', '.join(freq_strs)
        if len(freqs) > 5:
            freq_disp += f" ... {freqs[-1]:.2f}"
        print(f"  Frequencies        : {freq_disp} MHz")
        if hasattr(ant, 'name') and ant.has_az_pattern:
            print(f"  Front-to-back      : "
                  f"{cfg.get('ftb_ratio_db', 'N/A')} dB")
        pol_str = cfg['polarization']
        if cfg['polarization'] == 'custom':
            pol_str += f" ({cfg['pol_angle_deg']} deg)"
        print(f"  Polarization       : {pol_str}")
        if cfg["noise_range_db"] > 0:
            noise_str = f"+/-{cfg['noise_range_db']} dB"
        else:
            noise_str = "None"
        print(f"  Noise              : {noise_str}")
        print(f"  Output             : {cfg['output_dir']}")
        az_s = cfg.get('az_step_deg', 1.0)
        el_s = cfg.get('el_step_deg', 1.0)
        n_az_pts = int(360 / az_s) + 1
        n_el_pts = int(180 / el_s) + 1
        print(f"  Grid               : "
              f"{n_el_pts} el x {n_az_pts} az "
              f"({el_s}° x {az_s}°)")
        print()
        print("  Features:")
        for key, feat in cfg["features"].items():
            m = "[x]" if feat["enabled"] else "[ ]"
            print(f"    {m} {feat['description']}")
        print("=" * 60)

        if not prompt_yn("\nGenerate?", default=True):
            print("Cancelled.")
            raise GoBack()   # back to Output
        run_generation(cfg, freqs)

    # ── Section-based state machine ───────────────────────
    steps = [
        step_core,        # 0
        step_beamwidth,   # 1
        step_frequency,   # 2
        step_angular,     # 3
        step_polarization,# 4
        step_features,    # 5
        step_output,      # 6
        step_summary,     # 7
    ]

    step_idx = 0
    while step_idx < len(steps):
        try:
            steps[step_idx]()
            step_idx += 1      # advance on success
        except GoBack:
            if step_idx > 0:
                step_idx -= 1  # go back one section
                print(f"\n  ↩  Back to "
                      f"{_GEN_SECTIONS[step_idx]}")
            else:
                print("\n  Already at the first section.")
                if prompt_yn("  Cancel generation?",
                             default=False):
                    return


# ===================================================================
#  MENU 2: ANALYZE PATTERNS
# ===================================================================

def menu_analyze() -> None:
    """Interactive pattern analysis menu."""
    print("\n" + "=" * 60)
    print("   PATTERN ANALYSIS")
    print("=" * 60)

    analysis_type = prompt_choice(
        "Analysis type:",
        ["Analyze single file",
         "Analyze multiple files (compare)",
         "Batch analyze directory"],
        default="Analyze single file"
    )

    results = []

    if analysis_type == "Analyze single file":
        fp = prompt_file("  CSV file path")
        r = analyze_single(fp)
        results.append(r)

    elif analysis_type == "Analyze multiple files (compare)":
        files = prompt_dir_files(
            "Select files to compare:"
        )
        if files:
            for f in files:
                r = analyze_single(f)
                results.append(r)
            compare_patterns(results)

    elif analysis_type == "Batch analyze directory":
        d = prompt_dir("Pattern directory", default=".")
        files = sorted([
            *glob.glob(os.path.join(d, "*.csv")),
            *glob.glob(os.path.join(d, "*.dat"))
        ])
        if not files:
            print(f"  No CSV or DAT files in {d}")
            return
        print(f"  Found {len(files)} CSV/DAT files")
        for f in files:
            r = analyze_single(f)
            results.append(r)
        compare_patterns(results)

    # Export option
    if prompt_yn("  Export analysis to CSV?",
                 default=False):
        import csv
        out = prompt_save_file(
            "Export analysis as",
            default_name="analysis.csv",
            ext=".csv"
        )
        if results:
            keys = results[0].keys()
            with open(out, 'w', newline='') as f:
                writer = csv.DictWriter(f,
                                        fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            print(f"  Analysis export saved to {out}")
        else:
            print("  No results to export.")


# ===================================================================
#  MENU 3: GRAPH PATTERNS
# ===================================================================

def menu_graph() -> None:
    """Interactive pattern graphing menu."""
    print("\n" + "=" * 60)
    print("   GRAPH PATTERNS")
    print("=" * 60)

    if not check_plot_deps():
        print("\n  Install dependencies with:")
        print("    pip install matplotlib numpy")
        return

    graph_type = prompt_choice(
        "Graph type:",
        ["All plots (organized folders)",
         "Heatmap",
         "Az/El cuts",
         "Polar plot",
         "3D surface",
         "Gain vs Frequency (multi-file)",
         "Beamwidth vs Frequency (multi-file)",
         "Overlay cuts (multi-file)"],
        default="All plots (organized folders)"
    )

    # ── "All plots" option ────────────────────────────────
    if graph_type == "All plots (organized folders)":
        raw_path = prompt_dir(
            "Folder with pattern CSVs", default="."
        )
        if not raw_path or not os.path.isdir(raw_path):
            print(f"  Path not found: {raw_path}")
            return
        csv_files = sorted([
            *glob.glob(os.path.join(raw_path, "*.csv")),
            *glob.glob(os.path.join(raw_path, "*.dat"))
        ],
            key=lambda f: (
                __import__('core.io',
                           fromlist=['extract_freq_from_filename'])
                .extract_freq_from_filename(f) or 0.0
            )
        )
        if not csv_files:
            print(f"  No CSV or DAT files in {raw_path}")
            return
        print(f"  Found {len(csv_files)} CSV/DAT files")

        from core.io import extract_freq_from_filename as _efn

        # Re-sort properly now that we have the import
        csv_files = sorted(
            csv_files, key=lambda f: _efn(f) or 0.0
        )

        # Create base graphs directory
        base_dir = os.path.join(raw_path, "graphs")
        os.makedirs(base_dir, exist_ok=True)

        # Subfolders for each single-file plot type
        sub_dirs = {
            "heatmaps": os.path.join(base_dir, "heatmaps"),
            "cuts":     os.path.join(base_dir, "cuts"),
            "polar":    os.path.join(base_dir, "polar"),
            "3d":       os.path.join(base_dir, "3d_surface"),
        }
        for d in sub_dirs.values():
            os.makedirs(d, exist_ok=True)

        total = 0
        for fp in csv_files:
            base = os.path.splitext(
                os.path.basename(fp)
            )[0]
            graph_heatmap(
                fp, os.path.join(
                    sub_dirs["heatmaps"],
                    f"{base}_heatmap.png"))
            graph_cuts(
                fp, os.path.join(
                    sub_dirs["cuts"],
                    f"{base}_cuts.png"))
            graph_polar(
                fp, os.path.join(
                    sub_dirs["polar"],
                    f"{base}_polar.png"))
            graph_3d_surface(
                fp, os.path.join(
                    sub_dirs["3d"],
                    f"{base}_3d.png"))
            total += 4

        # Multi-file plots go in the base graphs dir
        copol_files = [f for f in csv_files
                       if '_xpol' not in f]
        if len(copol_files) > 1:
            graph_gain_vs_freq(
                copol_files,
                os.path.join(base_dir, "gain_vs_freq.png"))
            graph_bw_vs_freq(
                copol_files,
                os.path.join(base_dir, "bw_vs_freq.png"))
            graph_overlay_cuts(
                copol_files,
                os.path.join(base_dir, "overlay_cuts.png"))
            total += 3

        print(f"\n  Done! {total} graphs saved to: {base_dir}/")
        print(f"    heatmaps/  cuts/  polar/  3d_surface/")
        if len(copol_files) > 1:
            print(f"    + gain_vs_freq, bw_vs_freq, overlay_cuts")
        return

    if graph_type in ("Heatmap", "Az/El cuts",
                      "Polar plot", "3D surface"):
        # ── Pick source: single file or entire folder ─────
        source = prompt_choice(
            "Source:",
            ["Single CSV file",
             "All CSVs in a folder"],
            default="All CSVs in a folder"
        )
        if "Single" in source:
            fp = prompt_file("  CSV file",
                             must_exist=True,
                             pattern=("*.csv", "*.dat"))
            if not fp:
                print("  No file selected.")
                return
            raw_path = fp
        else:
            raw_path = prompt_dir(
                "Folder with pattern CSVs",
                default="."
            )
        if not raw_path or not os.path.exists(raw_path):
            print(f"  Path not found: {raw_path}")
            return

        # Determine if it's a folder or single file
        if os.path.isdir(raw_path):
            csv_files = sorted([
                *glob.glob(os.path.join(raw_path, "*.csv")),
                *glob.glob(os.path.join(raw_path, "*.dat"))
            ])
            if not csv_files:
                print(f"  No CSV or DAT files in {raw_path}")
                return
            print(f"  Found {len(csv_files)} CSV/DAT files")
        elif os.path.isfile(raw_path):
            csv_files = [raw_path]
        else:
            print(f"  Path not found: {raw_path}")
            return

        graph_dir = make_graph_output_dir(
            raw_path if os.path.isdir(raw_path)
            else os.path.dirname(raw_path) or "."
        )
        print(f"  Graphs will be saved to: {graph_dir}")

        for fp in csv_files:
            base = os.path.splitext(
                os.path.basename(fp)
            )[0]

            if "Heatmap" in graph_type:
                out = os.path.join(
                    graph_dir, f"{base}_heatmap.png"
                )
                graph_heatmap(fp, out)
            elif "cuts" in graph_type:
                out = os.path.join(
                    graph_dir, f"{base}_cuts.png"
                )
                graph_cuts(fp, out)
            elif "Polar" in graph_type:
                out = os.path.join(
                    graph_dir, f"{base}_polar.png"
                )
                graph_polar(fp, out)
            elif "3D" in graph_type:
                out = os.path.join(
                    graph_dir, f"{base}_3d.png"
                )
                graph_3d_surface(fp, out)

        if len(csv_files) > 1:
            print(f"\n  Done! {len(csv_files)} graphs "
                  f"saved to: {graph_dir}")

    else:
        files = prompt_dir_files(
            "Select pattern files:"
        )
        if not files:
            return
        graph_dir = make_graph_output_dir(
            os.path.dirname(files[0]) if files else None
        )
        print(f"  Graphs will be saved to: {graph_dir}")

        if "Gain vs" in graph_type:
            out = os.path.join(
                graph_dir, "gain_vs_freq.png"
            )
            graph_gain_vs_freq(files, out)
        elif "Beamwidth" in graph_type:
            out = os.path.join(
                graph_dir, "beamwidth_vs_freq.png"
            )
            graph_bw_vs_freq(files, out)
        elif "Overlay" in graph_type:
            out = os.path.join(
                graph_dir, "overlay_cuts.png"
            )
            graph_overlay_cuts(files, out)


# ===================================================================
#  MAIN MENU
# ===================================================================

def main_menu() -> None:
    """Top-level interactive menu loop."""
    while True:
        print("\n" + "=" * 60)
        print(f"   ANTENNAFORGE  v{VERSION}")
        print("=" * 60)
        print()
        print("  ── Generate & View ──────────────────────────")
        print("  [1] Generate Patterns"
              "      Create antenna pattern CSVs")
        print("  [2] Graph Patterns"
              "        Heatmap, cuts, polar, 3D")
        print("  [3] Generate PDF Report"
              "   Multi-freq report with plots")
        print()
        print("  ── Analyse ──────────────────────────────────")
        print("  [4] Analyze Patterns"
              "       Stats, comparison, export")
        print("  [5] Pattern Arithmetic"
              "     Add, subtract, envelope…")
        print("  [6] Pattern Rotation"
              "       Pan, tilt, roll transform")
        print("  [7] Sidelobe Mask Test"
              "      ITU-R / MIL-STD compliance")
        print()
        print("  ── RF Calculations ──────────────────────────")
        print("  [8] EIRP Calculator"
              "        Effective radiated power")
        print("  [9] Link Budget"
              "            Path loss & margin")
        print()
        print("  ── Utilities ────────────────────────────────")
        print("  [A] Interpolate Patterns"
              "    Freq interp / resample")
        print("  [B] Batch (JSON Recipe)"
              "     Automated generation")
        print()
        print("  [Q] Quit")

        raw = input("\n> ").strip().lower()

        if raw in ('1', 'generate'):
            menu_generate()
        elif raw in ('2', 'graph', 'plot'):
            menu_graph()
        elif raw in ('3', 'report', 'pdf'):
            menu_report()
        elif raw in ('4', 'analyze', 'analysis'):
            menu_analyze()
        elif raw in ('5', 'arithmetic', 'math'):
            menu_pattern_arithmetic()
        elif raw in ('6', 'rotate', 'tilt'):
            menu_rotate()
        elif raw in ('7', 'mask', 'sidelobe'):
            menu_sidelobe_mask()
        elif raw in ('8', 'eirp'):
            menu_eirp()
        elif raw in ('9', 'link', 'budget'):
            menu_link_budget()
        elif raw in ('a', 'interp', 'interpolate'):
            menu_interpolate()
        elif raw in ('b', 'batch', 'recipe'):
            menu_batch()
        elif raw in ('q', 'quit', 'exit'):
            print("  Goodbye!")
            break
        else:
            print("  Enter 1-9, A, B, or Q")


# ===================================================================
#  MENU 4: PATTERN ARITHMETIC
# ===================================================================

# ===================================================================
#  MENU: PATTERN ROTATION / TILT
# ===================================================================

def menu_rotate() -> None:
    """Interactive pattern rotation / mechanical tilt menu."""
    print("\n" + "=" * 60)
    print("   PATTERN ROTATION / TILT")
    print("=" * 60)

    from core.rotation import (
        rotate_pattern, rotate_directory,
    )

    mode = prompt_choice(
        "Scope:",
        ["Single file", "Entire directory"],
        default="Entire directory"
    )

    az_rot = prompt_float(
        "  Azimuth rotation (deg, + = clockwise)",
        default=0.0, min_val=-360, max_val=360)
    el_tilt = prompt_float(
        "  Elevation tilt (deg, + = up)",
        default=0.0, min_val=-90, max_val=90)
    roll = prompt_float(
        "  Roll (deg, + = CW from behind)",
        default=0.0, min_val=-180, max_val=180)

    if "Single" in mode:
        fp = prompt_file("  Input pattern CSV",
                         must_exist=True, pattern=("*.csv", "*.dat"))
        if not fp:
            return
        out = prompt_save_file("Output CSV",
                               default_name="rotated.csv",
                               ext=".csv")
        rotate_pattern(fp, out, az_rot, el_tilt, roll)
    else:
        d = prompt_dir("Pattern directory")
        if not d or not os.path.isdir(d):
            print(f"  Not a directory: {d}")
            return
        rotate_directory(d, None, az_rot, el_tilt, roll)


def menu_pattern_arithmetic() -> None:
    """Interactive pattern arithmetic (add/subtract/scale) menu."""
    print("\n" + "=" * 60)
    print("   PATTERN ARITHMETIC")
    print("=" * 60)

    from core.pattern_ops import (
        add_patterns, subtract_patterns,
        multiply_patterns, scale_pattern,
        max_envelope, average_patterns,
    )

    op = prompt_choice(
        "Operation:",
        ["Add (power sum)",
         "Subtract (dB difference)",
         "Multiply (element × AF)",
         "Scale (add dB offset)",
         "Max envelope (multi-file)",
         "Average (multi-file)"],
        default="Add (power sum)"
    )

    if "Max" in op or "Average" in op:
        files = prompt_dir_files("Select pattern files:")
        if not files:
            return
        out = prompt_save_file("Output CSV",
                               default_name="result.csv",
                               ext=".csv")
        if "Max" in op:
            max_envelope(files, out)
        else:
            average_patterns(files, out)

    elif "Scale" in op:
        fp = prompt_file("  Pattern CSV")
        offset = prompt_float("  dB offset to add",
                              default=0.0)
        out = prompt_save_file("Output CSV",
                               default_name="scaled.csv",
                               ext=".csv")
        scale_pattern(fp, offset, out)

    else:
        fp_a = prompt_file("  Pattern A CSV")
        fp_b = prompt_file("  Pattern B CSV")
        out = prompt_save_file("Output CSV",
                               default_name="result.csv",
                               ext=".csv")
        if "Add" in op:
            add_patterns(fp_a, fp_b, out)
        elif "Subtract" in op:
            subtract_patterns(fp_a, fp_b, out)
        elif "Multiply" in op:
            multiply_patterns(fp_a, fp_b, out)


# ===================================================================
#  MENU 5: EIRP CALCULATOR
# ===================================================================

def menu_eirp() -> None:
    """Interactive EIRP calculator."""
    print("\n" + "=" * 60)
    print("   EIRP CALCULATOR")
    print("=" * 60)

    from core.eirp import (
        compute_eirp, compute_power_density,
    )

    fp = prompt_file("  Gain pattern CSV")
    tx_pwr = prompt_float(
        "  Tx power (dBm)", default=30.0)
    cable_loss = prompt_float(
        "  Cable/connector loss (dB)", default=2.0,
        min_val=0)

    compute_eirp(fp, tx_pwr, cable_loss)

    if prompt_yn("  Also compute power density?",
                 default=False):
        dist = prompt_float(
            "  Distance (meters)", default=100.0,
            min_val=0.1)
        compute_power_density(fp, tx_pwr, cable_loss, dist)


# ===================================================================
#  MENU 6: LINK BUDGET
# ===================================================================

def menu_link_budget() -> None:
    """Interactive link budget calculator."""
    print("\n" + "=" * 60)
    print("   LINK BUDGET ANALYSIS")
    print("=" * 60)

    from core.link_budget import (
        compute_link_budget, compute_link_margin,
    )

    mode = prompt_choice(
        "Mode:",
        ["Full angular map",
         "Boresight link margin"],
        default="Boresight link margin"
    )

    tx_file = prompt_file("  Tx pattern CSV")
    rx_file = prompt_file("  Rx pattern CSV")
    dist = prompt_float(
        "  Distance (km)", default=10.0, min_val=0.001)
    freq = prompt_float(
        "  Frequency (MHz)", default=150.0, min_val=0.1)
    tx_pwr = prompt_float(
        "  Tx power (dBm)", default=30.0)
    tx_loss = prompt_float(
        "  Tx cable loss (dB)", default=2.0, min_val=0)
    rx_loss = prompt_float(
        "  Rx cable loss (dB)", default=2.0, min_val=0)

    if "Full" in mode:
        compute_link_budget(
            tx_file, rx_file, dist, freq,
            tx_pwr, tx_loss, rx_loss
        )
    else:
        rx_sens = prompt_float(
            "  Rx sensitivity (dBm)", default=-90.0)
        compute_link_margin(
            tx_file, rx_file, dist, freq,
            tx_pwr, rx_sens, tx_loss, rx_loss
        )


# ===================================================================
#  MENU 7: INTERPOLATE PATTERNS
# ===================================================================

def menu_interpolate() -> None:
    """Interactive frequency interpolation menu."""
    print("\n" + "=" * 60)
    print("   PATTERN INTERPOLATION")
    print("=" * 60)

    from core.interpolation import (
        interpolate_frequency, resample_pattern,
        multi_freq_interpolation,
    )

    mode = prompt_choice(
        "Mode:",
        ["Interpolate between 2 frequencies",
         "Multi-file frequency interpolation",
         "Resample to new angular grid"],
        default="Interpolate between 2 frequencies"
    )

    if "2 freq" in mode:
        f_lo = prompt_file("  Lower frequency CSV")
        f_hi = prompt_file("  Higher frequency CSV")
        target = prompt_float(
            "  Target frequency (MHz)", min_val=0.001
        )
        interpolate_frequency(f_lo, f_hi, target)

    elif "Multi" in mode:
        files = prompt_dir_files(
            "Select pattern files (sorted by freq):"
        )
        if not files:
            return
        raw = input(
            "  Target freqs (comma-sep MHz): "
        ).strip()
        try:
            targets = [float(x.strip())
                       for x in raw.split(',')]
        except ValueError:
            print("  Invalid frequency list")
            return
        multi_freq_interpolation(files, targets)

    elif "Resample" in mode:
        fp = prompt_file("  Pattern CSV")
        az_step = prompt_float(
            "  New az step (deg)", default=0.5,
            min_val=0.1, max_val=10)
        el_step = prompt_float(
            "  New el step (deg)", default=0.5,
            min_val=0.1, max_val=10)
        method = prompt_choice(
            "Interpolation method:",
            ["bilinear", "bicubic"],
            default="bilinear"
        )
        resample_pattern(fp, az_step, el_step,
                         method=method)


# ===================================================================
#  MENU 8: SIDELOBE MASK TEST
# ===================================================================

def menu_sidelobe_mask() -> None:
    """Interactive sidelobe mask compliance test menu."""
    print("\n" + "=" * 60)
    print("   SIDELOBE MASK COMPLIANCE TEST")
    print("=" * 60)

    from core.sidelobe_masks import (
        itu_r_s580, itu_r_s465, mil_std_envelope,
        load_mask_from_json, test_pattern_against_mask,
    )

    fp = prompt_file("  Pattern CSV")

    mask_type = prompt_choice(
        "Mask type:",
        ["ITU-R S.580-6",
         "ITU-R S.465-6",
         "MIL-STD envelope",
         "Custom (JSON file)"],
        default="ITU-R S.580-6"
    )

    if "S.580" in mask_type:
        peak_g = prompt_float(
            "  Peak gain (dBi)", default=30.0)
        mask = itu_r_s580(peak_g)
    elif "S.465" in mask_type:
        d_lam = prompt_float(
            "  Antenna diameter (wavelengths)",
            default=20.0, min_val=1)
        mask = itu_r_s465(d_lam)
    elif "MIL" in mask_type:
        peak_g = prompt_float(
            "  Peak gain (dBi)", default=20.0)
        sll = prompt_float(
            "  Required SLL (dB, negative)",
            default=-20.0, max_val=0)
        mask = mil_std_envelope(peak_g, sll)
    else:
        mask_path = prompt_file("  Mask JSON file",
                                must_exist=True,
                                pattern="*.json")
        mask = load_mask_from_json(mask_path)

    plane = prompt_choice(
        "Test plane:", ["az", "el"], default="az"
    )
    test_pattern_against_mask(fp, mask, plane)


# ===================================================================
#  MENU 9: PDF REPORT
# ===================================================================

def _report_config_menu(report_cfg: dict) -> dict:
    """Interactive report configuration sub-menu."""
    """Interactive toggle menu for report sections.

    Mutates *report_cfg* in place and returns it.
    """
    from reporting.report import (
        REPORT_SECTIONS, REPORT_OPTIONS,
        PRESETS, default_report_config,
    )

    while True:
        print("\n" + "-" * 60)
        print("   REPORT SECTIONS")
        print("-" * 60)

        # Group labels
        group_titles = {
            "global":   "GLOBAL PAGES",
            "per_freq": "PER-FREQUENCY PAGES",
            "option":   "OPTIONS",
        }
        current_group = None
        items = list(REPORT_SECTIONS.items())
        for i, (key, (_default, label, group)) in enumerate(
                items, 1):
            if group != current_group:
                current_group = group
                print(f"\n  {group_titles.get(group, group)}")
            marker = "x" if report_cfg.get(key, False) else " "
            status = " ON" if report_cfg.get(key, False) else "OFF"
            print(f"    {i:>2}. [{marker}] {label:<48} {status}")

        # Numeric options
        print(f"\n  NUMERIC OPTIONS")
        opt_start = len(items) + 1
        opt_items = list(REPORT_OPTIONS.items())
        for j, (key, (_default, label)) in enumerate(
                opt_items):
            val = report_cfg.get(key, _default)
            num = opt_start + j
            print(f"    {num:>2}. {label:<48} = {val}")

        total = opt_start + len(opt_items)

        print()
        print(f"    {total}. Select preset "
              f"(default/full/minimal/quick)")
        print(f"    {total+1}. Enable ALL sections")
        print(f"    {total+2}. Disable ALL sections")
        print()
        print("     0. Done — continue to generate")
        print()

        raw = input("  Toggle # (or 0 to proceed): ").strip()
        if raw == "" or raw == "0":
            break

        try:
            choice = int(raw)
        except ValueError:
            print("  Enter a number")
            continue

        if 1 <= choice <= len(items):
            key = items[choice - 1][0]
            report_cfg[key] = not report_cfg.get(key, False)
        elif opt_start <= choice < total:
            key = opt_items[choice - opt_start][0]
            if key == "extra_cut_angles":
                raw_angles = input(
                    "  Enter cut angles (comma-separated, "
                    "e.g. 15,30,45): "
                ).strip()
                if raw_angles:
                    try:
                        angles = [
                            float(x.strip())
                            for x in raw_angles.split(",")
                            if x.strip()
                        ]
                        report_cfg[key] = angles
                    except ValueError:
                        print("  Invalid angles")
                else:
                    report_cfg[key] = []
            else:
                try:
                    val = float(input(
                        f"  New value for "
                        f"{REPORT_OPTIONS[key][1]}: "
                    ).strip())
                    report_cfg[key] = int(val) if val == int(val) else val
                except ValueError:
                    print("  Invalid number")
        elif choice == total:
            # Preset picker
            print()
            for pi, (pkey, (pdesc, _pfn)) in enumerate(
                    PRESETS.items(), 1):
                print(f"    {pi}. {pdesc}")
            try:
                pc = int(input("  Preset #: ").strip())
                pkeys = list(PRESETS.keys())
                if 1 <= pc <= len(pkeys):
                    new = PRESETS[pkeys[pc - 1]][1]()
                    report_cfg.update(new)
                    print(f"  Applied preset: "
                          f"{pkeys[pc - 1]}")
            except (ValueError, IndexError):
                print("  Invalid choice")
        elif choice == total + 1:
            for key in REPORT_SECTIONS:
                report_cfg[key] = True
            print("  All sections enabled")
        elif choice == total + 2:
            for key in REPORT_SECTIONS:
                report_cfg[key] = False
            print("  All sections disabled")
        else:
            print("  Invalid choice")

    return report_cfg


def menu_report() -> None:
    """Interactive report generation menu (PDF / LaTeX)."""
    print("\n" + "=" * 60)
    print("   GENERATE REPORT")
    print("=" * 60)

    from reporting.report import (
        generate_report, default_report_config,
    )

    # Choose output format
    fmt = prompt_choice(
        "Report format:",
        ["PDF", "LaTeX (.tex)"],
        default="PDF"
    )
    is_latex = "latex" in fmt.lower() or "tex" in fmt.lower()

    input_dir = prompt_dir("Pattern directory")
    if not input_dir or not os.path.isdir(input_dir):
        print(f"  Not a directory: {input_dir}")
        return

    title = input(
        "  Report title (blank=auto): "
    ).strip() or None

    # ── Report configuration ─────────────────────────
    report_cfg = default_report_config()
    if prompt_yn("  Configure report sections?",
                 default=False):
        _report_config_menu(report_cfg)

    # Count enabled
    from reporting.report import REPORT_SECTIONS
    on = sum(1 for k in REPORT_SECTIONS
             if report_cfg.get(k, False))
    print(f"\n  {on}/{len(REPORT_SECTIONS)} sections enabled")

    if is_latex:
        from reporting.latex_report import (
            generate_latex_report,
        )
        out = prompt_save_file(
            "Output .tex",
            default_name="antenna_report.tex",
            ext=".tex"
        ) if prompt_yn("  Choose output path?",
                       default=False) else None
        generate_latex_report(input_dir, out, title, report_cfg)
    else:
        out = prompt_save_file(
            "Output PDF",
            default_name="antenna_report.pdf",
            ext=".pdf"
        ) if prompt_yn("  Choose output path?",
                       default=False) else None
        generate_report(input_dir, out, title, report_cfg)


# ===================================================================
#  MENU B: BATCH MODE
# ===================================================================

def menu_batch() -> None:
    """Interactive batch processing menu."""
    print("\n" + "=" * 60)
    print("   BATCH MODE (JSON RECIPE)")
    print("=" * 60)

    from core.batch import (
        run_batch, create_sample_recipe,
    )

    action = prompt_choice(
        "Action:",
        ["Run a recipe file",
         "Dry run (validate only)",
         "Create sample recipe"],
        default="Run a recipe file"
    )

    if "sample" in action.lower():
        out = prompt_save_file(
            "Save sample recipe as",
            default_name="sample_recipe.json",
            ext=".json"
        )
        create_sample_recipe(out)
    else:
        path = prompt_file("  Recipe JSON file",
                           must_exist=True,
                           pattern="*.json")
        if not path or not os.path.exists(path):
            print(f"  File not found: {path}")
            return
        dry = "Dry" in action
        run_batch(path, dry_run=dry)