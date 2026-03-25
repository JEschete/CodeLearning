"""
Dish (parabolic reflector) antenna type.

Circular aperture model using the Jinc function [2·J₁(x)/x]².
The Airy pattern is the gold-standard model for circular
aperture antennas — radar dishes, satcom terminals, radio
telescopes.

Pattern model:
  G(θ) = G_peak · η · [2·J₁(u)/u]²
  where u = 1.6163 · sin(θ) / sin(θ_3dB/2)

  The constant 1.6163 is the solution to [2·J₁(u)/u]² = 0.5,
  so the pattern is exactly -3 dB at the half-power beamwidth.

  η is the aperture efficiency (55-65% typical) which accounts
  for feed spillover, aperture blockage, and surface errors.

  Uses scipy.special.j1 when available; falls back to power
  series approximation otherwise.
"""

import math

from antennas.base import AntennaBase
from core.pattern_math import front_fade_scalar

# Try to import scipy for the Bessel function
try:
    from scipy.special import j1 as _scipy_j1
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Constant: [2·J₁(K)/K]² = 0.5 → K ≈ 1.6163
_K3DB = 1.6163


def _j1_approx(x: float) -> float:
    """First-order Bessel function of the first kind.

    Power series: J₁(x) = x/2 - x³/16 + x⁵/384 - x⁷/18432 + ...
    Accurate to ~8 significant figures for |x| < 8.
    For larger x, use asymptotic form.
    """
    ax = abs(x)
    if ax < 8.0:
        # Polynomial approximation (Abramowitz & Stegun)
        y = x * x
        ans1 = x * (72362614232.0
                     + y * (-7895059235.0
                            + y * (242396853.1
                                   + y * (-2972611.439
                                          + y * (15704.48260
                                                 + y * (-30.16036606))))))
        ans2 = (144725228442.0
                + y * (2300535178.0
                       + y * (18583304.74
                              + y * (99447.43394
                                     + y * (376.9991397
                                            + y)))))
        return ans1 / ans2
    else:
        # Asymptotic approximation for large x
        z = 8.0 / ax
        y = z * z
        xx = ax - 2.356194491
        ans1 = (1.0
                + y * (0.183105e-2
                       + y * (-0.3516396496e-4
                              + y * (0.2457520174e-5
                                     + y * (-0.240337019e-6)))))
        ans2 = (0.04687499995
                + y * (-0.2002690873e-3
                       + y * (0.8449199096e-5
                              + y * (-0.88228987e-6
                                     + y * 0.105787412e-6))))
        ans = math.sqrt(0.636619772 / ax) * (
            math.cos(xx) * ans1
            - z * math.sin(xx) * ans2
        )
        if x < 0:
            ans = -ans
        return ans


def _j1(x: float) -> float:
    """J1(x) using scipy if available, else approximation."""
    if HAS_SCIPY:
        return float(_scipy_j1(x))
    return _j1_approx(x)


def _jinc_sq(u: float) -> float:
    """Compute [2*J1(u)/u]**2 with proper limit at u=0."""
    if abs(u) < 1e-10:
        return 1.0
    val = 2.0 * _j1(u) / u
    return val * val


class DishAntenna(AntennaBase):
    """Parabolic reflector (dish) antenna.

    Circular aperture model using the Jinc function
    [2*J1(x)/x]**2 (Airy pattern). Typical use: satellite
    terminals, radar, radio telescopes.
    """

    @property
    def name(self) -> str:
        return "Dish"

    def default_params(self) -> dict:
        return {
            "dish_efficiency": 0.60,
            "feed_edge_taper_db": -12.0,
            "ftb_ratio_db": 30.0,
            "max_gain_dbi": 30.0,
            "az_beamwidth_deg": 5.0,
            "el_beamwidth_deg": 5.0,
            "f_min_mhz": 3000.0,
            "f_max_mhz": 6000.0,
        }

    def configure(self, cfg: dict) -> None:
        from ui.prompts import prompt_float

        cfg["dish_efficiency"] = prompt_float(
            "Aperture efficiency (0.0-1.0, typical 0.55-0.65)",
            default=cfg.get("dish_efficiency", 0.60),
            min_val=0.1, max_val=1.0
        )
        cfg["feed_edge_taper_db"] = prompt_float(
            "Feed edge taper (dB, typical -10 to -15)",
            default=cfg.get("feed_edge_taper_db", -12.0),
            min_val=-30.0, max_val=0.0
        )
        print("\n  Front-to-Back Ratio (FTB):")
        print("  The ratio between the peak forward gain and the")
        print("  maximum gain in the rear hemisphere (180° from")
        print("  boresight).  Higher values = less radiation")
        print("  behind the antenna.  Typical dish: 25-40 dB.")
        cfg["ftb_ratio_db"] = prompt_float(
            "Front-to-back ratio (dB)",
            default=cfg.get("ftb_ratio_db", 30.0),
            min_val=0
        )

    def validate_config(self, cfg: dict) -> list:
        warnings = []
        eff = cfg.get("dish_efficiency", 0.6)
        if eff < 0.3 or eff > 0.85:
            warnings.append(
                f"Dish efficiency {eff:.2f} is unusual "
                f"(typical range: 0.4-0.75)"
            )
        if cfg.get("az_beamwidth_deg", 0) >= 90:
            warnings.append(
                "Dish az beamwidth >= 90° is very unusual"
            )
        if cfg.get("max_gain_dbi", 0) < 15:
            warnings.append(
                "Dish gain < 15 dBi is unusual — "
                "check aperture size"
            )
        return warnings

    @property
    def has_az_pattern(self) -> bool:
        return True

    def compute_point_gain(self, az_eff, el_eff,
                           cos_az, cos_el,
                           n_az, n_el, az_bw, el_bw,
                           gain_peak, cfg):
        eff = cfg.get("dish_efficiency", 0.60)
        ftb_lin = 10 ** (-abs(cfg.get("ftb_ratio_db", 30.0))
                         / 10.0)
        # Feed edge taper: a Gaussian envelope that suppresses
        # sidelobes.  Stronger (more negative) taper = lower
        # sidelobes but wider main beam.  0 dB = uniform
        # illumination (highest sidelobes).
        edge_taper = cfg.get("feed_edge_taper_db", -12.0)
        # Convert to Gaussian sigma: taper_lin = exp(-r²/(2σ²))
        # At r=1 (dish edge), taper_lin = 10^(edge_taper/20)
        taper_lin = 10 ** (edge_taper / 20.0) if edge_taper < 0 else 1.0
        if taper_lin > 0 and taper_lin < 1.0:
            taper_sigma_sq = -0.5 / math.log(taper_lin)
        else:
            taper_sigma_sq = 0.0  # no taper

        # For dish, use radial off-axis angle (circular beam)
        az_rad = math.radians(az_eff)
        el_rad = math.radians(el_eff)

        # Effective half-beamwidths
        az_hw_rad = math.radians(az_bw / 2.0)
        el_hw_rad = math.radians(el_bw / 2.0)

        # ── Front contribution (Jinc² Airy pattern) ──────
        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        sig_k = cfg.get("sigmoid_k", 40.0)
        ff = front_fade_scalar(cos_az, k=sig_k)
        if az_hw_rad > 0 and el_hw_rad > 0:
            # Elliptical radial distance in beamwidth units
            sin_az = math.sin(az_rad)
            sin_el = math.sin(el_rad)
            sin_az_hw = math.sin(az_hw_rad)
            sin_el_hw = math.sin(el_hw_rad)

            if sin_az_hw > 1e-12 and sin_el_hw > 1e-12:
                # Normalized radial distance
                r_sq = ((sin_az / sin_az_hw) ** 2
                        + (sin_el / sin_el_hw) ** 2)
                r = math.sqrt(r_sq)
                u = _K3DB * r
                # Apply feed taper envelope to suppress sidelobes
                if taper_sigma_sq > 0:
                    taper_env = math.exp(
                        -r_sq / (2.0 * taper_sigma_sq))
                else:
                    taper_env = 1.0
                g_front = (gain_peak * eff
                           * _jinc_sq(u)
                           * taper_env * ff)
            else:
                g_front = 0.0
        else:
            g_front = 0.0

        # ── Back contribution ─────────────────────────────
        back_weight = (1.0 - cos_az) / 2.0
        cos_el_v = math.cos(el_rad)
        el_n_back = max(n_el * 0.3, 1.0)
        back_el = max(abs(cos_el_v), 1e-12) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el

        return max(g_front, g_back)

    @property
    def file_prefix(self) -> str:
        return "Dish"
