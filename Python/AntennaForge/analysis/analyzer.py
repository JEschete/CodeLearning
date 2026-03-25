"""
Pattern analysis functions.

Depends only on core.io for CSV reading.
"""

import math
import os

from core.io import read_pattern_csv


# ===================================================================
#  SINGLE FILE ANALYSIS
# ===================================================================

def analyze_single(filepath: str) -> dict:
    """Full analysis of a single pattern CSV.

    Prints detailed statistics and returns a summary dict with
    keys: ``file``, ``peak_gain``, ``bore_gain``, ``az_bw``,
    ``el_bw``, ``min_gain``, ``avg_gain``.

    Args:
        filepath: Path to a pattern CSV file.

    Returns:
        Analysis results dictionary.
    """
    print(f"\n  Analyzing: {os.path.basename(filepath)}")
    print("  " + "-" * 50)

    az, el, data = read_pattern_csv(filepath)
    n_el = len(el)
    n_az = len(az)

    # Find key indices
    az0 = az.index(0.0) if 0.0 in az else n_az // 2
    el0 = el.index(0.0) if 0.0 in el else n_el // 2

    # Global stats
    all_vals = [v for row in data for v in row]
    peak_gain = max(all_vals)
    min_gain = min(all_vals)
    avg_gain = sum(all_vals) / len(all_vals)

    # Find peak location
    peak_el_idx = 0
    peak_az_idx = 0
    for i, row in enumerate(data):
        for j, v in enumerate(row):
            if v == peak_gain:
                peak_el_idx = i
                peak_az_idx = j

    print(f"\n  GLOBAL STATISTICS:")
    print(f"    Peak gain      : {peak_gain:.2f} dBi")
    print(f"    Peak location  : az={az[peak_az_idx]:.0f} "
          f"deg, el={el[peak_el_idx]:.0f} deg")
    print(f"    Min gain       : {min_gain:.2f} dBi")
    print(f"    Mean gain      : {avg_gain:.2f} dBi")
    print(f"    Dynamic range  : "
          f"{peak_gain - min_gain:.2f} dB")
    print(f"    Grid size      : {n_el} x {n_az}")

    # Boresight gain
    bore_gain = data[el0][az0]
    print(f"\n  BORESIGHT (az=0, el=0):")
    print(f"    Gain           : {bore_gain:.2f} dBi")

    # Az cut at el=0
    az_cut = data[el0]
    az_bw = measure_beamwidth(az, az_cut, bore_gain)
    print(f"\n  AZIMUTH CUT (el=0):")
    print(f"    3dB beamwidth  : ~{az_bw} deg")

    # Front-to-back
    if 180.0 in az:
        az180 = az.index(180.0)
        back_gain = data[el0][az180]
        ftb = bore_gain - back_gain
        print(f"    Back lobe      : {back_gain:.2f} dBi")
        print(f"    Front-to-back  : {ftb:.1f} dB")

    # First sidelobe
    sl = find_first_sidelobe(az, az_cut, bore_gain, az_bw)
    if sl:
        print(f"    1st sidelobe   : {sl['level']:.1f} dBi "
              f"at az={sl['angle']:.0f} deg "
              f"({sl['relative']:.1f} dB below peak)")

    # El cut at az=0
    el_cut = [data[i][az0] for i in range(n_el)]
    el_bw = measure_beamwidth(el, el_cut, bore_gain)
    print(f"\n  ELEVATION CUT (az=0):")
    print(f"    3dB beamwidth  : ~{el_bw} deg")

    # Hemispheric power
    front_vals = []
    back_vals = []
    for i, row in enumerate(data):
        for j, v in enumerate(row):
            if -90 <= az[j] <= 90:
                front_vals.append(v)
            else:
                back_vals.append(v)

    if front_vals and back_vals:
        front_avg = sum(front_vals) / len(front_vals)
        back_avg = sum(back_vals) / len(back_vals)
        print(f"\n  HEMISPHERIC ANALYSIS:")
        print(f"    Front avg gain : {front_avg:.2f} dBi")
        print(f"    Back avg gain  : {back_avg:.2f} dBi")
        print(f"    F/B avg diff   : "
              f"{front_avg - back_avg:.1f} dB")

    # Symmetry check
    asym_az = check_symmetry_az(az, data, el0)
    asym_el = check_symmetry_el(el, data, az0)
    print(f"\n  SYMMETRY CHECK:")
    print(f"    Az asymmetry   : {asym_az:.2f} dB (RMS)")
    print(f"    El asymmetry   : {asym_el:.2f} dB (RMS)")

    # Coverage stats
    above_0 = sum(1 for v in all_vals if v >= 0)
    above_m3 = sum(
        1 for v in all_vals if v >= peak_gain - 3
    )
    above_m10 = sum(
        1 for v in all_vals if v >= peak_gain - 10
    )
    total = len(all_vals)
    print(f"\n  COVERAGE:")
    print(f"    >= 0 dBi       : "
          f"{above_0}/{total} "
          f"({100*above_0/total:.1f}%)")
    print(f"    Within 3dB     : "
          f"{above_m3}/{total} "
          f"({100*above_m3/total:.1f}%)")
    print(f"    Within 10dB    : "
          f"{above_m10}/{total} "
          f"({100*above_m10/total:.1f}%)")

    print()
    return {
        'file': filepath,
        'peak_gain': peak_gain,
        'bore_gain': bore_gain,
        'az_bw': az_bw,
        'el_bw': el_bw,
        'min_gain': min_gain,
        'avg_gain': avg_gain
    }


# ===================================================================
#  MEASUREMENT HELPERS
# ===================================================================

def measure_beamwidth(
    angles: list[float], gains: list[float], peak: float,
) -> int:
    """Measure 3 dB beamwidth from a 1-D gain cut.

    Walks outward from the peak in both directions until the
    gain drops 3 dB below *peak*.

    Args:
        angles: Angle values in degrees.
        gains: Corresponding gain values in dBi.
        peak: Reference peak gain in dBi.

    Returns:
        Estimated 3 dB beamwidth in integer degrees (0 if
        indeterminate).
    """
    threshold = peak - 3.0
    peak_idx = gains.index(max(gains))

    # Walk right from peak
    right = 0
    for i in range(peak_idx + 1, len(gains)):
        if gains[i] < threshold:
            right = abs(angles[i] - angles[peak_idx])
            break

    # Walk left from peak
    left = 0
    for i in range(peak_idx - 1, -1, -1):
        if gains[i] < threshold:
            left = abs(angles[peak_idx] - angles[i])
            break

    if left > 0 and right > 0:
        bw = round(left + right)
    elif left > 0:
        bw = round(left * 2)
    elif right > 0:
        bw = round(right * 2)
    else:
        return 0

    # Beamwidth can never exceed 360°; values above that indicate
    # an omnidirectional pattern where noise caused a false 3dB crossing.
    return 0 if bw > 360 else bw


def find_first_sidelobe(
    angles: list[float],
    gains: list[float],
    peak: float,
    bw: int,
) -> dict | None:
    """Find the first sidelobe outside the main beam.

    Args:
        angles: Angle values in degrees.
        gains: Corresponding gain values in dBi.
        peak: Peak gain in dBi.
        bw: Main-beam beamwidth in degrees.

    Returns:
        Dict with ``level``, ``angle``, ``relative`` keys,
        or ``None`` if no sidelobe is found.
    """
    if bw <= 0:
        return None
    peak_idx = gains.index(max(gains))
    half_bw_idx = max(1, bw // 2)
    search_start = peak_idx + half_bw_idx
    if search_start >= len(gains):
        return None

    best_val = -999
    best_idx = search_start
    in_rise = False
    for i in range(search_start, len(gains)):
        if gains[i] > best_val:
            best_val = gains[i]
            best_idx = i
            in_rise = True
        elif in_rise and gains[i] < best_val - 1.0:
            break

    if best_val > -999:
        return {
            'level': best_val,
            'angle': angles[best_idx],
            'relative': peak - best_val
        }
    return None


# ===================================================================
#  SYMMETRY CHECKS
# ===================================================================

def check_symmetry_az(
    az_angles: list[float],
    data: list[list[float]],
    el0_idx: int,
) -> float:
    """RMS asymmetry in azimuth at el=0.

    Compares gain at symmetric positive/negative azimuth angles.

    Args:
        az_angles: Azimuth grid values.
        data: 2-D gain array ``[el][az]``.
        el0_idx: Row index for el = 0.

    Returns:
        RMS difference in dB.
    """
    # Find the actual 0-degree index
    if 0.0 in az_angles:
        mid = az_angles.index(0.0)
    else:
        mid = len(az_angles) // 2
    diffs = []
    for i in range(1, min(mid + 1,
                          len(az_angles) - mid)):
        pos_idx = mid + i
        neg_idx = mid - i
        if pos_idx < len(az_angles) and neg_idx >= 0:
            diff = (data[el0_idx][pos_idx]
                    - data[el0_idx][neg_idx])
            diffs.append(diff ** 2)
    if diffs:
        return math.sqrt(sum(diffs) / len(diffs))
    return 0.0


def check_symmetry_el(
    el_angles: list[float],
    data: list[list[float]],
    az0_idx: int,
) -> float:
    """RMS asymmetry in elevation at az=0.

    Compares gain at symmetric positive/negative elevation angles.

    Args:
        el_angles: Elevation grid values.
        data: 2-D gain array ``[el][az]``.
        az0_idx: Column index for az = 0.

    Returns:
        RMS difference in dB.
    """
    # Find the actual 0-degree index
    if 0.0 in el_angles:
        mid = el_angles.index(0.0)
    else:
        mid = len(el_angles) // 2
    diffs = []
    for i in range(1, min(mid + 1,
                          len(el_angles) - mid)):
        pos_idx = mid + i
        neg_idx = mid - i
        if pos_idx < len(el_angles) and neg_idx >= 0:
            diff = (data[pos_idx][az0_idx]
                    - data[neg_idx][az0_idx])
            diffs.append(diff ** 2)
    if diffs:
        return math.sqrt(sum(diffs) / len(diffs))
    return 0.0


# ===================================================================
#  IN-MEMORY ANALYSIS (no file I/O)
# ===================================================================

def analyze_from_data(
    az: list[float],
    el: list[float],
    data: list[list[float]],
) -> dict:
    """Analyse raw pattern data without file I/O or printing.

    Accepts the same ``(az, el, data)`` triple returned by
    ``core.io.read_pattern_csv`` or produced by ``compute_pattern``.

    Returns:
        Dict with keys: ``peak_gain``, ``peak_az``, ``peak_el``,
        ``bore_gain``, ``az_bw``, ``el_bw``, ``min_gain``,
        ``avg_gain``, ``ftb``, ``first_sll``, ``az_asym``,
        ``el_asym``.
    """
    n_el = len(el)
    n_az = len(az)

    az0 = az.index(0.0) if 0.0 in az else n_az // 2
    el0 = el.index(0.0) if 0.0 in el else n_el // 2

    # Global stats
    all_vals = [v for row in data for v in row]
    peak_gain = max(all_vals)
    min_gain = min(all_vals)
    avg_gain = sum(all_vals) / len(all_vals)

    # Peak location
    peak_el_idx = 0
    peak_az_idx = 0
    for i, row in enumerate(data):
        for j, v in enumerate(row):
            if v == peak_gain:
                peak_el_idx = i
                peak_az_idx = j

    bore_gain = data[el0][az0]

    # Beamwidths
    az_cut = data[el0]
    az_bw = measure_beamwidth(az, az_cut, bore_gain)

    el_cut = [data[i][az0] for i in range(n_el)]
    el_bw = measure_beamwidth(el, el_cut, bore_gain)

    # Front-to-back
    ftb = None
    if 180.0 in az:
        az180 = az.index(180.0)
        back_gain = data[el0][az180]
        ftb = bore_gain - back_gain

    # First sidelobe
    first_sll = find_first_sidelobe(az, az_cut, bore_gain, az_bw)

    # Symmetry
    az_asym = check_symmetry_az(az, data, el0)
    el_asym = check_symmetry_el(el, data, az0)

    return {
        "peak_gain": peak_gain,
        "peak_az": az[peak_az_idx],
        "peak_el": el[peak_el_idx],
        "bore_gain": bore_gain,
        "az_bw": az_bw,
        "el_bw": el_bw,
        "min_gain": min_gain,
        "avg_gain": avg_gain,
        "ftb": ftb,
        "first_sll": first_sll,
        "az_asym": az_asym,
        "el_asym": el_asym,
    }


# ===================================================================
#  MULTI-FILE COMPARISON
# ===================================================================

def compare_patterns(
    results_list: list[dict],
    writer: "IO[str] | None" = None,
) -> None:
    """Print comparison table of multiple analyses.

    Args:
        results_list: List of dicts from :func:`analyze_single`.
        writer: File-like object to write to. Defaults to
                ``sys.stdout``.
    """
    import sys
    out = writer or sys.stdout

    if len(results_list) < 2:
        return

    # Sort by frequency extracted from filename (ascending),
    # falling back to filename for files without a parseable frequency.
    from core.io import extract_freq_from_filename
    results_list = sorted(
        results_list,
        key=lambda r: (
            extract_freq_from_filename(r['file']) or float('inf'),
            os.path.basename(r['file']).lower(),
        ),
    )

    out.write("\n  " + "=" * 60 + "\n")
    out.write("  PATTERN COMPARISON\n")
    out.write("  " + "=" * 60 + "\n")

    out.write(f"  {'File':<30} {'Peak':>7} {'Bore':>7} "
              f"{'AzBW':>6} {'ElBW':>6} {'Min':>7}\n")
    out.write(f"  {'':<30} {'(dBi)':>7} {'(dBi)':>7} "
              f"{'(deg)':>6} {'(deg)':>6} {'(dBi)':>7}\n")
    out.write("  " + "-" * 60 + "\n")

    for r in results_list:
        fname = os.path.basename(r['file'])[:28]
        out.write(f"  {fname:<30} {r['peak_gain']:>7.2f} "
                  f"{r['bore_gain']:>7.2f} "
                  f"{r['az_bw']:>6} {r['el_bw']:>6} "
                  f"{r['min_gain']:>7.2f}\n")
    out.write("\n")


def get_pattern_summary_table(results_list: list[dict]) -> str:
    """Format a summary table for the GUI preview.

    Args:
        results_list: List of analysis dicts, each must have 'freq'.

    Returns:
        Formatted table string.
    """
    if not results_list:
        return ""

    # Sort by frequency
    results_list = sorted(results_list, key=lambda x: x.get('freq', 0.0))

    lines = []
    lines.append(f"{'Freq':<8} {'Peak':>6} {'AzBW':>5} {'ElBW':>5} "
                 f"{'F/B':>5} {'SLL':>6} {'Min':>6} {'Dyn':>5}")
    lines.append(f"{'(MHz)':<8} {'(dBi)':>6} {'(deg)':>5} {'(deg)':>5} "
                 f"{'(dB)':>5} {'(dB)':>6} {'(dBi)':>6} {'(dB)':>5}")
    lines.append("-" * 60)

    for r in results_list:
        f = r.get('freq', 0.0)
        pk = r.get('peak_gain', 0.0)
        az = r.get('az_bw', 0)
        el = r.get('el_bw', 0)
        ftb = r.get('ftb')
        ftb_str = f"{ftb:.1f}" if ftb is not None else "-"
        
        sll = r.get('first_sll')
        sll_str = f"{-sll['relative']:.1f}" if sll else "-"
        
        mn = r.get('min_gain', 0.0)
        dyn = pk - mn

        lines.append(f"{f:<8.1f} {pk:>6.1f} {az:>5} {el:>5} "
                     f"{ftb_str:>5} {sll_str:>6} {mn:>6.1f} {dyn:>5.1f}")

    return "\n".join(lines)
