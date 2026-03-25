"""
EIRP (Effective Isotropic Radiated Power) calculator.

Given transmit power and cable/system losses, computes EIRP
at every (az, el) angle from a pattern CSV.

  EIRP(az,el) = P_tx_dBm - L_cable_dB + G(az,el)_dBi

Output: CSV in the same format as antenna patterns but with
values in dBm (EIRP) instead of dBi (gain).
"""

import math
import os

from core.io import (
    read_pattern_csv, write_pattern_csv,
)


def compute_eirp(
    pattern_file: str,
    tx_power_dbm: float,
    cable_loss_db: float,
    output_path: str | None = None,
) -> tuple[str, float, float, float]:
    """Compute EIRP at every (az, el) from a gain pattern.

    ``EIRP(az, el) = P_tx - |L_cable| + G(az, el)``

    Args:
        pattern_file:  Path to gain pattern CSV (dBi).
        tx_power_dbm:  Transmit power in dBm.
        cable_loss_db: Cable/connector loss in dB (positive value;
                       ``abs()`` is applied internally).
        output_path:   Output CSV path.  Auto-generated as
                       ``<pattern>_EIRP.csv`` when *None*.

    Returns:
        ``(output_path, peak_eirp_dbm, peak_az, peak_el)``
    """
    az, el, data = read_pattern_csv(pattern_file)

    eirp_offset = tx_power_dbm - abs(cable_loss_db)

    result = []
    peak_eirp = -999.0
    peak_az = 0.0
    peak_el = 0.0

    for i in range(len(el)):
        row = []
        for j in range(len(az)):
            eirp = data[i][j] + eirp_offset
            row.append(round(eirp, 2))
            if eirp > peak_eirp:
                peak_eirp = eirp
                peak_az = az[j]
                peak_el = el[i]
        result.append(row)

    if output_path is None:
        base, ext = os.path.splitext(pattern_file)
        output_path = f"{base}_EIRP{ext}"

    write_pattern_csv(output_path, az, el, result)

    print(f"\n  EIRP Pattern computed:")
    print(f"    Tx Power       : {tx_power_dbm:.1f} dBm"
          f" ({10**(tx_power_dbm/10)/1000:.2f} W)")
    print(f"    Cable Loss     : {cable_loss_db:.1f} dB")
    print(f"    Peak EIRP      : {peak_eirp:.1f} dBm "
          f"at az={peak_az:.0f}°, el={peak_el:.0f}°")
    print(f"    Peak EIRP      : "
          f"{10**(peak_eirp/10)/1000:.2f} W")
    print(f"    Output         : {output_path}")

    return output_path, peak_eirp, peak_az, peak_el


def compute_power_density(
    pattern_file: str,
    tx_power_dbm: float,
    cable_loss_db: float,
    distance_m: float,
    output_path: str | None = None,
) -> str:
    """Compute power density (W/m²) at a given distance.

    ``PD(az, el) = EIRP(az, el) / (4π d²)``

    Output is written in dBW/m².  Useful for FCC/ITU regulatory
    compliance checks.

    Args:
        pattern_file:  Path to gain pattern CSV (dBi).
        tx_power_dbm:  Transmit power in dBm.
        cable_loss_db: Cable/connector loss in dB.
        distance_m:    Distance from antenna in metres.
        output_path:   Output CSV path (auto-generated if *None*).

    Returns:
        Path to the written CSV.
    """
    az, el, data = read_pattern_csv(pattern_file)
    eirp_offset = tx_power_dbm - abs(cable_loss_db)
    area = 4.0 * math.pi * distance_m ** 2

    result = []
    for i in range(len(el)):
        row = []
        for j in range(len(az)):
            eirp_dbm = data[i][j] + eirp_offset
            eirp_w = 10 ** (eirp_dbm / 10.0) / 1000.0
            pd = eirp_w / area  # W/m²
            pd_dbw = (10.0 * math.log10(max(pd, 1e-30))
                      if pd > 0 else -300)
            row.append(round(pd_dbw, 2))
        result.append(row)

    if output_path is None:
        base, ext = os.path.splitext(pattern_file)
        output_path = f"{base}_PD_{distance_m}m{ext}"

    write_pattern_csv(output_path, az, el, result)
    print(f"  Power density at {distance_m}m saved: "
          f"{output_path}")
    return output_path
