"""
Shared pattern math functions.

These are the building blocks used by the engine and by individual
antenna type implementations. No UI or I/O dependencies.
"""

import math


# ═══════════════════════════════════════════════════════════════════
#  FRONT-HEMISPHERE SIGMOID BLEND
# ═══════════════════════════════════════════════════════════════════

# Steepness for the front-hemisphere sigmoid.
# k = 40 gives a ~±5° transition zone around ±90° azimuth,
# eliminating the visible hard line in heatmaps while keeping
# the front/back separation physically meaningful.
_SIGMOID_K = 40.0


def front_fade_scalar(cos_az: float, k: float = _SIGMOID_K) -> float:
    """Smooth sigmoid front-hemisphere weight.

    Returns ~1.0 at boresight (*cos_az* = 1), 0.5 at ±90°,
    ~0.0 in the back hemisphere (*cos_az* = −1).  Replaces the
    hard ``cos_az > 0`` gate that caused the ±90° heatmap artefact.

    Args:
        cos_az: Cosine of the azimuth angle.
        k: Sigmoid steepness.  Higher values give a sharper
           transition at ±90°.  Default ``40`` ≈ 10° zone;
           ``12`` ≈ 30° zone (more realistic).

    Returns:
        Sigmoid weight in the range (0, 1).
    """
    return 1.0 / (1.0 + math.exp(-k * cos_az))


# ═══════════════════════════════════════════════════════════════════
#  BEAMWIDTH / EXPONENT CONVERSION
# ═══════════════════════════════════════════════════════════════════

def bw_to_exponent(bw_deg: float) -> float:
    """Convert 3 dB beamwidth (degrees) to cos^n exponent.

    Solves ``cos(bw/2)^n = 0.5`` ⇒ ``n = ln(0.5) / ln(cos(bw/2))``.

    Args:
        bw_deg: Half-power beamwidth in degrees.

    Returns:
        Exponent *n* for cos^n beam model.
    """
    half = math.radians(bw_deg / 2.0)
    c = math.cos(half)
    if c <= 0 or c >= 1:
        return 1.0
    return math.log(0.5) / math.log(c)


# ═══════════════════════════════════════════════════════════════════
#  FREQUENCY-DEPENDENT BEAMWIDTH
# ═══════════════════════════════════════════════════════════════════

def compute_freq_dependent_bw(
    base_bw: float,
    freq: float,
    ref_freq: float,
    cfg: dict,
    plane: str = "az",
) -> float:
    """Compute beamwidth at a given frequency.

    Args:
        base_bw:  beamwidth (deg) at the reference frequency
        freq:     target frequency (MHz)
        ref_freq: reference frequency (MHz)
        cfg:      full config dict
        plane:    "az" or "el" — selects which feature config
                  to use (freq_dependent_bw_az or _el)

    Modes:
      exponent   - BW = base * (f_ref/f)^exp
      percentage - BW decays by X% per octave from ref freq
      three_point - quadratic Lagrange fit through 3 user values
    """
    feat_key = f"freq_dependent_bw_{plane}"
    feat = cfg["features"].get(feat_key)
    # Backwards compat: fall back to old single key
    if feat is None:
        feat = cfg["features"].get("freq_dependent_bw")
    if feat is None or not feat["enabled"] or ref_freq <= 0:
        return base_bw

    mode = feat.get("decay_mode", "exponent")

    if mode == "percentage":
        pct = feat.get("decay_pct_per_octave", 15.0)
        if pct == 0:
            return base_bw
        if freq <= 0 or ref_freq <= 0:
            return base_bw
        octaves = math.log2(freq / ref_freq)
        scale = 1.0 - (pct / 100.0) * octaves
        new_bw = base_bw * max(scale, 0.05)

    elif mode == "three_point":
        f_min = cfg["f_min_mhz"]
        f_max = cfg["f_max_mhz"]
        bw_start = (
            feat.get("three_point_start_deg") or base_bw
        )
        bw_mid = (
            feat.get("three_point_mid_deg") or base_bw
        )
        bw_end = (
            feat.get("three_point_end_deg") or base_bw
        )
        if f_max == f_min:
            t = 0.5
        else:
            t = (freq - f_min) / (f_max - f_min)
        t = max(0.0, min(1.0, t))
        # Quadratic Lagrange interpolation
        # t=0 -> bw_start, t=0.5 -> bw_mid, t=1.0 -> bw_end
        L0 = 2.0 * (t - 0.5) * (t - 1.0)
        L1 = -4.0 * t * (t - 1.0)
        L2 = 2.0 * t * (t - 0.5)
        new_bw = bw_start * L0 + bw_mid * L1 + bw_end * L2

    else:  # "exponent" (default)
        ratio = ref_freq / freq
        # variation_factor damps the exponent scaling.
        # 0 = constant BW, 1 = full aperture scaling.
        # Backward compat: accept old key lpda_variation_factor.
        var = feat.get("variation_factor",
                       feat.get("lpda_variation_factor", 1.0))
        if var < 1.0:
            scale = 1.0 + var * (
                ratio ** feat["scaling_exponent"] - 1.0
            )
        else:
            scale = ratio ** feat["scaling_exponent"]
        new_bw = base_bw * scale

    return max(
        feat["min_bw_deg"],
        min(feat["max_bw_deg"], new_bw)
    )


# ═══════════════════════════════════════════════════════════════════
#  SIDELOBE ENVELOPE
# ═══════════════════════════════════════════════════════════════════

def compute_sidelobe_envelope(
    angle_off_axis: float, beamwidth: float, cfg: dict,
) -> float:
    """Compute sidelobe gain (linear) at a given angle.

    Supports two sidelobe models:
      taylor  - decaying sidelobes (first_sl * decay^n)
      uniform - equal-amplitude sidelobes (no decay)
    """
    feat = cfg["features"]["sidelobes"]
    if not feat["enabled"] or beamwidth <= 0:
        return 0.0
    u = abs(angle_off_axis) / beamwidth
    if u < 0.7:
        return 0.0
    first_sl_lin = 10 ** (feat["first_sidelobe_db"] / 10.0)
    sl_type = feat.get("type", "taylor")
    if sl_type == "uniform":
        decay_lin = 1.0  # no decay between lobes
    else:
        decay_lin = 10 ** (-feat["decay_rate_db"] / 10.0)
    sl_index = int((u - 0.7) / 0.8)
    n_sl = feat["n_sidelobes"]
    if sl_index < n_sl:
        sl_amp = first_sl_lin * (decay_lin ** sl_index)
        phase = math.pi * ((u - 0.7) / 0.8 - sl_index)
        return sl_amp * (math.cos(phase) ** 2)
    else:
        # Smooth taper beyond last sidelobe instead of
        # hard cutoff to zero. Amplitude at last lobe edge
        # decays exponentially with continued distance.
        last_amp = first_sl_lin * (decay_lin ** (n_sl - 1))
        u_end = 0.7 + n_sl * 0.8
        extra = (u - u_end) / 0.8  # additional lobe-widths
        return last_amp * decay_lin * math.exp(-2.0 * extra)


def compute_sidelobe_radial(
    az_eff: float, el_eff: float,
    az_bw: float, el_bw: float,
    cfg: dict,
) -> float:
    """Compute sidelobe gain using radial off-axis angle.

    Instead of separate az/el sidelobes combined with max()
    (which creates rectangular bands), this computes a single
    sidelobe value based on the total off-axis angle, using
    an elliptical effective beamwidth that accounts for the
    beam aspect ratio. Produces circular/elliptical sidelobe
    rings.
    """
    feat = cfg["features"]["sidelobes"]
    if not feat["enabled"]:
        return 0.0
    if az_bw <= 0 or el_bw <= 0:
        return 0.0

    off_axis = math.sqrt(az_eff**2 + el_eff**2)
    if off_axis < 1e-6:
        return 0.0

    # Effective beamwidth in the direction of the off-axis
    # point (elliptical model). At 0° it's az_bw, at 90°
    # it's el_bw, smoothly interpolated between.
    angle_in_plane = math.atan2(
        abs(el_eff), abs(az_eff) + 1e-10
    )
    cos_a = math.cos(angle_in_plane)
    sin_a = math.sin(angle_in_plane)
    # Elliptical interpolation of beamwidth
    bw_eff = 1.0 / math.sqrt(
        (cos_a / az_bw) ** 2 + (sin_a / el_bw) ** 2
    )

    return compute_sidelobe_envelope(off_axis, bw_eff, cfg)


# ═══════════════════════════════════════════════════════════════════
#  PATTERN BREAKUP
# ═══════════════════════════════════════════════════════════════════

def apply_pattern_breakup(
    gain_linear: float, az: float, el: float, cfg: dict,
) -> float:
    """Apply deterministic ripple at high off-axis angles.

    Args:
        gain_linear: Current gain in linear scale.
        az:          Azimuth angle (degrees).
        el:          Elevation angle (degrees).
        cfg:         Full config dict.

    Returns:
        Modified gain (linear) with ripple applied.
    """
    feat = cfg["features"]["pattern_breakup"]
    if not feat["enabled"]:
        return gain_linear
    off_axis = math.sqrt(az**2 + el**2)
    if off_axis < feat["onset_angle_deg"]:
        return gain_linear
    severity = min(
        (off_axis - feat["onset_angle_deg"]) / 90.0, 1.0
    )
    ripple_amp_lin = (
        10 ** (feat["ripple_amplitude_db"] / 20.0) - 1.0
    )
    d = feat["ripple_density"]
    ripple = (
        math.sin(d * math.radians(az) * 1.7) *
        math.cos(d * math.radians(el) * 2.3) * 0.6 +
        math.sin(d * math.radians(az + el) * 0.9) * 0.4
    )
    gain_linear *= (1.0 + severity * ripple_amp_lin * ripple)
    return max(gain_linear, 1e-10)


# ═══════════════════════════════════════════════════════════════════
#  GROUND REFLECTION (2-RAY MODEL)
# ═══════════════════════════════════════════════════════════════════

def apply_ground_reflection(
    gain_linear: float, el_deg: float, freq_mhz: float, cfg: dict,
) -> float:
    """Apply 2-ray ground reflection interference.

    Args:
        gain_linear: Current gain in linear scale.
        el_deg:      Elevation angle (degrees).
        freq_mhz:    Frequency in MHz.
        cfg:         Full config dict.

    Returns:
        Modified gain (linear) with ground reflection.
    """
    feat = cfg["features"]["ground_reflection"]
    if not feat["enabled"]:
        return gain_linear
    wavelength = 300.0 / freq_mhz
    height_m = feat["height_wavelengths"] * wavelength
    rho = feat["reflection_coeff"]
    sin_el = math.sin(math.radians(el_deg))
    delta_phase = (
        2.0 * math.pi * 2.0 * height_m
        * sin_el / wavelength
    )
    interference = (
        1.0 + rho**2
        + 2.0 * rho * math.cos(delta_phase + math.pi)
    )
    return max(gain_linear * interference, 1e-10)


# ═══════════════════════════════════════════════════════════════════
#  CROSS-POLARIZATION
# ═══════════════════════════════════════════════════════════════════

def compute_cross_pol(
    az: float, el: float, copol_gain_linear: float, cfg: dict,
) -> float | None:
    """Compute cross-pol gain (linear) at one point.

    Args:
        az:                 Azimuth angle (degrees).
        el:                 Elevation angle (degrees).
        copol_gain_linear:  Co-pol gain in linear scale.
        cfg:                Full config dict.

    Returns:
        Cross-pol gain (linear), or ``None`` if cross-pol is disabled.
    """
    feat = cfg["features"]["cross_pol"]
    if not feat["enabled"]:
        return None
    boresight_iso = 10 ** (
        feat["boresight_isolation_db"] / 10.0
    )
    max_xpol = 10 ** (feat["max_cross_pol_db"] / 10.0)
    peak_angle = feat["peak_angle_deg"]
    off_axis = math.sqrt(az**2 + el**2)
    if peak_angle > 0:
        angular_factor = math.exp(
            -0.5 * ((off_axis - peak_angle)
                     / (peak_angle * 0.6))**2
        )
    else:
        angular_factor = 0.0
    diag_factor = abs(
        math.sin(2.0 * math.atan2(el, az + 1e-10))
    )
    xpol = (copol_gain_linear * boresight_iso
            + copol_gain_linear * max_xpol
            * angular_factor * diag_factor)
    return max(xpol, 1e-10)


# ═══════════════════════════════════════════════════════════════════
#  VSWR ROLLOFF
# ═══════════════════════════════════════════════════════════════════

def apply_vswr_rolloff(
    freq: float, f_min: float, f_max: float, cfg: dict,
) -> float:
    """Compute gain reduction factor at band edges due to VSWR.

    Args:
        freq:  Current frequency (MHz).
        f_min: Band lower edge (MHz).
        f_max: Band upper edge (MHz).
        cfg:   Full config dict.

    Returns:
        Multiplicative factor (0–1) to apply to linear gain.
    """
    feat = cfg["features"]["vswr_rolloff"]
    if not feat["enabled"]:
        return 1.0
    band = f_max - f_min
    if band <= 0:
        return 1.0
    edge_width = band * feat["rolloff_band_fraction"]
    if edge_width <= 0:
        return 1.0
    factor = 1.0
    for dist in [freq - f_min, f_max - freq]:
        if dist < edge_width:
            t = dist / edge_width
            if feat["rolloff_shape"] == "cosine":
                f_val = 0.5 * (
                    1.0 - math.cos(math.pi * t)
                )
            else:
                f_val = t
            loss_db = feat["max_rolloff_db"] * (1.0 - f_val)
            factor *= 10 ** (-loss_db / 10.0)
    return factor


# ═══════════════════════════════════════════════════════════════════
#  GAIN-BEAMWIDTH COUPLING
# ═══════════════════════════════════════════════════════════════════

def compute_freq_dependent_gain(
    freq: float, f_max: float, cfg: dict,
) -> float:
    """Logarithmic gain rolloff from f_max.

    Args:
        freq:  Current frequency (MHz).
        f_max: Upper band edge (MHz).
        cfg:   Full config dict.

    Returns:
        Multiplicative factor in (0, 1] to apply to max_gain_lin.
    """
    feat = cfg["features"]["gain_bw_coupling"]
    if not feat["enabled"] or freq >= f_max or f_max <= 0:
        return 1.0
    rolloff = feat["gain_rolloff_db_per_octave"]
    if rolloff <= 0:
        return 1.0
    octaves_below = math.log2(f_max / freq)
    loss_db = rolloff * octaves_below
    return 10 ** (-loss_db / 10.0)


def derive_bw_from_gain(
    gain_lin: float,
    base_az_bw: float,
    base_el_bw: float,
    base_gain_lin: float,
) -> tuple[float, float]:
    """Derive az/el beamwidths from gain, preserving aspect ratio.

    Uses the directivity relationship G proportional to 1/(az_bw * el_bw).
    When gain drops, both beamwidths widen by the same factor.

    Args:
        gain_lin:      Current peak gain (linear).
        base_az_bw:    Reference azimuth beamwidth (deg).
        base_el_bw:    Reference elevation beamwidth (deg).
        base_gain_lin: Reference peak gain (linear) at base BWs.

    Returns:
        ``(az_bw, el_bw)`` in degrees.
    """
    if gain_lin <= 0 or base_gain_lin <= 0:
        return base_az_bw, base_el_bw
    ratio = base_gain_lin / gain_lin
    scale = math.sqrt(ratio)
    return base_az_bw * scale, base_el_bw * scale


def derive_gain_from_bw(
    az_bw: float,
    el_bw: float,
    base_az_bw: float,
    base_el_bw: float,
    max_gain_lin: float,
) -> float:
    """Derive gain from beamwidths using directivity relationship.

    Args:
        az_bw:         Current azimuth beamwidth (deg).
        el_bw:         Current elevation beamwidth (deg).
        base_az_bw:    Reference azimuth beamwidth (deg).
        base_el_bw:    Reference elevation beamwidth (deg).
        max_gain_lin:  Peak gain (linear) at reference beamwidths.

    Returns:
        Scaled peak gain (linear).
    """
    bw_product_ref = base_az_bw * base_el_bw
    bw_product_now = az_bw * el_bw
    if bw_product_now <= 0:
        return max_gain_lin
    return max_gain_lin * (bw_product_ref / bw_product_now)


# ═══════════════════════════════════════════════════════════════════
#  ASYMMETRY (SQUINT + TILT)
# ═══════════════════════════════════════════════════════════════════

def apply_asymmetry(
    az: float, el: float, cfg: dict, seed_offset: int = 0,
) -> tuple[float, float, float]:
    """Apply pointing offset and deterministic perturbation.

    Args:
        az:          Azimuth angle (degrees).
        el:          Elevation angle (degrees).
        cfg:         Full config dict.
        seed_offset: Deterministic seed for perturbation.

    Returns:
        ``(az_eff, el_eff, perturbation_factor)``
    """
    feat = cfg["features"]["asymmetry"]
    if not feat["enabled"]:
        return az, el, 1.0
    az_eff = az - feat["az_squint_deg"]
    el_eff = el - feat["el_tilt_deg"]
    perturbation = 1.0
    if feat["random_asymmetry_db"] > 0:
        seed_val = (
            math.sin(az * 0.0731 + seed_offset)
            * math.cos(el * 0.0537 + seed_offset)
        )
        amp_lin = (
            10 ** (feat["random_asymmetry_db"] / 20.0)
            - 1.0
        )
        perturbation = 1.0 + amp_lin * seed_val
    return az_eff, el_eff, max(perturbation, 0.1)