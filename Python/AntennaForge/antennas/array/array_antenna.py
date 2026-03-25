"""
Phased Array antenna type.

Implements the Pattern Multiplication Theorem:
  Total pattern = Element pattern × Array Factor

Supports linear, planar (rectangular), and circular array
geometries with configurable:
  - Number of elements (Nx, Ny for planar)
  - Element spacing in wavelengths (dx, dy)
  - Progressive phase shift for beam steering (βx, βy)
  - Element weighting (uniform, Taylor, Chebyshev)
  - Element type (any registered antenna for element pattern)

Array Factor for linear array along x-axis:
  AF(θ) = Σ wₙ · exp(j·n·(k·d·sin(θ_az)·cos(θ_el) + β))

Grating lobes appear when d/λ > 1/(1+|sin(θ_scan)|).
The tool warns when element spacing exceeds λ/2.

Planar array is the product of two linear array factors:
  AF_planar = AF_x(az) × AF_y(el)

Mutual coupling model (toggleable):
  Approximates inter-element coupling using an impedance matrix
  Z_mn = Z_self · c₀ · exp(-α · |m-n| · d/λ) for m ≠ n.
  Coupled weights: w_coupled = Z⁻¹ · (Z_self · w_ideal).
  This perturbs both amplitude and phase of element excitations.
"""

import math

from antennas.base import AntennaBase


def _taylor_weights(n_elements: int, sll_db: float = -25) -> list[float]:
    """Compute Taylor window weights for sidelobe control.

    Uses a cosine-on-pedestal approximation to the Taylor
    distribution.

    Args:
        n_elements: Number of array elements.
        sll_db: Desired sidelobe level in dB (negative).

    Returns:
        Normalised weight list (peak = 1.0).
    """
    if n_elements <= 1:
        return [1.0]
    # Simple Taylor-like taper: raised cosine
    sll_lin = 10 ** (sll_db / 20.0)
    alpha = -sll_db / 20.0  # roughly maps to window shape
    weights = []
    for i in range(n_elements):
        x = 2.0 * i / (n_elements - 1) - 1.0  # -1 to +1
        w = sll_lin + (1.0 - sll_lin) * math.cos(
            math.pi * x / 2.0
        ) ** (2 * alpha)
        weights.append(w)
    # Normalize so peak weight = 1.0
    wmax = max(weights)
    if wmax > 0:
        weights = [w / wmax for w in weights]
    return weights


def _uniform_weights(n_elements: int) -> list[float]:
    """All-ones uniform weighting."""
    return [1.0] * n_elements


def _apply_element_errors(
    weights: list[float],
    phase_offsets: list[float] | None,
    rms_amp_db: float,
    rms_phase_deg: float,
    seed: int = 42,
) -> tuple[list[float], list[float]]:
    """Apply random per-element amplitude and phase errors.

    Uses a deterministic seed so results are repeatable.

    Args:
        weights: Ideal amplitude weights.
        phase_offsets: Existing phase offsets (or None).
        rms_amp_db: RMS amplitude error in dB (0 = none).
        rms_phase_deg: RMS phase error in degrees (0 = none).
        seed: Random seed for repeatability.

    Returns:
        Tuple of (perturbed_weights, perturbed_phases).
    """
    import random as _rnd
    n = len(weights)
    if phase_offsets is None:
        phase_offsets = [0.0] * n

    if rms_amp_db <= 0 and rms_phase_deg <= 0:
        return weights, phase_offsets

    rng = _rnd.Random(seed)
    new_w = list(weights)
    new_p = list(phase_offsets)
    for i in range(n):
        if rms_amp_db > 0:
            err_db = rng.gauss(0.0, rms_amp_db)
            new_w[i] *= 10 ** (err_db / 20.0)
        if rms_phase_deg > 0:
            err_rad = math.radians(rng.gauss(0.0, rms_phase_deg))
            new_p[i] += err_rad
    return new_w, new_p


def _build_coupling_matrix(
    n_elements: int,
    d_lambda: float,
    coupling_mag: float = 0.3,
    coupling_decay: float = 2.0,
) -> list[list[complex]]:
    """Build a normalised mutual-impedance matrix.

    Uses an exponential-decay model for coupling between elements:
        Z_mn = c₀ · exp(-α · |m-n| · d/λ)   for m ≠ n
        Z_mm = 1.0  (self-impedance normalised to unity)

    Args:
        n_elements:    Number of array elements.
        d_lambda:      Element spacing in wavelengths.
        coupling_mag:  Baseline coupling coefficient c₀ (0–1).
        coupling_decay: Exponential decay rate α.

    Returns:
        n×n complex impedance matrix (list-of-lists).
    """
    Z = [[complex(0.0)] * n_elements for _ in range(n_elements)]
    k = 2.0 * math.pi
    for m in range(n_elements):
        for n in range(n_elements):
            if m == n:
                Z[m][n] = complex(1.0, 0.0)
            else:
                dist = abs(m - n) * d_lambda
                mag = coupling_mag * math.exp(-coupling_decay * dist)
                # Phase of mutual impedance rotates with distance
                phase = -k * dist
                Z[m][n] = complex(mag * math.cos(phase),
                                  mag * math.sin(phase))
    return Z


def _solve_coupled_weights(
    Z: list[list[complex]],
    w_ideal: list[float],
) -> list[complex]:
    """Solve for coupled element weights via Gauss elimination.

    Computes  w_coupled = Z⁻¹ · (Z_self · w_ideal)
    where Z_self = I (identity, since Z is normalised).

    This is equivalent to solving Z · w_coupled = w_ideal
    using partial-pivot Gaussian elimination (no numpy needed).

    Args:
        Z: n×n complex impedance matrix.
        w_ideal: Desired (uncoupled) real amplitude weights.

    Returns:
        List of complex coupled weights.
    """
    n = len(w_ideal)
    # Build augmented matrix [Z | w_ideal]
    A = [[Z[i][j] for j in range(n)] for i in range(n)]
    b = [complex(w, 0.0) for w in w_ideal]

    # Forward elimination with partial pivoting
    for col in range(n):
        # Find pivot
        max_val = abs(A[col][col])
        max_row = col
        for row in range(col + 1, n):
            if abs(A[row][col]) > max_val:
                max_val = abs(A[row][col])
                max_row = row
        # Swap rows
        if max_row != col:
            A[col], A[max_row] = A[max_row], A[col]
            b[col], b[max_row] = b[max_row], b[col]

        pivot = A[col][col]
        if abs(pivot) < 1e-12:
            continue  # singular — skip

        for row in range(col + 1, n):
            factor = A[row][col] / pivot
            for j in range(col, n):
                A[row][j] -= factor * A[col][j]
            b[row] -= factor * b[col]

    # Back substitution
    x = [complex(0.0)] * n
    for i in range(n - 1, -1, -1):
        s = b[i]
        for j in range(i + 1, n):
            s -= A[i][j] * x[j]
        if abs(A[i][i]) > 1e-12:
            x[i] = s / A[i][i]
        else:
            x[i] = complex(0.0)
    return x


def _apply_coupling(
    weights: list[float],
    d_lambda: float,
    coupling_mag: float = 0.3,
    coupling_decay: float = 2.0,
) -> tuple[list[float], list[float]]:
    """Apply mutual coupling to ideal weights, returning perturbed amplitudes and phases.

    Args:
        weights:       Ideal (uncoupled) amplitude weights.
        d_lambda:      Element spacing in wavelengths.
        coupling_mag:  Baseline coupling magnitude (0–1).
        coupling_decay: Coupling decay rate.

    Returns:
        Tuple of (amplitude_weights, phase_offsets_rad).
    """
    n = len(weights)
    if n <= 1 or coupling_mag <= 0:
        return weights, [0.0] * n

    Z = _build_coupling_matrix(n, d_lambda, coupling_mag, coupling_decay)
    w_coupled = _solve_coupled_weights(Z, weights)

    # Extract magnitudes and phases
    amps = [abs(w) for w in w_coupled]
    phases = [math.atan2(w.imag, w.real) for w in w_coupled]

    # Normalise amplitudes so peak = 1.0
    a_max = max(amps) if amps else 1.0
    if a_max > 0:
        amps = [a / a_max for a in amps]

    return amps, phases


def _compute_linear_af(
    angle_rad: float,
    n_elements: int,
    d_lambda: float,
    beta_rad: float,
    weights: list[float],
    phase_offsets: list[float] | None = None,
) -> float:
    """Compute array factor magnitude-squared for a linear array.

    Args:
        angle_rad: Observation angle from broadside (radians).
        n_elements: Number of elements.
        d_lambda: Element spacing in wavelengths.
        beta_rad: Progressive phase shift (radians).
        weights: Per-element amplitude weights.
        phase_offsets: Per-element phase offsets from coupling (radians).

    Returns:
        Normalised |AF|**2 (peak = 1.0).
    """
    k = 2.0 * math.pi  # k·d is in wavelengths
    psi = k * d_lambda * math.sin(angle_rad) + beta_rad

    af_real = 0.0
    af_imag = 0.0
    for n, w in enumerate(weights):
        phase = n * psi
        if phase_offsets is not None:
            phase += phase_offsets[n]
        af_real += w * math.cos(phase)
        af_imag += w * math.sin(phase)

    af_sq = af_real ** 2 + af_imag ** 2
    # Normalize by sum of weights squared (max possible |AF|²)
    w_sum_sq = sum(w for w in weights) ** 2
    if w_sum_sq > 0:
        af_sq /= w_sum_sq
    return af_sq


class PhasedArrayAntenna(AntennaBase):
    """Phased array antenna.

    Implements the Pattern Multiplication Theorem with
    configurable linear, planar, or circular array geometries.
    Supports uniform and Taylor amplitude tapers, progressive
    phase beam steering, and grating-lobe warnings.
    """

    @property
    def name(self) -> str:
        return "Array"

    def default_params(self) -> dict:
        return {
            "array_geometry": "linear",
            "array_n_elements_x": 8,
            "array_n_elements_y": 1,
            "array_spacing_x_lambda": 0.5,
            "array_spacing_y_lambda": 0.5,
            "array_steer_az_deg": 0.0,
            "array_steer_el_deg": 0.0,
            "array_weighting": "uniform",
            "array_taper_sll_db": -25.0,
            "array_mutual_coupling": False,
            "array_element_pattern": "gaussian",
            "array_rms_phase_error_deg": 0.0,
            "array_rms_amplitude_error_db": 0.0,
            "array_circular_orientation": "parallel",
            "ftb_ratio_db": 20.0,
            "max_gain_dbi": 18.0,
            "az_beamwidth_deg": 30.0,
            "el_beamwidth_deg": 30.0,
            "f_min_mhz": 2000.0,
            "f_max_mhz": 4000.0,
        }

    def configure(self, cfg: dict) -> None:
        from ui.prompts import (
            prompt_float, prompt_int, prompt_choice,
        )

        cfg["array_geometry"] = prompt_choice(
            "Array geometry:",
            ["linear", "planar", "circular"],
            default=cfg.get("array_geometry", "linear")
        )

        if cfg["array_geometry"] == "circular":
            cfg["array_n_elements_x"] = prompt_int(
                "Number of elements",
                default=cfg.get("array_n_elements_x", 8),
                min_val=2, max_val=256
            )
            cfg["array_spacing_x_lambda"] = prompt_float(
                "Array radius (wavelengths)",
                default=cfg.get(
                    "array_spacing_x_lambda", 1.0),
                min_val=0.1, max_val=100.0
            )
        else:
            cfg["array_n_elements_x"] = prompt_int(
                "Elements in X (azimuth)",
                default=cfg.get("array_n_elements_x", 8),
                min_val=1, max_val=256
            )
            cfg["array_spacing_x_lambda"] = prompt_float(
                "X spacing (wavelengths, 0.5=λ/2)",
                default=cfg.get(
                    "array_spacing_x_lambda", 0.5),
                min_val=0.1, max_val=10.0
            )
            if cfg.get("array_spacing_x_lambda", 0.5) > 0.5:
                print("  ⚠ Spacing > λ/2: grating lobes "
                      "will appear!")

            if cfg["array_geometry"] == "planar":
                cfg["array_n_elements_y"] = prompt_int(
                    "Elements in Y (elevation)",
                    default=cfg.get(
                        "array_n_elements_y", 8),
                    min_val=1, max_val=256
                )
                cfg["array_spacing_y_lambda"] = prompt_float(
                    "Y spacing (wavelengths)",
                    default=cfg.get(
                        "array_spacing_y_lambda", 0.5),
                    min_val=0.1, max_val=10.0
                )

        # Beam steering
        cfg["array_steer_az_deg"] = prompt_float(
            "Steer azimuth (deg, 0=broadside)",
            default=cfg.get("array_steer_az_deg", 0.0),
            min_val=-90, max_val=90
        )
        if cfg["array_geometry"] == "planar":
            cfg["array_steer_el_deg"] = prompt_float(
                "Steer elevation (deg, 0=broadside)",
                default=cfg.get("array_steer_el_deg", 0.0),
                min_val=-90, max_val=90
            )

        cfg["array_weighting"] = prompt_choice(
            "Element weighting:",
            ["uniform", "taylor"],
            default=cfg.get("array_weighting", "uniform")
        )
        if cfg["array_weighting"] == "taylor":
            cfg["array_taper_sll_db"] = prompt_float(
                "Desired sidelobe level (dB, negative)",
                default=cfg.get("array_taper_sll_db", -25),
                max_val=0
            )

        print("\n  Front-to-Back Ratio (FTB):")
        print("  The ratio between the peak forward gain and the")
        print("  maximum gain in the rear hemisphere (180° from")
        print("  boresight).  Higher values = less radiation")
        print("  behind the array.  Typical array: 15-25 dB.")
        cfg["ftb_ratio_db"] = prompt_float(
            "Front-to-back ratio (dB)",
            default=cfg.get("ftb_ratio_db", 20.0),
            min_val=0
        )

        total = (cfg["array_n_elements_x"]
                 * cfg.get("array_n_elements_y", 1))
        print(f"  Total elements: {total}")

    def validate_config(self, cfg: dict) -> list:
        warnings = []
        dx = cfg.get("array_spacing_x_lambda", 0.5)
        if dx > 0.5:
            warnings.append(
                f"X spacing {dx}λ > λ/2: expect grating "
                f"lobes"
            )
        dy = cfg.get("array_spacing_y_lambda", 0.5)
        geo = cfg.get("array_geometry", "linear")
        if geo == "planar" and dy > 0.5:
            warnings.append(
                f"Y spacing {dy}λ > λ/2: expect grating "
                f"lobes in elevation"
            )
        return warnings

    def compute_point_gain(self, az_eff, el_eff,
                           cos_az, cos_el,
                           n_az, n_el, az_bw, el_bw,
                           gain_peak, cfg):
        geo = cfg.get("array_geometry", "linear")
        nx = cfg.get("array_n_elements_x", 8)
        ny = cfg.get("array_n_elements_y", 1)
        dx = cfg.get("array_spacing_x_lambda", 0.5)
        dy = cfg.get("array_spacing_y_lambda", 0.5)
        steer_az = math.radians(
            cfg.get("array_steer_az_deg", 0.0))
        steer_el = math.radians(
            cfg.get("array_steer_el_deg", 0.0))
        ftb_lin = 10 ** (
            -abs(cfg.get("ftb_ratio_db", 20.0)) / 10.0)
        coupling_on = cfg.get("array_mutual_coupling", False)

        weighting = cfg.get("array_weighting", "uniform")
        sll = cfg.get("array_taper_sll_db", -25.0)
        rms_amp = cfg.get("array_rms_amplitude_error_db", 0.0)
        rms_phase = cfg.get("array_rms_phase_error_deg", 0.0)

        az_rad = math.radians(az_eff)
        el_rad = math.radians(el_eff)

        # ── Element pattern ─────────────────────────
        elem_type = cfg.get("array_element_pattern", "gaussian")
        az_hw = az_bw / 2.0
        el_hw = el_bw / 2.0
        if az_hw > 0 and el_hw > 0:
            if elem_type == "cosine":
                # Cosine element: cos(pi/2 * theta/theta_3dB)
                u_az = min(abs(az_eff) / az_hw, 1.0)
                u_el = min(abs(el_eff) / el_hw, 1.0)
                g_element = (math.cos(math.pi / 2.0 * u_az)
                             * math.cos(math.pi / 2.0 * u_el))
                g_element = max(g_element, 0.0) ** 2
            elif elem_type == "patch":
                # Patch element: cos^1.5 rolloff (empirical)
                cos_az_e = math.cos(math.radians(
                    min(abs(az_eff), 90.0)))
                cos_el_e = math.cos(math.radians(
                    min(abs(el_eff), 90.0)))
                g_element = (cos_az_e ** 1.5
                             * cos_el_e ** 1.5)
            else:
                # Gaussian (default)
                r_sq = ((az_eff / az_hw) ** 2
                        + (el_eff / el_hw) ** 2)
                g_element = 0.5 ** r_sq
        else:
            g_element = 1.0

        # ── Array factor ─────────────────────────────
        if geo == "circular":
            # Circular array: elements distributed around
            # a circle of radius R wavelengths
            R = dx  # reuse spacing param as radius
            orientation = cfg.get(
                "array_circular_orientation", "parallel")
            af_sq = self._circular_af(
                az_rad, el_rad, nx, R,
                steer_az, weighting, sll, coupling_on,
                rms_amp, rms_phase, orientation
            )
        elif geo == "planar":
            # Planar: product of two linear AFs
            # X-axis progressive phase for steering
            k = 2.0 * math.pi
            beta_x = -k * dx * math.sin(steer_az)
            beta_y = -k * dy * math.sin(steer_el)

            if weighting == "taylor":
                wx = _taylor_weights(nx, sll)
                wy = _taylor_weights(ny, sll)
            else:
                wx = _uniform_weights(nx)
                wy = _uniform_weights(ny)

            # Apply mutual coupling if enabled
            px = None
            py = None
            if coupling_on:
                wx, px = _apply_coupling(wx, dx)
                wy, py = _apply_coupling(wy, dy)

            # Apply per-element errors
            if rms_amp > 0 or rms_phase > 0:
                wx, px = _apply_element_errors(
                    wx, px, rms_amp, rms_phase, seed=101)
                wy, py = _apply_element_errors(
                    wy, py, rms_amp, rms_phase, seed=202)

            af_x = _compute_linear_af(
                az_rad, nx, dx, beta_x, wx, px
            )
            af_y = _compute_linear_af(
                el_rad, ny, dy, beta_y, wy, py
            )
            af_sq = af_x * af_y
        else:
            # Linear array along X (azimuth)
            k = 2.0 * math.pi
            beta_x = -k * dx * math.sin(steer_az)
            if weighting == "taylor":
                wx = _taylor_weights(nx, sll)
            else:
                wx = _uniform_weights(nx)

            # Apply mutual coupling if enabled
            px = None
            if coupling_on:
                wx, px = _apply_coupling(wx, dx)

            # Apply per-element errors
            if rms_amp > 0 or rms_phase > 0:
                wx, px = _apply_element_errors(
                    wx, px, rms_amp, rms_phase, seed=101)

            af_sq = _compute_linear_af(
                az_rad, nx, dx, beta_x, wx, px
            )

        # ── Pattern Multiplication Theorem ───────────
        g_front = gain_peak * g_element * af_sq

        # ── Back lobe ────────────────────────────────
        back_weight = (1.0 - cos_az) / 2.0
        g_back = gain_peak * ftb_lin * back_weight

        return max(g_front, g_back)

    def _circular_af(self, az_rad, el_rad, n_elem,
                     radius, steer_az, weighting, sll,
                     coupling_on=False,
                     rms_amp=0.0, rms_phase=0.0,
                     orientation="parallel"):
        """Array factor for a circular array.

        Args:
            orientation: "parallel" — all elements point the same
                direction (broadside).  "radial" — each element
                points radially outward from the array centre.
        """
        if weighting == "taylor":
            weights = _taylor_weights(n_elem, sll)
        else:
            weights = _uniform_weights(n_elem)

        # For circular arrays, approximate coupling using
        # the arc distance between adjacent elements
        phase_offsets = None
        if coupling_on:
            arc_spacing = 2.0 * math.pi * radius / n_elem
            weights, phase_offsets = _apply_coupling(
                weights, arc_spacing)

        # Apply per-element errors
        if rms_amp > 0 or rms_phase > 0:
            weights, phase_offsets = _apply_element_errors(
                weights, phase_offsets, rms_amp, rms_phase,
                seed=303)

        k = 2.0 * math.pi
        af_real = 0.0
        af_imag = 0.0

        for n in range(n_elem):
            phi_n = 2.0 * math.pi * n / n_elem

            # Element orientation factor
            if orientation == "radial":
                # Radial: each element's broadside points outward.
                # Gain is proportional to cos(az - phi_n).
                elem_factor = max(
                    math.cos(az_rad - phi_n), 0.0)
            else:
                # Parallel: all elements point broadside (0°)
                elem_factor = 1.0

            # Phase contribution from element position
            phase = k * radius * (
                math.cos(az_rad - phi_n) * math.cos(el_rad)
                - math.cos(steer_az - phi_n)
            )
            if phase_offsets is not None:
                phase += phase_offsets[n]
            w = weights[n] * elem_factor
            af_real += w * math.cos(phase)
            af_imag += w * math.sin(phase)

        af_sq = af_real ** 2 + af_imag ** 2
        w_sum_sq = sum(weights) ** 2
        if w_sum_sq > 0:
            af_sq /= w_sum_sq
        return af_sq

    @property
    def file_prefix(self) -> str:
        return "Array"
