"""
Core unit tests for AntennaForge.

Covers:
  - bw_to_exponent
  - front_fade_scalar (sigmoid blend)
  - config save/load round-trip
  - config validation
  - frequency generation
  - CSV round-trip (write + read)
  - Per-antenna compute_point_gain at known angles
  - Pattern rotation identity and 180° flip
  - Pattern arithmetic (add, subtract, scale)
  - Analysis (beamwidth measurement)

Run:
    python -m pytest tests/test_core.py -v
"""

import json
import math
import os
import sys
import tempfile

# Make workspace root importable
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

import pytest

from config import (
    DEFAULT_CONFIG, save_config, load_config,
    generate_frequencies, validate_config, VERSION,
)
from core.pattern_math import (
    bw_to_exponent, front_fade_scalar,
)
from core.io import (
    write_pattern_file, read_pattern_file,
    extract_freq_from_filename,
)
from antennas import (
    available_names, get_antenna,
)
from analysis.analyzer import measure_beamwidth


# ===================================================================
#  HELPERS
# ===================================================================

def _default_cfg(**overrides):
    """Build a config dict with optional overrides."""
    from copy import deepcopy
    cfg = deepcopy(DEFAULT_CONFIG)
    for k, v in overrides.items():
        if k == "features":
            cfg["features"].update(v)
        else:
            cfg[k] = v
    return cfg


# ===================================================================
#  PATTERN MATH
# ===================================================================

class TestBwToExponent:
    """bw_to_exponent converts a 3 dB beamwidth to a cos^n exponent."""

    def test_90_degree_bw(self):
        n = bw_to_exponent(90.0)
        assert n > 0
        # cos(45)^n should ≈ 0.5 (-3 dB)
        half_pw = math.cos(math.radians(45.0)) ** n
        assert abs(half_pw - 0.5) < 0.05

    def test_narrow_beamwidth(self):
        n = bw_to_exponent(10.0)
        assert n > bw_to_exponent(90.0)

    def test_wide_beamwidth(self):
        n = bw_to_exponent(120.0)
        assert n > 0
        assert n < bw_to_exponent(20.0)

    def test_minimum_clamp(self):
        """Very wide BW should still give n > 0."""
        n = bw_to_exponent(360.0)
        assert n >= 0.01


class TestFrontFadeScalar:
    """front_fade_scalar implements sigmoid blend at ±90°.

    NOTE: the argument is cos(az), NOT az in degrees.
    cos_az =  1.0 → boresight   → returns ~1.0
    cos_az =  0.0 → ±90°        → returns  0.5
    cos_az = -1.0 → rear         → returns ~0.0
    """

    def test_boresight_is_one(self):
        assert front_fade_scalar(1.0) == pytest.approx(1.0,
                                                        abs=1e-6)

    def test_rear_is_zero(self):
        val = front_fade_scalar(-1.0)
        assert val < 0.01

    def test_90_is_half(self):
        """At ±90° cos(az)=0, sigmoid should be 0.5."""
        val = front_fade_scalar(0.0)
        assert val == pytest.approx(0.5, abs=1e-6)

    def test_monotonic_decrease(self):
        """Weight should decrease as cos_az goes from 1 to -1."""
        prev = front_fade_scalar(1.0)
        for c in [0.8, 0.5, 0.2, 0.0, -0.2, -0.5, -0.8, -1.0]:
            cur = front_fade_scalar(c)
            assert cur <= prev + 1e-9
            prev = cur


# ===================================================================
#  CONFIG
# ===================================================================

class TestConfigRoundTrip:
    """save_config → load_config preserves values."""

    def test_round_trip(self, tmp_path):
        cfg = _default_cfg(max_gain_dbi=12.5,
                           az_beamwidth_deg=30.0)
        fp = str(tmp_path / "cfg.json")
        save_config(cfg, fp)
        loaded = load_config(fp)
        assert loaded["max_gain_dbi"] == 12.5
        assert loaded["az_beamwidth_deg"] == 30.0
        assert loaded["features"]["sidelobes"]["enabled"] is True

    def test_forward_compat(self, tmp_path):
        """Loading a JSON missing new keys uses defaults."""
        fp = str(tmp_path / "minimal.json")
        with open(fp, 'w') as f:
            json.dump({"max_gain_dbi": 5.0}, f)
        loaded = load_config(fp)
        assert loaded["max_gain_dbi"] == 5.0
        assert "features" in loaded
        assert loaded["antenna_type"] == "LPDA"


class TestConfigValidation:
    """validate_config catches bad configs."""

    def test_valid_default(self):
        cfg = _default_cfg()
        errors = validate_config(cfg)
        assert errors == []

    def test_missing_key(self):
        cfg = _default_cfg()
        del cfg["antenna_type"]
        errors = validate_config(cfg)
        assert any("antenna_type" in e for e in errors)

    def test_wrong_type(self):
        cfg = _default_cfg(max_gain_dbi="not a number")
        errors = validate_config(cfg)
        assert any("max_gain_dbi" in e for e in errors)

    def test_out_of_range(self):
        cfg = _default_cfg(max_gain_dbi=999.0)
        errors = validate_config(cfg)
        assert any("exceeds maximum" in e for e in errors)

    def test_fmin_gt_fmax(self):
        cfg = _default_cfg(f_min_mhz=500.0, f_max_mhz=100.0)
        errors = validate_config(cfg)
        assert any("f_min_mhz" in e for e in errors)

    def test_bad_spacing(self):
        cfg = _default_cfg(freq_spacing="quadratic")
        errors = validate_config(cfg)
        assert any("freq_spacing" in e for e in errors)

    def test_unknown_antenna(self):
        cfg = _default_cfg(antenna_type="FakeAntenna")
        errors = validate_config(cfg)
        assert any("Unknown antenna_type" in e for e in errors)


# ===================================================================
#  FREQUENCY GENERATION
# ===================================================================

class TestFrequencyGeneration:

    def test_single_slice(self):
        f = generate_frequencies(100, 200, 1, "linear")
        assert f == [100]

    def test_two_slices(self):
        f = generate_frequencies(100, 200, 2, "linear")
        assert f == [100, 200]

    def test_linear_spacing(self):
        f = generate_frequencies(100, 500, 5, "linear")
        assert len(f) == 5
        assert f[0] == 100
        assert f[-1] == 500
        # Equal spacing
        step = f[1] - f[0]
        for i in range(1, len(f) - 1):
            assert abs((f[i+1] - f[i]) - step) < 0.01

    def test_log_spacing(self):
        f = generate_frequencies(10, 1000, 3, "log")
        assert len(f) == 3
        assert f[0] == 10
        assert f[-1] == 1000
        # Log-spaced: ratios should be equal
        r1 = f[1] / f[0]
        r2 = f[2] / f[1]
        assert abs(r1 - r2) < 0.1

    def test_zero_slices_raises(self):
        with pytest.raises(ValueError):
            generate_frequencies(100, 200, 0, "linear")


# ===================================================================
#  CSV ROUND-TRIP
# ===================================================================

class TestCSVRoundTrip:

    def test_write_read_identity(self, tmp_path):
        az = [-180, -90, 0, 90, 180]
        el = [-90, 0, 90]
        data = [
            [-10.0, -5.0, 0.0, -5.0, -10.0],
            [-5.0, 7.0, 7.0, 7.0, -5.0],
            [-10.0, -5.0, 0.0, -5.0, -10.0],
        ]
        fp = str(tmp_path / "test_pattern.csv")
        write_pattern_file(fp, az, el, data)
        az2, el2, data2 = read_pattern_file(fp)

        assert az2 == az
        assert el2 == el
        for i in range(len(el)):
            for j in range(len(az)):
                assert abs(data2[i][j] - data[i][j]) < 0.01

    def test_extract_freq(self):
        assert extract_freq_from_filename(
            "LPDA_100p00MHz_copol.csv") == pytest.approx(100.0)
        assert extract_freq_from_filename(
            "Horn_3456p78MHz_copol.csv") == pytest.approx(3456.78)
        assert extract_freq_from_filename(
            "random_file.csv") is None


# ===================================================================
#  ANTENNA POINT GAIN
# ===================================================================

class TestAntennaPointGain:
    """Each antenna returns sensible gain at known angles."""

    @pytest.fixture(params=available_names())
    def antenna_name(self, request):
        return request.param

    def _make_cfg(self, name):
        cfg = _default_cfg(antenna_type=name)
        ant = get_antenna(name)
        for k, v in ant.default_params().items():
            cfg[k] = v
        if name == "Omni":
            cfg["az_beamwidth_deg"] = 360.0
        return cfg

    def test_boresight_is_peak(self, antenna_name):
        """Gain at boresight should be >= gain at 90° off-axis."""
        cfg = self._make_cfg(antenna_name)
        ant = get_antenna(antenna_name)
        az_bw = cfg["az_beamwidth_deg"]
        el_bw = cfg["el_beamwidth_deg"]
        peak = cfg["max_gain_dbi"]
        n_az = bw_to_exponent(az_bw)
        n_el = bw_to_exponent(el_bw)

        g_bore = ant.compute_point_gain(
            0.0, 0.0,
            math.cos(0.0), math.cos(0.0),
            n_az, n_el, az_bw, el_bw, peak, cfg
        )
        g_side = ant.compute_point_gain(
            90.0, 0.0,
            math.cos(math.radians(90.0)), math.cos(0.0),
            n_az, n_el, az_bw, el_bw, peak, cfg
        )
        assert g_bore >= g_side - 0.01

    def test_gain_within_range(self, antenna_name):
        """Boresight gain (linear) should be reasonable."""
        cfg = self._make_cfg(antenna_name)
        ant = get_antenna(antenna_name)
        az_bw = cfg["az_beamwidth_deg"]
        el_bw = cfg["el_beamwidth_deg"]
        peak = cfg["max_gain_dbi"]
        n_az = bw_to_exponent(az_bw)
        n_el = bw_to_exponent(el_bw)

        g = ant.compute_point_gain(
            0.0, 0.0,
            math.cos(0.0), math.cos(0.0),
            n_az, n_el, az_bw, el_bw, peak, cfg
        )
        # g is returned in linear scale — should be positive
        assert g > 0

    def test_returns_finite(self, antenna_name):
        """Gain should be finite at all test angles."""
        cfg = self._make_cfg(antenna_name)
        ant = get_antenna(antenna_name)
        az_bw = cfg["az_beamwidth_deg"]
        el_bw = cfg["el_beamwidth_deg"]
        peak = cfg["max_gain_dbi"]
        n_az = bw_to_exponent(az_bw)
        n_el = bw_to_exponent(el_bw)

        for az in [-180, -90, -45, 0, 45, 90, 180]:
            for el in [-90, -45, 0, 45, 90]:
                cos_a = math.cos(math.radians(az))
                cos_e = math.cos(math.radians(el))
                g = ant.compute_point_gain(
                    float(az), float(el),
                    cos_a, cos_e,
                    n_az, n_el, az_bw, el_bw, peak, cfg
                )
                assert math.isfinite(g), (
                    f"{antenna_name} returned non-finite "
                    f"at az={az}, el={el}: {g}"
                )


# ===================================================================
#  PATTERN ROTATION
# ===================================================================

class TestPatternRotation:

    def _make_pattern(self, tmp_path, name="test.csv"):
        """Create a simple test pattern CSV."""
        az = list(range(-180, 181, 10))
        el = list(range(-90, 91, 10))
        data = []
        for e in el:
            row = []
            for a in az:
                # Simple cosine pattern
                g = 10.0 * math.cos(math.radians(a)) * \
                    math.cos(math.radians(e))
                row.append(round(g, 2))
            data.append(row)
        fp = str(tmp_path / name)
        write_pattern_file(fp, az, el, data)
        return fp, az, el, data

    def test_zero_rotation_identity(self, tmp_path):
        """Zero rotation should produce identical output."""
        from core.rotation import rotate_pattern
        src, az, el, data = self._make_pattern(tmp_path)
        out = str(tmp_path / "rotated.csv")
        rotate_pattern(src, out, 0, 0, 0)
        az2, el2, data2 = read_pattern_file(out)
        assert az2 == az
        assert el2 == el
        for i in range(len(el)):
            for j in range(len(az)):
                assert abs(data2[i][j] - data[i][j]) < 0.1

    @pytest.mark.skipif(not HAS_NUMPY,
                        reason="numpy required")
    def test_180_az_rotation(self, tmp_path):
        """180° az rotation should approximately flip the pattern."""
        from core.rotation import rotate_pattern
        src, az, el, data = self._make_pattern(tmp_path)
        out = str(tmp_path / "flipped.csv")
        rotate_pattern(src, out, 180.0, 0.0, 0.0)
        az2, el2, data2 = read_pattern_file(out)
        # Boresight (0,0) in original → (180,0) → wraps to (-180,0)
        # or somewhere at the back. The gain there should be negative
        # since original cos(180°) = -10
        _, el_out, _ = read_pattern_file(out)
        el0_idx = el_out.index(0) if 0 in el_out else len(el_out)//2
        bore_gain_rotated = data2[el0_idx][az2.index(0)]
        # After 180° rotation, boresight should have the "back" gain
        assert bore_gain_rotated < 0


# ===================================================================
#  PATTERN ARITHMETIC
# ===================================================================

class TestPatternArithmetic:

    def _make_flat(self, tmp_path, name, gain_db):
        """Create a flat-gain pattern CSV."""
        az = list(range(-180, 181, 30))
        el = list(range(-90, 91, 30))
        data = [[gain_db] * len(az) for _ in el]
        fp = str(tmp_path / name)
        write_pattern_file(fp, az, el, data)
        return fp

    def test_scale_pattern(self, tmp_path):
        from core.pattern_ops import scale_pattern
        fp = self._make_flat(tmp_path, "a.csv", 0.0)
        out = str(tmp_path / "scaled.csv")
        scale_pattern(fp, 3.0, out)
        _, _, data = read_pattern_file(out)
        assert abs(data[0][0] - 3.0) < 0.01

    def test_subtract_same_is_zero(self, tmp_path):
        from core.pattern_ops import subtract_patterns
        fp = self._make_flat(tmp_path, "a.csv", 5.0)
        out = str(tmp_path / "diff.csv")
        subtract_patterns(fp, fp, out)
        _, _, data = read_pattern_file(out)
        for row in data:
            for v in row:
                assert abs(v) < 0.01

    def test_multiply_is_add_db(self, tmp_path):
        from core.pattern_ops import multiply_patterns
        fa = self._make_flat(tmp_path, "a.csv", 3.0)
        fb = self._make_flat(tmp_path, "b.csv", 4.0)
        out = str(tmp_path / "product.csv")
        multiply_patterns(fa, fb, out)
        _, _, data = read_pattern_file(out)
        assert abs(data[0][0] - 7.0) < 0.01


# ===================================================================
#  ANALYSIS
# ===================================================================

class TestBeamwidthMeasurement:

    def test_known_cosine_pattern(self):
        """A pure cosine-squared pattern with known 3dB BW."""
        az = list(range(-180, 181, 1))
        # cos^2(az) pattern peaks at 0, drops 3dB at ±45°
        peak_db = 10.0
        gains = []
        for a in az:
            cos_val = math.cos(math.radians(a))
            if cos_val > 0:
                # cos^2 in power → 10*log10(cos^2) = 20*log10(cos)
                g = peak_db + 20.0 * math.log10(max(cos_val, 1e-10))
            else:
                g = peak_db - 60.0
            gains.append(round(g, 2))
        bw = measure_beamwidth(az, gains, peak_db)
        # cos^2 has 3dB BW ≈ 90° (cos²(45°)=0.5 → -3dB)
        assert bw is not None
        assert 80 < bw < 100


# ===================================================================
#  MAIN (standalone runner)
# ===================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
