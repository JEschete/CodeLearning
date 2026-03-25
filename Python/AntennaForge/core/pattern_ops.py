"""
Pattern arithmetic — add, subtract, multiply, and combine patterns.

Operates on CSV files. Useful for:
  - Array factor × element pattern from separate files
  - Difference patterns for monopulse analysis
  - Subtracting a reference pattern to isolate errors
"""

import logging
import math
import os

logger = logging.getLogger(__name__)

from core.io import (
    read_pattern_csv, write_pattern_csv,
)


def _validate_grids(
    az1: list[float], el1: list[float],
    az2: list[float], el2: list[float],
) -> None:
    """Assert two patterns share identical angular grids.

    Raises:
        ValueError: If grid sizes or angle values differ.
    """
    if len(az1) != len(az2) or len(el1) != len(el2):
        raise ValueError(
            f"Grid size mismatch: "
            f"{len(el1)}x{len(az1)} vs "
            f"{len(el2)}x{len(az2)}"
        )
    for a, b in zip(az1, az2):
        if abs(a - b) > 0.001:
            raise ValueError(
                f"Azimuth grid mismatch at {a} vs {b}"
            )
    for a, b in zip(el1, el2):
        if abs(a - b) > 0.001:
            raise ValueError(
                f"Elevation grid mismatch at {a} vs {b}"
            )


def add_patterns(file_a: str, file_b: str, output_path: str) -> str:
    """Add two patterns in dB (power sum in linear).

    ``Result(az,el) = 10 log10(10^(A/10) + 10^(B/10))``

    Args:
        file_a:      First pattern CSV.
        file_b:      Second pattern CSV.
        output_path: Destination CSV.

    Returns:
        *output_path*.
    """
    az1, el1, data_a = read_pattern_csv(file_a)
    az2, el2, data_b = read_pattern_csv(file_b)
    _validate_grids(az1, el1, az2, el2)

    result = []
    for i in range(len(el1)):
        row = []
        for j in range(len(az1)):
            lin_a = 10 ** (data_a[i][j] / 10.0)
            lin_b = 10 ** (data_b[i][j] / 10.0)
            val = 10.0 * math.log10(max(lin_a + lin_b, 1e-20))
            row.append(round(val, 2))
        result.append(row)

    write_pattern_csv(output_path, az1, el1, result)
    logger.info("Pattern sum saved: %s", output_path)
    return output_path


def subtract_patterns(file_a: str, file_b: str, output_path: str) -> str:
    """Subtract pattern B from A in dB.

    ``Result(az,el) = A(az,el) - B(az,el)``  (dB difference).
    Useful for comparing a measured pattern to a reference.

    Args:
        file_a:      Minuend pattern CSV.
        file_b:      Subtrahend pattern CSV.
        output_path: Destination CSV.

    Returns:
        *output_path*.
    """
    az1, el1, data_a = read_pattern_csv(file_a)
    az2, el2, data_b = read_pattern_csv(file_b)
    _validate_grids(az1, el1, az2, el2)

    result = []
    for i in range(len(el1)):
        row = []
        for j in range(len(az1)):
            val = data_a[i][j] - data_b[i][j]
            row.append(round(val, 2))
        result.append(row)

    write_pattern_csv(output_path, az1, el1, result)
    logger.info("Pattern difference saved: %s", output_path)
    return output_path


def multiply_patterns(file_a: str, file_b: str, output_path: str) -> str:
    """Multiply two patterns (add in dB).

    ``Result(az,el) = A(az,el) + B(az,el)``  in dB.
    Implements the Pattern Multiplication Theorem: element
    pattern × array factor.

    Args:
        file_a:      Element pattern CSV.
        file_b:      Array factor CSV.
        output_path: Destination CSV.

    Returns:
        *output_path*.
    """
    az1, el1, data_a = read_pattern_csv(file_a)
    az2, el2, data_b = read_pattern_csv(file_b)
    _validate_grids(az1, el1, az2, el2)

    result = []
    for i in range(len(el1)):
        row = []
        for j in range(len(az1)):
            val = data_a[i][j] + data_b[i][j]
            row.append(round(val, 2))
        result.append(row)

    write_pattern_csv(output_path, az1, el1, result)
    logger.info("Pattern product saved: %s", output_path)
    return output_path


def scale_pattern(file_a: str, scale_db: float, output_path: str) -> str:
    """Add a constant dB offset to a pattern.

    Useful for applying cable loss or amplifier gain.

    Args:
        file_a:      Source pattern CSV.
        scale_db:    Offset in dB (positive = gain, negative = loss).
        output_path: Destination CSV.

    Returns:
        *output_path*.
    """
    az, el, data = read_pattern_csv(file_a)

    result = []
    for i in range(len(el)):
        row = []
        for j in range(len(az)):
            val = data[i][j] + scale_db
            row.append(round(val, 2))
        result.append(row)

    write_pattern_csv(output_path, az, el, result)
    logger.info("Scaled pattern saved: %s", output_path)
    return output_path


def max_envelope(file_list: list[str], output_path: str) -> str:
    """Compute the max-hold envelope across multiple patterns.

    At each (az, el) keeps the maximum gain across all files.
    Useful for worst-case interference envelopes.

    Args:
        file_list:   List of pattern CSV paths.
        output_path: Destination CSV.

    Returns:
        *output_path*.

    Raises:
        ValueError: If *file_list* is empty.
    """
    if not file_list:
        raise ValueError("No files provided")

    az, el, data = read_pattern_csv(file_list[0])
    result = [row[:] for row in data]

    for fp in file_list[1:]:
        az2, el2, data2 = read_pattern_csv(fp)
        _validate_grids(az, el, az2, el2)
        for i in range(len(el)):
            for j in range(len(az)):
                result[i][j] = max(result[i][j],
                                   data2[i][j])

    write_pattern_csv(output_path, az, el, result)
    logger.info("Max envelope saved: %s", output_path)
    return output_path


def average_patterns(file_list: list[str], output_path: str) -> str:
    """Compute the power-average of multiple patterns.

    Averages in the linear domain, then converts back to dB.

    Args:
        file_list:   List of pattern CSV paths.
        output_path: Destination CSV.

    Returns:
        *output_path*.

    Raises:
        ValueError: If *file_list* is empty.
    """
    if not file_list:
        raise ValueError("No files provided")

    az, el, data = read_pattern_csv(file_list[0])
    n_files = len(file_list)

    # Accumulate in linear
    accum = []
    for i in range(len(el)):
        row = []
        for j in range(len(az)):
            row.append(10 ** (data[i][j] / 10.0))
        accum.append(row)

    for fp in file_list[1:]:
        az2, el2, data2 = read_pattern_csv(fp)
        _validate_grids(az, el, az2, el2)
        for i in range(len(el)):
            for j in range(len(az)):
                accum[i][j] += 10 ** (data2[i][j] / 10.0)

    result = []
    for i in range(len(el)):
        row = []
        for j in range(len(az)):
            avg_lin = accum[i][j] / n_files
            val = 10.0 * math.log10(max(avg_lin, 1e-20))
            row.append(round(val, 2))
        result.append(row)

    write_pattern_csv(output_path, az, el, result)
    logger.info("Average pattern saved: %s", output_path)
    return output_path
