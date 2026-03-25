"""
Panel / Sector antenna type.

Rectangular aperture model using sinc² pattern in both planes.
Common in SIGINT, comms planning, and cellular base station
sector antennas.

Pattern model:
  G(az, el) = G_peak * sinc²(u_az) * sinc²(u_el)
  where u = 1.3916 * sin(θ) / sin(θ_3dB/2)

  The constant 1.3916 is chosen so the pattern is exactly
  -3 dB at the half-power beamwidth: sinc²(1.3916) = 0.5.

  Back lobe uses configurable front-to-back ratio with
  continuous weighting (no discontinuity at ±90°).
"""

import math

from antennas.base import AntennaBase
from core.pattern_math import front_fade_scalar


def _sinc(x: float) -> float:
    """Unnormalized sinc: sin(x)/x, with sinc(0)=1."""
    if abs(x) < 1e-12:
        return 1.0
    return math.sin(x) / x


# Constant: sinc²(K)=0.5 → K≈1.3916
_K3DB = 1.3916


class PanelAntenna(AntennaBase):
    """Panel / Sector antenna.

    Rectangular aperture model using sinc-squared pattern in
    both principal planes with configurable downtilt. Typical
    use: cellular base stations, SIGINT sector coverage.
    """

    @property
    def name(self) -> str:
        return "Panel"

    def default_params(self) -> dict:
        return {
            "ftb_ratio_db": 20.0,
            "max_gain_dbi": 16.0,
            "az_beamwidth_deg": 65.0,
            "el_beamwidth_deg": 10.0,
            "f_min_mhz": 700.0,
            "f_max_mhz": 2700.0,
        }

    def configure(self, cfg: dict) -> None:
        from ui.prompts import prompt_float

        print("\n  Front-to-Back Ratio (FTB):")
        print("  The ratio between the peak forward gain and the")
        print("  maximum gain in the rear hemisphere (180° from")
        print("  boresight).  Higher values = less radiation")
        print("  behind the antenna.  Typical panel: 20-30 dB.")
        cfg["ftb_ratio_db"] = prompt_float(
            "Front-to-back ratio (dB)",
            default=cfg.get("ftb_ratio_db", 20.0),
            min_val=0
        )
        cfg["mechanical_tilt_deg"] = prompt_float(
            "Mechanical tilt (deg, 0=none, positive=down)",
            default=cfg.get("mechanical_tilt_deg",
                            cfg.get("panel_downtilt_deg", 0.0)),
            min_val=-45, max_val=45
        )

    def validate_config(self, cfg: dict) -> list:
        warnings = []
        if cfg.get("ftb_ratio_db", 0) <= 0:
            warnings.append(
                "Front-to-back ratio should be > 0 dB"
            )
        if cfg.get("az_beamwidth_deg", 0) >= 360:
            warnings.append(
                "Panel az beamwidth >= 360 makes no sense "
                "for a sector antenna"
            )
        return warnings

    def compute_point_gain(self, az_eff, el_eff,
                           cos_az, cos_el,
                           n_az, n_el, az_bw, el_bw,
                           gain_peak, cfg):
        ftb_lin = 10 ** (-abs(cfg.get("ftb_ratio_db", 20.0))
                         / 10.0)
        # mechanical_tilt_deg replaces panel_downtilt_deg
        downtilt = cfg.get("mechanical_tilt_deg",
                           cfg.get("panel_downtilt_deg", 0.0))
        el_eff_dt = el_eff - downtilt

        az_hw_rad = math.radians(az_bw / 2.0)
        el_hw_rad = math.radians(el_bw / 2.0)

        # ── Front contribution (sinc² model) ─────────
        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        sig_k = cfg.get("sigmoid_k", 40.0)
        ff = front_fade_scalar(cos_az, k=sig_k)
        if az_hw_rad > 0 and el_hw_rad > 0:
            sin_az_hw = math.sin(az_hw_rad)
            sin_el_hw = math.sin(el_hw_rad)
            if sin_az_hw > 1e-12 and sin_el_hw > 1e-12:
                u_az = (_K3DB * math.sin(math.radians(az_eff))
                        / sin_az_hw)
                u_el = (_K3DB
                        * math.sin(math.radians(el_eff_dt))
                        / sin_el_hw)
                g_az = _sinc(u_az) ** 2
                g_el = _sinc(u_el) ** 2
                g_front = gain_peak * g_az * g_el * ff
            else:
                g_front = 0.0
        else:
            g_front = 0.0

        # ── Back contribution (continuous) ────────────
        back_weight = (1.0 - cos_az) / 2.0
        cos_el_dt = math.cos(math.radians(el_eff_dt))
        el_n_back = max(n_el * 0.5, 1.0)
        back_el = max(abs(cos_el_dt), 1e-12) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el

        return max(g_front, g_back)

    @property
    def file_prefix(self) -> str:
        return "Panel"
