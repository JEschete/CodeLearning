"""
Diagnostic test suite for the ±90° azimuth boundary discontinuity.

Problem
-------
Directional antenna types (LPDA, Panel, Horn, Dish) use a hard
``cos_az > 0`` check to gate the front beam contribution.  At exactly
±90° azimuth, cos(az) = 0, so the front beam abruptly drops to zero
while the back-lobe formula picks up at back_weight = 0.5.  When the
main beam is wide enough to still have significant gain at ±90° (low
frequencies → wide beamwidth), this creates a visible hard line in
the heatmap.

These tests quantify the discontinuity across frequencies, beamwidths,
and antenna types so we can verify that any fix eliminates it.

Run
---
    python -m pytest tests/test_boundary_discontinuity.py -v
    python tests/test_boundary_discontinuity.py           # standalone
"""

import math
import sys
import os

# ── Make workspace root importable ──────────────────────────────
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from antennas import get_antenna
from core.pattern_math import bw_to_exponent


# ===================================================================
#  HELPERS
# ===================================================================

def _default_cfg(antenna_type="LPDA", az_bw=65.0, el_bw=70.0,
                 max_gain=7.0, ftb=15.0):
    """Build a minimal config dict suitable for compute_point_gain."""
    return {
        "antenna_type": antenna_type,
        "az_beamwidth_deg": az_bw,
        "el_beamwidth_deg": el_bw,
        "max_gain_dbi": max_gain,
        "ftb_ratio_db": ftb,
        "noise_range_db": 0,
        "f_min_mhz": 30,
        "f_max_mhz": 1000,
        "ref_freq_mhz": 500,
        # Panel extras
        "panel_downtilt_deg": 0.0,
        # Dish extras
        "dish_efficiency": 0.60,
        # Horn extras – none needed beyond ftb
        # Feature flags – all off for isolation
        "features": {
            "freq_dependent_bw_az": {"enabled": False},
            "freq_dependent_bw_el": {"enabled": False},
            "sidelobes": {"enabled": False},
            "pattern_breakup": {"enabled": False},
            "ground_reflection": {"enabled": False},
            "asymmetry": {"enabled": False},
            "cross_pol": {"enabled": False},
            "vswr_rolloff": {"enabled": False},
        },
    }


def _gain_db(antenna, az, el, cfg, az_bw=None, el_bw=None):
    """Compute scalar gain (dB) at a single (az, el) point."""
    if az_bw is None:
        az_bw = cfg["az_beamwidth_deg"]
    if el_bw is None:
        el_bw = cfg["el_beamwidth_deg"]

    n_az = bw_to_exponent(az_bw)
    n_el = bw_to_exponent(el_bw)
    gain_peak = 10 ** (cfg["max_gain_dbi"] / 10.0)  # linear

    az_rad = math.radians(az)
    el_rad = math.radians(el)
    cos_az = math.cos(az_rad)
    cos_el = math.cos(el_rad)

    g_lin = antenna.compute_point_gain(
        az, el, cos_az, cos_el,
        n_az, n_el, az_bw, el_bw,
        gain_peak, cfg,
    )
    if g_lin <= 0:
        return -999.0
    return 10 * math.log10(g_lin)


def _gain_db_vec(antenna, az_arr, el_val, cfg,
                 az_bw=None, el_bw=None):
    """Vectorized gain (dB) along an azimuth sweep at fixed elevation.

    Returns np.ndarray of dB values, same length as *az_arr*.
    """
    if not HAS_NUMPY:
        return np.array([
            _gain_db(antenna, a, el_val, cfg, az_bw, el_bw)
            for a in az_arr
        ])

    from core.engine import _vectorized_antenna_gain

    if az_bw is None:
        az_bw = cfg["az_beamwidth_deg"]
    if el_bw is None:
        el_bw = cfg["el_beamwidth_deg"]

    n_az = bw_to_exponent(az_bw)
    n_el = bw_to_exponent(el_bw)
    gain_peak = 10 ** (cfg["max_gain_dbi"] / 10.0)

    az_np = np.array(az_arr, dtype=np.float64)
    el_np = np.full_like(az_np, el_val)

    az_rad = np.radians(az_np)
    el_rad = np.radians(el_np)
    cos_az = np.cos(az_rad)
    cos_el = np.cos(el_rad)

    # _vectorized_antenna_gain expects 2-D grids
    az_eff = az_np.reshape(1, -1)
    el_eff = el_np.reshape(1, -1)
    cos_az_2d = cos_az.reshape(1, -1)
    cos_el_2d = cos_el.reshape(1, -1)

    g_lin = _vectorized_antenna_gain(
        antenna, az_eff, el_eff, cos_az_2d, cos_el_2d,
        n_az, n_el, az_bw, el_bw, gain_peak, cfg,
    )
    g_lin = g_lin.flatten()
    g_lin = np.maximum(g_lin, 1e-30)
    return 10 * np.log10(g_lin)


# ===================================================================
#  DIRECTIONAL ANTENNA TYPES TO TEST
# ===================================================================
DIRECTIONAL_TYPES = ["LPDA", "Panel", "Horn", "Dish"]


# ===================================================================
#  TEST 1 — Point-wise discontinuity at ±90° (scalar path)
# ===================================================================

def test_boundary_jump_scalar():
    """Measure gain jump across the ±90° boundary (scalar path).

    For each directional type, sweep az from 85° to 95° in 0.1°
    steps at el=0°.  Compute the maximum single-step dB jump.
    A smooth pattern should have < 1 dB step at 0.1° resolution.
    """
    results = {}
    for atype in DIRECTIONAL_TYPES:
        antenna = get_antenna(atype)
        cfg = _default_cfg(antenna_type=atype, az_bw=65.0,
                           el_bw=70.0)
        # Sweep 85° → 95° in 0.1° steps
        azimuths = [85.0 + i * 0.1 for i in range(101)]
        gains = [_gain_db(antenna, az, 0.0, cfg) for az in azimuths]

        # Max step
        max_jump = 0.0
        jump_at = None
        for i in range(1, len(gains)):
            delta = abs(gains[i] - gains[i - 1])
            if delta > max_jump:
                max_jump = delta
                jump_at = azimuths[i]

        results[atype] = {
            "max_jump_db": round(max_jump, 3),
            "jump_at_deg": jump_at,
            "gain_at_89.9": round(
                _gain_db(antenna, 89.9, 0.0, cfg), 3),
            "gain_at_90.0": round(
                _gain_db(antenna, 90.0, 0.0, cfg), 3),
            "gain_at_90.1": round(
                _gain_db(antenna, 90.1, 0.0, cfg), 3),
        }

    print("\n" + "=" * 65)
    print("TEST 1: Scalar boundary jump at ±90° (el=0°, az_bw=65°)")
    print("=" * 65)
    for atype, r in results.items():
        print(f"\n  {atype}:")
        print(f"    Max step jump : {r['max_jump_db']:>8.3f} dB "
              f"at az = {r['jump_at_deg']:.1f}°")
        print(f"    Gain @ 89.9°  : {r['gain_at_89.9']:>8.3f} dBi")
        print(f"    Gain @ 90.0°  : {r['gain_at_90.0']:>8.3f} dBi")
        print(f"    Gain @ 90.1°  : {r['gain_at_90.1']:>8.3f} dBi")
        jump = abs(r["gain_at_89.9"] - r["gain_at_90.1"])
        verdict = "PASS (smooth)" if jump < 1.0 else "FAIL (hard line)"
        print(f"    89.9→90.1 gap : {jump:>8.3f} dB  → {verdict}")

    # Hard assertion: every type should be < 1 dB step across 0.2°
    for atype, r in results.items():
        gap = abs(r["gain_at_89.9"] - r["gain_at_90.1"])
        assert gap < 1.0, (
            f"{atype}: {gap:.3f} dB jump across 89.9°→90.1° "
            f"(threshold 1.0 dB)"
        )


# ===================================================================
#  TEST 2 — Vectorized path matches scalar path
# ===================================================================

def test_scalar_vs_vectorized_at_boundary():
    """Ensure the vectorized (NumPy) path produces the same boundary
    behaviour as the scalar (pure-Python) path.

    Any mismatch suggests the fix was applied to only one path.
    """
    if not HAS_NUMPY:
        print("SKIP: NumPy not available")
        return

    print("\n" + "=" * 65)
    print("TEST 2: Scalar vs vectorized agreement at ±90°")
    print("=" * 65)

    for atype in DIRECTIONAL_TYPES:
        antenna = get_antenna(atype)
        cfg = _default_cfg(antenna_type=atype, az_bw=65.0,
                           el_bw=70.0)
        test_points = [89.0, 89.5, 89.9, 90.0, 90.1, 90.5, 91.0]
        scalar = [_gain_db(antenna, az, 0.0, cfg)
                  for az in test_points]
        vec = _gain_db_vec(
            antenna, test_points, 0.0, cfg
        )

        print(f"\n  {atype}:")
        all_ok = True
        for i, az in enumerate(test_points):
            diff = abs(scalar[i] - vec[i])
            ok = diff < 0.5  # allow small numerical diff
            tag = "OK" if ok else "MISMATCH"
            if not ok:
                all_ok = False
            print(f"    az={az:6.1f}°  scalar={scalar[i]:>8.3f}  "
                  f"vec={vec[i]:>8.3f}  diff={diff:.3f} {tag}")
        assert all_ok, (
            f"{atype}: Scalar/vectorized mismatch > 0.5 dB near ±90°"
        )


# ===================================================================
#  TEST 3 — Beamwidth dependence: wider BW → bigger jump
# ===================================================================

def test_beamwidth_vs_jump():
    """Sweep beamwidth from 30° to 120° and measure the boundary jump.

    Wider beamwidth means more gain at ±90°, so the front/back
    hard-clip discontinuity should be worse. This confirms the root
    cause is the `cos_az > 0` gate.
    """
    print("\n" + "=" * 65)
    print("TEST 3: Beamwidth dependence of boundary jump (LPDA)")
    print("=" * 65)

    antenna = get_antenna("LPDA")
    beamwidths = [30, 45, 60, 65, 80, 90, 100, 120]

    print(f"\n  {'BW (°)':>8}  {'G@89.9°':>10}  {'G@90.0°':>10}  "
          f"{'G@90.1°':>10}  {'Jump (dB)':>10}  {'Verdict'}")
    print("  " + "-" * 70)

    jumps = []
    for bw in beamwidths:
        cfg = _default_cfg(az_bw=bw, el_bw=bw)
        g_pre = _gain_db(antenna, 89.9, 0.0, cfg, az_bw=bw,
                         el_bw=bw)
        g_at = _gain_db(antenna, 90.0, 0.0, cfg, az_bw=bw,
                        el_bw=bw)
        g_post = _gain_db(antenna, 90.1, 0.0, cfg, az_bw=bw,
                          el_bw=bw)
        jump = abs(g_pre - g_post)
        jumps.append(jump)
        verdict = "OK" if jump < 1.0 else "HARD LINE"
        print(f"  {bw:>6}°  {g_pre:>10.3f}  {g_at:>10.3f}  "
              f"{g_post:>10.3f}  {jump:>10.3f}  {verdict}")

    # With BW >= 60°, jump should still be < 1 dB for a smooth pattern
    for bw, jump in zip(beamwidths, jumps):
        assert jump < 1.0, (
            f"BW={bw}°: {jump:.3f} dB jump across 89.9→90.1° "
            f"(threshold 1.0 dB)"
        )


# ===================================================================
#  TEST 4 — Full azimuth sweep: check continuity everywhere
# ===================================================================

def test_full_azimuth_continuity():
    """Sweep az from -180° to +180° at 0.5° steps and ensure no
    single step exceeds 2 dB anywhere in the pattern.
    """
    print("\n" + "=" * 65)
    print("TEST 4: Full azimuth continuity (el=0°, 0.5° steps)")
    print("=" * 65)

    for atype in DIRECTIONAL_TYPES:
        antenna = get_antenna(atype)
        cfg = _default_cfg(antenna_type=atype, az_bw=65.0,
                           el_bw=70.0)
        azimuths = [i * 0.5 for i in range(-360, 361)]
        gains = [_gain_db(antenna, az, 0.0, cfg) for az in azimuths]

        max_jump = 0.0
        jump_at = None
        for i in range(1, len(gains)):
            delta = abs(gains[i] - gains[i - 1])
            if delta > max_jump:
                max_jump = delta
                jump_at = azimuths[i]

        verdict = "PASS" if max_jump < 2.0 else "FAIL"
        print(f"  {atype:>8}: max step = {max_jump:.3f} dB "
              f"at az = {jump_at:.1f}°  → {verdict}")

        assert max_jump < 2.0, (
            f"{atype}: {max_jump:.3f} dB step at az={jump_at:.1f}° "
            f"(threshold 2.0 dB)"
        )


# ===================================================================
#  TEST 5 — Elevation sweep at az = 90° (the seam)
# ===================================================================

def test_elevation_sweep_at_90():
    """At az=90° (exactly on the seam), sweep el from -90° to +90°.

    The gain should still form a smooth curve, not a flat line at
    the back-lobe floor.  If `cos_az > 0` kills the front beam,
    we'll see only the back lobe here.
    """
    print("\n" + "=" * 65)
    print("TEST 5: Elevation sweep at az = 90° (on the seam)")
    print("=" * 65)

    antenna = get_antenna("LPDA")
    cfg = _default_cfg(az_bw=65.0, el_bw=70.0)

    elevations = list(range(-90, 91, 5))
    gains = [_gain_db(antenna, 90.0, el, cfg) for el in elevations]

    # Compare with front-side reference at az=89°
    gains_just_inside = [_gain_db(antenna, 89.0, el, cfg)
                         for el in elevations]

    print(f"\n  {'El (°)':>8}  {'G@az=90°':>10}  {'G@az=89°':>10}  "
          f"{'Gap (dB)':>10}")
    print("  " + "-" * 48)
    worst_gap = 0.0
    for el, g90, g89 in zip(elevations, gains, gains_just_inside):
        gap = abs(g89 - g90)
        if gap > worst_gap:
            worst_gap = gap
        print(f"  {el:>6}°  {g90:>10.3f}  {g89:>10.3f}  {gap:>10.3f}")

    print(f"\n  Worst gap (az=89° vs az=90°): {worst_gap:.3f} dB")
    verdict = "PASS" if worst_gap < 3.0 else "FAIL (hard line)"
    print(f"  → {verdict}")

    assert worst_gap < 3.0, (
        f"LPDA: {worst_gap:.3f} dB gap between az=89° and az=90° "
        f"(threshold 3.0 dB)"
    )


# ===================================================================
#  TEST 6 — Frequency-dependent beamwidth → hard line at low freq
# ===================================================================

def test_frequency_dependent_boundary():
    """Simulate freq-dependent BW: at low freq, BW is wider and the
    boundary artifact should be worse.

    Uses three frequencies to demonstrate the effect:
    - Low  freq (30 MHz)  → very wide BW → large jump
    - Mid  freq (200 MHz) → moderate BW  → medium jump
    - High freq (1000 MHz)→ narrow BW    → small/no jump
    """
    print("\n" + "=" * 65)
    print("TEST 6: Frequency-dependent beamwidth → boundary jump")
    print("=" * 65)

    antenna = get_antenna("LPDA")
    # Simulate what happens: at 30 MHz with ref=500 MHz, BW opens up
    # We'll manually set BW as if freq-dependent scaling applied
    freq_bw_pairs = [
        (30,   120.0, 130.0),  # very wide at bottom of band
        (64,    95.0, 100.0),  # wide (matches ~64 MHz plot)
        (200,   70.0,  75.0),  # moderate
        (500,   65.0,  70.0),  # reference
        (1000,  45.0,  50.0),  # narrow at top of band
    ]

    print(f"\n  {'Freq':>8}  {'AzBW':>6}  {'ElBW':>6}  "
          f"{'G@89.9':>8}  {'G@90.1':>8}  {'Jump':>8}  Verdict")
    print("  " + "-" * 65)

    for freq, az_bw, el_bw in freq_bw_pairs:
        cfg = _default_cfg(az_bw=az_bw, el_bw=el_bw)
        g_pre = _gain_db(antenna, 89.9, 0.0, cfg,
                         az_bw=az_bw, el_bw=el_bw)
        g_post = _gain_db(antenna, 90.1, 0.0, cfg,
                          az_bw=az_bw, el_bw=el_bw)
        jump = abs(g_pre - g_post)
        verdict = "OK" if jump < 1.0 else "HARD LINE"
        print(f"  {freq:>5} MHz  {az_bw:>5.0f}°  {el_bw:>5.0f}°  "
              f"{g_pre:>8.3f}  {g_post:>8.3f}  {jump:>8.3f}  "
              f"{verdict}")


# ===================================================================
#  TEST 7 — Negative azimuth boundary at -90°
# ===================================================================

def test_negative_boundary():
    """Same check at az = -90° to confirm both walls behave identically.
    """
    print("\n" + "=" * 65)
    print("TEST 7: Negative boundary at az = -90° (LPDA)")
    print("=" * 65)

    antenna = get_antenna("LPDA")
    cfg = _default_cfg(az_bw=65.0, el_bw=70.0)

    check_points = [-91.0, -90.5, -90.1, -90.0, -89.9, -89.5, -89.0]
    gains = [_gain_db(antenna, az, 0.0, cfg) for az in check_points]

    print(f"\n  {'Az (°)':>8}  {'Gain (dBi)':>12}")
    print("  " + "-" * 24)
    for az, g in zip(check_points, gains):
        print(f"  {az:>7.1f}°  {g:>12.3f}")

    jump = abs(gains[2] - gains[4])  # -90.1 vs -89.9
    print(f"\n  Jump across -90°: {jump:.3f} dB")

    # Check symmetry with +90°
    g_pos_pre = _gain_db(antenna, 89.9, 0.0, cfg)
    g_neg_pre = _gain_db(antenna, -89.9, 0.0, cfg)
    sym_diff = abs(g_pos_pre - g_neg_pre)
    print(f"  Symmetry (89.9° vs -89.9°): {sym_diff:.3f} dB diff")

    assert jump < 1.0, (
        f"LPDA: {jump:.3f} dB jump at -90° (threshold 1.0 dB)"
    )


# ===================================================================
#  TEST 8 — Gains should be physically reasonable at ±90°
# ===================================================================

def test_gain_reasonableness_at_boundary():
    """At ±90° (endfire), gain should be between the back-lobe floor
    and the front-beam value.  It should NOT be -999 or -inf.
    """
    print("\n" + "=" * 65)
    print("TEST 8: Gain reasonableness at ±90° boundary")
    print("=" * 65)

    for atype in DIRECTIONAL_TYPES:
        antenna = get_antenna(atype)
        cfg = _default_cfg(antenna_type=atype, az_bw=65.0,
                           el_bw=70.0)
        g_bore = _gain_db(antenna, 0.0, 0.0, cfg)
        g_90 = _gain_db(antenna, 90.0, 0.0, cfg)
        g_180 = _gain_db(antenna, 180.0, 0.0, cfg)

        # At endfire, gain should be between boresight and back
        reasonable = (g_90 <= g_bore) and (g_90 >= g_180 - 10)
        # Must not be -999 (our sentinel for g_lin=0)
        finite = g_90 > -200

        print(f"  {atype:>8}: bore={g_bore:.1f}  90°={g_90:.1f}  "
              f"180°={g_180:.1f}  "
              f"{'OK' if (reasonable and finite) else 'BAD'}")

        assert finite, (
            f"{atype}: Gain at 90° is {g_90:.1f} (should be finite)"
        )


# ===================================================================
#  TEST 9 — Diagnostic: dump the front/back contributions separately
# ===================================================================

def test_front_back_decomposition():
    """Decompose the LPDA gain into front and back contributions
    around ±90° to visualise the smooth sigmoid blending.
    """
    print("\n" + "=" * 65)
    print("TEST 9: Front/back decomposition around 90° (LPDA)")
    print("=" * 65)

    cfg = _default_cfg(az_bw=65.0, el_bw=70.0)
    gain_peak = 10 ** (cfg["max_gain_dbi"] / 10.0)
    ftb_lin = 10 ** (-abs(cfg["ftb_ratio_db"]) / 10.0)
    az_hw = cfg["az_beamwidth_deg"] / 2.0
    el_hw = cfg["el_beamwidth_deg"] / 2.0
    n_el = bw_to_exponent(cfg["el_beamwidth_deg"])

    from core.pattern_math import front_fade_scalar

    print(f"\n  {'Az (°)':>8}  {'cos(az)':>9}  {'fade':>6}  "
          f"{'Front':>8}  {'Back':>8}  {'Total':>8}")
    print("  " + "-" * 60)

    for az in [85, 87, 89, 89.5, 89.9, 90.0, 90.1, 90.5, 91, 93, 95]:
        az_rad = math.radians(az)
        cos_az = math.cos(az_rad)
        cos_el = math.cos(0.0)  # el = 0
        el_eff = 0.0

        # Front contribution with sigmoid fade
        ff = front_fade_scalar(cos_az)
        if az_hw > 0 and el_hw > 0:
            r_sq = (az / az_hw) ** 2 + (el_eff / el_hw) ** 2
            g_front = gain_peak * (0.5 ** r_sq) * ff
        else:
            g_front = 0.0

        # Back contribution
        back_weight = (1.0 - cos_az) / 2.0
        el_n_back = max(n_el * 0.5, 1.0)
        back_el = max(abs(cos_el), 1e-12) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el

        total = max(g_front, g_back)
        f_db = 10 * math.log10(g_front) if g_front > 0 else -999.0
        b_db = 10 * math.log10(g_back) if g_back > 0 else -999.0
        t_db = 10 * math.log10(total) if total > 0 else -999.0

        print(f"  {az:>7.1f}°  {cos_az:>9.6f}  {ff:>5.3f}  "
              f"{f_db:>8.2f}  {b_db:>8.2f}  {t_db:>8.2f}")


# ===================================================================
#  TEST 10 — First derivative (dG/dAz) spike detection
# ===================================================================

def test_derivative_spike():
    """Compute numerical dG/dAz around ±90° and check for spikes.

    A smooth pattern should have a smoothly varying derivative.
    A hard line shows up as a spike in the derivative.
    """
    print("\n" + "=" * 65)
    print("TEST 10: Derivative spike detection (LPDA, el=0°)")
    print("=" * 65)

    antenna = get_antenna("LPDA")
    cfg = _default_cfg(az_bw=65.0, el_bw=70.0)

    step = 0.1
    azimuths = [80.0 + i * step for i in range(201)]  # 80° to 100°
    gains = [_gain_db(antenna, az, 0.0, cfg) for az in azimuths]

    # First derivative (dB/deg)
    derivs = [(gains[i] - gains[i - 1]) / step
              for i in range(1, len(gains))]
    deriv_az = [azimuths[i] for i in range(1, len(azimuths))]

    # Find peak derivative magnitude
    max_deriv = 0.0
    max_deriv_az = None
    for az, d in zip(deriv_az, derivs):
        if abs(d) > max_deriv:
            max_deriv = abs(d)
            max_deriv_az = az

    print(f"\n  Peak |dG/dAz| = {max_deriv:.2f} dB/deg "
          f"at az = {max_deriv_az:.1f}°")

    # For reference: expected derivative of a smooth Gaussian:
    # dG/dAz ~ -2 * ln(0.5) * az / hw² * gain * ln(10)/10
    # At az=90°, hw=32.5°: ~1-2 dB/deg is normal far off-axis.
    # A spike > 10 dB/deg means hard cutoff.
    threshold = 10.0  # dB/deg
    verdict = ("PASS (smooth)" if max_deriv < threshold
               else "FAIL (derivative spike = hard line)")
    print(f"  Threshold: {threshold} dB/deg  → {verdict}")

    # Print derivative around the 90° region
    print(f"\n  {'Az (°)':>8}  {'dG/dAz':>10}")
    print("  " + "-" * 22)
    for az, d in zip(deriv_az, derivs):
        if 88.0 <= az <= 92.0:
            marker = " <<<" if abs(d) > threshold else ""
            print(f"  {az:>7.1f}°  {d:>10.2f}{marker}")

    assert max_deriv < threshold, (
        f"LPDA: derivative spike {max_deriv:.1f} dB/deg at "
        f"az={max_deriv_az:.1f}° (threshold {threshold})"
    )


# ===================================================================
#  RUNNER
# ===================================================================

def run_all():
    """Run all diagnostic tests and give a summary."""
    tests = [
        ("1 — Boundary jump (scalar)",       test_boundary_jump_scalar),
        ("2 — Scalar vs vectorized",         test_scalar_vs_vectorized_at_boundary),
        ("3 — Beamwidth dependence",         test_beamwidth_vs_jump),
        ("4 — Full azimuth continuity",      test_full_azimuth_continuity),
        ("5 — Elevation at 90°",             test_elevation_sweep_at_90),
        ("6 — Frequency-dependent BW",       test_frequency_dependent_boundary),
        ("7 — Negative boundary (-90°)",     test_negative_boundary),
        ("8 — Gain reasonableness",          test_gain_reasonableness_at_boundary),
        ("9 — Front/back decomposition",     test_front_back_decomposition),
        ("10 — Derivative spike",            test_derivative_spike),
    ]

    passed = 0
    failed = 0
    errors = []

    for label, fn in tests:
        try:
            fn()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append((label, str(e)))
        except Exception as e:
            failed += 1
            errors.append((label, f"ERROR: {e}"))

    print("\n" + "=" * 65)
    print(f"SUMMARY: {passed} passed, {failed} failed out of "
          f"{len(tests)}")
    print("=" * 65)
    for label, msg in errors:
        print(f"  FAIL  {label}")
        print(f"        {msg}")

    if failed == 0:
        print("  All tests passed — the boundary is smooth!")
    else:
        print(f"\n  {failed} test(s) detected the hard-line artifact.")
        print("  Root cause: `cos_az > 0` gate in front-beam code.")
        print("  Fix: replace hard gate with smooth sigmoid blend.")

    return failed


if __name__ == "__main__":
    failures = run_all()
    sys.exit(1 if failures else 0)
