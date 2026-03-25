"""
Sidelobe specification masks and compliance testing.

Supports loading sidelobe envelope masks from files and testing
antenna patterns against them. Includes built-in masks for
common standards:
  - ITU-R S.580-6 (earth station sidelobe reference)
  - ITU-R S.465-6 (earth station antennas)
  - MIL-STD generic envelope
  - Custom piecewise masks from JSON/CSV files

Each mask defines a maximum gain envelope as a function of
off-axis angle. The tool tests a pattern against the mask
at every angle and reports pass/fail with margin.
"""

import json
import math
import os

from typing import Callable

from core.io import read_pattern_csv


# =================================================================
#  BUILT-IN MASKS
# =================================================================

def itu_r_s580(peak_gain_dbi: float) -> Callable[[float], float]:
    """ITU-R S.580-6 reference radiation pattern.

    For earth station antennas operating with GSO satellites.

    Args:
        peak_gain_dbi: Peak antenna gain (dBi).

    Returns:
        Mask function ``f(off_axis_deg) → max_gain_dBi`` with a
        ``.name`` attribute.
    """
    G = peak_gain_dbi

    def mask(theta):
        theta = abs(theta)
        if theta < 1.0:
            return G
        elif theta <= 20.0:
            return 32.0 - 25.0 * math.log10(theta)
        elif theta <= 26.3:
            return -2.0  # ITU plateau
        elif theta <= 48.0:
            return 52.0 - 10.0 * math.log10(4) - 25.0 * math.log10(theta)
        elif theta <= 180.0:
            return -10.0
        return -10.0

    mask.name = "ITU-R S.580-6"
    return mask


def itu_r_s465(D_lambda: float) -> Callable[[float], float]:
    """ITU-R S.465-6 reference radiation pattern.

    Args:
        D_lambda: Antenna diameter in wavelengths (D/λ).

    Returns:
        Mask function ``f(off_axis_deg) → max_gain_dBi`` with a
        ``.name`` attribute.
    """
    G_max = 10.0 * math.log10(
        max(0.6 * (math.pi * D_lambda) ** 2, 1)
    )

    def mask(theta):
        theta = abs(theta)
        if theta < 1.0:
            return G_max
        elif theta <= 20.0:
            return max(32.0 - 25.0 * math.log10(max(theta, 0.1)),
                       -10.0)
        elif theta <= 26.3:
            return -2.0
        elif theta <= 48.0:
            return max(52.0 - 10.0 * math.log10(4)
                       - 25.0 * math.log10(max(theta, 0.1)),
                       -10.0)
        elif theta <= 180.0:
            return -10.0
        return -10.0

    mask.name = f"ITU-R S.465-6 (D/λ={D_lambda:.1f})"
    return mask


def mil_std_envelope(
    peak_gain_dbi: float, first_sll_db: float = -20.0,
) -> Callable[[float], float]:
    """Generic MIL-STD sidelobe envelope.

    Simple linear-in-dB decay envelope for military antennas.

    Args:
        peak_gain_dbi: Peak antenna gain (dBi).
        first_sll_db:  First sidelobe level relative to peak (dB,
                       typically negative).

    Returns:
        Mask function with ``.name`` attribute.
    """
    def mask(theta):
        theta = abs(theta)
        if theta < 1.0:
            return peak_gain_dbi
        elif theta <= 10.0:
            return peak_gain_dbi + first_sll_db + (
                -0.5 * (theta - 1.0))
        elif theta <= 60.0:
            base = peak_gain_dbi + first_sll_db - 4.5
            return base - 0.3 * (theta - 10.0)
        elif theta <= 180.0:
            return peak_gain_dbi + first_sll_db - 19.5 - 0.1 * (
                theta - 60.0)
        return -30.0

    mask.name = "MIL-STD Envelope"
    return mask


def load_mask_from_json(filepath: str) -> Callable[[float], float]:
    """Load a custom piecewise sidelobe mask from JSON.

    Expected format::

        {
          "name": "Custom Mask",
          "points": [
            {"angle_deg": 0, "max_gain_dbi": 30},
            {"angle_deg": 5, "max_gain_dbi": 10},
            ...
          ]
        }

    Piecewise linear interpolation is used between points.
    Extrapolates with the nearest endpoint value.

    Args:
        filepath: Path to the JSON mask definition.

    Returns:
        Mask function with ``.name`` attribute.
    """
    with open(filepath, 'r') as f:
        spec = json.load(f)

    points = spec["points"]
    points.sort(key=lambda p: p["angle_deg"])
    angles = [p["angle_deg"] for p in points]
    gains = [p["max_gain_dbi"] for p in points]

    def mask(theta):
        theta = abs(theta)
        if theta <= angles[0]:
            return gains[0]
        if theta >= angles[-1]:
            return gains[-1]
        for i in range(len(angles) - 1):
            if angles[i] <= theta <= angles[i + 1]:
                t = ((theta - angles[i])
                     / (angles[i + 1] - angles[i]))
                return gains[i] + t * (gains[i + 1]
                                       - gains[i])
        return gains[-1]

    mask.name = spec.get("name", "Custom Mask")
    return mask


# ===================================================================
#  COMPLIANCE TESTING
# ===================================================================

def test_pattern_against_mask(
    pattern_file: str,
    mask_func: Callable[[float], float],
    plane: str = "az",
) -> dict:
    """Test an antenna pattern against a sidelobe mask.

    Args:
        pattern_file: CSV file path.
        mask_func:    Mask function ``angle → max_dBi``.
        plane:        ``'az'`` or ``'el'`` — which principal cut to test.

    Returns:
        Dict with keys: ``file``, ``mask``, ``plane``, ``peak_gain``,
        ``passed`` (bool), ``n_violations``, ``min_margin_db``,
        ``violations`` (list of violation dicts).
    """
    az, el, data = read_pattern_csv(pattern_file)

    # Get boresight and the selected cut
    el0 = len(el) // 2
    az0 = len(az) // 2
    for idx, e in enumerate(el):
        if abs(e) < 0.01:
            el0 = idx
            break
    for idx, a in enumerate(az):
        if abs(a) < 0.01:
            az0 = idx
            break

    if plane == "az":
        angles = az
        gains = data[el0]
    else:
        angles = el
        gains = [data[i][az0] for i in range(len(el))]

    # Find peak and its index
    peak_gain = max(gains)

    violations = []
    min_margin = 999.0

    for i, (angle, gain) in enumerate(zip(angles, gains)):
        max_allowed = mask_func(angle)
        margin = max_allowed - gain
        if margin < min_margin:
            min_margin = margin
        if gain > max_allowed:
            violations.append({
                'angle': angle,
                'gain': gain,
                'max_allowed': max_allowed,
                'excess': gain - max_allowed,
            })

    passed = len(violations) == 0

    result = {
        'file': pattern_file,
        'mask': getattr(mask_func, 'name', 'Unknown'),
        'plane': plane,
        'peak_gain': peak_gain,
        'passed': passed,
        'n_violations': len(violations),
        'min_margin_db': round(min_margin, 2),
        'violations': violations,
    }

    # Print report
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\n  Sidelobe Mask Compliance: {status}")
    print(f"    Mask           : "
          f"{getattr(mask_func, 'name', 'Unknown')}")
    print(f"    Pattern        : "
          f"{os.path.basename(pattern_file)}")
    print(f"    Plane          : {plane.upper()}")
    print(f"    Peak gain      : {peak_gain:.1f} dBi")
    print(f"    Min margin     : {min_margin:.1f} dB")

    if violations:
        print(f"    Violations     : {len(violations)}")
        # Show worst 5
        worst = sorted(violations,
                       key=lambda v: -v['excess'])[:5]
        for v in worst:
            print(f"      {v['angle']:+.0f}° : "
                  f"{v['gain']:.1f} dBi "
                  f"(limit {v['max_allowed']:.1f}, "
                  f"excess +{v['excess']:.1f} dB)")
    else:
        print(f"    All sidelobes within mask.")

    return result
