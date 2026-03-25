"""
Frequency sweep animation.

Generates an animated GIF from a directory of frequency-slice CSVs.
Each frame shows the heatmap pattern at a single frequency, with a
title indicating the current frequency.

Dependencies: matplotlib, numpy, Pillow.
"""

import logging
import os
import tempfile

logger = logging.getLogger(__name__)

from graphing import check_plot_deps
from core.io import read_pattern_csv, extract_freq_from_filename


def generate_sweep_animation(
    csv_files: list[str],
    output_path: str | None = None,
    plot_style: str = "heatmap",
    frame_duration_ms: int = 500,
    loop: int = 0,
) -> str:
    """Generate an animated GIF from frequency-slice CSVs.

    Each CSV is rendered as a single frame (heatmap or polar).
    Files are sorted by frequency extracted from the filename.

    Args:
        csv_files:         List of CSV file paths.
        output_path:       Output GIF path.  If ``None``, placed
                           next to the first CSV as ``freq_sweep.gif``.
        plot_style:        Frame style — ``"heatmap"`` or ``"polar"``.
        frame_duration_ms: Duration of each frame in milliseconds.
        loop:              Number of loops (0 = infinite).

    Returns:
        Absolute path to the saved GIF.

    Raises:
        ValueError: If no valid CSVs are found.
        ImportError: If Pillow is not installed.
    """
    if not check_plot_deps():
        raise ImportError("matplotlib and numpy are required")

    try:
        from PIL import Image
    except ImportError:
        raise ImportError(
            "Pillow is required for GIF generation.\n"
            "Install with: pip install Pillow"
        )

    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Sort files by frequency
    freq_file_pairs = []
    for fp in csv_files:
        freq = extract_freq_from_filename(fp)
        if freq is not None:
            freq_file_pairs.append((freq, fp))
        else:
            # Fall back to filename sort order
            freq_file_pairs.append((0.0, fp))

    freq_file_pairs.sort(key=lambda x: x[0])

    if not freq_file_pairs:
        raise ValueError("No valid CSV files found for animation")

    # Determine output path
    if output_path is None:
        base_dir = os.path.dirname(freq_file_pairs[0][1]) or "."
        sub = os.path.join(base_dir, "animations")
        os.makedirs(sub, exist_ok=True)
        output_path = os.path.join(sub, "freq_sweep.gif")

    # Pre-scan all files to find global colour-scale bounds
    global_vmax = -999.0
    global_vmin = 999.0
    for freq, fp in freq_file_pairs:
        try:
            az, el, data = read_pattern_csv(fp)
            arr = np.array(data)
            global_vmax = max(global_vmax, arr.max())
            global_vmin = min(global_vmin, arr.min())
        except Exception:
            pass

    floor = max(global_vmin, global_vmax - 60)

    # Render each frame to a temporary PNG, then assemble
    frames: list[Image.Image] = []
    tmp_dir = tempfile.mkdtemp(prefix="antenna_anim_")

    try:
        for i, (freq, fp) in enumerate(freq_file_pairs):
            try:
                az, el, data = read_pattern_csv(fp)
                arr = np.array(data)
            except Exception as e:
                logger.warning("Skipping %s: %s", fp, e)
                continue

            if plot_style == "polar":
                frame_img = _render_polar_frame(
                    az, el, arr, freq, floor, global_vmax, tmp_dir, i
                )
            else:
                frame_img = _render_heatmap_frame(
                    az, el, arr, freq, floor, global_vmax, tmp_dir, i
                )

            if frame_img is not None:
                frames.append(frame_img)

        if not frames:
            raise ValueError("No frames could be rendered")

        # Save animated GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=frame_duration_ms,
            loop=loop,
            optimize=True,
        )
        logger.info("Saved animation: %s (%d frames)", output_path, len(frames))

    finally:
        # Clean up temp PNGs
        for f in os.listdir(tmp_dir):
            try:
                os.remove(os.path.join(tmp_dir, f))
            except OSError:
                pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass

    return output_path


def _render_heatmap_frame(
    az: list[float],
    el: list[float],
    arr,
    freq: float,
    vmin: float,
    vmax: float,
    tmp_dir: str,
    index: int,
) -> "Image.Image | None":
    """Render a single heatmap frame to a PIL Image.

    Args:
        az:      Azimuth angles.
        el:      Elevation angles.
        arr:     2-D numpy array of gain values.
        freq:    Frequency in MHz for the title.
        vmin:    Colour scale minimum.
        vmax:    Colour scale maximum.
        tmp_dir: Temporary directory for intermediate PNG.
        index:   Frame index.

    Returns:
        PIL Image, or ``None`` on failure.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image

    try:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        AZ, EL = np.meshgrid(az, el)
        im = ax.pcolormesh(
            AZ, EL, arr,
            shading="gouraud", cmap="jet",
            vmin=vmin, vmax=vmax,
        )
        ax.set_xlim(az[0], az[-1])
        ax.set_ylim(el[-1], el[0])

        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Gain (dBi)", fontsize=11)

        ax.set_xlabel("Azimuth (deg)", fontsize=11)
        ax.set_ylabel("Elevation (deg)", fontsize=11)

        if freq > 0:
            ax.set_title(f"Radiation Pattern — {freq:.1f} MHz",
                         fontsize=13, fontweight="bold")
        else:
            ax.set_title("Radiation Pattern", fontsize=13)

        ax.axhline(y=0, color="white", linewidth=0.5, alpha=0.5)
        ax.axvline(x=0, color="white", linewidth=0.5, alpha=0.5)

        # Mark peak
        peak_val = arr.max()
        peak_idx = np.unravel_index(arr.argmax(), arr.shape)
        peak_az = az[peak_idx[1]]
        peak_el = el[peak_idx[0]]
        ax.plot(peak_az, peak_el, "w+",
                markersize=12, markeredgewidth=2)
        ax.annotate(
            f"{peak_val:.1f} dBi",
            xy=(peak_az, peak_el),
            xytext=(peak_az + 15, peak_el + 15),
            color="white", fontsize=9,
            arrowprops=dict(arrowstyle="->", color="white"),
        )

        plt.tight_layout()
        tmp_png = os.path.join(tmp_dir, f"frame_{index:04d}.png")
        plt.savefig(tmp_png, dpi=100, bbox_inches="tight")
        plt.close(fig)

        img = Image.open(tmp_png).convert("RGBA")
        # Convert to palette mode for smaller GIFs
        img = img.convert("RGB").convert("P",
                                         palette=Image.ADAPTIVE,
                                         colors=256)
        return img

    except Exception as e:
        logger.warning("Frame %d render failed: %s", index, e)
        plt.close("all")
        return None


def _render_polar_frame(
    az: list[float],
    el: list[float],
    arr,
    freq: float,
    vmin: float,
    vmax: float,
    tmp_dir: str,
    index: int,
) -> "Image.Image | None":
    """Render a single polar-cut frame to a PIL Image.

    Shows azimuth and elevation cuts side by side.

    Args:
        az:      Azimuth angles.
        el:      Elevation angles.
        arr:     2-D numpy array of gain values.
        freq:    Frequency in MHz for the title.
        vmin:    Colour scale minimum (used as floor).
        vmax:    Colour scale maximum (peak).
        tmp_dir: Temporary directory for intermediate PNG.
        index:   Frame index.

    Returns:
        PIL Image, or ``None`` on failure.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image

    try:
        az0 = len(az) // 2
        el0 = len(el) // 2
        az_cut = arr[el0, :]
        el_cut = arr[:, az0]

        fig, axes = plt.subplots(
            1, 2, figsize=(12, 5),
            subplot_kw={"projection": "polar"},
        )

        az_rad = np.radians(az)
        el_rad = np.radians(el)

        peak = max(az_cut.max(), el_cut.max())
        floor = peak - 40

        az_norm = np.clip(az_cut, floor, peak)
        az_norm = (az_norm - floor) / (peak - floor)
        el_norm = np.clip(el_cut, floor, peak)
        el_norm = (el_norm - floor) / (peak - floor)

        axes[0].plot(az_rad, az_norm, "b-", linewidth=1.5)
        axes[0].set_theta_zero_location("N")
        axes[0].set_theta_direction(-1)

        axes[1].plot(el_rad, el_norm, "r-", linewidth=1.5)
        axes[1].set_theta_zero_location("N")
        axes[1].set_theta_direction(-1)

        if freq > 0:
            fig.suptitle(f"Polar Cuts — {freq:.1f} MHz",
                         fontsize=13, fontweight="bold", y=1.02)
            axes[0].set_title("Az Cut (el=0)", pad=15, fontsize=10)
            axes[1].set_title("El Cut (az=0)", pad=15, fontsize=10)
        else:
            axes[0].set_title("Az Cut (el=0)", pad=15, fontsize=10)
            axes[1].set_title("El Cut (az=0)", pad=15, fontsize=10)

        plt.tight_layout()
        tmp_png = os.path.join(tmp_dir, f"frame_{index:04d}.png")
        plt.savefig(tmp_png, dpi=100, bbox_inches="tight")
        plt.close(fig)

        img = Image.open(tmp_png).convert("RGBA")
        img = img.convert("RGB").convert("P",
                                         palette=Image.ADAPTIVE,
                                         colors=256)
        return img

    except Exception as e:
        logger.warning("Frame %d polar render failed: %s", index, e)
        plt.close("all")
        return None
