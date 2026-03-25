"""
Parameter fitting — derive AntennaForge config from reference patterns.

Given one or more measured/legacy pattern CSV files, determines the
AntennaForge configuration parameters that best reproduce them.

Depends on: config, core.io, core.engine, analysis.analyzer, antennas.
"""

import copy
import logging
import math
import os

logger = logging.getLogger(__name__)

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

try:
    from scipy.optimize import minimize as _scipy_minimize
    from scipy.optimize import differential_evolution as _scipy_de
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


# ===================================================================
#  PUBLIC API
# ===================================================================

def fit_parameters(
    reference_files: list[str],
    antenna_type: str,
    f_min_mhz: float,
    f_max_mhz: float,
    optimize: bool = True,
    max_passes: int = 3,
    target_rms: float = 0.5,
    progress_cb=None,
) -> dict:
    """Fit AntennaForge config parameters to reference pattern files.

    Args:
        reference_files: Paths to reference pattern CSV/DAT files.
        antenna_type: Antenna type name (e.g. ``"LPDA"``, ``"Panel"``).
        f_min_mhz: Lower band edge in MHz.
        f_max_mhz: Upper band edge in MHz.
        optimize: If ``True`` and SciPy is available, refine the
                  measurement-seeded config via numerical optimization.
        max_passes: Maximum number of optimization passes (base + scaling).
        target_rms: Target RMS error (dB) to stop early if achieved.
        progress_cb: Optional ``callback(message: str)`` for GUI
                     progress updates.

    Returns:
        Dict with keys:

        - **config** — fitted config dict (same schema as
          ``generation_config.json``).
        - **quality** — fit-quality metrics dict for the mid-band
          reference file.
        - **report** — human-readable summary string.
    """
    if not reference_files:
        raise ValueError("No reference files provided.")
    if f_min_mhz <= 0 or f_max_mhz <= f_min_mhz:
        raise ValueError("Invalid frequency range.")

    def log(msg):
        if progress_cb:
            progress_cb(msg)

    # ── Load and analyse all reference files ──────────────
    log("Loading reference patterns...")
    from analysis.analyzer import analyze_from_data

    ref_data = []

    # Check if input is a single .tbl file
    is_tbl = (len(reference_files) == 1
              and reference_files[0].lower().endswith('.tbl'))

    if is_tbl:
        from core.io import read_odessa_tbl
        tbl_path = reference_files[0]
        log(f"Reading ODESSA table: {os.path.basename(tbl_path)}")
        tbl = read_odessa_tbl(tbl_path)

        az = tbl['az_deg']
        el = tbl['el_deg']

        for i, freq in enumerate(tbl['freqs_mhz']):
            data = tbl['slices'][i]
            analysis = analyze_from_data(az, el, data)
            ref_data.append({
                'file': f"{os.path.basename(tbl_path)}[{freq:.2f}MHz]",
                'freq': freq,
                'az': az,
                'el': el,
                'data': data,
                'analysis': analysis,
            })
        log(f"Loaded {len(ref_data)} frequency slices from table.")
    else:
        from core.io import read_pattern_csv, extract_freq_from_filename

        for fpath in sorted(reference_files):
            freq = extract_freq_from_filename(fpath)
            if freq is None:
                freq = _extract_freq_flexible(fpath)
            az, el, data = read_pattern_csv(fpath)
            analysis = analyze_from_data(az, el, data)
            ref_data.append({
                'file': fpath,
                'freq': freq,
                'az': az,
                'el': el,
                'data': data,
                'analysis': analysis,
            })

    # ── Assign frequencies to files (CSV/DAT only) ────────
    if not is_tbl:
        # Validate parsed frequencies against the user-provided band.
        # If a frequency is far outside [f_min, f_max], it's probably a
        # spurious number from the filename (e.g. "slice_01" → 1.0 MHz)
        # rather than a real frequency.  Allow 50 % margin.
        band_lo = f_min_mhz * 0.5
        band_hi = f_max_mhz * 1.5
        for r in ref_data:
            if r['freq'] is not None and not (band_lo <= r['freq'] <= band_hi):
                r['freq'] = None          # reject implausible value

        n_parsed = sum(1 for r in ref_data if r['freq'] is not None)
        n_files = len(ref_data)

        if n_parsed < n_files / 2:
            # Most filenames don't contain a parseable frequency.
            # Assign evenly-spaced frequencies across the user-provided
            # band, assuming files are sorted by name = sorted by freq.
            ref_data.sort(
                key=lambda r: os.path.basename(r['file']).lower())
            if n_files == 1:
                assigned = [(f_min_mhz + f_max_mhz) / 2.0]
            else:
                step = (f_max_mhz - f_min_mhz) / (n_files - 1)
                assigned = [round(f_min_mhz + i * step, 2)
                            for i in range(n_files)]
            for r, f in zip(ref_data, assigned):
                r['freq'] = f
            log(f"Frequencies not found in filenames — assigned "
                f"{n_files} evenly from {f_min_mhz:.1f} to "
                f"{f_max_mhz:.1f} MHz (sorted by filename).")
        else:
            ref_data.sort(key=lambda r: r['freq'] or 0.0)
            if n_parsed < n_files:
                log(f"Warning: {n_files - n_parsed} file(s) had no "
                    f"parseable frequency in the filename.")

    # ── Detect spacing and pick representative file ───────
    # Determine if spacing is likely log or linear
    spacing_mode = _detect_spacing([r['freq'] for r in ref_data if r['freq']])
    
    if spacing_mode == "log":
        # Geometric mean for log spacing
        import math
        f_mid = math.sqrt(f_min_mhz * f_max_mhz)
    else:
        # Arithmetic mean for linear spacing
        f_mid = (f_min_mhz + f_max_mhz) / 2.0

    mid_idx = min(
        range(len(ref_data)),
        key=lambda i: abs((ref_data[i]['freq'] or 0) - f_mid),
    )

    mid = ref_data[mid_idx]
    mid_name = os.path.basename(mid['file'])
    mid_freq = mid['freq'] or f_mid
    log(f"Reference file: {mid_name} ({mid_freq:.1f} MHz)")
    log(f"Antenna type: {antenna_type}")
    log(f"Band: {f_min_mhz:.1f} - {f_max_mhz:.1f} MHz")

    # ── Seed config from measurements ─────────────────────
    log("Seeding parameters from measurements...")
    cfg = _seed_config(
        ref_data, mid_idx, antenna_type, f_min_mhz, f_max_mhz, spacing_mode)

    # ── Optional SciPy optimisation ───────────────────────
    optimized = False
    if optimize and _HAS_SCIPY and _HAS_NUMPY:
        log(f"Starting iterative optimization (max {max_passes} passes)...")

        # Stage 0: Principal-plane cut fitting
        log("Stage 0: Principal-plane cut fitting...")
        cfg, _ = _optimize_cuts(cfg, ref_data, log)

        for i in range(max_passes):
            log(f"Pass {i+1}/{max_passes}: Optimizing base parameters...")
            cfg, imp_base = _optimize_config(cfg, ref_data, log)

            log(f"Pass {i+1}/{max_passes}: Optimizing frequency scaling...")
            cfg, imp_scale = _optimize_scaling(cfg, ref_data, log)

            # Check convergence
            quality = _compute_fit_quality(cfg, mid)
            if quality['rms_db'] <= target_rms:
                log(f"Target RMS {target_rms} dB reached. Stopping.")
                break

            if not imp_base and not imp_scale:
                log("Optimization converged (no further improvement).")
                break
        
        optimized = True
        log("Cleaning up temporary optimization data...")
    elif optimize and not _HAS_SCIPY:
        log("SciPy not available — skipping optimization.")

    # ── Fit quality ───────────────────────────────────────
    log("Computing fit quality across all files...")
    quality = _compute_fit_quality(cfg, mid)
    agg_quality = _compute_aggregate_quality(cfg, ref_data)

    # ── Report ────────────────────────────────────────────
    report = _build_report(
        cfg, ref_data, mid_idx, quality, antenna_type, optimized,
        agg_quality=agg_quality,
    )

    return {
        'config': cfg,
        'quality': quality,
        'agg_quality': agg_quality,
        'report': report,
    }


# ===================================================================
#  RECOMMENDED RUNS PER ANTENNA TYPE
# ===================================================================

# Maps antenna type to (recommended_runs, reason).
# Higher values for types with more unique parameters or where
# feature toggling is important for convergence.
_RECOMMENDED_RUNS: dict[str, tuple[int, str]] = {
    "LPDA":     (4,  "4 base strategies (BW mode x gain coupling)"),
    "Omni":     (4,  "Omni: 4 base + feature toggle exploration"),
    "Monopole": (6,  "Monopole: element length + feature toggles need exploration"),
    "Panel":    (6,  "Panel: downtilt + BW modes + feature toggles"),
    "Horn":     (4,  "Horn: 4 base strategies (straightforward pattern)"),
    "Dish":     (8,  "Dish: DE + feature combos — many interacting params"),
    "Array":    (10, "Array: DE + spacing/steering — large search space"),
}


# Per-type auto-stop RMS targets (dB).
# Below these thresholds the fit is "close enough" given model fidelity.
_TYPE_TARGET_RMS: dict[str, float] = {
    "Monopole": 0.5,
    "Omni":     1.0,
    "LPDA":     1.5,
    "Horn":     1.5,
    "Panel":    1.5,
    "Dish":     2.0,
    "Array":    2.5,
}


def type_target_rms(antenna_type: str) -> float:
    """Return the per-type auto-stop RMS target in dB."""
    return _TYPE_TARGET_RMS.get(antenna_type, 1.5)


def recommended_runs(antenna_type: str) -> tuple[int, str]:
    """Return ``(n_runs, reason)`` for the given antenna type.

    Used by the GUI to auto-populate the Runs field and display
    a helpful hint next to it.
    """
    return _RECOMMENDED_RUNS.get(antenna_type, (4, "Default"))


# ===================================================================
#  MULTI-RUN STRATEGY EXPLORATION
# ===================================================================

def _generate_strategies(antenna_type: str = "LPDA") -> list[dict]:
    """Generate strategy combinations with systematic feature enumeration.

    The first strategies cover the 4 base combinations
    (bw_mode × gain_coupling).  Additional strategies systematically
    explore the most impactful feature combinations rather than
    relying on random toggling.
    """
    # ── Base strategies (4) ──────────────────────────────
    base = []
    for bw_mode in ('exponent', 'three_point'):
        for gc in (True, False):
            base.append({
                'bw_mode': bw_mode,
                'gain_coupling': gc,
                'vswr': False,
                'feature_overrides': None,
                'label': f"{bw_mode}/gc={'on' if gc else 'off'}",
            })

    # ── Systematic feature combinations (4-8) ────────────
    # Enumerate the most impactful feature toggles:
    # sidelobes × ground_reflection = 4 combos.
    # Skip sidelobes toggling for Dish/Array (physically inappropriate).
    can_toggle_sl = antenna_type not in ('Dish', 'Array')

    feature_combos = []
    sl_options = [True, False] if can_toggle_sl else [False]
    for sl_on in sl_options:
        for gr_on in (True, False):
            overrides = {'ground_reflection': gr_on}
            if can_toggle_sl:
                overrides['sidelobes'] = sl_on
            label_parts = []
            if can_toggle_sl:
                label_parts.append(f"sl={'on' if sl_on else 'off'}")
            label_parts.append(f"gr={'on' if gr_on else 'off'}")
            feature_combos.append({
                'bw_mode': 'exponent',
                'gain_coupling': True,
                'vswr': False,
                'feature_overrides': overrides,
                'label': f"feat/{'/'.join(label_parts)}",
            })

    # Add VSWR-on variants for the best base strategy
    vswr_strats = []
    for gc in (True, False):
        vswr_strats.append({
            'bw_mode': 'exponent',
            'gain_coupling': gc,
            'vswr': True,
            'feature_overrides': None,
            'label': f"exponent/gc={'on' if gc else 'off'}/vswr",
        })

    return base + feature_combos + vswr_strats


def _perturb_config(cfg: dict) -> None:
    """Apply random perturbations to config for optimization restarts.

    Perturbations are tailored per antenna type so that every type's
    unique parameters get explored during multi-run fitting.
    """
    import random

    atype = cfg.get('antenna_type', '')
    is_omni = atype in ("Omni", "Monopole")

    # ── Common parameters (all types) ─────────────────────
    # Gain +/- 2.5 dB (wider than before for better exploration)
    cfg['max_gain_dbi'] += random.uniform(-2.5, 2.5)

    # sigmoid_k — back-lobe sharpness (directional types only)
    if not is_omni:
        k = cfg.get('sigmoid_k', 12.0)
        cfg['sigmoid_k'] = max(3.0, min(50.0, k * random.uniform(0.7, 1.3)))

    # ── Beamwidths ────────────────────────────────────────
    # Az beamwidth (skip for omni types — fixed at 360°)
    if not is_omni and 'az_beamwidth_deg' in cfg:
        bw = cfg['az_beamwidth_deg']
        cfg['az_beamwidth_deg'] = max(1.0, bw * random.uniform(0.80, 1.20))

    # El beamwidth (skip for Monopole — driven by element_length)
    if atype != 'Monopole' and 'el_beamwidth_deg' in cfg:
        bw = cfg['el_beamwidth_deg']
        cfg['el_beamwidth_deg'] = max(1.0, bw * random.uniform(0.80, 1.20))

    # FTB +/- 4 dB (directional types only)
    if not is_omni and 'ftb_ratio_db' in cfg:
        ftb = cfg['ftb_ratio_db']
        cfg['ftb_ratio_db'] = max(0.0, ftb + random.uniform(-4.0, 4.0))

    # ── Monopole-specific ─────────────────────────────────
    if atype == 'Monopole':
        L = cfg.get('element_length_wavelengths', 0.25)
        cfg['element_length_wavelengths'] = max(
            0.05, min(2.0, L * random.uniform(0.7, 1.3)))

    # ── Mechanical tilt (all directional types) ─────────
    if not is_omni and 'mechanical_tilt_deg' in cfg:
        dt = cfg.get('mechanical_tilt_deg', 0.0)
        cfg['mechanical_tilt_deg'] = max(-30.0, min(30.0,
            dt + random.uniform(-5.0, 5.0)))

    # ── Panel-specific ────────────────────────────────────
    # (no extra params beyond mechanical_tilt_deg)

    # ── Dish-specific ─────────────────────────────────────
    if atype == 'Dish':
        eff = cfg.get('dish_efficiency', 0.6)
        cfg['dish_efficiency'] = max(0.2, min(0.95,
            eff + random.uniform(-0.15, 0.15)))
        taper = cfg.get('feed_edge_taper_db', -12.0)
        cfg['feed_edge_taper_db'] = max(-25.0, min(-3.0,
            taper + random.uniform(-3.0, 3.0)))

    # ── Horn-specific ─────────────────────────────────────
    if atype == 'Horn':
        ap = cfg.get('horn_aperture_wavelengths')
        if ap is not None:
            cfg['horn_aperture_wavelengths'] = max(0.5, min(20.0,
                ap * random.uniform(0.8, 1.2)))

    # ── Array-specific ────────────────────────────────────
    if atype == 'Array':
        # Element spacing
        for key in ('array_spacing_x_lambda', 'array_spacing_y_lambda'):
            if key in cfg:
                v = cfg[key]
                cfg[key] = max(0.25, min(1.5,
                    v * random.uniform(0.85, 1.15)))
        # Steering angles
        for key in ('array_steer_az_deg', 'array_steer_el_deg'):
            if key in cfg:
                cfg[key] += random.uniform(-5.0, 5.0)
        # Taper SLL
        if 'array_taper_sll_db' in cfg:
            v = cfg['array_taper_sll_db']
            cfg['array_taper_sll_db'] = max(-40.0, min(-10.0,
                v + random.uniform(-3.0, 3.0)))
        # Per-element errors
        if 'array_rms_phase_error_deg' in cfg:
            v = cfg['array_rms_phase_error_deg']
            cfg['array_rms_phase_error_deg'] = max(0.0, min(30.0,
                v + random.uniform(-2.0, 2.0)))
        if 'array_rms_amplitude_error_db' in cfg:
            v = cfg['array_rms_amplitude_error_db']
            cfg['array_rms_amplitude_error_db'] = max(0.0, min(3.0,
                v + random.uniform(-0.3, 0.3)))

    # ── Feature sub-parameters ────────────────────────────
    feats = cfg.get('features', {})

    # Sidelobe parameters
    sl = feats.get('sidelobes', {})
    if sl.get('enabled'):
        v = sl.get('first_sidelobe_db', -13.2)
        sl['first_sidelobe_db'] = max(-30.0, min(-5.0,
            v + random.uniform(-3.0, 3.0)))
        dr = sl.get('decay_rate_db', 2.0)
        sl['decay_rate_db'] = max(0.5, min(6.0,
            dr * random.uniform(0.7, 1.3)))

    # Ground reflection parameters
    gr = feats.get('ground_reflection', {})
    if gr.get('enabled'):
        h = gr.get('height_wavelengths', 1.0)
        gr['height_wavelengths'] = max(0.2, min(10.0,
            h * random.uniform(0.7, 1.3)))
        rc = gr.get('reflection_coeff', 0.5)
        gr['reflection_coeff'] = max(0.1, min(0.95,
            rc + random.uniform(-0.15, 0.15)))

    # VSWR rolloff parameters
    vr = feats.get('vswr_rolloff', {})
    if vr.get('enabled'):
        mr = vr.get('max_rolloff_db', 3.0)
        vr['max_rolloff_db'] = max(0.5, min(8.0,
            mr * random.uniform(0.7, 1.3)))

    # Gain-BW coupling
    gc = feats.get('gain_bw_coupling', {})
    if gc.get('enabled'):
        ro = gc.get('gain_rolloff_db_per_octave', 1.5)
        gc['gain_rolloff_db_per_octave'] = max(0.1, min(5.0,
            ro * random.uniform(0.7, 1.3)))

    # BW scaling exponents
    for key in ('freq_dependent_bw_az', 'freq_dependent_bw_el'):
        feat = feats.get(key, {})
        if feat.get('enabled'):
            mode = feat.get('decay_mode', 'exponent')
            if mode == 'exponent':
                e = feat.get('scaling_exponent', 0.8)
                feat['scaling_exponent'] = max(0.05, min(2.0,
                    e * random.uniform(0.7, 1.3)))

    # ── Feature toggling (random chance) ──────────────────
    # With small probability, toggle features the heuristic
    # may have gotten wrong.  Skip features that are physically
    # inappropriate for the antenna type.
    toggle_features = ['ground_reflection', 'vswr_rolloff',
                       'freq_dependent_bw_el']
    if not is_omni:
        toggle_features.append('freq_dependent_bw_az')
    # Sidelobe overlay: only for LPDA/Omni/Monopole/Horn/Panel.
    # Dish has intrinsic Airy sidelobes; Array uses Taylor weighting.
    if atype not in ('Dish', 'Array'):
        toggle_features.append('sidelobes')

    for fname in toggle_features:
        feat = feats.get(fname, {})
        if random.random() < 0.25:
            feat['enabled'] = not feat.get('enabled', False)


def fit_parameters_multirun(
    reference_files: list[str],
    antenna_type: str,
    f_min_mhz: float,
    f_max_mhz: float,
    n_runs: int = 1,
    optimize: bool = True,
    max_passes: int = 3,
    target_rms: float = 0.5,
    progress_cb=None,
    stop_event=None,
) -> dict:
    """Run multiple fitting strategies and return the best result.

    When *n_runs* is 1, delegates directly to :func:`fit_parameters`
    (backward compatible).  When *n_runs* > 1, generates strategy
    combinations, runs each, and picks the one with the lowest
    aggregate linear-percentage error across all reference files.

    When *n_runs* is 0, runs indefinitely until *stop_event* is set
    or the target RMS is achieved.

    Args:
        stop_event: Optional ``threading.Event``.  When set, the
                    current run finishes and the best result so far
                    is returned.

    Returns the same dict as :func:`fit_parameters`, with an
    additional ``'strategy_results'`` key listing per-run scores.
    """
    unlimited = n_runs == 0

    # Use per-type target if user hasn't set a tighter one
    effective_rms = min(target_rms, type_target_rms(antenna_type))

    if n_runs == 1:
        return fit_parameters(
            reference_files, antenna_type, f_min_mhz, f_max_mhz,
            optimize, max_passes, target_rms, progress_cb,
        )

    if not reference_files:
        raise ValueError("No reference files provided.")
    if f_min_mhz <= 0 or f_max_mhz <= f_min_mhz:
        raise ValueError("Invalid frequency range.")

    def log(msg):
        if progress_cb:
            progress_cb(msg)

    # ── Load reference data once (shared across all runs) ──
    log("Loading reference patterns...")
    from analysis.analyzer import analyze_from_data

    ref_data = []
    is_tbl = (len(reference_files) == 1
              and reference_files[0].lower().endswith('.tbl'))

    if is_tbl:
        from core.io import read_odessa_tbl
        tbl_path = reference_files[0]
        tbl = read_odessa_tbl(tbl_path)
        az = tbl['az_deg']
        el = tbl['el_deg']
        for i, freq in enumerate(tbl['freqs_mhz']):
            data = tbl['slices'][i]
            analysis = analyze_from_data(az, el, data)
            ref_data.append({
                'file': f"{os.path.basename(tbl_path)}[{freq:.2f}MHz]",
                'freq': freq, 'az': az, 'el': el,
                'data': data, 'analysis': analysis,
            })
    else:
        from core.io import read_pattern_csv, extract_freq_from_filename
        for fpath in sorted(reference_files):
            freq = extract_freq_from_filename(fpath)
            if freq is None:
                freq = _extract_freq_flexible(fpath)
            az, el, data = read_pattern_csv(fpath)
            analysis = analyze_from_data(az, el, data)
            ref_data.append({
                'file': fpath, 'freq': freq,
                'az': az, 'el': el,
                'data': data, 'analysis': analysis,
            })

    # Frequency assignment (same logic as fit_parameters)
    if not is_tbl:
        band_lo, band_hi = f_min_mhz * 0.5, f_max_mhz * 1.5
        for r in ref_data:
            if r['freq'] is not None and not (band_lo <= r['freq'] <= band_hi):
                r['freq'] = None
        n_parsed = sum(1 for r in ref_data if r['freq'] is not None)
        n_files = len(ref_data)
        if n_parsed < n_files / 2:
            ref_data.sort(key=lambda r: os.path.basename(r['file']).lower())
            if n_files == 1:
                assigned = [(f_min_mhz + f_max_mhz) / 2.0]
            else:
                step = (f_max_mhz - f_min_mhz) / (n_files - 1)
                assigned = [round(f_min_mhz + i * step, 2)
                            for i in range(n_files)]
            for r, f in zip(ref_data, assigned):
                r['freq'] = f
        else:
            ref_data.sort(key=lambda r: r['freq'] or 0.0)

    spacing_mode = _detect_spacing(
        [r['freq'] for r in ref_data if r['freq']])

    if spacing_mode == "log":
        f_mid = math.sqrt(f_min_mhz * f_max_mhz)
    else:
        f_mid = (f_min_mhz + f_max_mhz) / 2.0

    mid_idx = min(
        range(len(ref_data)),
        key=lambda i: abs((ref_data[i]['freq'] or 0) - f_mid),
    )

    log(f"Loaded {len(ref_data)} reference files.")

    # ── Warm-start: check fit cache ───────────────────────
    cached_seed = _find_cached_seed(antenna_type, f_min_mhz, f_max_mhz)
    if cached_seed:
        log("Found cached fit — will use as additional seed.")

    # ── Generate and run strategies ────────────────────────
    base_strategies = _generate_strategies(antenna_type)

    # Insert a cached-seed strategy if available
    if cached_seed:
        base_strategies.insert(0, {
            'bw_mode': 'exponent',
            'gain_coupling': True,
            'vswr': False,
            'feature_overrides': None,
            'cached_seed': cached_seed,
            'label': "cached-warm-start",
        })

    if unlimited:
        log("Unlimited mode — will run until stopped or target RMS reached.")
    else:
        # Build a fixed list of strategies for n_runs
        strategies = list(base_strategies)
        if n_runs > len(strategies):
            import random as _rnd
            while len(strategies) < n_runs:
                base = _rnd.choice(base_strategies)
                new_strat = base.copy()
                new_strat['label'] += " (rnd)"
                new_strat['perturb'] = True
                strategies.append(new_strat)
        strategies = strategies[:n_runs]

    import random

    def _next_strategy(run_i):
        """Return the strategy for run *run_i*."""
        if not unlimited:
            return strategies[run_i]
        if run_i < len(base_strategies):
            return base_strategies[run_i]
        base = random.choice(base_strategies)
        new_strat = base.copy()
        new_strat['label'] += f" (rnd-{run_i + 1})"
        new_strat['perturb'] = True
        return new_strat

    def _stopped():
        return stop_event is not None and stop_event.is_set()

    total_label = "∞" if unlimited else str(n_runs)
    results = []
    run_i = 0
    while True:
        if _stopped():
            log("\nStop requested — finishing up.")
            break
        if not unlimited and run_i >= n_runs:
            break

        strat = _next_strategy(run_i)
        log(f"\nRun {run_i + 1}/{total_label}: {strat['label']}")

        # Seed with strategy overrides
        cfg = _seed_config(
            ref_data, mid_idx, antenna_type,
            f_min_mhz, f_max_mhz, spacing_mode)

        # Apply cached warm-start seed (overlay numeric params)
        cs = strat.get('cached_seed')
        if cs:
            for k, v in cs.items():
                if isinstance(v, (int, float)) and k in cfg:
                    cfg[k] = v

        # Apply strategy overrides
        if not strat['gain_coupling']:
            cfg['features']['gain_bw_coupling']['enabled'] = False
            # Fall back to mid-band anchor
            mid = ref_data[mid_idx]
            ma = mid['analysis']
            cfg['max_gain_dbi'] = round(
                max(r['analysis']['peak_gain'] for r in ref_data), 1)
            if antenna_type not in ("Omni", "Monopole") and ma['az_bw'] > 0:
                cfg['az_beamwidth_deg'] = float(ma['az_bw'])
            if ma['el_bw'] > 0:
                cfg['el_beamwidth_deg'] = float(ma['el_bw'])
            if mid['freq']:
                cfg['ref_frequency_mhz'] = mid['freq']

        if strat['bw_mode'] == 'three_point':
            for key in ('freq_dependent_bw_az', 'freq_dependent_bw_el'):
                feat = cfg['features'][key]
                if feat['enabled']:
                    feat['decay_mode'] = 'three_point'

        cfg['features']['vswr_rolloff']['enabled'] = strat['vswr']

        # Apply systematic feature overrides (from enumeration)
        fo = strat.get('feature_overrides')
        if fo:
            for feat_name, enabled in fo.items():
                if feat_name in cfg['features']:
                    cfg['features'][feat_name]['enabled'] = enabled

        if strat.get('perturb'):
            _perturb_config(cfg)

        # Optimise
        if optimize and _HAS_SCIPY and _HAS_NUMPY:
            # Stage 0: Principal-plane cut fitting (fast, constrains big params)
            cfg, _ = _optimize_cuts(cfg, ref_data, log)

            for _ in range(max_passes):
                cfg, imp_b = _optimize_config(cfg, ref_data, log)
                cfg, imp_s = _optimize_scaling(cfg, ref_data, log)

                # Check convergence against target RMS (using mid-band file)
                if _compute_fit_quality(cfg, ref_data[mid_idx])['rms_db'] <= effective_rms:
                    break

                if not imp_b and not imp_s:
                    break

        # Score against all files
        agg = _compute_aggregate_quality(cfg, ref_data)
        score = agg['agg_mean_pct_err']
        log(f"  Score: {score:.1f}% mean pct error, "
            f"{agg['agg_rms_db']:.2f} dB RMS")

        results.append({
            'cfg': cfg,
            'agg': agg,
            'score': score,
            'strategy': strat,
        })
        run_i += 1

        # In unlimited mode, report best-so-far and check target RMS
        if unlimited and results:
            best_so_far = min(results, key=lambda r: r['score'])
            log(f"  Best so far: {best_so_far['score']:.1f}% "
                f"(run {results.index(best_so_far) + 1})")
            q = _compute_fit_quality(
                best_so_far['cfg'], ref_data[mid_idx])
            if q['rms_db'] <= effective_rms:
                log(f"Target RMS {effective_rms} dB achieved — stopping.")
                break

    if not results:
        raise RuntimeError("No fitting runs completed (stopped too early).")

    # ── Pick best / ensemble averaging ─────────────────────
    results.sort(key=lambda r: r['score'])
    best = results[0]

    # Ensemble: average top-K parameter vectors (weighted by 1/score)
    # to smooth out local-minima artifacts.
    top_k = min(3, len(results))
    if top_k >= 2:
        top = results[:top_k]
        inv_scores = [1.0 / max(r['score'], 0.01) for r in top]
        total_w = sum(inv_scores)
        weights_k = [w / total_w for w in inv_scores]

        # Average the numeric config values
        ensemble_cfg = copy.deepcopy(best['cfg'])
        numeric_keys = [k for k in ensemble_cfg
                        if isinstance(ensemble_cfg[k], (int, float))
                        and k not in ('n_slices', 'antenna_type')]
        for key in numeric_keys:
            vals = [r['cfg'].get(key, ensemble_cfg[key]) for r in top]
            if all(isinstance(v, (int, float)) for v in vals):
                ensemble_cfg[key] = sum(v * w for v, w in zip(vals, weights_k))
                if isinstance(best['cfg'][key], int):
                    ensemble_cfg[key] = round(ensemble_cfg[key])
                else:
                    prec = 3 if 'wavelength' in key or 'efficiency' in key else 1
                    ensemble_cfg[key] = round(ensemble_cfg[key], prec)

        # Score the ensemble — only use it if it's actually better
        ens_agg = _compute_aggregate_quality(ensemble_cfg, ref_data)
        ens_score = ens_agg['agg_mean_pct_err']
        if ens_score < best['score']:
            log(f"Ensemble (top-{top_k}) improved: "
                f"{best['score']:.1f}% → {ens_score:.1f}%")
            best_cfg = ensemble_cfg
            best_agg = ens_agg
        else:
            best_cfg = best['cfg']
            best_agg = best['agg']
    else:
        best_cfg = best['cfg']
        best_agg = best['agg']

    log(f"\n{len(results)} run(s) completed. "
        f"Best: {best['strategy']['label']} ({best['score']:.1f}%)")

    # Save to warm-start cache for future fits
    _save_to_fit_cache(
        antenna_type, f_min_mhz, f_max_mhz,
        best_cfg, best['score'])

    quality = _compute_fit_quality(best_cfg, ref_data[mid_idx])

    # Build strategy summary for report
    strat_summary = []
    for i, r in enumerate(results):
        mark = " *best" if r is best else ""
        strat_summary.append(
            f"  {i+1:<4} {r['strategy']['label']:<30} "
            f"{r['agg']['agg_mean_pct_err']:>6.1f}%  "
            f"{r['agg']['agg_rms_db']:>7.2f}{mark}")

    report = _build_report(
        best_cfg, ref_data, mid_idx, quality, antenna_type, True,
        agg_quality=best_agg,
        strategy_summary=strat_summary,
    )

    return {
        'config': best_cfg,
        'quality': quality,
        'agg_quality': best_agg,
        'report': report,
        'strategy_results': results,
    }


# ===================================================================
#  BATCH FITTING
# ===================================================================

def batch_fit(
    parent_dir: str,
    output_dir: str,
    n_runs: int = 0,
    target_rms: float = 0.0,
    progress_cb=None,
    stop_event=None,
) -> dict:
    """Fit many pattern sets from subfolders, generate patterns, and compare.

    Each immediate subfolder of *parent_dir* is treated as one pattern
    set.  The antenna type and frequency range are auto-detected from
    a ``generation_config.json`` in the subfolder (preferred) or from
    filenames (fallback).

    For each set the pipeline is:

    1. Auto-detect type / frequency range
    2. Fit via :func:`fit_parameters_multirun`
    3. Save ``fitted_config.json``
    4. Generate patterns from the fitted config
    5. Compare generated vs. original patterns

    A detailed per-set and grand summary report is produced.

    Args:
        parent_dir:  Directory whose subfolders contain pattern sets.
        output_dir:  Where to write fitted configs, generated patterns,
                     and the final report.
        n_runs:      Runs per set.  0 = ``2 × recommended_runs(type)``
                     (auto-default).
        target_rms:  Per-set RMS target (dB).  0 = use per-type default.
        progress_cb: ``callback(message: str)`` for progress updates.
        stop_event:  ``threading.Event`` — set to abort.

    Returns:
        Dict with keys ``'results'`` (list of per-set dicts),
        ``'report'`` (full text report), and ``'report_path'``
        (path to the saved report file).
    """
    import json
    import time
    from datetime import datetime

    def log(msg):
        logger.info(msg)
        if progress_cb:
            progress_cb(msg)

    def _stopped():
        return stop_event is not None and stop_event.is_set()

    # ── Discover subfolders ───────────────────────────────
    if not os.path.isdir(parent_dir):
        raise ValueError(f"Parent directory not found: {parent_dir}")

    subdirs = sorted([
        d for d in os.listdir(parent_dir)
        if os.path.isdir(os.path.join(parent_dir, d))
    ])
    if not subdirs:
        raise ValueError(f"No subfolders found in: {parent_dir}")

    log(f"Found {len(subdirs)} pattern set(s) in {parent_dir}")
    os.makedirs(output_dir, exist_ok=True)

    set_results = []
    t_batch_start = time.time()

    for si, subdir_name in enumerate(subdirs):
        if _stopped():
            log("\nStop requested — aborting batch.")
            break

        subdir_path = os.path.join(parent_dir, subdir_name)
        log(f"\n{'='*60}")
        log(f"SET {si+1}/{len(subdirs)}: {subdir_name}")
        log(f"{'='*60}")

        # ── Collect pattern files ─────────────────────────
        pattern_files = sorted([
            os.path.join(subdir_path, f) for f in os.listdir(subdir_path)
            if f.lower().endswith(('.csv', '.dat'))
            and ('copol' in f.lower() or 'xpol' not in f.lower())
        ])
        # Filter to copol-only if copol files exist
        copol_files = [f for f in pattern_files if 'copol' in os.path.basename(f).lower()]
        if copol_files:
            pattern_files = copol_files

        if not pattern_files:
            log(f"  Skipping — no pattern files found.")
            set_results.append({
                'name': subdir_name, 'status': 'skipped',
                'reason': 'no pattern files',
            })
            continue

        log(f"  {len(pattern_files)} pattern file(s)")

        # ── Auto-detect type / freq from generation_config.json ──
        config_path = os.path.join(subdir_path, 'generation_config.json')
        antenna_type = None
        f_min = None
        f_max = None

        if os.path.isfile(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as fp:
                    gen_cfg = json.load(fp)
                antenna_type = gen_cfg.get('antenna_type')
                f_min = gen_cfg.get('f_min_mhz')
                f_max = gen_cfg.get('f_max_mhz')
                log(f"  Config detected: {antenna_type}, "
                    f"{f_min}-{f_max} MHz")
            except Exception as exc:
                log(f"  Warning: could not read config: {exc}")

        # ── Fallback: parse filenames ─────────────────────
        if not antenna_type or f_min is None or f_max is None:
            from core.io import extract_freq_from_filename
            freqs_parsed = []
            type_guess = None
            for fpath in pattern_files:
                fname = os.path.basename(fpath)
                freq = extract_freq_from_filename(fname)
                if freq is not None:
                    freqs_parsed.append(freq)
                # Guess type from prefix (first token before underscore)
                if type_guess is None:
                    prefix = fname.split('_')[0].upper()
                    known = {
                        'LPDA': 'LPDA', 'MONOPOLE': 'Monopole',
                        'OMNI': 'Omni', 'HORN': 'Horn',
                        'PANEL': 'Panel', 'DISH': 'Dish',
                        'ARRAY': 'Array',
                    }
                    if prefix in known:
                        type_guess = known[prefix]

            if freqs_parsed:
                if f_min is None:
                    f_min = min(freqs_parsed)
                if f_max is None:
                    f_max = max(freqs_parsed)
            if antenna_type is None:
                antenna_type = type_guess or 'LPDA'

            if f_min is None or f_max is None:
                log(f"  Skipping — cannot determine frequency range.")
                set_results.append({
                    'name': subdir_name, 'status': 'skipped',
                    'reason': 'unknown frequency range',
                })
                continue

            log(f"  Filename fallback: {antenna_type}, "
                f"{f_min}-{f_max} MHz")

        # ── Determine runs ────────────────────────────────
        if n_runs == 0:
            rec, _ = recommended_runs(antenna_type)
            effective_runs = rec * 2
        else:
            effective_runs = n_runs

        effective_target = target_rms if target_rms > 0 else type_target_rms(antenna_type)

        log(f"  Fitting: {effective_runs} runs, "
            f"target RMS {effective_target:.1f} dB")

        # ── Fit ───────────────────────────────────────────
        t_fit_start = time.time()
        try:
            fit_result = fit_parameters_multirun(
                reference_files=pattern_files,
                antenna_type=antenna_type,
                f_min_mhz=f_min,
                f_max_mhz=f_max,
                n_runs=effective_runs,
                optimize=True,
                max_passes=3,
                target_rms=effective_target,
                progress_cb=progress_cb,
                stop_event=stop_event,
            )
        except Exception as exc:
            log(f"  Fitting FAILED: {exc}")
            set_results.append({
                'name': subdir_name, 'status': 'error',
                'reason': str(exc),
            })
            continue
        t_fit_elapsed = time.time() - t_fit_start

        fitted_cfg = fit_result['config']
        quality = fit_result.get('quality', {})
        agg_quality = fit_result.get('agg_quality', {})

        log(f"  Fit complete in {t_fit_elapsed:.1f}s — "
            f"RMS {quality.get('rms_db', '?')} dB, "
            f"Pct {agg_quality.get('agg_mean_pct_err', '?')}%")

        # ── Save fitted config ────────────────────────────
        set_output_dir = os.path.join(output_dir, subdir_name)
        os.makedirs(set_output_dir, exist_ok=True)

        fitted_cfg_path = os.path.join(set_output_dir, 'fitted_config.json')
        with open(fitted_cfg_path, 'w', encoding='utf-8') as fp:
            json.dump(fitted_cfg, fp, indent=2, default=str)
        log(f"  Saved: {fitted_cfg_path}")

        # ── Generate patterns from fitted config ──────────
        log(f"  Generating patterns from fitted config...")
        gen_cfg = copy.deepcopy(fitted_cfg)
        gen_cfg['output_dir'] = set_output_dir
        gen_cfg['noise_range_db'] = 0.0  # clean patterns for comparison

        from config import generate_frequencies
        gen_freqs = generate_frequencies(
            gen_cfg['f_min_mhz'], gen_cfg['f_max_mhz'],
            gen_cfg.get('n_slices', len(pattern_files)),
            gen_cfg.get('freq_spacing', 'log'),
        )

        import io as _io
        from core.engine import run_generation
        buf = _io.StringIO()
        gen_output_dir = run_generation(gen_cfg, gen_freqs, writer=buf)

        # ── Compare original vs generated patterns ────────
        log(f"  Comparing original vs. fitted patterns...")
        comparison = _compare_pattern_sets(
            subdir_path, gen_output_dir, pattern_files, progress_cb)

        set_results.append({
            'name': subdir_name,
            'status': 'ok',
            'antenna_type': antenna_type,
            'f_min_mhz': f_min,
            'f_max_mhz': f_max,
            'n_files': len(pattern_files),
            'n_runs': effective_runs,
            'fit_time_s': round(t_fit_elapsed, 1),
            'quality': quality,
            'agg_quality': agg_quality,
            'fitted_cfg_path': fitted_cfg_path,
            'gen_output_dir': gen_output_dir,
            'comparison': comparison,
            'fit_report': fit_result.get('report', ''),
        })

    # ── Build grand report ────────────────────────────────
    t_total = time.time() - t_batch_start
    report = _build_batch_report(set_results, parent_dir, t_total)

    report_path = os.path.join(output_dir, 'batch_fit_report.txt')
    with open(report_path, 'w', encoding='utf-8') as fp:
        fp.write(report)
    log(f"\nReport saved: {report_path}")
    log(f"Total batch time: {t_total:.1f}s")

    return {
        'results': set_results,
        'report': report,
        'report_path': report_path,
    }


def _compare_pattern_sets(
    original_dir: str,
    generated_dir: str,
    original_files: list[str],
    progress_cb=None,
) -> dict:
    """Compare original pattern files against generated ones.

    Matches files by frequency (parsed from filenames).  Returns a dict
    with per-frequency comparison metrics and summary statistics.
    """
    from core.io import extract_freq_from_filename, read_pattern_csv
    from analysis.analyzer import analyze_from_data

    # Build freq→file maps
    orig_by_freq = {}
    for fpath in original_files:
        freq = extract_freq_from_filename(fpath)
        if freq is not None:
            orig_by_freq[freq] = fpath

    gen_files = sorted([
        os.path.join(generated_dir, f) for f in os.listdir(generated_dir)
        if f.lower().endswith(('.csv', '.dat'))
        and 'copol' in f.lower()
    ])
    gen_by_freq = {}
    for fpath in gen_files:
        freq = extract_freq_from_filename(fpath)
        if freq is not None:
            gen_by_freq[freq] = fpath

    # Match by closest frequency
    matched = []
    for o_freq, o_path in sorted(orig_by_freq.items()):
        if not gen_by_freq:
            break
        g_freq = min(gen_by_freq.keys(), key=lambda f: abs(f - o_freq))
        if abs(g_freq - o_freq) / max(o_freq, 1) < 0.05:  # within 5%
            matched.append((o_freq, o_path, gen_by_freq.pop(g_freq)))

    if not matched:
        return {'status': 'no_matches', 'per_freq': [], 'summary': {}}

    per_freq = []
    for freq, o_path, g_path in matched:
        try:
            o_az, o_el, o_data = read_pattern_csv(o_path)
            g_az, g_el, g_data = read_pattern_csv(g_path)
            o_analysis = analyze_from_data(o_az, o_el, o_data)
            g_analysis = analyze_from_data(g_az, g_el, g_data)

            def pct(a, b):
                if a == 0:
                    return 0.0 if b == 0 else float('inf')
                return (b - a) / abs(a) * 100.0

            # Full-pattern RMS comparison (dB)
            if _HAS_NUMPY:
                import numpy as _np
                o_arr = _np.array(o_data)
                g_arr = _np.array(g_data)
                # May have different grid sizes — use min dimensions
                r = min(o_arr.shape[0], g_arr.shape[0])
                c = min(o_arr.shape[1], g_arr.shape[1])
                diff = o_arr[:r, :c] - g_arr[:r, :c]
                rms_db = float(_np.sqrt(_np.mean(diff ** 2)))
                max_err_db = float(_np.max(_np.abs(diff)))
            else:
                rms_db = 0.0
                max_err_db = 0.0

            per_freq.append({
                'freq_mhz': freq,
                'rms_db': round(rms_db, 2),
                'max_err_db': round(max_err_db, 2),
                'peak_gain_orig': round(o_analysis['peak_gain'], 2),
                'peak_gain_gen': round(g_analysis['peak_gain'], 2),
                'peak_gain_pct': round(pct(o_analysis['peak_gain'], g_analysis['peak_gain']), 2),
                'bore_gain_orig': round(o_analysis.get('bore_gain', 0), 2),
                'bore_gain_gen': round(g_analysis.get('bore_gain', 0), 2),
                'bore_gain_pct': round(pct(o_analysis.get('bore_gain', 0), g_analysis.get('bore_gain', 0)), 2),
                'az_bw_orig': o_analysis.get('az_bw', 'N/A'),
                'az_bw_gen': g_analysis.get('az_bw', 'N/A'),
                'el_bw_orig': o_analysis.get('el_bw', 'N/A'),
                'el_bw_gen': g_analysis.get('el_bw', 'N/A'),
                'min_gain_orig': round(o_analysis.get('min_gain', 0), 2),
                'min_gain_gen': round(g_analysis.get('min_gain', 0), 2),
            })
        except Exception as exc:
            per_freq.append({
                'freq_mhz': freq,
                'error': str(exc),
            })

    # Summary stats
    valid = [p for p in per_freq if 'error' not in p]
    summary = {}
    if valid:
        summary['avg_rms_db'] = round(sum(p['rms_db'] for p in valid) / len(valid), 2)
        summary['max_rms_db'] = round(max(p['rms_db'] for p in valid), 2)
        summary['avg_peak_pct'] = round(
            sum(abs(p['peak_gain_pct']) for p in valid) / len(valid), 2)
        summary['max_peak_pct'] = round(
            max(abs(p['peak_gain_pct']) for p in valid), 2)
        summary['avg_bore_pct'] = round(
            sum(abs(p['bore_gain_pct']) for p in valid) / len(valid), 2)
        summary['n_matched'] = len(valid)
        summary['n_errors'] = len(per_freq) - len(valid)

    return {
        'status': 'ok',
        'per_freq': per_freq,
        'summary': summary,
    }


def _build_batch_report(
    set_results: list[dict],
    parent_dir: str,
    total_time: float,
) -> str:
    """Build the detailed batch fit report text."""
    from datetime import datetime
    lines = []
    w = 78

    lines.append("=" * w)
    lines.append("  BATCH FIT REPORT")
    lines.append("=" * w)
    lines.append(f"  Generated:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Source:      {parent_dir}")
    lines.append(f"  Total sets:  {len(set_results)}")
    ok_sets = [r for r in set_results if r.get('status') == 'ok']
    skip_sets = [r for r in set_results if r.get('status') == 'skipped']
    err_sets = [r for r in set_results if r.get('status') == 'error']
    lines.append(f"  Completed:   {len(ok_sets)}  |  "
                 f"Skipped: {len(skip_sets)}  |  "
                 f"Errors: {len(err_sets)}")
    lines.append(f"  Total time:  {total_time:.1f}s")

    # ── Grand Summary Table ───────────────────────────────
    if ok_sets:
        lines.append(f"\n{'='*w}")
        lines.append("  GRAND SUMMARY")
        lines.append(f"{'='*w}")
        hdr = (f"  {'Set Name':<25} {'Type':<8} {'Band (MHz)':<16} "
               f"{'Files':>5} {'RMS dB':>7} {'Pct%':>6} "
               f"{'CmpRMS':>7} {'Time':>6}")
        lines.append(hdr)
        lines.append(f"  {'-'*(w-2)}")

        for r in ok_sets:
            q = r.get('agg_quality', {})
            comp = r.get('comparison', {}).get('summary', {})
            band = f"{r['f_min_mhz']:.0f}-{r['f_max_mhz']:.0f}"
            cmp_rms = f"{comp.get('avg_rms_db', 0):.2f}" if comp else "N/A"
            lines.append(
                f"  {r['name']:<25} {r['antenna_type']:<8} {band:<16} "
                f"{r['n_files']:>5} "
                f"{q.get('agg_rms_db', 0):>7.2f} "
                f"{q.get('agg_mean_pct_err', 0):>6.1f} "
                f"{cmp_rms:>7} "
                f"{r['fit_time_s']:>5.0f}s"
            )

        # Averages row
        if len(ok_sets) > 1:
            avg_rms = sum(r.get('agg_quality', {}).get('agg_rms_db', 0)
                          for r in ok_sets) / len(ok_sets)
            avg_pct = sum(r.get('agg_quality', {}).get('agg_mean_pct_err', 0)
                          for r in ok_sets) / len(ok_sets)
            comp_vals = [r.get('comparison', {}).get('summary', {}).get('avg_rms_db', 0)
                         for r in ok_sets]
            avg_cmp = sum(comp_vals) / len(comp_vals) if comp_vals else 0
            lines.append(f"  {'-'*(w-2)}")
            lines.append(
                f"  {'AVERAGE':<25} {'':8} {'':16} "
                f"{'':>5} {avg_rms:>7.2f} {avg_pct:>6.1f} "
                f"{avg_cmp:>7.2f} {'':>6}"
            )

    # ── Skipped / Error sets ──────────────────────────────
    if skip_sets:
        lines.append(f"\n  SKIPPED SETS:")
        for r in skip_sets:
            lines.append(f"    {r['name']}: {r.get('reason', 'unknown')}")
    if err_sets:
        lines.append(f"\n  FAILED SETS:")
        for r in err_sets:
            lines.append(f"    {r['name']}: {r.get('reason', 'unknown')}")

    # ── Detailed Per-Set Reports ──────────────────────────
    for r in ok_sets:
        lines.append(f"\n\n{'#'*w}")
        lines.append(f"  SET: {r['name']}")
        lines.append(f"{'#'*w}")
        lines.append(f"  Antenna Type:    {r['antenna_type']}")
        lines.append(f"  Frequency Range: {r['f_min_mhz']:.1f} - {r['f_max_mhz']:.1f} MHz")
        lines.append(f"  Pattern Files:   {r['n_files']}")
        lines.append(f"  Fitting Runs:    {r['n_runs']}")
        lines.append(f"  Fit Time:        {r['fit_time_s']:.1f}s")
        lines.append(f"  Config Saved:    {r['fitted_cfg_path']}")
        lines.append(f"  Generated Dir:   {r.get('gen_output_dir', 'N/A')}")

        # Fit quality metrics
        q = r.get('quality', {})
        aq = r.get('agg_quality', {})
        lines.append(f"\n  FIT QUALITY (mid-band):")
        lines.append(f"  {'-'*40}")
        lines.append(f"    RMS Error:       {q.get('rms_db', 'N/A')} dB")
        lines.append(f"    Max Error:       {q.get('max_err_db', 'N/A')} dB")
        lines.append(f"    Beam RMS:        {q.get('beam_rms_db', 'N/A')} dB")
        lines.append(f"    Mean Pct Error:  {q.get('mean_pct_err', 'N/A')}%")
        lines.append(f"    Beam Pct Error:  {q.get('beam_pct_err', 'N/A')}%")

        lines.append(f"\n  FIT QUALITY (aggregate across all files):")
        lines.append(f"  {'-'*40}")
        lines.append(f"    Agg RMS:         {aq.get('agg_rms_db', 'N/A')} dB")
        lines.append(f"    Agg Max Error:   {aq.get('agg_max_err_db', 'N/A')} dB")
        lines.append(f"    Agg Mean Pct:    {aq.get('agg_mean_pct_err', 'N/A')}%")
        lines.append(f"    Agg Beam Pct:    {aq.get('agg_beam_pct_err', 'N/A')}%")

        # Per-file fit quality
        pf = aq.get('per_file', [])
        if pf:
            lines.append(f"\n  PER-FILE FIT QUALITY:")
            lines.append(f"  {'-'*72}")
            lines.append(
                f"    {'Freq (MHz)':>10}  {'File':<30} "
                f"{'RMS dB':>7} {'MaxErr':>7} {'Pct%':>6} {'BeamPct':>8}"
            )
            lines.append(f"    {'-'*68}")
            for pq in pf:
                freq_s = f"{pq.get('freq', 0):.1f}" if pq.get('freq') else "?"
                lines.append(
                    f"    {freq_s:>10}  {pq.get('file', '?'):<30} "
                    f"{pq.get('rms_db', 0):>7.2f} "
                    f"{pq.get('max_err_db', 0):>7.2f} "
                    f"{pq.get('mean_pct_err', 0):>6.1f} "
                    f"{pq.get('beam_pct_err', 0):>8.1f}"
                )

        # Pattern comparison (original vs generated)
        comp = r.get('comparison', {})
        pfreq = comp.get('per_freq', [])
        if pfreq:
            lines.append(f"\n  ORIGINAL vs. GENERATED COMPARISON:")
            lines.append(f"  {'-'*72}")
            lines.append(
                f"    {'Freq':>8}  {'RMS dB':>7} {'MaxErr':>7} "
                f"{'PkOrig':>7} {'PkGen':>7} {'Pk%':>6}  "
                f"{'BrOrig':>7} {'BrGen':>7} {'Br%':>6}"
            )
            lines.append(f"    {'-'*68}")
            for pf_entry in pfreq:
                if 'error' in pf_entry:
                    lines.append(
                        f"    {pf_entry['freq_mhz']:>8.1f}  "
                        f"ERROR: {pf_entry['error']}")
                    continue
                lines.append(
                    f"    {pf_entry['freq_mhz']:>8.1f}  "
                    f"{pf_entry['rms_db']:>7.2f} "
                    f"{pf_entry['max_err_db']:>7.2f} "
                    f"{pf_entry['peak_gain_orig']:>7.2f} "
                    f"{pf_entry['peak_gain_gen']:>7.2f} "
                    f"{pf_entry['peak_gain_pct']:>6.1f}  "
                    f"{pf_entry['bore_gain_orig']:>7.2f} "
                    f"{pf_entry['bore_gain_gen']:>7.2f} "
                    f"{pf_entry['bore_gain_pct']:>6.1f}"
                )

            # Beamwidth comparison table
            lines.append(f"\n    {'Freq':>8}  "
                         f"{'AzBW Orig':>10} {'AzBW Gen':>10}  "
                         f"{'ElBW Orig':>10} {'ElBW Gen':>10}  "
                         f"{'MinOrig':>8} {'MinGen':>8}")
            lines.append(f"    {'-'*68}")
            for pf_entry in pfreq:
                if 'error' in pf_entry:
                    continue
                az_o = pf_entry.get('az_bw_orig', 'N/A')
                az_g = pf_entry.get('az_bw_gen', 'N/A')
                el_o = pf_entry.get('el_bw_orig', 'N/A')
                el_g = pf_entry.get('el_bw_gen', 'N/A')
                az_o_s = f"{az_o}" if isinstance(az_o, str) else f"{az_o:.1f}"
                az_g_s = f"{az_g}" if isinstance(az_g, str) else f"{az_g:.1f}"
                el_o_s = f"{el_o}" if isinstance(el_o, str) else f"{el_o:.1f}"
                el_g_s = f"{el_g}" if isinstance(el_g, str) else f"{el_g:.1f}"
                lines.append(
                    f"    {pf_entry['freq_mhz']:>8.1f}  "
                    f"{az_o_s:>10} {az_g_s:>10}  "
                    f"{el_o_s:>10} {el_g_s:>10}  "
                    f"{pf_entry.get('min_gain_orig', 0):>8.2f} "
                    f"{pf_entry.get('min_gain_gen', 0):>8.2f}"
                )

            # Comparison summary
            cs = comp.get('summary', {})
            if cs:
                lines.append(f"\n  COMPARISON SUMMARY:")
                lines.append(f"  {'-'*40}")
                lines.append(f"    Matched Frequencies: {cs.get('n_matched', 0)}")
                lines.append(f"    Avg Pattern RMS:     {cs.get('avg_rms_db', 0):.2f} dB")
                lines.append(f"    Max Pattern RMS:     {cs.get('max_rms_db', 0):.2f} dB")
                lines.append(f"    Avg |Peak Gain %|:   {cs.get('avg_peak_pct', 0):.2f}%")
                lines.append(f"    Max |Peak Gain %|:   {cs.get('max_peak_pct', 0):.2f}%")
                lines.append(f"    Avg |Bore Gain %|:   {cs.get('avg_bore_pct', 0):.2f}%")
                if cs.get('n_errors', 0):
                    lines.append(f"    Comparison Errors:   {cs['n_errors']}")

        # Include the per-set fit report (from fit_parameters_multirun)
        fit_rpt = r.get('fit_report', '')
        if fit_rpt:
            lines.append(f"\n  DETAILED FIT REPORT:")
            lines.append(f"  {'-'*40}")
            for rpt_line in fit_rpt.split('\n'):
                lines.append(f"    {rpt_line}")

    lines.append(f"\n{'='*w}")
    lines.append(f"  END OF BATCH FIT REPORT")
    lines.append(f"{'='*w}")

    return "\n".join(lines)


# ===================================================================
#  FLEXIBLE FREQUENCY EXTRACTION
# ===================================================================

def _extract_freq_flexible(fpath: str) -> float | None:
    """Try to extract a frequency from any reasonable filename.

    Handles common legacy patterns such as:
    - ``antenna_100MHz.csv``, ``pattern_2p4GHz.dat``
    - ``100_MHz_copol.csv``, ``2550MHz.csv``
    - ``slice_100.csv`` (bare number, assumed MHz)

    Returns frequency in MHz, or ``None``.
    """
    import re
    base = os.path.splitext(os.path.basename(fpath))[0]

    # Separator: optional underscores, hyphens, or whitespace
    _sep = r'[\s_\-]*'

    # Pattern 1: number followed by GHz (convert to MHz)
    m = re.search(rf'(\d+(?:[p.]\d+)?){_sep}GHz', base, re.IGNORECASE)
    if m:
        num = m.group(1).replace('p', '.')
        try:
            return float(num) * 1000.0
        except ValueError:
            pass

    # Pattern 2: number followed by MHz
    m = re.search(rf'(\d+(?:[p.]\d+)?){_sep}MHz', base, re.IGNORECASE)
    if m:
        num = m.group(1).replace('p', '.')
        try:
            return float(num)
        except ValueError:
            pass

    # Pattern 3: bare number in the filename (assume MHz)
    # Pick the largest number that looks like a frequency
    candidates = re.findall(r'(\d+(?:\.\d+)?)', base)
    if candidates:
        nums = [float(c) for c in candidates]
        # Heuristic: pick the number most likely to be a frequency
        # (typically the largest value that isn't a huge index)
        plausible = [n for n in nums if 0.1 <= n <= 1e6]
        if plausible:
            return max(plausible)

    return None


# ===================================================================
#  ANTENNA TYPE DETECTION
# ===================================================================

def _detect_antenna_type(analysis: dict) -> str:
    """Heuristic antenna type detection from pattern measurements."""
    az_bw = analysis.get('az_bw', 0)
    el_bw = analysis.get('el_bw', 0)
    peak = analysis.get('peak_gain', 0)
    ftb = analysis.get('ftb')

    # Omnidirectional patterns
    if az_bw == 0 or az_bw >= 300:
        return "Monopole" if el_bw < 90 else "Omni"

    # High-gain narrow beam → Dish
    if az_bw < 15 and el_bw < 15 and peak > 20:
        return "Dish"

    # Very high FTB with narrow beam → Horn
    if ftb is not None and ftb > 22 and az_bw < 60:
        return "Horn"

    # Strongly asymmetric beamwidths → Panel
    if az_bw > 0 and el_bw > 0:
        ratio = max(az_bw, el_bw) / max(min(az_bw, el_bw), 1)
        if ratio > 2.0:
            return "Panel"

    return "LPDA"


def _detect_ground_reflection(mid_ref: dict) -> bool:
    """Heuristic to detect ground reflection from pattern data."""
    # Ground reflection typically creates strong interference lobes
    # in the elevation pattern, appearing as high sidelobes.
    analysis = mid_ref['analysis']
    sll = analysis.get('first_sll')
    
    if not sll or sll.get('relative') is None or sll['relative'] < -9.0:
        return False

    # Check if the high sidelobe is specifically in the Elevation plane.
    az_axis = mid_ref['az']
    el_axis = mid_ref['el']
    data = mid_ref['data']
    
    idx_az0 = min(range(len(az_axis)), key=lambda i: abs(az_axis[i]))
    idx_el0 = min(range(len(el_axis)), key=lambda i: abs(el_axis[i]))
    
    az_cut = data[idx_el0]
    el_cut = [row[idx_az0] for row in data]
    
    def get_approx_sll(cut, axis, bw):
        peak = max(cut)
        mask = bw * 0.8
        candidates = [val for i, val in enumerate(cut) if abs(axis[i]) > mask]
        return (max(candidates) - peak) if candidates else -99.0

    az_bw = analysis.get('az_bw') or 60.0
    el_bw = analysis.get('el_bw') or 60.0
    
    az_sll = get_approx_sll(az_cut, az_axis, az_bw)
    el_sll = get_approx_sll(el_cut, el_axis, el_bw)
    
    # If Elevation SLL is high (> -6 dB) and significantly higher than Az SLL
    if el_sll > -6.0 and el_sll > (az_sll + 2.0):
        return True
    return False


def _detect_spacing(freqs: list[float]) -> str:
    """Determine if a list of frequencies is Linear or Log spaced."""
    if len(freqs) < 3:
        return "linear"
    
    # Sort to ensure diffs are valid
    freqs = sorted(freqs)
    
    # Linear: diffs are constant
    diffs = np.diff(freqs) if _HAS_NUMPY else [freqs[i+1]-freqs[i] for i in range(len(freqs)-1)]
    
    # Log: ratios are constant (diffs of logs are constant)
    import math
    log_freqs = [math.log(f) for f in freqs]
    log_diffs = np.diff(log_freqs) if _HAS_NUMPY else [log_freqs[i+1]-log_freqs[i] for i in range(len(log_freqs)-1)]
    
    # Calculate Coefficient of Variation (std / mean) for both
    def cv(arr):
        return np.std(arr) / np.mean(arr) if _HAS_NUMPY else 0.0 # Fallback if no numpy

    if _HAS_NUMPY:
        return "log" if cv(log_diffs) < cv(diffs) else "linear"
    
    return "linear" # Default fallback


def _estimate_element_length(ref_entry: dict) -> float:
    """Estimate monopole element length from the elevation pattern shape.

    Searches for the first null (deep minimum) in the elevation pattern
    to infer the electrical element length.  Quarter-wave monopoles
    have no nulls before 90°; half-wave dipoles have a narrower peak.
    Longer elements produce nulls at angles that depend on kL.

    Falls back to 0.25 (quarter-wave) if no null is detected.
    """
    el = ref_entry['el']
    data = ref_entry['data']
    az = ref_entry['az']

    # Get the az=0 elevation cut
    try:
        az0 = az.index(0.0)
    except ValueError:
        az0 = min(range(len(az)), key=lambda i: abs(az[i]))

    el_cut = [data[i][az0] for i in range(len(el))]
    peak_gain = max(el_cut)

    # Look for the 3dB beamwidth of the elevation cut to estimate length
    # Narrower el_bw → longer element
    threshold = peak_gain - 3.0
    peak_idx = el_cut.index(peak_gain)

    # Walk outward from peak to find 3dB drop angle
    half_bw = 90.0
    for i in range(peak_idx + 1, len(el_cut)):
        if el_cut[i] < threshold:
            half_bw = abs(el[i] - el[peak_idx])
            break

    # Map beamwidth to approximate element length:
    #   L=0.25λ → el_bw ≈ 78°  (half_bw ≈ 39°)
    #   L=0.50λ → el_bw ≈ 47°  (half_bw ≈ 23.5°)
    #   L=0.625λ → el_bw ≈ 35° (half_bw ≈ 17.5°)
    if half_bw >= 35:
        return 0.25
    elif half_bw >= 20:
        # Linear interpolation between 0.25 and 0.5
        t = (35.0 - half_bw) / (35.0 - 20.0)
        return 0.25 + t * 0.25
    elif half_bw >= 15:
        t = (20.0 - half_bw) / (20.0 - 15.0)
        return 0.50 + t * 0.125
    else:
        return 0.625


# ===================================================================
#  GAIN-VS-FREQUENCY DETECTION
# ===================================================================

def _detect_gain_slope(
    ref_data: list[dict],
) -> tuple[float | None, float | None]:
    """Regress peak_gain vs log2(freq) across reference files.

    Returns ``(slope_db_per_octave, gain_at_fmax)`` or ``(None, None)``
    if fewer than 3 valid data points.
    """
    pairs = [
        (r['freq'], r['analysis']['peak_gain'])
        for r in ref_data
        if r['freq'] is not None and r['freq'] > 0
    ]
    if len(pairs) < 3:
        return None, None

    xs = [math.log2(f) for f, _ in pairs]
    ys = [g for _, g in pairs]
    n = len(xs)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x * y for x, y in zip(xs, ys))
    sum_x2 = sum(x * x for x in xs)
    denom = n * sum_x2 - sum_x ** 2
    if abs(denom) < 1e-12:
        return None, None

    slope = (n * sum_xy - sum_x * sum_y) / denom       # dB / octave
    intercept = (sum_y - slope * sum_x) / n

    # Gain at the highest frequency
    f_max_log2 = max(xs)
    gain_at_fmax = intercept + slope * f_max_log2

    return slope, gain_at_fmax


def _detect_vswr_rolloff(ref_data: list[dict]) -> bool:
    """Check if band-edge files show gain dips relative to neighbours."""
    sorted_refs = sorted(ref_data, key=lambda r: r['freq'] or 0)
    peaks = [r['analysis']['peak_gain'] for r in sorted_refs]

    if len(peaks) < 3:
        return False

    # Check if edges dip relative to their nearest inner neighbours
    if len(peaks) >= 5:
        low_edge_dip = peaks[0] < peaks[2] - 1.5
        high_edge_dip = peaks[-1] < peaks[-3] - 1.5
    else:
        # Fewer files — compare edges to the mid-band peak
        mid_peak = max(peaks[1:-1]) if len(peaks) > 2 else peaks[1]
        low_edge_dip = peaks[0] < mid_peak - 1.5
        high_edge_dip = peaks[-1] < mid_peak - 1.5

    return low_edge_dip or high_edge_dip


# ===================================================================
#  BW-VS-FREQUENCY EXPONENT FITTING
# ===================================================================

def _fit_bw_exponent(
    entries: list[dict],
    plane: str,
    ref_freq: float,
    base_bw: float,
    is_lpda: bool,
) -> tuple[float, float]:
    """Fit BW exponent model to measured beamwidth data.

    For non-LPDA: ``BW(f) = base_bw * (ref_freq / f) ^ exp``
    For LPDA:     ``BW(f) = base_bw * (1 + var * ((ref_freq / f)^exp - 1))``

    Returns ``(exponent, variation_factor)``.
    """
    freqs = [e['freq'] for e in entries if e[f'{plane}_bw'] > 0]
    bws = [e[f'{plane}_bw'] for e in entries if e[f'{plane}_bw'] > 0]

    if len(freqs) < 2 or base_bw <= 0:
        return 0.8, 0.4      # safe defaults

    if not is_lpda:
        # Single-parameter fit in log space:
        #   log(BW / base_bw) = exp * log(ref_freq / f)
        sum_xy, sum_x2 = 0.0, 0.0
        for f, bw in zip(freqs, bws):
            if f <= 0 or bw <= 0:
                continue
            x = math.log(ref_freq / f)
            y = math.log(bw / base_bw)
            sum_xy += x * y
            sum_x2 += x * x
        exp = sum_xy / max(sum_x2, 1e-12)
        return max(0.1, min(exp, 2.0)), 0.0

    # LPDA two-parameter fit: grid search over exp, linear solve for var
    best_exp, best_var, best_err = 0.5, 0.3, 1e9
    for exp_int in range(2, 31):          # exp from 0.10 to 1.50
        exp_try = exp_int * 0.05
        sum_num, sum_den = 0.0, 0.0
        for f, bw in zip(freqs, bws):
            if f <= 0:
                continue
            ratio_exp = (ref_freq / f) ** exp_try - 1.0
            residual = bw - base_bw
            term = base_bw * ratio_exp
            sum_num += residual * term
            sum_den += term * term
        var_try = sum_num / max(sum_den, 1e-12)
        var_try = max(0.0, min(var_try, 1.0))
        err = sum(
            (bw - base_bw * (1.0 + var_try * ((ref_freq / f) ** exp_try - 1.0))) ** 2
            for f, bw in zip(freqs, bws) if f > 0
        )
        if err < best_err:
            best_err = err
            best_exp = exp_try
            best_var = var_try

    return best_exp, best_var


# ===================================================================
#  WARM-START FIT HISTORY CACHE
# ===================================================================

_FIT_CACHE_FILE = os.path.join(
    os.path.expanduser("~"), ".antennaforge", "fit_cache.json")


def _load_fit_cache() -> list[dict]:
    """Load fit cache from disk.  Returns empty list on failure."""
    try:
        with open(_FIT_CACHE_FILE, "r") as f:
            import json
            return json.load(f)
    except (FileNotFoundError, ValueError, OSError):
        return []


def _save_to_fit_cache(
    antenna_type: str, f_min: float, f_max: float,
    cfg: dict, score: float,
) -> None:
    """Append a successful fit to the cache (keeps last 50 per type)."""
    import json
    cache = _load_fit_cache()

    entry = {
        'antenna_type': antenna_type,
        'f_min_mhz': f_min,
        'f_max_mhz': f_max,
        'score': score,
        'cfg': {k: v for k, v in cfg.items()
                if isinstance(v, (int, float, str, bool, type(None)))},
    }
    cache.append(entry)

    # Keep last 50 entries per type
    by_type = {}
    for e in cache:
        t = e.get('antenna_type', '')
        by_type.setdefault(t, []).append(e)
    trimmed = []
    for entries in by_type.values():
        trimmed.extend(entries[-50:])

    os.makedirs(os.path.dirname(_FIT_CACHE_FILE), exist_ok=True)
    try:
        with open(_FIT_CACHE_FILE, "w") as f:
            json.dump(trimmed, f, indent=1)
    except OSError:
        pass


def _find_cached_seed(
    antenna_type: str, f_min: float, f_max: float,
) -> dict | None:
    """Find a cached fit result for similar type and frequency range.

    Returns the cached config dict if a close match exists,
    else ``None``.  "Close" means same type and frequency range
    overlap of at least 50%.
    """
    cache = _load_fit_cache()
    best = None
    best_score = 1e9

    for entry in cache:
        if entry.get('antenna_type') != antenna_type:
            continue
        c_lo = entry.get('f_min_mhz', 0)
        c_hi = entry.get('f_max_mhz', 0)
        # Check overlap
        overlap_lo = max(f_min, c_lo)
        overlap_hi = min(f_max, c_hi)
        if overlap_hi <= overlap_lo:
            continue
        overlap = overlap_hi - overlap_lo
        span = max(f_max - f_min, c_hi - c_lo, 1e-6)
        if overlap / span < 0.5:
            continue
        score = entry.get('score', 1e9)
        if score < best_score:
            best_score = score
            best = entry.get('cfg')

    return best


# ===================================================================
#  MEASUREMENT-BASED CONFIG SEEDING
# ===================================================================

def _seed_config(
    ref_data: list[dict],
    mid_idx: int,
    antenna_type: str,
    f_min: float,
    f_max: float,
    spacing_mode: str = "linear",
) -> dict:
    """Build initial config dict directly from measurements."""
    from config import DEFAULT_CONFIG
    from antennas import get_antenna

    cfg = copy.deepcopy(DEFAULT_CONFIG)

    # Merge antenna-specific defaults
    try:
        antenna = get_antenna(antenna_type)
        for k, v in antenna.default_params().items():
            cfg[k] = v
    except KeyError:
        pass

    cfg['antenna_type'] = antenna_type

    mid = ref_data[mid_idx]
    a = mid['analysis']

    # ── Detect gain-vs-frequency trend ─────────────────────
    gain_slope, gain_at_fmax = _detect_gain_slope(ref_data)
    has_gain_coupling = (gain_slope is not None and gain_slope > 0.3)

    if has_gain_coupling:
        # Anchor at f_max: use highest-frequency file for base values
        cfg['features']['gain_bw_coupling']['enabled'] = True
        cfg['features']['gain_bw_coupling']['mode'] = 'independent'
        cfg['features']['gain_bw_coupling']['gain_rolloff_db_per_octave'] = (
            round(gain_slope, 2))
        cfg['ref_frequency_mhz'] = None       # engine defaults to f_max

        # Seed gain and beamwidths from highest-frequency file
        hi_ref = max(ref_data, key=lambda r: r['freq'] or 0)
        hi_a = hi_ref['analysis']
        cfg['max_gain_dbi'] = round(hi_a['peak_gain'], 1)

        if antenna_type in ("Omni", "Monopole"):
            cfg['az_beamwidth_deg'] = 360.0
        elif hi_a['az_bw'] > 0:
            cfg['az_beamwidth_deg'] = float(hi_a['az_bw'])

        if hi_a['el_bw'] > 0:
            cfg['el_beamwidth_deg'] = float(hi_a['el_bw'])
    else:
        # No coupling — use mid-band file (original behaviour)
        cfg['features']['gain_bw_coupling']['enabled'] = False
        all_peaks = [r['analysis']['peak_gain'] for r in ref_data]
        global_peak = max(all_peaks) if all_peaks else a['peak_gain']
        cfg['max_gain_dbi'] = round(global_peak, 1)

        if antenna_type in ("Omni", "Monopole"):
            cfg['az_beamwidth_deg'] = 360.0
        elif a['az_bw'] > 0:
            cfg['az_beamwidth_deg'] = float(a['az_bw'])

        if a['el_bw'] > 0:
            cfg['el_beamwidth_deg'] = float(a['el_bw'])

        mid_freq = mid['freq']
        if mid_freq:
            cfg['ref_frequency_mhz'] = mid_freq

    if a['ftb'] is not None and a['ftb'] > 0:
        cfg['ftb_ratio_db'] = round(a['ftb'], 1)

    # ── Frequency range ───────────────────────────────────
    freqs = [r['freq'] for r in ref_data if r['freq'] is not None]
    if freqs:
        cfg['f_min_mhz'] = min(freqs)
        cfg['f_max_mhz'] = max(freqs)
        cfg['n_slices'] = len(freqs)
        cfg['freq_spacing'] = spacing_mode

    # ── Angular grid from reference ───────────────────────
    az, el = mid['az'], mid['el']
    if len(az) > 1:
        cfg['az_step_deg'] = round(abs(az[1] - az[0]), 2)
    if len(el) > 1:
        cfg['el_step_deg'] = round(abs(el[1] - el[0]), 2)

    # ── Monopole element length estimation ─────────────────
    if antenna_type == "Monopole":
        cfg['element_length_wavelengths'] = _estimate_element_length(mid)

    # ── Sidelobes ─────────────────────────────────────────
    # Check measured sidelobe level for ALL types (including Monopole
    # and Omni — the generation engine can add sidelobes to any type).
    sll = a.get('first_sll')
    if sll and sll.get('relative'):
        val = -abs(sll['relative'])
        if val > -10.0:
            val = -20.0
        cfg['features']['sidelobes']['enabled'] = True
        cfg['features']['sidelobes']['first_sidelobe_db'] = round(val, 1)
    else:
        cfg['features']['sidelobes']['enabled'] = False

    # ── BW-vs-frequency scaling (multi-file) ──────────────
    # For omni antennas, az BW is fixed — disable az scaling
    if antenna_type in ("Omni", "Monopole"):
        cfg['features']['freq_dependent_bw_az']['enabled'] = False

    if len(ref_data) > 1:
        _estimate_bw_scaling(cfg, ref_data)

    # ── Clean fit: disable noise / asymmetry / ground ─────
    cfg['noise_range_db'] = 0.0
    cfg['features']['asymmetry']['enabled'] = False

    if _detect_ground_reflection(mid):
        cfg['features']['ground_reflection']['enabled'] = True
        cfg['features']['ground_reflection']['height_wavelengths'] = 1.5
        cfg['features']['ground_reflection']['reflection_coeff'] = 0.5
    else:
        cfg['features']['ground_reflection']['enabled'] = False

    cfg['features']['cross_pol']['enabled'] = False
    cfg['features']['pattern_breakup']['enabled'] = False

    # ── VSWR rolloff: enable if band-edge dip detected ─────
    if len(ref_data) >= 3 and _detect_vswr_rolloff(ref_data):
        cfg['features']['vswr_rolloff']['enabled'] = True
    else:
        cfg['features']['vswr_rolloff']['enabled'] = False

    return cfg


def _estimate_bw_scaling(cfg: dict, ref_data: list[dict]) -> None:
    """Estimate BW-vs-frequency behaviour from multi-file measurements.

    Defaults to exponent mode (physically motivated) rather than
    three-point Lagrange.  Falls back to percentage for 2-file case.
    """
    entries = []
    for r in ref_data:
        if r['freq'] is not None and r['freq'] > 0:
            entries.append({
                'freq': r['freq'],
                'az_bw': r['analysis']['az_bw'],
                'el_bw': r['analysis']['el_bw'],
            })

    if len(entries) < 2:
        return
    entries.sort(key=lambda e: e['freq'])

    ref_freq = cfg.get('ref_frequency_mhz') or cfg['f_max_mhz']
    is_lpda = cfg['antenna_type'] == 'LPDA'

    for plane, key in [('az', 'freq_dependent_bw_az'),
                       ('el', 'freq_dependent_bw_el')]:
        bws = [e[f'{plane}_bw'] for e in entries if e[f'{plane}_bw'] > 0]
        if not bws or max(bws) - min(bws) < 3:
            cfg['features'][key]['enabled'] = False
            continue

        cfg['features'][key]['enabled'] = True

        if len(entries) >= 3:
            # Fit the exponent model (physically motivated)
            ref_entry = min(entries, key=lambda e: abs(e['freq'] - ref_freq))
            base_bw = ref_entry[f'{plane}_bw']
            exp, var = _fit_bw_exponent(
                entries, plane, ref_freq, base_bw, is_lpda)

            cfg['features'][key]['decay_mode'] = 'exponent'
            cfg['features'][key]['scaling_exponent'] = round(exp, 2)
            if is_lpda:
                cfg['features'][key]['variation_factor'] = round(var, 2)

            # Also populate three-point values for multi-run fallback
            cfg['features'][key]['three_point_start_deg'] = float(
                entries[0][f'{plane}_bw'])
            mid_e = entries[len(entries) // 2]
            cfg['features'][key]['three_point_mid_deg'] = float(
                mid_e[f'{plane}_bw'])
            cfg['features'][key]['three_point_end_deg'] = float(
                entries[-1][f'{plane}_bw'])
        else:
            # Two files → percentage decay per octave
            f_ratio = entries[-1]['freq'] / max(entries[0]['freq'], 1e-6)
            bw_ratio = bws[-1] / max(bws[0], 0.1)
            if f_ratio > 1 and bw_ratio < 1:
                octaves = math.log2(f_ratio)
                pct = (1.0 - bw_ratio) / max(octaves, 0.01) * 100
                cfg['features'][key]['decay_mode'] = 'percentage'
                cfg['features'][key]['decay_pct_per_octave'] = round(pct, 1)


# ===================================================================
#  SCIPY OPTIMISATION
# ===================================================================

def _subsample_refs(ref_data: list[dict], n_target: int = 7) -> list[int]:
    """Pick *n_target* evenly-spaced indices from *ref_data*."""
    n = len(ref_data)
    if n <= n_target:
        return list(range(n))
    step = (n - 1) / (n_target - 1)
    return [round(i * step) for i in range(n_target)]


def _prepare_grid(ref_entry: dict, stride_deg: float = 5.0) -> dict:
    """Build a subsampled grid dict for one reference file."""
    az = ref_entry['az']
    el = ref_entry['el']
    az_step = abs(az[1] - az[0]) if len(az) > 1 else 1.0
    el_step = abs(el[1] - el[0]) if len(el) > 1 else 1.0
    az_stride = max(1, int(stride_deg / az_step))
    el_stride = max(1, int(stride_deg / el_step))
    return {
        'freq': ref_entry['freq'],
        'az': az[::az_stride],
        'el': el[::el_stride],
        'data': np.array(ref_entry['data'])[::el_stride, ::az_stride],
        'peak': ref_entry['analysis']['peak_gain'],
    }


def _estimate_noise_floor(grids: list[dict]) -> float:
    """Estimate measurement noise floor from reference data.

    Looks at the variance in low-gain regions (below peak - 25 dB)
    across all grids.  Returns the estimated noise standard deviation
    in dB.  Used for adaptive far-out weighting.
    """
    low_vals = []
    for g in grids:
        ref = g['data']
        peak = g['peak']
        mask = ref < peak - 25.0
        if np.any(mask):
            low_vals.append(np.std(ref[mask]))
    if low_vals:
        return float(np.mean(low_vals))
    return 5.0  # default: assume moderately noisy


def _extract_principal_cuts(ref_entry: dict) -> dict:
    """Extract az=0 and el=0 principal-plane cuts from a reference.

    Returns dict with 'az_cut' (gain vs el), 'el_cut' (gain vs az),
    and the corresponding angle arrays.
    """
    az = ref_entry['az']
    el = ref_entry['el']
    data = ref_entry['data']

    # Find indices closest to 0°
    az0_idx = min(range(len(az)), key=lambda i: abs(az[i]))
    el0_idx = min(range(len(el)), key=lambda i: abs(el[i]))

    # Az cut = gain vs elevation at az=0
    az_cut = np.array([data[i][az0_idx] for i in range(len(el))])
    # El cut = gain vs azimuth at el=0
    el_cut = np.array(data[el0_idx])

    return {
        'az_cut_angles': np.array(el),
        'az_cut_gain': az_cut,
        'el_cut_angles': np.array(az),
        'el_cut_gain': el_cut,
        'freq': ref_entry['freq'],
        'peak': ref_entry['analysis']['peak_gain'],
    }


def _optimize_cuts(
    cfg: dict, ref_data: list[dict], log,
) -> tuple[dict, bool]:
    """Stage-1 optimizer: fit principal-plane cuts only.

    Much faster than full 2D pattern (1D cost evaluations) and
    effectively constrains gain, BW, FTB, and element_length
    before the full-pattern refinement.

    Returns ``(cfg, improved_flag)``.
    """
    from core.engine import compute_pattern

    valid_refs = [r for r in ref_data if r['freq'] is not None]
    if len(valid_refs) < 1:
        return cfg, False

    indices = _subsample_refs(valid_refs, n_target=5)
    cuts = [_extract_principal_cuts(valid_refs[i]) for i in indices]

    atype = cfg['antenna_type']
    is_omni = atype in ("Omni", "Monopole")
    is_monopole = atype == "Monopole"

    # Build a small param vector: just the "big" params
    params = [('max_gain_dbi', cfg['max_gain_dbi'],
               cfg['max_gain_dbi'] - 5.0, cfg['max_gain_dbi'] + 5.0)]

    if is_monopole:
        params.append(('element_length_wavelengths',
                        cfg.get('element_length_wavelengths', 0.25), 0.05, 2.0))
    elif is_omni:
        params.append(('el_beamwidth_deg', cfg['el_beamwidth_deg'], 5.0, 180.0))
    else:
        params.append(('az_beamwidth_deg', cfg['az_beamwidth_deg'],
                        max(1.0, cfg['az_beamwidth_deg'] * 0.5),
                        cfg['az_beamwidth_deg'] * 1.5))
        params.append(('el_beamwidth_deg', cfg['el_beamwidth_deg'],
                        max(1.0, cfg['el_beamwidth_deg'] * 0.5),
                        cfg['el_beamwidth_deg'] * 1.5))
        if 'ftb_ratio_db' in cfg:
            params.append(('ftb_ratio_db', cfg['ftb_ratio_db'], 0.0, 60.0))

    param_names = [p[0] for p in params]
    x0 = np.array([p[1] for p in params], dtype=np.float64)
    lo = np.array([p[2] for p in params], dtype=np.float64)
    hi = np.array([p[3] for p in params], dtype=np.float64)

    def cost(x):
        trial = copy.deepcopy(cfg)
        trial['noise_range_db'] = 0.0
        trial['features']['pattern_breakup']['enabled'] = False
        xc = np.clip(x, lo, hi)
        for i, name in enumerate(param_names):
            trial[name] = float(xc[i])

        total_err = 0.0
        for c in cuts:
            try:
                # Compute full pattern, extract same cuts
                copol, _ = compute_pattern(
                    list(c['el_cut_angles']),
                    list(c['az_cut_angles']),
                    c['freq'], trial)
                sim = np.array(copol)

                # Az=0 cut (el axis): column at az=0
                az0 = len(c['el_cut_angles']) // 2
                sim_az_cut = sim[:, az0] if sim.ndim == 2 else sim[0]
                # El=0 cut (az axis): row at el=0
                el0 = len(c['az_cut_angles']) // 2
                sim_el_cut = sim[el0, :] if sim.ndim == 2 else sim[0]

                # Compare cuts in dB
                err_az = np.mean((c['az_cut_gain'] - sim_az_cut) ** 2)
                err_el = np.mean((c['el_cut_gain'] - sim_el_cut) ** 2)
                total_err += err_az + err_el
            except Exception:
                return 1e12
        return float(np.sqrt(total_err / len(cuts)))

    initial_cost = cost(x0)
    log(f"  Cut-fit: {len(param_names)} params, initial={initial_cost:.1f}")

    result = _scipy_minimize(
        cost, x0, method='Nelder-Mead',
        options={'maxiter': 100 + 50 * len(param_names),
                 'xatol': 0.1, 'fatol': 0.05},
    )

    if result.fun < initial_cost - 0.1:
        xc = np.clip(result.x, lo, hi)
        for i, name in enumerate(param_names):
            val = float(xc[i])
            if isinstance(cfg.get(name), float):
                cfg[name] = round(val, 3 if 'wavelength' in name else 1)
            else:
                cfg[name] = val
        log(f"  Cut-fit improved: {initial_cost:.1f} → {result.fun:.1f}")
        return cfg, True

    return cfg, False


def _sensitivity_screen(
    cfg: dict, param_names: list, x0, lo, hi, cost_fn,
) -> list[int]:
    """Rank parameters by cost sensitivity.

    Perturbs each parameter ±10% independently and measures cost
    change.  Returns indices sorted by decreasing sensitivity
    (most sensitive first).
    """
    n = len(param_names)
    sensitivities = np.zeros(n)
    base_cost = cost_fn(x0)

    for i in range(n):
        delta = max(0.1 * abs(x0[i]), (hi[i] - lo[i]) * 0.05)
        # Try +delta
        x_up = x0.copy()
        x_up[i] = min(x0[i] + delta, hi[i])
        c_up = cost_fn(x_up)
        # Try -delta
        x_dn = x0.copy()
        x_dn[i] = max(x0[i] - delta, lo[i])
        c_dn = cost_fn(x_dn)
        # Sensitivity = max cost change
        sensitivities[i] = max(abs(c_up - base_cost), abs(c_dn - base_cost))

    return list(np.argsort(sensitivities)[::-1])


def _optimize_config(
    cfg: dict, ref_data: list[dict], log,
) -> tuple[dict, bool]:
    """Refine base config via coarse-to-fine optimization.

    Uses three stages:
      1. Sensitivity screening — rank params by impact.
      2. Coarse grid (15°) — fast global search.
         For complex types (Dish, Array ≥8 params): Differential
         Evolution.  For simple types: Nelder-Mead.
      3. Fine grid (3°) — Nelder-Mead polish from the best coarse
         solution.

    Cost function blends weighted percentage error with normalized
    cross-correlation for shape robustness.  Noise floor is
    estimated from reference data for adaptive far-out weighting.

    Returns ``(cfg, improved_flag)``.
    """
    from core.engine import compute_pattern

    # Filter out entries with no frequency before optimising
    valid_refs = [r for r in ref_data if r['freq'] is not None]
    if len(valid_refs) < 1:
        return cfg, False

    # Select a representative subset of files across the band
    indices = _subsample_refs(valid_refs, n_target=7)

    atype = cfg['antenna_type']
    is_omni = atype in ("Omni", "Monopole")
    is_monopole = atype == "Monopole"
    seeded_gain = cfg['max_gain_dbi']
    az_bw_seed = cfg['az_beamwidth_deg']
    el_bw_seed = cfg['el_beamwidth_deg']

    # ── Dynamic gain margin ───────────────────────────────
    ref_peaks = [r['analysis']['peak_gain'] for r in valid_refs]
    gain_spread = max(ref_peaks) - min(ref_peaks) if ref_peaks else 0.0
    gain_margin = max(3.0, min(8.0, 2.0 + gain_spread))

    # Preserve gain coupling setting from seeding
    has_gc = cfg['features']['gain_bw_coupling']['enabled']

    # ── Per-type realistic bounds ────────────────────────
    _TYPE_BOUNDS = {
        'Monopole': {'gain': (0.0, 5.2)},
        'Omni':     {'gain': (2.0, 8.0), 'el_bw': (15.0, 90.0)},
        'LPDA':     {'gain': (6.0, 10.0), 'az_bw': (50.0, 90.0),
                     'el_bw': (50.0, 90.0), 'ftb': (10.0, 20.0)},
        'Panel':    {'gain': (12.0, 18.0), 'az_bw': (33.0, 120.0),
                     'el_bw': (5.0, 30.0), 'ftb': (15.0, 35.0)},
        'Dish':     {'gain': (20.0, 45.0), 'az_bw': (0.5, 15.0),
                     'el_bw': (0.5, 15.0), 'ftb': (25.0, 45.0)},
        'Horn':     {'gain': (10.0, 25.0), 'az_bw': (10.0, 60.0),
                     'el_bw': (10.0, 60.0), 'ftb': (20.0, 35.0)},
        'Array':    {'gain': (10.0, 35.0), 'az_bw': (2.0, 120.0),
                     'el_bw': (2.0, 120.0), 'ftb': (10.0, 40.0)},
    }
    tb = _TYPE_BOUNDS.get(atype, {})

    def _clamp_bounds(lo, hi, abs_lo, abs_hi):
        return max(lo, abs_lo), min(hi, abs_hi)

    # ── Build per-type parameter vector ───────────────────
    g_abs = tb.get('gain', (seeded_gain - 10, seeded_gain + 10))
    g_lo, g_hi = _clamp_bounds(
        seeded_gain - gain_margin, seeded_gain + gain_margin,
        g_abs[0], g_abs[1])
    params = [('max_gain_dbi', cfg['max_gain_dbi'], g_lo, g_hi)]

    if is_monopole:
        elem_seed = cfg.get('element_length_wavelengths', 0.25)
        params.append(('element_length_wavelengths', elem_seed, 0.05, 2.0))
    elif is_omni:
        el_abs = tb.get('el_bw', (5.0, 180.0))
        params.append(('el_beamwidth_deg', cfg['el_beamwidth_deg'],
                        el_abs[0], el_abs[1]))
    else:
        az_abs = tb.get('az_bw', (1.0, 360.0))
        el_abs = tb.get('el_bw', (1.0, 180.0))
        ftb_abs = tb.get('ftb', (0.0, 60.0))
        az_lo, az_hi = _clamp_bounds(
            az_bw_seed * 0.5, az_bw_seed * 1.5, az_abs[0], az_abs[1])
        el_lo, el_hi = _clamp_bounds(
            el_bw_seed * 0.5, el_bw_seed * 1.5, el_abs[0], el_abs[1])
        params.append(('az_beamwidth_deg', cfg['az_beamwidth_deg'],
                        az_lo, az_hi))
        params.append(('el_beamwidth_deg', cfg['el_beamwidth_deg'],
                        el_lo, el_hi))
        params.append(('ftb_ratio_db', cfg['ftb_ratio_db'],
                        ftb_abs[0], ftb_abs[1]))
        params.append(('sigmoid_k', cfg.get('sigmoid_k', 12.0), 3.0, 50.0))

    if not is_omni:
        params.append(('mechanical_tilt_deg',
                        cfg.get('mechanical_tilt_deg', 0.0), -30.0, 30.0))

    if atype == 'Dish':
        params.append(('dish_efficiency',
                        cfg.get('dish_efficiency', 0.6), 0.2, 0.95))
        params.append(('feed_edge_taper_db',
                        cfg.get('feed_edge_taper_db', -12.0), -25.0, -3.0))
    elif atype == 'Horn':
        ap = cfg.get('horn_aperture_wavelengths')
        if ap is not None:
            params.append(('horn_aperture_wavelengths', ap, 0.5, 20.0))
    elif atype == 'Array':
        params.append(('array_spacing_x_lambda',
                        cfg.get('array_spacing_x_lambda', 0.5), 0.25, 1.5))
        params.append(('array_spacing_y_lambda',
                        cfg.get('array_spacing_y_lambda', 0.5), 0.25, 1.5))
        if cfg.get('array_rms_phase_error_deg', 0) > 0:
            params.append(('array_rms_phase_error_deg',
                            cfg['array_rms_phase_error_deg'], 0.0, 30.0))
        if cfg.get('array_rms_amplitude_error_db', 0) > 0:
            params.append(('array_rms_amplitude_error_db',
                            cfg['array_rms_amplitude_error_db'], 0.0, 3.0))

    feats = cfg.get('features', {})
    sl = feats.get('sidelobes', {})
    if sl.get('enabled'):
        params.append(('_sidelobe_db', sl.get('first_sidelobe_db', -13.2),
                        -30.0, -5.0))
    gr = feats.get('ground_reflection', {})
    if gr.get('enabled'):
        params.append(('_gr_height', gr.get('height_wavelengths', 1.0),
                        0.2, 10.0))
        params.append(('_gr_coeff', gr.get('reflection_coeff', 0.5),
                        0.1, 0.95))
    vr = feats.get('vswr_rolloff', {})
    if vr.get('enabled'):
        params.append(('_vswr_max_db', vr.get('max_rolloff_db', 3.0),
                        0.5, 8.0))

    param_names = [p[0] for p in params]
    x0 = np.array([p[1] for p in params], dtype=np.float64)
    lo = np.array([p[2] for p in params], dtype=np.float64)
    hi = np.array([p[3] for p in params], dtype=np.float64)
    n_params = len(params)

    def _apply_params(trial, x):
        xc = np.clip(x, lo, hi)
        for i, name in enumerate(param_names):
            val = float(xc[i])
            if name.startswith('_'):
                if name == '_sidelobe_db':
                    trial['features']['sidelobes']['first_sidelobe_db'] = val
                elif name == '_gr_height':
                    trial['features']['ground_reflection']['height_wavelengths'] = val
                elif name == '_gr_coeff':
                    trial['features']['ground_reflection']['reflection_coeff'] = val
                elif name == '_vswr_max_db':
                    trial['features']['vswr_rolloff']['max_rolloff_db'] = val
            else:
                trial[name] = val

    # ── Per-type cost weighting ─────────────────────────
    _COST_PROFILES = {
        'Monopole': {'beam_w': 8.0, 'far_w': 0.05,
                     'beam_th': 6.0, 'sl_th': 20.0},
        'Omni':     {'beam_w': 6.0, 'far_w': 0.1,
                     'beam_th': 10.0, 'sl_th': 25.0},
        'LPDA':     {'beam_w': 5.0, 'far_w': 0.1,
                     'beam_th': 10.0, 'sl_th': 25.0},
        'Panel':    {'beam_w': 6.0, 'far_w': 0.2,
                     'beam_th': 10.0, 'sl_th': 20.0},
        'Dish':     {'beam_w': 10.0, 'far_w': 0.3,
                     'beam_th': 6.0, 'sl_th': 20.0},
        'Horn':     {'beam_w': 6.0, 'far_w': 0.15,
                     'beam_th': 10.0, 'sl_th': 25.0},
        'Array':    {'beam_w': 8.0, 'far_w': 0.3,
                     'beam_th': 6.0, 'sl_th': 20.0},
    }
    cp = _COST_PROFILES.get(atype, {'beam_w': 5.0, 'far_w': 0.1,
                                     'beam_th': 10.0, 'sl_th': 25.0})

    def _make_cost(grid_list, noise_sigma):
        """Build a cost function for the given grids.

        Blends weighted percentage error (60%) with normalized
        cross-correlation (40%) for shape robustness.  Uses
        adaptive noise-floor weighting based on measured noise.
        """
        # Adaptive far-out threshold: if data is noisy below
        # peak-25 dB, reduce far_w further to avoid fitting noise
        adaptive_far_w = cp['far_w']
        if noise_sigma > 4.0:
            adaptive_far_w *= 0.5  # very noisy — ignore far-out
        elif noise_sigma < 2.0:
            adaptive_far_w *= 1.5  # clean data — trust far-out more

        def cost(x):
            trial = copy.deepcopy(cfg)
            trial['noise_range_db'] = 0.0
            trial['features']['pattern_breakup']['enabled'] = False
            if not has_gc:
                trial['features']['gain_bw_coupling']['enabled'] = False
                trial['features']['freq_dependent_bw_az']['enabled'] = False
                trial['features']['freq_dependent_bw_el']['enabled'] = False
            _apply_params(trial, x)

            total_pct = 0.0
            total_corr = 0.0
            for g in grid_list:
                try:
                    copol, _ = compute_pattern(
                        list(g['az']), list(g['el']), g['freq'], trial)
                    ref_arr = g['data']
                    sim = np.array(copol)

                    ref_lin = np.power(10.0, ref_arr / 10.0)
                    sim_lin = np.power(10.0, sim / 10.0)
                    ref_peak_lin = np.power(10.0, g['peak'] / 10.0)

                    # Adaptive per-type weighting
                    weights = np.ones_like(ref_arr)
                    weights[ref_arr >= g['peak'] - cp['beam_th']] = cp['beam_w']
                    weights[ref_arr < g['peak'] - cp['sl_th']] = adaptive_far_w

                    pct_err = np.abs(ref_lin - sim_lin) / np.maximum(
                        ref_peak_lin * 1e-6, ref_lin) * 100.0
                    total_pct += float(np.mean((pct_err * weights) ** 2))

                    # Cross-correlation (shape similarity, gain-offset-insensitive)
                    ref_flat = ref_arr.ravel()
                    sim_flat = sim.ravel()
                    ref_zm = ref_flat - np.mean(ref_flat)
                    sim_zm = sim_flat - np.mean(sim_flat)
                    denom = (np.linalg.norm(ref_zm) * np.linalg.norm(sim_zm))
                    if denom > 1e-12:
                        corr = float(np.dot(ref_zm, sim_zm) / denom)
                    else:
                        corr = 0.0
                    # Convert to error: 0 = perfect match, 1 = uncorrelated
                    total_corr += (1.0 - max(corr, 0.0))
                except Exception:
                    return 1e12

            n_grids = len(grid_list)
            pct_cost = float(np.sqrt(total_pct / n_grids))
            corr_cost = (total_corr / n_grids) * 500.0  # scale to pct range
            return 0.6 * pct_cost + 0.4 * corr_cost

        return cost

    # ── Stage 1: Coarse grid (15°) ───────────────────────
    coarse_grids = [_prepare_grid(valid_refs[i], stride_deg=15.0)
                    for i in indices]
    noise_sigma = _estimate_noise_floor(coarse_grids)

    cost_coarse = _make_cost(coarse_grids, noise_sigma)
    initial_cost = cost_coarse(x0)

    use_de = atype in ('Dish', 'Array') and n_params >= 7
    method_label = "DE" if use_de else "Nelder-Mead"
    log(f"Coarse ({method_label}): {initial_cost:.1f} "
        f"({n_params} params: {', '.join(param_names)})")

    if use_de:
        # Differential Evolution — global search for complex types
        bounds_de = list(zip(lo.tolist(), hi.tolist()))
        de_result = _scipy_de(
            cost_coarse, bounds_de,
            x0=x0,
            maxiter=80,
            seed=42,
            tol=0.01,
            polish=False,  # we'll polish ourselves on fine grid
        )
        x_best = de_result.x
        coarse_cost = de_result.fun
    else:
        # Sensitivity screening: optimize top params first, then all
        if n_params >= 5:
            ranking = _sensitivity_screen(
                cfg, param_names, x0, lo, hi, cost_coarse)
            top_k = min(3, n_params)
            top_idx = ranking[:top_k]

            # Phase 1: optimize only top-K params
            x0_sub = x0[top_idx]

            def cost_sub(x_sub):
                x_full = x0.copy()
                x_full[top_idx] = x_sub
                return cost_coarse(x_full)

            res_sub = _scipy_minimize(
                cost_sub, x0_sub, method='Nelder-Mead',
                options={'maxiter': 100, 'xatol': 0.1, 'fatol': 0.05})
            x_warm = x0.copy()
            x_warm[top_idx] = res_sub.x
        else:
            x_warm = x0

        # Phase 2: full Nelder-Mead from warm start
        nm_result = _scipy_minimize(
            cost_coarse, x_warm, method='Nelder-Mead',
            options={'maxiter': 150 + 50 * n_params,
                     'xatol': 0.1, 'fatol': 0.05})
        x_best = nm_result.x
        coarse_cost = nm_result.fun

    log(f"Coarse result: {coarse_cost:.1f}")

    # ── Stage 2: Fine grid (3°) — Nelder-Mead polish ─────
    fine_grids = [_prepare_grid(valid_refs[i], stride_deg=3.0)
                  for i in indices]
    cost_fine = _make_cost(fine_grids, noise_sigma)

    fine_result = _scipy_minimize(
        cost_fine, x_best, method='Nelder-Mead',
        options={'maxiter': 150 + 80 * n_params,
                 'xatol': 0.02, 'fatol': 0.005})

    final_cost = fine_result.fun
    log(f"Fine result:   {final_cost:.1f}")

    # ── Apply best result ─────────────────────────────────
    # Compare against initial cost on the fine grid
    fine_initial = cost_fine(x0)
    if final_cost < fine_initial - 0.01:
        _apply_params(cfg, fine_result.x)
        for name in param_names:
            if name.startswith('_'):
                continue
            if name in cfg and isinstance(cfg[name], float):
                cfg[name] = round(cfg[name], 3 if 'wavelength' in name
                                  or 'efficiency' in name else 1)
        log(f"Optimized: {fine_initial:.1f} → {final_cost:.1f} "
            f"(improved by {fine_initial - final_cost:.1f})")
        return cfg, True

    log("Measurement-seeded config already optimal.")
    return cfg, False


def _optimize_scaling(
    cfg: dict, ref_data: list[dict], log,
) -> tuple[dict, bool]:
    """Optimize frequency-dependent scaling parameters across the band."""
    if len(ref_data) < 3:
        return cfg, False

    from core.engine import compute_pattern

    sorted_refs = sorted(
        [r for r in ref_data if r['freq'] is not None],
        key=lambda r: r['freq'],
    )
    if len(sorted_refs) < 3:
        return cfg, False

    # If the band is very narrow, skip scaling optimisation
    if sorted_refs[-1]['freq'] / max(sorted_refs[0]['freq'], 1e-6) < 1.1:
        return cfg, False

    # Use a spread of files across the band
    indices = _subsample_refs(sorted_refs, n_target=7)
    grids = [_prepare_grid(sorted_refs[i]) for i in indices]

    feat_az = cfg['features']['freq_dependent_bw_az']
    feat_el = cfg['features']['freq_dependent_bw_el']

    if not feat_az['enabled'] and not feat_el['enabled']:
        return cfg, False

    is_omni = cfg['antenna_type'] in ("Omni", "Monopole")

    # For omni antennas, az BW is fixed at 360 — only optimise el scaling
    if is_omni:
        feat_az['enabled'] = False

    # Determine mode from whichever feature is enabled (prefer az, fall
    # back to el when az is disabled — e.g. omni antennas)
    if feat_az['enabled']:
        mode = feat_az.get('decay_mode', 'exponent')
    elif feat_el['enabled']:
        mode = feat_el.get('decay_mode', 'exponent')
    else:
        return cfg, False

    is_lpda = cfg['antenna_type'] == 'LPDA'
    has_gc = cfg['features']['gain_bw_coupling']['enabled']

    def _safe(val, default):
        """Return *val* if it is a real number, else *default*."""
        return val if val is not None else default

    # Build parameter vector — only include enabled planes
    x0_list = []
    planes = []    # track which planes are in x0
    if mode == 'three_point':
        if feat_az['enabled']:
            x0_list.extend([
                _safe(feat_az.get('three_point_start_deg'), 90),
                _safe(feat_az.get('three_point_end_deg'), 45),
            ])
            planes.append('az')
        if feat_el['enabled']:
            x0_list.extend([
                _safe(feat_el.get('three_point_start_deg'), 90),
                _safe(feat_el.get('three_point_end_deg'), 45),
            ])
            planes.append('el')
    else:
        val_key = ('scaling_exponent' if mode == 'exponent'
                   else 'decay_pct_per_octave')
        default_val = 0.8 if mode == 'exponent' else 15.0
        if feat_az['enabled']:
            x0_list.append(_safe(feat_az.get(val_key), default_val))
            planes.append('az')
        if feat_el['enabled']:
            x0_list.append(_safe(feat_el.get(val_key), default_val))
            planes.append('el')
        if is_lpda and mode == 'exponent':
            if 'az' in planes:
                x0_list.append(_safe(feat_az.get('variation_factor'), 0.3))
            if 'el' in planes:
                x0_list.append(_safe(feat_el.get('variation_factor'), 0.3))

    if not x0_list:
        return cfg, False

    if has_gc:
        x0_list.append(
            cfg['features']['gain_bw_coupling']['gain_rolloff_db_per_octave'])

    x0 = np.array(x0_list, dtype=np.float64)

    def cost(x):
        trial = copy.deepcopy(cfg)
        idx = 0
        if mode == 'three_point':
            if 'az' in planes:
                trial['features']['freq_dependent_bw_az']['three_point_start_deg'] = float(x[idx])
                trial['features']['freq_dependent_bw_az']['three_point_end_deg'] = float(x[idx + 1])
                idx += 2
            if 'el' in planes:
                trial['features']['freq_dependent_bw_el']['three_point_start_deg'] = float(x[idx])
                trial['features']['freq_dependent_bw_el']['three_point_end_deg'] = float(x[idx + 1])
                idx += 2
        else:
            key = ('scaling_exponent' if mode == 'exponent'
                   else 'decay_pct_per_octave')
            if 'az' in planes:
                trial['features']['freq_dependent_bw_az'][key] = float(
                    np.clip(x[idx], 0.05, 2.0) if mode == 'exponent' else x[idx])
                idx += 1
            if 'el' in planes:
                trial['features']['freq_dependent_bw_el'][key] = float(
                    np.clip(x[idx], 0.05, 2.0) if mode == 'exponent' else x[idx])
                idx += 1
            if is_lpda and mode == 'exponent':
                if 'az' in planes:
                    trial['features']['freq_dependent_bw_az']['variation_factor'] = float(
                        np.clip(x[idx], 0.0, 1.0))
                    idx += 1
                if 'el' in planes:
                    trial['features']['freq_dependent_bw_el']['variation_factor'] = float(
                        np.clip(x[idx], 0.0, 1.0))
                    idx += 1

        if has_gc and idx < len(x):
            trial['features']['gain_bw_coupling']['gain_rolloff_db_per_octave'] = float(
                np.clip(x[idx], 0.0, 5.0))

        total_err = 0.0
        for g in grids:
            try:
                sim, _ = compute_pattern(
                    list(g['az']), list(g['el']), g['freq'], trial)
                ref_arr = g['data']
                sim_arr = np.array(sim)

                ref_lin = np.power(10.0, ref_arr / 10.0)
                sim_lin = np.power(10.0, sim_arr / 10.0)
                ref_peak_lin = np.power(10.0, g['peak'] / 10.0)

                pct_err = np.abs(ref_lin - sim_lin) / np.maximum(
                    ref_peak_lin * 1e-6, ref_lin) * 100.0
                total_err += float(np.mean(pct_err ** 2))
            except Exception:
                return 1e12
        return float(np.sqrt(total_err / len(grids)))

    initial_cost = cost(x0)
    res = _scipy_minimize(
        cost, x0, method='Nelder-Mead',
        options={'maxiter': 200, 'xatol': 0.01, 'fatol': 0.01})

    if res.fun < initial_cost - 0.01:
        idx = 0
        if mode == 'three_point':
            if 'az' in planes:
                cfg['features']['freq_dependent_bw_az']['three_point_start_deg'] = round(float(res.x[idx]), 1)
                cfg['features']['freq_dependent_bw_az']['three_point_end_deg'] = round(float(res.x[idx + 1]), 1)
                idx += 2
            if 'el' in planes:
                cfg['features']['freq_dependent_bw_el']['three_point_start_deg'] = round(float(res.x[idx]), 1)
                cfg['features']['freq_dependent_bw_el']['three_point_end_deg'] = round(float(res.x[idx + 1]), 1)
                idx += 2
        else:
            key = ('scaling_exponent' if mode == 'exponent'
                   else 'decay_pct_per_octave')
            if 'az' in planes:
                cfg['features']['freq_dependent_bw_az'][key] = round(float(
                    np.clip(res.x[idx], 0.05, 2.0) if mode == 'exponent' else res.x[idx]), 2)
                idx += 1
            if 'el' in planes:
                cfg['features']['freq_dependent_bw_el'][key] = round(float(
                    np.clip(res.x[idx], 0.05, 2.0) if mode == 'exponent' else res.x[idx]), 2)
                idx += 1
            if is_lpda and mode == 'exponent':
                if 'az' in planes:
                    cfg['features']['freq_dependent_bw_az']['variation_factor'] = round(
                        float(np.clip(res.x[idx], 0.0, 1.0)), 2)
                    idx += 1
                if 'el' in planes:
                    cfg['features']['freq_dependent_bw_el']['variation_factor'] = round(
                        float(np.clip(res.x[idx], 0.0, 1.0)), 2)
                    idx += 1

        if has_gc and idx < len(res.x):
            cfg['features']['gain_bw_coupling']['gain_rolloff_db_per_octave'] = round(
                float(np.clip(res.x[idx], 0.0, 5.0)), 2)

        log(f"Scaling optimized: {initial_cost:.1f} -> {res.fun:.1f}")
        return cfg, True

    return cfg, False


# ===================================================================
#  FIT QUALITY
# ===================================================================

def _compute_fit_quality(cfg: dict, ref_entry: dict) -> dict:
    """Pattern-level fit quality for one reference file.

    Returns dB-space and linear-space percentage error metrics.
    """
    from core.engine import compute_pattern

    freq = ref_entry['freq']
    if freq is None:
        freq = (cfg['f_min_mhz'] + cfg['f_max_mhz']) / 2.0

    az = ref_entry['az']
    el = ref_entry['el']
    ref = ref_entry['data']

    eval_cfg = copy.deepcopy(cfg)
    eval_cfg['noise_range_db'] = 0.0

    copol, _ = compute_pattern(az, el, freq, eval_cfg)

    if _HAS_NUMPY:
        ref_arr = np.array(ref)
        sim_arr = np.array(copol)
        diff = ref_arr - sim_arr

        rms = float(np.sqrt(np.mean(diff ** 2)))
        max_err = float(np.max(np.abs(diff)))

        peak = np.max(ref_arr)
        mask = ref_arr >= peak - 10
        beam_rms = (float(np.sqrt(np.mean(diff[mask] ** 2)))
                    if np.any(mask) else rms)

        # Linear-space percentage error
        ref_lin = np.power(10.0, ref_arr / 10.0)
        sim_lin = np.power(10.0, sim_arr / 10.0)
        valid = ref_lin > 1e-6
        pct_err = np.zeros_like(ref_lin)
        pct_err[valid] = (
            np.abs(ref_lin[valid] - sim_lin[valid])
            / ref_lin[valid] * 100.0
        )
        mean_pct = float(np.mean(pct_err[valid])) if np.any(valid) else 0.0
        rms_pct = float(np.sqrt(np.mean(pct_err[valid] ** 2))) if np.any(valid) else 0.0
        beam_mask = mask & valid
        beam_pct = (float(np.mean(pct_err[beam_mask]))
                    if np.any(beam_mask) else mean_pct)
    else:
        total, max_err, count = 0.0, 0.0, 0
        for i in range(len(el)):
            for j in range(len(az)):
                d = ref[i][j] - copol[i][j]
                total += d * d
                max_err = max(max_err, abs(d))
                count += 1
        rms = math.sqrt(total / max(count, 1))
        beam_rms = rms
        mean_pct = 0.0
        rms_pct = 0.0
        beam_pct = 0.0

    return {
        'rms_db': round(rms, 2),
        'max_err_db': round(max_err, 2),
        'beam_rms_db': round(beam_rms, 2),
        'mean_pct_err': round(mean_pct, 1),
        'rms_pct_err': round(rms_pct, 1),
        'beam_pct_err': round(beam_pct, 1),
    }


def _compute_aggregate_quality(
    cfg: dict, ref_data: list[dict],
) -> dict:
    """Compute fit quality aggregated across all reference files."""
    all_q = []
    for r in ref_data:
        q = _compute_fit_quality(cfg, r)
        q['freq'] = r['freq']
        q['file'] = os.path.basename(r['file'])
        all_q.append(q)

    n = len(all_q)
    agg_rms = math.sqrt(sum(q['rms_db'] ** 2 for q in all_q) / n)
    agg_max = max(q['max_err_db'] for q in all_q)
    agg_pct = sum(q['mean_pct_err'] for q in all_q) / n
    agg_beam_pct = sum(q['beam_pct_err'] for q in all_q) / n

    return {
        'per_file': all_q,
        'agg_rms_db': round(agg_rms, 2),
        'agg_max_err_db': round(agg_max, 2),
        'agg_mean_pct_err': round(agg_pct, 1),
        'agg_beam_pct_err': round(agg_beam_pct, 1),
    }


# ===================================================================
#  REPORT
# ===================================================================

def _build_report(
    cfg: dict,
    ref_data: list[dict],
    mid_idx: int,
    quality: dict,
    antenna_type: str,
    optimized: bool,
    *,
    agg_quality: dict | None = None,
    strategy_summary: list[str] | None = None,
) -> str:
    """Build human-readable fit report."""
    lines = []
    lines.append("PARAMETER FIT REPORT")
    lines.append("=" * 50)

    lines.append(f"\nReference Files:  {len(ref_data)}")
    freqs = [r['freq'] for r in ref_data if r['freq'] is not None]
    if freqs:
        lines.append(f"Frequency Range:  {min(freqs):.1f} - {max(freqs):.1f} MHz")
    lines.append(f"Antenna Type:     {antenna_type}")
    lines.append(f"Optimized:        {'Yes' if optimized else 'No'}")

    # ── Strategy results (multi-run) ─────────────────────
    if strategy_summary:
        lines.append(f"\nSTRATEGY RESULTS:")
        lines.append("-" * 50)
        lines.append(f"  {'Run':<5}{'Strategy':<30} {'Pct(%)':>7} {'RMS(dB)':>8}")
        lines.append(f"  {'-'*48}")
        for s in strategy_summary:
            lines.append(s)

    # ── Detected features ────────────────────────────────
    lines.append(f"\nDETECTED FEATURES:")
    lines.append("-" * 50)

    coupling = cfg['features']['gain_bw_coupling']
    if coupling['enabled']:
        lines.append(
            f"  Gain Coupling:    {coupling.get('gain_rolloff_db_per_octave', 0):.2f} "
            f"dB/octave ({coupling.get('mode', 'independent')})")
    else:
        lines.append(f"  Gain Coupling:    off")

    ref_freq = cfg.get('ref_frequency_mhz')
    if ref_freq:
        lines.append(f"  Reference Freq:   {ref_freq:.1f} MHz")
    else:
        lines.append(f"  Reference Freq:   f_max ({cfg['f_max_mhz']:.1f} MHz)")

    vswr = cfg['features']['vswr_rolloff']
    lines.append(f"  VSWR Rolloff:     {'on' if vswr['enabled'] else 'off'}")

    # ── Fitted parameters ────────────────────────────────
    lines.append(f"\nFITTED PARAMETERS:")
    lines.append("-" * 50)
    lines.append(f"  Max Gain:         {cfg['max_gain_dbi']:.1f} dBi")
    lines.append(f"  Az Beamwidth:     {cfg['az_beamwidth_deg']:.1f} deg")
    lines.append(f"  El Beamwidth:     {cfg['el_beamwidth_deg']:.1f} deg")
    if antenna_type not in ("Omni", "Monopole"):
        lines.append(f"  Front-to-Back:    {cfg['ftb_ratio_db']:.1f} dB")
        lines.append(f"  Sigmoid K:        {cfg['sigmoid_k']:.1f}")

    # Mechanical tilt (directional types)
    if antenna_type not in ("Omni", "Monopole"):
        lines.append(f"  Mech. Tilt:       {cfg.get('mechanical_tilt_deg', 0.0):.1f} deg")

    # Type-specific
    if antenna_type == "Dish":
        lines.append(f"  Dish Efficiency:  {cfg.get('dish_efficiency', 0.6):.2f}")
        lines.append(f"  Edge Taper:       {cfg.get('feed_edge_taper_db', -12.0):.1f} dB")
    elif antenna_type == "Horn":
        ap = cfg.get('horn_aperture_wavelengths')
        if ap is not None:
            lines.append(f"  Aperture:         {ap:.2f} lambda")
    elif antenna_type == "Monopole":
        lines.append(f"  Element Length:   {cfg.get('element_length_wavelengths', 0.25):.3f} lambda")
    elif antenna_type == "Array":
        lines.append(f"  Spacing X:        {cfg.get('array_spacing_x_lambda', 0.5):.3f} lambda")
        lines.append(f"  Spacing Y:        {cfg.get('array_spacing_y_lambda', 0.5):.3f} lambda")

    # Sidelobes
    sl = cfg['features']['sidelobes']
    if sl['enabled']:
        lines.append(f"  First Sidelobe:   {sl['first_sidelobe_db']:.1f} dB")

    # BW scaling
    for plane, key in [('Az', 'freq_dependent_bw_az'),
                       ('El', 'freq_dependent_bw_el')]:
        feat = cfg['features'][key]
        if feat['enabled']:
            mode = feat['decay_mode']
            if mode == 'three_point':
                tp_s = feat.get('three_point_start_deg')
                tp_m = feat.get('three_point_mid_deg')
                tp_e = feat.get('three_point_end_deg')
                s = f"{tp_s:.0f}" if tp_s is not None else "?"
                m = f"{tp_m:.0f}" if tp_m is not None else "?"
                e = f"{tp_e:.0f}" if tp_e is not None else "?"
                lines.append(
                    f"  {plane} BW Scaling:  three-point "
                    f"({s} / {m} / {e} deg)")
            elif mode == 'percentage':
                lines.append(
                    f"  {plane} BW Scaling:  {feat.get('decay_pct_per_octave', 0):.1f}%/octave")
            elif mode == 'exponent':
                exp = feat.get('scaling_exponent', 0)
                detail = f"exp={exp:.2f}"
                if cfg['antenna_type'] == 'LPDA':
                    var = feat.get('variation_factor', 0)
                    detail += f", var={var:.2f}"
                lines.append(f"  {plane} BW Scaling:  exponent ({detail})")
            else:
                lines.append(f"  {plane} BW Scaling:  {mode}")
        else:
            lines.append(f"  {plane} BW Scaling:  off (constant)")

    # ── Aggregate quality (all files) ─────────────────────
    if agg_quality:
        lines.append(f"\nFIT QUALITY (all {len(ref_data)} files):")
        lines.append("-" * 50)
        lines.append(f"  Mean Pct Error:   {agg_quality['agg_mean_pct_err']:.1f}%  (linear)")
        lines.append(f"  Beam Pct Error:   {agg_quality['agg_beam_pct_err']:.1f}%  (linear)")
        lines.append(f"  Overall RMS:      {agg_quality['agg_rms_db']:.2f} dB")
        lines.append(f"  Max Error:        {agg_quality['agg_max_err_db']:.2f} dB")

    # ── Mid-band quality detail ──────────────────────────
    mid = ref_data[mid_idx]
    mid_name = os.path.basename(mid['file'])
    lines.append(f"\nMID-BAND DETAIL ({mid_name}):")
    lines.append("-" * 50)
    lines.append(f"  RMS:              {quality['rms_db']:.2f} dB")
    lines.append(f"  Main-Beam RMS:    {quality['beam_rms_db']:.2f} dB")
    mpct = quality.get('mean_pct_err')
    mpct_str = f"{mpct:.1f}" if isinstance(mpct, (int, float)) else "N/A"
    lines.append(f"  Mean Pct Error:   {mpct_str}%  (linear)")

    # Measured vs fitted comparison
    a = mid['analysis']
    lines.append(f"\n  {'Parameter':<18} {'Measured':>10} {'Fitted':>10}")
    lines.append(f"  {'-'*38}")
    lines.append(f"  {'Peak Gain (dBi)':<18} {a['peak_gain']:>10.1f} {cfg['max_gain_dbi']:>10.1f}")
    lines.append(f"  {'Az BW (deg)':<18} {a['az_bw']:>10} {cfg['az_beamwidth_deg']:>10.1f}")
    lines.append(f"  {'El BW (deg)':<18} {a['el_bw']:>10} {cfg['el_beamwidth_deg']:>10.1f}")
    if a['ftb'] is not None:
        lines.append(f"  {'F/B Ratio (dB)':<18} {a['ftb']:>10.1f} {cfg['ftb_ratio_db']:>10.1f}")

    # ── Per-file quality table ───────────────────────────
    if agg_quality and len(ref_data) > 1:
        pf = agg_quality.get('per_file', [])
        lines.append(f"\nPER-FILE FIT QUALITY:")
        lines.append("-" * 72)
        lines.append(
            f"  {'Freq':>8}  {'Peak':>7}  {'AzBW':>6}  {'ElBW':>6}"
            f"  {'RMS':>6}  {'Pct%':>6}  File")
        lines.append(
            f"  {'(MHz)':>8}  {'(dBi)':>7}  {'(deg)':>6}  {'(deg)':>6}"
            f"  {'(dB)':>6}  {'(lin)':>6}")
        lines.append(f"  {'-'*70}")

        for i, r in enumerate(ref_data):
            ra = r['analysis']
            freq_str = f"{r['freq']:.1f}" if r['freq'] else "?"
            fname = os.path.basename(r['file'])[:20]
            mid_mark = " *" if i == mid_idx else ""

            # Find matching per-file quality
            rms_str = "-"
            pct_str = "-"
            for pq in pf:
                if pq.get('freq') == r['freq']:
                    rms_str = f"{pq['rms_db']:.1f}"
                    pct_str = f"{pq['mean_pct_err']:.0f}"
                    break

            lines.append(
                f"  {freq_str:>8}  {ra['peak_gain']:>7.1f}  "
                f"{ra['az_bw']:>6}  {ra['el_bw']:>6}  "
                f"{rms_str:>6}  {pct_str:>5}%"
                f"  {fname}{mid_mark}")
        lines.append(f"  (* = mid-band reference)")

    return "\n".join(lines)
