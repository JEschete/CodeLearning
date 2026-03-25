"""
Log-Periodic Dipole Array (LPDA) antenna type.

Directional pattern with front-to-back ratio, azimuth and
elevation shaping via cos^n model, and sidelobe envelope.

v4.1 pattern model:
  - Continuous main beam + sidelobe (front-facing, radial)
  - Continuous back lobe using (1 - cos_az)/2 weighting
    so endfire (±90°) gets 50% of back lobe → no dead zone
  - Total = max(front contribution, back contribution)
  - No if/else hemisphere switch, no blend artifacts
  - Radial sidelobes (elliptical rings, not rectangular)
  - Sidelobe taper beyond last lobe (no hard cutoff)
"""

import math

from antennas.base import AntennaBase
from core.pattern_math import (
    compute_sidelobe_radial,
    front_fade_scalar,
)


class LPDAntenna(AntennaBase):
    """Log-Periodic Dipole Array antenna.

    Directional pattern with front-to-back ratio, Gaussian
    elliptical main beam, and radial sidelobe envelope.
    Typical use: broadband communications, EMC testing,
    spectrum monitoring.
    """

    @property
    def name(self) -> str:
        return "LPDA"

    def default_params(self) -> dict:
        return {"ftb_ratio_db": 15.0}

    def configure(self, cfg: dict) -> None:
        from ui.prompts import prompt_float

        print("\n  Front-to-Back Ratio (FTB):")
        print("  The ratio between the peak forward gain and the")
        print("  maximum gain in the rear hemisphere (180° from")
        print("  boresight).  Higher values = less radiation")
        print("  behind the antenna.  Typical LPDA: 10-20 dB.")
        cfg["ftb_ratio_db"] = prompt_float(
            "Front-to-back ratio (dB)",
            default=cfg["ftb_ratio_db"], min_val=0
        )

    def validate_config(self, cfg: dict) -> list:
        warnings = []
        if cfg.get("ftb_ratio_db", 0) <= 0:
            warnings.append(
                "Front-to-back ratio should be > 0 dB"
            )
        if cfg.get("az_beamwidth_deg", 0) >= 360:
            warnings.append(
                "LPDA az beamwidth >= 360 makes no "
                "sense for a directional antenna"
            )
        if cfg.get("max_gain_dbi", 0) <= 0:
            warnings.append(
                "Peak gain <= 0 dBi is unusual for LPDA"
            )
        return warnings

    def compute_point_gain(self, az_eff, el_eff,
                           cos_az, cos_el,
                           n_az, n_el, az_bw, el_bw,
                           gain_peak, cfg):
        ftb_lin = 10 ** (-abs(cfg["ftb_ratio_db"]) / 10.0)

        # Apply conservation of energy approximation if enabled
        if cfg.get("ftb_affects_gain", False):
            gain_peak = gain_peak / (1.0 + ftb_lin)

        # ── Front contribution (main beam + sidelobes) ───
        # Elliptical Gaussian beam: gain = peak * 0.5^(r²)
        # where r is the normalized radial distance on the
        # beam ellipse. r=1 on the -3dB contour, giving
        # smooth elliptical iso-gain rings instead of the
        # rectangular contours from separable cos^n models.
        az_hw = az_bw / 2.0
        el_hw = el_bw / 2.0

        # Smooth sigmoid fade replaces hard cos_az > 0 gate
        sig_k = cfg.get("sigmoid_k", 40.0)
        ff = front_fade_scalar(cos_az, k=sig_k)
        if az_hw > 0 and el_hw > 0:
            r_sq = ((az_eff / az_hw) ** 2
                    + (el_eff / el_hw) ** 2)
            g_main = gain_peak * (0.5 ** r_sq) * ff
        else:
            g_main = 0.0

        g_front = g_main

        # Radial sidelobe envelope (elliptical rings)
        sl = compute_sidelobe_radial(
            az_eff, el_eff, az_bw, el_bw, cfg
        )
        g_front = max(g_front, sl * gain_peak)

        # ── Back contribution (continuous, all angles) ───
        # back_weight: 0 at boresight, 0.5 at endfire,
        # 1 at 180°. Ensures no dead zone at ±90°.
        back_weight = (1.0 - cos_az) / 2.0
        # Broader elevation pattern for back lobe
        el_n_back = max(n_el * 0.5, 1.0)
        back_el = max(abs(cos_el), 1e-12) ** el_n_back
        g_back = gain_peak * ftb_lin * back_weight * back_el

        # ── Total: dominant contribution at each point ───
        return max(g_front, g_back)