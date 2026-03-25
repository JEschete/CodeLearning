"""
How To Page — Complete guided walkthrough of every feature in the GUI.
"""

import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import ScrollablePage, Card, SectionHeading


class HowToPage(ScrollablePage):
    """Built-in user guide with step-by-step instructions per feature."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._build()

    # ────────────────────────────────────────────────────────────
    def _build(self) -> None:
        SectionHeading(self, text="How To — User Guide").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self,
            text="Step-by-step instructions for every feature in the "
                 "AntennaForge.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        sections = [
            self._section_quickstart,
            self._section_generate,
            self._section_visualize,
            self._section_analysis,
            self._section_operations,
            self._section_rf_calcs,
            self._section_reports,
            self._section_settings,
            self._section_tips,
        ]
        for fn in sections:
            fn()

    # ────────────────────────────────────────────────────────────
    def _add_card(self, title: str, body: str) -> None:
        """Helper: add a titled card with wrapped text."""
        card = Card(self, title=title)
        card.pack(fill="x", padx=24, pady=8)
        frm = ctk.CTkFrame(card, fg_color="transparent")
        frm.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))
        ctk.CTkLabel(
            frm, text=body, font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            wraplength=700, justify="left", anchor="nw",
        ).pack(fill="x")

    # ────────────────────────────────────────────────────────────
    def _section_quickstart(self) -> None:
        self._add_card("🚀  Quick Start", (
            "1.  Click  Generate  in the sidebar.\n"
            "2.  Choose an antenna type (e.g. LPDA, Dish, Horn).\n"
            "3.  Adjust beamwidth, gain, and frequency range.\n"
            "4.  Click  Generate Patterns.\n"
            "5.  Switch to  Visualize  and select the output directory.\n"
            "6.  Pick a plot type and click  Plot.\n\n"
            "That's it — you now have synthetic radiation-pattern CSVs "
            "and publication-quality plots."
        ))

    def _section_generate(self) -> None:
        self._add_card("📡  Generate — Creating Patterns", (
            "The Generate page lets you configure every parameter of the "
            "synthetic antenna pattern.\n\n"
            "Core Parameters\n"
            "  • Antenna Type — selects the model (LPDA, Omni, Panel, "
            "Dish, Horn, Monopole, Array).  Changing the type auto-loads "
            "default beamwidth and gain.\n"
            "  • Max Gain (dBi) — peak boresight gain.\n"
            "  • Front-to-Back (dB) — F/B ratio.\n\n"
            "Beamwidth\n"
            "  • Use the slider OR type a value in the entry box; both "
            "stay in sync.  Range: 1°–360°.\n\n"
            "Frequency\n"
            "  • F min / F max define the band edges in MHz.\n"
            "  • Number of Slices — how many frequency points to generate.\n"
            "  • Freq Slice Spacing — linear or logarithmic distribution.\n"
            "  • Ref Frequency — leave blank for auto (geometric mean).\n\n"
            "Polarization\n"
            "  • Vertical / Horizontal presets, or Custom (enter your "
            "own angle in degrees).\n\n"
            "Physics Features\n"
            "  • Toggle each feature ON/OFF independently:\n"
            "    - Freq-dependent BW (Az / El)\n"
            "    - Sidelobes (Taylor taper)\n"
            "    - Pattern Breakup, Ground Reflection, Cross-Pol, "
            "VSWR Rolloff, Asymmetry/Squint.\n\n"
            "Sidelobe Parameters\n"
            "  • First SLL (dB), Decay Rate, Number of Sidelobes.\n\n"
            "Output\n"
            "  • Choose where the CSV files are saved.  Default is "
            "antenna_patterns/ in the working directory."
        ))

    def _section_visualize(self) -> None:
        self._add_card("📊  Visualize — Plotting Patterns", (
            "Input\n"
            "  • Pattern CSV — pick a single CSV for Heatmap, Cuts, "
            "Polar, or 3-D Surface.\n"
            "  • Pattern Directory — point to a folder of CSVs:\n"
            "      ‣ For single-file types, the tool iterates every CSV "
            "and produces one plot per file.\n"
            "      ‣ For multi-file types (Gain vs Freq, BW vs Freq, "
            "Overlay Cuts), all CSVs are used together.\n\n"
            "Plot Types\n"
            "  • Heatmap — azimuth × elevation colour map.\n"
            "  • Cuts (Az+El) — principal-plane gain cuts.\n"
            "  • Polar — polar-coordinate radiation pattern.\n"
            "  • 3D Surface — Matplotlib 3-D surface view.\n"
            "  • Gain vs Freq — peak gain across frequencies.\n"
            "  • BW vs Freq — beamwidth vs frequency.\n"
            "  • Overlay Cuts — multiple frequency cuts overlaid.\n\n"
            "Features\n"
            "  • Existing PNGs are detected automatically — "
            "no redundant regeneration.\n"
            "  • ◀ Prev / Next ▶ arrows cycle through all generated "
            "images.\n"
            "  • Open Folder opens the plot directory in Windows Explorer."
        ))

    def _section_analysis(self) -> None:
        self._add_card("🔍  Analysis — Inspecting Patterns", (
            "Single Pattern Analysis\n"
            "  • Select a CSV and click Analyze.\n"
            "  • Reports peak gain, boresight gain, beamwidths, min/avg "
            "gain.\n\n"
            "Compare Multiple Patterns\n"
            "  • Select multiple CSVs or point to a directory.\n"
            "  • Gives a side-by-side comparison table.\n\n"
            "Sidelobe Mask Compliance\n"
            "  • Tests a pattern against ITU-R S.580-6, ITU-R S.465-6, "
            "or MIL-STD envelopes.\n"
            "  • Choose the test plane (azimuth or elevation) and "
            "enter the peak gain.\n"
            "  • Output shows PASS / FAIL, number of violations, "
            "minimum margin, and angle-by-angle details.\n\n"
            "Mask references:\n"
            "  • ITU-R S.580-6 (2004) — earth-station antennas, "
            "D/λ ≥ 100.\n"
            "  • ITU-R S.465-6 (2010) — earth-station antennas, "
            "smaller D/λ.\n"
            "  • MIL-STD-188-164A/B — military sidelobe envelopes."
        ))

    def _section_operations(self) -> None:
        self._add_card("⚙  Operations — Pattern Math", (
            "Arithmetic\n"
            "  • Six operations on one or two pattern CSVs:\n"
            "    - Add (power-sum two patterns)\n"
            "    - Subtract (dB difference of two patterns)\n"
            "    - Multiply (dB + dB of two patterns)\n"
            "    - Scale (add a dB offset to a single pattern)\n"
            "    - Max Envelope (element-wise max of two patterns)\n"
            "    - Average (power-average of two patterns)\n"
            "  • Output is a new CSV.\n\n"
            "Rotation\n"
            "  • Rotate a pattern in azimuth, elevation, and/or roll "
            "by a given number of degrees.\n"
            "  • Supports single-file or whole-directory rotation.\n"
            "  • Output is a new CSV (or set of CSVs).\n\n"
            "Interpolation\n"
            "  Three modes:\n"
            "  • Freq Interpolate (2 files) — blend two single-freq "
            "patterns to an intermediate frequency.\n"
            "  • Multi-Freq Interpolate — interpolate across a "
            "directory of frequency slices.\n"
            "  • Resample Grid — resample a pattern to a finer or "
            "coarser angular grid (new az/el step size)."
        ))

    def _section_rf_calcs(self) -> None:
        self._add_card("📐  RF Calcs — Link Budget & EIRP", (
            "EIRP Calculator\n"
            "  • Select a pattern CSV, enter Tx power (dBm) and "
            "cable loss (dB).\n"
            "  • Computes EIRP at every azimuth/elevation angle and "
            "writes a new CSV.\n"
            "  • Reports peak EIRP and the angle at which it occurs.\n\n"
            "Power Density\n"
            "  • Same inputs as EIRP plus a distance (m).\n"
            "  • Outputs power-density CSV (W/m² and dBW/m²) at every "
            "angle.\n\n"
            "Free-Space Path Loss\n"
            "  • Enter frequency (MHz) and distance (km).\n"
            "  • Uses FSPL = 20 log₁₀(d) + 20 log₁₀(f) + 32.44.\n\n"
            "Link Budget\n"
            "  • Two modes:\n"
            "    - Boresight Margin — quick single-number Tx→Rx margin.\n"
            "    - Angular Map — full off-axis link budget written to CSV.\n"
            "  • Takes Tx pattern CSV, Rx pattern CSV, Tx power, "
            "cable losses, distance, frequency, and Rx sensitivity.\n"
            "  • Reports received power image, link margin, and S/N."
        ))

    def _section_reports(self) -> None:
        self._add_card("📄  Reports — PDF & LaTeX", (
            "Generate professional PDF or LaTeX reports from pattern "
            "data.\n\n"
            "Steps\n"
            "  1.  Select a pattern directory (or single CSV).\n"
            "  2.  Choose a preset:\n"
            "       • Default — recommended sections enabled.\n"
            "       • Full — every section enabled.\n"
            "       • Minimal — summary + basic per-freq only.\n"
            "       • Quick — global pages only, no per-freq detail.\n"
            "  3.  Toggle individual sections on/off as desired.\n"
            "  4.  Set author name, notes, and format (PDF / LaTeX).\n"
            "  5.  Click Generate Report.\n\n"
            "Global sections: Cover Page, Table of Contents, Summary "
            "Table, Gain vs Freq, BW vs Freq, Overlay Cuts.\n"
            "Per-freq sections: Heatmap + Cuts, Polar, 3-D Surface, "
            "Statistics, Detailed Analysis, Sidelobe Detail.\n"
            "Options: Cross-pol inclusion, dynamic range, polar range, "
            "extra cut angles."
        ))

    def _section_settings(self) -> None:
        self._add_card("🔧  Settings — Configuration & Batch", (
            "Appearance\n"
            "  • Switch between Dark, Light, and System themes.\n"
            "  • Custom colour accent picker available.\n\n"
            "Configuration Files\n"
            "  • Load a previously saved JSON config to restore all "
            "Generate-page parameters.\n"
            "  • Save Current Config writes the active Generate "
            "settings to a JSON file.\n\n"
            "Batch Processing\n"
            "  • Load a batch-recipe JSON (multiple configs).\n"
            "  • Run Batch processes all configs sequentially.\n"
            "  • Dry Run validates without generating.\n"
            "  • Sample Recipe creates a starter JSON template.\n\n"
            "Current Defaults\n"
            "  • View the built-in DEFAULT_CONFIG dictionary."
        ))

    def _section_tips(self) -> None:
        self._add_card("💡  Tips & Tricks", (
            "• Hover over any widget label to see a tooltip.\n"
            "• Beamwidth sliders and entry boxes stay in sync — "
            "use whichever is faster.\n"
            "• The Visualize page detects previously generated PNGs "
            "so you don't re-render unnecessarily.\n"
            "• Use directory mode in Visualize to batch-plot every "
            "CSV in a folder.\n"
            "• The ◀ / ▶ arrows let you flip through all generated "
            "plots without leaving the app.\n"
            "• Check sidelobe compliance before submitting coordination "
            "filings — saves review cycles.\n"
            "• Press Ctrl+Q or close the window to exit."
        ))
