"""
Link budget calculator.

Given two antenna patterns (Tx and Rx), distance, and frequency,
compute received power at every relative orientation.

  P_rx(az_tx, az_rx) = EIRP_tx(az_tx) - FSPL + G_rx(az_rx)

  FSPL = 20·log10(d_km) + 20·log10(f_MHz) + 32.44  (dB)

Outputs a heatmap of received power vs Tx/Rx pointing angles.
Directly useful for link budget analysis, OJX modeling, and
communications planning.
"""

import math
import os

from core.io import (
    read_pattern_csv, write_pattern_csv,
    extract_freq_from_filename,
)


def free_space_path_loss(distance_km: float, freq_mhz: float) -> float:
    """Compute free-space path loss in dB.

    ``FSPL = 20 log10(d) + 20 log10(f) + 32.44``

    Args:
        distance_km: Distance in kilometres.
        freq_mhz:    Frequency in MHz.

    Returns:
        FSPL in dB, or ``0.0`` if either argument is ≤ 0.
    """
    if distance_km <= 0 or freq_mhz <= 0:
        return 0.0
    return (20.0 * math.log10(distance_km)
            + 20.0 * math.log10(freq_mhz)
            + 32.44)


def compute_link_budget(
    tx_pattern_file: str,
    rx_pattern_file: str,
    distance_km: float,
    freq_mhz: float,
    tx_power_dbm: float = 30.0,
    tx_cable_loss_db: float = 0.0,
    rx_cable_loss_db: float = 0.0,
    output_path: str | None = None,
) -> tuple[str, float, float, float]:
    """Compute received power for all Tx→Rx orientation pairs.

    Generates a 2-D map where X = Tx azimuth offset and
    Y = Rx azimuth offset, both at el = 0° (boresight link).

    ``P_rx = P_tx - L_tx + G_tx(az_tx) - FSPL + G_rx(az_rx) - L_rx``

    Args:
        tx_pattern_file:  Tx gain pattern CSV.
        rx_pattern_file:  Rx gain pattern CSV.
        distance_km:      Link distance in km.
        freq_mhz:         Frequency in MHz.
        tx_power_dbm:     Transmitter power (dBm).
        tx_cable_loss_db: Tx cable loss (dB, positive).
        rx_cable_loss_db: Rx cable loss (dB, positive).
        output_path:      Output CSV (defaults to
                          ``./link_budget_result.csv``).

    Returns:
        ``(output_path, peak_rx_dbm, best_tx_az, best_rx_az)``
    """
    az_tx, el_tx, data_tx = read_pattern_csv(tx_pattern_file)
    az_rx, el_rx, data_rx = read_pattern_csv(rx_pattern_file)

    # Extract boresight (el=0) cuts
    el_tx_0 = len(el_tx) // 2
    el_rx_0 = len(el_rx) // 2
    # Try to find exact 0° index
    for idx, e in enumerate(el_tx):
        if abs(e) < 0.01:
            el_tx_0 = idx
            break
    for idx, e in enumerate(el_rx):
        if abs(e) < 0.01:
            el_rx_0 = idx
            break

    tx_cut = data_tx[el_tx_0]  # Tx gain vs az at el=0
    rx_cut = data_rx[el_rx_0]  # Rx gain vs az at el=0

    fspl = free_space_path_loss(distance_km, freq_mhz)

    result = []
    peak_rx = -999.0
    best_tx_az = 0.0
    best_rx_az = 0.0

    # Build a 2D grid: rows = Rx az, columns = Tx az
    for i, g_rx in enumerate(rx_cut):
        row = []
        for j, g_tx in enumerate(tx_cut):
            p_rx = (tx_power_dbm
                    - abs(tx_cable_loss_db)
                    + g_tx
                    - fspl
                    + g_rx
                    - abs(rx_cable_loss_db))
            row.append(round(p_rx, 2))
            if p_rx > peak_rx:
                peak_rx = p_rx
                best_tx_az = az_tx[j]
                best_rx_az = az_rx[i]
        result.append(row)

    if output_path is None:
        output_path = "./link_budget_result.csv"

    write_pattern_csv(output_path, az_tx, az_rx, result)

    print(f"\n  Link Budget Analysis:")
    print(f"    Distance      : {distance_km:.2f} km")
    print(f"    Frequency     : {freq_mhz:.2f} MHz")
    print(f"    FSPL          : {fspl:.1f} dB")
    print(f"    Tx Power      : {tx_power_dbm:.1f} dBm")
    print(f"    Tx Cable Loss : {tx_cable_loss_db:.1f} dB")
    print(f"    Rx Cable Loss : {rx_cable_loss_db:.1f} dB")
    print(f"    Peak Rx Power : {peak_rx:.1f} dBm "
          f"(Tx az={best_tx_az:.0f}°, "
          f"Rx az={best_rx_az:.0f}°)")
    print(f"    Output        : {output_path}")

    return output_path, peak_rx, best_tx_az, best_rx_az


def compute_link_margin(
    tx_pattern_file: str,
    rx_pattern_file: str,
    distance_km: float,
    freq_mhz: float,
    tx_power_dbm: float = 30.0,
    rx_sensitivity_dbm: float = -90.0,
    tx_cable_loss_db: float = 0.0,
    rx_cable_loss_db: float = 0.0,
) -> dict:
    """Compute link margin at boresight.

    ``Link_Margin = P_rx(boresight) - Rx_sensitivity``

    Args:
        tx_pattern_file:    Tx gain pattern CSV.
        rx_pattern_file:    Rx gain pattern CSV.
        distance_km:        Link distance in km.
        freq_mhz:           Frequency in MHz.
        tx_power_dbm:       Transmitter power (dBm).
        rx_sensitivity_dbm: Receiver sensitivity threshold (dBm).
        tx_cable_loss_db:   Tx cable loss (dB).
        rx_cable_loss_db:   Rx cable loss (dB).

    Returns:
        Dict with keys: ``tx_power_dbm``, ``tx_gain_dbi``,
        ``tx_cable_loss_db``, ``fspl_db``, ``rx_gain_dbi``,
        ``rx_cable_loss_db``, ``rx_power_dbm``,
        ``rx_sensitivity_dbm``, ``link_margin_db``,
        ``distance_km``, ``freq_mhz``.
    """
    az_tx, el_tx, data_tx = read_pattern_csv(tx_pattern_file)
    az_rx, el_rx, data_rx = read_pattern_csv(rx_pattern_file)

    # Boresight gains — find actual 0° indices
    el_tx_0 = len(el_tx) // 2
    az_tx_0 = len(az_tx) // 2
    el_rx_0 = len(el_rx) // 2
    az_rx_0 = len(az_rx) // 2

    for idx, e in enumerate(el_tx):
        if abs(e) < 0.01:
            el_tx_0 = idx
            break
    for idx, a in enumerate(az_tx):
        if abs(a) < 0.01:
            az_tx_0 = idx
            break
    for idx, e in enumerate(el_rx):
        if abs(e) < 0.01:
            el_rx_0 = idx
            break
    for idx, a in enumerate(az_rx):
        if abs(a) < 0.01:
            az_rx_0 = idx
            break

    g_tx = data_tx[el_tx_0][az_tx_0]
    g_rx = data_rx[el_rx_0][az_rx_0]

    fspl = free_space_path_loss(distance_km, freq_mhz)
    p_rx = (tx_power_dbm - abs(tx_cable_loss_db)
            + g_tx - fspl + g_rx - abs(rx_cable_loss_db))
    margin = p_rx - rx_sensitivity_dbm

    result = {
        'tx_power_dbm': tx_power_dbm,
        'tx_gain_dbi': g_tx,
        'tx_cable_loss_db': tx_cable_loss_db,
        'fspl_db': fspl,
        'rx_gain_dbi': g_rx,
        'rx_cable_loss_db': rx_cable_loss_db,
        'rx_power_dbm': round(p_rx, 2),
        'rx_sensitivity_dbm': rx_sensitivity_dbm,
        'link_margin_db': round(margin, 2),
        'distance_km': distance_km,
        'freq_mhz': freq_mhz,
    }

    print(f"\n  Link Budget (Boresight):")
    print(f"    Tx Power       : {tx_power_dbm:+.1f} dBm")
    print(f"    Tx Gain        : {g_tx:+.1f} dBi")
    print(f"    Tx Cable Loss  : -{abs(tx_cable_loss_db):.1f} dB")
    print(f"    FSPL           : -{fspl:.1f} dB")
    print(f"    Rx Gain        : {g_rx:+.1f} dBi")
    print(f"    Rx Cable Loss  : -{abs(rx_cable_loss_db):.1f} dB")
    print(f"    ─────────────────────────────")
    print(f"    Rx Power       : {p_rx:+.1f} dBm")
    print(f"    Rx Sensitivity : {rx_sensitivity_dbm:+.1f} dBm")
    print(f"    Link Margin    : {margin:+.1f} dB "
          f"({'PASS' if margin > 0 else 'FAIL'})")

    return result
