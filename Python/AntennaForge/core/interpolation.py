"""
Pattern interpolation and resampling.

Interpolate between two pattern files at different frequencies
to synthesize patterns at intermediate frequencies without
regenerating. Also supports resampling patterns to different
angular grids.

Uses bicubic (scipy) or bilinear (fallback) interpolation on
the az/el grid.
"""

import logging
import math
import os

logger = logging.getLogger(__name__)

from core.io import (
    read_pattern_csv, write_pattern_csv,
    extract_freq_from_filename,
)


def interpolate_frequency(
    file_lo: str,
    file_hi: str,
    target_freq: float,
    output_path: str | None = None,
) -> str:
    """Interpolate a pattern at an intermediate frequency.

    Given patterns at *f_lo* and *f_hi*, produce a pattern at
    *target_freq* using linear interpolation in the frequency
    domain (per-point).

    Args:
        file_lo: CSV path at lower frequency.
        file_hi: CSV path at higher frequency.
        target_freq: Desired frequency in MHz.
        output_path: Output CSV path (auto-generated if *None*).

    Returns:
        Path to the written CSV file.

    Raises:
        ValueError: If grids differ in size, frequencies can't be
            extracted, or both files share the same frequency.
    """
    az1, el1, data_lo = read_pattern_csv(file_lo)
    az2, el2, data_hi = read_pattern_csv(file_hi)

    if len(az1) != len(az2) or len(el1) != len(el2):
        raise ValueError(
            "Grid sizes must match for interpolation"
        )

    freq_lo = extract_freq_from_filename(file_lo)
    freq_hi = extract_freq_from_filename(file_hi)

    if freq_lo is None or freq_hi is None:
        raise ValueError(
            "Cannot extract frequencies from filenames"
        )
    if freq_lo == freq_hi:
        raise ValueError(
            "Both files are at the same frequency"
        )

    # Interpolation weight
    t = ((target_freq - freq_lo)
         / (freq_hi - freq_lo))
    t = max(0.0, min(1.0, t))

    result = []
    for i in range(len(el1)):
        row = []
        for j in range(len(az1)):
            val = (data_lo[i][j] * (1.0 - t)
                   + data_hi[i][j] * t)
            row.append(round(val, 2))
        result.append(row)

    if output_path is None:
        freq_label = f"{target_freq:.2f}".replace('.', 'p')
        base_dir = os.path.dirname(file_lo) or "."
        output_path = os.path.join(
            base_dir,
            f"interp_{freq_label}MHz.csv"
        )

    write_pattern_csv(output_path, az1, el1, result)
    logger.info("Interpolated pattern at %.2f MHz (t=%.3f)",
                target_freq, t)
    logger.info("  Between: %.2f and %.2f MHz", freq_lo, freq_hi)
    logger.info("  Saved: %s", output_path)
    return output_path


def resample_pattern(
    input_file: str,
    az_step_new: float,
    el_step_new: float,
    output_path: str | None = None,
    method: str = "bilinear",
) -> str:
    """Resample a pattern to a new angular grid.

    Uses scipy ``RectBivariateSpline`` when available; falls back
    to nearest-neighbour otherwise.

    Args:
        input_file: Source CSV path.
        az_step_new: New azimuth step in degrees.
        el_step_new: New elevation step in degrees.
        output_path: Output CSV path (auto-generated if *None*).
        method: ``'bilinear'`` or ``'bicubic'`` (requires scipy).

    Returns:
        Path to the written CSV file.
    """
    az_old, el_old, data_old = read_pattern_csv(input_file)

    # New grid
    n_az_new = int(
        (az_old[-1] - az_old[0]) / az_step_new
    ) + 1
    n_el_new = int(
        (el_old[-1] - el_old[0]) / el_step_new
    ) + 1
    az_new = [round(az_old[0] + i * az_step_new, 4)
              for i in range(n_az_new)]
    el_new = [round(el_old[0] + i * el_step_new, 4)
              for i in range(n_el_new)]

    try:
        # Try scipy for high-quality interpolation
        from scipy.interpolate import RectBivariateSpline
        import numpy as np

        arr = np.array(data_old)
        el_arr = np.array(el_old)
        az_arr = np.array(az_old)

        if method == "bicubic":
            kx, ky = 3, 3
        else:
            kx, ky = 1, 1

        spline = RectBivariateSpline(
            el_arr, az_arr, arr, kx=kx, ky=ky
        )
        result_arr = spline(
            np.array(el_new), np.array(az_new)
        )
        result = [
            [round(float(result_arr[i, j]), 2)
             for j in range(len(az_new))]
            for i in range(len(el_new))
        ]

    except ImportError:
        # Fallback: nearest-neighbor
        logger.debug("scipy not available, using nearest-neighbor resampling")
        result = []
        for new_el in el_new:
            row = []
            # Find nearest el index
            ei = _nearest_idx(el_old, new_el)
            for new_az in az_new:
                ai = _nearest_idx(az_old, new_az)
                row.append(data_old[ei][ai])
            result.append(row)

    if output_path is None:
        base, ext = os.path.splitext(input_file)
        output_path = (
            f"{base}_resampled_{az_step_new}x"
            f"{el_step_new}deg{ext}"
        )

    write_pattern_csv(output_path, az_new, el_new, result)
    logger.info("Resampled: %dx%d -> %dx%d (step: %s\u00b0 x %s\u00b0)",
                len(el_old), len(az_old), len(el_new), len(az_new),
                el_step_new, az_step_new)
    logger.info("Saved: %s", output_path)
    return output_path


def multi_freq_interpolation(
    file_list: list[str],
    target_freqs: list[float],
    output_dir: str | None = None,
) -> list[str]:
    """Interpolate across multiple frequency files.

    Given a sorted list of pattern CSVs at different frequencies,
    produce patterns at each *target_freq* using the two nearest
    bracketing files.

    Args:
        file_list: Paths to pattern CSV files.
        target_freqs: Desired frequencies in MHz.
        output_dir: Directory for output files (auto if *None*).

    Returns:
        List of output CSV paths.

    Raises:
        ValueError: If fewer than 2 files have extractable
            frequencies.
    """
    # Sort files by frequency
    freq_files = []
    for fp in file_list:
        freq = extract_freq_from_filename(fp)
        if freq is not None:
            freq_files.append((freq, fp))
    freq_files.sort(key=lambda x: x[0])

    if len(freq_files) < 2:
        raise ValueError(
            "Need at least 2 files for interpolation"
        )

    if output_dir is None:
        output_dir = os.path.dirname(
            freq_files[0][1]) or "."

    outputs = []
    for target in target_freqs:
        # Find bracketing files
        lo_file = None
        hi_file = None
        for i in range(len(freq_files) - 1):
            if (freq_files[i][0] <= target
                    <= freq_files[i + 1][0]):
                lo_file = freq_files[i][1]
                hi_file = freq_files[i + 1][1]
                break

        if lo_file is None:
            logger.warning("%.2f MHz outside range, skipping", target)
            continue

        freq_label = f"{target:.2f}".replace('.', 'p')
        out = os.path.join(
            output_dir, f"interp_{freq_label}MHz.csv"
        )
        interpolate_frequency(lo_file, hi_file, target, out)
        outputs.append(out)

    return outputs


def _nearest_idx(arr: list[float], val: float) -> int:
    """Find index of nearest value in a sorted list.

    Args:
        arr: Sorted list of numeric values.
        val: Target value to find the nearest match for.

    Returns:
        Index of the element in *arr* closest to *val*.
    """
    best = 0
    best_dist = abs(arr[0] - val)
    for i in range(1, len(arr)):
        d = abs(arr[i] - val)
        if d < best_dist:
            best_dist = d
            best = i
    return best
