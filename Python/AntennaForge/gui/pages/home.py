"""Home / Dashboard page."""

import customtkinter as ctk
from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import ScrollablePage, Card, SectionHeading, ActionButton, Tooltip


class HomePage(ScrollablePage):
    """Dashboard landing page with quick-start actions."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._build()

    def _build(self) -> None:
        # ── Hero / Welcome ──────────────────────────────────────
        hero = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"],
                            corner_radius=12)
        hero.pack(fill="x", padx=24, pady=(24, 16))

        ctk.CTkLabel(
            hero, text="📡  AntennaForge",
            font=FONTS["heading"],
            text_color=COLORS["sidebar_text_act"],
        ).pack(padx=24, pady=(24, 4))

        ctk.CTkLabel(
            hero, text="Generate, visualise, and analyse idealised antenna radiation patterns",
            font=FONTS["body"],
            text_color=COLORS["sidebar_text"],
        ).pack(padx=24, pady=(0, 24))

        # ── Quick-action cards ──────────────────────────────────
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=24, pady=8)
        actions_frame.columnconfigure((0, 1, 2, 3), weight=1)

        quick_actions = [
            ("📡", "Generate\nPatterns",    "generate",
             "Create antenna pattern CSVs",
             "Open the pattern generation wizard — choose antenna type, beamwidth, "
             "frequency range, and physics features"),
            ("📊", "Visualize\nPatterns",   "visualize",
             "Heatmaps, cuts, polar & 3D",
             "Plot antenna patterns as heatmaps, principal-plane cuts, polar, "
             "or 3-D surface views"),
            ("🔍", "Analyze\nPatterns",     "analysis",
             "Beamwidth, sidelobes, symmetry",
             "Compute beamwidth, F/B ratio, sidelobe levels, and run mask "
             "compliance tests"),
            ("📄", "Generate\nReports",     "reports",
             "PDF and LaTeX reports",
             "Create professional multi-section PDF or LaTeX reports from "
             "pattern data"),
        ]

        for col, (icon, title, page, desc, tip) in enumerate(quick_actions):
            card = Card(actions_frame)
            card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")

            ctk.CTkLabel(
                card, text=icon, font=("Segoe UI Symbol", 32),
                text_color=COLORS["accent"],
            ).pack(pady=(CARD_PAD, 4))

            ctk.CTkLabel(
                card, text=title, font=FONTS["body_bold"],
                text_color=COLORS["text_primary"], justify="center",
            ).pack(pady=4)

            ctk.CTkLabel(
                card, text=desc, font=FONTS["small"],
                text_color=COLORS["text_muted"], justify="center",
                wraplength=160,
            ).pack(pady=(0, 8))

            btn = ActionButton(
                card, text="Open →", width=120,
                command=lambda p=page: self.app.show_page(p),
            )
            btn.pack(pady=(4, CARD_PAD))
            Tooltip(btn, tip)

        # ── Second row of tools  ────────────────────────────────
        tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        tools_frame.pack(fill="x", padx=24, pady=8)
        tools_frame.columnconfigure((0, 1, 2, 3), weight=1)

        tools = [
            ("⚙", "Pattern Ops", "operations", "Math, rotation, interpolation",
             "Combine, rotate, or interpolate antenna patterns"),
            ("📐", "RF Calculations", "rf_calc", "EIRP & link budget",
             "Compute EIRP, path loss, power density, and link budgets"),
            ("🔧", "Settings", "settings", "Configure defaults",
             "Fonts, colours, theme, config files, and batch processing"),
        ]

        for col, (icon, title, page, desc, tip) in enumerate(tools):
            card = Card(tools_frame)
            card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=CARD_PAD, pady=CARD_PAD)

            ctk.CTkLabel(
                inner, text=f"{icon}  {title}",
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"], anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner, text=desc, font=FONTS["small"],
                text_color=COLORS["text_muted"], anchor="w",
            ).pack(anchor="w", pady=(2, 8))

            btn = ActionButton(
                inner, text="Open", width=100, style="secondary",
                command=lambda p=page: self.app.show_page(p),
            )
            btn.pack(anchor="w")
            Tooltip(btn, tip)

        # ── Capabilities summary ────────────────────────────────
        info = Card(self, title="Capabilities")
        info.pack(fill="x", padx=24, pady=(16, 8))

        capabilities = [
            "7 antenna types: LPDA, Omni, Panel, Dish, Horn, Monopole, Phased Array",
            "Multi-frequency pattern generation with freq-dependent beamwidth",
            "Physics: Taylor sidelobes, ground reflection, cross-pol, VSWR rolloff",
            "Graphing: heatmaps, principal-plane cuts, polar, 3-D surface plots",
            "EIRP calculator, link budget analysis, sidelobe mask compliance",
            "PDF and LaTeX reports with 13 configurable sections",
            "Pattern arithmetic: add, subtract, max envelope, rotate, interpolate",
            "Batch mode with JSON recipe files for automated generation",
        ]

        for cap in capabilities:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=CARD_PAD, pady=2)
            ctk.CTkLabel(
                row, text="  •", font=FONTS["body"],
                text_color=COLORS["accent"], width=24, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=cap, font=FONTS["body"],
                text_color=COLORS["text_secondary"], anchor="w",
            ).pack(side="left", fill="x", expand=True)

        # ── Dependency Status ───────────────────────────────────
        dep_card = Card(self, title="Dependency Status")
        dep_card.pack(fill="x", padx=24, pady=(8, 24))

        try:
            from core.deps import check_all, _PACKAGES
            status = check_all()
        except ImportError:
            status = {}
            _PACKAGES = {}

        for name, available in status.items():
            row = ctk.CTkFrame(dep_card, fg_color="transparent")
            row.pack(fill="x", padx=CARD_PAD, pady=2)
            mark = "✓" if available else "✗"
            color = COLORS["success"] if available else COLORS["error"]
            desc = _PACKAGES.get(name, {}).get("required_for", "")
            ctk.CTkLabel(
                row, text=f"  {mark}", font=FONTS["body"],
                text_color=color, width=28, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f"{name}  —  {desc}", font=FONTS["body"],
                text_color=COLORS["text_secondary"] if available
                           else COLORS["error"], anchor="w",
            ).pack(side="left", fill="x", expand=True)

        if any(not v for v in status.values()):
            pip_row = ctk.CTkFrame(dep_card, fg_color="transparent")
            pip_row.pack(fill="x", padx=CARD_PAD, pady=(4, 8))
            missing = [_PACKAGES[n]["pip"] for n, v in status.items() if not v]
            ctk.CTkLabel(
                pip_row,
                text=f"Install missing: pip install {' '.join(missing)}",
                font=FONTS["mono"],
                text_color=COLORS["warning"],
            ).pack(anchor="w")

        # bottom padding
        ctk.CTkFrame(self, height=24, fg_color="transparent").pack()
