"""
Generate Page — Full antenna pattern generation wizard.

All configuration happens in-place with cards for each parameter group.
Parameter visibility changes dynamically based on the selected antenna type.
"""

import os, threading, copy, json
import tkinter as tk
import tkinter.filedialog as fd
import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import (
    Card, SectionHeading, ActionButton,
    LabeledEntry, LabeledOption, LabeledSwitch, LabeledSlider,
    LabeledSliderEntry, FilePicker, ResultBox, Tooltip,
    safe_float, safe_int,
)

# ── Per-type visibility rules ───────────────────────────────────
# Each key maps to the set of widget attribute names that should be
# VISIBLE for that antenna type.  Widgets not listed are hidden.
# "always" widgets (gain, freq card, angular card, output, etc.) are
# handled outside this map.

_TYPE_WIDGETS = {
    "LPDA":     {"w_ftb_affects_gain", "w_ftb", "w_az_bw", "w_el_bw",
                 "w_sidelobes", "sl_card",
                 "w_freq_bw_az", "w_freq_bw_el",
                 "w_breakup", "w_ground", "w_xpol", "w_vswr", "w_asym",
                 "w_sigmoid_k", "gbw_card"},
    "Omni":     {"w_el_bw",
                 "w_freq_bw_el",
                 "w_ground", "w_vswr"},
    "Panel":    {"w_ftb_affects_gain", "w_ftb", "w_az_bw", "w_el_bw",
                 "w_downtilt",
                 "w_sidelobes", "sl_card",
                 "w_freq_bw_az", "w_freq_bw_el",
                 "w_breakup", "w_ground", "w_xpol", "w_vswr", "w_asym",
                 "w_sigmoid_k", "gbw_card"},
    "Dish":     {"w_ftb_affects_gain", "w_ftb", "w_az_bw", "w_el_bw",
                 "w_downtilt", "w_dish_eff", "w_feed_taper",
                 "w_freq_bw_az", "w_freq_bw_el",
                 "w_breakup", "w_ground", "w_xpol", "w_vswr", "w_asym",
                 "w_sigmoid_k", "gbw_card"},
    "Horn":     {"w_ftb_affects_gain", "w_ftb", "w_az_bw", "w_el_bw",
                 "w_downtilt", "w_horn_aperture",
                 "w_sidelobes", "sl_card",
                 "w_freq_bw_az", "w_freq_bw_el",
                 "w_breakup", "w_ground", "w_xpol", "w_vswr", "w_asym",
                 "w_sigmoid_k", "gbw_card"},
    "Monopole": {"w_elem_len", "w_mono_phys_len",
                 "w_ground", "w_vswr"},
    "Array":    {"w_ftb_affects_gain", "w_ftb", "w_az_bw", "w_el_bw",
                 "w_downtilt", "arr_card",
                 "w_freq_bw_az", "w_freq_bw_el",
                 "w_breakup", "w_ground", "w_xpol", "w_vswr", "w_asym",
                 "w_sigmoid_k", "gbw_card"},
}

# Widgets whose visibility is toggled (must match attribute names).
# ORDERED LIST — pack order within each parent frame must match _build().
_TOGGLABLE = [
    # Core card inner widgets
    "w_ftb_affects_gain", "w_ftb", "w_downtilt", "w_dish_eff",
    "w_feed_taper", "w_horn_aperture",
    "w_elem_len", "w_mono_phys_len",
    # Beamwidth card inner widgets
    "w_az_bw", "w_el_bw",
    # Array card (top-level)
    "arr_card",
    # BW decay card inner widgets
    "w_freq_bw_az", "w_freq_bw_el",
    # GBW coupling card (top-level)
    "gbw_card",
    # Physics effects card inner widgets
    "w_sidelobes", "w_breakup", "w_ground", "w_xpol", "w_vswr", "w_asym",
    # Sidelobe params card (top-level)
    "sl_card",
    # New physics param cards
    "breakup_card", "ground_card", "xpol_card", "vswr_card", "asym_card",
    # Simulation settings card inner widgets
    "w_sigmoid_k",
]


class GeneratePage(ctk.CTkFrame):
    """Antenna pattern generation page with antenna-type-specific controls."""

    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=COLORS["bg"])
        self.app = app

        # Preview state
        self._preview_after_id = None
        self._preview_running = False

        # ── Split layout: controls | preview (resizable) ──────────
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

        # Set initial sash position after layout (~50/50 split)
        def _init_sash():
            self.update_idletasks()
            w = self._paned.winfo_width()
            if w > 1:
                self._paned.sash_place(0, int(w * 0.5), 0)
        self.after(200, _init_sash)

        # Build controls into left panel
        self._build()

        # Capture pack info from _build() so _apply_visibility can
        # re-pack widgets with consistent padding.
        self._widget_pack_info: dict[str, dict] = {}
        for attr_name in _TOGGLABLE:
            widget = getattr(self, attr_name, None)
            if widget is not None and widget.winfo_manager() == "pack":
                info = widget.pack_info()
                self._widget_pack_info[attr_name] = {
                    "fill": info.get("fill", ""),
                    "padx": info.get("padx", 0),
                    "pady": info.get("pady", 0),
                    "anchor": info.get("anchor", ""),
                }
        # Apply initial visibility for LPDA
        self._apply_visibility("LPDA")

        # Build right preview panel
        self._build_preview_panel()

        # Attach change listeners for live preview
        self._attach_preview_triggers()

        # Trigger initial preview after a short delay
        self.after(1000, self._run_preview)

    # ────────────────────────────────────────────────────────────
    def _build(self) -> None:
        SectionHeading(self._left_panel, text="Generate Antenna Patterns").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self._left_panel, text="Configure parameters and generate multi-frequency pattern CSV files.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # ══════════════════════════════════════════════════════════
        #  SECTION 1: Antenna Definition
        # ══════════════════════════════════════════════════════════

        # ── Core parameters card ────────────────────────────────
        core = Card(self._left_panel, title="Core Parameters")
        core.pack(fill="x", padx=24, pady=8)

        inner = ctk.CTkFrame(core, fg_color="transparent")
        inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        # Get available antenna types
        try:
            from antennas import available_names
            antenna_types = available_names()
        except Exception:
            antenna_types = ["LPDA", "Omni", "Panel", "Dish", "Horn",
                             "Monopole", "Array"]

        self.w_type = LabeledOption(inner, "Antenna Type", antenna_types,
                                    default="LPDA",
                                    command=self._on_type_change)
        self.w_type.pack(fill="x", pady=4)

        self.w_gain = LabeledEntry(inner, "Max Gain (dBi)", "7.0",
                                   tooltip="Peak boresight gain in dBi")
        self.w_gain.pack(fill="x", pady=4)

        self.w_ftb_affects_gain = LabeledSwitch(inner, "FTB Affects Gain", False)
        self.w_ftb_affects_gain.pack(fill="x", pady=4)
        Tooltip(self.w_ftb_affects_gain, "If enabled, low FTB reduces forward gain\n"
                                         "to conserve total radiated power.")

        self.w_ftb = LabeledEntry(inner, "Front-to-Back (dB)", "15.0",
                                  tooltip="Front-to-back ratio")
        self.w_ftb.pack(fill="x", pady=4)

        # ── Type-specific parameters (always in Core card) ──────
        self.w_downtilt = LabeledEntry(inner, "Mechanical Tilt (°)", "0.0",
                                       tooltip="Mechanical tilt angle in degrees.\n"
                                               "Positive = downtilt (below horizon).\n"
                                               "Applies to Panel, Dish, Horn, Array.")
        self.w_downtilt.pack(fill="x", pady=4)

        self.w_dish_eff = LabeledEntry(inner, "Aperture Efficiency", "0.60",
                                       tooltip="Dish aperture efficiency (0–1)")
        self.w_dish_eff.pack(fill="x", pady=4)

        self.w_feed_taper = LabeledEntry(inner, "Feed Edge Taper (dB)", "-12.0",
                                         tooltip="Feed illumination taper at dish edge.\n"
                                                 "More negative = lower sidelobes.\n"
                                                 "Typical: -10 to -15 dB. 0 = uniform.")
        self.w_feed_taper.pack(fill="x", pady=4)

        self.w_horn_aperture = LabeledEntry(inner, "Horn Aperture (λ)", "",
                                            tooltip="Horn aperture width in wavelengths at ref freq.\n"
                                                    "If set, beamwidth is derived from aperture.\n"
                                                    "Leave empty to use manual BW settings.")
        self.w_horn_aperture.pack(fill="x", pady=4)

        self.w_elem_len = LabeledEntry(inner, "Element Length (λ)", "0.25",
                                       tooltip="Monopole element length in wavelengths (0.25 = quarter-wave)")
        self.w_elem_len.pack(fill="x", pady=4)

        self.w_mono_phys_len = LabeledEntry(inner, "Physical Length (m)", "",
                                            tooltip="Monopole physical length in metres.\n"
                                                    "If set, element length in λ scales with\n"
                                                    "frequency: L(f) = phys / (c/f).\n"
                                                    "Leave empty to use fixed λ value.")
        self.w_mono_phys_len.pack(fill="x", pady=4)

        # ── Beamwidth card ──────────────────────────────────────
        self.bw_card = Card(self._left_panel, title="Beamwidth")
        self.bw_card.pack(fill="x", padx=24, pady=8)

        bw_inner = ctk.CTkFrame(self.bw_card, fg_color="transparent")
        bw_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_az_bw = LabeledSliderEntry(bw_inner, "Azimuth BW (°)",
                                          1, 360, default=65, step=1, fmt=".0f",
                                          tooltip="3 dB azimuth beamwidth in degrees")
        self.w_az_bw.pack(fill="x", pady=4)

        self.w_el_bw = LabeledSliderEntry(bw_inner, "Elevation BW (°)",
                                          1, 360, default=70, step=1, fmt=".0f",
                                          tooltip="3 dB elevation beamwidth in degrees")
        self.w_el_bw.pack(fill="x", pady=4)

        # ── Array parameters card ───────────────────────────────
        self.arr_card = Card(self._left_panel, title="Array Parameters")
        self.arr_card.pack(fill="x", padx=24, pady=8)

        arr_inner = ctk.CTkFrame(self.arr_card, fg_color="transparent")
        arr_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_arr_geom = LabeledOption(arr_inner, "Geometry",
                                        ["linear", "planar", "circular"],
                                        default="linear")
        self.w_arr_geom.pack(fill="x", pady=4)

        self.w_arr_nx = LabeledEntry(arr_inner, "Elements X", "8",
                                     tooltip="Number of elements along X axis")
        self.w_arr_nx.pack(fill="x", pady=4)

        self.w_arr_ny = LabeledEntry(arr_inner, "Elements Y", "1",
                                     tooltip="Number of elements along Y (planar only)")
        self.w_arr_ny.pack(fill="x", pady=4)

        self.w_arr_dx = LabeledEntry(arr_inner, "Spacing X (λ)", "0.5",
                                     tooltip="Element spacing along X in wavelengths")
        self.w_arr_dx.pack(fill="x", pady=4)

        self.w_arr_dy = LabeledEntry(arr_inner, "Spacing Y (λ)", "0.5",
                                     tooltip="Element spacing along Y in wavelengths")
        self.w_arr_dy.pack(fill="x", pady=4)

        self.w_arr_steer_az = LabeledEntry(arr_inner, "Steer Az (°)", "0.0",
                                           tooltip="Beam steering azimuth angle")
        self.w_arr_steer_az.pack(fill="x", pady=4)

        self.w_arr_steer_el = LabeledEntry(arr_inner, "Steer El (°)", "0.0",
                                           tooltip="Beam steering elevation angle")
        self.w_arr_steer_el.pack(fill="x", pady=4)

        self.w_arr_weight = LabeledOption(arr_inner, "Weighting",
                                          ["uniform", "taylor"],
                                          default="uniform")
        self.w_arr_weight.pack(fill="x", pady=4)

        self.w_arr_taper = LabeledEntry(arr_inner, "Taper SLL (dB)", "-25.0",
                                        tooltip="Taylor taper sidelobe level (dB)")
        self.w_arr_taper.pack(fill="x", pady=4)

        self.w_arr_coupling = LabeledSwitch(
            arr_inner, "Mutual Coupling", default=False)
        self.w_arr_coupling.pack(fill="x", pady=4)
        Tooltip(self.w_arr_coupling,
                "Enable impedance-matrix mutual coupling model.\n"
                "Perturbs element weights based on inter-element\n"
                "electromagnetic coupling. Improves realism for\n"
                "closely-spaced arrays (d ≤ λ/2).")

        self.w_arr_elem_pat = LabeledOption(
            arr_inner, "Element Pattern",
            ["gaussian", "cosine", "patch"],
            default="gaussian")
        self.w_arr_elem_pat.pack(fill="x", pady=4)
        Tooltip(self.w_arr_elem_pat,
                "Individual element radiation pattern model:\n"
                "• Gaussian — smooth Gaussian rolloff (default).\n"
                "• Cosine — cos^n pattern (typical dipole).\n"
                "• Patch — truncated cosine (microstrip element).")

        self.w_arr_rms_phase = LabeledEntry(
            arr_inner, "RMS Phase Error (°)", "0.0",
            tooltip="Per-element random phase error (degrees RMS).\n"
                    "Models manufacturing tolerances.\n"
                    "Typical: 5–15° for passive arrays.")
        self.w_arr_rms_phase.pack(fill="x", pady=4)

        self.w_arr_rms_amp = LabeledEntry(
            arr_inner, "RMS Amplitude Error (dB)", "0.0",
            tooltip="Per-element random amplitude error (dB RMS).\n"
                    "Models feed network imperfections.\n"
                    "Typical: 0.5–1.5 dB for passive arrays.")
        self.w_arr_rms_amp.pack(fill="x", pady=4)

        self.w_arr_circ_orient = LabeledOption(
            arr_inner, "Circular Orientation",
            ["parallel", "radial"],
            default="parallel")
        self.w_arr_circ_orient.pack(fill="x", pady=4)
        Tooltip(self.w_arr_circ_orient,
                "Element orientation for circular arrays:\n"
                "• Parallel — all elements face the same direction.\n"
                "• Radial — each element faces outward from centre.")

        # ══════════════════════════════════════════════════════════
        #  SECTION 2: Frequency & Scaling
        # ══════════════════════════════════════════════════════════

        # ── Frequency card ──────────────────────────────────────
        self._freq_card = Card(self._left_panel, title="Frequency")
        self._freq_card.pack(fill="x", padx=24, pady=8)

        freq_inner = ctk.CTkFrame(self._freq_card, fg_color="transparent")
        freq_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_fmin = LabeledEntry(freq_inner, "F min (MHz)", "30.0")
        self.w_fmin.pack(fill="x", pady=4)

        self.w_fmax = LabeledEntry(freq_inner, "F max (MHz)", "300.0")
        self.w_fmax.pack(fill="x", pady=4)

        self.w_nslices = LabeledEntry(freq_inner, "Number of Slices", "10")
        self.w_nslices.pack(fill="x", pady=4)

        self.w_spacing = LabeledOption(freq_inner, "Freq Slice Spacing",
                                       ["linear", "log"], default="linear")
        self.w_spacing.pack(fill="x", pady=4)

        self.w_reffreq = LabeledEntry(freq_inner, "Ref Frequency (MHz)", "",
                                      tooltip="Leave blank for auto (geometric mean)")
        self.w_reffreq.pack(fill="x", pady=4)

        # ── BW Decay Mode card ──────────────────────────────────
        self.bw_decay_card = Card(self._left_panel, title="Beamwidth vs Frequency")
        self.bw_decay_card.pack(fill="x", padx=24, pady=8)

        bwd_inner = ctk.CTkFrame(self.bw_decay_card, fg_color="transparent")
        bwd_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        # Freq-dependent BW enable switches (moved here from Physics)
        self.w_freq_bw_az = LabeledSwitch(bwd_inner,
                                          "Freq-dependent BW (Az)", True)
        self.w_freq_bw_az.pack(fill="x", pady=4)

        self.w_freq_bw_el = LabeledSwitch(bwd_inner,
                                          "Freq-dependent BW (El)", True)
        self.w_freq_bw_el.pack(fill="x", pady=4)

        _decay_modes = ["Exponent", "Percentage", "Three-Point"]

        self.w_decay_mode_az = LabeledOption(
            bwd_inner, "Az Decay Mode", _decay_modes,
            default="Exponent",
            command=lambda _v: self._refresh_decay_widgets(),
        )
        self.w_decay_mode_az.pack(fill="x", pady=4)

        self.w_decay_mode_el = LabeledOption(
            bwd_inner, "El Decay Mode", _decay_modes,
            default="Exponent",
            command=lambda _v: self._refresh_decay_widgets(),
        )
        self.w_decay_mode_el.pack(fill="x", pady=4)

        # -- Exponent sub-params --
        self._bwd_exp_frame = ctk.CTkFrame(bwd_inner, fg_color="transparent")
        self._bwd_exp_frame.pack(fill="x", pady=2)
        self.w_az_scaling_exp = LabeledEntry(
            self._bwd_exp_frame, "Az Scaling Exponent", "0.8",
            tooltip="cos^n exponent: 1.0 = inverse-linear, 0.5 = sqrt")
        self.w_az_scaling_exp.pack(fill="x", pady=2)
        self.w_el_scaling_exp = LabeledEntry(
            self._bwd_exp_frame, "El Scaling Exponent", "0.8",
            tooltip="cos^n exponent for elevation BW scaling")
        self.w_el_scaling_exp.pack(fill="x", pady=2)

        self._bwd_lpda_frame = ctk.CTkFrame(bwd_inner, fg_color="transparent")
        self._bwd_lpda_frame.pack(fill="x", pady=2)
        self.w_az_lpda_var = LabeledEntry(
            self._bwd_lpda_frame, "Az LPDA Variation Factor", "0.3",
            tooltip="0=constant BW, 1=full frequency scaling")
        self.w_az_lpda_var.pack(fill="x", pady=2)
        self.w_el_lpda_var = LabeledEntry(
            self._bwd_lpda_frame, "El LPDA Variation Factor", "0.3",
            tooltip="LPDA variation damping for elevation")
        self.w_el_lpda_var.pack(fill="x", pady=2)

        # -- Percentage sub-params --
        self._bwd_pct_frame = ctk.CTkFrame(bwd_inner, fg_color="transparent")
        self._bwd_pct_frame.pack(fill="x", pady=2)
        self.w_az_pct_per_oct = LabeledEntry(
            self._bwd_pct_frame, "Az % per Octave", "15.0",
            tooltip="Beamwidth reduction per frequency doubling")
        self.w_az_pct_per_oct.pack(fill="x", pady=2)
        self.w_el_pct_per_oct = LabeledEntry(
            self._bwd_pct_frame, "El % per Octave", "15.0",
            tooltip="Elevation BW reduction per octave")
        self.w_el_pct_per_oct.pack(fill="x", pady=2)

        # -- Three-Point sub-params --
        self._bwd_3pt_frame = ctk.CTkFrame(bwd_inner, fg_color="transparent")
        self._bwd_3pt_frame.pack(fill="x", pady=2)
        self.w_az_3pt_start = LabeledEntry(
            self._bwd_3pt_frame, "Az BW @ f_start (deg)", "90",
            tooltip="Azimuth beamwidth at lowest frequency")
        self.w_az_3pt_start.pack(fill="x", pady=2)
        self.w_az_3pt_mid = LabeledEntry(
            self._bwd_3pt_frame, "Az BW @ f_mid (deg)", "65",
            tooltip="Azimuth beamwidth at band centre")
        self.w_az_3pt_mid.pack(fill="x", pady=2)
        self.w_az_3pt_end = LabeledEntry(
            self._bwd_3pt_frame, "Az BW @ f_end (deg)", "45",
            tooltip="Azimuth beamwidth at highest frequency")
        self.w_az_3pt_end.pack(fill="x", pady=2)
        self.w_el_3pt_start = LabeledEntry(
            self._bwd_3pt_frame, "El BW @ f_start (deg)", "90",
            tooltip="Elevation beamwidth at lowest frequency")
        self.w_el_3pt_start.pack(fill="x", pady=2)
        self.w_el_3pt_mid = LabeledEntry(
            self._bwd_3pt_frame, "El BW @ f_mid (deg)", "70",
            tooltip="Elevation beamwidth at band centre")
        self.w_el_3pt_mid.pack(fill="x", pady=2)
        self.w_el_3pt_end = LabeledEntry(
            self._bwd_3pt_frame, "El BW @ f_end (deg)", "50",
            tooltip="Elevation beamwidth at highest frequency")
        self.w_el_3pt_end.pack(fill="x", pady=2)

        # -- Min / Max BW clamps --
        self._bwd_clamp_frame = ctk.CTkFrame(bwd_inner, fg_color="transparent")
        self._bwd_clamp_frame.pack(fill="x", pady=2)
        self.w_az_min_bw = LabeledEntry(
            self._bwd_clamp_frame, "Az Min BW (deg)", "10",
            tooltip="Floor: beamwidth will never go below this")
        self.w_az_min_bw.pack(fill="x", pady=2)
        self.w_az_max_bw = LabeledEntry(
            self._bwd_clamp_frame, "Az Max BW (deg)", "180",
            tooltip="Ceiling: beamwidth will never exceed this")
        self.w_az_max_bw.pack(fill="x", pady=2)
        self.w_el_min_bw = LabeledEntry(
            self._bwd_clamp_frame, "El Min BW (deg)", "10",
            tooltip="Floor for elevation beamwidth")
        self.w_el_min_bw.pack(fill="x", pady=2)
        self.w_el_max_bw = LabeledEntry(
            self._bwd_clamp_frame, "El Max BW (deg)", "90",
            tooltip="Ceiling for elevation beamwidth")
        self.w_el_max_bw.pack(fill="x", pady=2)

        # Initial sub-frame visibility
        self._refresh_decay_widgets()

        # ── Gain-Beamwidth Coupling card ─────────────────────────
        self.gbw_card = Card(self._left_panel, title="Gain-Beamwidth Coupling")
        self.gbw_card.pack(fill="x", padx=24, pady=8)

        gbw_inner = ctk.CTkFrame(self.gbw_card, fg_color="transparent")
        gbw_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_gbw_enabled = LabeledSwitch(
            gbw_inner, "Enable Coupling", False,
            command=lambda: self._refresh_gbw_widgets())
        self.w_gbw_enabled.pack(fill="x", pady=4)

        self._gbw_radio_frame = ctk.CTkFrame(
            gbw_inner, fg_color="transparent")
        self._gbw_mode_var = ctk.StringVar(value="independent")
        for value, label in [
            ("gain_drives_bw",  "Gain drives beamwidth"),
            ("bw_drives_gain",  "Beamwidth drives gain"),
            ("independent",     "Independent curves"),
        ]:
            ctk.CTkRadioButton(
                self._gbw_radio_frame, text=label,
                variable=self._gbw_mode_var, value=value,
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"],
                border_color=COLORS["entry_border"],
                hover_color=COLORS["accent_light"],
                command=lambda: self._refresh_gbw_widgets(),
            ).pack(anchor="w", pady=2)

        self._gbw_param_frame = ctk.CTkFrame(
            gbw_inner, fg_color="transparent")
        self.w_gbw_rolloff = LabeledEntry(
            self._gbw_param_frame,
            "Gain Rolloff (dB/octave)", "1.5",
            tooltip="How much peak gain decreases per "
                    "octave below f_max")
        self.w_gbw_rolloff.pack(fill="x", pady=2)

        # Hide radio + param frames initially (shown when enabled)
        self._refresh_gbw_widgets()

        # ══════════════════════════════════════════════════════════
        #  SECTION 3: Physics Effects
        # ══════════════════════════════════════════════════════════

        # ── Physics Effects card (toggles only) ──────────────────
        self._physics_card = Card(self._left_panel, title="Physics Effects")
        self._physics_card.pack(fill="x", padx=24, pady=8)

        feat_inner = ctk.CTkFrame(self._physics_card, fg_color="transparent")
        feat_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_sidelobes = LabeledSwitch(feat_inner, "Sidelobes (Taylor)",
                                         True,
                                         command=self._refresh_physics_cards)
        self.w_sidelobes.pack(fill="x", pady=4)

        self.w_breakup = LabeledSwitch(feat_inner, "Pattern Breakup", False,
                                       command=self._refresh_physics_cards)
        self.w_breakup.pack(fill="x", pady=4)

        self.w_ground = LabeledSwitch(feat_inner, "Ground Reflection", False,
                                      command=self._refresh_physics_cards)
        self.w_ground.pack(fill="x", pady=4)

        self.w_xpol = LabeledSwitch(feat_inner, "Cross-Polarization", False,
                                    command=self._refresh_physics_cards)
        self.w_xpol.pack(fill="x", pady=4)

        self.w_vswr = LabeledSwitch(feat_inner, "VSWR Rolloff", True,
                                    command=self._refresh_physics_cards)
        self.w_vswr.pack(fill="x", pady=4)

        self.w_asym = LabeledSwitch(feat_inner, "Asymmetry / Squint", False,
                                    command=self._refresh_physics_cards)
        self.w_asym.pack(fill="x", pady=4)

        # ── Sidelobe sub-params (visible when enabled) ──────────
        self.sl_card = Card(self._left_panel, title="Sidelobe Parameters")
        self.sl_card.pack(fill="x", padx=24, pady=8)

        sl_inner = ctk.CTkFrame(self.sl_card, fg_color="transparent")
        sl_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_sl_first = LabeledEntry(sl_inner, "First SLL (dB)", "-20.0",
                                       tooltip="First sidelobe level relative to peak")
        self.w_sl_first.pack(fill="x", pady=4)

        self.w_sl_decay = LabeledEntry(sl_inner, "Decay Rate (dB/lobe)",
                                       "5.0")
        self.w_sl_decay.pack(fill="x", pady=4)

        self.w_sl_count = LabeledEntry(sl_inner, "Number of Sidelobes", "5")
        self.w_sl_count.pack(fill="x", pady=4)

        # ── Pattern Breakup sub-params ──────────────────────────
        self.breakup_card = Card(self._left_panel, title="Breakup Parameters")
        self.breakup_card.pack(fill="x", padx=24, pady=8)
        brk_inner = ctk.CTkFrame(self.breakup_card, fg_color="transparent")
        brk_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_brk_onset = LabeledEntry(brk_inner, "Onset Angle (°)", "90.0")
        self.w_brk_onset.pack(fill="x", pady=4)
        self.w_brk_amp = LabeledEntry(brk_inner, "Ripple Amp (dB)", "4.0")
        self.w_brk_amp.pack(fill="x", pady=4)
        self.w_brk_dens = LabeledEntry(brk_inner, "Ripple Density", "3.0")
        self.w_brk_dens.pack(fill="x", pady=4)

        # ── Ground Reflection sub-params ────────────────────────
        self.ground_card = Card(self._left_panel, title="Ground Parameters")
        self.ground_card.pack(fill="x", padx=24, pady=8)
        gnd_inner = ctk.CTkFrame(self.ground_card, fg_color="transparent")
        gnd_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_gnd_height = LabeledEntry(gnd_inner, "Height (λ)", "1.0")
        self.w_gnd_height.pack(fill="x", pady=4)
        self.w_gnd_refl = LabeledEntry(gnd_inner, "Reflection Coeff", "0.7")
        self.w_gnd_refl.pack(fill="x", pady=4)

        # ── Cross-Pol sub-params ────────────────────────────────
        self.xpol_card = Card(self._left_panel, title="Cross-Pol Parameters")
        self.xpol_card.pack(fill="x", padx=24, pady=8)
        xp_inner = ctk.CTkFrame(self.xpol_card, fg_color="transparent")
        xp_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_xp_iso = LabeledEntry(xp_inner, "Boresight Iso (dB)", "-25.0")
        self.w_xp_iso.pack(fill="x", pady=4)
        self.w_xp_peak = LabeledEntry(xp_inner, "Peak Angle (°)", "45.0")
        self.w_xp_peak.pack(fill="x", pady=4)
        self.w_xp_max = LabeledEntry(xp_inner, "Max XPol (dB)", "-15.0")
        self.w_xp_max.pack(fill="x", pady=4)

        # ── VSWR Rolloff sub-params ─────────────────────────────
        self.vswr_card = Card(self._left_panel, title="VSWR Parameters")
        self.vswr_card.pack(fill="x", padx=24, pady=8)
        vs_inner = ctk.CTkFrame(self.vswr_card, fg_color="transparent")
        vs_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_vswr_frac = LabeledEntry(vs_inner, "Band Fraction", "0.1")
        self.w_vswr_frac.pack(fill="x", pady=4)
        self.w_vswr_max = LabeledEntry(vs_inner, "Max Rolloff (dB)", "3.0")
        self.w_vswr_max.pack(fill="x", pady=4)
        self.w_vswr_shape = LabeledOption(vs_inner, "Rolloff Shape",
                                          ["cosine", "linear"], default="cosine")
        self.w_vswr_shape.pack(fill="x", pady=4)

        # ── Asymmetry sub-params ────────────────────────────────
        self.asym_card = Card(self._left_panel, title="Asymmetry Parameters")
        self.asym_card.pack(fill="x", padx=24, pady=8)
        as_inner = ctk.CTkFrame(self.asym_card, fg_color="transparent")
        as_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_asym_sq = LabeledEntry(as_inner, "Az Squint (°)", "0.0")
        self.w_asym_sq.pack(fill="x", pady=4)
        self.w_asym_tilt = LabeledEntry(as_inner, "El Tilt (°)", "0.0")
        self.w_asym_tilt.pack(fill="x", pady=4)
        self.w_asym_rand = LabeledEntry(as_inner, "Random Asym (dB)", "1.0")
        self.w_asym_rand.pack(fill="x", pady=4)

        # ══════════════════════════════════════════════════════════
        #  SECTION 4: Simulation Settings
        # ══════════════════════════════════════════════════════════

        self._sim_card = Card(self._left_panel, title="Simulation Settings")
        self._sim_card.pack(fill="x", padx=24, pady=8)

        sim_inner = ctk.CTkFrame(self._sim_card, fg_color="transparent")
        sim_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        # -- Polarization --
        self.w_pol = LabeledOption(sim_inner, "Polarization",
                                   ["vertical", "horizontal", "custom"],
                                   default="vertical",
                                   command=self._on_pol_change)
        self.w_pol.pack(fill="x", pady=4)

        self.w_pol_angle = LabeledEntry(sim_inner, "Pol Angle (°)", "0.0",
                                        tooltip="Only used for custom polarization")
        self.w_pol_angle.pack(fill="x", pady=4)
        self.w_pol_angle.pack_forget()

        # -- Angular resolution --
        self.w_az_step = LabeledOption(sim_inner, "Azimuth Step (°)",
                                       ["0.1", "0.5", "1.0", "2.0", "5.0"],
                                       default="1.0")
        self.w_az_step.pack(fill="x", pady=4)

        self.w_el_step = LabeledOption(sim_inner, "Elevation Step (°)",
                                       ["0.1", "0.5", "1.0", "2.0", "5.0"],
                                       default="1.0")
        self.w_el_step.pack(fill="x", pady=4)

        # -- Front-fade steepness (moved from Physics Effects) --
        self.w_sigmoid_k = LabeledSliderEntry(
            sim_inner, "Front-Fade Steepness (k)", 2, 60,
            default=12, step=1, fmt=".0f",
            tooltip="Sigmoid steepness for front/back hemisphere transition.\n"
                    "Higher = sharper edge at ±90° azimuth.\n"
                    "  40 ≈ 10° transition (steep)\n"
                    "  12 ≈ 30° transition (realistic, default)\n"
                    "   5 ≈ 60° transition (very gradual)")
        self.w_sigmoid_k.pack(fill="x", pady=4)

        # -- Noise --
        self._noise_type_var = ctk.StringVar(value="uniform")
        self._noise_radio_frame = ctk.CTkFrame(sim_inner, fg_color="transparent")
        self._noise_radio_frame.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(self._noise_radio_frame, text="Noise Mode:",
                     font=FONTS["body_bold"], text_color=COLORS["text_secondary"]).pack(anchor="w")

        for val, lbl in [("uniform", "Uniform"), ("gaussian", "Gaussian"), ("quantization", "Quantization")]:
            ctk.CTkRadioButton(
                self._noise_radio_frame, text=lbl, variable=self._noise_type_var, value=val,
                font=FONTS["small"], text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"], border_color=COLORS["entry_border"],
                hover_color=COLORS["accent_light"]
            ).pack(anchor="w", pady=1, padx=10)

        self.w_noise = LabeledSliderEntry(sim_inner, "Noise Value (dB)", 0, 5,
                                          default=0.0, step=0.1, fmt=".1f")
        Tooltip(self.w_noise, "Uniform: Range (+/- dB)\nGaussian: Sigma (dB)\nQuantization: Step Size (dB)")
        self.w_noise.pack(fill="x", pady=4)

        # ══════════════════════════════════════════════════════════
        #  SECTION 5: Output & Run
        # ══════════════════════════════════════════════════════════

        # ── Output card ─────────────────────────────────────────
        self._out_card = Card(self._left_panel, title="Output")
        self._out_card.pack(fill="x", padx=24, pady=8)

        out_inner = ctk.CTkFrame(self._out_card, fg_color="transparent")
        out_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_outdir = FilePicker(out_inner, "Output Directory",
                                   mode="directory")
        # Use a path relative to the project folder (not os.getcwd() which
        # can resolve to System32 when launched from a shortcut).
        _project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.w_outdir.set(os.path.join(os.path.dirname(_project_dir), "antenna_patterns"))
        self.w_outdir.pack(fill="x", pady=4)

        # Output format selection
        self._out_fmt_var = ctk.StringVar(value=".dat")
        self._out_fmt_frame = ctk.CTkFrame(out_inner, fg_color="transparent")
        self._out_fmt_frame.pack(fill="x", pady=4)

        ctk.CTkLabel(self._out_fmt_frame, text="Format:",
                     font=FONTS["body_bold"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 10))

        for val in [".dat", ".csv"]:
            ctk.CTkRadioButton(
                self._out_fmt_frame, text=val, variable=self._out_fmt_var, value=val,
                font=FONTS["small"], text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"], border_color=COLORS["entry_border"],
                hover_color=COLORS["accent_light"]
            ).pack(side="left", padx=(0, 14))

        # ── Config I/O buttons ──────────────────────────────────
        cfg_row = ctk.CTkFrame(self._left_panel, fg_color="transparent")
        cfg_row.pack(fill="x", padx=24, pady=(0, 8))

        ActionButton(
            cfg_row, text="📂  Load Config", width=140,
            style="secondary", command=self._on_load_config,
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ActionButton(
            cfg_row, text="💾  Save Config", width=140,
            style="secondary", command=self._on_save_config,
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # ── Generate button ─────────────────────────────────────
        btn_row = ctk.CTkFrame(self._left_panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=16)

        ActionButton(
            btn_row, text="🚀  Generate Patterns", width=240,
            style="success", command=self._on_generate,
        ).pack(side="left")

        ActionButton(
            btn_row, text="Reset Defaults", width=140,
            style="secondary", command=self._reset_defaults,
        ).pack(side="left", padx=(16, 0))

        # ── Result log ──────────────────────────────────────────
        self.result = ResultBox(self._left_panel, height=180)
        self.result.pack(fill="x", padx=24, pady=(0, 24))

        # ══════════════════════════════════════════════════════════
        #  SECTION 6: Batch Processing
        # ══════════════════════════════════════════════════════════

        batch = Card(self._left_panel, title="Batch Processing")
        batch.pack(fill="x", padx=24, pady=8)

        b_inner = ctk.CTkFrame(batch, fg_color="transparent")
        b_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_recipe = FilePicker(
            b_inner, "Recipe JSON",
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
        )
        self.w_recipe.pack(fill="x", pady=4)

        self.w_batch_output = FilePicker(
            b_inner, "Output Folder",
            mode="directory",
        )
        self.w_batch_output.pack(fill="x", pady=4)

        opts_row = ctk.CTkFrame(b_inner, fg_color="transparent")
        opts_row.pack(fill="x", pady=(4, 0))

        self.w_batch_images = LabeledSwitch(
            opts_row, "Generate Images",
            command=self._on_batch_images_toggle,
        )
        self.w_batch_images.pack(side="left")

        img_note = ctk.CTkLabel(
            b_inner, text="(Generates heatmap / polar / 3D / trend PNGs "
            "for every job -- this is slow)",
            font=FONTS["small"], text_color=COLORS["text_muted"],
            anchor="w",
        )
        img_note.pack(fill="x", pady=(0, 2))

        # ── Report generation (requires Generate Images) ────────
        report_row = ctk.CTkFrame(b_inner, fg_color="transparent")
        report_row.pack(fill="x", pady=(4, 0))

        self.w_batch_report = LabeledSwitch(
            report_row, "Generate Report",
            command=self._on_batch_report_toggle,
        )
        self.w_batch_report.pack(side="left")
        self.w_batch_report._switch.configure(state="disabled")

        self._rpt_note = ctk.CTkLabel(
            b_inner, text="(Requires Generate Images. Produces a PDF "
            "report for each batch job.)",
            font=FONTS["small"], text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._rpt_note.pack(fill="x", pady=(0, 2))

        # Report preset radio buttons
        self._report_preset_var = ctk.StringVar(value="default")
        self._report_radio_frame = ctk.CTkFrame(
            b_inner, fg_color="transparent")
        
        for value, label in [
            ("default", "Default"),
            ("full",    "Full (all sections)"),
            ("minimal", "Minimal (summary + basic)"),
            ("quick",   "Quick (global pages only)"),
        ]:
            rb = ctk.CTkRadioButton(
                self._report_radio_frame, text=label,
                variable=self._report_preset_var, value=value,
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"],
                border_color=COLORS["entry_border"],
                hover_color=COLORS["accent_light"],
            )
            rb.pack(side="left", padx=(0, 14))

        # Report Format Selector
        self._report_fmt_var = ctk.StringVar(value="PDF")
        self._report_fmt_frame = ctk.CTkFrame(b_inner, fg_color="transparent")
        
        ctk.CTkLabel(self._report_fmt_frame, text="Format:", 
                     font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 10))
        
        from core.deps import HAS_PPTX
        _r_formats = ["PDF"]
        if HAS_PPTX:
            _r_formats.append("PPTX")

        for fmt in _r_formats:
            ctk.CTkRadioButton(
                self._report_fmt_frame, text=fmt, variable=self._report_fmt_var, value=fmt,
                font=FONTS["small"], text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"], border_color=COLORS["entry_border"],
                hover_color=COLORS["accent_light"],
            ).pack(side="left", padx=(0, 14))

        btn_row2 = ctk.CTkFrame(b_inner, fg_color="transparent")
        btn_row2.pack(fill="x", pady=(8, 4))

        ActionButton(
            btn_row2, text="\u25b6  Run Batch", width=160,
            style="success", command=self._on_run_batch,
        ).pack(side="left")
        self._btn_cancel_batch = ActionButton(
            btn_row2, text="\u25a0  Cancel", width=120,
            style="danger", command=self._on_cancel_batch,
        )
        self._btn_cancel_batch.pack(side="left", padx=(12, 0))
        self._btn_cancel_batch.configure(state="disabled")
        ActionButton(
            btn_row2, text="\ud83d\udc41  Dry Run", width=140,
            style="secondary", command=self._on_dry_run,
        ).pack(side="left", padx=(12, 0))

        ActionButton(
            btn_row2, text="\ud83d\udcdd  Sample Recipe", width=160,
            style="secondary", command=self._on_sample_recipe,
        ).pack(side="left", padx=(12, 0))

        self.batch_result = ResultBox(self._left_panel, height=200)
        self.batch_result.pack(fill="x", padx=24, pady=(0, 24))

        # ══════════════════════════════════════════════════════════
        #  TOOLTIPS
        # ══════════════════════════════════════════════════════════

        # ── Batch tooltips ──────────────────────────────────────
        Tooltip(self.w_recipe,
                "JSON recipe file describing multiple antenna configs to "
                "generate in batch")
        Tooltip(self.w_batch_output,
                "Base output folder -- each job creates a subfolder here. "
                "Leave empty to use the output_dir from the recipe.")
        Tooltip(self.w_batch_images,
                "Produce heatmap / polar / 3D / trend PNGs for each job. "
                "This is slow -- each job generates multiple plot images.")
        Tooltip(self.w_batch_report,
                "Generate a PDF report for each batch job. "
                "Requires Generate Images to be enabled.")

        # ── Core parameters ──
        Tooltip(self.w_type,
                "Select the antenna model to generate.\n"
                "LPDA: log-periodic dipole array (broadband, moderate gain).\n"
                "Omni: omnidirectional (360° azimuth, elevation-only shaping).\n"
                "Panel: flat-panel sector antenna with optional downtilt.\n"
                "Dish: parabolic reflector (high gain, narrow beam).\n"
                "Horn: pyramidal / conical horn (clean pattern, moderate gain).\n"
                "Monopole: quarter-wave vertical (ground-plane dependent).\n"
                "Array: phased array with configurable geometry and steering.")
        Tooltip(self.w_gain,
                "Peak boresight gain in dBi. This is the maximum gain "
                "at the main beam center. Typical values:\n"
                "  Omni: 2–5 dBi    Panel: 14–18 dBi\n"
                "  LPDA: 6–10 dBi   Dish: 20–45 dBi\n"
                "  Horn: 10–25 dBi  Array: 15–30+ dBi")
        Tooltip(self.w_ftb,
                "Front-to-back ratio (dB). The difference between "
                "the forward peak gain and the gain at 180° (directly behind "
                "the antenna). Higher F/B = less backward radiation.\n"
                "Typical: 15–30 dB for directional antennas.")

        # ── Type-specific parameters ──
        Tooltip(self.w_downtilt,
                "Mechanical tilt angle in degrees.\n"
                "Positive values tilt the main beam below the horizon.\n"
                "Applies to Panel, Dish, Horn, and Array.\n"
                "Typical cell-site panels use 0–15° downtilt.")
        Tooltip(self.w_dish_eff,
                "Aperture efficiency (0 to 1). The fraction of the "
                "parabolic dish aperture that contributes effectively to gain.\n"
                "Typical: 0.50–0.70 for standard feeds.\n"
                "Higher efficiency → higher gain but higher sidelobes.")
        Tooltip(self.w_elem_len,
                "Monopole element length in wavelengths.\n"
                "0.25λ = standard quarter-wave monopole.\n"
                "0.50λ = half-wave (higher gain, different elevation pattern).\n"
                "5/8λ (0.625) = popular for mobile antennas (≈3 dBd gain).")

        # ── Beamwidth ──
        Tooltip(self.w_az_bw,
                "3 dB azimuth beamwidth in degrees — the angular width "
                "of the main beam (in the horizontal plane) between the "
                "half-power points.\n"
                "Wider beam = broader coverage, lower gain.\n"
                "Typical: 65° (panel), 30° (dish), 360° (omni).")
        Tooltip(self.w_el_bw,
                "3 dB elevation beamwidth in degrees — the angular width "
                "of the main beam in the vertical plane.\n"
                "Narrower beam = higher gain concentration.\n"
                "Typical: 7–15° (panel), 1–5° (dish), 60–90° (omni).")

        # ── Array parameters ──
        Tooltip(self.w_arr_geom,
                "Array geometry layout:\n"
                "• Linear — elements along a single axis (1×N).\n"
                "• Planar — 2-D rectangular grid (NX × NY).\n"
                "• Circular — elements equally spaced on a ring.")
        Tooltip(self.w_arr_nx,
                "Number of array elements along the X axis.\n"
                "More elements → narrower beam, higher gain.\n"
                "Typical: 4–64 elements.")
        Tooltip(self.w_arr_ny,
                "Number of elements along Y (planar arrays only).\n"
                "For linear arrays, keep this at 1.\n"
                "NX × NY = total element count.")
        Tooltip(self.w_arr_dx,
                "Element spacing along X in wavelengths (λ).\n"
                "0.5λ = standard half-wave spacing (no grating lobes).\n"
                "< 0.5λ = wider beam, more overlap.\n"
                "> 0.5λ = risk of grating lobes appearing at wide scan.")
        Tooltip(self.w_arr_dy,
                "Element spacing along Y in wavelengths (planar only).\n"
                "Same considerations as X spacing.\n"
                "0.5λ is the standard starting point.")
        Tooltip(self.w_arr_steer_az,
                "Electronic beam steering angle in azimuth (degrees).\n"
                "0° = broadside (perpendicular to the array face).\n"
                "Positive = steer right, negative = steer left.\n"
                "Maximum useful scan ≈ ±60° before grating lobes appear.")
        Tooltip(self.w_arr_steer_el,
                "Electronic beam steering angle in elevation (degrees).\n"
                "0° = broadside. Positive = steer up.\n"
                "Gain drops and beamwidth broadens at large scan angles.")
        Tooltip(self.w_arr_weight,
                "Element amplitude weighting (tapering):\n"
                "• Uniform — all elements have equal amplitude.\n"
                "  Highest gain but highest sidelobes (≈ −13 dB).\n"
                "• Taylor — amplitude taper across the aperture.\n"
                "  Lower sidelobes at the cost of slightly reduced gain.")
        Tooltip(self.w_arr_taper,
                "Taylor taper sidelobe level in dB (negative).\n"
                "Controls the peak sidelobe level of the Taylor window.\n"
                "−20 dB is moderate; −30 dB gives very low sidelobes\n"
                "but wider main beam and lower efficiency.")

        # ── Frequency ──
        Tooltip(self.w_fmin,
                "Lower edge of the frequency band in MHz.\n"
                "Patterns are generated at each frequency slice between "
                "F min and F max.")
        Tooltip(self.w_fmax,
                "Upper edge of the frequency band in MHz.\n"
                "Wider bands show more beamwidth and gain variation.")
        Tooltip(self.w_nslices,
                "Number of frequency slices to generate.\n"
                "Each slice produces a separate CSV file.\n"
                "More slices give finer frequency resolution but take longer.\n"
                "Typical: 5–20 for quick checks; 50–200 for detailed studies.")
        Tooltip(self.w_spacing,
                "Frequency distribution between slices:\n"
                "• Linear — equal MHz steps between F min and F max.\n"
                "• Log — equal ratio steps (better for wideband antennas "
                "where behaviour changes by octave).")
        Tooltip(self.w_reffreq,
                "Reference frequency for beamwidth scaling (MHz).\n"
                "The beamwidths you enter apply at this frequency; other "
                "slices scale inversely (BW ∝ 1/f).\n"
                "Leave blank → auto-calculated as the geometric mean of "
                "F min and F max.")

        # ── BW decay mode ──
        Tooltip(self.w_freq_bw_az,
                "Scale azimuth beamwidth inversely with frequency.\n"
                "When ON: BW(f) = BW_ref × (f_ref / f).\n"
                "This models the physical narrowing of beams at higher "
                "frequencies. Disable if you want fixed beamwidth "
                "across the band.")
        Tooltip(self.w_freq_bw_el,
                "Scale elevation beamwidth inversely with frequency.\n"
                "Same as azimuth scaling but for the vertical plane.\n"
                "Important for dish and horn antennas where the aperture "
                "is electrically larger at higher frequencies.")
        Tooltip(self.w_decay_mode_az,
                "How azimuth beamwidth scales with frequency:\n"
                "• Exponent — BW = base × (f_ref/f)^exp\n"
                "• Percentage — BW shrinks by X% per octave\n"
                "• Three-Point — specify BW at start/mid/end freq")
        Tooltip(self.w_decay_mode_el,
                "How elevation beamwidth scales with frequency.\n"
                "Same three modes as azimuth; can be set independently.")

        # Exponent sub-params
        Tooltip(self.w_az_scaling_exp,
                "Azimuth scaling exponent for BW(f) = base × (f_ref/f)^exp.\n"
                "1.0 = inversely linear (physical aperture scaling).\n"
                "0.5 = square-root (gentler narrowing with frequency).\n"
                "0.8 = typical default. Range: 0.1–2.0.")
        Tooltip(self.w_el_scaling_exp,
                "Elevation scaling exponent — same formula as azimuth.\n"
                "Can differ from the Az exponent to model antennas with\n"
                "different H/V aperture growth rates.")
        Tooltip(self.w_az_lpda_var,
                "LPDA variation factor for azimuth (0–1).\n"
                "Damps the exponent scaling for log-periodic designs whose\n"
                "beamwidth changes less than a simple aperture antenna.\n"
                "0 = constant BW (no frequency dependence).\n"
                "1 = full exponent scaling (same as a dish/horn).\n"
                "Typical LPDA: 0.2–0.4.")
        Tooltip(self.w_el_lpda_var,
                "LPDA variation factor for elevation (0–1).\n"
                "Same concept as the azimuth factor.\n"
                "Can be set independently if H-plane and E-plane\n"
                "behave differently across the band.")

        # Percentage sub-params
        Tooltip(self.w_az_pct_per_oct,
                "Azimuth BW reduction per octave (%).\n"
                "Each time frequency doubles, azimuth beamwidth decreases\n"
                "by this percentage. 15% = moderate narrowing.\n"
                "0% = no change. 50% = aggressive narrowing.\n"
                "Scale is linear: BW = base × (1 − pct/100 × octaves).")
        Tooltip(self.w_el_pct_per_oct,
                "Elevation BW reduction per octave (%).\n"
                "Same linear-decay model as azimuth.\n"
                "Set independently to match measured elevation behaviour.")

        # Three-Point sub-params
        Tooltip(self.w_az_3pt_start,
                "Azimuth beamwidth at the lowest frequency (f_start).\n"
                "This is the wide end of the band where the aperture\n"
                "is electrically smallest. Units: degrees.")
        Tooltip(self.w_az_3pt_mid,
                "Azimuth beamwidth at band centre (f_mid).\n"
                "Quadratic Lagrange interpolation curves through\n"
                "all three points, allowing non-linear shaping.")
        Tooltip(self.w_az_3pt_end,
                "Azimuth beamwidth at the highest frequency (f_end).\n"
                "The narrow end of the band where the aperture\n"
                "is electrically largest. Units: degrees.")
        Tooltip(self.w_el_3pt_start,
                "Elevation beamwidth at f_start.\n"
                "Specified independently from azimuth to allow\n"
                "different H-plane vs E-plane behaviour.")
        Tooltip(self.w_el_3pt_mid,
                "Elevation beamwidth at f_mid (band centre).\n"
                "The interpolation uses quadratic Lagrange fitting\n"
                "through the three frequency/BW pairs.")
        Tooltip(self.w_el_3pt_end,
                "Elevation beamwidth at f_end.\n"
                "The narrowest expected elevation beamwidth\n"
                "at the top of the operating band.")

        # Min / Max BW clamps
        Tooltip(self.w_az_min_bw,
                "Azimuth beamwidth floor (degrees).\n"
                "The computed BW will never go below this value,\n"
                "regardless of mode. Prevents unrealistically narrow\n"
                "beams. Default: 10°.")
        Tooltip(self.w_az_max_bw,
                "Azimuth beamwidth ceiling (degrees).\n"
                "Caps the BW to prevent unphysical wide patterns.\n"
                "For sector antennas, 120–180° is typical.\n"
                "For omni, this can remain at 360°.")
        Tooltip(self.w_el_min_bw,
                "Elevation beamwidth floor (degrees).\n"
                "Same clamping concept as azimuth.\n"
                "Prevents the elevation beam from becoming\n"
                "unrealistically narrow. Default: 10°.")
        Tooltip(self.w_el_max_bw,
                "Elevation beamwidth ceiling (degrees).\n"
                "Caps the elevation BW. For most antennas,\n"
                "90° is a sensible upper limit.\n"
                "For hemisphere coverage, set higher.")

        # ── Physics effects ──
        Tooltip(self.w_sidelobes,
                "Add sidelobes using a Taylor-window envelope.\n"
                "When ON, the pattern includes realistic sidelobe "
                "structure controlled by the Sidelobe Parameters card.\n"
                "When OFF, only the main lobe is generated "
                "(cosine-squared rolloff).")
        Tooltip(self.w_breakup,
                "Simulate pattern breakup at frequencies away from "
                "the design center.\n"
                "Adds frequency-dependent ripple to the pattern, "
                "modelling real-world behaviour where patterns degrade "
                "at band edges.")
        Tooltip(self.w_ground,
                "Apply ground-reflection interference lobing.\n"
                "Models the effect of a perfectly conducting ground plane "
                "below the antenna, creating elevation nulls and lobes.\n"
                "Most relevant for monopoles and ground-mounted antennas.")
        Tooltip(self.w_xpol,
                "Generate a cross-polarization pattern alongside "
                "the co-pol pattern.\n"
                "Produces a separate _xpol.csv file for each frequency "
                "slice. Cross-pol isolation depends on the antenna type "
                "and polarization purity.")
        Tooltip(self.w_vswr,
                "Simulate VSWR mismatch loss at band edges.\n"
                "Rolls off gain near F min and F max to model the "
                "impedance mismatch that increases return loss outside "
                "the antenna's matched bandwidth.")
        Tooltip(self.w_asym,
                "Introduce left/right asymmetry (beam squint) into "
                "the azimuth pattern.\n"
                "Models manufacturing imperfections or intentional "
                "beam offset. The squint amount is random per slice.")

        # ── Sidelobe parameters ──
        Tooltip(self.w_sl_first,
                "First sidelobe level relative to mainlobe peak (dB).\n"
                "Enter as negative, e.g. −20 dB.\n"
                "−13 dB ≈ uniform illumination.\n"
                "−20 to −25 dB = typical tapered designs.\n"
                "−30 dB or lower = aggressive tapering, broader main beam.")
        Tooltip(self.w_sl_decay,
                "Rate at which successive sidelobes decay (dB per lobe).\n"
                "Higher values = faster sidelobe rolloff.\n"
                "Typical: 3–8 dB/lobe. The nth sidelobe level ≈ "
                "1st_SLL − n × decay.")
        Tooltip(self.w_sl_count,
                "Number of sidelobe pairs per principal-plane cut.\n"
                "More lobes = more detailed pattern structure.\n"
                "5–8 is typical; beyond ~10 they fall below the "
                "noise floor.")

        # ── Simulation settings ──
        Tooltip(self.w_pol,
                "Antenna polarization plane:\n"
                "• Vertical — E-field aligned vertically (most common).\n"
                "• Horizontal — E-field aligned horizontally.\n"
                "• Custom — arbitrary tilt angle (enter below).\n"
                "Affects cross-pol pattern generation when enabled.")
        Tooltip(self.w_pol_angle,
                "Custom polarization tilt angle in degrees.\n"
                "0° = vertical, 90° = horizontal, 45° = slant.\n"
                "Only used when Polarization is set to 'custom'.")
        Tooltip(self.w_az_step,
                "Azimuth angular step size in degrees.\n"
                "Determines how many azimuth points per CSV row.\n"
                "1.0° → 361 points (−180 to +180).\n"
                "0.5° → 721 points — higher fidelity for narrow beams.\n"
                "Smaller steps = larger files and longer generation time.")
        Tooltip(self.w_el_step,
                "Elevation angular step size in degrees.\n"
                "Determines how many elevation rows per CSV.\n"
                "1.0° → 361 rows.  For dish antennas with very narrow "
                "beams, 0.5° or 0.1° may be needed to resolve the main lobe.")
        Tooltip(self.w_sigmoid_k,
                "Controls the steepness of the sigmoid front/back fade.\n"
                "This function smoothly attenuates the pattern behind ±90° "
                "azimuth.  Higher k = sharper wall at ±90°.\n\n"
                "  k = 40  →  ~10° transition zone (steep, default)\n"
                "  k = 12  →  ~30° transition zone (realistic for most antennas)\n"
                "  k =  5  →  ~60° transition zone (very gradual)\n\n"
                "Applies to LPDA, Panel, Horn, and Dish.")
        Tooltip(self.w_noise,
                "Random noise amplitude in dB added to pattern values.\n"
                "Simulates measurement uncertainty and manufacturing "
                "tolerances.\n"
                "0 dB = perfect pattern (no noise).\n"
                "0.5–1.0 dB = realistic measurement noise.")

        # ── Output ──
        Tooltip(self.w_outdir,
                "Folder where generated CSV pattern files will be saved.\n"
                "One file per frequency slice (plus _xpol.csv if cross-pol "
                "is enabled). The folder is created if it doesn't exist.")

    # ────────────────────────────────────────────────────────────
    #  VISIBILITY
    # ────────────────────────────────────────────────────────────
    def _apply_visibility(self, antenna_type: str) -> None:
        """Show/hide widgets based on the selected antenna type.

        Uses pack_forget on all togglable widgets first, then re-packs
        only the visible ones.  Section-aware card placement ensures
        correct ordering via ``before=`` references to always-visible
        anchor cards (freq, physics, sim, output).
        """
        visible = _TYPE_WIDGETS.get(antenna_type, _TYPE_WIDGETS["LPDA"])

        # Phase 1: Forget ALL togglable inner widgets
        for attr_name in _TOGGLABLE:
            widget = getattr(self, attr_name, None)
            if widget is not None and widget.winfo_manager():
                widget.pack_forget()

        # Forget conditional cards
        for card in (self.bw_card, self.bw_decay_card, self.sl_card,
                     self.breakup_card, self.ground_card, self.xpol_card,
                     self.vswr_card, self.asym_card):
            if card.winfo_manager():
                card.pack_forget()

        # Phase 2: Re-pack inner togglable widgets (non-card items)
        for attr_name in _TOGGLABLE:
            if attr_name in ("sl_card", "arr_card", "gbw_card",
                             "breakup_card", "ground_card", "xpol_card",
                             "vswr_card", "asym_card"):
                continue  # cards handled in Phase 3
            if attr_name not in visible:
                continue
            widget = getattr(self, attr_name, None)
            if widget is None:
                continue
            saved = self._widget_pack_info.get(attr_name, {})
            widget.pack(fill="x", pady=saved.get("pady", 4))

        # Phase 3: Re-pack conditional cards in correct section order
        # Section 1 — Antenna Definition (before freq card)
        if "w_az_bw" in visible or "w_el_bw" in visible:
            self.bw_card.pack(fill="x", padx=24, pady=8,
                              before=self._freq_card)
        if "arr_card" in visible:
            self.arr_card.pack(fill="x", padx=24, pady=8,
                               before=self._freq_card)

        # Section 2 — Frequency & Scaling (before physics card)
        if "w_freq_bw_az" in visible or "w_freq_bw_el" in visible:
            self.bw_decay_card.pack(fill="x", padx=24, pady=8,
                                    before=self._physics_card)
            self._refresh_decay_widgets()
        if "gbw_card" in visible:
            self.gbw_card.pack(fill="x", padx=24, pady=8,
                               before=self._physics_card)

        # Section 3 — Physics Effects sub-cards
        self._refresh_physics_cards()

    def _refresh_physics_cards(self) -> None:
        """Show/hide physics sub-parameter cards based on switches."""
        # Helper to pack a card if its switch is visible AND enabled
        def _update(switch, card):
            if switch.winfo_manager() and switch.get():
                if not card.winfo_manager():
                    card.pack(fill="x", padx=24, pady=8, before=self._sim_card)
            else:
                if card.winfo_manager():
                    card.pack_forget()

        # Sidelobes
        _update(self.w_sidelobes, self.sl_card)
        # Breakup
        _update(self.w_breakup, self.breakup_card)
        # Ground
        _update(self.w_ground, self.ground_card)
        # XPol
        _update(self.w_xpol, self.xpol_card)
        # VSWR
        _update(self.w_vswr, self.vswr_card)
        # Asymmetry
        _update(self.w_asym, self.asym_card)

    # ────────────────────────────────────────────────────────────
    #  BW DECAY SUB-PARAMETER VISIBILITY
    # ────────────────────────────────────────────────────────────
    def _refresh_decay_widgets(self) -> None:
        """Show/hide BW-decay sub-parameter widgets per-plane based on mode."""
        az_mode = self.w_decay_mode_az.get()   # Exponent/Percentage/Three-Point
        el_mode = self.w_decay_mode_el.get()

        az_exp = az_mode == "Exponent"
        el_exp = el_mode == "Exponent"
        az_pct = az_mode == "Percentage"
        el_pct = el_mode == "Percentage"
        az_3pt = az_mode == "Three-Point"
        el_3pt = el_mode == "Three-Point"

        # Show LPDA rows only when exponent mode + LPDA type selected
        try:
            is_lpda = self.w_type.get() == "LPDA"
        except Exception:
            is_lpda = False

        # Per-widget visibility: (widget, should_show)
        rules = [
            # Exponent
            (self.w_az_scaling_exp, az_exp),
            (self.w_el_scaling_exp, el_exp),
            # LPDA variation
            (self.w_az_lpda_var,    az_exp and is_lpda),
            (self.w_el_lpda_var,    el_exp and is_lpda),
            # Percentage
            (self.w_az_pct_per_oct, az_pct),
            (self.w_el_pct_per_oct, el_pct),
            # Three-Point
            (self.w_az_3pt_start,   az_3pt),
            (self.w_az_3pt_mid,     az_3pt),
            (self.w_az_3pt_end,     az_3pt),
            (self.w_el_3pt_start,   el_3pt),
            (self.w_el_3pt_mid,     el_3pt),
            (self.w_el_3pt_end,     el_3pt),
        ]

        for widget, show in rules:
            if show:
                if not widget.winfo_manager():
                    widget.pack(fill="x", pady=2)
            else:
                if widget.winfo_manager():
                    widget.pack_forget()

        # Show/hide the container frames (empty frames should hide)
        any_exp  = az_exp or el_exp
        any_lpda = (az_exp or el_exp) and is_lpda
        any_pct  = az_pct or el_pct
        any_3pt  = az_3pt or el_3pt

        for frame, show in [
            (self._bwd_exp_frame,   any_exp),
            (self._bwd_lpda_frame,  any_lpda),
            (self._bwd_pct_frame,   any_pct),
            (self._bwd_3pt_frame,   any_3pt),
            (self._bwd_clamp_frame, True),      # always visible
        ]:
            if show:
                if not frame.winfo_manager():
                    frame.pack(fill="x", pady=2)
            else:
                if frame.winfo_manager():
                    frame.pack_forget()

    # ────────────────────────────────────────────────────────────
    #  GAIN-BW COUPLING VISIBILITY
    # ────────────────────────────────────────────────────────────
    def _refresh_gbw_widgets(self) -> None:
        """Show/hide gain-BW coupling sub-widgets based on state."""
        enabled = self.w_gbw_enabled.get()
        mode = self._gbw_mode_var.get()
        needs_rolloff = mode in ("gain_drives_bw", "independent")

        if enabled:
            if not self._gbw_radio_frame.winfo_manager():
                self._gbw_radio_frame.pack(
                    fill="x", padx=(20, 0), pady=(2, 4))
            if needs_rolloff:
                if not self._gbw_param_frame.winfo_manager():
                    self._gbw_param_frame.pack(fill="x", pady=2)
            else:
                if self._gbw_param_frame.winfo_manager():
                    self._gbw_param_frame.pack_forget()
        else:
            if self._gbw_radio_frame.winfo_manager():
                self._gbw_radio_frame.pack_forget()
            if self._gbw_param_frame.winfo_manager():
                self._gbw_param_frame.pack_forget()

    # ────────────────────────────────────────────────────────────
    #  CALLBACKS
    # ────────────────────────────────────────────────────────────
    def _on_type_change(self, value) -> None:
        """Update defaults and visibility when antenna type changes."""
        # 1. Apply visibility rules
        self._apply_visibility(value)

        # 2. Load type-specific default values
        try:
            from antennas import get_antenna
            ant = get_antenna(value)
            params = ant.default_params()
            if "az_beamwidth_deg" in params:
                self.w_az_bw.set(params["az_beamwidth_deg"])
            if "el_beamwidth_deg" in params:
                self.w_el_bw.set(params["el_beamwidth_deg"])
            if "max_gain_dbi" in params:
                self.w_gain.set(params["max_gain_dbi"])
            if "ftb_ratio_db" in params:
                self.w_ftb.set(params["ftb_ratio_db"])
            if "f_min_mhz" in params:
                self.w_fmin.set(str(params["f_min_mhz"]))
            if "f_max_mhz" in params:
                self.w_fmax.set(str(params["f_max_mhz"]))
            # Type-specific widget defaults
            if "element_length_wavelengths" in params:
                self.w_elem_len.set(str(params["element_length_wavelengths"]))
            if "dish_efficiency" in params:
                self.w_dish_eff.set(str(params["dish_efficiency"]))
            if "feed_edge_taper_db" in params:
                self.w_feed_taper.set(str(params["feed_edge_taper_db"]))
        except Exception:
            pass

        # 3. Reset optional fields for types that don't use them
        if value != "Horn":
            self.w_horn_aperture.set("")
        if value != "Monopole":
            self.w_mono_phys_len.set("")

        # 4. Auto-enable gain-BW coupling for LPDA
        self.w_gbw_enabled.set(value == "LPDA")
        self._refresh_gbw_widgets()

    def _on_pol_change(self, value) -> None:
        """Show pol-angle entry only for custom polarization."""
        if value == "custom":
            self.w_pol_angle.pack(fill="x", pady=4,
                                  after=self.w_pol)
        else:
            self.w_pol_angle.pack_forget()

    def _reset_defaults(self) -> None:
        """Reset all fields to default values."""
        self.w_type.set("LPDA")
        self.w_gain.set("7.0")
        self.w_ftb.set("15.0")
        self.w_ftb_affects_gain.set(False)
        self.w_az_bw.set(65)
        self.w_el_bw.set(70)
        self.w_fmin.set("30.0")
        self.w_fmax.set("300.0")
        self.w_nslices.set("10")
        self.w_spacing.set("linear")
        self.w_reffreq.set("")
        self.w_az_step.set("1.0")
        self.w_el_step.set("1.0")
        self.w_pol.set("vertical")
        self.w_pol_angle.set("0.0")
        self.w_noise.set(0.0)
        self._noise_type_var.set("uniform")
        self.w_freq_bw_az.set(True)
        self.w_freq_bw_el.set(True)
        self.w_sidelobes.set(True)
        self.w_breakup.set(False)
        self.w_ground.set(False)
        self.w_xpol.set(False)
        self.w_vswr.set(True)
        self.w_asym.set(False)
        self.w_sigmoid_k.set(12)
        self.w_sl_first.set("-20.0")
        self.w_sl_decay.set("5.0")
        self.w_sl_count.set("5")
        # Type-specific
        self.w_downtilt.set("0.0")
        self.w_dish_eff.set("0.60")
        self.w_feed_taper.set("-12.0")
        self.w_horn_aperture.set("")
        self.w_elem_len.set("0.25")
        self.w_mono_phys_len.set("")
        self.w_arr_geom.set("linear")
        self.w_arr_nx.set("8")
        self.w_arr_ny.set("1")
        self.w_arr_dx.set("0.5")
        self.w_arr_dy.set("0.5")
        self.w_arr_steer_az.set("0.0")
        self.w_arr_steer_el.set("0.0")
        self.w_arr_weight.set("uniform")
        self.w_arr_taper.set("-25.0")
        self.w_arr_elem_pat.set("gaussian")
        self.w_arr_rms_phase.set("0.0")
        self.w_arr_rms_amp.set("0.0")
        self.w_arr_circ_orient.set("parallel")
        # Physics sub-params
        self.w_brk_onset.set("90.0")
        self.w_brk_amp.set("4.0")
        self.w_brk_dens.set("3.0")
        self.w_gnd_height.set("1.0")
        self.w_gnd_refl.set("0.7")
        self.w_xp_iso.set("-25.0")
        self.w_xp_peak.set("45.0")
        self.w_xp_max.set("-15.0")
        self.w_vswr_frac.set("0.1")
        self.w_vswr_max.set("3.0")
        self.w_vswr_shape.set("cosine")
        self.w_asym_sq.set("0.0")
        self.w_asym_tilt.set("0.0")
        self.w_asym_rand.set("1.0")
        self._out_fmt_var.set(".dat")

        # BW decay defaults
        self.w_decay_mode_az.set("Exponent")
        self.w_decay_mode_el.set("Exponent")
        self.w_az_scaling_exp.set("0.8")
        self.w_el_scaling_exp.set("0.8")
        self.w_az_lpda_var.set("0.3")
        self.w_el_lpda_var.set("0.3")
        self.w_az_pct_per_oct.set("15.0")
        self.w_el_pct_per_oct.set("15.0")
        self.w_az_3pt_start.set("90")
        self.w_az_3pt_mid.set("65")
        self.w_az_3pt_end.set("45")
        self.w_el_3pt_start.set("90")
        self.w_el_3pt_mid.set("70")
        self.w_el_3pt_end.set("50")
        self.w_az_min_bw.set("10")
        self.w_az_max_bw.set("180")
        self.w_el_min_bw.set("10")
        self.w_el_max_bw.set("90")
        self._refresh_decay_widgets()
        # Gain-BW coupling defaults (LPDA = enabled)
        self.w_gbw_enabled.set(True)
        self._gbw_mode_var.set("independent")
        self.w_gbw_rolloff.set("1.5")
        self._refresh_gbw_widgets()
        # Reset visibility for LPDA
        self._apply_visibility("LPDA")
        self._refresh_physics_cards()
        self.result.set_text("")
        self.app.status.reset()

    # ────────────────────────────────────────────────────────────
    #  LIVE PREVIEW PANEL
    # ────────────────────────────────────────────────────────────
    def _build_preview_panel(self) -> None:
        """Build the live preview panel on the right side."""
        self._right_panel.grid_rowconfigure(1, weight=2)
        self._right_panel.grid_rowconfigure(2, weight=1)
        self._right_panel.grid_columnconfigure(0, weight=1)

        # ── Row 0: Toolbar ────────────────────────────────────
        toolbar = Card(self._right_panel, title="Live Preview")
        toolbar.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))

        tb_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        tb_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))
        tb_inner.columnconfigure(0, weight=1)
        tb_inner.columnconfigure(1, weight=1)

        self._preview_freq = LabeledEntry(
            tb_inner, "Frequency (MHz)", "165.0",
            tooltip="Single frequency for live preview")
        self._preview_freq.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._preview_plot_type = LabeledOption(
            tb_inner, "Plot Type",
            ["Heatmap", "Cuts (Az+El)", "Polar"],
            default="Heatmap",
        )
        self._preview_plot_type.grid(row=0, column=1, sticky="ew")

        # Heatmap colour-scale range (row 1 of toolbar)
        tb_inner.columnconfigure(2, weight=0)
        tb_inner.columnconfigure(3, weight=0)

        self._hm_vmin = LabeledEntry(
            tb_inner, "Scale min (dBi)", "",
            tooltip="Leave blank for auto")
        self._hm_vmin.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 0))

        self._hm_vmax = LabeledEntry(
            tb_inner, "Scale max (dBi)", "",
            tooltip="Leave blank for auto")
        self._hm_vmax.grid(row=1, column=1, sticky="ew", pady=(4, 0))

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

        self._analysis_box = ResultBox(analysis_card, height=200)
        self._analysis_box.pack(fill="both", expand=True, padx=CARD_PAD,
                                pady=(4, CARD_PAD))

    # ────────────────────────────────────────────────────────────
    #  AUTO-UPDATE SYSTEM
    # ────────────────────────────────────────────────────────────
    def _schedule_preview(self, *_args) -> None:
        """Cancel pending preview, schedule a new one in 500 ms."""
        if self._preview_after_id is not None:
            self.after_cancel(self._preview_after_id)
        self._preview_after_id = self.after(500, self._run_preview)

    def _run_preview(self) -> None:
        """Compute pattern at preview frequency; update canvas + analysis."""
        self._preview_after_id = None

        if self._preview_running:
            # Already computing — reschedule
            self._schedule_preview()
            return
        self._preview_running = True

        try:
            cfg = self._build_config()
        except Exception:
            self._preview_running = False
            return

        freq = safe_float(self._preview_freq._var.get(), 165.0)
        plot_type = self._preview_plot_type.get()

        # Force minimum 1-degree step for speed
        cfg["az_step_deg"] = max(cfg["az_step_deg"], 1.0)
        cfg["el_step_deg"] = max(cfg["el_step_deg"], 1.0)
        # Skip cross-pol for preview
        cfg["features"]["cross_pol"]["enabled"] = False

        def _compute():
            try:
                az_step = cfg["az_step_deg"]
                el_step = cfg["el_step_deg"]
                az_angles = [round(-180 + i * az_step, 4)
                             for i in range(int(360 / az_step) + 1)]
                el_angles = [round(-90 + i * el_step, 4)
                             for i in range(int(180 / el_step) + 1)]

                from core.engine import compute_pattern
                from analysis.analyzer import analyze_from_data

                # 1. Compute main preview pattern
                copol, _ = compute_pattern(az_angles, el_angles, freq, cfg)

                # 2. Compute stats across frequency range (configured slices)
                range_stats = []
                from config import generate_frequencies
                freqs = generate_frequencies(
                    cfg["f_min_mhz"], cfg["f_max_mhz"],
                    cfg["n_slices"], cfg["freq_spacing"]
                )

                for f_step in freqs:
                    # Optimization: reuse main result if freq matches
                    if abs(f_step - freq) < 1e-6:
                        s = analyze_from_data(az_angles, el_angles, copol)
                    else:
                        c_step, _ = compute_pattern(
                            az_angles, el_angles, f_step, cfg)
                        s = analyze_from_data(az_angles, el_angles, c_step)
                    s['freq'] = f_step
                    range_stats.append(s)

                # Schedule GUI update on the main thread
                try:
                    self.after(0, lambda: self._update_preview(
                        az_angles, el_angles, copol,
                        freq, plot_type, cfg, range_stats))
                except RuntimeError:
                    pass  # widget destroyed
            except Exception as e:
                msg = str(e)
                try:
                    self.after(0, lambda: self._preview_error(msg))
                except RuntimeError:
                    pass  # widget destroyed
            finally:
                self._preview_running = False

        threading.Thread(target=_compute, daemon=True).start()

    def _update_preview(self, az, el, data, freq, plot_type, cfg, range_stats=None):
        """Render the plot and analysis on the main thread."""
        from graphing.live_plots import (
            live_heatmap, live_cuts, live_polar)

        title = f"{cfg['antenna_type']} @ {freq:.2f} MHz"

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

        # Update analysis
        try:
            from analysis.analyzer import analyze_from_data
            m = analyze_from_data(az, el, data)
            self._display_metrics(m, range_stats)
        except Exception:
            pass

    def _display_metrics(self, m: dict, range_stats: list[dict] | None = None) -> None:
        """Format and show analysis metrics in the results box."""
        lines = [
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
        sll = m.get("first_sll")
        if sll is not None:
            lines.append(
                f"1st Sidelobe: {sll['level']:.1f} dBi "
                f"({sll['relative']:.1f} dB below peak)")
        lines.append(f"Min Gain:     {m['min_gain']:.2f} dBi")
        lines.append(f"Avg Gain:     {m['avg_gain']:.2f} dBi")
        az_a = m.get("az_asym")
        el_a = m.get("el_asym")
        if az_a is not None:
            lines.append(
                f"Symmetry:     Az {az_a:.2f} dB  |  "
                f"El {el_a:.2f} dB  (RMS)")

        if range_stats:
            from analysis.analyzer import get_pattern_summary_table
            lines.append("\n" + get_pattern_summary_table(range_stats))

        self._analysis_box.set_text("\n".join(lines))

    def _preview_error(self, msg: str) -> None:
        """Show an error in the analysis box."""
        self._analysis_box.set_text(f"Preview error: {msg}")

    # ────────────────────────────────────────────────────────────
    #  CHANGE LISTENERS
    # ────────────────────────────────────────────────────────────
    def _attach_preview_triggers(self) -> None:
        """Connect every parameter widget to the debounced preview."""
        # LabeledEntry (StringVar _var)
        for w in [
            self.w_gain, self.w_ftb, self.w_downtilt,
            self.w_dish_eff, self.w_feed_taper,
            self.w_horn_aperture,
            self.w_elem_len, self.w_mono_phys_len,
            self.w_fmin, self.w_fmax, self.w_reffreq,
            self.w_nslices,
            self.w_pol_angle,
            self.w_sl_first, self.w_sl_decay, self.w_sl_count,
            self.w_brk_onset, self.w_brk_amp, self.w_brk_dens,
            self.w_gnd_height, self.w_gnd_refl,
            self.w_xp_iso, self.w_xp_peak, self.w_xp_max,
            self.w_vswr_frac, self.w_vswr_max,
            self.w_asym_sq, self.w_asym_tilt, self.w_asym_rand,
            self.w_arr_nx, self.w_arr_ny,
            self.w_arr_dx, self.w_arr_dy,
            self.w_arr_steer_az, self.w_arr_steer_el,
            self.w_arr_taper,
            self.w_arr_rms_phase, self.w_arr_rms_amp,
            self.w_az_scaling_exp, self.w_el_scaling_exp,
            self.w_az_lpda_var, self.w_el_lpda_var,
            self.w_az_pct_per_oct, self.w_el_pct_per_oct,
            self.w_az_3pt_start, self.w_az_3pt_mid,
            self.w_az_3pt_end,
            self.w_el_3pt_start, self.w_el_3pt_mid,
            self.w_el_3pt_end,
            self.w_az_min_bw, self.w_az_max_bw,
            self.w_el_min_bw, self.w_el_max_bw,
            self.w_gbw_rolloff,
            self._preview_freq,
            self._hm_vmin, self._hm_vmax,
        ]:
            w._var.trace_add("write", self._schedule_preview)

        # LabeledSliderEntry (DoubleVar _var)
        for w in [
            self.w_az_bw, self.w_el_bw,
            self.w_sigmoid_k, self.w_noise,
        ]:
            w._var.trace_add("write", self._schedule_preview)

        # LabeledOption (StringVar _var)
        for w in [
            self.w_type, self.w_pol, self.w_spacing,
            self.w_az_step, self.w_el_step,
            self.w_decay_mode_az, self.w_decay_mode_el,
            self.w_arr_geom, self.w_arr_weight,
            self.w_arr_elem_pat, self.w_arr_circ_orient,
            self.w_vswr_shape,
            self._preview_plot_type,
        ]:
            w._var.trace_add("write", self._schedule_preview)

        # LabeledSwitch (BooleanVar _var)
        for w in [
            self.w_freq_bw_az, self.w_freq_bw_el,
            self.w_sidelobes, self.w_breakup, self.w_ground,
            self.w_xpol, self.w_vswr, self.w_asym,
            self.w_gbw_enabled, self.w_arr_coupling, 
            self.w_ftb_affects_gain,
        ]:
            w._var.trace_add("write", self._schedule_preview)

        # Radio button StringVars
        self._noise_type_var.trace_add(
            "write", self._schedule_preview)
        self._gbw_mode_var.trace_add(
            "write", self._schedule_preview)

    # ────────────────────────────────────────────────────────────
    #  CONFIG BUILDER
    # ────────────────────────────────────────────────────────────
    def _build_config(self) -> dict:
        """Assemble config dict from GUI state."""
        from config import DEFAULT_CONFIG
        cfg = copy.deepcopy(DEFAULT_CONFIG)

        atype = self.w_type.get()
        cfg["antenna_type"]      = atype
        cfg["max_gain_dbi"]      = safe_float(self.w_gain.get(), 15.0)
        cfg["ftb_ratio_db"]      = safe_float(self.w_ftb.get(), 0.0)
        cfg["ftb_affects_gain"]  = self.w_ftb_affects_gain.get()
        cfg["az_beamwidth_deg"]  = safe_float(self.w_az_bw.get(), 65.0)
        cfg["el_beamwidth_deg"]  = safe_float(self.w_el_bw.get(), 30.0)
        cfg["f_min_mhz"]         = safe_float(self.w_fmin.get(), 700.0)
        cfg["f_max_mhz"]         = safe_float(self.w_fmax.get(), 3800.0)
        cfg["n_slices"]          = safe_int(self.w_nslices.get(), 5)
        cfg["freq_spacing"]      = self.w_spacing.get()
        cfg["az_step_deg"]       = safe_float(self.w_az_step.get(), 1.0)
        cfg["el_step_deg"]       = safe_float(self.w_el_step.get(), 1.0)
        cfg["polarization"]      = self.w_pol.get()
        cfg["pol_angle_deg"]     = safe_float(self.w_pol_angle.get(), 0.0)
        cfg["noise_range_db"]    = safe_float(self.w_noise.get(), 0.0)
        cfg["noise_type"]        = self._noise_type_var.get()
        cfg["sigmoid_k"]         = safe_float(self.w_sigmoid_k.get(), 12.0)
        cfg["output_dir"]        = self.w_outdir.get() or "./antenna_patterns"
        cfg["output_format"]     = self._out_fmt_var.get()

        ref = self.w_reffreq.get().strip()
        cfg["ref_frequency_mhz"] = safe_float(ref) if ref else None

        # ── Type-specific extras ──────────────────────────────
        # Mechanical tilt (universal for directional types)
        if atype in ("Panel", "Dish", "Horn", "Array"):
            cfg["mechanical_tilt_deg"] = safe_float(self.w_downtilt.get(), 0.0)

        if atype == "Dish":
            cfg["dish_efficiency"] = safe_float(self.w_dish_eff.get(), 0.6)
            cfg["feed_edge_taper_db"] = safe_float(self.w_feed_taper.get(), -12.0)
        elif atype == "Horn":
            aperture_str = self.w_horn_aperture.get().strip()
            cfg["horn_aperture_wavelengths"] = (
                safe_float(aperture_str) if aperture_str else None)
        elif atype == "Monopole":
            cfg["element_length_wavelengths"] = safe_float(self.w_elem_len.get(), 0.25)
            phys_str = self.w_mono_phys_len.get().strip()
            cfg["monopole_physical_length_m"] = (
                safe_float(phys_str) if phys_str else None)
        elif atype == "Array":
            cfg["array_geometry"]              = self.w_arr_geom.get()
            cfg["array_n_elements_x"]          = safe_int(self.w_arr_nx.get(), 8)
            cfg["array_n_elements_y"]          = safe_int(self.w_arr_ny.get(), 1)
            cfg["array_spacing_x_lambda"]      = safe_float(self.w_arr_dx.get(), 0.5)
            cfg["array_spacing_y_lambda"]      = safe_float(self.w_arr_dy.get(), 0.5)
            cfg["array_steer_az_deg"]          = safe_float(self.w_arr_steer_az.get(), 0.0)
            cfg["array_steer_el_deg"]          = safe_float(self.w_arr_steer_el.get(), 0.0)
            cfg["array_weighting"]             = self.w_arr_weight.get()
            cfg["array_taper_sll_db"]          = safe_float(self.w_arr_taper.get(), -25.0)
            cfg["array_mutual_coupling"]       = self.w_arr_coupling.get()
            cfg["array_element_pattern"]       = self.w_arr_elem_pat.get()
            cfg["array_rms_phase_error_deg"]   = safe_float(self.w_arr_rms_phase.get(), 0.0)
            cfg["array_rms_amplitude_error_db"] = safe_float(self.w_arr_rms_amp.get(), 0.0)
            cfg["array_circular_orientation"]  = self.w_arr_circ_orient.get()

        # Feature toggles
        cfg["features"]["freq_dependent_bw_az"]["enabled"] = self.w_freq_bw_az.get()
        cfg["features"]["freq_dependent_bw_el"]["enabled"] = self.w_freq_bw_el.get()

        # BW decay mode params  ────────────────────────────────
        _mode_map = {"Exponent": "exponent",
                     "Percentage": "percentage",
                     "Three-Point": "three_point"}
        for plane, mode_w, params in [
            ("az", self.w_decay_mode_az, {
                "scaling_exponent":     lambda: safe_float(self.w_az_scaling_exp.get(), 0.8),
                "variation_factor":     lambda: safe_float(self.w_az_lpda_var.get(), 0.3),
                "decay_pct_per_octave": lambda: safe_float(self.w_az_pct_per_oct.get(), 15.0),
                "three_point_start_deg":lambda: safe_float(self.w_az_3pt_start.get(), 90.0),
                "three_point_mid_deg":  lambda: safe_float(self.w_az_3pt_mid.get(), 65.0),
                "three_point_end_deg":  lambda: safe_float(self.w_az_3pt_end.get(), 45.0),
                "min_bw_deg":           lambda: safe_float(self.w_az_min_bw.get(), 10.0),
                "max_bw_deg":           lambda: safe_float(self.w_az_max_bw.get(), 180.0),
            }),
            ("el", self.w_decay_mode_el, {
                "scaling_exponent":     lambda: safe_float(self.w_el_scaling_exp.get(), 0.8),
                "variation_factor":     lambda: safe_float(self.w_el_lpda_var.get(), 0.3),
                "decay_pct_per_octave": lambda: safe_float(self.w_el_pct_per_oct.get(), 15.0),
                "three_point_start_deg":lambda: safe_float(self.w_el_3pt_start.get(), 90.0),
                "three_point_mid_deg":  lambda: safe_float(self.w_el_3pt_mid.get(), 70.0),
                "three_point_end_deg":  lambda: safe_float(self.w_el_3pt_end.get(), 50.0),
                "min_bw_deg":           lambda: safe_float(self.w_el_min_bw.get(), 10.0),
                "max_bw_deg":           lambda: safe_float(self.w_el_max_bw.get(), 90.0),
            }),
        ]:
            feat_key = f"freq_dependent_bw_{plane}"
            feat = cfg["features"][feat_key]
            feat["decay_mode"] = _mode_map.get(mode_w.get(), "exponent")
            for k, fn in params.items():
                feat[k] = fn()
        cfg["features"]["sidelobes"]["enabled"]            = self.w_sidelobes.get()
        cfg["features"]["pattern_breakup"]["enabled"]      = self.w_breakup.get()
        cfg["features"]["ground_reflection"]["enabled"]    = self.w_ground.get()
        cfg["features"]["cross_pol"]["enabled"]            = self.w_xpol.get()
        cfg["features"]["vswr_rolloff"]["enabled"]         = self.w_vswr.get()
        cfg["features"]["asymmetry"]["enabled"]            = self.w_asym.get()

        # Gain-BW coupling
        gbw = cfg["features"]["gain_bw_coupling"]
        gbw["enabled"] = self.w_gbw_enabled.get()
        gbw["mode"] = self._gbw_mode_var.get()
        gbw["gain_rolloff_db_per_octave"] = safe_float(
            self.w_gbw_rolloff.get(), 1.5)

        # Sidelobe sub-params
        if self.w_sidelobes.get():
            sl = cfg["features"]["sidelobes"]
            sl["first_sidelobe_db"] = safe_float(self.w_sl_first.get(), -13.0)
            sl["decay_rate_db"]     = safe_float(self.w_sl_decay.get(), 5.0)
            sl["n_sidelobes"]       = safe_int(self.w_sl_count.get(), 5)

        # Breakup sub-params
        if self.w_breakup.get():
            bp = cfg["features"]["pattern_breakup"]
            bp["onset_angle_deg"]     = safe_float(self.w_brk_onset.get(), 90.0)
            bp["ripple_amplitude_db"] = safe_float(self.w_brk_amp.get(), 4.0)
            bp["ripple_density"]      = safe_float(self.w_brk_dens.get(), 3.0)

        # Ground sub-params
        if self.w_ground.get():
            gr = cfg["features"]["ground_reflection"]
            gr["height_wavelengths"] = safe_float(self.w_gnd_height.get(), 1.0)
            gr["reflection_coeff"]   = safe_float(self.w_gnd_refl.get(), 0.7)

        # Cross-Pol sub-params
        if self.w_xpol.get():
            xp = cfg["features"]["cross_pol"]
            xp["boresight_isolation_db"] = safe_float(self.w_xp_iso.get(), -25.0)
            xp["peak_angle_deg"]         = safe_float(self.w_xp_peak.get(), 45.0)
            xp["max_cross_pol_db"]       = safe_float(self.w_xp_max.get(), -15.0)

        # VSWR sub-params
        if self.w_vswr.get():
            vs = cfg["features"]["vswr_rolloff"]
            vs["rolloff_band_fraction"] = safe_float(self.w_vswr_frac.get(), 0.1)
            vs["max_rolloff_db"]        = safe_float(self.w_vswr_max.get(), 3.0)
            vs["rolloff_shape"]         = self.w_vswr_shape.get()

        # Asymmetry sub-params
        if self.w_asym.get():
            asy = cfg["features"]["asymmetry"]
            asy["az_squint_deg"]       = safe_float(self.w_asym_sq.get(), 0.0)
            asy["el_tilt_deg"]         = safe_float(self.w_asym_tilt.get(), 0.0)
            asy["random_asymmetry_db"] = safe_float(self.w_asym_rand.get(), 1.0)

        return cfg

    # ────────────────────────────────────────────────────────────
    #  BATCH TOGGLE HELPERS
    # ────────────────────────────────────────────────────────────
    def _on_batch_images_toggle(self) -> None:
        """Enable/disable the report switch based on images toggle."""
        if self.w_batch_images.get():
            self.w_batch_report._switch.configure(state="normal")
        else:
            self.w_batch_report.set(False)
            self.w_batch_report._switch.configure(state="disabled")
            self._report_radio_frame.pack_forget()
            self._report_fmt_frame.pack_forget()

    def _on_batch_report_toggle(self) -> None:
        """Show/hide report preset radios based on report toggle."""
        if self.w_batch_report.get():
            self._report_radio_frame.pack(
                fill="x", padx=(20, 0), pady=(2, 4),
                after=self._rpt_note,
            )
            self._report_fmt_frame.pack(
                fill="x", padx=(20, 0), pady=(0, 4),
                after=self._report_radio_frame
            )
        else:
            self._report_radio_frame.pack_forget()
            self._report_fmt_frame.pack_forget()

    # ────────────────────────────────────────────────────────────
    #  BATCH ACTIONS
    # ────────────────────────────────────────────────────────────
    def _on_cancel_batch(self) -> None:
        """Signal the running batch to stop after the current job."""
        if hasattr(self, "_batch_cancel"):
            self._batch_cancel.set()
        self._btn_cancel_batch.configure(state="disabled")
        self.batch_result.append(
            "\n>> Cancel requested -- stopping after current job...\n")
        self.app.status.busy("Cancelling batch...")

    def _on_run_batch(self) -> None:
        path = self.w_recipe.get()
        if not path:
            self.batch_result.set_text("Select a batch recipe JSON file.")
            return

        output_base = self.w_batch_output.get() or None
        gen_images = self.w_batch_images.get()
        gen_report = self.w_batch_report.get() and gen_images
        report_preset = self._report_preset_var.get() if gen_report else None
        report_format = self._report_fmt_var.get() if gen_report else "PDF"

        self.app.status.busy("Running batch...")
        self.batch_result.set_text("Starting batch...\n")

        self._batch_cancel = threading.Event()
        self._btn_cancel_batch.configure(state="normal")

        def _progress(msg: str) -> None:
            """Push a progress line into the result box (thread-safe)."""
            self.after(0, lambda m=msg: self.batch_result.append(m + "\n"))
            if msg.lstrip().startswith("Job "):
                short = msg.strip().split("\n")[0]
                self.after(0, lambda s=short: self.app.status.busy(
                    f"Batch: {s}"))

        def work():
            try:
                from core.batch import run_batch

                results = run_batch(
                    path,
                    generate_images=gen_images,
                    generate_report=gen_report,
                    report_preset=report_preset,
                    report_format=report_format,
                    output_base=output_base,
                    progress_callback=_progress,
                    cancel_event=self._batch_cancel,
                )

                dirs_text = "\n".join(results) if results else "(none)"
                final = f"\nOutput directories:\n{dirs_text}\n"
                self.after(0, lambda: self.batch_result.append(final))
                self.after(0, lambda: self.app.status.success(
                    f"Batch complete \u2014 {len(results)} jobs"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.batch_result.append(
                    f"\n\u2717 Error: {msg}\n"))
                self.after(0, lambda: self.app.status.error(msg))
            finally:
                self.after(0, lambda: self._btn_cancel_batch.configure(
                    state="disabled"))
        threading.Thread(target=work, daemon=True).start()

    def _on_dry_run(self) -> None:
        path = self.w_recipe.get()
        if not path:
            self.batch_result.set_text("Select a batch recipe JSON file.")
            return

        self.batch_result.set_text("Dry run\u2026\n")

        def _progress(msg: str) -> None:
            self.batch_result.append(msg + "\n")

        try:
            from core.batch import run_batch
            run_batch(path, dry_run=True,
                      progress_callback=_progress)
            self.app.status.success("Dry run OK")
        except Exception as e:
            self.batch_result.append(f"\n\u2717 Error: {e}\n")
            self.app.status.error(str(e))

    def _on_sample_recipe(self) -> None:
        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(
            title="Save Sample Recipe",
            filetypes=[("JSON", "*.json")],
            defaultextension=".json",
            initialfile="sample_recipe.json",
        )
        if not path:
            return
        try:
            from core.batch import create_sample_recipe
            out = create_sample_recipe(path)
            self.batch_result.set_text(f"Sample recipe created:\n{out}")
            self.app.status.success("Sample recipe created")
        except Exception as e:
            self.batch_result.set_text(f"Error: {e}")
            self.app.status.error(str(e))

    # ────────────────────────────────────────────────────────────
    #  CONFIG I/O
    # ────────────────────────────────────────────────────────────
    def _on_save_config(self) -> None:
        cfg = self._build_config()
        path = fd.asksaveasfilename(
            title="Save Configuration",
            filetypes=[("JSON", "*.json")],
            defaultextension=".json",
            initialfile="antenna_config.json"
        )
        if path:
            try:
                with open(path, "w") as f:
                    json.dump(cfg, f, indent=2)
                self.app.status.success(f"Saved config: {os.path.basename(path)}")
            except Exception as e:
                self.app.status.error(f"Save failed: {e}")

    def _on_load_config(self) -> None:
        path = fd.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON", "*.json"), ("All", "*.*")]
        )
        if path:
            try:
                with open(path, "r") as f:
                    cfg = json.load(f)
                self._apply_config(cfg)
                self.app.status.success(f"Loaded config: {os.path.basename(path)}")
            except Exception as e:
                self.app.status.error(f"Load failed: {e}")
                self.result.set_text(f"Error loading config: {e}")

    def _apply_config(self, cfg: dict) -> None:
        """Populate widgets from a configuration dictionary."""
        # Core
        self.w_type.set(cfg.get("antenna_type", "LPDA"))
        self.w_gain.set(str(cfg.get("max_gain_dbi", 7.0)))
        self.w_ftb.set(str(cfg.get("ftb_ratio_db", 15.0)))
        self.w_ftb_affects_gain.set(cfg.get("ftb_affects_gain", False))

        # Type specific
        self.w_downtilt.set(str(cfg.get("mechanical_tilt_deg",
                                        cfg.get("panel_downtilt_deg", 0.0))))
        self.w_dish_eff.set(str(cfg.get("dish_efficiency", 0.6)))
        self.w_feed_taper.set(str(cfg.get("feed_edge_taper_db", -12.0)))
        aperture = cfg.get("horn_aperture_wavelengths")
        self.w_horn_aperture.set(str(aperture) if aperture else "")
        self.w_elem_len.set(str(cfg.get("element_length_wavelengths", 0.25)))
        phys = cfg.get("monopole_physical_length_m")
        self.w_mono_phys_len.set(str(phys) if phys else "")

        # Array
        self.w_arr_geom.set(cfg.get("array_geometry", "linear"))
        self.w_arr_nx.set(str(cfg.get("array_n_elements_x", 8)))
        self.w_arr_ny.set(str(cfg.get("array_n_elements_y", 1)))
        self.w_arr_dx.set(str(cfg.get("array_spacing_x_lambda", 0.5)))
        self.w_arr_dy.set(str(cfg.get("array_spacing_y_lambda", 0.5)))
        self.w_arr_steer_az.set(str(cfg.get("array_steer_az_deg", 0.0)))
        self.w_arr_steer_el.set(str(cfg.get("array_steer_el_deg", 0.0)))
        self.w_arr_weight.set(cfg.get("array_weighting", "uniform"))
        self.w_arr_taper.set(str(cfg.get("array_taper_sll_db", -25.0)))
        self.w_arr_coupling.set(cfg.get("array_mutual_coupling", False))
        self.w_arr_elem_pat.set(cfg.get("array_element_pattern", "gaussian"))
        self.w_arr_rms_phase.set(str(cfg.get("array_rms_phase_error_deg", 0.0)))
        self.w_arr_rms_amp.set(str(cfg.get("array_rms_amplitude_error_db", 0.0)))
        self.w_arr_circ_orient.set(cfg.get("array_circular_orientation", "parallel"))

        # Beamwidth (LabeledSliderEntry uses float)
        self.w_az_bw.set(cfg.get("az_beamwidth_deg", 65.0))
        self.w_el_bw.set(cfg.get("el_beamwidth_deg", 70.0))

        # Frequency
        self.w_fmin.set(str(cfg.get("f_min_mhz", 30.0)))
        self.w_fmax.set(str(cfg.get("f_max_mhz", 300.0)))
        self.w_nslices.set(str(cfg.get("n_slices", 10)))
        self.w_spacing.set(cfg.get("freq_spacing", "linear"))
        ref = cfg.get("ref_frequency_mhz")
        self.w_reffreq.set(str(ref) if ref is not None else "")

        # Angular
        self.w_az_step.set(str(cfg.get("az_step_deg", 1.0)))
        self.w_el_step.set(str(cfg.get("el_step_deg", 1.0)))

        # Polarization / Sim
        self.w_pol.set(cfg.get("polarization", "vertical"))
        self.w_pol_angle.set(str(cfg.get("pol_angle_deg", 0.0)))
        self.w_noise.set(cfg.get("noise_range_db", 0.0))
        self._noise_type_var.set(cfg.get("noise_type", "uniform"))
        self.w_sigmoid_k.set(cfg.get("sigmoid_k", 12.0))

        # Output
        self.w_outdir.set(cfg.get("output_dir", "./antenna_patterns"))
        self._out_fmt_var.set(cfg.get("output_format", ".dat"))

        # Features
        feats = cfg.get("features", {})

        def _set_feat(key, widget, default=True):
            f = feats.get(key, {})
            val = f.get("enabled", default) if isinstance(f, dict) else default
            widget.set(val)
            return f

        f_az = _set_feat("freq_dependent_bw_az", self.w_freq_bw_az)
        f_el = _set_feat("freq_dependent_bw_el", self.w_freq_bw_el)
        f_sl = _set_feat("sidelobes", self.w_sidelobes)
        f_brk = _set_feat("pattern_breakup", self.w_breakup, False)
        f_gnd = _set_feat("ground_reflection", self.w_ground, False)
        f_xp = _set_feat("cross_pol", self.w_xpol, False)
        f_vswr = _set_feat("vswr_rolloff", self.w_vswr)
        f_asym = _set_feat("asymmetry", self.w_asym, False)
        f_gbw = _set_feat("gain_bw_coupling", self.w_gbw_enabled, False)

        # BW Decay params
        _mode_map_inv = {"exponent": "Exponent", "percentage": "Percentage", "three_point": "Three-Point"}
        self.w_decay_mode_az.set(_mode_map_inv.get(f_az.get("decay_mode", "exponent"), "Exponent"))
        self.w_decay_mode_el.set(_mode_map_inv.get(f_el.get("decay_mode", "exponent"), "Exponent"))

        self.w_az_scaling_exp.set(str(f_az.get("scaling_exponent", 0.8)))
        self.w_el_scaling_exp.set(str(f_el.get("scaling_exponent", 0.8)))
        self.w_az_lpda_var.set(str(f_az.get("variation_factor",
                                           f_az.get("lpda_variation_factor", 0.3))))
        self.w_el_lpda_var.set(str(f_el.get("variation_factor",
                                           f_el.get("lpda_variation_factor", 0.3))))
        self.w_az_pct_per_oct.set(str(f_az.get("decay_pct_per_octave", 15.0)))
        self.w_el_pct_per_oct.set(str(f_el.get("decay_pct_per_octave", 15.0)))
        self.w_az_3pt_start.set(str(f_az.get("three_point_start_deg") or 90))
        self.w_az_3pt_mid.set(str(f_az.get("three_point_mid_deg") or 65))
        self.w_az_3pt_end.set(str(f_az.get("three_point_end_deg") or 45))
        self.w_el_3pt_start.set(str(f_el.get("three_point_start_deg") or 90))
        self.w_el_3pt_mid.set(str(f_el.get("three_point_mid_deg") or 70))
        self.w_el_3pt_end.set(str(f_el.get("three_point_end_deg") or 50))
        self.w_az_min_bw.set(str(f_az.get("min_bw_deg", 10.0)))
        self.w_az_max_bw.set(str(f_az.get("max_bw_deg", 180.0)))
        self.w_el_min_bw.set(str(f_el.get("min_bw_deg", 10.0)))
        self.w_el_max_bw.set(str(f_el.get("max_bw_deg", 90.0)))

        # Sub-params
        self.w_sl_first.set(str(f_sl.get("first_sidelobe_db", -20.0)))
        self.w_sl_decay.set(str(f_sl.get("decay_rate_db", 5.0)))
        self.w_sl_count.set(str(f_sl.get("n_sidelobes", 5)))
        self.w_brk_onset.set(str(f_brk.get("onset_angle_deg", 90.0)))
        self.w_brk_amp.set(str(f_brk.get("ripple_amplitude_db", 4.0)))
        self.w_brk_dens.set(str(f_brk.get("ripple_density", 3.0)))
        self.w_gnd_height.set(str(f_gnd.get("height_wavelengths", 1.0)))
        self.w_gnd_refl.set(str(f_gnd.get("reflection_coeff", 0.7)))
        self.w_xp_iso.set(str(f_xp.get("boresight_isolation_db", -25.0)))
        self.w_xp_peak.set(str(f_xp.get("peak_angle_deg", 45.0)))
        self.w_xp_max.set(str(f_xp.get("max_cross_pol_db", -15.0)))
        self.w_vswr_frac.set(str(f_vswr.get("rolloff_band_fraction", 0.1)))
        self.w_vswr_max.set(str(f_vswr.get("max_rolloff_db", 3.0)))
        self.w_vswr_shape.set(f_vswr.get("rolloff_shape", "cosine"))
        self.w_asym_sq.set(str(f_asym.get("az_squint_deg", 0.0)))
        self.w_asym_tilt.set(str(f_asym.get("el_tilt_deg", 0.0)))
        self.w_asym_rand.set(str(f_asym.get("random_asymmetry_db", 1.0)))
        self._gbw_mode_var.set(f_gbw.get("mode", "independent"))
        self.w_gbw_rolloff.set(str(f_gbw.get("gain_rolloff_db_per_octave", 1.5)))

        # Trigger updates
        self._apply_visibility(self.w_type.get())
        self._refresh_decay_widgets()
        self._refresh_gbw_widgets()
        self._refresh_physics_cards()
        self._on_pol_change(self.w_pol.get())

    # ────────────────────────────────────────────────────────────
    #  SINGLE GENERATION
    # ────────────────────────────────────────────────────────────
    def _on_generate(self) -> None:
        """Generate patterns in a background thread."""
        self.app.status.busy("Generating patterns…")
        self.result.set_text("Building configuration…\n")

        def work():
            try:
                cfg = self._build_config()

                from config import validate_config, generate_frequencies
                errors = validate_config(cfg)
                if errors:
                    msg = "Validation errors:\n" + "\n".join(f"  • {e}" for e in errors)
                    self.after(0, lambda: self.result.set_text(msg))
                    self.after(0, lambda: self.app.status.error("Validation failed"))
                    return

                freqs = generate_frequencies(
                    cfg["f_min_mhz"], cfg["f_max_mhz"],
                    cfg["n_slices"], cfg["freq_spacing"],
                )

                self.after(0, lambda: self.result.append(
                    f"Config OK — generating {len(freqs)} slices…\n"
                    f"Output: {cfg['output_dir']}\n\n"
                ))

                from core.engine import run_generation
                import io as _io
                buf = _io.StringIO()
                run_generation(cfg, freqs, writer=buf)

                output = buf.getvalue()
                self.after(0, lambda: self.result.append(output))
                self.after(0, lambda: self.app.status.success(
                    f"Done — {len(freqs)} pattern(s) generated"))

            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))

        threading.Thread(target=work, daemon=True).start()
