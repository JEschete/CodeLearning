"""
Analysis Page — Pattern analysis, comparison, and statistics.
"""

import json
import os
import threading
import tkinter.filedialog as fd

import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import (
    ScrollablePage, Card, SectionHeading, ActionButton,
    FilePicker, ResultBox, Tooltip, LabeledOption, LabeledEntry,
    LabeledSwitch,
)


class AnalysisPage(ScrollablePage):
    """Pattern analysis page for beamwidth, sidelobes, symmetry, and comparison."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._build()

    def _build(self) -> None:
        SectionHeading(self, text="Pattern Analysis").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self, text="Fit, analyse, and compare antenna pattern files.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # ── Parameter Fit (first — primary workflow) ──────────
        fit_card = Card(self, title="Parameter Fit")
        fit_card.pack(fill="x", padx=24, pady=8)

        fit_inner = ctk.CTkFrame(fit_card, fg_color="transparent")
        fit_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        ctk.CTkLabel(
            fit_inner,
            text=(
                "Load pre-existing antenna pattern files and derive the "
                "AntennaForge configuration parameters that best reproduce "
                "them.  The fitted config can be saved as JSON or sent "
                "directly to the Generate page."
            ),
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            wraplength=620,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.w_fit_type = LabeledOption(
            fit_inner, "Antenna Type",
            ["LPDA", "Omni", "Panel", "Horn", "Dish",
             "Monopole", "Array"],
            default="LPDA",
            command=self._on_fit_type_changed,
        )
        self.w_fit_type.pack(fill="x", pady=4)

        freq_row = ctk.CTkFrame(fit_inner, fg_color="transparent")
        freq_row.pack(fill="x", pady=4)

        self.w_fit_fmin = LabeledEntry(
            freq_row, "F Min (MHz)", "30.0")
        self.w_fit_fmin.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.w_fit_fmax = LabeledEntry(
            freq_row, "F Max (MHz)", "300.0")
        self.w_fit_fmax.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.w_fit_files = FilePicker(
            fit_inner, "Pattern Files", mode="files",
            filetypes=[("Pattern files", "*.csv *.dat *.tbl"),
                       ("ODESSA Table", "*.tbl"),
                       ("CSV/DAT files", "*.csv *.dat"),
                       ("All files", "*.*")])
        self.w_fit_files.pack(fill="x", pady=4)

        self.w_fit_dir = FilePicker(
            fit_inner, "Or Pattern Dir", mode="directory")
        self.w_fit_dir.pack(fill="x", pady=4)

        opt_row = ctk.CTkFrame(fit_inner, fg_color="transparent")
        opt_row.pack(fill="x", pady=4)

        self.w_fit_optimize = LabeledSwitch(
            opt_row, "Optimize (SciPy)", default=True)
        self.w_fit_optimize.pack(side="left")

        self.w_fit_nruns = LabeledEntry(
            opt_row, "Runs", "4", width=60)
        self.w_fit_nruns.pack(side="left", padx=(16, 0))

        self._runs_hint = ctk.CTkLabel(
            opt_row, text="",
            font=FONTS["small"], text_color=COLORS["text_secondary"],
        )
        self._runs_hint.pack(side="left", padx=(4, 0))

        self.w_fit_rms = LabeledEntry(
            opt_row, "Target RMS", "0.5", width=60)
        self.w_fit_rms.pack(side="left", padx=(16, 0))

        # Set initial hint for default type
        self._on_fit_type_changed("LPDA")

        fit_btn_row = ctk.CTkFrame(fit_inner, fg_color="transparent")
        fit_btn_row.pack(anchor="w", pady=(8, 4))

        self._btn_fit = ActionButton(
            fit_btn_row, text="Fit Parameters", width=180,
            command=self._on_fit,
        )
        self._btn_fit.pack(side="left")

        self._btn_stop_fit = ActionButton(
            fit_btn_row, text="Stop", width=80, style="secondary",
            command=self._on_stop_fit,
        )
        self._btn_stop_fit.pack(side="left", padx=(8, 0))
        self._btn_stop_fit.pack_forget()  # hidden initially

        self._fit_stop_event = None

        self.fit_result = ResultBox(self, height=340)
        self.fit_result.pack(fill="x", padx=24, pady=(0, 4))

        # Action buttons for fit results
        self._fit_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._fit_btn_frame.pack(fill="x", padx=24, pady=(0, 24))

        self._btn_save_fit = ActionButton(
            self._fit_btn_frame, text="Save Config JSON",
            width=160, style="secondary",
            command=self._on_save_fit_config,
        )
        self._btn_save_fit.pack(side="left", padx=(0, 8))
        self._btn_save_fit.configure(state="disabled")

        self._btn_send_gen = ActionButton(
            self._fit_btn_frame, text="Send to Generate",
            width=160,
            command=self._on_send_to_generate,
        )
        self._btn_send_gen.pack(side="left")
        self._btn_send_gen.configure(state="disabled")

        self._fit_config = None  # populated after a successful fit

        # ── Single file analysis ────────────────────────────────
        single = Card(self, title="Single Pattern Analysis")
        single.pack(fill="x", padx=24, pady=8)

        s_inner = ctk.CTkFrame(single, fg_color="transparent")
        s_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_single = FilePicker(s_inner, "Pattern CSV")
        self.w_single.pack(fill="x", pady=4)

        ActionButton(
            s_inner, text="Analyze", width=160,
            command=self._on_single,
        ).pack(anchor="w", pady=(8, 4))

        self.single_result = ResultBox(self, height=220)
        self.single_result.pack(fill="x", padx=24, pady=(0, 16))

        # ── Multi-file comparison ───────────────────────────────
        multi = Card(self, title="Compare Multiple Patterns")
        multi.pack(fill="x", padx=24, pady=8)

        m_inner = ctk.CTkFrame(multi, fg_color="transparent")
        m_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_multi = FilePicker(m_inner, "CSV Files", mode="files")
        self.w_multi.pack(fill="x", pady=4)

        self.w_dir = FilePicker(m_inner, "Or Pattern Dir", mode="directory")
        self.w_dir.pack(fill="x", pady=4)

        ActionButton(
            m_inner, text="Compare", width=160,
            command=self._on_compare,
        ).pack(anchor="w", pady=(8, 4))

        self.multi_result = ResultBox(self, height=280)
        self.multi_result.pack(fill="x", padx=24, pady=(0, 16))

        # ── Pattern Set Comparison ──────────────────────────────
        pcomp_card = Card(self, title="Pattern Set Comparison")
        pcomp_card.pack(fill="x", padx=24, pady=8)

        pc_inner = ctk.CTkFrame(pcomp_card, fg_color="transparent")
        pc_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        ctk.CTkLabel(
            pc_inner,
            text=(
                "Compare two sets of pattern files frequency-by-frequency.  "
                "Shows percentage difference in peak gain, boresight gain, "
                "beamwidths, and minimum gain — useful for validating a "
                "fitted pattern against measured data."
            ),
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            wraplength=620,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.w_pcomp_a = FilePicker(
            pc_inner, "Pattern Set A (files)",
            mode="files",
            filetypes=[("Pattern files", "*.csv *.dat *.tbl"),
                       ("All files", "*.*")])
        self.w_pcomp_a.pack(fill="x", pady=4)

        self.w_pcomp_a_dir = FilePicker(
            pc_inner, "Or Set A Dir", mode="directory")
        self.w_pcomp_a_dir.pack(fill="x", pady=4)

        self.w_pcomp_b = FilePicker(
            pc_inner, "Pattern Set B (files)",
            mode="files",
            filetypes=[("Pattern files", "*.csv *.dat *.tbl"),
                       ("All files", "*.*")])
        self.w_pcomp_b.pack(fill="x", pady=4)

        self.w_pcomp_b_dir = FilePicker(
            pc_inner, "Or Set B Dir", mode="directory")
        self.w_pcomp_b_dir.pack(fill="x", pady=4)

        ActionButton(
            pc_inner, text="Compare Sets", width=180,
            command=self._on_pattern_compare,
        ).pack(anchor="w", pady=(8, 4))

        self.pcomp_result = ResultBox(self, height=320)
        self.pcomp_result.pack(fill="x", padx=24, pady=(0, 16))

        # ── Batch Fitting ────────────────────────────────────────
        batch_card = Card(self, title="Batch Fitting")
        batch_card.pack(fill="x", padx=24, pady=8)

        b_inner = ctk.CTkFrame(batch_card, fg_color="transparent")
        b_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        ctk.CTkLabel(
            b_inner,
            text=(
                "Fit many pattern sets at once.  Select a parent folder whose "
                "subfolders each contain one pattern set (co-pol CSVs).  For each "
                "set the tool auto-detects type/frequency, fits parameters, "
                "generates patterns from the fitted config, compares them against "
                "the originals, and produces a detailed report."
            ),
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            wraplength=620,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.w_batch_parent = FilePicker(
            b_inner, "Parent Dir (subfolders = pattern sets)",
            mode="directory")
        self.w_batch_parent.pack(fill="x", pady=4)

        self.w_batch_output = FilePicker(
            b_inner, "Output Dir", mode="directory")
        self.w_batch_output.pack(fill="x", pady=4)

        batch_opt_row = ctk.CTkFrame(b_inner, fg_color="transparent")
        batch_opt_row.pack(fill="x", pady=4)

        self.w_batch_runs = LabeledEntry(
            batch_opt_row, "Runs per set (0=auto)", "0", width=80)
        self.w_batch_runs.pack(side="left", padx=(0, 16))

        self.w_batch_rms = LabeledEntry(
            batch_opt_row, "Target RMS (0=auto)", "0", width=80)
        self.w_batch_rms.pack(side="left")

        batch_btn_row = ctk.CTkFrame(b_inner, fg_color="transparent")
        batch_btn_row.pack(anchor="w", pady=(8, 4))

        self._btn_batch = ActionButton(
            batch_btn_row, text="Run Batch Fit", width=180,
            command=self._on_batch_fit,
        )
        self._btn_batch.pack(side="left")

        self._btn_batch_stop = ActionButton(
            batch_btn_row, text="Stop", width=80, style="secondary",
            command=self._on_stop_batch,
        )
        self._btn_batch_stop.pack(side="left", padx=(8, 0))
        self._btn_batch_stop.pack_forget()

        self._batch_stop_event = None

        self.batch_result = ResultBox(self, height=400)
        self.batch_result.pack(fill="x", padx=24, pady=(0, 16))

        # ── Sidelobe mask compliance ────────────────────────────
        mask_card = Card(self, title="Sidelobe Mask Compliance")
        mask_card.pack(fill="x", padx=24, pady=8)

        doc_frame = ctk.CTkFrame(mask_card, fg_color="transparent")
        doc_frame.pack(fill="x", padx=CARD_PAD, pady=(4, 0))

        ctk.CTkLabel(
            doc_frame,
            text=(
                "Sidelobe envelope masks define maximum-allowed gain as a "
                "function of off-axis angle.  The tool supports three standards:\n\n"
                "• ITU-R S.580-6  —  Reference radiation patterns for earth-station "
                "antennas (D/λ ≥ 100). Gain envelope:  G = 32 − 25 log₁₀(θ) for "
                "1° < θ < 48°, then −10 dBi.\n"
                "   Rec. ITU-R S.580-6 (2004)\n\n"
                "• ITU-R S.465-6  —  Reference radiation pattern for earth-station "
                "antennas (smaller D/λ ratios). Uses G = G₁ − 2 + 15 log₁₀(D/λ) "
                "formulas with angle break-points.\n"
                "   Rec. ITU-R S.465-6 (2010)\n\n"
                "• MIL-STD  —  Military standard sidelobe envelope for phased-array "
                "and reflector antennas.  Typically G = G₀ − 25 log₁₀(θ) in the "
                "near-sidelobe region tapering to a floor.\n"
                "   MIL-STD-188-164A / MIL-STD-188-164B"
            ),
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            wraplength=620,
            justify="left",
        ).pack(anchor="w", padx=0, pady=(0, 8))

        mk_inner = ctk.CTkFrame(mask_card, fg_color="transparent")
        mk_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_mask_file = FilePicker(mk_inner, "Pattern CSV")
        self.w_mask_file.pack(fill="x", pady=4)

        self.w_mask_type = LabeledOption(
            mk_inner, "Mask Standard",
            ["ITU-R S.580-6", "ITU-R S.465-6", "MIL-STD"],
            default="ITU-R S.580-6",
        )
        self.w_mask_type.pack(fill="x", pady=4)

        self.w_mask_plane = LabeledOption(
            mk_inner, "Test Plane", ["az", "el"], default="az")
        self.w_mask_plane.pack(fill="x", pady=4)

        self.w_mask_gain = LabeledEntry(
            mk_inner, "Peak Gain (dBi)", "35.0",
            tooltip="Used for S.580 and MIL-STD masks")
        self.w_mask_gain.pack(fill="x", pady=4)

        ActionButton(
            mk_inner, text="Test Compliance", width=200,
            command=self._on_mask_test,
        ).pack(anchor="w", pady=(8, 4))

        self.mask_result = ResultBox(self, height=200)
        self.mask_result.pack(fill="x", padx=24, pady=(0, 16))

        # ── Tooltips ───────────────────────────────────────────
        # Single pattern analysis
        Tooltip(self.w_single,
                "Select a single antenna pattern CSV file to analyse.\n"
                "The tool extracts boresight and peak gain, 3 dB beamwidth "
                "in both planes, sidelobe levels, symmetry, and coverage "
                "statistics.\n"
                "CSV format: rows = elevation, columns = azimuth, values in dBi.")

        # Multi-file comparison
        Tooltip(self.w_multi,
                "Select multiple CSV files to compare side-by-side.\n"
                "Useful for comparing patterns across frequency slices or "
                "different antenna configurations.\n"
                "The comparison shows gain variation, beamwidth spread, and "
                "per-file statistics in a tabular summary.")
        Tooltip(self.w_dir,
                "Select a folder containing pattern CSVs.\n"
                "All .csv files in the directory will be loaded for "
                "comparison — handy when you have a full generation run.\n"
                "Files are sorted by frequency extracted from the filename.")

        # Pattern set comparison
        Tooltip(self.w_pcomp_a,
                "Select pattern files for Set A (e.g. measured data).\n"
                "Files are matched to Set B by sorted order — ensure both "
                "sets have the same number of frequency slices.")
        Tooltip(self.w_pcomp_b,
                "Select pattern files for Set B (e.g. fitted/generated data).\n"
                "Percentage differences are computed as (B − A) / |A| × 100.")

        # Sidelobe mask compliance
        Tooltip(self.w_mask_file,
                "Pattern CSV to test against the selected sidelobe mask.\n"
                "The tool extracts the principal-plane cut and compares it "
                "point-by-point against the envelope limit.")
        Tooltip(self.w_mask_type,
                "Sidelobe envelope standard to test against:\n"
                "• ITU-R S.580-6 — for earth-station dishes with D/λ ≥ 100.\n"
                "  Envelope: 32 − 25 log₁₀(θ) dBi (1° < θ < 48°).\n"
                "• ITU-R S.465-6 — for smaller dishes (flexible D/λ).\n"
                "  Uses frequency-dependent angle breakpoints.\n"
                "• MIL-STD — military envelope for phased arrays and "
                "reflectors with a stepped floor.")
        Tooltip(self.w_mask_plane,
                "Principal plane to test:\n"
                "• az — tests the azimuth cut (elevation = 0°).\n"
                "• el — tests the elevation cut (azimuth = 0°).\n"
                "Choose the plane most relevant to your coordination "
                "or compliance requirement.")
        Tooltip(self.w_mask_gain,
                "Peak gain in dBi used by the mask formula.\n"
                "For S.580 and MIL-STD, the mask shape depends on the "
                "antenna's peak gain. Enter the same value as your "
                "antenna's rated peak gain for an accurate test.")

        # Batch fitting
        Tooltip(self.w_batch_parent,
                "Select a parent directory whose immediate subfolders each "
                "contain one pattern set (co-pol CSV/DAT files).  The subfolder "
                "name becomes the set name in the report.\n"
                "Auto-detection reads generation_config.json if present, "
                "otherwise parses filenames for type and frequency.")
        Tooltip(self.w_batch_output,
                "Output directory for batch results.  Each set gets a "
                "subfolder with fitted_config.json and generated patterns.  "
                "A batch_fit_report.txt summarizes all sets.")
        Tooltip(self.w_batch_runs,
                "Runs per set.  0 = auto (2× recommended for the "
                "detected antenna type).  Higher values explore more "
                "strategies but take longer.")
        Tooltip(self.w_batch_rms,
                "Target RMS error in dB.  0 = use per-type default "
                "(e.g. 0.5 dB for Monopole, 1.5 dB for LPDA).")

        # Parameter fit
        Tooltip(self.w_fit_files,
                "Select pattern files: CSV/DAT (one per frequency) or a "
                "single ODESSA .tbl file (contains all frequency slices).\n"
                "The fitter analyses each slice to extract gain, beamwidth, "
                "F/B ratio, and sidelobe levels, then maps them to "
                "AntennaForge config parameters.")
        Tooltip(self.w_fit_dir,
                "Select a folder of pattern CSVs instead of individual "
                "files.\nAll .csv / .dat files in the folder will be used. "
                "Frequency is extracted from filenames automatically.")
        Tooltip(self.w_fit_type,
                "Antenna type to fit against.  Choose the type that "
                "best describes your reference antenna (LPDA, Panel, "
                "Horn, Dish, etc.).  The fitter uses the selected type's "
                "radiation model during optimization.")
        Tooltip(self.w_fit_fmin,
                "Lower edge of the antenna's operating band in MHz.\n"
                "This sets f_min_mhz in the fitted config and anchors "
                "the frequency-dependent beamwidth scaling.")
        Tooltip(self.w_fit_fmax,
                "Upper edge of the antenna's operating band in MHz.\n"
                "This sets f_max_mhz in the fitted config.")
        Tooltip(self.w_fit_optimize,
                "When enabled (and SciPy is installed), the fitter refines "
                "the measurement-seeded parameters via numerical "
                "optimization to minimize the RMS pattern error.\n"
                "Disable for a fast measurement-only estimate.")
        Tooltip(self.w_fit_rms,
                "Target RMS error (in dB) to stop optimization early.\n"
                "If the fitter achieves this accuracy, it stops refining "
                "to save time. Default is 0.5 dB.")

    # ────────────────────────────────────────────────────────────
    def _on_single(self) -> None:
        path = self.w_single.get()
        if not path:
            self.single_result.set_text("Select a pattern CSV file first.")
            return

        self.app.status.busy("Analyzing…")

        def work():
            try:
                from analysis.analyzer import analyze_single
                r = analyze_single(path)

                lines = [
                    f"File:            {os.path.basename(path)}",
                    f"Peak Gain:       {r.get('peak_gain', 'N/A')} dBi",
                    f"Boresight Gain:  {r.get('bore_gain', 'N/A')} dBi",
                    f"Az Beamwidth:    {r.get('az_bw', 'N/A')}°",
                    f"El Beamwidth:    {r.get('el_bw', 'N/A')}°",
                    f"Min Gain:        {r.get('min_gain', 'N/A')} dBi",
                    f"Avg Gain:        {r.get('avg_gain', 'N/A')} dBi",
                ]
                text = "\n".join(lines)
                self.after(0, lambda: self.single_result.set_text(text))
                self.after(0, lambda: self.app.status.success("Analysis complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.single_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    def _on_compare(self) -> None:
        files = self.w_multi.get_files()
        d = self.w_dir.get()
        if not files and d:
            files = sorted([
                os.path.join(d, f) for f in os.listdir(d)
                if f.endswith((".csv", ".dat"))
            ])
        if not files:
            self.multi_result.set_text("Select CSV files or a directory.")
            return

        self.app.status.busy(f"Comparing {len(files)} files…")

        def work():
            try:
                from analysis.analyzer import analyze_single, compare_patterns
                import io as _io

                results = [analyze_single(f) for f in files]

                buf = _io.StringIO()
                compare_patterns(results, writer=buf)

                text = buf.getvalue()
                self.after(0, lambda: self.multi_result.set_text(text))
                self.after(0, lambda: self.app.status.success("Comparison complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.multi_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    def _on_pattern_compare(self) -> None:
        """Compare two pattern sets frequency-by-frequency."""
        files_a = self.w_pcomp_a.get_files()
        dir_a = self.w_pcomp_a_dir.get()
        if not files_a and dir_a:
            files_a = sorted([
                os.path.join(dir_a, f) for f in os.listdir(dir_a)
                if f.lower().endswith((".csv", ".dat"))
            ])

        files_b = self.w_pcomp_b.get_files()
        dir_b = self.w_pcomp_b_dir.get()
        if not files_b and dir_b:
            files_b = sorted([
                os.path.join(dir_b, f) for f in os.listdir(dir_b)
                if f.lower().endswith((".csv", ".dat"))
            ])

        if not files_a or not files_b:
            self.pcomp_result.set_text(
                "Select pattern files (or directories) for both Set A and Set B.")
            return

        if len(files_a) != len(files_b):
            self.pcomp_result.set_text(
                f"Set A has {len(files_a)} files, Set B has {len(files_b)} files.\n"
                "Both sets must have the same number of frequency slices.")
            return

        self.app.status.busy(f"Comparing {len(files_a)} pattern pairs…")

        def work():
            try:
                from analysis.analyzer import analyze_single

                results_a = [analyze_single(f) for f in files_a]
                results_b = [analyze_single(f) for f in files_b]

                def pct_diff(v1, v2):
                    if v1 == 0:
                        return 0.0 if v2 == 0 else float('inf')
                    return (v2 - v1) / abs(v1) * 100.0

                header = (
                    f"  {'File':<33} {'Peak%':>7} {'Bore%':>7} "
                    f"{'AzBW%':>7} {'ElBW%':>7} {'Min%':>7}"
                )
                sep = "  " + "-" * 72
                banner = " " + "=" * 72

                lines = [
                    banner,
                    "  PATTERN SET COMPARISON  ( (B − A) / |A| × 100 )",
                    banner, "", header, sep,
                ]

                for i, (ra, rb) in enumerate(zip(results_a, results_b)):
                    fname = os.path.basename(files_a[i])
                    pk = pct_diff(ra.get('peak_gain', 0), rb.get('peak_gain', 0))
                    br = pct_diff(ra.get('bore_gain', 0), rb.get('bore_gain', 0))
                    az = pct_diff(ra.get('az_bw', 0), rb.get('az_bw', 0))
                    el = pct_diff(ra.get('el_bw', 0), rb.get('el_bw', 0))
                    mn = pct_diff(ra.get('min_gain', 0), rb.get('min_gain', 0))
                    lines.append(
                        f"  {fname:<33} {pk:>7.2f} {br:>7.2f} "
                        f"{az:>7.2f} {el:>7.2f} {mn:>7.2f}"
                    )

                # Summary statistics
                if len(results_a) > 1:
                    all_pk = [pct_diff(ra.get('peak_gain', 0), rb.get('peak_gain', 0))
                              for ra, rb in zip(results_a, results_b)]
                    all_br = [pct_diff(ra.get('bore_gain', 0), rb.get('bore_gain', 0))
                              for ra, rb in zip(results_a, results_b)]
                    all_az = [pct_diff(ra.get('az_bw', 0), rb.get('az_bw', 0))
                              for ra, rb in zip(results_a, results_b)]
                    all_el = [pct_diff(ra.get('el_bw', 0), rb.get('el_bw', 0))
                              for ra, rb in zip(results_a, results_b)]

                    lines.append(sep)
                    lines.append(
                        f"  {'Avg |diff|':<33} "
                        f"{sum(abs(v) for v in all_pk)/len(all_pk):>7.2f} "
                        f"{sum(abs(v) for v in all_br)/len(all_br):>7.2f} "
                        f"{sum(abs(v) for v in all_az)/len(all_az):>7.2f} "
                        f"{sum(abs(v) for v in all_el)/len(all_el):>7.2f}"
                    )
                    lines.append(
                        f"  {'Max |diff|':<33} "
                        f"{max(abs(v) for v in all_pk):>7.2f} "
                        f"{max(abs(v) for v in all_br):>7.2f} "
                        f"{max(abs(v) for v in all_az):>7.2f} "
                        f"{max(abs(v) for v in all_el):>7.2f}"
                    )

                text = "\n".join(lines)
                self.after(0, lambda: self.pcomp_result.set_text(text))
                self.after(0, lambda: self.app.status.success(
                    "Pattern comparison complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.pcomp_result.set_text(
                    f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    # ── Batch fitting handlers ────────────────────────────

    def _on_batch_fit(self) -> None:
        """Run batch fitting over all subfolders."""
        parent = self.w_batch_parent.get()
        if not parent:
            self.batch_result.set_text("Select a parent directory first.")
            return

        output = self.w_batch_output.get()
        if not output:
            self.batch_result.set_text("Select an output directory first.")
            return

        try:
            n_runs = int(self.w_batch_runs.get())
        except ValueError:
            n_runs = 0

        try:
            target_rms = float(self.w_batch_rms.get())
        except ValueError:
            target_rms = 0.0

        self._batch_stop_event = threading.Event()
        self._btn_batch.configure(state="disabled")
        self._btn_batch_stop.pack(side="left", padx=(8, 0))
        self.batch_result.set_text("Starting batch fit...\n")
        self.app.status.busy("Batch fitting in progress…")

        def progress(msg):
            self.after(0, lambda m=msg: self.batch_result.append(m + "\n"))

        def work():
            try:
                from core.fitting import batch_fit
                result = batch_fit(
                    parent_dir=parent,
                    output_dir=output,
                    n_runs=n_runs,
                    target_rms=target_rms,
                    progress_cb=progress,
                    stop_event=self._batch_stop_event,
                )
                self.after(0, lambda: self._batch_finished(result))
            except Exception as exc:
                msg = str(exc)
                self.after(0, lambda: self.batch_result.append(
                    f"\nBatch fit error: {msg}\n"))
                self.after(0, lambda: self.app.status.error(msg))
                self.after(0, self._batch_reset_ui)

        threading.Thread(target=work, daemon=True).start()

    def _on_stop_batch(self) -> None:
        """Signal the batch fit to stop after the current set."""
        if self._batch_stop_event:
            self._batch_stop_event.set()
        self.batch_result.append("\nStop requested — finishing current set...\n")

    def _batch_finished(self, result: dict) -> None:
        """Handle batch fit completion."""
        self._batch_reset_ui()
        report = result.get('report', '')
        report_path = result.get('report_path', '')
        n_ok = sum(1 for r in result.get('results', [])
                   if r.get('status') == 'ok')
        self.batch_result.append(
            f"\n{'='*60}\n"
            f"Batch complete: {n_ok} set(s) fitted.\n"
            f"Report saved: {report_path}\n"
            f"{'='*60}\n"
        )
        self.app.status.success(
            f"Batch fit complete — {n_ok} set(s), report at {report_path}")

    def _batch_reset_ui(self) -> None:
        """Reset batch UI controls."""
        self._btn_batch.configure(state="normal")
        self._btn_batch_stop.pack_forget()
        self._batch_stop_event = None

    def _on_mask_test(self) -> None:
        path = self.w_mask_file.get()
        if not path:
            self.mask_result.set_text("Select a pattern CSV first.")
            return

        self.app.status.busy("Testing compliance…")

        def work():
            try:
                mask_type = self.w_mask_type.get()
                plane = self.w_mask_plane.get()
                gain = float(self.w_mask_gain.get())

                from core.sidelobe_masks import (
                    itu_r_s580, itu_r_s465, mil_std_envelope,
                    test_pattern_against_mask,
                )

                if mask_type == "ITU-R S.580-6":
                    mask_fn = itu_r_s580(gain)
                elif mask_type == "ITU-R S.465-6":
                    mask_fn = itu_r_s465(4.0)  # D/λ default
                else:
                    mask_fn = mil_std_envelope(gain)

                r = test_pattern_against_mask(path, mask_fn, plane)

                lines = [
                    f"Mask:        {r.get('mask', mask_type)}",
                    f"Plane:       {r.get('plane', plane)}",
                    f"Peak Gain:   {r.get('peak_gain', 'N/A')} dBi",
                    f"Result:      {'✓ PASS' if r.get('passed') else '✗ FAIL'}",
                    f"Violations:  {r.get('n_violations', 0)}",
                    f"Min Margin:  {r.get('min_margin_db', 'N/A')} dB",
                ]
                if r.get('violations'):
                    lines.append("\nViolation Details:")
                    for v in r['violations'][:20]:
                        lines.append(
                            f"  {v.get('angle', '?')}°: "
                            f"{v.get('gain', '?')} dBi vs "
                            f"{v.get('max_allowed', '?')} dBi limit "
                            f"(excess {v.get('excess', '?')} dB)"
                        )

                text = "\n".join(lines)
                self.after(0, lambda: self.mask_result.set_text(text))

                status = "PASS" if r.get('passed') else "FAIL"
                color = COLORS["success"] if r.get('passed') else COLORS["error"]
                self.after(0, lambda: self.app.status.set_message(
                    f"Mask test: {status}", color))

            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.mask_result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()

    # ────────────────────────────────────────────────────────────
    #  PARAMETER FIT
    # ────────────────────────────────────────────────────────────
    def _on_fit_type_changed(self, choice: str) -> None:
        """Update recommended runs and target RMS when antenna type changes."""
        from core.fitting import recommended_runs, type_target_rms
        n, reason = recommended_runs(choice)
        self.w_fit_nruns.set(str(n))
        self._runs_hint.configure(text=f"(rec: {n})")
        # Update target RMS to per-type default
        self.w_fit_rms.set(str(type_target_rms(choice)))
        # Update tooltip dynamically
        Tooltip(self.w_fit_nruns,
                f"{reason}\nSet to 0 for unlimited runs (use Stop button).")

    def _on_fit(self) -> None:
        from gui.widgets import safe_float

        files = self.w_fit_files.get_files()
        d = self.w_fit_dir.get()
        if not files and d:
            files = sorted([
                os.path.join(d, f) for f in os.listdir(d)
                if f.lower().endswith((".csv", ".dat", ".tbl"))
            ])
        if not files:
            self.fit_result.set_text(
                "Select pattern CSV files or a directory first.")
            return

        atype = self.w_fit_type.get()
        f_min = safe_float(self.w_fit_fmin.get())
        f_max = safe_float(self.w_fit_fmax.get())

        if f_min is None or f_max is None or f_min <= 0 or f_max <= f_min:
            self.fit_result.set_text(
                "Enter a valid frequency range (F Min < F Max, both > 0).")
            return

        optimize = self.w_fit_optimize.get()
        n_runs = max(0, int(safe_float(self.w_fit_nruns.get()) or 1))
        target_rms = safe_float(self.w_fit_rms.get())
        if target_rms is None or target_rms < 0:
            target_rms = 0.5

        self.app.status.busy("Fitting parameters...")
        label = "unlimited" if n_runs == 0 else str(n_runs)
        self.fit_result.set_text(
            f"Starting parameter fit ({label} runs)...\n")
        self._fit_config = None
        self._btn_save_fit.configure(state="disabled")
        self._btn_send_gen.configure(state="disabled")

        # Show stop button, disable fit button
        self._fit_stop_event = threading.Event()
        self._btn_fit.configure(state="disabled")
        self._btn_stop_fit.pack(side="left", padx=(8, 0))

        def progress(msg):
            self.after(0, lambda m=msg: self.fit_result.append(m + "\n"))

        stop_event = self._fit_stop_event

        def work():
            try:
                from core.fitting import fit_parameters_multirun

                result = fit_parameters_multirun(
                    files,
                    antenna_type=atype,
                    f_min_mhz=f_min,
                    f_max_mhz=f_max,
                    n_runs=n_runs,
                    optimize=optimize,
                    target_rms=target_rms,
                    progress_cb=progress,
                    stop_event=stop_event,
                )

                cfg = result['config']
                report = result['report']

                def on_done():
                    self._fit_config = cfg
                    self.fit_result.set_text(report)
                    self._btn_save_fit.configure(state="normal")
                    self._btn_send_gen.configure(state="normal")
                    self.app.status.success("Parameter fit complete")
                    self._fit_finished()

                self.after(0, on_done)

            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.fit_result.set_text(
                    f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))
                self.after(0, self._fit_finished)

        threading.Thread(target=work, daemon=True).start()

    def _on_stop_fit(self) -> None:
        """Signal the fitting thread to stop after the current run."""
        if self._fit_stop_event is not None:
            self._fit_stop_event.set()
            self._btn_stop_fit.configure(state="disabled", text="Stopping...")
            self.app.status.busy("Stopping after current run...")

    def _fit_finished(self) -> None:
        """Re-enable the Fit button and hide the Stop button."""
        self._btn_fit.configure(state="normal")
        self._btn_stop_fit.pack_forget()
        self._btn_stop_fit.configure(state="normal", text="Stop")
        self._fit_stop_event = None

    def _on_save_fit_config(self) -> None:
        if self._fit_config is None:
            return
        path = fd.asksaveasfilename(
            title="Save Fitted Configuration",
            filetypes=[("JSON", "*.json")],
            defaultextension=".json",
            initialfile="fitted_config.json",
        )
        if path:
            try:
                with open(path, "w") as f:
                    json.dump(self._fit_config, f, indent=2)
                self.app.status.success(
                    f"Config saved: {os.path.basename(path)}")
            except Exception as e:
                self.app.status.error(f"Save failed: {e}")

    def _on_send_to_generate(self) -> None:
        if self._fit_config is None:
            return
        # Navigate to the Generate page (creates it lazily if needed)
        self.app.show_page("generate")
        gen_page = self.app._pages.get("generate")
        if gen_page and hasattr(gen_page, '_apply_config'):
            gen_page._apply_config(self._fit_config)
            self.app.status.success(
                "Fitted config loaded on Generate page")
