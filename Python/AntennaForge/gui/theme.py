"""
Theme constants and colour palette for the AntennaForge GUI.

Colour values are (light_mode, dark_mode) tuples so customtkinter
automatically switches when ``set_appearance_mode()`` is called.

User overrides are stored in antennaforge_prefs.json and merged
on startup via ``apply_saved_colors()``.
"""

import copy

# ── Default colour palette (light, dark) ───────────────────────
_DEFAULT_COLORS = {
    # Sidebar
    "sidebar_bg":       ("#E2E8F0", "#1B1F3B"),
    "sidebar_hover":    ("#CBD5E1", "#2A2F55"),
    "sidebar_active":   ("#3B82F6", "#3B82F6"),
    "sidebar_text":     ("#475569", "#A5B4FC"),
    "sidebar_text_act": ("#FFFFFF", "#FFFFFF"),

    # Main area
    "bg":               ("#F8FAFC", "#0F172A"),
    "surface":          ("#E2E8F0", "#1E293B"),
    "surface_hover":    ("#CBD5E1", "#334155"),
    "card":             ("#FFFFFF", "#1E293B"),
    "card_border":      ("#E2E8F0", "#334155"),

    # Text
    "text_primary":     ("#0F172A", "#F1F5F9"),
    "text_secondary":   ("#475569", "#94A3B8"),
    "text_muted":       ("#94A3B8", "#64748B"),

    # Accent / brand
    "accent":           ("#3B82F6", "#3B82F6"),
    "accent_hover":     ("#2563EB", "#2563EB"),
    "accent_light":     ("#DBEAFE", "#DBEAFE"),

    # Status
    "success":          ("#16A34A", "#22C55E"),
    "warning":          ("#D97706", "#F59E0B"),
    "error":            ("#DC2626", "#EF4444"),
    "info":             ("#0891B2", "#06B6D4"),

    # Inputs
    "entry_bg":         ("#F1F5F9", "#0F172A"),
    "entry_border":     ("#CBD5E1", "#334155"),
    "entry_focus":      ("#3B82F6", "#3B82F6"),
}

# ── Live mutable copy — all widgets read from this ─────────────
COLORS = copy.deepcopy(_DEFAULT_COLORS)


def get_default_colors() -> dict:
    """Return a fresh copy of the built-in defaults."""
    return copy.deepcopy(_DEFAULT_COLORS)


def apply_color_overrides(overrides: dict[str, tuple]) -> None:
    """Merge *overrides* into the global COLORS dict in-place.

    Each value should be a ``(light, dark)`` tuple or a single
    ``"#hex"`` string (applied to both modes).
    """
    for key, val in overrides.items():
        if key not in COLORS:
            continue
        if isinstance(val, str):
            COLORS[key] = (val, val)
        elif isinstance(val, (list, tuple)) and len(val) == 2:
            COLORS[key] = tuple(val)


def apply_saved_colors() -> None:
    """Load user colour prefs from disk and merge into COLORS."""
    try:
        from gui.user_prefs import load_prefs
        prefs = load_prefs()
        saved = prefs.get("colors", {})
        if saved:
            apply_color_overrides(saved)
    except Exception:
        pass


def reset_colors() -> None:
    """Restore all COLORS to built-in defaults (in-place)."""
    COLORS.clear()
    COLORS.update(copy.deepcopy(_DEFAULT_COLORS))

# ── Typography ──────────────────────────────────────────────────
_DEFAULT_FONT_FAMILY = "Segoe UI"
_DEFAULT_MONO_FAMILY = "Consolas"
_DEFAULT_ICON_FAMILY = "Segoe UI Symbol"
_DEFAULT_FONT_SIZE   = 12          # base size for "body"

def _build_fonts(family: str = _DEFAULT_FONT_FAMILY,
                 mono: str = _DEFAULT_MONO_FAMILY,
                 icon: str = _DEFAULT_ICON_FAMILY,
                 base: int = _DEFAULT_FONT_SIZE) -> dict:
    """Build the FONTS dict from a *family*, *mono* family, and *base* size."""
    return {
        "heading":      (family, base + 6, "bold"),
        "subheading":   (family, base + 2, "bold"),
        "body":         (family, base),
        "body_bold":    (family, base, "bold"),
        "small":        (family, base - 2),
        "tiny":         (family, base - 3),
        "mono":         (mono,   base - 1),
        "sidebar":      (family, base),
        "sidebar_bold": (family, base, "bold"),
        "icon":         (icon,   base + 4),
    }

FONTS: dict = _build_fonts()


def get_default_fonts() -> dict:
    """Return the factory-default FONTS dict."""
    return _build_fonts()


def apply_font_overrides(family: str | None = None,
                         mono: str | None = None,
                         base: int | None = None) -> None:
    """Rebuild FONTS in-place with the given overrides."""
    cur = _current_font_params()
    fam = family or cur["family"]
    mon = mono   or cur["mono"]
    bsz = base   if base is not None else cur["base"]
    FONTS.clear()
    FONTS.update(_build_fonts(fam, mon, base=bsz))


def apply_saved_fonts() -> None:
    """Load user font prefs from disk and merge into FONTS."""
    try:
        from gui.user_prefs import load_prefs
        prefs = load_prefs()
        fp = prefs.get("fonts", {})
        if fp:
            apply_font_overrides(
                family=fp.get("family"),
                mono=fp.get("mono"),
                base=fp.get("base"),
            )
    except Exception:
        pass


def reset_fonts() -> None:
    """Restore FONTS to built-in defaults (in-place)."""
    FONTS.clear()
    FONTS.update(_build_fonts())


def _current_font_params() -> dict:
    """Extract the current family / mono / base from FONTS."""
    body = FONTS.get("body", (_DEFAULT_FONT_FAMILY, _DEFAULT_FONT_SIZE))
    mono = FONTS.get("mono", (_DEFAULT_MONO_FAMILY, _DEFAULT_FONT_SIZE - 1))
    return {
        "family": body[0],
        "mono":   mono[0],
        "base":   body[1] if len(body) >= 2 else _DEFAULT_FONT_SIZE,
    }

# ── Sizes ───────────────────────────────────────────────────────
SIDEBAR_WIDTH   = 220
CARD_CORNER     = 10
CARD_PAD        = 16
ENTRY_HEIGHT    = 36
BTN_HEIGHT      = 38
BTN_CORNER      = 8
SCROLLBAR_WIDTH = 12

# ── Sidebar items (label, icon, page_key) ──────────────────────
SIDEBAR_ITEMS = [
    ("Home",        "🏠",  "home"),
    ("Parametric",  "📡",  "generate"),
    ("Geometry",    "🔬",  "physics_antennas"),
    ("Visualize",   "📊",  "visualize"),
    ("Analysis",    "🔍",  "analysis"),
    ("Operations",  "⚙",   "operations"),
    ("RF Calcs",    "📐",  "rf_calc"),
    ("Reports",     "📄",  "reports"),
    ("How To",      "❓",  "howto"),
    ("Settings",    "🔧",  "settings"),
]
