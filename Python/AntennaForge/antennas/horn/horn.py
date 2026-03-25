"""
Horn (pyramidal) antenna type.

Standard gain horn model using separate E-plane and H-plane
aperture distributions. The E-plane has a uniform illumination
(sinc pattern) while the H-plane has a cosine taper
(sinc × cos pattern), which is the standard model for a
pyramidal horn antenna.

Pattern model:
  E-plane (elevation): sinc²(u_el)
  H-plane (azimuth):   [cos(v) / (1 - (2v/π)²)]²

  where u_el = 1.3916 · sin(θ_el) / sin(θ_el_3dB/2)
        v    = 1.1891 · sin(θ_az) / sin(θ_az_3dB/2)

  The H-plane constant 1.1891 gives -3 dB at the beamwidth.

Used as a lab reference antenna, radar feed, and calibration
standard.
"""

import math

from antennas.base import AntennaBase
from core.pattern_math import front_fade_scalar


def _sinc(x: float) -> float:
    """Unnormalized sinc: sin(x)/x, with sinc(0)=1."""
    if abs(x) < 1e-12:
        return 1.0
    return math.sin(x) / x


# E-plane: sinc²(K) = 0.5 → K ≈ 1.3916
_K_E = 1.3916

# H-plane: [cos(K) / (1 - (2K/π)²)]² = 0.5 → K ≈ 1.1891
_K_H = 1.1891


def _horn_h_plane(v: float) -> float:
    """H-plane pattern factor: cos(v)/(1-(2v/pi)**2).

    Returns 1.0 at v=0, drops to 0 at v=π/2.
    The denominator goes to zero at v=±π/2 but
    L'Hôpital gives a finite value there.
    """
    denom = 1.0 - (2.0 * v / math.pi) ** 2
    if abs(denom) < 1e-10:
        # L'Hôpital's rule limit: π/4 · cos(v)
        return math.pi / 4.0 * math.cos(v)
    return math.cos(v) / denom


class HornAntenna(AntennaBase):
    """Pyramidal horn antenna.

    E-plane uses sinc-squared pattern, H-plane uses cosine
    taper. Standard gain horn model for use as a calibration
    reference, radar feed, or lab standard.
    """

    @property
    def name(self) -> str:
        return "Horn"

    def default_params(self) -> dict:
        return {
            "ftb_ratio_db": 25.0,
            "horn_aperture_wavelengths": None,
            "max_gain_dbi": 15.0,
            "az_beamwidth_deg": 30.0,
            "el_beamwidth_deg": 30.0,
            "f_min_mhz": 4000.0,
            "f_max_mhz": 8000.0,
        }

    def configure(self, cfg: dict) -> None:
        from ui.prompts import prompt_float

        print("\n  Horn Aperture (optional):")
        print("  If set, beamwidth is derived from aperture size")
        print("  and scales properly with frequency.  Leave at 0")
        print("  to use manual beamwidth settings.")
        aperture = prompt_float(
            "Aperture width (wavelengths, 0=manual BW)",
            default=cfg.get("horn_aperture_wavelengths") or 0.0,
            min_val=0.0, max_val=100.0
        )
        cfg["horn_aperture_wavelengths"] = (
            aperture if aperture > 0 else None
        )

        print("\n  Front-to-Back Ratio (FTB):")
        print("  The ratio between the peak forward gain and the")
        print("  maximum gain in the rear hemisphere (180° from")
        print("  boresight).  Higher values = less radiation")
        print("  behind the antenna.  Typical horn: 20-30 dB.")
        cfg["ftb_ratio_db"] = prompt_float(
            "Front-to-back ratio (dB)",
            default=cfg.get("ftb_ratio_db", 25.0),
            min_val=0
        )

    def validate_config(self, cfg: dict) -> list:
        warnings = []
        if cfg.get("az_beamwidth_deg", 0) >= 180:
            warnings.append(
                "Horn az beamwidth >= 180° is unusual"
            )
        if cfg.get("max_gain_dbi", 0) < 5:
            warnings.append(
                "Horn gain < 5 dBi is very low"
            )
        return warnings

    def compute_point_gain(self, az_eff, el_eff,
                           cos_az, cos_el,
                           n_az, n_el, az_bw, el_bw,
                           gain_peak, cfg):
        ftb_lin = 10 ** (-abs(cfg.get("ftb_ratio_db", 25.0))
                         / 10.0)

        az_hw_rad = math.radians(az_bw / 2.0)
        el_hw_rad = math.radians(el_bw / 2.0)

        # ── Front contribution ────────────────────────
        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        sig_k = cfg.get("sigmoid_k", 40.0)
        ff = front_fade_scalar(cos_az, k=sig_k)
        if az_hw_rad > 0 and el_hw_rad > 0:
            sin_az = math.sin(math.radians(az_eff))
            sin_el = math.sin(math.radians(el_eff))
            sin_az_hw = math.sin(az_hw_rad)
            sin_el_hw = math.sin(el_hw_rad)

            if sin_az_hw > 1e-12 and sin_el_hw > 1e-12:
                # E-plane (elevation): sinc² pattern
                u_el = _K_E * sin_el / sin_el_hw
                g_el = _sinc(u_el) ** 2

                # H-plane (azimuth): cos-taper pattern
                v_az = _K_H * sin_az / sin_az_hw
                g_az = _horn_h_plane(v_az) ** 2

                g_front = gain_peak * g_az * g_el * ff
            else:
                g_front = 0.0
        else:
            g_front = 0.0

        # ── Back contribution ─────────────────────────
        back_weight = (1.0 - cos_az) / 2.0
        el_n_back = max(n_el * 0.3, 1.0)
        back_el = (max(abs(cos_el), 1e-12) ** el_n_back)
        g_back = gain_peak * ftb_lin * back_weight * back_el

        return max(g_front, g_back)

    @property
    def file_prefix(self) -> str:
        return "Horn"
