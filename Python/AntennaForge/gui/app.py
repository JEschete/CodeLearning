"""
AntennaForge — Main GUI Application

Modern sidebar-based navigation.  Each page swaps in-place in the
content area without opening new windows.
"""

import sys, os
import customtkinter as ctk

# Ensure package root is importable — works whether launched from anywhere
_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)
# Also add the parent so 'antenna_tool.xxx' style imports work
_parent = os.path.dirname(_pkg_root)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from gui.theme import COLORS, FONTS, SIDEBAR_WIDTH, SIDEBAR_ITEMS, apply_saved_colors, apply_saved_fonts
from gui.widgets import StatusBar, ScrollablePage, Tooltip

# Sidebar tooltip descriptions (keyed by page name)
_SIDEBAR_TIPS: dict[str, str] = {
    "home":       "Dashboard — quick links and dependency status",
    "generate":   "Parametric pattern generation (single or batch)",
    "visualize":  "Plot heatmaps, cuts, polar, and 3-D surface views",
    "analysis":   "Beamwidth, sidelobes, comparison, mask compliance",
    "operations": "Pattern arithmetic, rotation, and interpolation",
    "rf_calc":    "EIRP, FSPL, power density, link budget",
    "reports":    "Create PDF or LaTeX reports from pattern data",
    "howto":      "Built-in user guide and workflow tips",
    "settings":   "Fonts, colours, theme, config files",
    "physics_antennas": "Geometry-driven antenna design (LPDA)",
}


class App(ctk.CTk):
    """Root window — sidebar + stacked content area."""

    def __init__(self) -> None:
        super().__init__()

        # ── Load persistent user prefs ──────────────────────────
        apply_saved_colors()
        apply_saved_fonts()

        try:
            from gui.user_prefs import load_prefs
            _prefs = load_prefs()
            _saved_theme = _prefs.get("theme", "dark")
        except Exception:
            _saved_theme = "dark"

        # ── Window setup ────────────────────────────────────────
        self.title("AntennaForge v1.0")
        self.geometry("1280x820")
        self.minsize(1024, 680)
        ctk.set_appearance_mode(_saved_theme)
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["bg"])

        # ── Layout grid ─────────────────────────────────────────
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ─────────────────────────────────────────────
        self._build_sidebar()

        # ── Content container ───────────────────────────────────
        self._content = ctk.CTkFrame(self, fg_color=COLORS["bg"],
                                     corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        # ── Status bar ──────────────────────────────────────────
        self.status = StatusBar(self)
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew")

        # ── Page cache ──────────────────────────────────────────
        self._pages: dict[str, ctk.CTkBaseClass] = {}
        self._current_page: str = ""

        # ── Load pages lazily ───────────────────────────────────
        self.show_page("home")

    # ────────────────────────────────────────────────────────────
    #  SIDEBAR
    # ────────────────────────────────────────────────────────────
    def _build_sidebar(self) -> None:
        self._sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_WIDTH,
            fg_color=COLORS["sidebar_bg"], corner_radius=0,
        )
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self._sidebar.grid_propagate(False)

        # Logo area
        logo = ctk.CTkLabel(
            self._sidebar, text="📡  AntennaForge",
            font=FONTS["subheading"],
            text_color=COLORS["sidebar_text_act"],
        )
        logo.pack(pady=(20, 24), padx=12)
        sep = ctk.CTkFrame(self._sidebar, height=1, fg_color=COLORS["sidebar_hover"])
        sep.pack(fill="x", padx=16, pady=(0, 12))

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for label, icon, key in SIDEBAR_ITEMS:
            btn = ctk.CTkButton(
                self._sidebar,
                text=f" {icon}  {label}",
                font=FONTS["sidebar"],
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_buttons[key] = btn
            tip = _SIDEBAR_TIPS.get(key)
            if tip:
                Tooltip(btn, tip)

        # Version label at bottom
        ver = ctk.CTkLabel(
            self._sidebar, text="v1.0", font=FONTS["tiny"],
            text_color=COLORS["text_muted"],
        )
        ver.pack(side="bottom", pady=10)

    def rebuild_sidebar(self) -> None:
        """Destroy and recreate the sidebar with current COLORS."""
        if hasattr(self, "_sidebar") and self._sidebar.winfo_exists():
            self._sidebar.destroy()
        self._build_sidebar()
        # Re-highlight the active page
        if self._current_page:
            for k, btn in self._nav_buttons.items():
                if k == self._current_page:
                    btn.configure(
                        fg_color=COLORS["sidebar_active"],
                        text_color=COLORS["sidebar_text_act"],
                    )

    def rebuild_all(self, return_to: str = "settings"):
        """Rebuild sidebar + all pages, then navigate to *return_to*.

        Called by the Settings page after colour changes so every
        widget picks up the new COLORS values.
        """
        # Destroy all cached pages
        for k in list(self._pages):
            self._pages[k].destroy()
        self._pages.clear()

        # Rebuild sidebar
        self.rebuild_sidebar()

        # Update root background
        self.configure(fg_color=COLORS["bg"])
        self._content.configure(fg_color=COLORS["bg"])

        # Re-show the requested page (it will be lazily created)
        self._current_page = ""
        self.show_page(return_to)

    # ────────────────────────────────────────────────────────────
    #  PAGE MANAGEMENT
    # ────────────────────────────────────────────────────────────
    def show_page(self, key: str):
        """Switch to the given page (create lazily on first visit)."""
        if key == self._current_page:
            return

        # Highlight sidebar
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color=COLORS["sidebar_text_act"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["sidebar_text"],
                )

        # Hide current
        if self._current_page and self._current_page in self._pages:
            self._pages[self._current_page].grid_forget()

        # Create page if needed
        if key not in self._pages:
            self._pages[key] = self._create_page(key)

        # Show
        self._pages[key].grid(row=0, column=0, sticky="nsew")
        self._current_page = key

    def _create_page(self, key: str) -> ctk.CTkBaseClass:
        """Lazy-import and instantiate the page widget."""
        if key == "home":
            from gui.pages.home import HomePage
            return HomePage(self._content, self)
        elif key == "generate":
            from gui.pages.generate import GeneratePage
            return GeneratePage(self._content, self)
        elif key == "visualize":
            from gui.pages.visualize import VisualizePage
            return VisualizePage(self._content, self)
        elif key == "analysis":
            from gui.pages.analysis import AnalysisPage
            return AnalysisPage(self._content, self)
        elif key == "operations":
            from gui.pages.operations import OperationsPage
            return OperationsPage(self._content, self)
        elif key == "rf_calc":
            from gui.pages.rf_calc import RFCalcPage
            return RFCalcPage(self._content, self)
        elif key == "reports":
            from gui.pages.reports import ReportsPage
            return ReportsPage(self._content, self)
        elif key == "settings":
            from gui.pages.settings import SettingsPage
            return SettingsPage(self._content, self)
        elif key == "physics_antennas":
            from gui.pages.physics_antennas import PhysicsAntennasPage
            return PhysicsAntennasPage(self._content, self)
        elif key == "howto":
            from gui.pages.howto import HowToPage
            return HowToPage(self._content, self)
        else:
            # Fallback placeholder
            f = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
            ctk.CTkLabel(f, text=f"Page: {key}", font=FONTS["heading"],
                         text_color=COLORS["text_primary"]).pack(pady=40)
            return f


# ════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════

def launch() -> None:
    """Launch the GUI application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    launch()
