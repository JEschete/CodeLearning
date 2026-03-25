"""
Extended test suite for AntennaForge modules.

Covers:
  - EIRP computation (core/eirp.py)
  - Link budget & link margin (core/link_budget.py)
  - Sidelobe masks (core/sidelobe_masks.py)
  - Interpolation & resampling (core/interpolation.py)
  - Pattern arithmetic (core/pattern_ops.py)
  - Pattern rotation helpers (core/rotation.py)
  - Dependency checker (deps.py)
  - IO edge cases (core/io.py)

Run:
    python -m pytest tests/test_extended.py -v
"""

import json
import math
import os
import sys
import tempfile
import shutil

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

from core.io import (
    write_pattern_file, read_pattern_file, extract_freq_from_filename,
)
from core.pattern_math import bw_to_exponent

# ===================================================================
#  HELPERS
# ===================================================================

def _make_tmp_dir():
    """Create and return a temporary directory."""
    return tempfile.mkdtemp(prefix="af_test_")


def _write_uniform_pattern(filepath, gain_db=10.0, az_range=(-180, 180),
                            el_range=(-90, 90), step=5):
    """Write a simple uniform-gain CSV pattern."""
    az = list(range(az_range[0], az_range[1] + 1, step))
    el = list(range(el_range[0], el_range[1] + 1, step))
    pattern = [[gain_db] * len(az) for _ in el]
    write_pattern_file(filepath, az, el, pattern)
    return filepath, az, el


def _write_gradient_pattern(filepath, peak=20.0, step=5):
    """Write a pattern with peak at boresight (0,0), decaying with angle."""
    az = list(range(-180, 181, step))
    el = list(range(-90, 91, step))
    pattern = []
    for e in el:
        row = []
        for a in az:
            dist = math.sqrt(a ** 2 + e ** 2)
            g = peak - 0.1 * dist  # linear decay with angle
            row.append(round(g, 2))
        pattern.append(row)
    write_pattern_file(filepath, az, el, pattern)
    return filepath, az, el


# ===================================================================
#  IO EDGE CASES
# ===================================================================

class TestIOEdgeCases:
    """Additional IO tests beyond test_core.py."""

    def test_read_pattern_directory_raises(self, tmp_path):
        """read_pattern_file should raise ValueError for a directory."""
        with pytest.raises(ValueError):
            read_pattern_file(str(tmp_path))

    def test_extract_freq_copol_suffix(self):
        assert extract_freq_from_filename("LPDA_165p00MHz_copol.csv") == 165.0

    def test_extract_freq_xpol_suffix(self):
        assert extract_freq_from_filename("Horn_2400p50MHz_xpol.csv") == 2400.5

    def test_extract_freq_no_suffix(self):
        assert extract_freq_from_filename("Dish_950p00MHz.csv") == 950.0

    def test_extract_freq_no_match(self):
        assert extract_freq_from_filename("random_file.csv") is None

    def test_write_read_roundtrip_preserves_shape(self, tmp_path):
        fp = str(tmp_path / "test.csv")
        az = [-10, 0, 10]
        el = [-5, 0, 5]
        data = [[1.1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]]
        write_pattern_file(fp, az, el, data)
        az2, el2, data2 = read_pattern_file(fp)
        assert len(az2) == 3
        assert len(el2) == 3
        assert len(data2) == 3
        assert len(data2[0]) == 3

    def test_write_read_roundtrip_preserves_values(self, tmp_path):
        fp = str(tmp_path / "vals.csv")
        az = [-1, 0, 1]
        el = [-1, 0, 1]
        data = [[-10.5, 0.0, 5.5], [3.3, 20.0, 3.3], [-10.5, 0.0, 5.5]]
        write_pattern_file(fp, az, el, data)
        _, _, data2 = read_pattern_file(fp)
        for r_orig, r_read in zip(data, data2):
            for v_orig, v_read in zip(r_orig, r_read):
                assert abs(v_orig - v_read) < 0.01


# ===================================================================
#  EIRP
# ===================================================================

class TestEIRP:
    """Tests for core/eirp.py."""

    def test_compute_eirp_basic(self, tmp_path):
        from core.eirp import compute_eirp

        fp = str(tmp_path / "pattern.csv")
        _write_uniform_pattern(fp, gain_db=10.0)
        out, peak_eirp, peak_az, peak_el = compute_eirp(
            fp, tx_power_dbm=30.0, cable_loss_db=2.0,
        )
        # EIRP = 30 - 2 + 10 = 38
        assert abs(peak_eirp - 38.0) < 0.1
        assert os.path.isfile(out)

    def test_compute_eirp_negative_cable_loss(self, tmp_path):
        """Negative cable_loss_db should be treated as positive."""
        from core.eirp import compute_eirp

        fp = str(tmp_path / "pattern.csv")
        _write_uniform_pattern(fp, gain_db=10.0)
        _, peak1, _, _ = compute_eirp(fp, 30.0, cable_loss_db=3.0)
        _, peak2, _, _ = compute_eirp(fp, 30.0, cable_loss_db=-3.0)
        assert abs(peak1 - peak2) < 0.01

    def test_compute_eirp_custom_output(self, tmp_path):
        from core.eirp import compute_eirp

        fp = str(tmp_path / "p.csv")
        _write_uniform_pattern(fp, gain_db=5.0)
        custom = str(tmp_path / "custom_eirp.csv")
        out, _, _, _ = compute_eirp(fp, 20.0, 0.0, output_path=custom)
        assert out == custom
        assert os.path.isfile(custom)

    def test_compute_eirp_peak_at_boresight(self, tmp_path):
        """Gradient pattern should have peak near (0, 0)."""
        from core.eirp import compute_eirp

        fp = str(tmp_path / "grad.csv")
        _write_gradient_pattern(fp, peak=15.0, step=5)
        _, _, peak_az, peak_el = compute_eirp(fp, 30.0, 0.0)
        assert abs(peak_az) < 6
        assert abs(peak_el) < 6

    def test_compute_power_density(self, tmp_path):
        from core.eirp import compute_power_density

        fp = str(tmp_path / "pd.csv")
        _write_uniform_pattern(fp, gain_db=10.0)
        out = compute_power_density(fp, 30.0, 0.0, distance_m=1000.0)
        assert os.path.isfile(out)


# ===================================================================
#  LINK BUDGET
# ===================================================================

class TestLinkBudget:
    """Tests for core/link_budget.py."""

    def test_fspl_known_values(self):
        from core.link_budget import free_space_path_loss
        # FSPL at 1 km, 1000 MHz = 20*log10(1) + 20*log10(1000) + 32.44
        # = 0 + 60 + 32.44 = 92.44
        assert abs(free_space_path_loss(1.0, 1000.0) - 92.44) < 0.01

    def test_fspl_zero_distance(self):
        from core.link_budget import free_space_path_loss
        assert free_space_path_loss(0.0, 1000.0) == 0.0

    def test_fspl_zero_freq(self):
        from core.link_budget import free_space_path_loss
        assert free_space_path_loss(10.0, 0.0) == 0.0

    def test_fspl_negative_values(self):
        from core.link_budget import free_space_path_loss
        assert free_space_path_loss(-5.0, 100.0) == 0.0

    def test_link_budget_basic(self, tmp_path):
        from core.link_budget import compute_link_budget

        tx_fp = str(tmp_path / "tx.csv")
        rx_fp = str(tmp_path / "rx.csv")
        _write_uniform_pattern(tx_fp, gain_db=10.0)
        _write_uniform_pattern(rx_fp, gain_db=5.0)

        out, peak_rx, _, _ = compute_link_budget(
            tx_fp, rx_fp,
            distance_km=10.0, freq_mhz=500.0,
            tx_power_dbm=30.0,
        )
        assert os.path.isfile(out)
        # P_rx ≈ 30 + 10 - FSPL(10, 500) + 5 = 45 - FSPL
        from core.link_budget import free_space_path_loss
        fspl = free_space_path_loss(10.0, 500.0)
        expected = 30.0 + 10.0 - fspl + 5.0
        assert abs(peak_rx - expected) < 0.5

    def test_link_margin_pass(self, tmp_path):
        from core.link_budget import compute_link_margin

        tx_fp = str(tmp_path / "tx.csv")
        rx_fp = str(tmp_path / "rx.csv")
        _write_uniform_pattern(tx_fp, gain_db=30.0)
        _write_uniform_pattern(rx_fp, gain_db=30.0)

        result = compute_link_margin(
            tx_fp, rx_fp,
            distance_km=1.0, freq_mhz=100.0,
            tx_power_dbm=40.0,
            rx_sensitivity_dbm=-90.0,
        )
        assert isinstance(result, dict)
        assert "link_margin_db" in result
        # Very high gains + short distance → should pass easily
        assert result["link_margin_db"] > 0

    def test_link_margin_fail(self, tmp_path):
        from core.link_budget import compute_link_margin

        tx_fp = str(tmp_path / "tx.csv")
        rx_fp = str(tmp_path / "rx.csv")
        _write_uniform_pattern(tx_fp, gain_db=-10.0)
        _write_uniform_pattern(rx_fp, gain_db=-10.0)

        result = compute_link_margin(
            tx_fp, rx_fp,
            distance_km=1000.0, freq_mhz=5000.0,
            tx_power_dbm=0.0,
            rx_sensitivity_dbm=-50.0,
        )
        # Very low gains + long distance + high freq → should fail
        assert result["link_margin_db"] < 0


# ===================================================================
#  SIDELOBE MASKS
# ===================================================================

class TestSidelobeMasks:
    """Tests for core/sidelobe_masks.py."""

    def test_itu_580_at_boresight(self):
        from core.sidelobe_masks import itu_r_s580
        mask = itu_r_s580(30.0)
        assert mask.name == "ITU-R S.580-6"
        # At theta < 1°, returns peak gain
        assert mask(0.5) == 30.0

    def test_itu_580_far_off(self):
        from core.sidelobe_masks import itu_r_s580
        mask = itu_r_s580(30.0)
        # At theta > 48°, returns -10
        assert mask(90.0) == -10.0

    def test_itu_580_monotonic_decrease(self):
        from core.sidelobe_masks import itu_r_s580
        mask = itu_r_s580(35.0)
        vals = [mask(t) for t in [0, 2, 5, 10, 20, 30, 50, 90, 180]]
        # Should generally decrease (not strictly at every point, but overall)
        assert vals[0] > vals[-1]

    def test_itu_465_has_name(self):
        from core.sidelobe_masks import itu_r_s465
        mask = itu_r_s465(20.0)
        assert "S.465" in mask.name

    def test_mil_std_envelope(self):
        from core.sidelobe_masks import mil_std_envelope
        mask = mil_std_envelope(30.0, first_sll_db=-20.0)
        assert mask.name == "MIL-STD Envelope"
        # At boresight region
        assert mask(0.5) == 30.0
        # Should decay
        assert mask(90.0) < mask(5.0)

    def test_load_mask_from_json(self, tmp_path):
        from core.sidelobe_masks import load_mask_from_json

        mask_data = {
            "name": "Custom Test Mask",
            "points": [
                {"angle_deg": 0, "max_gain_dbi": 30},
                {"angle_deg": 10, "max_gain_dbi": 10},
                {"angle_deg": 90, "max_gain_dbi": -5},
                {"angle_deg": 180, "max_gain_dbi": -10},
            ],
        }
        fp = str(tmp_path / "mask.json")
        with open(fp, "w") as f:
            json.dump(mask_data, f)

        mask = load_mask_from_json(fp)
        assert mask.name == "Custom Test Mask"
        assert mask(0) == 30.0
        assert mask(180) == -10.0
        # Interpolation at 5° should be between 30 and 10
        v = mask(5.0)
        assert 10.0 < v < 30.0

    def test_pattern_against_mask_pass(self, tmp_path):
        from core.sidelobe_masks import (
            itu_r_s580, test_pattern_against_mask,
        )
        # Very low uniform gain should pass against any reasonable mask
        fp = str(tmp_path / "low.csv")
        _write_uniform_pattern(fp, gain_db=-20.0)
        mask = itu_r_s580(30.0)
        result = test_pattern_against_mask(fp, mask, plane="az")
        assert isinstance(result, dict)
        assert result["passed"] is True
        assert result["n_violations"] == 0


# ===================================================================
#  PATTERN OPERATIONS
# ===================================================================

class TestPatternOps:
    """Tests for core/pattern_ops.py."""

    def test_add_patterns_equal(self, tmp_path):
        from core.pattern_ops import add_patterns

        f1 = str(tmp_path / "a.csv")
        f2 = str(tmp_path / "b.csv")
        out = str(tmp_path / "sum.csv")
        _write_uniform_pattern(f1, gain_db=10.0)
        _write_uniform_pattern(f2, gain_db=10.0)

        add_patterns(f1, f2, out)
        _, _, data = read_pattern_file(out)
        # 10log10(10^1 + 10^1) = 10log10(20) ≈ 13.01
        assert abs(data[0][0] - 13.01) < 0.1

    def test_subtract_patterns(self, tmp_path):
        from core.pattern_ops import subtract_patterns

        f1 = str(tmp_path / "a.csv")
        f2 = str(tmp_path / "b.csv")
        out = str(tmp_path / "diff.csv")
        _write_uniform_pattern(f1, gain_db=15.0)
        _write_uniform_pattern(f2, gain_db=10.0)

        subtract_patterns(f1, f2, out)
        _, _, data = read_pattern_file(out)
        assert abs(data[0][0] - 5.0) < 0.01

    def test_multiply_patterns(self, tmp_path):
        from core.pattern_ops import multiply_patterns

        f1 = str(tmp_path / "a.csv")
        f2 = str(tmp_path / "b.csv")
        out = str(tmp_path / "prod.csv")
        _write_uniform_pattern(f1, gain_db=10.0)
        _write_uniform_pattern(f2, gain_db=5.0)

        multiply_patterns(f1, f2, out)
        _, _, data = read_pattern_file(out)
        # dB sum: 10 + 5 = 15
        assert abs(data[0][0] - 15.0) < 0.01

    def test_scale_pattern(self, tmp_path):
        from core.pattern_ops import scale_pattern

        f1 = str(tmp_path / "a.csv")
        out = str(tmp_path / "scaled.csv")
        _write_uniform_pattern(f1, gain_db=10.0)

        scale_pattern(f1, 3.0, out)
        _, _, data = read_pattern_file(out)
        assert abs(data[0][0] - 13.0) < 0.01

    def test_max_envelope(self, tmp_path):
        from core.pattern_ops import max_envelope

        f1 = str(tmp_path / "a.csv")
        f2 = str(tmp_path / "b.csv")
        out = str(tmp_path / "env.csv")
        _write_uniform_pattern(f1, gain_db=10.0)
        _write_uniform_pattern(f2, gain_db=15.0)

        max_envelope([f1, f2], out)
        _, _, data = read_pattern_file(out)
        assert abs(data[0][0] - 15.0) < 0.01

    def test_average_patterns(self, tmp_path):
        from core.pattern_ops import average_patterns

        f1 = str(tmp_path / "a.csv")
        f2 = str(tmp_path / "b.csv")
        out = str(tmp_path / "avg.csv")
        _write_uniform_pattern(f1, gain_db=10.0)
        _write_uniform_pattern(f2, gain_db=10.0)

        average_patterns([f1, f2], out)
        _, _, data = read_pattern_file(out)
        # avg of equal dB values = same value
        assert abs(data[0][0] - 10.0) < 0.1

    def test_max_envelope_empty_raises(self):
        from core.pattern_ops import max_envelope
        with pytest.raises(ValueError):
            max_envelope([], "out.csv")

    def test_average_empty_raises(self):
        from core.pattern_ops import average_patterns
        with pytest.raises(ValueError):
            average_patterns([], "out.csv")


# ===================================================================
#  INTERPOLATION
# ===================================================================

class TestInterpolation:
    """Tests for core/interpolation.py."""

    def test_interpolate_frequency_midpoint(self, tmp_path):
        from core.interpolation import interpolate_frequency

        f_lo = str(tmp_path / "Ant_100p00MHz_copol.csv")
        f_hi = str(tmp_path / "Ant_200p00MHz_copol.csv")
        _write_uniform_pattern(f_lo, gain_db=10.0)
        _write_uniform_pattern(f_hi, gain_db=20.0)

        out = interpolate_frequency(f_lo, f_hi, target_freq=150.0)
        _, _, data = read_pattern_file(out)
        # linear interp: t=0.5 → 10 + 0.5*(20-10) = 15
        assert abs(data[0][0] - 15.0) < 0.1

    def test_interpolate_frequency_at_lower(self, tmp_path):
        from core.interpolation import interpolate_frequency

        f_lo = str(tmp_path / "A_100p00MHz_copol.csv")
        f_hi = str(tmp_path / "A_200p00MHz_copol.csv")
        _write_uniform_pattern(f_lo, gain_db=10.0)
        _write_uniform_pattern(f_hi, gain_db=20.0)

        out = interpolate_frequency(f_lo, f_hi, target_freq=100.0)
        _, _, data = read_pattern_file(out)
        # t=0 → 10.0
        assert abs(data[0][0] - 10.0) < 0.1

    def test_interpolate_mismatched_grids(self, tmp_path):
        from core.interpolation import interpolate_frequency

        f_lo = str(tmp_path / "X_100p00MHz_copol.csv")
        f_hi = str(tmp_path / "X_200p00MHz_copol.csv")
        _write_uniform_pattern(f_lo, gain_db=10.0, step=5)
        _write_uniform_pattern(f_hi, gain_db=20.0, step=10)

        with pytest.raises(ValueError):
            interpolate_frequency(f_lo, f_hi, target_freq=150.0)

    def test_multi_freq_interpolation(self, tmp_path):
        from core.interpolation import multi_freq_interpolation

        for freq, gain in [(100, 10), (200, 20), (300, 30)]:
            fp = str(tmp_path / f"T_{freq}p00MHz_copol.csv")
            _write_uniform_pattern(fp, gain_db=gain)

        file_list = sorted(str(p) for p in tmp_path.glob("*.csv"))
        results = multi_freq_interpolation(
            file_list, target_freqs=[150.0, 250.0],
        )
        assert len(results) == 2

    def test_multi_freq_too_few_files(self, tmp_path):
        from core.interpolation import multi_freq_interpolation

        fp = str(tmp_path / "T_100p00MHz_copol.csv")
        _write_uniform_pattern(fp, gain_db=10.0)

        with pytest.raises(ValueError):
            multi_freq_interpolation([fp], target_freqs=[150.0])


# ===================================================================
#  ROTATION HELPERS
# ===================================================================

class TestRotation:
    """Tests for core/rotation.py."""

    def test_identity_rotation(self, tmp_path):
        from core.rotation import rotate_pattern

        fp = str(tmp_path / "orig.csv")
        _write_gradient_pattern(fp, peak=20.0, step=10)
        out = str(tmp_path / "rot.csv")

        result = rotate_pattern(fp, out, az_rotate=0, el_tilt=0, roll=0)
        assert result is not None
        # Identity → output should match input
        _, _, d_in = read_pattern_file(fp)
        _, _, d_out = read_pattern_file(result)
        for ri, ro in zip(d_in, d_out):
            for vi, vo in zip(ri, ro):
                assert abs(vi - vo) < 0.01

    def test_rotation_preserves_shape(self, tmp_path):
        from core.rotation import rotate_pattern

        fp = str(tmp_path / "orig.csv")
        fp2, az, el = _write_gradient_pattern(fp, peak=20.0, step=10)
        out = str(tmp_path / "rot.csv")

        rotate_pattern(fp, out, az_rotate=45, el_tilt=10, roll=0)
        az2, el2, data2 = read_pattern_file(out)
        assert len(az2) == len(az)
        assert len(el2) == len(el)

    def test_rotation_internal_helpers(self):
        from core.rotation import (
            _deg2rad, _rad2deg, _azel_to_xyz, _xyz_to_azel,
        )
        # Round-trip degree conversion
        assert abs(_rad2deg(_deg2rad(45.0)) - 45.0) < 1e-10

        # Boresight → (0, 1, 0) and back
        x, y, z = _azel_to_xyz(0, 0)
        az, el = _xyz_to_azel(x, y, z)
        assert abs(az) < 1e-10
        assert abs(el) < 1e-10

    def test_rotation_matrix_identity(self):
        from core.rotation import _rotation_matrix
        R = _rotation_matrix(0, 0, 0)
        # Should be identity
        for i in range(3):
            for j in range(3):
                expected = 1.0 if i == j else 0.0
                assert abs(R[i][j] - expected) < 1e-10


# ===================================================================
#  DEPENDENCY CHECKER
# ===================================================================

class TestDeps:
    """Tests for deps.py."""

    def test_check_all_returns_dict(self):
        from core.deps import check_all
        result = check_all()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"numpy", "scipy", "matplotlib", "pillow"}
        for v in result.values():
            assert isinstance(v, bool)

    def test_missing_packages_is_list(self):
        from core.deps import missing_packages
        result = missing_packages()
        assert isinstance(result, list)

    def test_missing_summary_string(self):
        from core.deps import missing_summary
        result = missing_summary()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_install_command(self):
        from core.deps import install_command
        cmd = install_command()
        assert "pip install" in cmd
        assert "numpy" in cmd

    def test_require_known_package(self):
        from core.deps import require
        # numpy should be available in most test environments
        result = require("numpy", "testing")
        assert isinstance(result, bool)

    def test_require_unknown_package(self):
        from core.deps import require
        result = require("nonexistent_fake_package", "testing")
        assert result is False

    def test_flags_match_check_all(self):
        import core.deps as deps
        status = deps.check_all()
        assert status["numpy"] == deps.HAS_NUMPY
        assert status["scipy"] == deps.HAS_SCIPY
        assert status["matplotlib"] == deps.HAS_MATPLOTLIB
        assert status["pillow"] == deps.HAS_PIL


# ===================================================================
#  GRAPHING SUBFOLDER ORGANIZATION
# ===================================================================

class TestGraphSubfolders:
    """Test that plot functions create output in type-specific subfolders."""

    @pytest.mark.skipif(
        not HAS_NUMPY, reason="Requires numpy"
    )
    def test_plots_build_output_path(self, tmp_path):
        """_build_output_path should create correct subfolder path."""
        try:
            from graphing.plots import _build_output_path
        except ImportError:
            pytest.skip("matplotlib not available")

        fp = str(tmp_path / "pattern.csv")
        result = _build_output_path(fp, "heatmap", "heatmaps")
        assert "heatmaps" in result
        assert result.endswith("_heatmap.png")
        # Directory should have been created
        assert os.path.isdir(os.path.join(str(tmp_path), "heatmaps"))

    def test_multi_plots_output_path(self, tmp_path):
        """_multi_output_path should create correct subfolder path."""
        try:
            from graphing.multi_plots import _multi_output_path
        except ImportError:
            pytest.skip("matplotlib not available")

        f1 = str(tmp_path / "a.csv")
        f2 = str(tmp_path / "b.csv")
        result = _multi_output_path([f1, f2], "gain_vs_freq", "gain_vs_freq")
        assert "gain_vs_freq" in result
        assert result.endswith(".png")


# ===================================================================
#  LINK BUDGET — FSPL FORMULA VERIFICATION
# ===================================================================

class TestFSPLFormula:
    """Verify FSPL against known reference values."""

    def test_fspl_1km_100mhz(self):
        from core.link_budget import free_space_path_loss
        # FSPL = 20*log10(1) + 20*log10(100) + 32.44 = 0 + 40 + 32.44 = 72.44
        assert abs(free_space_path_loss(1.0, 100.0) - 72.44) < 0.01

    def test_fspl_10km_1ghz(self):
        from core.link_budget import free_space_path_loss
        # FSPL = 20*log10(10) + 20*log10(1000) + 32.44 = 20 + 60 + 32.44 = 112.44
        assert abs(free_space_path_loss(10.0, 1000.0) - 112.44) < 0.01

    def test_fspl_doubles_with_distance(self):
        from core.link_budget import free_space_path_loss
        # Doubling distance adds ~6.02 dB
        f1 = free_space_path_loss(10.0, 500.0)
        f2 = free_space_path_loss(20.0, 500.0)
        assert abs((f2 - f1) - 20 * math.log10(2)) < 0.01


# ===================================================================
#  SIDELOBE MASK — DETAILED REGION CHECKS
# ===================================================================

class TestSidelobeRegions:
    """Detailed checks of ITU-R S.580-6 angular regions."""

    def test_region_1_less_than_1_deg(self):
        from core.sidelobe_masks import itu_r_s580
        mask = itu_r_s580(40.0)
        assert mask(0.5) == 40.0
        assert mask(0.0) == 40.0

    def test_region_2_1_to_20_deg(self):
        from core.sidelobe_masks import itu_r_s580
        mask = itu_r_s580(40.0)
        # 32 - 25*log10(5) ≈ 32 - 17.47 = 14.53
        expected = 32.0 - 25.0 * math.log10(5.0)
        assert abs(mask(5.0) - expected) < 0.01

    def test_region_3_20_to_26_deg(self):
        from core.sidelobe_masks import itu_r_s580
        mask = itu_r_s580(40.0)
        assert mask(22.0) == -2.0

    def test_region_5_beyond_48_deg(self):
        from core.sidelobe_masks import itu_r_s580
        mask = itu_r_s580(40.0)
        assert mask(60.0) == -10.0
        assert mask(180.0) == -10.0


# ===================================================================
#  MUTUAL COUPLING MODEL
# ===================================================================

class TestMutualCoupling:
    """Tests for the array mutual coupling impedance-matrix model."""

    def test_coupling_matrix_diagonal_is_unity(self):
        from antennas.array.array_antenna import _build_coupling_matrix
        Z = _build_coupling_matrix(4, 0.5)
        for i in range(4):
            assert abs(Z[i][i] - 1.0) < 1e-12

    def test_coupling_matrix_symmetry(self):
        from antennas.array.array_antenna import _build_coupling_matrix
        Z = _build_coupling_matrix(6, 0.5, coupling_mag=0.4)
        for i in range(6):
            for j in range(6):
                # Z_ij magnitude should equal Z_ji magnitude
                assert abs(abs(Z[i][j]) - abs(Z[j][i])) < 1e-10

    def test_coupling_matrix_decay_with_distance(self):
        from antennas.array.array_antenna import _build_coupling_matrix
        Z = _build_coupling_matrix(5, 0.5, coupling_mag=0.3, coupling_decay=2.0)
        # Adjacent coupling should be stronger than next-nearest
        assert abs(Z[0][1]) > abs(Z[0][2])
        assert abs(Z[0][2]) > abs(Z[0][3])

    def test_coupling_zero_magnitude_returns_identity(self):
        from antennas.array.array_antenna import _build_coupling_matrix
        Z = _build_coupling_matrix(4, 0.5, coupling_mag=0.0)
        for i in range(4):
            for j in range(4):
                expected = 1.0 if i == j else 0.0
                assert abs(Z[i][j]) - expected < 1e-12

    def test_solve_coupled_weights_identity(self):
        from antennas.array.array_antenna import _solve_coupled_weights
        # Identity matrix should return original weights
        n = 4
        Z = [[complex(1 if i == j else 0) for j in range(n)]
             for i in range(n)]
        w = [1.0, 0.8, 0.8, 1.0]
        result = _solve_coupled_weights(Z, w)
        for i in range(n):
            assert abs(result[i].real - w[i]) < 1e-10
            assert abs(result[i].imag) < 1e-10

    def test_apply_coupling_returns_correct_lengths(self):
        from antennas.array.array_antenna import _apply_coupling
        amps, phases = _apply_coupling([1.0] * 8, 0.5)
        assert len(amps) == 8
        assert len(phases) == 8

    def test_apply_coupling_normalised_peak(self):
        from antennas.array.array_antenna import _apply_coupling
        amps, _ = _apply_coupling([1.0] * 6, 0.5)
        assert abs(max(amps) - 1.0) < 1e-10

    def test_apply_coupling_single_element(self):
        from antennas.array.array_antenna import _apply_coupling
        amps, phases = _apply_coupling([1.0], 0.5)
        assert amps == [1.0]
        assert phases == [0.0]

    def test_coupling_changes_pattern(self):
        """Coupling ON vs OFF should produce different gain at off-boresight angles."""
        from antennas.array.array_antenna import PhasedArrayAntenna
        ant = PhasedArrayAntenna()
        params = ant.default_params()
        params["array_n_elements_x"] = 8
        params["array_spacing_x_lambda"] = 0.5

        # Use a moderate off-boresight angle where the array factor
        # is significant but not dominated by the back lobe
        test_az = 10.0

        # Compute without coupling
        params["array_mutual_coupling"] = False
        g_off = ant.compute_point_gain(
            test_az, 0.0,
            math.cos(math.radians(test_az)), 1.0,
            361, 181,
            65.0, 70.0,
            10.0,
            params,
        )

        # Compute same point with coupling
        params["array_mutual_coupling"] = True
        g_on = ant.compute_point_gain(
            test_az, 0.0,
            math.cos(math.radians(test_az)), 1.0,
            361, 181,
            65.0, 70.0,
            10.0,
            params,
        )

        # They should differ (coupling perturbs weights)
        assert g_off != g_on

    def test_coupling_boresight_similar(self):
        """At boresight, coupling should not drastically change gain."""
        from antennas.array.array_antenna import PhasedArrayAntenna
        ant = PhasedArrayAntenna()
        params = ant.default_params()
        params["array_n_elements_x"] = 8
        params["array_spacing_x_lambda"] = 0.5

        params["array_mutual_coupling"] = False
        g_off = ant.compute_point_gain(
            0.0, 0.0, 1.0, 1.0,
            361, 181, 65.0, 70.0, 10.0, params)

        params["array_mutual_coupling"] = True
        g_on = ant.compute_point_gain(
            0.0, 0.0, 1.0, 1.0,
            361, 181, 65.0, 70.0, 10.0, params)

        # Both should be close to gain_peak (within 20%)
        assert abs(g_off - g_on) / g_off < 0.20

    def test_coupling_planar_array(self):
        """Coupling should work for planar arrays too."""
        from antennas.array.array_antenna import PhasedArrayAntenna
        ant = PhasedArrayAntenna()
        params = ant.default_params()
        params["array_geometry"] = "planar"
        params["array_n_elements_x"] = 4
        params["array_n_elements_y"] = 4
        params["array_mutual_coupling"] = True

        g = ant.compute_point_gain(
            15.0, 10.0,
            math.cos(math.radians(15)), math.cos(math.radians(10)),
            361, 181, 65.0, 70.0, 10.0, params)
        assert g > 0

    def test_coupling_circular_array(self):
        """Coupling should work for circular arrays."""
        from antennas.array.array_antenna import PhasedArrayAntenna
        ant = PhasedArrayAntenna()
        params = ant.default_params()
        params["array_geometry"] = "circular"
        params["array_n_elements_x"] = 8
        params["array_spacing_x_lambda"] = 1.0
        params["array_mutual_coupling"] = True

        g = ant.compute_point_gain(
            20.0, 0.0,
            math.cos(math.radians(20)), 1.0,
            361, 181, 65.0, 70.0, 10.0, params)
        assert g > 0

    def test_coupling_with_taylor_weights(self):
        """Coupling should apply on top of Taylor taper."""
        from antennas.array.array_antenna import _apply_coupling, _taylor_weights
        tw = _taylor_weights(8, -25.0)
        amps, phases = _apply_coupling(tw, 0.5)
        assert len(amps) == 8
        # Coupled weights should differ from uncoupled Taylor
        differences = [abs(a - t) for a, t in zip(amps, tw)]
        assert any(d > 1e-6 for d in differences)

    def test_default_params_has_coupling_key(self):
        from antennas.array.array_antenna import PhasedArrayAntenna
        ant = PhasedArrayAntenna()
        params = ant.default_params()
        assert "array_mutual_coupling" in params
        assert params["array_mutual_coupling"] is False


# ===================================================================
#  FREQUENCY SWEEP ANIMATION
# ===================================================================

class TestFreqSweepAnimation:
    """Tests for the frequency sweep animation module."""

    def test_import_animation_module(self):
        from graphing.animation import generate_sweep_animation
        assert callable(generate_sweep_animation)

    @pytest.mark.skipif(
        not HAS_NUMPY, reason="Requires numpy"
    )
    def test_generate_animation_creates_gif(self, tmp_path):
        """Full integration: create CSVs, generate GIF."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")
        try:
            import matplotlib
        except ImportError:
            pytest.skip("matplotlib not installed")

        from core.io import write_pattern_file
        from graphing.animation import generate_sweep_animation
        import numpy as np

        # Create 3 fake frequency-slice CSVs
        az = list(range(-180, 181, 5))
        el = list(range(-90, 91, 5))
        for freq in [100, 200, 300]:
            pattern = []
            for e in el:
                row = [float(10.0 - 0.01 * (a**2 + e**2) + freq * 0.001)
                       for a in az]
                pattern.append(row)
            fname = f"Test_{freq}p00MHz_copol.csv"
            write_pattern_file(str(tmp_path / fname), az, el, pattern)

        csvs = sorted(str(tmp_path / f) for f in os.listdir(tmp_path)
                       if f.endswith((".csv", ".dat")))

        out = str(tmp_path / "test_anim.gif")
        result = generate_sweep_animation(csvs, output_path=out)
        assert os.path.isfile(result)
        assert result.endswith(".gif")

        # Verify it's a valid GIF with multiple frames
        img = Image.open(result)
        assert img.format == "GIF"
        frame_count = 0
        try:
            while True:
                frame_count += 1
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        assert frame_count == 3

    @pytest.mark.skipif(
        not HAS_NUMPY, reason="Requires numpy"
    )
    def test_animation_polar_style(self, tmp_path):
        """Generate polar-style animation."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")
        try:
            import matplotlib
        except ImportError:
            pytest.skip("matplotlib not installed")

        from core.io import write_pattern_file
        from graphing.animation import generate_sweep_animation

        az = list(range(-180, 181, 10))
        el = list(range(-90, 91, 10))
        for freq in [100, 200]:
            pattern = [[float(5.0 - 0.005 * (a**2 + e**2))
                         for a in az] for e in el]
            write_pattern_file(
                str(tmp_path / f"T_{freq}p00MHz_copol.csv"),
                az, el, pattern)

        csvs = sorted(str(tmp_path / f) for f in os.listdir(tmp_path)
                       if f.endswith((".csv", ".dat")))
        out = str(tmp_path / "polar_anim.gif")
        result = generate_sweep_animation(
            csvs, output_path=out, plot_style="polar")
        assert os.path.isfile(result)

    def test_animation_empty_list_raises(self):
        from graphing.animation import generate_sweep_animation
        with pytest.raises(ValueError, match="No valid CSV"):
            generate_sweep_animation([])

    def test_animation_auto_output_path(self, tmp_path):
        """When output_path is None, should create in animations/ subfolder."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")
        try:
            import matplotlib
        except ImportError:
            pytest.skip("matplotlib not installed")

        from core.io import write_pattern_file
        from graphing.animation import generate_sweep_animation

        az = list(range(-180, 181, 10))
        el = list(range(-90, 91, 10))
        for freq in [100, 200]:
            pattern = [[float(5.0) for a in az] for e in el]
            write_pattern_file(
                str(tmp_path / f"X_{freq}p00MHz_copol.csv"),
                az, el, pattern)

        csvs = sorted(str(tmp_path / f) for f in os.listdir(tmp_path)
                       if f.endswith((".csv", ".dat")))
        result = generate_sweep_animation(csvs)
        assert os.path.isfile(result)
        assert "animations" in result
        assert result.endswith("freq_sweep.gif")
