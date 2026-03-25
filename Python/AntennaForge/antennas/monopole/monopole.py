"""
Monopole / Dipole antenna type.

Canonical vertically polarized reference antenna with
omnidirectional azimuth pattern and elevation pattern
determined entirely by the electrical length.

The elevation pattern is the sole source of truth — there is no
separate el_beamwidth_deg parameter.  The dipole formula fully
determines the beam shape:

  G(el) = G_peak · [cos(kL·sin(el)/2) - cos(kL/2)]²
           / [1 - cos(kL/2)]² / cos²(el)

  where kL = 2π·L, L is element length in wavelengths.

When ``monopole_physical_length_m`` is set, the electrical length
scales with frequency:  L(f) = physical_length / (c / f).
This models a fixed physical element whose pattern changes across
the band (e.g. a 0.25λ monopole at f_min becomes 0.5λ at 2×f_min).

When only ``element_length_wavelengths`` is set (no physical
length), every frequency slice uses the same electrical length.
"""

import math

from antennas.base import AntennaBase


class MonopoleAntenna(AntennaBase):
    """Monopole / Dipole antenna.

    Vertically polarized reference antenna with omnidirectional
    azimuth pattern and elevation pattern determined entirely by
    the electrical element length.  Supports quarter-wave,
    half-wave, and arbitrary dipole lengths.  Optional physical
    length enables frequency-dependent pattern evolution.
    """

    @property
    def name(self) -> str:
        return "Monopole"

    @property
    def has_az_pattern(self) -> bool:
        return False

    def default_params(self) -> dict:
        return {
            "element_length_wavelengths": 0.25,
            "monopole_physical_length_m": None,
            "max_gain_dbi": 2.15,
            "f_min_mhz": 100.0,
            "f_max_mhz": 500.0,
        }

    def configure(self, cfg: dict) -> None:
        from ui.prompts import (
            prompt_float, prompt_choice,
        )

        cfg["az_beamwidth_deg"] = 360.0
        print("  Az beamwidth: 360 deg (omnidirectional)")

        preset = prompt_choice(
            "Element type:",
            ["Quarter-wave monopole (0.25λ)",
             "Half-wave dipole (0.5λ)",
             "Custom length"],
            default="Quarter-wave monopole (0.25λ)"
        )
        if "Quarter" in preset:
            cfg["element_length_wavelengths"] = 0.25
        elif "Half" in preset:
            cfg["element_length_wavelengths"] = 0.5
        else:
            cfg["element_length_wavelengths"] = prompt_float(
                "Element length (wavelengths)",
                default=cfg.get(
                    "element_length_wavelengths", 0.25),
                min_val=0.05, max_val=5.0
            )
        print(f"  Element length: "
              f"{cfg['element_length_wavelengths']}λ")

        use_phys = prompt_choice(
            "Frequency-dependent pattern?",
            ["No (fixed electrical length)",
             "Yes (specify physical length)"],
            default="No (fixed electrical length)"
        )
        if "Yes" in use_phys:
            cfg["monopole_physical_length_m"] = prompt_float(
                "Physical element length (metres)",
                default=cfg.get(
                    "monopole_physical_length_m", 0.5),
                min_val=0.001, max_val=100.0
            )
        else:
            cfg["monopole_physical_length_m"] = None

    def validate_config(self, cfg: dict) -> list:
        warnings = []
        L = cfg.get("element_length_wavelengths", 0.25)
        if L > 1.5:
            warnings.append(
                f"Element length {L}λ will produce many "
                f"elevation lobes — verify this is intended"
            )
        if cfg.get("az_beamwidth_deg", 360) != 360:
            warnings.append(
                "Monopole must have az_beamwidth = 360"
            )
        return warnings

    @staticmethod
    def electrical_length(cfg: dict, freq_mhz: float) -> float:
        """Return element length in wavelengths at *freq_mhz*.

        If ``monopole_physical_length_m`` is set, scale with
        frequency.  Otherwise return the fixed value.
        """
        phys = cfg.get("monopole_physical_length_m")
        if phys and freq_mhz > 0:
            wavelength = 300.0 / freq_mhz
            return phys / wavelength
        return cfg.get("element_length_wavelengths", 0.25)

    def compute_point_gain(self, az_eff, el_eff,
                           cos_az, cos_el,
                           n_az, n_el, az_bw, el_bw,
                           gain_peak, cfg):
        L = cfg.get("element_length_wavelengths", 0.25)
        kL = 2.0 * math.pi * L  # k·L in radians

        el_rad = math.radians(el_eff)
        cos_el_v = math.cos(el_rad)
        sin_el_v = math.sin(el_rad)

        # Avoid division by zero at el = ±90°
        if abs(cos_el_v) < 1e-10:
            return gain_peak * 1e-7

        # General dipole pattern:
        # F(el) = [cos(kL/2·sin(el)) - cos(kL/2)] / cos(el)
        numerator = (math.cos(kL / 2.0 * sin_el_v)
                     - math.cos(kL / 2.0))
        denom_norm = 1.0 - math.cos(kL / 2.0)

        if abs(denom_norm) < 1e-12:
            # Degenerate case (full-wave): use cos^n fallback
            g_el = max(abs(cos_el_v), 1e-12) ** n_el
            return gain_peak * g_el

        f_el = numerator / (denom_norm * cos_el_v)
        g = gain_peak * f_el * f_el

        return max(g, gain_peak * 1e-7)

    @property
    def file_prefix(self) -> str:
        return "Monopole"
