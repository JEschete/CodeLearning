"""
Omnidirectional antenna type.

No azimuth shaping (360° az beamwidth). Elevation pattern
uses cos^n model with sidelobe envelope.
"""

from antennas.base import AntennaBase
from core.pattern_math import (
    compute_sidelobe_envelope,
)


class OmniAntenna(AntennaBase):
    """Omnidirectional antenna.

    Uniform 360-degree azimuth pattern with elevation shaping
    via cos^n model and sidelobe envelope. Typical use:
    base-station collinear arrays, reference measurements.
    """

    @property
    def name(self) -> str:
        return "Omni"

    @property
    def has_az_pattern(self) -> bool:
        return False

    def default_params(self) -> dict:
        return {
            "max_gain_dbi": 5.0,
            "el_beamwidth_deg": 30.0,
            "f_min_mhz": 400.0,
            "f_max_mhz": 6000.0,
        }

    def configure(self, cfg: dict) -> None:
        cfg["az_beamwidth_deg"] = 360.0
        print("  Az beamwidth: 360 deg (omni)")

    def validate_config(self, cfg: dict) -> list:
        warnings = []
        if cfg.get("az_beamwidth_deg", 360) != 360:
            warnings.append(
                "Omni antenna must have az_beamwidth = 360"
            )
        return warnings

    def compute_point_gain(self, az_eff, el_eff,
                           cos_az, cos_el,
                           n_az, n_el, az_bw, el_bw,
                           gain_peak, cfg):
        gain_el = max(abs(cos_el), 0) ** n_el
        g = gain_el * gain_peak
        sl_el = compute_sidelobe_envelope(
            el_eff, el_bw, cfg
        )
        return max(g, sl_el * gain_peak)
