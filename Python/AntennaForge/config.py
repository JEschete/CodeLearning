"""
Configuration management.

DEFAULT_CONFIG holds all shared parameters. Antenna-specific defaults
are merged in at runtime via AntennaBase.default_params().

This module is a leaf node — no internal imports.
"""

import json
import logging
import math
import os
from copy import deepcopy

logger = logging.getLogger(__name__)


# ===================================================================
#  DEFAULT CONFIGURATION
# ===================================================================

VERSION = "1.0"

DEFAULT_CONFIG = {
    "antenna_type": "LPDA",
    "max_gain_dbi": 7.0,
    "az_beamwidth_deg": 65.0,
    "el_beamwidth_deg": 70.0,
    "ref_frequency_mhz": None,
    "f_min_mhz": 30.0,
    "f_max_mhz": 300.0,
    "n_slices": 10,
    "freq_spacing": "linear",
    "az_step_deg": 1.0,
    "el_step_deg": 1.0,
    "ftb_ratio_db": 15.0,
    "polarization": "vertical",
    "pol_angle_deg": 0.0,
    "noise_range_db": 0.0,
    "noise_type": "uniform",
    "sigmoid_k": 12.0,
    "mechanical_tilt_deg": 0.0,
    "monopole_physical_length_m": None,
    "output_dir": "./antenna_patterns",
    "output_format": ".dat",
    "features": {
        "freq_dependent_bw_az": {
            "enabled": True,
            "description": "Az beamwidth narrows with frequency",
            "decay_mode": "exponent",
            "scaling_exponent": 0.8,
            "variation_factor": 0.4,
            "decay_pct_per_octave": 15.0,
            "three_point_start_deg": None,
            "three_point_mid_deg": None,
            "three_point_end_deg": None,
            "min_bw_deg": 10.0,
            "max_bw_deg": 180.0
        },
        "freq_dependent_bw_el": {
            "enabled": True,
            "description": "El beamwidth narrows with frequency",
            "decay_mode": "exponent",
            "scaling_exponent": 0.8,
            "variation_factor": 0.4,
            "decay_pct_per_octave": 15.0,
            "three_point_start_deg": None,
            "three_point_mid_deg": None,
            "three_point_end_deg": None,
            "min_bw_deg": 10.0,
            "max_bw_deg": 90.0
        },
        "sidelobes": {
            "enabled": True,
            "description": "Realistic sidelobe structure",
            "type": "taylor",
            "first_sidelobe_db": -13.2,
            "decay_rate_db": 2.0,
            "n_sidelobes": 5
        },
        "pattern_breakup": {
            "enabled": True,
            "description":
                "Pattern breakup/irregularity at high angles",
            "onset_angle_deg": 90.0,
            "ripple_amplitude_db": 4.0,
            "ripple_density": 3.0
        },
        "ground_reflection": {
            "enabled": False,
            "description":
                "Ground plane reflection (2-ray model)",
            "height_wavelengths": 1.0,
            "reflection_coeff": 0.7,
            "ground_type": "good_soil"
        },
        "cross_pol": {
            "enabled": False,
            "description":
                "Generate cross-polarization pattern CSVs",
            "boresight_isolation_db": -25.0,
            "peak_angle_deg": 45.0,
            "max_cross_pol_db": -15.0
        },
        "vswr_rolloff": {
            "enabled": True,
            "description":
                "Gain rolloff at band edges "
                "due to impedance mismatch",
            "rolloff_band_fraction": 0.1,
            "max_rolloff_db": 3.0,
            "rolloff_shape": "cosine"
        },
        "asymmetry": {
            "enabled": False,
            "description":
                "Pattern asymmetry (squint and tilt)",
            "az_squint_deg": 0.0,
            "el_tilt_deg": 0.0,
            "random_asymmetry_db": 1.0
        },
        "gain_bw_coupling": {
            "enabled": False,
            "description":
                "Frequency-dependent gain with "
                "beamwidth coupling",
            "mode": "independent",
            "gain_rolloff_db_per_octave": 1.5
        }
    }
}


# ===================================================================
#  CONFIG SCHEMA VALIDATION
# ===================================================================

# Required top-level keys with (type, min, max) constraints.
# None means no bound.
_SCHEMA = {
    "antenna_type":      (str,   None,  None),
    "max_gain_dbi":      (float, -30.0, 60.0),
    "az_beamwidth_deg":  (float, 1.0,   360.0),
    "el_beamwidth_deg":  (float, 1.0,   360.0),
    "f_min_mhz":         (float, 0.001, 1e6),
    "f_max_mhz":         (float, 0.001, 1e6),
    "n_slices":          (int,   1,     10000),
    "freq_spacing":      (str,   None,  None),
    "az_step_deg":       (float, 0.01,  45.0),
    "el_step_deg":       (float, 0.01,  45.0),
    "ftb_ratio_db":      (float, 0.0,   80.0),
    "noise_range_db":    (float, 0.0,   30.0),
    "noise_type":        (str,   None,  None),
    "sigmoid_k":         (float, 1.0,   100.0),
    "output_format":     (str,   None,  None),
}

_VALID_SPACINGS = {"linear", "log"}
_VALID_POLS = {"vertical", "horizontal", "custom"}
_VALID_NOISE_TYPES = {"uniform", "gaussian", "quantization"}


def validate_config(cfg: dict) -> list[str]:
    """Validate a configuration dictionary.

    Checks required keys, types, value ranges, and cross-field
    constraints.

    Args:
        cfg: Configuration dictionary to validate.

    Returns:
        List of error strings. Empty list means valid.
    """
    from antennas import available_names

    errors = []

    # ── Required top-level keys ──────────────────────
    for key, (typ, lo, hi) in _SCHEMA.items():
        if key not in cfg:
            errors.append(f"Missing required key: '{key}'")
            continue
        val = cfg[key]
        # Type check (allow int where float expected)
        if typ is float and isinstance(val, int):
            val = float(val)
        if not isinstance(val, typ):
            errors.append(
                f"'{key}' must be {typ.__name__}, "
                f"got {type(val).__name__}"
            )
            continue
        if typ in (int, float):
            if lo is not None and val < lo:
                errors.append(
                    f"'{key}' = {val} is below minimum {lo}"
                )
            if hi is not None and val > hi:
                errors.append(
                    f"'{key}' = {val} exceeds maximum {hi}"
                )

    # ── Cross-field checks ───────────────────────────
    f_min = cfg.get("f_min_mhz", 0)
    f_max = cfg.get("f_max_mhz", 0)
    if (isinstance(f_min, (int, float))
            and isinstance(f_max, (int, float))
            and f_min > f_max):
        errors.append(
            f"f_min_mhz ({f_min}) > f_max_mhz ({f_max})"
        )

    if cfg.get("freq_spacing") not in _VALID_SPACINGS:
        errors.append(
            f"freq_spacing must be one of {_VALID_SPACINGS}, "
            f"got '{cfg.get('freq_spacing')}'"
        )

    pol = cfg.get("polarization", "vertical")
    if pol not in _VALID_POLS:
        errors.append(
            f"polarization must be one of {_VALID_POLS}, "
            f"got '{pol}'"
        )

    nt = cfg.get("noise_type", "uniform")
    if nt not in _VALID_NOISE_TYPES:
        errors.append(
            f"noise_type must be one of {_VALID_NOISE_TYPES}, "
            f"got '{nt}'"
        )

    ant = cfg.get("antenna_type", "")
    names = available_names()
    if ant and ant not in names:
        errors.append(
            f"Unknown antenna_type '{ant}'. "
            f"Available: {', '.join(names)}"
        )

    # ── Features block ───────────────────────────────
    feats = cfg.get("features")
    if feats is None:
        errors.append("Missing 'features' dict")
    elif not isinstance(feats, dict):
        errors.append("'features' must be a dict")
    else:
        for fname, fval in feats.items():
            if not isinstance(fval, dict):
                errors.append(
                    f"features.{fname} must be a dict"
                )
                continue
            if "enabled" not in fval:
                errors.append(
                    f"features.{fname} missing 'enabled' key"
                )
            elif not isinstance(fval["enabled"], bool):
                errors.append(
                    f"features.{fname}.enabled must be bool"
                )

        # Sidelobe-specific
        sl = feats.get("sidelobes", {})
        if sl.get("enabled"):
            fsl = sl.get("first_sidelobe_db", 0)
            if isinstance(fsl, (int, float)) and fsl > 0:
                errors.append(
                    "sidelobes.first_sidelobe_db should "
                    "be <= 0 (dB below main lobe)"
                )

    if errors:
        logger.warning("Config validation found %d issue(s):",
                       len(errors))
        for e in errors:
            logger.warning("  • %s", e)

    return errors


# ===================================================================
#  SAVE / LOAD
# ===================================================================

def save_config(cfg: dict, filepath: str) -> None:
    """Write config dict to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(cfg, f, indent=2)
    logger.info("Settings saved to: %s", filepath)


def load_config(filepath: str) -> dict:
    """Load JSON config, merging with defaults for forward compat."""
    with open(filepath, 'r') as f:
        loaded = json.load(f)
    cfg = deepcopy(DEFAULT_CONFIG)
    for key, val in loaded.items():
        if key == "features" and isinstance(val, dict):
            for fkey, fval in val.items():
                if fkey in cfg["features"]:
                    if isinstance(fval, dict):
                        cfg["features"][fkey].update(fval)
                    else:
                        cfg["features"][fkey] = fval
                else:
                    cfg["features"][fkey] = fval
        # Backward compat: panel_downtilt_deg -> mechanical_tilt_deg
        elif key == "panel_downtilt_deg" and "mechanical_tilt_deg" not in loaded:
            cfg["mechanical_tilt_deg"] = val
        else:
            cfg[key] = val

    # Backward compat: rename lpda_variation_factor -> variation_factor
    for bw_key in ("freq_dependent_bw_az", "freq_dependent_bw_el"):
        feat = cfg["features"].get(bw_key, {})
        if "lpda_variation_factor" in feat:
            if "variation_factor" not in feat or feat["variation_factor"] == DEFAULT_CONFIG["features"][bw_key]["variation_factor"]:
                feat["variation_factor"] = feat.pop("lpda_variation_factor")
            else:
                feat.pop("lpda_variation_factor", None)

    return cfg


# ===================================================================
#  FREQUENCY GENERATION
# ===================================================================

def generate_frequencies(
    f_min: float, f_max: float, n_slices: int, spacing: str,
) -> list[float]:
    """Generate a list of frequency points.

    First slice is always *f_min*, last is always *f_max*,
    with intermediate slices spaced linearly or logarithmically.

    Args:
        f_min: Lower frequency bound in MHz.
        f_max: Upper frequency bound in MHz.
        n_slices: Number of frequency points.
        spacing: ``'linear'`` or ``'log'``.

    Returns:
        List of frequency values in MHz.

    Raises:
        ValueError: If *n_slices* < 1.
    """
    if n_slices <= 0:
        raise ValueError(
            f"n_slices must be >= 1, got {n_slices}"
        )
    if n_slices == 1:
        return [f_min]
    if spacing == "log":
        if f_min <= 0:
            f_min = 0.001
        log_min = math.log10(f_min)
        log_max = math.log10(f_max)
        freqs = [
            round(10 ** (log_min + i * (log_max - log_min)
                         / (n_slices - 1)), 4)
            for i in range(n_slices)
        ]
    else:
        step = (f_max - f_min) / (n_slices - 1)
        freqs = [
            round(f_min + i * step, 4)
            for i in range(n_slices)
        ]
    # Guarantee endpoints are exact
    freqs[0] = f_min
    freqs[-1] = f_max
    return freqs
