"""
Pattern rotation and mechanical tilt.

Applies coordinate-frame rotations to an existing antenna
pattern CSV and re-grids onto the original (az, el) mesh.

Supported transforms
────────────────────
  az_rotate   Rotate pattern in azimuth (pan left/right).
              Positive = clockwise when viewed from above.
  el_tilt     Tilt boresight up (positive) or down (negative).
  roll        Roll about the boresight axis.

Each transform parameter is in **degrees**.

The algorithm:
  1.  For every (az_out, el_out) in the output grid, compute
      the direction as a Cartesian unit vector.
  2.  Apply the **inverse** rotation (negate angles) to find
      the source direction in the original pattern's frame.
  3.  Convert back to (az_src, el_src).
  4.  Bilinear-interpolate the original gain at that point.
      Azimuth wraps modularly; elevation clips at ±90.
"""

import logging
import math
import os

logger = logging.getLogger(__name__)

from core.io import (
    read_pattern_csv, write_pattern_csv,
)


# ===================================================================
#  ROTATION MATH  (pure Python + optional NumPy)
# ===================================================================

def _deg2rad(d: float) -> float:
    """Convert degrees to radians."""
    return d * math.pi / 180.0


def _rad2deg(r: float) -> float:
    """Convert radians to degrees."""
    return r * 180.0 / math.pi


def _rotation_matrix(
    az_deg: float, el_deg: float, roll_deg: float,
) -> list[list[float]]:
    """Build a 3x3 rotation matrix (passive / alias convention).

    Order of application: Roll -> Elevation tilt -> Azimuth.
    This matches the physical order for a pan-tilt-roll mount.

    Args:
        az_deg: Azimuth rotation in degrees.
        el_deg: Elevation tilt in degrees.
        roll_deg: Boresight roll in degrees.

    Returns:
        3x3 nested list representing the combined rotation matrix.
    """
    a = _deg2rad(az_deg)
    e = _deg2rad(el_deg)
    r = _deg2rad(roll_deg)

    # Rz(azimuth)
    ca, sa = math.cos(a), math.sin(a)
    Rz = [[ca, -sa, 0],
           [sa,  ca, 0],
           [0,   0,  1]]

    # Rx(elevation tilt)
    ce, se = math.cos(e), math.sin(e)
    Rx = [[1,  0,   0],
          [0,  ce, -se],
          [0,  se,  ce]]

    # Ry(roll)
    cr, sr = math.cos(r), math.sin(r)
    Ry = [[cr,  0, sr],
          [0,   1,  0],
          [-sr, 0, cr]]

    # Combined: Rz · Rx · Ry
    def matmul(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(3))
                 for j in range(3)] for i in range(3)]

    return matmul(Rz, matmul(Rx, Ry))


def _transpose(M: list[list[float]]) -> list[list[float]]:
    """Transpose a 3x3 matrix (= inverse for rotation matrices)."""
    return [[M[j][i] for j in range(3)] for i in range(3)]


def _apply_matrix(
    M: list[list[float]], x: float, y: float, z: float,
) -> tuple[float, float, float]:
    """Apply a 3x3 matrix to a vector ``(x, y, z)``."""
    return (M[0][0]*x + M[0][1]*y + M[0][2]*z,
            M[1][0]*x + M[1][1]*y + M[1][2]*z,
            M[2][0]*x + M[2][1]*y + M[2][2]*z)


def _azel_to_xyz(az_deg: float, el_deg: float) -> tuple[float, float, float]:
    """Convert (az, el) in degrees to a unit Cartesian vector.

    Convention:
      boresight = (0, 0) → y = +1
      az +90    → x = +1  (right)
      el +90    → z = +1  (up)
    """
    a = _deg2rad(az_deg)
    e = _deg2rad(el_deg)
    ce = math.cos(e)
    return (ce * math.sin(a),
            ce * math.cos(a),
            math.sin(e))


def _xyz_to_azel(
    x: float, y: float, z: float,
) -> tuple[float, float]:
    """Convert Cartesian (x, y, z) back to (az, el) in degrees."""
    r = math.sqrt(x*x + y*y + z*z)
    if r < 1e-15:
        return 0.0, 0.0
    el = _rad2deg(math.asin(max(-1, min(1, z / r))))
    az = _rad2deg(math.atan2(x, y))
    return az, el


# ===================================================================
#  BILINEAR INTERPOLATION ON (AZ, EL) GRID
# ===================================================================

def _bilinear_lookup(
    az_grid: list[float],
    el_grid: list[float],
    data: list[list[float]],
    az_query: float,
    el_query: float,
) -> float:
    """Bilinear interpolation lookup on an (az, el) gain grid.

    Azimuth wraps modularly within the grid range; elevation
    clips to the grid boundaries.

    Args:
        az_grid: Sorted azimuth grid values.
        el_grid: Sorted elevation grid values.
        data: 2-D gain array ``[el_idx][az_idx]``.
        az_query: Query azimuth in degrees.
        el_query: Query elevation in degrees.

    Returns:
        Interpolated gain value.
    """
    n_el = len(el_grid)
    n_az = len(az_grid)

    az_min, az_max = az_grid[0], az_grid[-1]
    el_min, el_max = el_grid[0], el_grid[-1]

    # Normalise azimuth into the grid range
    az_span = az_max - az_min
    if az_span > 0:
        aq = az_min + ((az_query - az_min) % (az_span))
    else:
        aq = az_min

    # Clip elevation
    eq = max(el_min, min(el_max, el_query))

    # Find bracketing indices — elevation
    ei = 0
    for k in range(n_el - 1):
        if el_grid[k + 1] >= eq:
            ei = k
            break
    else:
        ei = n_el - 2
    ei = max(0, min(n_el - 2, ei))
    e_frac = 0.0
    de = el_grid[ei + 1] - el_grid[ei]
    if abs(de) > 1e-12:
        e_frac = (eq - el_grid[ei]) / de
    e_frac = max(0.0, min(1.0, e_frac))

    # Find bracketing indices — azimuth
    ai = 0
    for k in range(n_az - 1):
        if az_grid[k + 1] >= aq:
            ai = k
            break
    else:
        ai = n_az - 2
    ai = max(0, min(n_az - 2, ai))
    a_frac = 0.0
    da = az_grid[ai + 1] - az_grid[ai]
    if abs(da) > 1e-12:
        a_frac = (aq - az_grid[ai]) / da
    a_frac = max(0.0, min(1.0, a_frac))

    # Bilinear
    g00 = data[ei][ai]
    g01 = data[ei][ai + 1]
    g10 = data[ei + 1][ai]
    g11 = data[ei + 1][ai + 1]

    g0 = g00 + a_frac * (g01 - g00)
    g1 = g10 + a_frac * (g11 - g10)
    return g0 + e_frac * (g1 - g0)


# ===================================================================
#  NUMPY-ACCELERATED PATH  (optional)
# ===================================================================

def _rotate_pattern_numpy(
    az_grid: list[float],
    el_grid: list[float],
    data: list[list[float]],
    inv_mat: list[list[float]],
) -> list[list[float]]:
    """Vectorised rotation + scipy RegularGridInterpolator.

    Applies the inverse rotation matrix to every output-grid
    point, then interpolates the source pattern at the
    resulting coordinates.

    Args:
        az_grid: Azimuth grid (degrees).
        el_grid: Elevation grid (degrees).
        data: Source gain array ``[el][az]``.
        inv_mat: 3x3 inverse rotation matrix.

    Returns:
        Rotated gain grid (nested list) ``[el][az]``.
    """
    import numpy as np
    try:
        from scipy.interpolate import RegularGridInterpolator
        has_scipy = True
    except ImportError:
        has_scipy = False

    arr = np.asarray(data, dtype=np.float64)
    n_el, n_az = arr.shape

    # Build output coordinate mesh
    AZ, EL = np.meshgrid(
        np.array(az_grid, dtype=np.float64),
        np.array(el_grid, dtype=np.float64),
    )
    az_rad = np.deg2rad(AZ)
    el_rad = np.deg2rad(EL)
    ce = np.cos(el_rad)
    x = ce * np.sin(az_rad)
    y = ce * np.cos(az_rad)
    z = np.sin(el_rad)

    # Apply inverse rotation
    M = np.array(inv_mat, dtype=np.float64)
    xs = M[0, 0]*x + M[0, 1]*y + M[0, 2]*z
    ys = M[1, 0]*x + M[1, 1]*y + M[1, 2]*z
    zs = M[2, 0]*x + M[2, 1]*y + M[2, 2]*z

    # Back to (az, el)
    r = np.sqrt(xs*xs + ys*ys + zs*zs)
    r = np.maximum(r, 1e-15)
    el_src = np.rad2deg(np.arcsin(np.clip(zs / r, -1, 1)))
    az_src = np.rad2deg(np.arctan2(xs, ys))

    # Wrap azimuth
    az_min, az_max = az_grid[0], az_grid[-1]
    az_span = az_max - az_min
    if az_span > 0:
        az_src = az_min + np.mod(az_src - az_min, az_span)

    # Clip elevation
    el_src = np.clip(el_src, el_grid[0], el_grid[-1])

    if has_scipy:
        interp = RegularGridInterpolator(
            (np.array(el_grid), np.array(az_grid)),
            arr,
            method='linear',
            bounds_error=False,
            fill_value=None,
        )
        pts = np.stack([el_src.ravel(), az_src.ravel()],
                       axis=-1)
        result = interp(pts).reshape(n_el, n_az)
    else:
        # Fallback: per-row vectorised search
        result = np.empty_like(arr)
        el_arr = np.array(el_grid)
        az_arr = np.array(az_grid)
        for i in range(n_el):
            for j in range(n_az):
                result[i, j] = _bilinear_lookup(
                    az_grid, el_grid, data,
                    float(az_src[i, j]),
                    float(el_src[i, j]),
                )

    return [[round(float(result[i][j]), 2)
             for j in range(n_az)]
            for i in range(n_el)]


# ===================================================================
#  PUBLIC API
# ===================================================================

def rotate_pattern(
    input_path: str,
    output_path: str,
    az_rotate: float = 0.0,
    el_tilt: float = 0.0,
    roll: float = 0.0,
) -> str | None:
    """Rotate/tilt an antenna pattern and write a new CSV.

    Args:
        input_path: Source pattern CSV path.
        output_path: Destination CSV path.
        az_rotate: Azimuth rotation in degrees (positive = CW).
        el_tilt: Elevation tilt in degrees (positive = up).
        roll: Boresight roll in degrees.

    Returns:
        *output_path* on success, ``None`` on failure.
    """
    if (abs(az_rotate) < 0.001
            and abs(el_tilt) < 0.001
            and abs(roll) < 0.001):
        # Identity transform — just copy
        import shutil
        shutil.copy2(input_path, output_path)
        logger.info("No rotation applied (copy): %s", output_path)
        return output_path

    az_grid, el_grid, data = read_pattern_csv(input_path)

    # Build forward rotation matrix and its inverse
    fwd = _rotation_matrix(az_rotate, el_tilt, roll)
    inv = _transpose(fwd)

    try:
        import numpy as np
        result = _rotate_pattern_numpy(
            az_grid, el_grid, data, inv
        )
        logger.debug("Using numpy path")
    except ImportError:
        # Pure-Python fallback
        n_el = len(el_grid)
        n_az = len(az_grid)
        result = []
        total = n_el * n_az
        done = 0
        for i, e in enumerate(el_grid):
            row = []
            for j, a in enumerate(az_grid):
                x, y, z = _azel_to_xyz(a, e)
                xs, ys, zs = _apply_matrix(inv, x, y, z)
                az_s, el_s = _xyz_to_azel(xs, ys, zs)
                g = _bilinear_lookup(
                    az_grid, el_grid, data, az_s, el_s
                )
                row.append(round(g, 2))
                done += 1
            result.append(row)
            if (i + 1) % 20 == 0 or i == n_el - 1:
                logger.debug("%d/%d points...", done, total)

    write_pattern_csv(output_path, az_grid, el_grid, result)
    parts = []
    if abs(az_rotate) >= 0.001:
        parts.append(f"az={az_rotate:+.1f}°")
    if abs(el_tilt) >= 0.001:
        parts.append(f"el={el_tilt:+.1f}°")
    if abs(roll) >= 0.001:
        parts.append(f"roll={roll:+.1f}°")
    logger.info("Rotated pattern (%s) -> %s",
                ', '.join(parts), output_path)
    return output_path


def rotate_directory(
    input_dir: str,
    output_dir: str | None = None,
    az_rotate: float = 0.0,
    el_tilt: float = 0.0,
    roll: float = 0.0,
) -> list[str]:
    """Apply the same rotation to every CSV in a directory.

    Args:
        input_dir: Directory containing pattern CSVs.
        output_dir: Destination directory (auto-generated if *None*).
        az_rotate: Azimuth rotation in degrees.
        el_tilt: Elevation tilt in degrees.
        roll: Boresight roll in degrees.

    Returns:
        List of output CSV paths.
    """
    import glob
    csv_files = sorted([
        *glob.glob(os.path.join(input_dir, "*.csv")),
        *glob.glob(os.path.join(input_dir, "*.dat"))
    ])
    if not csv_files:
        logger.info("No CSVs or DATs in %s", input_dir)
        return []

    if output_dir is None:
        tag = ""
        if abs(az_rotate) >= 0.001:
            tag += f"_az{az_rotate:+.0f}"
        if abs(el_tilt) >= 0.001:
            tag += f"_el{el_tilt:+.0f}"
        if abs(roll) >= 0.001:
            tag += f"_roll{roll:+.0f}"
        output_dir = input_dir.rstrip('/\\') + tag
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for fp in csv_files:
        name = os.path.basename(fp)
        out = os.path.join(output_dir, name)
        logger.info("[%d/%d] %s", len(results)+1, len(csv_files), name)
        rotate_pattern(fp, out, az_rotate, el_tilt, roll)
        results.append(out)

    logger.info("%d files rotated -> %s", len(results), output_dir)
    return results
