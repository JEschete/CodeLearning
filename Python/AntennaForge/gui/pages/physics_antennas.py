"""
Physics Antennas Page — Geometry-driven LPDA design.

Split-pane layout: parameter cards on the left, live visualisation
(geometry diagram, heatmap, polar, az/el cuts) on the right.

Uses Carrel's equations (core.lpda_geometry) to compute element
layout from tau/sigma, then bridges to the existing pattern engine
for radiation-pattern visualisation.
"""

import copy
import math
import os
import threading
import tkinter as tk
import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import (
    Card, SectionHeading, ActionButton,
    LabeledEntry, LabeledOption, LabeledSliderEntry,
    FilePicker, ResultBox, Tooltip, safe_float, safe_int,
)


class PhysicsAntennasPage(ctk.CTkFrame):
    """LPDA geometry design page with live preview."""

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=COLORS["bg"])
        self.app = app

        # Preview state
        self._preview_after_id = None
        self._preview_running = False
        self._freq_updating = False  # guard slider ↔ entry sync

        # Cached geometry
        self._geometry = None

        # ── Split layout: left params | right preview (resizable) ──
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        _mode = ctk.get_appearance_mode().lower()
        _idx = 1 if _mode == "dark" else 0
        _bg = COLORS["bg"][_idx]

        self._paned = tk.PanedWindow(
            self, orient=tk.HORIZONTAL,
            sashwidth=6, sashrelief=tk.FLAT,
            bg=_bg, sashcursor="sb_h_double_arrow",
            opaqueresize=True,
        )
        self._paned.grid(row=0, column=0, sticky="nsew")

        _left_wrapper = tk.Frame(self._paned, bg=_bg)
        self._paned.add(_left_wrapper, stretch="always", minsize=200)
        self._left_panel = ctk.CTkScrollableFrame(
            _left_wrapper,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["surface"],
            scrollbar_button_hover_color=COLORS["surface_hover"],
        )
        self._left_panel.pack(fill="both", expand=True)

        _right_wrapper = tk.Frame(self._paned, bg=_bg)
        self._paned.add(_right_wrapper, stretch="always", minsize=300)
        self._right_panel = ctk.CTkFrame(_right_wrapper, fg_color=COLORS["bg"])
        self._right_panel.pack(fill="both", expand=True)

        # Set initial sash position after layout (~40/60 split)
        def _init_sash():
            self.update_idletasks()
            w = self._paned.winfo_width()
            if w > 1:
                self._paned.sash_place(0, int(w * 0.4), 0)
        self.after(200, _init_sash)

        self._build_params()
        self._build_preview_panel()
        self._attach_preview_triggers()

        # Initial computation
        self.after(200, self._run_preview)

    # ────────────────────────────────────────────────────────────
    #  LEFT PANEL — PARAMETER CARDS
    # ────────────────────────────────────────────────────────────
    def _build_params(self) -> None:
        lp = self._left_panel

        # ── Page heading ──────────────────────────────────────
        SectionHeading(lp, text="Geometry Model").pack(
            fill="x", padx=CARD_PAD, pady=(CARD_PAD, 8))

        # ── Antenna type selector ─────────────────────────────
        type_card = Card(lp, title="Antenna Type")
        type_card.pack(fill="x", padx=8, pady=4)
        inner = ctk.CTkFrame(type_card, fg_color="transparent")
        inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_phy_type = LabeledOption(
            inner, "Type", ["LPDA"],
            default="LPDA",
        )
        self.w_phy_type.pack(fill="x", pady=2)

        # ── LPDA Design Parameters ────────────────────────────
        design_card = Card(lp, title="LPDA Design Parameters")
        design_card.pack(fill="x", padx=8, pady=4)
        di = ctk.CTkFrame(design_card, fg_color="transparent")
        di.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_tau = LabeledSliderEntry(
            di, "Tau (\u03c4)", from_=0.70, to=0.98,
            default=0.88, step=0.01, fmt=".2f",
            tooltip="Scale factor between successive elements",
        )
        self.w_tau.pack(fill="x", pady=4)

        self.w_sigma = LabeledSliderEntry(
            di, "Sigma (\u03c3)", from_=0.03, to=0.22,
            default=0.157, step=0.001, fmt=".3f",
            tooltip="Relative spacing factor",
        )
        self.w_sigma.pack(fill="x", pady=4)

        self.w_f_low = LabeledEntry(
            di, "F low (MHz)", "50",
            tooltip="Lowest design frequency",
        )
        self.w_f_low.pack(fill="x", pady=4)

        self.w_f_high = LabeledEntry(
            di, "F high (MHz)", "500",
            tooltip="Highest design frequency",
        )
        self.w_f_high.pack(fill="x", pady=4)

        self.w_z0 = LabeledEntry(
            di, "Feed Z\u2080 (\u03a9)", "50",
            tooltip="Feed impedance",
        )
        self.w_z0.pack(fill="x", pady=4)

        # ── Construction Parameters ───────────────────────────
        const_card = Card(lp, title="Construction")
        const_card.pack(fill="x", padx=8, pady=4)
        ci = ctk.CTkFrame(const_card, fg_color="transparent")
        ci.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_elem_dia = LabeledEntry(
            ci, "Element dia (mm)", "6.0",
            tooltip="Element tube/wire diameter",
        )
        self.w_elem_dia.pack(fill="x", pady=4)

        self.w_boom_dia = LabeledEntry(
            ci, "Boom dia (mm)", "25.0",
            tooltip="Boom tube diameter",
        )
        self.w_boom_dia.pack(fill="x", pady=4)

        # ── Computed Geometry ─────────────────────────────────
        geo_card = Card(lp, title="Computed Geometry")
        geo_card.pack(fill="x", padx=8, pady=4)

        self._geo_box = ResultBox(geo_card, height=220)
        self._geo_box.pack(fill="both", expand=True,
                           padx=CARD_PAD, pady=(4, CARD_PAD))

        # ── Import / Export geometry ──────────────────────────
        io_card = Card(lp, title="Geometry I/O")
        io_card.pack(fill="x", padx=8, pady=4)
        io_inner = ctk.CTkFrame(io_card, fg_color="transparent")
        io_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        io_btn_row = ctk.CTkFrame(io_inner, fg_color="transparent")
        io_btn_row.pack(fill="x", pady=2)

        ActionButton(
            io_btn_row, "Import Geometry CSV",
            command=self._import_geometry,
            style="secondary", width=170,
        ).pack(side="left", padx=(0, 8))

        ActionButton(
            io_btn_row, "Export Geometry CSV",
            command=self._export_geometry,
            style="secondary", width=170,
        ).pack(side="left")

        # ══════════════════════════════════════════════════════
        #  GENERATION SECTION — full pattern output like Generate page
        # ══════════════════════════════════════════════════════

        gen_heading = ctk.CTkLabel(
            lp, text="Pattern Generation",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        gen_heading.pack(fill="x", padx=CARD_PAD, pady=(16, 4))

        # ── Generation settings ───────────────────────────────
        gen_card = Card(lp, title="Generation Settings")
        gen_card.pack(fill="x", padx=8, pady=4)
        gi = ctk.CTkFrame(gen_card, fg_color="transparent")
        gi.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_n_slices = LabeledEntry(
            gi, "Frequency slices", "10",
            tooltip="Number of frequency points across the band",
        )
        self.w_n_slices.pack(fill="x", pady=4)

        self.w_freq_spacing = LabeledOption(
            gi, "Spacing", ["linear", "log"],
            default="linear",
        )
        self.w_freq_spacing.pack(fill="x", pady=4)

        self.w_az_step = LabeledOption(
            gi, "Az step (deg)", ["1", "2", "5"],
            default="1",
        )
        self.w_az_step.pack(fill="x", pady=4)

        self.w_el_step = LabeledOption(
            gi, "El step (deg)", ["1", "2", "5"],
            default="1",
        )
        self.w_el_step.pack(fill="x", pady=4)

        # ── Output settings ───────────────────────────────────
        out_card = Card(lp, title="Output")
        out_card.pack(fill="x", padx=8, pady=4)
        oi = ctk.CTkFrame(out_card, fg_color="transparent")
        oi.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_outdir = FilePicker(oi, "Output Directory",
                                   mode="directory")
        _project_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.w_outdir.set(os.path.join(
            os.path.dirname(_project_dir), "antenna_patterns"))
        self.w_outdir.pack(fill="x", pady=4)

        # Output format selection
        self._out_fmt_var = ctk.StringVar(value=".dat")
        fmt_frame = ctk.CTkFrame(oi, fg_color="transparent")
        fmt_frame.pack(fill="x", pady=4)

        ctk.CTkLabel(
            fmt_frame, text="Format:",
            font=FONTS["body_bold"],
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 10))

        for val in [".dat", ".csv"]:
            ctk.CTkRadioButton(
                fmt_frame, text=val,
                variable=self._out_fmt_var, value=val,
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"],
                border_color=COLORS["entry_border"],
                hover_color=COLORS["accent_light"],
            ).pack(side="left", padx=(0, 14))

        # ── Generate button ───────────────────────────────────
        gen_btn_row = ctk.CTkFrame(lp, fg_color="transparent")
        gen_btn_row.pack(fill="x", padx=8, pady=(8, 4))

        ActionButton(
            gen_btn_row, "Generate Patterns",
            command=self._on_generate,
            style="success", width=220,
        ).pack(side="left")

        # ── Generation result log ─────────────────────────────
        self._gen_result = ResultBox(lp, height=140)
        self._gen_result.pack(fill="x", padx=8, pady=(4, CARD_PAD))

    # ────────────────────────────────────────────────────────────
    #  RIGHT PANEL — TOOLBAR + CANVAS + ANALYSIS
    # ────────────────────────────────────────────────────────────
    def _build_preview_panel(self) -> None:
        self._right_panel.grid_rowconfigure(1, weight=3)
        self._right_panel.grid_rowconfigure(2, weight=1)
        self._right_panel.grid_columnconfigure(0, weight=1)

        # ── Row 0: Toolbar card ───────────────────────────────
        toolbar = Card(self._right_panel, title="Live Preview")
        toolbar.grid(row=0, column=0, sticky="ew",
                     padx=4, pady=(4, 2))

        tb_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        tb_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        # Row 0 of toolbar: plot type selector
        tb_row0 = ctk.CTkFrame(tb_inner, fg_color="transparent")
        tb_row0.pack(fill="x", pady=(0, 4))
        tb_row0.columnconfigure(0, weight=1)

        self.w_plot_type = LabeledOption(
            tb_row0, "Plot Type",
            ["Geometry", "Heatmap", "Cuts (Az+El)", "Polar"],
            default="Geometry",
        )
        self.w_plot_type.grid(row=0, column=0, sticky="ew")

        # Row 1 of toolbar: frequency slider + entry
        tb_row1 = ctk.CTkFrame(tb_inner, fg_color="transparent")
        tb_row1.pack(fill="x", pady=(0, 2))
        tb_row1.columnconfigure(1, weight=1)

        freq_label = ctk.CTkLabel(
            tb_row1, text="Frequency (MHz)",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            anchor="w", width=130,
        )
        freq_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        # Slider — range will be updated when f_low/f_high change
        self._freq_slider_var = ctk.DoubleVar(value=100.0)
        self._freq_slider = ctk.CTkSlider(
            tb_row1, from_=50.0, to=500.0,
            variable=self._freq_slider_var,
            fg_color=COLORS["entry_border"],
            progress_color=COLORS["accent"],
            button_color=COLORS["text_primary"],
            button_hover_color=COLORS["accent_light"],
            command=self._on_freq_slider_change,
        )
        self._freq_slider.grid(row=0, column=1, sticky="ew", padx=4)

        # Editable entry for direct decimal input
        self._freq_entry_var = ctk.StringVar(value="100.0")
        self._freq_entry = ctk.CTkEntry(
            tb_row1, textvariable=self._freq_entry_var, width=90,
            font=FONTS["mono"],
            fg_color=COLORS["entry_bg"],
            border_color=COLORS["entry_border"],
            text_color=COLORS["text_primary"],
            justify="center",
        )
        self._freq_entry.grid(row=0, column=2, padx=(8, 0))
        self._freq_entry.bind("<Return>", self._on_freq_entry_commit)
        self._freq_entry.bind("<FocusOut>", self._on_freq_entry_commit)

        # MHz suffix label
        ctk.CTkLabel(
            tb_row1, text="MHz", font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).grid(row=0, column=3, padx=(4, 0))

        # Row 2 of toolbar: heatmap colour-scale range
        tb_row2 = ctk.CTkFrame(tb_inner, fg_color="transparent")
        tb_row2.pack(fill="x", pady=(4, 0))
        tb_row2.columnconfigure(0, weight=1)
        tb_row2.columnconfigure(1, weight=1)

        self._hm_vmin = LabeledEntry(
            tb_row2, "Scale min (dBi)", "",
            tooltip="Leave blank for auto")
        self._hm_vmin.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._hm_vmax = LabeledEntry(
            tb_row2, "Scale max (dBi)", "",
            tooltip="Leave blank for auto")
        self._hm_vmax.grid(row=0, column=1, sticky="ew")

        # ── Row 1: Matplotlib canvas ──────────────────────────
        self._canvas_frame = ctk.CTkFrame(
            self._right_panel, fg_color=COLORS["card"],
            corner_radius=8)
        self._canvas_frame.grid(row=1, column=0, sticky="nsew",
                                padx=4, pady=2)

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        self._preview_fig = Figure(figsize=(7, 5), dpi=100,
                                   facecolor="#0F172A")
        self._preview_canvas = FigureCanvasTkAgg(
            self._preview_fig, master=self._canvas_frame)
        self._preview_canvas.get_tk_widget().pack(
            fill="both", expand=True)

        # Placeholder
        ax = self._preview_fig.add_subplot(111)
        ax.set_facecolor("#0F172A")
        ax.text(0.5, 0.5, "Adjust parameters to see live preview",
                ha="center", va="center", color="#64748B",
                fontsize=14, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self._preview_canvas.draw()

        # ── Row 2: Analysis results ───────────────────────────
        analysis_card = Card(self._right_panel,
                             title="Pattern Analysis")
        analysis_card.grid(row=2, column=0, sticky="nsew",
                           padx=4, pady=(2, 4))

        self._analysis_box = ResultBox(analysis_card, height=180)
        self._analysis_box.pack(fill="both", expand=True,
                                padx=CARD_PAD, pady=(4, CARD_PAD))

    # ────────────────────────────────────────────────────────────
    #  FREQUENCY SLIDER ↔ ENTRY SYNC
    # ────────────────────────────────────────────────────────────
    def _on_freq_slider_change(self, val) -> None:
        """Slider moved → update entry text."""
        if self._freq_updating:
            return
        self._freq_updating = True
        self._freq_entry_var.set(f"{float(val):.2f}")
        self._freq_updating = False

    def _on_freq_entry_commit(self, _event=None) -> None:
        """Entry committed → update slider position."""
        if self._freq_updating:
            return
        self._freq_updating = True
        try:
            v = float(self._freq_entry_var.get())
            f_lo = safe_float(self.w_f_low.get(), 50.0)
            f_hi = safe_float(self.w_f_high.get(), 500.0)
            v = max(f_lo, min(f_hi, v))
            self._freq_slider_var.set(v)
            self._freq_entry_var.set(f"{v:.2f}")
        except ValueError:
            self._freq_entry_var.set(
                f"{self._freq_slider_var.get():.2f}")
        self._freq_updating = False

    def _sync_freq_slider_range(self, *_args) -> None:
        """Update slider min/max when F low or F high changes."""
        f_lo = safe_float(self.w_f_low.get(), 50.0)
        f_hi = safe_float(self.w_f_high.get(), 500.0)
        if f_lo >= f_hi:
            return
        self._freq_slider.configure(from_=f_lo, to=f_hi)
        # Clamp current value into new range
        cur = self._freq_slider_var.get()
        clamped = max(f_lo, min(f_hi, cur))
        if clamped != cur:
            self._freq_slider_var.set(clamped)
            self._freq_entry_var.set(f"{clamped:.2f}")

    def _get_preview_freq(self) -> float:
        """Return the current preview frequency from the slider/entry."""
        return safe_float(
            self._freq_entry_var.get(),
            self._freq_slider_var.get())

    # ────────────────────────────────────────────────────────────
    #  AUTO-UPDATE SYSTEM (debounced, same pattern as GeneratePage)
    # ────────────────────────────────────────────────────────────
    def _schedule_preview(self, *_args) -> None:
        if self._preview_after_id is not None:
            self.after_cancel(self._preview_after_id)
        self._preview_after_id = self.after(500, self._run_preview)

    def _attach_preview_triggers(self) -> None:
        """Connect parameter widgets to debounced preview."""
        # DoubleVar (sliders)
        for w in [self.w_tau, self.w_sigma]:
            w._var.trace_add("write", self._schedule_preview)

        # Frequency slider
        self._freq_slider_var.trace_add("write", self._schedule_preview)

        # StringVar (entries + option menus)
        for w in [self.w_f_low, self.w_f_high, self.w_z0,
                  self.w_plot_type, self.w_phy_type,
                  self._hm_vmin, self._hm_vmax]:
            w._var.trace_add("write", self._schedule_preview)

        # Frequency entry (triggers on commit via Return/FocusOut,
        # but also track var for slider-driven changes)
        self._freq_entry_var.trace_add("write", self._schedule_preview)

        # Sync slider range when freq bounds change
        self.w_f_low._var.trace_add("write", self._sync_freq_slider_range)
        self.w_f_high._var.trace_add("write", self._sync_freq_slider_range)

    # ────────────────────────────────────────────────────────────
    #  LIVE PREVIEW COMPUTATION
    # ────────────────────────────────────────────────────────────
    def _run_preview(self) -> None:
        self._preview_after_id = None

        if self._preview_running:
            self._schedule_preview()
            return
        self._preview_running = True

        # Read params
        tau = safe_float(str(self.w_tau.get()), 0.88)
        sigma = safe_float(str(self.w_sigma.get()), 0.157)
        f_low = safe_float(self.w_f_low.get(), 50.0)
        f_high = safe_float(self.w_f_high.get(), 500.0)
        z0 = safe_float(self.w_z0.get(), 50.0)
        freq = self._get_preview_freq()
        plot_type = self.w_plot_type.get()

        def _compute():
            try:
                from core.lpda_geometry import (
                    compute_lpda_geometry, estimate_beamwidths,
                    estimate_ftb, geometry_summary_text,
                )

                # 1. Compute geometry
                geometry = compute_lpda_geometry(
                    tau, sigma, f_low, f_high, z0)
                self._geometry = geometry
                summary = geometry_summary_text(geometry)

                # 2. If plot type is Geometry, just render diagram
                if plot_type == "Geometry":
                    try:
                        self.after(0, lambda: self._update_geometry_plot(
                            geometry, summary))
                    except RuntimeError:
                        pass
                    return

                # 3. For pattern plots, build config and compute
                az_bw, el_bw = estimate_beamwidths(geometry, freq)
                ftb = estimate_ftb(tau)
                cfg = self._build_pattern_config(
                    geometry, freq, az_bw, el_bw, ftb)

                az_step = cfg["az_step_deg"]
                el_step = cfg["el_step_deg"]
                az_angles = [round(-180 + i * az_step, 4)
                             for i in range(int(360 / az_step) + 1)]
                el_angles = [round(-90 + i * el_step, 4)
                             for i in range(int(180 / el_step) + 1)]

                from core.engine import compute_pattern
                copol, _ = compute_pattern(
                    az_angles, el_angles, freq, cfg)

                try:
                    self.after(0, lambda: self._update_pattern_plot(
                        az_angles, el_angles, copol,
                        freq, plot_type, summary, geometry))
                except RuntimeError:
                    pass

            except Exception as e:
                msg = str(e)
                try:
                    self.after(0, lambda: self._preview_error(msg))
                except RuntimeError:
                    pass
            finally:
                self._preview_running = False

        threading.Thread(target=_compute, daemon=True).start()

    def _build_pattern_config(
        self, geometry: dict, freq: float,
        az_bw: float, el_bw: float, ftb: float,
    ) -> dict:
        """Build a config dict compatible with the pattern engine."""
        from config import DEFAULT_CONFIG
        cfg = copy.deepcopy(DEFAULT_CONFIG)

        cfg["antenna_type"] = "LPDA"
        cfg["max_gain_dbi"] = geometry["directivity_dbi_est"]
        cfg["az_beamwidth_deg"] = az_bw
        cfg["el_beamwidth_deg"] = el_bw
        cfg["ftb_ratio_db"] = ftb
        cfg["f_min_mhz"] = geometry["f_low_mhz"]
        cfg["f_max_mhz"] = geometry["f_high_mhz"]
        cfg["n_slices"] = 1
        cfg["az_step_deg"] = 2.0   # fast for preview
        cfg["el_step_deg"] = 2.0
        cfg["noise_range_db"] = 0.0
        cfg["sigmoid_k"] = 12.0

        # Enable sidelobes + VSWR for realism, disable slow features
        cfg["features"]["sidelobes"]["enabled"] = True
        cfg["features"]["pattern_breakup"]["enabled"] = False
        cfg["features"]["ground_reflection"]["enabled"] = False
        cfg["features"]["cross_pol"]["enabled"] = False
        cfg["features"]["vswr_rolloff"]["enabled"] = True
        cfg["features"]["asymmetry"]["enabled"] = False

        # Beamwidth decay (LPDA-characteristic)
        cfg["features"]["freq_dependent_bw_az"]["enabled"] = True
        cfg["features"]["freq_dependent_bw_el"]["enabled"] = True

        return cfg

    def _build_generation_config(self, geometry: dict) -> dict:
        """Build a full config dict for pattern file generation.

        Uses the user-specified az/el step, frequency slices,
        output dir, and format — same output as the Generate page.
        """
        from config import DEFAULT_CONFIG
        from core.lpda_geometry import estimate_beamwidths, estimate_ftb

        cfg = copy.deepcopy(DEFAULT_CONFIG)

        # Use mid-band freq for beamwidth estimate
        f_mid = (geometry["f_low_mhz"] + geometry["f_high_mhz"]) / 2.0
        az_bw, el_bw = estimate_beamwidths(geometry, f_mid)
        ftb = estimate_ftb(geometry["tau"])

        cfg["antenna_type"] = "LPDA"
        cfg["max_gain_dbi"] = geometry["directivity_dbi_est"]
        cfg["az_beamwidth_deg"] = az_bw
        cfg["el_beamwidth_deg"] = el_bw
        cfg["ftb_ratio_db"] = ftb
        cfg["f_min_mhz"] = geometry["f_low_mhz"]
        cfg["f_max_mhz"] = geometry["f_high_mhz"]
        cfg["n_slices"] = safe_int(self.w_n_slices.get(), 10)
        cfg["freq_spacing"] = self.w_freq_spacing.get()
        cfg["az_step_deg"] = safe_float(self.w_az_step.get(), 1.0)
        cfg["el_step_deg"] = safe_float(self.w_el_step.get(), 1.0)
        cfg["output_dir"] = self.w_outdir.get() or "./antenna_patterns"
        cfg["output_format"] = self._out_fmt_var.get()
        cfg["noise_range_db"] = 0.0
        cfg["sigmoid_k"] = 12.0

        # Physics features
        cfg["features"]["sidelobes"]["enabled"] = True
        cfg["features"]["pattern_breakup"]["enabled"] = True
        cfg["features"]["ground_reflection"]["enabled"] = False
        cfg["features"]["cross_pol"]["enabled"] = False
        cfg["features"]["vswr_rolloff"]["enabled"] = True
        cfg["features"]["asymmetry"]["enabled"] = False
        cfg["features"]["freq_dependent_bw_az"]["enabled"] = True
        cfg["features"]["freq_dependent_bw_el"]["enabled"] = True

        return cfg

    # ────────────────────────────────────────────────────────────
    #  PLOT UPDATES (main thread)
    # ────────────────────────────────────────────────────────────
    def _update_geometry_plot(self, geometry: dict, summary: str) -> None:
        from graphing.geometry_plots import live_lpda_geometry

        try:
            title = (f"LPDA  \u03c4={geometry['tau']:.3f}  "
                     f"\u03c3={geometry['sigma']:.3f}  "
                     f"N={geometry['n_elements']}")
            live_lpda_geometry(self._preview_fig, geometry, title=title)
            self._preview_canvas.draw_idle()
        except Exception:
            pass

        self._geo_box.set_text(summary)
        self._analysis_box.set_text(
            f"Geometry mode \u2014 switch plot type to see pattern analysis.\n\n"
            f"Boom length: {geometry['boom_length_m']:.3f} m\n"
            f"Elements: {geometry['n_elements']}\n"
            f"Est. directivity: {geometry['directivity_dbi_est']:.1f} dBi"
        )
        self._preview_running = False

    def _update_pattern_plot(
        self, az, el, data, freq, plot_type, summary, geometry,
    ) -> None:
        from graphing.live_plots import (
            live_heatmap, live_cuts, live_polar)

        title = (f"LPDA Physics @ {freq:.1f} MHz  "
                 f"\u03c4={geometry['tau']:.3f}")

        try:
            if plot_type == "Heatmap":
                hm_lo = self._hm_vmin.get().strip()
                hm_hi = self._hm_vmax.get().strip()
                vmin_o = float(hm_lo) if hm_lo else None
                vmax_o = float(hm_hi) if hm_hi else None
                live_heatmap(self._preview_fig, az, el, data,
                             title=title,
                             vmin_override=vmin_o,
                             vmax_override=vmax_o)
            elif plot_type == "Cuts (Az+El)":
                live_cuts(self._preview_fig, az, el, data,
                          title=title)
            elif plot_type == "Polar":
                live_polar(self._preview_fig, az, el, data,
                           title=title)
            self._preview_canvas.draw_idle()
        except Exception:
            pass

        # Update geometry box
        self._geo_box.set_text(summary)

        # Update analysis
        try:
            from analysis.analyzer import analyze_from_data
            m = analyze_from_data(az, el, data)
            lines = [
                f"Preview @ {freq:.1f} MHz",
                f"Peak Gain:    {m['peak_gain']:.2f} dBi  "
                f"(az={m.get('peak_az', 0):.0f}, "
                f"el={m.get('peak_el', 0):.0f})",
                f"Bore Gain:    {m['bore_gain']:.2f} dBi",
                f"Az Beamwidth: {m['az_bw']} deg",
                f"El Beamwidth: {m['el_bw']} deg",
            ]
            ftb = m.get("ftb")
            if ftb is not None:
                lines.append(f"Front/Back:   {ftb:.1f} dB")
            lines.append(f"Min Gain:     {m['min_gain']:.2f} dBi")
            self._analysis_box.set_text("\n".join(lines))
        except Exception:
            pass

    def _preview_error(self, msg: str) -> None:
        self._analysis_box.set_text(f"Preview error: {msg}")
        self._preview_running = False

    # ────────────────────────────────────────────────────────────
    #  IMPORT GEOMETRY CSV
    # ────────────────────────────────────────────────────────────
    def _import_geometry(self) -> None:
        """Import element geometry from a CSV file.

        Expected CSV format (header required):
            Element,Length_m,Position_m,Freq_MHz

        After import, tau/sigma/freq fields are updated to match
        the imported geometry, and the preview refreshes.
        """
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            title="Import LPDA Geometry CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            lengths = []
            positions = []
            freqs = []

            with open(path, "r", encoding="utf-8") as f:
                header = f.readline().strip()
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) < 4:
                        continue
                    lengths.append(float(parts[1]))
                    positions.append(float(parts[2]))
                    freqs.append(float(parts[3]))

            if len(lengths) < 3:
                self.app.status.error(
                    "Need at least 3 elements in CSV")
                return

            n = len(lengths)

            # Derive tau from successive element length ratios
            ratios = [lengths[i+1] / lengths[i]
                      for i in range(n - 1) if lengths[i] > 0]
            tau_est = sum(ratios) / len(ratios) if ratios else 0.88

            # Derive sigma from spacings and element lengths
            sigmas = []
            for i in range(n - 1):
                spacing = abs(positions[i+1] - positions[i])
                half_len = lengths[i+1] / 2.0
                if half_len > 0:
                    sigmas.append(spacing / (4.0 * half_len))
            sigma_est = sum(sigmas) / len(sigmas) if sigmas else 0.157

            # Derive frequency range from element resonant freqs
            f_low_est = min(freqs)
            f_high_est = max(freqs)

            # Clamp to valid ranges
            tau_est = max(0.70, min(0.98, tau_est))
            sigma_est = max(0.03, min(0.22, sigma_est))

            # Update GUI widgets
            self.w_tau.set(round(tau_est, 2))
            self.w_sigma.set(round(sigma_est, 3))
            self.w_f_low.set(f"{f_low_est:.1f}")
            self.w_f_high.set(f"{f_high_est:.1f}")

            self.app.status.success(
                f"Imported {n} elements from {os.path.basename(path)}"
                f" \u2014 \u03c4={tau_est:.3f} \u03c3={sigma_est:.3f}")

        except Exception as e:
            self.app.status.error(f"Import failed: {e}")

    # ────────────────────────────────────────────────────────────
    #  EXPORT GEOMETRY CSV
    # ────────────────────────────────────────────────────────────
    def _export_geometry(self) -> None:
        """Export element geometry table to CSV."""
        if self._geometry is None:
            self.app.status.error("No geometry computed yet")
            return

        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(
            title="Export LPDA Geometry",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        g = self._geometry
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Element,Length_m,Position_m,Freq_MHz\n")
                for i in range(g["n_elements"]):
                    f.write(
                        f"{i+1},{g['lengths_m'][i]:.6f},"
                        f"{g['positions_m'][i]:.6f},"
                        f"{g['element_freqs_mhz'][i]:.4f}\n"
                    )
            self.app.status.success(f"Exported to {path}")
        except Exception as e:
            self.app.status.error(f"Export failed: {e}")

    # ────────────────────────────────────────────────────────────
    #  FULL PATTERN GENERATION (same output as Generate page)
    # ────────────────────────────────────────────────────────────
    def _on_generate(self) -> None:
        """Generate pattern CSVs across frequency band in background."""
        if self._geometry is None:
            self.app.status.error("Compute geometry first")
            return

        self.app.status.busy("Generating patterns\u2026")
        self._gen_result.set_text("Building configuration\u2026\n")

        geometry = self._geometry

        def work():
            try:
                cfg = self._build_generation_config(geometry)

                from config import validate_config, generate_frequencies
                errors = validate_config(cfg)
                if errors:
                    msg = ("Validation errors:\n"
                           + "\n".join(f"  \u2022 {e}" for e in errors))
                    self.after(0, lambda: self._gen_result.set_text(msg))
                    self.after(0, lambda: self.app.status.error(
                        "Validation failed"))
                    return

                freqs = generate_frequencies(
                    cfg["f_min_mhz"], cfg["f_max_mhz"],
                    cfg["n_slices"], cfg["freq_spacing"],
                )

                self.after(0, lambda: self._gen_result.append(
                    f"Config OK \u2014 generating {len(freqs)} slices\u2026\n"
                    f"Output: {cfg['output_dir']}\n\n"
                ))

                from core.engine import run_generation
                import io as _io
                buf = _io.StringIO()
                run_generation(cfg, freqs, writer=buf)

                output = buf.getvalue()
                self.after(0, lambda: self._gen_result.append(output))
                self.after(0, lambda: self.app.status.success(
                    f"Done \u2014 {len(freqs)} pattern(s) generated"))

            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self._gen_result.set_text(
                    f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()
