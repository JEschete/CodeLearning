"""
Reports Page — PDF and LaTeX report generation.
"""

import os, threading
from collections import OrderedDict
import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import (
    ScrollablePage, Card, SectionHeading, ActionButton,
    LabeledEntry, LabeledOption, LabeledSwitch, FilePicker, ResultBox,
    Tooltip,
)


class ReportsPage(ScrollablePage):
    """PDF and LaTeX report generation page with configurable sections."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._section_switches = {}
        self._build()

    def _build(self) -> None:
        SectionHeading(self, text="Generate Reports").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self,
            text="Create PDF or LaTeX reports from generated pattern directories.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # ── Input card ──────────────────────────────────────────
        inp = Card(self, title="Input")
        inp.pack(fill="x", padx=24, pady=8)

        i_inner = ctk.CTkFrame(inp, fg_color="transparent")
        i_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_input_dir = FilePicker(i_inner, "Pattern Directory",
                                      mode="directory")
        self.w_input_dir.pack(fill="x", pady=4)

        from core.deps import HAS_PPTX
        formats = ["PDF", "LaTeX (.tex)"]
        if HAS_PPTX:
            formats.insert(1, "PPTX")

        self.w_format = LabeledOption(
            i_inner, "Output Format",
            formats,
            default="PDF",
        )
        self.w_format.pack(fill="x", pady=4)

        self.w_title = LabeledEntry(i_inner, "Report Title", "",
                                    tooltip="Leave blank for auto-generated title")
        self.w_title.pack(fill="x", pady=4)

        # ── Preset card ─────────────────────────────────────────
        preset = Card(self, title="Presets")
        preset.pack(fill="x", padx=24, pady=8)

        p_inner = ctk.CTkFrame(preset, fg_color="transparent")
        p_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_preset = LabeledOption(
            p_inner, "Preset",
            ["default", "full", "minimal", "quick"],
            default="default",
            command=self._on_preset_change,
        )
        self.w_preset.pack(fill="x", pady=4)

        ctk.CTkLabel(
            p_inner,
            text="default: Standard report  |  full: All sections  |  "
                 "minimal: Just data  |  quick: Summary only",
            font=FONTS["tiny"], text_color=COLORS["text_muted"],
            wraplength=600, justify="left",
        ).pack(anchor="w", pady=(0, 4))

        # ── Section toggles ─────────────────────────────────────
        sec = Card(self, title="Report Sections")
        sec.pack(fill="x", padx=24, pady=8)

        s_inner = ctk.CTkFrame(sec, fg_color="transparent")
        s_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        # Get actual section names from the reporting module
        try:
            from reporting.report import REPORT_SECTIONS
            sections = REPORT_SECTIONS.copy()
        except Exception:
            sections = OrderedDict([
                ("cover_page",        (True,  "Cover Page",         "global")),
                ("table_of_contents", (True,  "Table of Contents",  "global")),
                ("summary_table",     (True,  "Summary Table",      "global")),
                ("gain_vs_freq",      (True,  "Gain vs Freq",       "global")),
                ("bw_vs_freq",        (True,  "BW vs Freq",         "global")),
                ("overlay_cuts",      (True,  "Overlay Cuts",       "global")),
                ("per_freq_heatmap",  (True,  "Per-freq Heatmap",   "per_freq")),
                ("per_freq_polar",    (True,  "Per-freq Polar",     "per_freq")),
                ("per_freq_3d",       (False, "Per-freq 3D Surface","per_freq")),
                ("per_freq_stats",    (True,  "Per-freq Statistics", "per_freq")),
                ("per_freq_detailed", (True,  "Per-freq Detailed",  "per_freq")),
                ("per_freq_sidelobe", (True,  "Per-freq Sidelobe",  "per_freq")),
                ("include_xpol",      (False, "Include Cross-Pol",  "option")),
            ])

        # Inject Generation Settings toggle if not present
        if "generation_config" not in sections:
            sections["generation_config"] = (True, "Generation Settings", "global")

        # Two columns of toggles
        left_col = ctk.CTkFrame(s_inner, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True)
        right_col = ctk.CTkFrame(s_inner, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)

        items = list(sections.items())
        mid = (len(items) + 1) // 2

        for i, (key, val) in enumerate(items):
            enabled, label, group = val[0], val[1], val[2]
            parent = left_col if i < mid else right_col
            sw = LabeledSwitch(parent, f"{label}  ({group})", default=enabled)
            sw.pack(fill="x", pady=2)
            self._section_switches[key] = sw

        # ── Options card ────────────────────────────────────────
        opts = Card(self, title="Report Options")
        opts.pack(fill="x", padx=24, pady=8)

        o_inner = ctk.CTkFrame(opts, fg_color="transparent")
        o_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_dyn_range = LabeledEntry(o_inner, "Dynamic Range (dB)", "60",
                                        tooltip="Heatmap colour range")
        self.w_dyn_range.pack(fill="x", pady=4)

        self.w_polar_range = LabeledEntry(o_inner, "Polar Range (dB)", "40",
                                          tooltip="Polar plot dB range")
        self.w_polar_range.pack(fill="x", pady=4)

        # ── Cover Page card ─────────────────────────────────────
        cover = Card(self, title="Cover Page Fields")
        cover.pack(fill="x", padx=24, pady=8)

        c_inner = ctk.CTkFrame(cover, fg_color="transparent")
        c_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        c_left = ctk.CTkFrame(c_inner, fg_color="transparent")
        c_left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        c_right = ctk.CTkFrame(c_inner, fg_color="transparent")
        c_right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self.w_cover_subtitle = LabeledEntry(
            c_left, "Subtitle", "Antenna Pattern Report",
            tooltip="Subtitle shown on the cover page")
        self.w_cover_subtitle.pack(fill="x", pady=2)

        self.w_cover_author = LabeledEntry(
            c_left, "Author", "",
            tooltip="Author name(s) for the cover page")
        self.w_cover_author.pack(fill="x", pady=2)

        self.w_cover_org = LabeledEntry(
            c_left, "Organisation", "",
            tooltip="Organisation or company name")
        self.w_cover_org.pack(fill="x", pady=2)

        self.w_cover_project = LabeledEntry(
            c_right, "Project", "",
            tooltip="Project name or identifier")
        self.w_cover_project.pack(fill="x", pady=2)

        self.w_cover_doc_id = LabeledEntry(
            c_right, "Document ID", "",
            tooltip="Document identifier or number")
        self.w_cover_doc_id.pack(fill="x", pady=2)

        self.w_cover_revision = LabeledEntry(
            c_right, "Revision", "",
            tooltip="Document revision (e.g. Rev A, v1.2)")
        self.w_cover_revision.pack(fill="x", pady=2)

        self.w_cover_date = LabeledEntry(
            c_right, "Date", "",
            tooltip="Cover date (leave blank for today)")
        self.w_cover_date.pack(fill="x", pady=2)

        # ── Classification card ─────────────────────────────────
        cls_card = Card(self, title="Classification Markings")
        cls_card.pack(fill="x", padx=24, pady=8)

        cl_inner = ctk.CTkFrame(cls_card, fg_color="transparent")
        cl_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        try:
            from reporting.report import CLASSIFICATION_LEVELS
            cls_levels = CLASSIFICATION_LEVELS
        except Exception:
            cls_levels = [
                "UNCLASSIFIED", "CUI", "CONFIDENTIAL",
                "SECRET", "TOP SECRET", "TOP SECRET//SCI",
            ]

        self.w_classification = LabeledOption(
            cl_inner, "Classification Level", cls_levels,
            default="UNCLASSIFIED",
        )
        self.w_classification.pack(fill="x", pady=4)

        self.w_cls_caveats = LabeledEntry(
            cl_inner, "Caveats / Releasability", "",
            tooltip="Extra caveats e.g. //NOFORN, //REL TO USA, GBR")
        self.w_cls_caveats.pack(fill="x", pady=4)

        ctk.CTkLabel(
            cl_inner,
            text="Classification banners appear on every page header/footer "
                 "and on every figure caption.",
            font=FONTS["tiny"], text_color=COLORS["text_muted"],
            wraplength=600, justify="left",
        ).pack(anchor="w", pady=(0, 4))

        # ── Generate button ─────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=16)

        self.btn_generate = ActionButton(
            btn_row, text="📄  Generate Report", width=220,
            style="success", command=self._on_generate,
        )
        self.btn_generate.pack(side="left")

        # ── Output log ──────────────────────────────────────────
        self.result = ResultBox(self, height=160)
        self.result.pack(fill="x", padx=24, pady=(0, 24))

        # ── Tooltips ───────────────────────────────────────────
        Tooltip(self.w_input_dir,
                "Folder containing generated antenna pattern CSVs")
        Tooltip(self.w_format,
                "PDF produces a ready-to-view document. "
                "LaTeX (.tex) outputs source you can customise and compile.")
        Tooltip(self.w_preset,
                "Quickly select which report sections to include: "
                "default, full (all), minimal (data only), or quick (summary)")

    # ────────────────────────────────────────────────────────────
    def _on_preset_change(self, preset_name) -> None:
        """Apply a preset to section toggles."""
        try:
            from reporting.report import PRESETS, REPORT_SECTIONS
            if preset_name in PRESETS:
                _, factory = PRESETS[preset_name]
                cfg = factory()
                for key, sw in self._section_switches.items():
                    sw.set(cfg.get(key, key == "generation_config"))
        except Exception:
            pass  # ignore if reporting module not available

    def _build_report_config(self) -> dict:
        """Assemble report config from GUI state."""
        try:
            from reporting.report import default_report_config
            cfg = default_report_config()
        except Exception:
            cfg = {}

        for key, sw in self._section_switches.items():
            cfg[key] = sw.get()

        cfg["dynamic_range_db"] = float(self.w_dyn_range.get())
        cfg["polar_range_db"] = float(self.w_polar_range.get())

        # Cover page fields
        cfg["cover_subtitle"] = self.w_cover_subtitle.get().strip()
        cfg["cover_author"] = self.w_cover_author.get().strip()
        cfg["cover_organisation"] = self.w_cover_org.get().strip()
        cfg["cover_project"] = self.w_cover_project.get().strip()
        cfg["cover_document_id"] = self.w_cover_doc_id.get().strip()
        cfg["cover_revision"] = self.w_cover_revision.get().strip()
        cfg["cover_date"] = self.w_cover_date.get().strip()

        # Classification
        cfg["classification"] = self.w_classification.get()
        cfg["classification_caveats"] = self.w_cls_caveats.get().strip()
        # figure_classification blank ⇒ inherits overall level
        cfg["figure_classification"] = ""

        return cfg

    def _on_generate(self) -> None:
        input_dir = self.w_input_dir.get()
        if not input_dir:
            self.result.set_text("Select a pattern directory first.")
            return

        self.btn_generate.configure(state="disabled")
        fmt = self.w_format.get()
        title = self.w_title.get().strip() or None
        report_cfg = self._build_report_config()

        self.app.status.busy(f"Generating {fmt} report…")
        title_display = title or "(auto from directory name)"
        self.result.set_text(
            f"Generating {fmt} from {input_dir}…\n"
            f"Title: {title_display}\n"
        )

        def work():
            try:
                if "PDF" in fmt:
                    from reporting.report import generate_report
                    out = generate_report(input_dir, title=title,
                                          report_cfg=report_cfg)
                elif "PPTX" in fmt:
                    from reporting.pptx_report import generate_pptx_report
                    out = generate_pptx_report(input_dir, title=title,
                                               report_cfg=report_cfg)
                else:
                    from reporting.latex_report import generate_latex_report
                    out = generate_latex_report(input_dir, title=title,
                                               report_cfg=report_cfg)

                if out:
                    text = f"Report generated:\n{out}"
                    self.after(0, lambda: self.result.set_text(text))
                    self.after(0, lambda: self.app.status.success("Report generated"))
                else:
                    self.after(0, lambda: self.result.set_text("Report generation returned None."))
                    self.after(0, lambda: self.app.status.error("Report failed"))

            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))
            finally:
                self.after(0, lambda: self.btn_generate.configure(state="normal"))

        threading.Thread(target=work, daemon=True).start()
