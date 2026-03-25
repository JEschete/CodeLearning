"""
Operations Page — Pattern arithmetic, rotation, and interpolation.
"""

import os, threading
import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import (
    ScrollablePage, Card, SectionHeading, ActionButton,
    LabeledEntry, LabeledOption, LabeledSlider, LabeledSliderEntry, FilePicker, ResultBox,
    Tooltip, safe_float,
)


class OperationsPage(ScrollablePage):
    """Pattern arithmetic, rotation, and interpolation operations."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._build()

    def _build(self) -> None:
        SectionHeading(self, text="Pattern Operations").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self,
            text="Combine, transform, and resample antenna patterns.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # ════════════════════════════════════════════════════════
        #  ARITHMETIC
        # ════════════════════════════════════════════════════════
        arith = Card(self, title="Pattern Arithmetic")
        arith.pack(fill="x", padx=24, pady=8)

        a_inner = ctk.CTkFrame(arith, fg_color="transparent")
        a_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_arith_op = LabeledOption(
            a_inner, "Operation",
            ["Add (power)", "Subtract (dB)", "Multiply (dB+dB)",
             "Scale (dB offset)", "Max Envelope", "Average (power)"],
            default="Add (power)",
        )
        self.w_arith_op.pack(fill="x", pady=4)

        self.w_arith_a = FilePicker(a_inner, "Pattern A")
        self.w_arith_a.pack(fill="x", pady=4)

        self.w_arith_b = FilePicker(a_inner, "Pattern B (or multi)")
        self.w_arith_b.pack(fill="x", pady=4)

        self.w_arith_files = FilePicker(a_inner, "Multi Files (env/avg)",
                                        mode="files")
        self.w_arith_files.pack(fill="x", pady=4)

        self.w_scale_db = LabeledEntry(a_inner, "Scale Amount (dB)", "0.0",
                                       tooltip="Only for Scale operation")
        self.w_scale_db.pack(fill="x", pady=4)

        self.w_arith_out = FilePicker(a_inner, "Output CSV", save=True)
        self.w_arith_out.pack(fill="x", pady=4)

        ActionButton(
            a_inner, text="⚙  Run Arithmetic", width=200,
            command=self._on_arithmetic,
        ).pack(anchor="w", pady=(8, 4))

        self.arith_result = ResultBox(self, height=100)
        self.arith_result.pack(fill="x", padx=24, pady=(0, 16))

        # ════════════════════════════════════════════════════════
        #  ROTATION
        # ════════════════════════════════════════════════════════
        rot = Card(self, title="Pattern Rotation")
        rot.pack(fill="x", padx=24, pady=8)

        r_inner = ctk.CTkFrame(rot, fg_color="transparent")
        r_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_rot_in = FilePicker(r_inner, "Input CSV")
        self.w_rot_in.pack(fill="x", pady=4)

        self.w_rot_dir = FilePicker(r_inner, "Or Input Dir",
                                    mode="directory")
        self.w_rot_dir.pack(fill="x", pady=4)

        self.w_rot_az = LabeledSliderEntry(r_inner, "Yaw / Az Rotate (°)",
                                             -180, 180, default=0, step=1, fmt=".0f")
        self.w_rot_az.pack(fill="x", pady=4)

        self.w_rot_el = LabeledSliderEntry(r_inner, "Pitch / El Tilt (°)",
                                             -90, 90, default=0, step=1, fmt=".0f")
        self.w_rot_el.pack(fill="x", pady=4)

        self.w_rot_roll = LabeledSliderEntry(r_inner, "Roll (°)",
                                               -180, 180, default=0, step=1, fmt=".0f")
        self.w_rot_roll.pack(fill="x", pady=4)

        self.w_rot_out = FilePicker(r_inner, "Output CSV / Dir", save=True)
        self.w_rot_out.pack(fill="x", pady=4)

        ActionButton(
            r_inner, text="🔄  Rotate", width=160,
            command=self._on_rotate,
        ).pack(anchor="w", pady=(8, 4))

        self.rot_result = ResultBox(self, height=80)
        self.rot_result.pack(fill="x", padx=24, pady=(0, 16))

        # ════════════════════════════════════════════════════════
        #  INTERPOLATION
        # ════════════════════════════════════════════════════════
        interp = Card(self, title="Interpolation & Resampling")
        interp.pack(fill="x", padx=24, pady=8)

        i_inner = ctk.CTkFrame(interp, fg_color="transparent")
        i_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_interp_mode = LabeledOption(
            i_inner, "Mode",
            ["Freq Interpolate (2 files)", "Multi-Freq Interpolate",
             "Resample Grid"],
            default="Freq Interpolate (2 files)",
        )
        self.w_interp_mode.pack(fill="x", pady=4)

        self.w_interp_lo = FilePicker(i_inner, "Low-Freq CSV")
        self.w_interp_lo.pack(fill="x", pady=4)

        self.w_interp_hi = FilePicker(i_inner, "High-Freq CSV")
        self.w_interp_hi.pack(fill="x", pady=4)

        self.w_interp_freq = LabeledEntry(i_inner, "Target Freq (MHz)", "",
                                          tooltip="For 2-file interpolation")
        self.w_interp_freq.pack(fill="x", pady=4)

        self.w_interp_files = FilePicker(i_inner, "Multi Files",
                                         mode="files")
        self.w_interp_files.pack(fill="x", pady=4)

        self.w_resample_az = LabeledEntry(i_inner, "New Az Step (°)", "1.0",
                                          tooltip="For grid resample")
        self.w_resample_az.pack(fill="x", pady=4)

        self.w_resample_el = LabeledEntry(i_inner, "New El Step (°)", "1.0")
        self.w_resample_el.pack(fill="x", pady=4)

        ActionButton(
            i_inner, text="📐  Interpolate", width=180,
            command=self._on_interpolate,
        ).pack(anchor="w", pady=(8, 4))

        self.interp_result = ResultBox(self, height=80)
        self.interp_result.pack(fill="x", padx=24, pady=(0, 24))

        # ════════════════════════════════════════════════════════
        #  EXPORT / CONVERSION
        # ════════════════════════════════════════════════════════
        export = Card(self, title="Export / Conversion")
        export.pack(fill="x", padx=24, pady=8)

        e_inner = ctk.CTkFrame(export, fg_color="transparent")
        e_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_export_files = FilePicker(e_inner, "Input Files", mode="files")
        self.w_export_files.pack(fill="x", pady=4)

        self.w_export_out = FilePicker(e_inner, "Output .tbl", save=True,
                                       filetypes=[("ODESSA Table", "*.tbl")])
        self.w_export_out.pack(fill="x", pady=4)

        ActionButton(
            e_inner, text="Export to ODESSA .tbl", width=200,
            command=self._on_export,
        ).pack(anchor="w", pady=(8, 4))

        self.export_result = ResultBox(self, height=80)
        self.export_result.pack(fill="x", padx=24, pady=(0, 24))

        # ── Tooltips ───────────────────────────────────────────
        # Arithmetic
        Tooltip(self.w_arith_op,
                "Pattern combination operation:\n"
                "• Add (power) — convert dB→linear, sum, convert back.\n"
                "  Use for combining co-located antenna contributions.\n"
                "• Subtract (dB) — simple dB subtraction A − B.\n"
                "  Use for isolating pattern differences.\n"
                "• Multiply (dB+dB) — add dB values point-by-point.\n"
                "  Equivalent to multiplying power.\n"
                "• Scale (dB offset) — add a constant dB value to every point.\n"
                "  Use for gain adjustments or cable loss correction.\n"
                "• Max Envelope — take the per-point maximum across\n"
                "  multiple patterns (worst-case interference).\n"
                "• Average (power) — power-average across multiple patterns\n"
                "  (useful for composite coverage).")
        Tooltip(self.w_arith_a,
                "First input pattern CSV (required for all operations).\n"
                "For Scale, this is the only input file needed.")
        Tooltip(self.w_arith_b,
                "Second input pattern CSV.\n"
                "Required for Add, Subtract, and Multiply.\n"
                "Grid dimensions must match Pattern A.")
        Tooltip(self.w_arith_files,
                "Select multiple CSV files for Max Envelope or Average.\n"
                "All files must have the same az/el grid dimensions.\n"
                "If empty, falls back to using Pattern A + Pattern B.")
        Tooltip(self.w_scale_db,
                "Constant dB offset for the Scale operation.\n"
                "Positive values increase gain, negative decrease.\n"
                "Example: −2.5 to account for 2.5 dB of cable loss.")
        Tooltip(self.w_arith_out,
                "Output path for the resulting combined CSV.\n"
                "The file will have the same az/el grid as the inputs.")

        # Rotation
        Tooltip(self.w_rot_in,
                "Single pattern CSV to rotate.\n"
                "Either this or Input Dir must be specified.")
        Tooltip(self.w_rot_dir,
                "Rotate every CSV in this directory at once.\n"
                "Useful for rotating a full multi-frequency generation run.\n"
                "Output goes to the specified output directory.")
        Tooltip(self.w_rot_az,
                "Yaw rotation in degrees — shifts the pattern left/right.\n"
                "Positive = rotate beam clockwise when viewed from above.\n"
                "Example: +30° points the main beam to 30° azimuth.")
        Tooltip(self.w_rot_el,
                "Pitch tilt in degrees — tilts the beam up or down.\n"
                "Positive = tilt upward, negative = tilt downward.\n"
                "Common use: applying mechanical downtilt to a sector antenna.")
        Tooltip(self.w_rot_roll,
                "Roll rotation in degrees around the boresight axis.\n"
                "Rotates the polarization frame without changing "
                "the beam pointing direction.\n"
                "±45° converts between V/H and slant polarization.")
        Tooltip(self.w_rot_out,
                "Output file or directory for the rotated pattern(s).\n"
                "For single-file: specify a .csv path.\n"
                "For directory: specify an output folder name.\n"
                "Leave blank for auto-naming (_rotated suffix).")

        # Interpolation
        Tooltip(self.w_interp_mode,
                "Interpolation / resampling mode:\n"
                "• Freq Interpolate (2 files) — blend a low-freq and "
                "high-freq pattern to estimate a pattern at a target "
                "frequency between them.\n"
                "• Multi-Freq Interpolate — given many frequency files, "
                "produce patterns at arbitrary target frequencies using "
                "spline interpolation.\n"
                "• Resample Grid — change the angular step size of an "
                "existing pattern (e.g. 1° → 0.5°) via 2-D interpolation.")
        Tooltip(self.w_interp_lo,
                "Lower-frequency pattern CSV for 2-file interpolation.\n"
                "Also used as the input file for Resample Grid mode.")
        Tooltip(self.w_interp_hi,
                "Higher-frequency pattern CSV for 2-file interpolation.\n"
                "Not used in Resample Grid mode.")
        Tooltip(self.w_interp_freq,
                "Target frequency in MHz for 2-file interpolation.\n"
                "Must be between the two input file frequencies.\n"
                "For Multi-Freq mode: comma-separated list of target "
                "frequencies (e.g. '850, 900, 950').")
        Tooltip(self.w_interp_files,
                "Multiple CSV files at different frequencies.\n"
                "Used by Multi-Freq Interpolate mode.\n"
                "The tool sorts them by frequency and interpolates "
                "across the set.")
        Tooltip(self.w_resample_az,
                "New azimuth angular step in degrees for grid resample.\n"
                "Smaller step = finer resolution (more columns in output).\n"
                "Uses cubic spline interpolation between existing points.")
        Tooltip(self.w_resample_el,
                "New elevation angular step in degrees for grid resample.\n"
                "Smaller step = finer resolution (more rows in output).\n"
                "Use when the source pattern has coarser resolution "
                "than needed for your analysis.")
        
        # Export
        Tooltip(self.w_export_files,
                "Select multiple pattern CSV/DAT files (frequency slices).\n"
                "The tool will sort them by frequency and combine them\n"
                "into a single 3D lookup table.")

    # ────────────────────────────────────────────────────────────
    #  ARITHMETIC HANDLER
    # ────────────────────────────────────────────────────────────
    def _on_arithmetic(self) -> None:
        op = self.w_arith_op.get()
        fa = self.w_arith_a.get()
        fb = self.w_arith_b.get()
        out = self.w_arith_out.get()
        multi = self.w_arith_files.get_files()

        if not out:
            self.arith_result.set_text("Specify an output file path.")
            return

        self.app.status.busy(f"Running {op}…")

        def work():
            try:
                from core.pattern_ops import (
                    add_patterns, subtract_patterns, multiply_patterns,
                    scale_pattern, max_envelope, average_patterns,
                )

                if "Add" in op:
                    result = add_patterns(fa, fb, out)
                elif "Subtract" in op:
                    result = subtract_patterns(fa, fb, out)
                elif "Multiply" in op:
                    result = multiply_patterns(fa, fb, out)
                elif "Scale" in op:
                    db = float(self.w_scale_db.get())
                    result = scale_pattern(fa, db, out)
                elif "Envelope" in op:
                    flist = multi if multi else [fa, fb]
                    result = max_envelope(flist, out)
                elif "Average" in op:
                    flist = multi if multi else [fa, fb]
                    result = average_patterns(flist, out)
                else:
                    result = "Unknown operation"

                self.after(0, lambda: self.arith_result.set_text(
                    f"Done → {result}"))
                self.after(0, lambda: self.app.status.success("Arithmetic complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.arith_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    # ────────────────────────────────────────────────────────────
    #  EXPORT HANDLER
    # ────────────────────────────────────────────────────────────
    def _on_export(self) -> None:
        files = self.w_export_files.get_files()
        out = self.w_export_out.get()

        if not files:
            self.export_result.set_text("Select input files for export.")
            return
        if not out:
            self.export_result.set_text("Specify an output .tbl file.")
            return

        self.app.status.busy("Exporting...")

        def work():
            try:
                from core.io import export_odessa_tbl
                msg = export_odessa_tbl(files, out)
                self.after(0, lambda: self.export_result.set_text(msg))
                self.after(0, lambda: self.app.status.success("Export complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.export_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    # ────────────────────────────────────────────────────────────
    #  ROTATION HANDLER
    # ────────────────────────────────────────────────────────────
    def _on_rotate(self) -> None:
        inp = self.w_rot_in.get()
        indir = self.w_rot_dir.get()
        out = self.w_rot_out.get()
        az = safe_float(self.w_rot_az.get(), 0.0)
        el = safe_float(self.w_rot_el.get(), 0.0)
        roll = safe_float(self.w_rot_roll.get(), 0.0)

        if not inp and not indir:
            self.rot_result.set_text("Select an input file or directory.")
            return

        self.app.status.busy("Rotating…")

        def work():
            try:
                from core.rotation import rotate_pattern, rotate_directory

                if indir:
                    results = rotate_directory(
                        indir, out or None,
                        az_rotate=az, el_tilt=el, roll=roll)
                    text = f"Rotated {len(results)} files:\n" + "\n".join(results)
                else:
                    base, ext = os.path.splitext(inp)
                    result = rotate_pattern(
                        inp, out or f"{base}_rotated{ext}",
                        az_rotate=az, el_tilt=el, roll=roll)
                    text = f"Done → {result}"

                self.after(0, lambda: self.rot_result.set_text(text))
                self.after(0, lambda: self.app.status.success("Rotation complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.rot_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    # ────────────────────────────────────────────────────────────
    #  INTERPOLATION HANDLER
    # ────────────────────────────────────────────────────────────
    def _on_interpolate(self) -> None:
        mode = self.w_interp_mode.get()
        self.app.status.busy("Interpolating…")

        def work():
            try:
                from core.interpolation import (
                    interpolate_frequency, resample_pattern,
                    multi_freq_interpolation,
                )

                if "2 files" in mode:
                    lo = self.w_interp_lo.get()
                    hi = self.w_interp_hi.get()
                    freq = float(self.w_interp_freq.get())
                    result = interpolate_frequency(lo, hi, freq)
                    text = f"Interpolated at {freq} MHz → {result}"

                elif "Multi" in mode:
                    flist = self.w_interp_files.get_files()
                    freq_str = self.w_interp_freq.get()
                    targets = [float(x.strip()) for x in freq_str.split(",")]
                    results = multi_freq_interpolation(flist, targets)
                    text = f"Interpolated {len(results)} files:\n" + "\n".join(results)

                elif "Resample" in mode:
                    inp = self.w_interp_lo.get()
                    az_step = float(self.w_resample_az.get())
                    el_step = float(self.w_resample_el.get())
                    result = resample_pattern(inp, az_step, el_step)
                    text = f"Resampled → {result}"

                else:
                    text = "Unknown mode"

                self.after(0, lambda: self.interp_result.set_text(text))
                self.after(0, lambda: self.app.status.success("Interpolation complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.interp_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()
