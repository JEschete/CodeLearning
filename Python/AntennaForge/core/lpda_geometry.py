"""
LPDA geometry computation using Carrel's design equations.

Given tau (scale factor) and sigma (spacing factor), computes the
physical element lengths and positions for a Log-Periodic Dipole Array.

This is a pure-math module with no UI dependencies.
"""

import math

# Speed of light (m/s) — using MHz for frequency, results in metres
_C_MHZ = 299.792458  # c / 1e6, so L(m) = _C_MHZ / (2 * f_MHz)


def compute_lpda_geometry(
    tau: float,
    sigma: float,
    f_low_mhz: float,
    f_high_mhz: float,
    z0: float = 50.0,
) -> dict:
    """Compute LPDA element geometry from Carrel's design equations.

    Args:
        tau: Scale factor (0.7 – 0.98). Ratio of successive element
             lengths: L_{n+1} = tau * L_n.
        sigma: Relative spacing factor (0.03 – 0.22). Relates element
               spacing to element length: s_n = 4 * sigma * L_{n+1}.
        f_low_mhz: Lower design frequency (MHz).
        f_high_mhz: Upper design frequency (MHz).
        z0: Feed impedance (Ohms), default 50.

    Returns:
        dict with keys:
            n_elements, tau, sigma, alpha_deg,
            lengths_m (full dipole lengths),
            positions_m (from tip of boom, i.e. shortest-element end),
            spacings_m, boom_length_m, directivity_dbi_est,
            f_low_mhz, f_high_mhz, z0_ohms,
            element_freqs_mhz (resonant frequency of each element)
    """
    tau = max(0.70, min(0.98, tau))
    sigma = max(0.03, min(0.22, sigma))

    if f_low_mhz <= 0 or f_high_mhz <= f_low_mhz:
        raise ValueError("Frequencies must satisfy 0 < f_low < f_high")

    # ── Half-angle of the LPDA structure ──────────────────────
    # alpha = atan((1 - tau) / (4 * sigma))
    alpha = math.atan((1.0 - tau) / (4.0 * sigma))
    alpha_deg = math.degrees(alpha)

    # ── Active-region bandwidth (Bar) ─────────────────────────
    # Bar = 1.1 + 7.7 * (1 - tau)^2 * cot(alpha)
    cot_alpha = 1.0 / math.tan(alpha) if alpha > 1e-10 else 1e10
    B_ar = 1.1 + 7.7 * (1.0 - tau) ** 2 * cot_alpha

    # ── Design bandwidth ──────────────────────────────────────
    B_s = (f_high_mhz / f_low_mhz) * B_ar

    # ── Number of elements ────────────────────────────────────
    N = 1 + math.ceil(math.log(B_s) / math.log(1.0 / tau))
    N = max(3, min(50, N))  # clamp to reasonable range

    # ── Element half-lengths (longest first) ──────────────────
    # L_1 is a half-wave dipole at the lowest frequency
    L1_half = _C_MHZ / (2.0 * f_low_mhz)  # half-length of longest element
    half_lengths = [L1_half * (tau ** (n)) for n in range(N)]
    # Full dipole lengths (tip-to-tip)
    full_lengths = [2.0 * hl for hl in half_lengths]

    # ── Element spacings (between adjacent elements) ──────────
    # s_n = 4 * sigma * half_length_{n+1}
    spacings = []
    for n in range(N - 1):
        s = 4.0 * sigma * half_lengths[n + 1]
        spacings.append(s)

    # ── Element positions along boom (from apex) ──────────────
    # Position of element 1 (longest) from the virtual apex:
    #   d_1 = L1_half / (2 * tan(alpha))
    # But we want positions from the boom tip (shortest element end).
    # First compute from apex, then invert.
    if alpha > 1e-10:
        d1_from_apex = L1_half / (2.0 * math.tan(alpha))
    else:
        d1_from_apex = 0.0

    positions_from_apex = [d1_from_apex * (tau ** n) for n in range(N)]

    # Boom length
    boom_length = positions_from_apex[0] - positions_from_apex[-1]

    # Positions from the front (shortest-element end) of the boom
    positions = [positions_from_apex[0] - p for p in positions_from_apex]

    # ── Resonant frequency of each element ────────────────────
    element_freqs = [_C_MHZ / (2.0 * hl) for hl in half_lengths]

    # ── Estimated directivity (Carrel empirical) ──────────────
    # Approximation from Carrel's design curves:
    #   D ≈ 10 * log10(N_active * 2 * sigma / (1 - tau))
    # where N_active ≈ number of elements in the active region.
    # A more practical approximation for typical LPDA:
    N_active = max(2, round(N * 0.6))
    if (1.0 - tau) > 0:
        D_lin = N_active * 2.0 * sigma / (1.0 - tau)
        D_lin = max(D_lin, 1.0)
        directivity_dbi = 10.0 * math.log10(D_lin)
    else:
        directivity_dbi = 7.0  # fallback

    # Clamp to realistic range for LPDA
    directivity_dbi = max(5.0, min(12.0, directivity_dbi))

    return {
        "n_elements": N,
        "tau": tau,
        "sigma": sigma,
        "alpha_deg": alpha_deg,
        "lengths_m": full_lengths,
        "positions_m": positions,
        "spacings_m": spacings,
        "boom_length_m": boom_length,
        "directivity_dbi_est": directivity_dbi,
        "f_low_mhz": f_low_mhz,
        "f_high_mhz": f_high_mhz,
        "z0_ohms": z0,
        "element_freqs_mhz": element_freqs,
    }


def estimate_beamwidths(geometry: dict, freq_mhz: float) -> tuple[float, float]:
    """Estimate az/el beamwidths at a given frequency from LPDA geometry.

    Uses the empirical relationship:
        BW_az ≈ 70 * lambda / boom_length  (clamped to [30, 120])
        BW_el ≈ BW_az * 1.1                (LPDA el is slightly wider)

    Args:
        geometry: Output from compute_lpda_geometry().
        freq_mhz: Operating frequency in MHz.

    Returns:
        (az_beamwidth_deg, el_beamwidth_deg)
    """
    wavelength = _C_MHZ / freq_mhz if freq_mhz > 0 else 1.0
    boom = geometry["boom_length_m"]
    if boom > 0:
        bw_az = 70.0 * wavelength / boom
    else:
        bw_az = 65.0  # fallback

    bw_az = max(30.0, min(120.0, bw_az))
    bw_el = max(30.0, min(120.0, bw_az * 1.1))
    return bw_az, bw_el


def estimate_ftb(tau: float) -> float:
    """Estimate front-to-back ratio from tau.

    Higher tau → higher FTB. Empirical approximation:
        FTB ≈ 8 + 40 * (tau - 0.8) dB   for 0.8 ≤ tau ≤ 0.98

    Returns:
        Estimated FTB in dB (clamped to [8, 25]).
    """
    ftb = 8.0 + 40.0 * (tau - 0.8)
    return max(8.0, min(25.0, ftb))


def geometry_summary_text(geometry: dict) -> str:
    """Format geometry as a readable text summary for the ResultBox."""
    g = geometry
    lines = [
        f"LPDA Design Summary",
        f"{'='*40}",
        f"  tau = {g['tau']:.4f}    sigma = {g['sigma']:.4f}",
        f"  Structure angle = {g['alpha_deg']:.1f} deg",
        f"  Frequency range: {g['f_low_mhz']:.1f} - {g['f_high_mhz']:.1f} MHz",
        f"  Feed impedance: {g['z0_ohms']:.0f} Ohm",
        f"  Number of elements: {g['n_elements']}",
        f"  Boom length: {g['boom_length_m']:.3f} m",
        f"  Est. directivity: {g['directivity_dbi_est']:.1f} dBi",
        f"  Est. front-to-back: {estimate_ftb(g['tau']):.1f} dB",
        f"",
        f"  {'#':>3}  {'Length (m)':>10}  {'Pos (m)':>9}  {'Freq (MHz)':>11}",
        f"  {'---':>3}  {'----------':>10}  {'---------':>9}  {'-----------':>11}",
    ]
    for i in range(g["n_elements"]):
        lines.append(
            f"  {i+1:3d}  {g['lengths_m'][i]:10.4f}  "
            f"{g['positions_m'][i]:9.4f}  "
            f"{g['element_freqs_mhz'][i]:11.2f}"
        )
    return "\n".join(lines)
