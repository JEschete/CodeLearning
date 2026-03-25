"""
Settings Page \u2014 Appearance, colour customization, config I/O.
"""

import os, json, copy
import customtkinter as ctk

from gui.theme import (
    COLORS, FONTS, CARD_PAD,
    get_default_colors, apply_color_overrides, reset_colors,
    apply_font_overrides, reset_fonts, _current_font_params,
    _DEFAULT_FONT_FAMILY, _DEFAULT_MONO_FAMILY, _DEFAULT_FONT_SIZE,
)
from gui.widgets import (
    ScrollablePage, Card, SectionHeading, ActionButton,
    LabeledEntry, LabeledOption, LabeledSwitch, FilePicker, ResultBox,
    Tooltip,
)
from gui.user_prefs import load_prefs, save_prefs

# Friendly names grouped logically — order matters for the UI.
_COLOR_GROUPS = [
    ("Sidebar", [
        ("sidebar_bg",       "Background"),
        ("sidebar_hover",    "Hover"),
        ("sidebar_active",   "Active / Accent"),
        ("sidebar_text",     "Text"),
        ("sidebar_text_act", "Active text"),
    ]),
    ("Main area", [
        ("bg",             "Background"),
        ("surface",        "Surface"),
        ("surface_hover",  "Surface hover"),
        ("card",           "Card"),
        ("card_border",    "Card border"),
    ]),
    ("Text", [
        ("text_primary",   "Primary"),
        ("text_secondary", "Secondary"),
        ("text_muted",     "Muted"),
    ]),
    ("Accent / Brand", [
        ("accent",        "Accent"),
        ("accent_hover",  "Accent hover"),
        ("accent_light",  "Accent light"),
    ]),
    ("Status", [
        ("success", "Success"),
        ("warning", "Warning"),
        ("error",   "Error"),
        ("info",    "Info"),
    ]),
    ("Inputs", [
        ("entry_bg",     "Entry background"),
        ("entry_border", "Entry border"),
        ("entry_focus",  "Entry focus"),
    ]),
]


class SettingsPage(ScrollablePage):
    """Settings page for appearance, fonts, colours, and config files."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._color_entries: dict[str, dict] = {}   # key → {"light": Entry, "dark": Entry, "swatch": Frame}
        self._build()

    def _build(self) -> None:
        SectionHeading(self, text="Settings").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self, text="Appearance, colour customization, and configuration files.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # ── Theme selector ──────────────────────────────────────
        theme_card = Card(self, title="Appearance")
        theme_card.pack(fill="x", padx=24, pady=8)

        t_inner = ctk.CTkFrame(theme_card, fg_color="transparent")
        t_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        prefs = load_prefs()
        saved_theme = prefs.get("theme", "dark")

        self.w_theme = LabeledOption(
            t_inner, "Colour Theme",
            ["dark", "light", "system"],
            default=saved_theme,
            command=self._on_theme_change,
        )
        self.w_theme.pack(fill="x", pady=4)

        # -- Font selection -----------------------------------------------
        # Gather system fonts (plus sensible fallbacks)
        try:
            import tkinter.font as tkfont
            _all = sorted(set(tkfont.families()), key=str.lower)
        except Exception:
            _all = ["Segoe UI", "Arial", "Helvetica", "Consolas", "Courier New"]

        # ── Professional sans-serif fonts ──
        _curated_sans = [
            "Segoe UI", "Arial", "Calibri", "Helvetica", "Verdana",
            "Tahoma", "Trebuchet MS", "Inter", "Roboto", "Open Sans",
            "Noto Sans", "Lato", "Source Sans Pro", "Candara",
            "Century Gothic", "Franklin Gothic Medium", "Gill Sans MT",
            "Lucida Sans Unicode", "Palatino Linotype",
            "Book Antiqua", "Garamond", "Georgia", "Cambria",
            "Times New Roman", "Constantia", "Corbel",
            # ── Decorative / display / fun fonts ──
            "Comic Sans MS", "Papyrus", "Impact", "Bauhaus 93",
            "Broadway", "Cooper Black", "Stencil", "Harlow Solid Italic",
            "Jokerman", "Chiller", "Showcard Gothic",
            "Snap ITC", "Juice ITC", "Ravie", "Playbill",
            "Elephant", "Forte", "Niagara Solid", "Niagara Engraved",
            "Old English Text MT", "Algerian", "Berlin Sans FB Demi",
            "Blackadder ITC", "Castellar", "Colonna MT",
            "Curlz MT", "Edwardian Script ITC", "Engravers MT",
            "Felix Titling", "French Script MT", "Gigi",
            "Haettenschweiler", "Harrington", "High Tower Text",
            "Informal Roman", "Kunstler Script", "Lucida Calligraphy",
            "Lucida Handwriting", "Magneto", "Matura MT Script Capitals",
            "Mistral", "Modern No. 20", "Onyx", "Palace Script MT",
            "Parchment", "Perpetua Titling MT", "Poor Richard",
            "Pristina", "Rage Italic", "Rockwell", "Script MT Bold",
            "Vladimir Script", "Wide Latin", "Wingdings",
            # ── Extra goodies (Linux / macOS common) ──
            "Ubuntu", "Cantarell", "DejaVu Sans", "Liberation Sans",
            "Noto Serif", "PT Sans", "Droid Sans",
            "Futura", "Avenir", "Optima", "Didot", "Copperplate",
            "American Typewriter", "Marker Felt", "Chalkboard",
            "Trattatello", "Zapfino", "Brush Script MT",
        ]

        # ── Monospace fonts ──
        _curated_mono = [
            "Consolas", "Courier New", "Cascadia Code", "Cascadia Mono",
            "JetBrains Mono", "Fira Code", "Source Code Pro", "Menlo",
            "DejaVu Sans Mono", "Lucida Console",
            "Monaco", "Andale Mono", "Ubuntu Mono", "Liberation Mono",
            "Noto Sans Mono", "Droid Sans Mono", "IBM Plex Mono",
            "Hack", "Inconsolata", "Victor Mono", "Anonymous Pro",
            "OCR A Extended", "Terminal",
        ]
        sans_choices = [f for f in _curated_sans if f in _all]
        mono_choices = [f for f in _curated_mono if f in _all]
        if not sans_choices:
            sans_choices = _all[:30]
        if not mono_choices:
            mono_choices = [f for f in _all if "mono" in f.lower() or "console" in f.lower() or "courier" in f.lower()][:10]

        fp = _current_font_params()

        self.w_font_family = LabeledOption(
            t_inner, "UI Font Family", sans_choices,
            default=fp["family"] if fp["family"] in sans_choices else sans_choices[0],
        )
        self.w_font_family.pack(fill="x", pady=4)

        self.w_font_mono = LabeledOption(
            t_inner, "Mono Font Family", mono_choices,
            default=fp["mono"] if fp["mono"] in mono_choices else mono_choices[0],
        )
        self.w_font_mono.pack(fill="x", pady=4)

        size_choices = ["9", "10", "11", "12", "13", "14", "15", "16"]
        self.w_font_size = LabeledOption(
            t_inner, "Base Font Size", size_choices,
            default=str(fp["base"]) if str(fp["base"]) in size_choices else "12",
        )
        self.w_font_size.pack(fill="x", pady=4)

        font_btn_row = ctk.CTkFrame(t_inner, fg_color="transparent")
        font_btn_row.pack(fill="x", pady=(8, 4))

        ActionButton(
            font_btn_row, text="✏  Apply Fonts", width=160,
            command=self._on_apply_fonts,
        ).pack(side="left")

        ActionButton(
            font_btn_row, text="🔄  Reset Fonts", width=160,
            style="secondary", command=self._on_reset_fonts,
        ).pack(side="left", padx=(12, 0))

        # ── Per-colour editors ──────────────────────────────────
        color_card = Card(self, title="Colour Customization")
        color_card.pack(fill="x", padx=24, pady=8)

        cc_inner = ctk.CTkFrame(color_card, fg_color="transparent")
        cc_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        ctk.CTkLabel(
            cc_inner,
            text="Each colour has a Light-mode and Dark-mode hex value.  "
                 "Edit any cell, then click Apply Colours.",
            font=FONTS["small"], text_color=COLORS["text_muted"],
            wraplength=700, justify="left",
        ).pack(anchor="w", pady=(0, 8))

        for group_name, items in _COLOR_GROUPS:
            # Group heading
            ctk.CTkLabel(
                cc_inner, text=group_name, font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", pady=(10, 2))

            for key, label in items:
                row = ctk.CTkFrame(cc_inner, fg_color="transparent")
                row.pack(fill="x", pady=1)
                row.columnconfigure(1, weight=1)
                row.columnconfigure(3, weight=1)

                cur = COLORS.get(key, ("#000000", "#000000"))
                light_val = cur[0] if isinstance(cur, (list, tuple)) else cur
                dark_val  = cur[1] if isinstance(cur, (list, tuple)) else cur

                # Label
                ctk.CTkLabel(
                    row, text=label, font=FONTS["small"],
                    text_color=COLORS["text_secondary"],
                    width=130, anchor="w",
                ).grid(row=0, column=0, sticky="w")

                # Light entry
                lv = ctk.StringVar(value=light_val)
                le = ctk.CTkEntry(row, textvariable=lv, width=82,
                                  font=FONTS["mono"], height=26,
                                  fg_color=COLORS["entry_bg"],
                                  border_color=COLORS["entry_border"],
                                  text_color=COLORS["text_primary"])
                le.grid(row=0, column=1, sticky="w", padx=(0, 4))

                ctk.CTkLabel(row, text="L", font=FONTS["tiny"],
                             text_color=COLORS["text_muted"], width=12
                ).grid(row=0, column=2)

                # Dark entry
                dv = ctk.StringVar(value=dark_val)
                de = ctk.CTkEntry(row, textvariable=dv, width=82,
                                  font=FONTS["mono"], height=26,
                                  fg_color=COLORS["entry_bg"],
                                  border_color=COLORS["entry_border"],
                                  text_color=COLORS["text_primary"])
                de.grid(row=0, column=3, sticky="w", padx=(4, 4))

                ctk.CTkLabel(row, text="D", font=FONTS["tiny"],
                             text_color=COLORS["text_muted"], width=12
                ).grid(row=0, column=4)

                # Swatch (shows dark colour)
                sw = ctk.CTkFrame(row, width=22, height=22,
                                  corner_radius=4, fg_color=dark_val)
                sw.grid(row=0, column=5, padx=(4, 0))

                # Bind live swatch preview
                def _preview(_, v=dv, s=sw):
                    c = v.get().strip()
                    if c.startswith("#") and len(c) in (4, 7):
                        try:
                            s.configure(fg_color=c)
                        except Exception:
                            pass
                de.bind("<KeyRelease>", _preview)

                self._color_entries[key] = {
                    "light_var": lv, "dark_var": dv, "swatch": sw,
                }

        # Buttons row
        btn_row = ctk.CTkFrame(cc_inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(12, 4))

        ActionButton(
            btn_row, text="🎨  Apply Colours", width=180,
            command=self._on_apply_all_colors,
        ).pack(side="left")

        ActionButton(
            btn_row, text="🔄  Reset to Defaults", width=180,
            style="secondary", command=self._on_reset_colors,
        ).pack(side="left", padx=(12, 0))

        ActionButton(
            btn_row, text="📋  Export Theme JSON", width=180,
            style="secondary", command=self._on_export_theme,
        ).pack(side="left", padx=(12, 0))

        ActionButton(
            btn_row, text="📂  Import Theme JSON", width=180,
            style="secondary", command=self._on_import_theme,
        ).pack(side="left", padx=(12, 0))

        self.color_result = ResultBox(self, height=60)
        self.color_result.pack(fill="x", padx=24, pady=(0, 8))

        # ── Config file I/O ─────────────────────────────────────
        cfg_io = Card(self, title="Configuration Files")
        cfg_io.pack(fill="x", padx=24, pady=8)

        c_inner = ctk.CTkFrame(cfg_io, fg_color="transparent")
        c_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_cfg_load = FilePicker(
            c_inner, "Load Config JSON",
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
        )
        self.w_cfg_load.pack(fill="x", pady=4)

        btn_row = ctk.CTkFrame(c_inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(8, 4))

        ActionButton(
            btn_row, text="📂  Load Config", width=160,
            command=self._on_load_config,
        ).pack(side="left")

        ActionButton(
            btn_row, text="💾  Save Current Config", width=200,
            style="secondary", command=self._on_save_config,
        ).pack(side="left", padx=(12, 0))

        self.cfg_result = ResultBox(self, height=200)
        self.cfg_result.pack(fill="x", padx=24, pady=(0, 16))

        # ── Current defaults view ───────────────────────────────
        defaults = Card(self, title="Current Default Configuration")
        defaults.pack(fill="x", padx=24, pady=8)

        d_inner = ctk.CTkFrame(defaults, fg_color="transparent")
        d_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        ActionButton(
            d_inner, text="Show Defaults", width=160,
            style="secondary", command=self._on_show_defaults,
        ).pack(anchor="w", pady=(4, 8))

        self.defaults_result = ResultBox(self, height=300)
        self.defaults_result.pack(fill="x", padx=24, pady=(0, 24))

        # ── Tooltips ───────────────────────────────────────────
        Tooltip(self.w_theme,
                "Switch between dark, light, or system-follow colour mode")
        Tooltip(self.w_font_family,
                "Main UI typeface — applies to labels, buttons, and headings")
        Tooltip(self.w_font_mono,
                "Monospaced typeface used in result boxes and code output")
        Tooltip(self.w_font_size,
                "Base font size in points — all other sizes scale from this")
        Tooltip(self.w_cfg_load,
                "Select a previously saved JSON configuration file to reload")


    # ────────────────────────────────────────────────────────────
    #  THEME
    # ────────────────────────────────────────────────────────────
    def _on_theme_change(self, value) -> None:
        ctk.set_appearance_mode(value)
        # Persist
        prefs = load_prefs()
        prefs["theme"] = value
        save_prefs(prefs)
        # Rebuild everything (sidebar + all pages including this one)
        self.app.rebuild_all("settings")

    # ────────────────────────────────────────────────────────────
    #  FONT CUSTOMIZATION
    # ────────────────────────────────────────────────────────────
    def _on_apply_fonts(self) -> None:
        family = self.w_font_family.get()
        mono   = self.w_font_mono.get()
        base   = int(self.w_font_size.get())
        apply_font_overrides(family=family, mono=mono, base=base)
        # Persist
        prefs = load_prefs()
        prefs["fonts"] = {"family": family, "mono": mono, "base": base}
        save_prefs(prefs)
        self.app.rebuild_all("settings")

    def _on_reset_fonts(self) -> None:
        reset_fonts()
        prefs = load_prefs()
        prefs.pop("fonts", None)
        save_prefs(prefs)
        self.app.rebuild_all("settings")

    # ────────────────────────────────────────────────────────────
    #  COLOUR CUSTOMIZATION
    # ────────────────────────────────────────────────────────────
    def _read_color_entries(self) -> dict:
        """Read all colour entries and return {key: (light, dark)}."""
        result = {}
        for key, widgets in self._color_entries.items():
            lv = widgets["light_var"].get().strip()
            dv = widgets["dark_var"].get().strip()
            if lv and dv:
                result[key] = (lv, dv)
        return result

    def _on_apply_all_colors(self) -> None:
        overrides = self._read_color_entries()
        apply_color_overrides(overrides)
        # Persist
        prefs = load_prefs()
        prefs["colors"] = {k: list(v) for k, v in overrides.items()}
        save_prefs(prefs)
        # Rebuild everything (sidebar + all pages including settings)
        self.app.rebuild_all("settings")

    def _on_reset_colors(self) -> None:
        reset_colors()
        prefs = load_prefs()
        prefs.pop("colors", None)
        save_prefs(prefs)
        # Rebuild everything with defaults
        self.app.rebuild_all("settings")

    def _on_export_theme(self) -> None:
        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(
            title="Export Theme",
            filetypes=[("JSON", "*.json")],
            defaultextension=".json",
            initialfile="antennaforge_theme.json",
        )
        if not path:
            return
        data = self._read_color_entries()
        serial = {k: list(v) for k, v in data.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serial, f, indent=2)
        self.color_result.set_text(f"Theme exported to:\n{path}")
        self.app.status.success("Theme exported")

    def _on_import_theme(self) -> None:
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            title="Import Theme",
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Populate entries
            for key, val in data.items():
                if key in self._color_entries:
                    if isinstance(val, (list, tuple)) and len(val) == 2:
                        self._color_entries[key]["light_var"].set(val[0])
                        self._color_entries[key]["dark_var"].set(val[1])
                        try:
                            self._color_entries[key]["swatch"].configure(fg_color=val[1])
                        except Exception:
                            pass
            self.color_result.set_text(
                f"Imported theme from:\n{path}\n"
                "Click 'Apply Colours' to activate and save.")
            self.app.status.success("Theme imported — click Apply")
        except Exception as e:
            self.color_result.set_text(f"Error importing theme: {e}")
            self.app.status.error(str(e))

    def _on_load_config(self) -> None:
        path = self.w_cfg_load.get()
        if not path:
            self.cfg_result.set_text("Select a JSON config file to load.")
            return
        try:
            from config import load_config
            cfg = load_config(path)
            text = json.dumps(cfg, indent=2, default=str)
            self.cfg_result.set_text(f"Loaded: {path}\n\n{text}")
            self.app.status.success("Config loaded")
        except Exception as e:
            self.cfg_result.set_text(f"Error loading config: {e}")
            self.app.status.error(str(e))

    def _on_save_config(self) -> None:
        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(
            title="Save Config As",
            filetypes=[("JSON", "*.json")],
            defaultextension=".json",
        )
        if not path:
            return
        try:
            # Get config from Generate page if it exists
            gen_page = self.app._pages.get("generate")
            if gen_page and hasattr(gen_page, "_build_config"):
                cfg = gen_page._build_config()
            else:
                from config import DEFAULT_CONFIG
                cfg = copy.deepcopy(DEFAULT_CONFIG)

            from config import save_config
            save_config(cfg, path)
            self.cfg_result.set_text(f"Config saved to:\n{path}")
            self.app.status.success("Config saved")
        except Exception as e:
            self.cfg_result.set_text(f"Error: {e}")
            self.app.status.error(str(e))

    def _on_show_defaults(self) -> None:
        try:
            from config import DEFAULT_CONFIG
            text = json.dumps(DEFAULT_CONFIG, indent=2, default=str)
            self.defaults_result.set_text(text)
        except Exception as e:
            self.defaults_result.set_text(f"Error: {e}")
