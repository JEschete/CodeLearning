"""
Pattern computation engine.

compute_pattern() dispatches per-point gain to the registered
antenna type.  run_generation() drives the frequency loop and
writes CSVs.

Uses NumPy for vectorized computation when available (~50-100×
faster). Falls back to pure-Python loop otherwise.
"""

import logging
import math
import os
import random
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from antennas import get_antenna
from core.pattern_math import (
    bw_to_exponent,
    compute_freq_dependent_bw,
    apply_pattern_breakup,
    apply_ground_reflection,
    compute_cross_pol,
    apply_vswr_rolloff,
    apply_asymmetry,
    compute_freq_dependent_gain,
    derive_bw_from_gain,
    derive_gain_from_bw,
)
from core.io import write_pattern_csv


# ===================================================================
#  VECTORIZED PATTERN COMPUTATION (NumPy)
# ===================================================================

def _compute_pattern_numpy(
    az_angles: list[float],
    el_angles: list[float],
    freq: float,
    cfg: dict,
    antenna: "AntennaBase",
    az_bw: float,
    el_bw: float,
    n_az: float,
    n_el: float,
    gain_peak: float,
    pol_loss: float,
    asym_seed: float,
    do_xpol: bool,
) -> tuple[list[list[float]], list[list[float]] | None]:
    """Vectorized pattern computation using NumPy.

    Computes the full co-pol (and optionally cross-pol) gain grid
    using NumPy array operations for ~50-100x speedup over the
    scalar fallback.

    Args:
        az_angles: Azimuth angles in degrees.
        el_angles: Elevation angles in degrees.
        freq: Operating frequency in MHz.
        cfg: Generation configuration dict.
        antenna: Registered antenna instance.
        az_bw: 3 dB azimuth beamwidth in degrees.
        el_bw: 3 dB elevation beamwidth in degrees.
        n_az: Azimuth cos^n exponent.
        n_el: Elevation cos^n exponent.
        gain_peak: Peak gain in linear (accounting for VSWR).
        pol_loss: Polarization mismatch factor (0-1).
        asym_seed: Seed for deterministic asymmetry noise.
        do_xpol: Whether to compute cross-polarization.

    Returns:
        Tuple of (copol_2d, xpol_2d_or_None) where each is a
        nested list of dB values [el][az].
    """
    az_arr = np.array(az_angles, dtype=np.float64)
    el_arr = np.array(el_angles, dtype=np.float64)
    # meshgrid: az_grid[i,j] = az_angles[j],
    #           el_grid[i,j] = el_angles[i]
    az_grid, el_grid = np.meshgrid(az_arr, el_arr)

    # ── Asymmetry ────────────────────────────────────────
    feat_asym = cfg["features"]["asymmetry"]
    if feat_asym["enabled"]:
        az_eff = az_grid - feat_asym["az_squint_deg"]
        el_eff = el_grid - feat_asym["el_tilt_deg"]
        if feat_asym["random_asymmetry_db"] > 0:
            seed_val = (
                np.sin(az_grid * 0.0731 + asym_seed)
                * np.cos(el_grid * 0.0537 + asym_seed)
            )
            amp_lin = (
                10 ** (feat_asym["random_asymmetry_db"]
                       / 20.0) - 1.0
            )
            asym_p = np.maximum(
                1.0 + amp_lin * seed_val, 0.1
            )
        else:
            asym_p = np.ones_like(az_grid)
    else:
        az_eff = az_grid.copy()
        el_eff = el_grid.copy()
        asym_p = np.ones_like(az_grid)

    az_rad = np.radians(az_eff)
    el_rad = np.radians(el_eff)
    cos_az = np.cos(az_rad)
    cos_el = np.cos(el_rad)

    # ── Antenna-specific main beam (vectorized) ──────────
    # Dispatch to antenna's vectorized method if available,
    # otherwise use generic vectorized models.
    g = _vectorized_antenna_gain(
        antenna, az_eff, el_eff, cos_az, cos_el,
        n_az, n_el, az_bw, el_bw, gain_peak, cfg, freq
    )

    # ── Sidelobes (vectorized radial model) ──────────────
    # Skip overlay for types with intrinsic sidelobe models:
    # - Dish (Airy/Jinc² pattern has physical sidelobes)
    # - Array with Taylor weighting (taper controls sidelobes)
    feat_sl = cfg["features"]["sidelobes"]
    _skip_sl = (
        antenna.name == "Dish"
        or (antenna.name == "Array"
            and cfg.get("array_weighting") == "taylor")
    )
    if feat_sl["enabled"] and az_bw > 0 and el_bw > 0 and not _skip_sl:
        sl = _vectorized_sidelobes(
            az_eff, el_eff, az_bw, el_bw, cfg
        )
        g = np.maximum(g, sl * gain_peak)

    # ── Pattern breakup ──────────────────────────────────
    feat_bp = cfg["features"]["pattern_breakup"]
    if feat_bp["enabled"]:
        off_axis = np.sqrt(az_eff**2 + el_eff**2)
        mask = off_axis >= feat_bp["onset_angle_deg"]
        if np.any(mask):
            severity = np.minimum(
                (off_axis - feat_bp["onset_angle_deg"])
                / 90.0, 1.0
            )
            ripple_amp_lin = (
                10 ** (feat_bp["ripple_amplitude_db"]
                       / 20.0) - 1.0
            )
            d = feat_bp["ripple_density"]
            ripple = (
                np.sin(d * np.radians(az_eff) * 1.7)
                * np.cos(d * np.radians(el_eff) * 2.3)
                * 0.6
                + np.sin(
                    d * np.radians(az_eff + el_eff) * 0.9
                ) * 0.4
            )
            g = np.where(
                mask,
                g * (1.0 + severity
                     * ripple_amp_lin * ripple),
                g
            )
            g = np.maximum(g, 1e-10)

    # ── Ground reflection ────────────────────────────────
    feat_gr = cfg["features"]["ground_reflection"]
    if feat_gr["enabled"]:
        wavelength = 300.0 / freq
        height_m = (
            feat_gr["height_wavelengths"] * wavelength
        )
        rho = feat_gr["reflection_coeff"]
        sin_el = np.sin(np.radians(el_eff))
        delta_phase = (
            2.0 * math.pi * 2.0 * height_m
            * sin_el / wavelength
        )
        interference = (
            1.0 + rho**2
            + 2.0 * rho
            * np.cos(delta_phase + math.pi)
        )
        g = np.maximum(g * interference, 1e-10)

    # ── Polarization + asymmetry ─────────────────────────
    g *= asym_p * pol_loss
    g = np.maximum(g, gain_peak * 1e-7)

    # ── Convert to dB ────────────────────────────────────
    # Keep a copy of pre-noise linear gain for cross-pol
    g_pre_noise = g.copy() if do_xpol else None

    g_db = 10.0 * np.log10(g)

    noise_val = cfg["noise_range_db"]
    noise_type = cfg.get("noise_type", "uniform")

    if noise_val > 0:
        if noise_type == "uniform":
            noise = np.random.uniform(-noise_val, noise_val, g_db.shape)
            g_db += noise
        elif noise_type == "gaussian":
            noise = np.random.normal(0, noise_val, g_db.shape)
            g_db += noise
        elif noise_type == "quantization":
            g_db = np.round(g_db / noise_val) * noise_val

    copol = np.round(g_db, 2).tolist()

    # ── Cross-pol (per-point fallback) ───────────────────
    xpol = None
    if do_xpol:
        xpol = []
        for i, elv in enumerate(el_angles):
            xpol_row = []
            for j, azv in enumerate(az_angles):
                ae = float(az_eff[i, j])
                ee = float(el_eff[i, j])
                co_lin = float(g_pre_noise[i, j])
                xg = compute_cross_pol(
                    ae, ee, co_lin / pol_loss, cfg
                )
                if xg is not None:
                    xg *= pol_loss
                    xg = max(xg, gain_peak * 1e-8)
                    xg_db = 10.0 * math.log10(xg)
                    if noise_val > 0:
                        if noise_type == "uniform":
                            xg_db += random.uniform(-noise_val, noise_val)
                        elif noise_type == "gaussian":
                            xg_db += random.gauss(0, noise_val)
                        elif noise_type == "quantization":
                            xg_db = round(xg_db / noise_val) * noise_val

                    xpol_row.append(round(xg_db, 2))
            xpol.append(xpol_row)

    return copol, xpol


def _vectorized_array_gain(
    az_eff: "np.ndarray",
    el_eff: "np.ndarray",
    cos_az: "np.ndarray",
    cos_el: "np.ndarray",
    n_el: float,
    az_bw: float,
    el_bw: float,
    gain_peak: float,
    sig_k: float,
    cfg: dict,
) -> "np.ndarray":
    """Vectorized gain computation for the Array antenna type.

    Computes element pattern and array factor entirely via NumPy
    broadcasting — no per-point Python loops.  Weights, coupling,
    and element errors are computed once (they depend on array
    geometry, not observation angle).

    Supports linear, planar, and circular array geometries.
    """
    from antennas.array.array_antenna import (
        _taylor_weights, _uniform_weights,
        _apply_coupling, _apply_element_errors,
    )

    geo = cfg.get("array_geometry", "linear")
    nx = cfg.get("array_n_elements_x", 8)
    ny = cfg.get("array_n_elements_y", 1)
    dx = cfg.get("array_spacing_x_lambda", 0.5)
    dy = cfg.get("array_spacing_y_lambda", 0.5)
    steer_az = math.radians(cfg.get("array_steer_az_deg", 0.0))
    steer_el = math.radians(cfg.get("array_steer_el_deg", 0.0))
    ftb_lin = 10 ** (-abs(cfg.get("ftb_ratio_db", 20.0)) / 10.0)
    coupling_on = cfg.get("array_mutual_coupling", False)
    weighting = cfg.get("array_weighting", "uniform")
    sll = cfg.get("array_taper_sll_db", -25.0)
    rms_amp = cfg.get("array_rms_amplitude_error_db", 0.0)
    rms_phase = cfg.get("array_rms_phase_error_deg", 0.0)

    az_rad = np.radians(az_eff)
    el_rad = np.radians(el_eff)

    k = 2.0 * math.pi

    # ── Element pattern (vectorized) ───────────────────────
    elem_type = cfg.get("array_element_pattern", "gaussian")
    az_hw = az_bw / 2.0
    el_hw = el_bw / 2.0
    if az_hw > 0 and el_hw > 0:
        if elem_type == "cosine":
            u_az = np.clip(np.abs(az_eff) / az_hw, 0.0, 1.0)
            u_el = np.clip(np.abs(el_eff) / el_hw, 0.0, 1.0)
            g_element = (np.cos(math.pi / 2.0 * u_az)
                         * np.cos(math.pi / 2.0 * u_el))
            g_element = np.maximum(g_element, 0.0) ** 2
        elif elem_type == "patch":
            cos_az_e = np.cos(np.radians(
                np.clip(np.abs(az_eff), 0.0, 90.0)))
            cos_el_e = np.cos(np.radians(
                np.clip(np.abs(el_eff), 0.0, 90.0)))
            g_element = cos_az_e ** 1.5 * cos_el_e ** 1.5
        else:
            # Gaussian (default)
            r_sq = (az_eff / az_hw) ** 2 + (el_eff / el_hw) ** 2
            g_element = np.power(0.5, r_sq)
    else:
        g_element = np.ones_like(az_eff)

    # ── Helper: vectorized linear AF ───────────────────────
    def _vec_linear_af(angle_rad, n_elem, d_lam, beta, weights, phases):
        """Compute |AF|² over the full grid using broadcasting.

        angle_rad: 2-D array of observation angles (radians).
        weights/phases: 1-D arrays of length n_elem.
        Returns: 2-D array of normalised |AF|².
        """
        # psi: shape (n_el_grid, n_az_grid)
        psi = k * d_lam * np.sin(angle_rad) + beta

        # Element indices: shape (n_elem,)
        ns = np.arange(n_elem, dtype=np.float64)
        w = np.array(weights, dtype=np.float64)

        # phase_per_elem: shape (n_el_grid, n_az_grid, n_elem)
        # via broadcasting: psi[..., None] * ns[None, None, :]
        elem_phase = psi[..., np.newaxis] * ns
        if phases is not None:
            p = np.array(phases, dtype=np.float64)
            elem_phase = elem_phase + p

        # Weighted sum using broadcasting
        af_real = np.sum(w * np.cos(elem_phase), axis=-1)
        af_imag = np.sum(w * np.sin(elem_phase), axis=-1)

        af_sq = af_real ** 2 + af_imag ** 2
        w_sum_sq = np.sum(w) ** 2
        if w_sum_sq > 0:
            af_sq /= w_sum_sq
        return af_sq

    # ── Compute array factor per geometry ──────────────────
    if geo == "circular":
        R = dx  # radius in wavelengths
        orientation = cfg.get(
            "array_circular_orientation", "parallel")

        if weighting == "taylor":
            weights = _taylor_weights(nx, sll)
        else:
            weights = _uniform_weights(nx)

        phase_offsets = None
        if coupling_on:
            arc_spacing = 2.0 * math.pi * R / nx
            weights, phase_offsets = _apply_coupling(
                weights, arc_spacing)
        if rms_amp > 0 or rms_phase > 0:
            weights, phase_offsets = _apply_element_errors(
                weights, phase_offsets, rms_amp, rms_phase,
                seed=303)

        w_arr = np.array(weights, dtype=np.float64)
        # Element angular positions around circle
        phi_n = 2.0 * math.pi * np.arange(nx) / nx

        # Phase contribution per element:
        # k * R * (cos(az - phi_n) * cos(el) - cos(steer_az - phi_n))
        # Shape: (n_el_grid, n_az_grid, n_elem)
        cos_az_phi = np.cos(az_rad[..., np.newaxis]
                            - phi_n)  # broadcast
        cos_steer_phi = np.cos(steer_az - phi_n)
        elem_phase = k * R * (
            cos_az_phi * np.cos(el_rad)[..., np.newaxis]
            - cos_steer_phi)

        if phase_offsets is not None:
            p = np.array(phase_offsets, dtype=np.float64)
            elem_phase = elem_phase + p

        # Element orientation factor
        if orientation == "radial":
            elem_factor = np.maximum(cos_az_phi, 0.0)
            w_eff = w_arr * elem_factor
        else:
            w_eff = w_arr  # broadcast scalar * (n_elem,)

        af_real = np.sum(w_eff * np.cos(elem_phase), axis=-1)
        af_imag = np.sum(w_eff * np.sin(elem_phase), axis=-1)
        af_sq = af_real ** 2 + af_imag ** 2
        w_sum_sq = np.sum(w_arr) ** 2
        if w_sum_sq > 0:
            af_sq /= w_sum_sq

    elif geo == "planar":
        beta_x = -k * dx * math.sin(steer_az)
        beta_y = -k * dy * math.sin(steer_el)

        if weighting == "taylor":
            wx = _taylor_weights(nx, sll)
            wy = _taylor_weights(ny, sll)
        else:
            wx = _uniform_weights(nx)
            wy = _uniform_weights(ny)

        px, py = None, None
        if coupling_on:
            wx, px = _apply_coupling(wx, dx)
            wy, py = _apply_coupling(wy, dy)
        if rms_amp > 0 or rms_phase > 0:
            wx, px = _apply_element_errors(
                wx, px, rms_amp, rms_phase, seed=101)
            wy, py = _apply_element_errors(
                wy, py, rms_amp, rms_phase, seed=202)

        af_x = _vec_linear_af(az_rad, nx, dx, beta_x, wx, px)
        af_y = _vec_linear_af(el_rad, ny, dy, beta_y, wy, py)
        af_sq = af_x * af_y

    else:
        # Linear array along X (azimuth)
        beta_x = -k * dx * math.sin(steer_az)

        if weighting == "taylor":
            wx = _taylor_weights(nx, sll)
        else:
            wx = _uniform_weights(nx)

        px = None
        if coupling_on:
            wx, px = _apply_coupling(wx, dx)
        if rms_amp > 0 or rms_phase > 0:
            wx, px = _apply_element_errors(
                wx, px, rms_amp, rms_phase, seed=101)

        af_sq = _vec_linear_af(az_rad, nx, dx, beta_x, wx, px)

    # ── Pattern Multiplication Theorem ─────────────────────
    g_front = gain_peak * g_element * af_sq

    # ── Back lobe (matches scalar compute_point_gain) ─────
    back_weight = (1.0 - cos_az) / 2.0
    g_back = gain_peak * ftb_lin * back_weight

    return np.maximum(g_front, g_back)


def _vectorized_antenna_gain(
    antenna: "AntennaBase",
    az_eff: "np.ndarray",
    el_eff: "np.ndarray",
    cos_az: "np.ndarray",
    cos_el: "np.ndarray",
    n_az: float,
    n_el: float,
    az_bw: float,
    el_bw: float,
    gain_peak: float,
    cfg: dict,
    freq: float = 0.0,
) -> "np.ndarray":
    """Vectorized main-beam gain for known antenna types.

    Dispatches to optimised NumPy implementations for each
    built-in antenna model. Falls back to per-element scalar
    calls for unknown/custom types.

    Args:
        antenna: Registered antenna instance.
        az_eff: 2-D array of effective azimuth angles (deg).
        el_eff: 2-D array of effective elevation angles (deg).
        cos_az: cos(az_eff) pre-computed.
        cos_el: cos(el_eff) pre-computed.
        n_az: Azimuth cos^n exponent.
        n_el: Elevation cos^n exponent.
        az_bw: 3 dB azimuth beamwidth (deg).
        el_bw: 3 dB elevation beamwidth (deg).
        gain_peak: Peak linear gain.
        cfg: Configuration dict.
        freq: Operating frequency in MHz (used by Monopole).

    Returns:
        2-D NumPy array of linear gain values.
    """
    name = antenna.name
    sig_k = float(cfg.get("sigmoid_k", 40.0))

    if name == "LPDA":
        ftb_lin = 10 ** (
            -abs(cfg["ftb_ratio_db"]) / 10.0
        )
        az_hw = az_bw / 2.0
        el_hw = el_bw / 2.0

        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        front_fade = 1.0 / (1.0 + np.exp(-sig_k * cos_az))
        if az_hw > 0 and el_hw > 0:
            r_sq = (az_eff / az_hw) ** 2 + (el_eff / el_hw) ** 2
            g_main = gain_peak * np.power(0.5, r_sq) * front_fade
        else:
            g_main = np.zeros_like(cos_az)

        # Back lobe
        back_weight = (1.0 - cos_az) / 2.0
        el_n_back = max(n_el * 0.5, 1.0)
        back_el = np.maximum(
            np.abs(cos_el), 1e-12
        ) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el

        return np.maximum(g_main, g_back)

    elif name == "Omni":
        gain_el = np.maximum(
            np.abs(cos_el), 0.0
        ) ** n_el
        return gain_el * gain_peak

    elif name == "Panel":
        ftb_lin = 10 ** (
            -abs(cfg.get("ftb_ratio_db", 20.0)) / 10.0
        )
        downtilt = cfg.get("mechanical_tilt_deg",
                          cfg.get("panel_downtilt_deg", 0.0))
        el_eff_dt = el_eff - downtilt
        K = 1.3916
        az_hw_rad = np.radians(az_bw / 2.0)
        el_hw_rad = np.radians(el_bw / 2.0)
        sin_az_hw = np.sin(az_hw_rad)
        sin_el_hw = np.sin(el_hw_rad)
        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        front_fade = 1.0 / (1.0 + np.exp(-sig_k * cos_az))
        if sin_az_hw > 1e-12 and sin_el_hw > 1e-12:
            u_az = K * np.sin(np.radians(az_eff)) / sin_az_hw
            u_el = K * np.sin(np.radians(el_eff_dt)) / sin_el_hw
            g_az = np.sinc(u_az / np.pi) ** 2
            g_el = np.sinc(u_el / np.pi) ** 2
            g_front = gain_peak * g_az * g_el * front_fade
        else:
            g_front = np.zeros_like(cos_az)
        back_weight = (1.0 - cos_az) / 2.0
        el_n_back = max(n_el * 0.5, 1.0)
        back_el = np.maximum(
            np.abs(np.cos(np.radians(el_eff_dt))),
            1e-12) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el
        return np.maximum(g_front, g_back)

    elif name == "Horn":
        ftb_lin = 10 ** (
            -abs(cfg.get("ftb_ratio_db", 25.0)) / 10.0
        )
        K_E = 1.3916
        K_H = 1.1891
        az_hw_rad = np.radians(az_bw / 2.0)
        el_hw_rad = np.radians(el_bw / 2.0)
        sin_az_hw = np.sin(az_hw_rad)
        sin_el_hw = np.sin(el_hw_rad)
        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        front_fade = 1.0 / (1.0 + np.exp(-sig_k * cos_az))
        if sin_az_hw > 1e-12 and sin_el_hw > 1e-12:
            # E-plane (sinc²)
            u_el = K_E * np.sin(np.radians(el_eff)) / sin_el_hw
            g_el = np.sinc(u_el / np.pi) ** 2
            # H-plane (cos-taper)
            v_az = K_H * np.sin(np.radians(az_eff)) / sin_az_hw
            denom = 1.0 - (2.0 * v_az / np.pi) ** 2
            safe_denom = np.where(np.abs(denom) < 1e-10,
                                  1.0, denom)
            g_az_val = np.cos(v_az) / safe_denom
            g_az_lim = np.pi / 4.0 * np.cos(v_az)
            g_az = np.where(np.abs(denom) < 1e-10,
                            g_az_lim, g_az_val) ** 2
            g_front = gain_peak * g_az * g_el * front_fade
        else:
            g_front = np.zeros_like(cos_az)
        back_weight = (1.0 - cos_az) / 2.0
        el_n_back = max(n_el * 0.3, 1.0)
        back_el = np.maximum(
            np.abs(cos_el), 1e-12) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el
        return np.maximum(g_front, g_back)

    elif name == "Dish":
        eff = cfg.get("dish_efficiency", 0.60)
        ftb_lin = 10 ** (
            -abs(cfg.get("ftb_ratio_db", 30.0)) / 10.0
        )
        # Feed edge taper: Gaussian envelope suppressing sidelobes
        edge_taper = cfg.get("feed_edge_taper_db", -12.0)
        taper_lin = (10 ** (edge_taper / 20.0)
                     if edge_taper < 0 else 1.0)
        if 0 < taper_lin < 1.0:
            import math as _math
            taper_sigma_sq = -0.5 / _math.log(taper_lin)
        else:
            taper_sigma_sq = 0.0

        K = 1.6163
        az_hw_rad = np.radians(az_bw / 2.0)
        el_hw_rad = np.radians(el_bw / 2.0)
        sin_az_hw = np.sin(az_hw_rad)
        sin_el_hw = np.sin(el_hw_rad)
        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        front_fade = 1.0 / (1.0 + np.exp(-sig_k * cos_az))
        if sin_az_hw > 1e-12 and sin_el_hw > 1e-12:
            sin_az = np.sin(np.radians(az_eff))
            sin_el = np.sin(np.radians(el_eff))
            r_sq = ((sin_az / sin_az_hw) ** 2
                    + (sin_el / sin_el_hw) ** 2)
            r = np.sqrt(r_sq)
            u = K * r
            # Jinc² using J₁ — safe division via masking
            try:
                from scipy.special import j1
                safe_u = np.where(np.abs(u) < 1e-10, 1.0, u)
                raw = 2.0 * j1(safe_u) / safe_u
                jinc_val = np.where(np.abs(u) < 1e-10, 1.0, raw ** 2)
            except ImportError:
                jinc_val = np.where(
                    np.abs(u) < 1e-10, 1.0,
                    np.power(0.5, (u / K) ** 2))
            # Apply feed taper envelope
            if taper_sigma_sq > 0:
                taper_env = np.exp(-r_sq / (2.0 * taper_sigma_sq))
            else:
                taper_env = 1.0
            g_front = (gain_peak * eff * jinc_val
                       * taper_env * front_fade)
        else:
            g_front = np.zeros_like(cos_az)
        back_weight = (1.0 - cos_az) / 2.0
        el_n_back = max(n_el * 0.3, 1.0)
        back_el = np.maximum(
            np.abs(cos_el), 1e-12) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el
        return np.maximum(g_front, g_back)

    elif name == "Monopole":
        from antennas.monopole.monopole import MonopoleAntenna
        L = MonopoleAntenna.electrical_length(cfg, freq)
        kL = 2.0 * np.pi * L
        el_rad_v = np.radians(el_eff)
        cos_el_v = np.cos(el_rad_v)
        sin_el_v = np.sin(el_rad_v)
        safe_cos = np.where(np.abs(cos_el_v) < 1e-10,
                            1e-10, cos_el_v)
        numerator = (np.cos(kL / 2.0 * sin_el_v)
                     - np.cos(kL / 2.0))
        denom_norm = 1.0 - np.cos(kL / 2.0)
        if abs(denom_norm) < 1e-12:
            g_el = np.maximum(
                np.abs(cos_el), 1e-12) ** n_el
            return gain_peak * g_el
        f_el = numerator / (denom_norm * safe_cos)
        return np.maximum(
            gain_peak * f_el * f_el,
            gain_peak * 1e-7)

    elif name == "Array":
        return _vectorized_array_gain(
            az_eff, el_eff, cos_az, cos_el,
            n_el, az_bw, el_bw, gain_peak, sig_k, cfg)

    else:
        # Fallback: per-point for unknown antenna types
        shape = az_eff.shape
        g = np.empty(shape)
        for i in range(shape[0]):
            for j in range(shape[1]):
                g[i, j] = antenna.compute_point_gain(
                    float(az_eff[i, j]),
                    float(el_eff[i, j]),
                    float(cos_az[i, j]),
                    float(cos_el[i, j]),
                    n_az, n_el, az_bw, el_bw,
                    gain_peak, cfg
                )
        return g


def _vectorized_sidelobes(
    az_eff: "np.ndarray",
    el_eff: "np.ndarray",
    az_bw: float,
    el_bw: float,
    cfg: dict,
) -> "np.ndarray":
    """Vectorized radial sidelobe envelope.

    Computes a 2-D sidelobe amplitude grid using the Taylor
    taper model with configurable first-lobe level, decay rate,
    and number of lobes.

    Args:
        az_eff: 2-D array of effective azimuth angles (deg).
        el_eff: 2-D array of effective elevation angles (deg).
        az_bw: 3 dB azimuth beamwidth (deg).
        el_bw: 3 dB elevation beamwidth (deg).
        cfg: Configuration dict with ``features.sidelobes``.

    Returns:
        2-D NumPy array of sidelobe amplitude (linear, relative to peak).
    """
    feat = cfg["features"]["sidelobes"]
    first_sl_lin = 10 ** (feat["first_sidelobe_db"] / 10.0)
    sl_type = feat.get("type", "taylor")
    if sl_type == "uniform":
        decay_lin = 1.0
    else:
        decay_lin = 10 ** (-feat["decay_rate_db"] / 10.0)
    n_sl = feat["n_sidelobes"]

    off_axis = np.sqrt(az_eff**2 + el_eff**2)
    angle_in_plane = np.arctan2(
        np.abs(el_eff), np.abs(az_eff) + 1e-10
    )
    cos_a = np.cos(angle_in_plane)
    sin_a = np.sin(angle_in_plane)
    bw_eff = 1.0 / np.sqrt(
        (cos_a / az_bw) ** 2 + (sin_a / el_bw) ** 2
    )

    u = off_axis / np.maximum(bw_eff, 1e-10)
    sl_index = ((u - 0.7) / 0.8).astype(int)
    sl_index_f = np.maximum(sl_index, 0).astype(float)

    # In-lobe region
    sl_amp = first_sl_lin * np.power(decay_lin, sl_index_f)
    phase = np.pi * ((u - 0.7) / 0.8 - sl_index_f)
    in_lobe = sl_amp * np.cos(phase) ** 2

    # Beyond last lobe: smooth taper
    last_amp = first_sl_lin * (decay_lin ** (n_sl - 1))
    u_end = 0.7 + n_sl * 0.8
    extra = (u - u_end) / 0.8
    beyond = last_amp * decay_lin * np.exp(
        -2.0 * np.maximum(extra, 0.0)
    )

    result = np.where(
        u < 0.7, 0.0,
        np.where(sl_index < n_sl, in_lobe, beyond)
    )
    # Zero out near-boresight
    result = np.where(off_axis < 1e-6, 0.0, result)
    return result


# ===================================================================
#  MAIN PATTERN COMPUTATION
# ===================================================================

def compute_pattern(
    az_angles: list[float],
    el_angles: list[float],
    freq: float,
    cfg: dict,
) -> tuple[list[list[float]], list[list[float]] | None]:
    """Compute full az/el co-pol (and optionally cross-pol) pattern.

    Dispatches to the NumPy vectorized path when available,
    otherwise falls back to a pure-Python per-point loop.

    Args:
        az_angles: List of azimuth angles in degrees.
        el_angles: List of elevation angles in degrees.
        freq: Operating frequency in MHz.
        cfg: Full generation configuration dict.

    Returns:
        Tuple of ``(copol_2d, xpol_2d_or_None)`` where each
        element is a nested list ``[el_idx][az_idx]`` of gain
        values in dBi.
    """
    antenna = get_antenna(cfg["antenna_type"])

    # For Monopole with physical length, update electrical length
    # for this frequency slice so both vectorized and scalar paths
    # see the correct value.
    if antenna.name == "Monopole":
        from antennas.monopole.monopole import MonopoleAntenna
        cfg["element_length_wavelengths"] = (
            MonopoleAntenna.electrical_length(cfg, freq)
        )

    # For Horn with aperture size, derive beamwidths from aperture.
    # horn_aperture_wavelengths is the physical width expressed in
    # wavelengths at the reference frequency.  At frequency f the
    # aperture in wavelengths = aperture_ref * f / f_ref, so:
    #   BW_H(f) = 67° / (aperture * f/f_ref)   (H-plane, cosine)
    #   BW_E(f) = 51° / (aperture * f/f_ref)   (E-plane, sinc)
    # This replaces the BW-decay feature for Horn when aperture is set.
    if antenna.name == "Horn":
        aperture = cfg.get("horn_aperture_wavelengths")
        if aperture and aperture > 0 and freq > 0:
            f_ref = cfg.get("ref_frequency_mhz")
            if not f_ref:
                f_ref = (cfg["f_min_mhz"] + cfg["f_max_mhz"]) / 2.0
            a_at_freq = aperture * freq / f_ref
            if a_at_freq > 0:
                cfg["az_beamwidth_deg"] = min(
                    67.0 / a_at_freq, 180.0)
                cfg["el_beamwidth_deg"] = min(
                    51.0 / a_at_freq, 180.0)

    f_min = cfg["f_min_mhz"]
    f_max = cfg["f_max_mhz"]
    ref_freq = cfg.get("ref_frequency_mhz")
    if not ref_freq:
        # When gain-BW coupling is active, anchor both gain and
        # beamwidth at f_max so the configured values are consistent.
        coupling = cfg["features"].get("gain_bw_coupling", {})
        if coupling.get("enabled"):
            ref_freq = f_max
        else:
            ref_freq = (f_min + f_max) / 2.0
    max_gain_lin = 10 ** (cfg["max_gain_dbi"] / 10.0)

    # ── Beamwidth scaling ────────────────────────────────────
    if not antenna.has_az_pattern:
        az_bw = 360.0
    else:
        az_bw = compute_freq_dependent_bw(
            cfg["az_beamwidth_deg"], freq, ref_freq, cfg,
            plane="az"
        )
    el_bw = compute_freq_dependent_bw(
        cfg["el_beamwidth_deg"], freq, ref_freq, cfg,
        plane="el"
    )

    n_az = bw_to_exponent(az_bw) if az_bw < 360 else 0
    n_el = bw_to_exponent(el_bw)

    # ── Polarization ─────────────────────────────────────────
    if cfg["polarization"] == "vertical":
        pol_angle = 0.0
    elif cfg["polarization"] == "horizontal":
        pol_angle = 90.0
    else:
        pol_angle = cfg["pol_angle_deg"]
    pol_loss = max(
        math.cos(math.radians(pol_angle)) ** 2, 0.01
    )

    # ── VSWR ─────────────────────────────────────────────────
    vswr_factor = apply_vswr_rolloff(freq, f_min, f_max, cfg)
    gain_peak = max_gain_lin * vswr_factor

    # ── Gain-BW coupling ─────────────────────────────────────
    coupling = cfg["features"].get("gain_bw_coupling", {})
    if coupling.get("enabled"):
        mode = coupling.get("mode", "independent")
        if mode == "gain_drives_bw":
            freq_gain_factor = compute_freq_dependent_gain(
                freq, f_max, cfg)
            gain_peak = max_gain_lin * vswr_factor * freq_gain_factor
            az_bw, el_bw = derive_bw_from_gain(
                gain_peak,
                cfg["az_beamwidth_deg"],
                cfg["el_beamwidth_deg"],
                max_gain_lin,
            )
            n_az = bw_to_exponent(az_bw) if az_bw < 360 else 0
            n_el = bw_to_exponent(el_bw)
        elif mode == "bw_drives_gain":
            gain_peak = derive_gain_from_bw(
                az_bw, el_bw,
                cfg["az_beamwidth_deg"],
                cfg["el_beamwidth_deg"],
                max_gain_lin,
            ) * vswr_factor
        elif mode == "independent":
            freq_gain_factor = compute_freq_dependent_gain(
                freq, f_max, cfg)
            gain_peak = max_gain_lin * vswr_factor * freq_gain_factor

    asym_seed = freq * 17.3
    do_xpol = cfg["features"]["cross_pol"]["enabled"]

    # ── Vectorized path (NumPy) ──────────────────────────────
    if HAS_NUMPY:
        return _compute_pattern_numpy(
            az_angles, el_angles, freq, cfg,
            antenna, az_bw, el_bw, n_az, n_el,
            gain_peak, pol_loss, asym_seed, do_xpol
        )

    # ── Scalar fallback ──────────────────────────────────────
    copol = []
    xpol = []

    # ── Per-point loop ───────────────────────────────────────
    for el in el_angles:
        copol_row = []
        xpol_row = []
        for az in az_angles:
            az_eff, el_eff, asym_p = apply_asymmetry(
                az, el, cfg, asym_seed
            )
            az_rad = math.radians(az_eff)
            el_rad = math.radians(el_eff)
            cos_az = math.cos(az_rad)
            cos_el = math.cos(el_rad)

            # ── Antenna-specific gain ────────────────
            g = antenna.compute_point_gain(
                az_eff, el_eff, cos_az, cos_el,
                n_az, n_el, az_bw, el_bw,
                gain_peak, cfg
            )

            # ── Shared post-processing ───────────────
            g = apply_pattern_breakup(
                g, az_eff, el_eff, cfg
            )
            g = apply_ground_reflection(
                g, el_eff, freq, cfg
            )
            g *= asym_p
            g *= pol_loss
            g = max(g, gain_peak * 1e-7)
            g_db = 10.0 * math.log10(g)

            noise_val = cfg["noise_range_db"]
            noise_type = cfg.get("noise_type", "uniform")

            if noise_val > 0:
                if noise_type == "uniform":
                    g_db += random.uniform(-noise_val, noise_val)
                elif noise_type == "gaussian":
                    g_db += random.gauss(0, noise_val)
                elif noise_type == "quantization":
                    g_db = round(g_db / noise_val) * noise_val
            copol_row.append(round(g_db, 2))

            if do_xpol:
                xg = compute_cross_pol(
                    az_eff, el_eff, g / pol_loss, cfg
                )
                if xg is not None:
                    xg *= pol_loss
                    xg = max(xg, gain_peak * 1e-8)
                    xg_db = 10.0 * math.log10(xg)
                    if noise_val > 0:
                        if noise_type == "uniform":
                            xg_db += random.uniform(-noise_val, noise_val)
                        elif noise_type == "gaussian":
                            xg_db += random.gauss(0, noise_val)
                        elif noise_type == "quantization":
                            xg_db = round(xg_db / noise_val) * noise_val
                    xpol_row.append(round(xg_db, 2))

        copol.append(copol_row)
        if do_xpol:
            xpol.append(xpol_row)

    return copol, xpol if do_xpol else None


# ===================================================================
#  GENERATION LOOP
# ===================================================================

def run_generation(
    cfg: dict,
    freqs: list[float],
    writer: "IO[str] | None" = None,
) -> None:
    """Generate pattern CSVs for all frequencies.

    Drives the frequency loop: for each frequency slice, calls
    :func:`compute_pattern`, writes co-pol (and optionally
    cross-pol) CSV files into the output directory.

    Args:
        cfg: Full generation configuration dict.
        freqs: List of frequencies in MHz.
        writer: File-like object for progress output.
                Defaults to ``sys.stdout``.
    """
    import time

    out = writer or sys.stdout

    # Schema validation
    from config import validate_config
    schema_errors = validate_config(cfg)
    if schema_errors:
        logger.error("Config validation failed with %d error(s). "
                     "Fix them before generating.",
                     len(schema_errors))
        return

    # Validate config via antenna-specific checks
    antenna = get_antenna(cfg["antenna_type"])
    warnings = antenna.validate_config(cfg)
    if warnings:
        logger.warning("CONFIG WARNINGS:")
        for w in warnings:
            logger.warning("  %s", w)

    stamp = datetime.now().strftime("%Y%m%d%H%M")
    base_dir = cfg['output_dir']
    # Always use a timestamped sub-folder so every run is isolated
    output_dir = os.path.join(base_dir, stamp)
    os.makedirs(output_dir, exist_ok=True)

    az_step = cfg.get("az_step_deg", 1.0)
    el_step = cfg.get("el_step_deg", 1.0)
    az_angles = [round(-180 + i * az_step, 4)
                 for i in range(
                     int(360 / az_step) + 1)]
    el_angles = [round(-90 + i * el_step, 4)
                 for i in range(
                     int(180 / el_step) + 1)]
    do_xpol = cfg["features"]["cross_pol"]["enabled"]
    count = 0

    prefix = antenna.file_prefix
    t_start = time.time()

    try:
        for i, freq in enumerate(freqs):
            freq_label = (
                f"{freq:.2f}".replace(".", "p") + "MHz"
            )
            elapsed = time.time() - t_start
            if i > 0:
                per_slice = elapsed / i
                eta = per_slice * (len(freqs) - i)
                eta_str = f"  ETA {eta:.0f}s"
            else:
                eta_str = ""
            out.write(
                f"\r  [{i+1}/{len(freqs)}] "
                f"Computing {freq:.2f} MHz..."
                f"{eta_str}   "
            )
            if hasattr(out, 'flush'):
                out.flush()

            copol, xpol = compute_pattern(
                az_angles, el_angles, freq, cfg
            )
            
            ext = cfg.get("output_format", ".csv")
            if not ext.startswith("."):
                ext = "." + ext

            co_name = f"{prefix}_{freq_label}_copol{ext}"
            write_pattern_csv(
                os.path.join(output_dir, co_name),
                az_angles, el_angles, copol
            )
            count += 1

            if do_xpol and xpol is not None:
                xp_name = (
                    f"{prefix}_{freq_label}_xpol{ext}"
                )
                write_pattern_csv(
                    os.path.join(output_dir, xp_name),
                    az_angles, el_angles, xpol
                )
                count += 1

    except KeyboardInterrupt:
        elapsed = time.time() - t_start
        logger.info("Interrupted after %.1fs. "
                    "%d files written to: %s/",
                    elapsed, count, output_dir)
        return

    elapsed = time.time() - t_start

    # ── Save generation config alongside patterns ─────────
    import json
    config_path = os.path.join(output_dir, "generation_config.json")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, default=str)
        logger.info("Config saved: %s", config_path)
    except Exception:
        logger.warning("Could not save config to %s",
                       config_path, exc_info=True)

    logger.info("Done! %d CSV files written to: %s/ "
                "(%.1fs)", count, output_dir, elapsed)
    if do_xpol:
        logger.info("  (%d co-pol + %d cross-pol)",
                    len(freqs), len(freqs))

    return output_dir
