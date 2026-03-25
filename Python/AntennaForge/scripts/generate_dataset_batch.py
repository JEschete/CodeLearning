#!/usr/bin/env python3
"""Generate large-scale dataset batch JSONs for AntennaForge.

Creates batch recipe files with randomized antenna configurations
split between Testing and Validation folders, organized by antenna type.
Supports interactive prompts or non-interactive CLI flags.

Usage:
    python scripts/generate_dataset_batch.py                    # interactive
    python scripts/generate_dataset_batch.py --count 50000      # non-interactive
"""

import argparse
import json
import math
import os
import random
import sys

# math used by _rand_freq for log-uniform distribution

# ═══════════════════════════════════════════════════════════════════
#  ANTENNA TYPES & PARAMETER RANGES
# ═══════════════════════════════════════════════════════════════════

ANTENNA_TYPES = ["LPDA", "Omni", "Monopole", "Panel", "Horn", "Dish", "Array"]

# Frequency ranges: (f_min_lo, f_min_hi, band_ratio_lo, band_ratio_hi)
FREQ_RANGES = {
    "LPDA":     (20,    2000,  2.0,  10.0),
    "Omni":     (50,    5000,  1.1,  5.0),
    "Monopole": (20,    3000,  1.1,  3.0),
    "Panel":    (400,   30000, 1.1,  4.0),
    "Horn":     (1000,  50000, 1.2,  3.0),
    "Dish":     (500,   40000, 1.05, 1.5),
    "Array":    (500,   10000, 1.1,  2.5),
}

# Core param ranges: (gain_lo, gain_hi, az_bw_lo, az_bw_hi, el_bw_lo, el_bw_hi,
#                      ftb_lo, ftb_hi, sigmoid_lo, sigmoid_hi)
CORE_RANGES = {
    "LPDA":     (5,  12,  30,  90,   30, 90,  8,  25, 5,  25),
    "Omni":     (0,  9,   360, 360,  10, 90,  0,  0,  5,  20),
    "Monopole": (0,  5,   360, 360,  20, 90,  0,  0,  5,  15),
    "Panel":    (10, 20,  20,  120,  5,  40,  15, 35, 8,  20),
    "Horn":     (8,  25,  10,  80,   8,  60,  15, 35, 6,  20),
    "Dish":     (20, 45,  1,   15,   1,  15,  25, 45, 8,  20),
    "Array":    (8,  25,  5,   60,   10, 70,  10, 30, 8,  20),
}

# Feature enable probabilities per type
# (bw_az, bw_el, sidelobes, breakup, ground, vswr, asym, gbw_coupling, xpol)
FEATURE_PROBS = {
    "LPDA":     (0.70, 0.75, 0.60, 0.40, 0.25, 0.50, 0.20, 0.40, 0.15),
    "Omni":     (0.00, 0.75, 0.55, 0.40, 0.30, 0.50, 0.00, 0.35, 0.10),
    "Monopole": (0.00, 0.60, 0.40, 0.30, 0.35, 0.50, 0.00, 0.30, 0.10),
    "Panel":    (0.75, 0.75, 0.65, 0.45, 0.20, 0.55, 0.25, 0.45, 0.15),
    "Horn":     (0.75, 0.75, 0.65, 0.35, 0.20, 0.50, 0.20, 0.40, 0.15),
    "Dish":     (0.80, 0.80, 0.70, 0.45, 0.15, 0.50, 0.15, 0.45, 0.10),
    "Array":    (0.70, 0.70, 0.60, 0.40, 0.15, 0.50, 0.20, 0.40, 0.15),
}


# ═══════════════════════════════════════════════════════════════════
#  RANDOM CONFIG GENERATORS
# ═══════════════════════════════════════════════════════════════════

def _rand_freq(antenna_type):
    """Return (f_min, f_max) for the given type using log-uniform for f_min."""
    fmin_lo, fmin_hi, ratio_lo, ratio_hi = FREQ_RANGES[antenna_type]
    # Log-uniform distribution for f_min to cover decades evenly
    log_lo = math.log10(fmin_lo)
    log_hi = math.log10(fmin_hi)
    f_min = round(10 ** random.uniform(log_lo, log_hi), 2)
    ratio = random.uniform(ratio_lo, ratio_hi)
    f_max = round(f_min * ratio, 2)
    # Cap at 100 GHz
    f_max = min(f_max, 100000.0)
    return f_min, f_max


def _rand_features(antenna_type):
    """Generate a randomized features dict for the given antenna type."""
    probs = FEATURE_PROBS[antenna_type]
    p_bw_az, p_bw_el, p_sl, p_brk, p_gr, p_vswr, p_asym, p_gbw, p_xpol = probs
    features = {}

    # ── freq_dependent_bw_az ──
    if p_bw_az > 0 and random.random() < p_bw_az:
        decay_mode = random.choice(["exponent", "percentage"])
        feat = {"enabled": True, "decay_mode": decay_mode}
        if decay_mode == "exponent":
            feat["scaling_exponent"] = round(random.uniform(0.3, 1.2), 2)
            if antenna_type == "LPDA":
                feat["lpda_variation_factor"] = round(random.uniform(0.1, 0.6), 2)
        else:
            feat["decay_pct_per_octave"] = round(random.uniform(5, 30), 1)
        feat["min_bw_deg"] = round(random.uniform(5, 15), 1)
        feat["max_bw_deg"] = round(random.uniform(150, 180), 1)
        features["freq_dependent_bw_az"] = feat
    else:
        features["freq_dependent_bw_az"] = {"enabled": False}

    # ── freq_dependent_bw_el ──
    if random.random() < p_bw_el:
        decay_mode = random.choice(["exponent", "percentage"])
        feat = {"enabled": True, "decay_mode": decay_mode}
        if decay_mode == "exponent":
            feat["scaling_exponent"] = round(random.uniform(0.3, 1.2), 2)
            if antenna_type == "LPDA":
                feat["lpda_variation_factor"] = round(random.uniform(0.1, 0.6), 2)
        else:
            feat["decay_pct_per_octave"] = round(random.uniform(5, 30), 1)
        feat["min_bw_deg"] = round(random.uniform(5, 15), 1)
        feat["max_bw_deg"] = round(random.uniform(60, 90), 1)
        features["freq_dependent_bw_el"] = feat
    else:
        features["freq_dependent_bw_el"] = {"enabled": False}

    # ── sidelobes ──
    if random.random() < p_sl:
        features["sidelobes"] = {
            "enabled": True,
            "type": "taylor",
            "first_sidelobe_db": round(random.uniform(-25, -8), 1),
            "decay_rate_db": round(random.uniform(1, 6), 1),
            "n_sidelobes": random.randint(3, 10),
        }
    else:
        features["sidelobes"] = {"enabled": False}

    # ── pattern_breakup ──
    if random.random() < p_brk:
        features["pattern_breakup"] = {
            "enabled": True,
            "onset_angle_deg": round(random.uniform(40, 120), 1),
            "ripple_amplitude_db": round(random.uniform(1, 6), 1),
            "ripple_density": round(random.uniform(2, 8), 1),
        }
    else:
        features["pattern_breakup"] = {"enabled": False}

    # ── ground_reflection ──
    if random.random() < p_gr:
        features["ground_reflection"] = {
            "enabled": True,
            "height_wavelengths": round(random.uniform(0.5, 10), 2),
            "reflection_coeff": round(random.uniform(0.2, 0.9), 2),
        }
    else:
        features["ground_reflection"] = {"enabled": False}

    # ── vswr_rolloff ──
    if random.random() < p_vswr:
        features["vswr_rolloff"] = {
            "enabled": True,
            "rolloff_band_fraction": round(random.uniform(0.05, 0.20), 2),
            "max_rolloff_db": round(random.uniform(1, 5), 1),
            "rolloff_shape": random.choice(["cosine", "linear"]),
        }
    else:
        features["vswr_rolloff"] = {"enabled": False}

    # ── asymmetry ──
    if p_asym > 0 and random.random() < p_asym:
        features["asymmetry"] = {
            "enabled": True,
            "az_squint_deg": round(random.uniform(-5, 5), 1),
            "el_tilt_deg": round(random.uniform(-3, 3), 1),
            "random_asymmetry_db": round(random.uniform(0.2, 2.0), 2),
        }
    else:
        features["asymmetry"] = {"enabled": False}

    # ── gain_bw_coupling ──
    if random.random() < p_gbw:
        features["gain_bw_coupling"] = {
            "enabled": True,
            "mode": random.choice(["independent", "gain_drives_bw"]),
            "gain_rolloff_db_per_octave": round(random.uniform(0.3, 3.0), 2),
        }
    else:
        features["gain_bw_coupling"] = {"enabled": False}

    # ── cross_pol ──
    if random.random() < p_xpol:
        features["cross_pol"] = {
            "enabled": True,
            "boresight_isolation_db": round(random.uniform(-35, -15), 1),
            "peak_angle_deg": round(random.uniform(30, 60), 1),
            "max_cross_pol_db": round(random.uniform(-25, -10), 1),
        }
    else:
        features["cross_pol"] = {"enabled": False}

    return features


def random_config(antenna_type, index, base_dir, split, n_slices):
    """Generate a single randomized config dict."""
    r = CORE_RANGES[antenna_type]
    gain_lo, gain_hi = r[0], r[1]
    az_lo, az_hi = r[2], r[3]
    el_lo, el_hi = r[4], r[5]
    ftb_lo, ftb_hi = r[6], r[7]
    sig_lo, sig_hi = r[8], r[9]

    f_min, f_max = _rand_freq(antenna_type)

    # Resolve n_slices
    if n_slices == "random":
        ns = random.randint(5, 25)
    else:
        ns = int(n_slices)

    # Folder name: f_min-f_max MHz with index
    f_min_s = f"{f_min:g}"
    f_max_s = f"{f_max:g}"
    folder_name = f"{f_min_s}-{f_max_s}MHz_{index:05d}"
    output_dir = os.path.join(
        base_dir, split, antenna_type, folder_name
    ).replace("\\", "/")

    cfg = {
        "antenna_type": antenna_type,
        "max_gain_dbi": round(random.uniform(gain_lo, gain_hi), 2),
        "az_beamwidth_deg": round(random.uniform(az_lo, az_hi), 1),
        "el_beamwidth_deg": round(random.uniform(el_lo, el_hi), 1),
        "f_min_mhz": f_min,
        "f_max_mhz": f_max,
        "n_slices": ns,
        "freq_spacing": random.choice(["linear", "log"]),
        "sigmoid_k": round(random.uniform(sig_lo, sig_hi), 1),
        "noise_range_db": 0.0,
        "noise_type": "uniform",
        "polarization": "vertical" if random.random() < 0.70 else "horizontal",
        "output_dir": output_dir,
        "output_format": ".csv",
    }

    # Front-to-back ratio (directional types only)
    if ftb_hi > 0:
        cfg["ftb_ratio_db"] = round(random.uniform(ftb_lo, ftb_hi), 1)

    # ── Type-specific parameters ──
    if antenna_type == "Monopole":
        cfg["element_length_wavelengths"] = round(random.uniform(0.1, 1.0), 3)

    elif antenna_type == "Panel":
        cfg["panel_downtilt_deg"] = round(random.uniform(-15, 15), 1)

    elif antenna_type == "Dish":
        cfg["dish_efficiency"] = round(random.uniform(0.35, 0.85), 2)

    elif antenna_type == "Array":
        geometry = random.choice(["linear", "planar", "circular"])
        cfg["array_geometry"] = geometry
        cfg["array_n_elements_x"] = random.randint(4, 16)
        cfg["array_spacing_x_lambda"] = round(random.uniform(0.3, 0.8), 2)
        cfg["array_steer_az_deg"] = round(random.uniform(-45, 45), 1)
        cfg["array_steer_el_deg"] = round(random.uniform(-30, 30), 1)

        if geometry == "planar":
            cfg["array_n_elements_y"] = random.randint(2, 8)
            cfg["array_spacing_y_lambda"] = round(random.uniform(0.3, 0.8), 2)
        else:
            cfg["array_n_elements_y"] = 1

        weighting = random.choice(["uniform", "taylor"])
        cfg["array_weighting"] = weighting
        if weighting == "taylor":
            cfg["array_taper_sll_db"] = round(random.uniform(-35, -15), 1)

        cfg["array_mutual_coupling"] = random.random() < 0.20

    # ── Features ──
    cfg["features"] = _rand_features(antenna_type)

    return cfg


# ═══════════════════════════════════════════════════════════════════
#  INTERACTIVE PROMPTS
# ═══════════════════════════════════════════════════════════════════

def _prompt(msg, default=None, cast=None):
    """Prompt user with a default value. Returns cast(value)."""
    suffix = f" [{default}]" if default is not None else ""
    while True:
        try:
            raw = input(f"{msg}{suffix}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if not raw and default is not None:
            raw = str(default)
        if not raw:
            print("  (required — please enter a value)")
            continue
        if cast:
            try:
                return cast(raw)
            except (ValueError, TypeError):
                print(f"  Invalid input: {raw!r}")
                continue
        return raw


def interactive_prompts():
    """Run interactive prompts and return a namespace-like dict."""
    print()
    print("=" * 48)
    print("  AntennaForge Dataset Batch Generator")
    print("=" * 48)
    print()

    count = _prompt("Total number of configs to generate", default=100, cast=int)
    if count <= 0:
        print("Count must be > 0.")
        sys.exit(1)

    print()
    print("Available antenna types:")
    for i, t in enumerate(ANTENNA_TYPES, 1):
        print(f"  {i}. {t}")
    print("  A. All types")
    print()
    choice = _prompt(
        "Select types (comma-separated numbers, or A for all)", default="A"
    )
    if choice.upper() == "A":
        types = list(ANTENNA_TYPES)
    else:
        indices = [int(x.strip()) for x in choice.split(",") if x.strip().isdigit()]
        types = [ANTENNA_TYPES[i - 1] for i in indices if 1 <= i <= len(ANTENNA_TYPES)]
        if not types:
            print("No valid types selected, using all.")
            types = list(ANTENNA_TYPES)

    print()
    split_pct = _prompt(
        "Testing/Validation split % for Testing", default=80, cast=int
    )
    if not 0 <= split_pct <= 100:
        print("Split must be 0-100.")
        sys.exit(1)

    print()
    ns_raw = _prompt(
        "Frequency slices per config (5-25, or 'r' for random)", default="10"
    )
    if ns_raw.lower() in ("r", "random"):
        n_slices = "random"
    else:
        try:
            n_slices = int(ns_raw)
        except ValueError:
            print(f"Invalid slice count: {ns_raw!r}, using 10.")
            n_slices = 10
        if isinstance(n_slices, int) and n_slices < 1:
            print("Slices must be >= 1, using 1.")
            n_slices = 1

    print()
    base_dir = _prompt("Output base directory for patterns", default="./datasets")

    seed_raw = input("  Random seed (blank for random): ").strip()
    if seed_raw:
        try:
            seed = int(seed_raw)
        except ValueError:
            print(f"  Invalid seed: {seed_raw!r}, using random.")
            seed = None
    else:
        seed = None

    out_dir = _prompt(
        "Batch JSON output directory", default="./batch_scripts"
    )

    return {
        "count": count,
        "types": types,
        "split": split_pct,
        "n_slices": n_slices,
        "base_dir": base_dir,
        "seed": seed,
        "out": out_dir,
    }


# ═══════════════════════════════════════════════════════════════════
#  CLI PARSER
# ═══════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Generate dataset batch JSONs for AntennaForge.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--count", type=int, default=None,
                   help="Total configs to generate (triggers non-interactive mode)")
    p.add_argument("--types", nargs="*", default=None,
                   help="Antenna types (e.g., LPDA Panel Horn) or 'all'")
    p.add_argument("--split", type=int, default=80,
                   help="Testing split %% (default: 80)")
    p.add_argument("--n-slices", default="10",
                   help="Slices per config: integer or 'random' (default: 10)")
    p.add_argument("--base-dir", default="./datasets",
                   help="Root output dir for patterns (default: ./datasets)")
    p.add_argument("--out", default="./batch_scripts",
                   help="Directory for batch JSONs (default: ./batch_scripts)")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed for reproducibility")
    return p.parse_args()


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    args = parse_args()

    # Decide interactive vs non-interactive
    if args.count is None:
        opts = interactive_prompts()
    else:
        # Non-interactive: resolve types
        if args.types is None or args.types == ["all"]:
            types = list(ANTENNA_TYPES)
        else:
            types = [t for t in args.types if t in ANTENNA_TYPES]
            if not types:
                print(f"Error: no valid types in {args.types}")
                print(f"Available: {', '.join(ANTENNA_TYPES)}")
                sys.exit(1)

        ns = args.n_slices
        if ns.lower() in ("r", "random"):
            ns = "random"
        else:
            try:
                ns = int(ns)
            except ValueError:
                print(f"Error: invalid --n-slices value: {ns!r}")
                sys.exit(1)
            if ns < 1:
                print("Error: --n-slices must be >= 1")
                sys.exit(1)

        if not 0 <= args.split <= 100:
            print("Error: --split must be 0-100")
            sys.exit(1)

        if args.count <= 0:
            print("Error: --count must be > 0")
            sys.exit(1)

        opts = {
            "count": args.count,
            "types": types,
            "split": args.split,
            "n_slices": ns,
            "base_dir": args.base_dir,
            "seed": args.seed,
            "out": args.out,
        }

    count = opts["count"]
    types = opts["types"]
    split_pct = opts["split"]
    n_slices = opts["n_slices"]
    base_dir = opts["base_dir"]
    seed = opts["seed"]
    out_dir = opts["out"]

    if seed is not None:
        random.seed(seed)

    # ── Distribute configs across types ──
    n_types = len(types)
    if count < n_types:
        print(f"Error: count ({count}) is less than the number of "
              f"antenna types ({n_types}).  Each type needs at least "
              f"one config — increase count to >= {n_types}.")
        sys.exit(1)

    per_type = count // n_types
    remainder = count % n_types
    if remainder:
        print(f"  Note: {count} configs / {n_types} types — "
              f"{remainder} type(s) will get one extra config.")

    # Build all configs
    all_configs = []
    global_index = 0

    for ti, atype in enumerate(types):
        n = per_type + (1 if ti < remainder else 0)
        for _ in range(n):
            global_index += 1
            # Placeholder split — will assign after shuffle
            cfg = random_config(atype, global_index, base_dir, "Testing", n_slices)
            all_configs.append((atype, global_index, cfg))

    # ── Shuffle and split ──
    random.shuffle(all_configs)
    n_testing = int(count * split_pct / 100)

    for i, (atype, idx, cfg) in enumerate(all_configs):
        split = "Testing" if i < n_testing else "Validation"
        # Rewrite output_dir with correct split
        f_min = cfg["f_min_mhz"]
        f_max = cfg["f_max_mhz"]
        folder_name = f"{f_min:g}-{f_max:g}MHz_{idx:05d}"
        cfg["output_dir"] = os.path.join(
            base_dir, split, atype, folder_name
        ).replace("\\", "/")

    # ── Count per type per split ──
    dist = {}
    for i, (atype, _, _) in enumerate(all_configs):
        split = "Testing" if i < n_testing else "Validation"
        key = (atype, split)
        dist[key] = dist.get(key, 0) + 1

    # ── Print summary ──
    print()
    print("=" * 55)
    print("  Dataset Batch Summary")
    print("=" * 55)
    print(f"  Total configs:  {count:,}")
    print(f"  Antenna types:  {', '.join(types)}")
    print(f"  Split:          {split_pct}% Testing / {100 - split_pct}% Validation")
    print(f"  n_slices:       {n_slices}")
    print(f"  Seed:           {seed if seed is not None else '(random)'}")
    print(f"  Base dir:       {base_dir}")
    print()
    print(f"  {'Type':<12} {'Testing':>8}  {'Validation':>10}  {'Total':>7}")
    print(f"  {'-' * 12} {'-' * 8}  {'-' * 10}  {'-' * 7}")
    for atype in types:
        t = dist.get((atype, "Testing"), 0)
        v = dist.get((atype, "Validation"), 0)
        print(f"  {atype:<12} {t:>8,}  {v:>10,}  {t + v:>7,}")
    total_t = sum(dist.get((t, "Testing"), 0) for t in types)
    total_v = sum(dist.get((t, "Validation"), 0) for t in types)
    print(f"  {'-' * 12} {'-' * 8}  {'-' * 10}  {'-' * 7}")
    print(f"  {'TOTAL':<12} {total_t:>8,}  {total_v:>10,}  {count:>7,}")
    print()

    # ── Write batch JSON ──
    os.makedirs(out_dir, exist_ok=True)
    just_configs = [cfg for (_, _, cfg) in all_configs]

    filepath = os.path.join(out_dir, "dataset_batch.json")
    batch = {
        "description": (
            f"AntennaForge dataset batch - {count:,} configs"
            f" ({', '.join(types)})"
        ),
        "configs": just_configs,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2)

    print(f"  Written: {filepath}  ({count:,} configs)")
    print()


if __name__ == "__main__":
    main()
