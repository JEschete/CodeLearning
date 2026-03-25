"""
File I/O and directory utilities.

Leaf node — no internal imports.
"""

import csv
import math
import os
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
#  CSV I/O
# ═══════════════════════════════════════════════════════════════════

def write_pattern_file(
    filepath: str,
    az_angles: list[float],
    el_angles: list[float],
    pattern: list[list[float]],
) -> None:
    """Write a 2-D gain pattern to a file.

    Format: first row = ``['0', az0, az1, ...]``,
    subsequent rows = ``[el_i, g(el_i,az0), g(el_i,az1), ...]``.

    Args:
        filepath:   Destination file path.
        az_angles:  Azimuth values (degrees).
        el_angles:  Elevation values (degrees).
        pattern:    2-D list of gain values (dBi), indexed ``[el][az]``.
    """
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["0"] + [str(a) for a in az_angles]
        writer.writerow(header)
        for i, el in enumerate(el_angles):
            writer.writerow([str(el)] + pattern[i])


def read_pattern_file(
    filepath: str,
) -> tuple[list[float], list[float], list[list[float]]]:
    """Read a pattern file.

    Args:
        filepath:  Path to a file written by :func:`write_pattern_file`.

    Returns:
        ``(az_angles, el_angles, data_2d)`` where *data_2d* is a
        list-of-lists of float gain values indexed ``[el][az]``.

    Raises:
        ValueError: If *filepath* is a directory.
    """
    if os.path.isdir(filepath):
        raise ValueError(
            f"Expected a file but got a directory: "
            f"{filepath}\n  Please select a specific "
            f"file, not a folder."
        )
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    az_angles = [float(x) for x in rows[0][1:]]
    el_angles = []
    data = []
    for row in rows[1:]:
        el_angles.append(float(row[0]))
        data.append([float(x) for x in row[1:]])
    return az_angles, el_angles, data


# Backwards-compatible aliases (many modules import these names)
read_pattern_csv = read_pattern_file
write_pattern_csv = write_pattern_file


def extract_freq_from_filename(fname: str) -> float | None:
    """Extract frequency in MHz from a pattern filename.

    Expected naming convention: ``TYPE_FREQpDECMHz_copol.csv``
    (e.g. ``LPDA_165p00MHz_copol.csv`` → ``165.0``).

    Args:
        fname: Filename or full path.

    Returns:
        Frequency in MHz, or ``None`` if no match.
    """
    base = os.path.basename(fname)
    base = base.replace('_copol', '').replace('_xpol', '')
    base = base.replace('.csv', '').replace('.dat', '')
    parts = base.split('_')
    for i, p in enumerate(parts):
        if 'MHz' in p:
            num = p.replace('MHz', '').replace('p', '.')
            # Handle case where MHz is a separate token (e.g. 2550_MHz)
            if not num and i > 0:
                num = parts[i-1].replace('p', '.')
            try:
                return float(num)
            except ValueError:
                pass
    return None


# ═══════════════════════════════════════════════════════════════════
#  DIRECTORY UTILITIES
# ═══════════════════════════════════════════════════════════════════

def make_timestamped_dir(base_path: str) -> str:
    """Create a directory named ``<base_path>_YYYYMMDDHHmm``.

    Args:
        base_path: Base directory path (timestamp is appended).

    Returns:
        Full path to the created directory.
    """
    stamp = datetime.now().strftime("%Y%m%d%H%M")
    full_path = f"{base_path}_{stamp}"
    os.makedirs(full_path, exist_ok=True)
    return full_path


def make_graph_output_dir(source_path: str | None = None) -> str:
    """Create a timestamped ``graphs_YYYYMMDDHHmm`` folder.

    The folder is placed next to *source_path* if provided,
    otherwise in the current working directory.

    Args:
        source_path: Reference file or directory path (optional).

    Returns:
        Full path to the created graphs directory.
    """
    if source_path and os.path.isdir(source_path):
        base = os.path.join(source_path, "graphs")
    elif source_path:
        base = os.path.join(
            os.path.dirname(source_path) or ".", "graphs"
        )
    else:
        base = "./graphs"
    stamp = datetime.now().strftime("%Y%m%d%H%M")
    full_path = f"{base}_{stamp}"
    os.makedirs(full_path, exist_ok=True)
    return full_path


# ═══════════════════════════════════════════════════════════════════
#  ODESSA .tbl IMPORT
# ═══════════════════════════════════════════════════════════════════

def read_odessa_tbl(filepath: str) -> dict:
    """Read an ODESSA .tbl file and return all frequency slices.

    Returns:
        Dict with keys:

        - **az_deg** — list of azimuth angles in degrees.
        - **el_deg** — list of elevation angles in degrees.
        - **freqs_mhz** — list of frequencies in MHz.
        - **slices** — list of 2-D patterns ``[el][az]``, one per frequency.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Parse header — find dimension lines (first integer before "..")
    n_az = n_el = n_freq = 0
    header_end = 0
    dim_count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('..') or stripped == '':
            continue
        # Dimension line: "361\t.. Number of values ..."
        parts = stripped.split('\t')
        try:
            val = int(parts[0])
        except ValueError:
            break
        dim_count += 1
        if dim_count == 3:
            # skip "number of dependent" and "number of independent"
            pass
        if '- Az' in stripped or 'first independent' in stripped:
            n_az = val
        elif '- El' in stripped or 'second independent' in stripped:
            n_el = val
        elif '- Freq' in stripped or 'third independent' in stripped:
            n_freq = val
        header_end = i + 1

    if n_az == 0 or n_el == 0 or n_freq == 0:
        raise ValueError(
            f"Could not parse .tbl header: az={n_az}, el={n_el}, freq={n_freq}")

    # Collect all non-comment, non-blank data lines after the header
    data_lines = []
    for line in lines[header_end:]:
        stripped = line.strip()
        if stripped.startswith('..') or stripped == '':
            continue
        data_lines.append(stripped)

    # First data line: azimuth values (radians)
    az_rad = [float(v) for v in data_lines[0].split()]
    # Second data line: elevation values (radians)
    el_rad = [float(v) for v in data_lines[1].split()]
    # Third data line: frequency values (Hz)
    freq_hz = [float(v) for v in data_lines[2].split()]

    if len(az_rad) != n_az:
        raise ValueError(
            f".tbl az count mismatch: header says {n_az}, got {len(az_rad)}")
    if len(el_rad) != n_el:
        raise ValueError(
            f".tbl el count mismatch: header says {n_el}, got {len(el_rad)}")
    if len(freq_hz) != n_freq:
        raise ValueError(
            f".tbl freq count mismatch: header says {n_freq}, got {len(freq_hz)}")

    # Remaining data lines: one per azimuth, each containing n_el * n_freq values
    # Layout: for each el, for each freq → gain value
    az_blocks = data_lines[3:]
    if len(az_blocks) != n_az:
        raise ValueError(
            f".tbl data block count mismatch: expected {n_az}, got {len(az_blocks)}")

    # Parse all blocks into a 3-D array: [i_az][i_el * n_freq + i_freq]
    raw = []
    for block_line in az_blocks:
        vals = [float(v) for v in block_line.split()]
        if len(vals) != n_el * n_freq:
            raise ValueError(
                f".tbl data line has {len(vals)} values, "
                f"expected {n_el * n_freq}")
        raw.append(vals)

    # Convert to degrees
    az_deg = [math.degrees(a) for a in az_rad]
    el_deg = [math.degrees(e) for e in el_rad]
    freqs_mhz = [f / 1e6 for f in freq_hz]

    # Filter out mirrored elevation values (marked as -500 dB)
    # Find the valid elevation range
    valid_el_start = 0
    for i_el in range(n_el):
        # Check if this elevation row is all -500
        test_val = raw[0][i_el * n_freq]
        if test_val > -499:
            valid_el_start = i_el
            break

    if valid_el_start > 0:
        el_deg = el_deg[valid_el_start:]
        n_el_valid = len(el_deg)
    else:
        n_el_valid = n_el

    # Extract 2-D slices: slices[freq_idx] = pattern[el][az]
    slices = []
    for i_freq in range(n_freq):
        pattern = []
        for i_el_out, i_el in enumerate(
                range(valid_el_start, valid_el_start + n_el_valid)):
            row = []
            for i_az in range(n_az):
                row.append(raw[i_az][i_el * n_freq + i_freq])
            pattern.append(row)
        slices.append(pattern)

    return {
        'az_deg': az_deg,
        'el_deg': el_deg,
        'freqs_mhz': freqs_mhz,
        'slices': slices,
    }


# ═══════════════════════════════════════════════════════════════════
#  EXPORT UTILITIES
# ═══════════════════════════════════════════════════════════════════

def export_odessa_tbl(input_files: list[str], output_path: str) -> str:
    """Combine multiple pattern files into an ODESSA .tbl file.

    Handles frequency extraction, sorting, and elevation mirroring
    (0-90 -> -90-90) if required.

    Args:
        input_files: List of paths to .csv/.dat pattern files.
        output_path: Destination .tbl file path.

    Returns:
        Status message string.
    """
    if not input_files:
        raise ValueError("No input files provided.")

    # Ensure output filename has .tbl extension
    if not output_path.lower().endswith(".tbl"):
        output_path += ".tbl"

    # 1. Parse all files
    parsed_data = []
    for fp in input_files:
        try:
            az, el, data = read_pattern_file(fp)
            freq = extract_freq_from_filename(fp)
            # Default to 0.0 if no freq found, convert MHz to Hz
            freq_hz = (freq * 1e6) if freq is not None else 0.0
            parsed_data.append({
                'path': fp, 'freq': freq_hz, 'az': az, 'el': el, 'data': data
            })
        except Exception as e:
            raise ValueError(f"Error reading {os.path.basename(fp)}: {e}")

    # 2. Sort by frequency
    parsed_data.sort(key=lambda x: x['freq'])

    # 3. Validate consistency (grids must match first file)
    ref = parsed_data[0]
    ref_az, ref_el = ref['az'], ref['el']

    for p in parsed_data[1:]:
        if len(p['az']) != len(ref_az) or len(p['el']) != len(ref_el):
            raise ValueError(f"Grid mismatch in {os.path.basename(p['path'])}")

    # 4. Handle Elevation Mirroring (if data is 0..90, mirror to -90..90)
    # ODESSA expects full elevation coverage.
    final_el = list(ref_el)
    mirror_needed = (min(ref_el) >= 0)
    
    if mirror_needed:
        # Create negative angles (excluding 0 if present)
        neg_el = [-e for e in reversed(ref_el) if e > 1e-6]
        final_el = neg_el + final_el

    # 5. Write .tbl file
    with open(output_path, 'w') as f:
        # Header
        f.write(".. UNCLASSIFIED\n")
        f.write(f"1\t.. Number of dependent variables\n")
        f.write(f"3\t.. Number of independent variables\n")
        f.write(f"{len(ref_az)}\t.. Number of values for first independent variable - Az\n")
        f.write(f"{len(final_el)}\t.. Number of values for second independent variable - El\n")
        f.write(f"{len(parsed_data)}\t.. Number of values for third independent variable - Frequency\n")

        # Axis values (converted to radians)
        f.write("\n.. Values for azimuth (rad)\n")
        f.write(" ".join(f"{math.radians(a):.10f}" for a in ref_az))

        f.write("\n\n.. Values for elevation (rad)\n")
        f.write(" ".join(f"{math.radians(e):.10f}" for e in final_el))

        f.write("\n\n.. Values for frequency (Hz)\n")
        f.write(" ".join(f"{p['freq']:.10f}" for p in parsed_data))

        # Data Block: Az -> El -> Freq
        for i_az, az_val in enumerate(ref_az):
            f.write(f"\n\n.. Output for all elevations and frequencies at az = {math.radians(az_val):.10f}\n")
            for i_el, el_val in enumerate(final_el):
                # If point is mirrored (negative el) and we are mirroring, use -500.0 dB
                is_mirrored_point = mirror_needed and (el_val < -1e-6)
                
                # Map final_el index back to source data index
                # If mirroring, the source index for the positive part is (i_el - len(neg_el))
                if is_mirrored_point:
                    # Mirrored zone: -500.0 dB
                    for _ in parsed_data:
                        f.write("-500.0000000000 ")
                else:
                    # Real data zone
                    # If mirroring, shift index. If not, i_el is correct.
                    src_idx = i_el - len(neg_el) if mirror_needed else i_el
                    for p in parsed_data:
                        val = p['data'][src_idx][i_az]
                        f.write(f"{val:.10f} ")
                f.write("\n")

        f.write("\n.. UNCLASSIFIED\n")

    return f"Exported {len(input_files)} patterns to {os.path.basename(output_path)}"
