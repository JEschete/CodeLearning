"""
Abstract base class for all antenna types.

Each antenna type implements compute_point_gain() which is called
by the engine for every (az, el) point. Everything else — BW
scaling, asymmetry, breakup, ground reflection, polarization,
noise, cross-pol — is handled by the engine before/after this call.
"""

from abc import ABC, abstractmethod


class AntennaBase(ABC):
    """Base class for antenna type implementations."""

    # ── Identity ──────────────────────────────────────────────

    @property
    @abstractmethod
    def name(self) -> str:
        """Registry key and display name. e.g. 'LPDA'."""
        ...

    @property
    def has_az_pattern(self) -> bool:
        """True if this antenna shapes the azimuth pattern.

        False for omni-directional types where azimuth gain
        is uniform (n_az = 0, az_bw = 360).
        """
        return True

    # ── Config ────────────────────────────────────────────────

    @abstractmethod
    def default_params(self) -> dict:
        """Antenna-specific default config values.

        Merged into cfg at top level. For example, LPDA
        returns {'ftb_ratio_db': 15.0}.
        """
        ...

    @abstractmethod
    def configure(self, cfg: dict) -> None:
        """Interactive prompts for antenna-specific settings.

        Mutates cfg in place. Called by menu_generate after
        the shared parameter prompts.

        Uses lazy imports from ui.prompts so that the antenna
        module doesn't hard-depend on the UI at import time.
        """
        ...

    def validate_config(self, cfg: dict) -> list:
        """Return list of warning strings. Empty = valid."""
        return []

    # ── Pattern computation ───────────────────────────────────

    @abstractmethod
    def compute_point_gain(
        self,
        az_eff: float,
        el_eff: float,
        cos_az: float,
        cos_el: float,
        n_az: float,
        n_el: float,
        az_bw: float,
        el_bw: float,
        gain_peak: float,
        cfg: dict,
    ) -> float:
        """Return co-pol gain (linear) at one (az, el) point.

        The engine handles everything else:
          Before: freq-dependent BW, exponents, VSWR, asymmetry
          After:  breakup, ground reflection, pol loss, noise,
                  cross-pol
        """
        ...

    # ── Filename prefix ───────────────────────────────────────

    @property
    def file_prefix(self) -> str:
        """Prefix for generated CSV filenames."""
        return self.name
