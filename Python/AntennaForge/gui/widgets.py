"""
Reusable custom widgets for the AntennaForge GUI.

All widgets use customtkinter as the base and the project theme
for consistent styling.
"""

import customtkinter as ctk
from gui.theme import COLORS, FONTS, CARD_CORNER, CARD_PAD


# ════════════════════════════════════════════════════════════════
#  TOOLTIP (hover popup)
# ════════════════════════════════════════════════════════════════

class Tooltip:
    """Hover tooltip for any widget.  Attach with ``Tooltip(widget, text)``."""

    _DELAY_MS = 400        # ms before tooltip appears
    _WRAP_LENGTH = 280     # pixel wrap for long text
    _OFFSET_X = 12         # horizontal offset from pointer
    _OFFSET_Y = 16         # vertical offset from pointer
    _AUTO_HIDE_MS = 5000   # auto-dismiss if tooltip lingers (safety net)

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._tw = None
        self._after_id = None
        self._auto_hide_id = None
        self._pointer_x = 0
        self._pointer_y = 0
        # Bind to the label sub-widget if this is a compound widget
        # (LabeledEntry, LabeledOption, FilePicker, etc.) so the
        # detection zone covers the label text, not the full frame.
        target = getattr(widget, '_label', widget)
        self._target = target
        target.bind("<Enter>", self._schedule, add="+")
        target.bind("<Leave>", self._hide, add="+")
        target.bind("<Motion>", self._track, add="+")
        target.bind("<ButtonPress>", self._hide, add="+")

    # Allow changing text after creation
    def update_text(self, text: str) -> None:
        self._text = text

    def _track(self, event) -> None:
        """Track the mouse pointer so the tooltip appears near it."""
        self._pointer_x = event.x_root
        self._pointer_y = event.y_root

    def _schedule(self, event=None) -> None:
        self._cancel()
        if event:
            self._pointer_x = event.x_root
            self._pointer_y = event.y_root
        self._after_id = self._widget.after(self._DELAY_MS, self._show)

    def _cancel(self) -> None:
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self) -> None:
        if self._tw or not self._text:
            return
        x = self._pointer_x + self._OFFSET_X
        y = self._pointer_y + self._OFFSET_Y
        self._tw = tw = ctk.CTkToplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        # Build content first so we can measure it
        frm = ctk.CTkFrame(tw, fg_color=COLORS["surface"],
                           corner_radius=6, border_width=1,
                           border_color=COLORS["card_border"])
        frm.pack()
        lbl = ctk.CTkLabel(frm, text=self._text, font=FONTS["small"],
                           text_color=COLORS["text_primary"],
                           wraplength=self._WRAP_LENGTH, justify="left")
        lbl.pack(padx=8, pady=4)
        tw.update_idletasks()  # force geometry calculation
        # Clamp to screen edges
        tw_w = tw.winfo_reqwidth()
        tw_h = tw.winfo_reqheight()
        scr_w = tw.winfo_screenwidth()
        scr_h = tw.winfo_screenheight()
        if x + tw_w > scr_w - 8:
            x = self._pointer_x - tw_w - 4
        if y + tw_h > scr_h - 8:
            y = self._pointer_y - tw_h - 4
        tw.wm_geometry(f"+{x}+{y}")
        # Safety-net: auto-dismiss after timeout even if <Leave> is
        # missed (e.g. window focus change, Alt-Tab, drag).
        self._auto_hide_id = self._widget.after(
            self._AUTO_HIDE_MS, self._hide)

    def _hide(self, _event=None) -> None:
        self._cancel()
        if self._auto_hide_id:
            self._widget.after_cancel(self._auto_hide_id)
            self._auto_hide_id = None
        if self._tw:
            self._tw.destroy()
            self._tw = None


# ════════════════════════════════════════════════════════════════
#  SCROLLABLE PAGE FRAME
# ════════════════════════════════════════════════════════════════

class ScrollablePage(ctk.CTkScrollableFrame):
    """Base container for every page — scrollable, themed."""

    def __init__(self, master, **kw):
        super().__init__(
            master,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["surface"],
            scrollbar_button_hover_color=COLORS["surface_hover"],
            **kw,
        )


# ════════════════════════════════════════════════════════════════
#  CARD
# ════════════════════════════════════════════════════════════════

class Card(ctk.CTkFrame):
    """Rounded card container with optional title."""

    def __init__(self, master, title: str = "", **kw):
        super().__init__(
            master,
            fg_color=COLORS["card"],
            corner_radius=CARD_CORNER,
            border_width=1,
            border_color=COLORS["card_border"],
            **kw,
        )
        if title:
            lbl = ctk.CTkLabel(
                self, text=title,
                font=FONTS["subheading"],
                text_color=COLORS["text_primary"],
                anchor="w",
            )
            lbl.pack(fill="x", padx=CARD_PAD, pady=(CARD_PAD, 4))
            sep = ctk.CTkFrame(self, height=1,
                               fg_color=COLORS["card_border"])
            sep.pack(fill="x", padx=CARD_PAD, pady=(0, 8))


# ════════════════════════════════════════════════════════════════
#  LABELED ENTRY
# ════════════════════════════════════════════════════════════════

class LabeledEntry(ctk.CTkFrame):
    """Label + Entry on one row.  Access value via .get()/.set()."""

    def __init__(self, master, label: str, default="",
                 width=160, tooltip: str = "", **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.columnconfigure(1, weight=1)

        self._label = ctk.CTkLabel(
            self, text=label, font=FONTS["body"],
            text_color=COLORS["text_secondary"], anchor="w", width=180,
        )
        self._label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._var = ctk.StringVar(value=str(default))
        self._entry = ctk.CTkEntry(
            self, textvariable=self._var, width=width,
            font=FONTS["body"],
            fg_color=COLORS["entry_bg"],
            border_color=COLORS["entry_border"],
            text_color=COLORS["text_primary"],
        )
        self._entry.grid(row=0, column=1, sticky="ew")

        if tooltip:
            self._tip_label = ctk.CTkLabel(
                self, text=tooltip, font=FONTS["tiny"],
                text_color=COLORS["text_muted"], anchor="w",
            )
            self._tip_label.grid(row=1, column=1, sticky="w", pady=(0, 2))

    def get(self) -> str:
        return self._var.get()

    def set(self, value) -> None:
        self._var.set(str(value))

    @property
    def var(self):
        return self._var


# ════════════════════════════════════════════════════════════════
#  LABELED OPTION MENU (drop-down)
# ════════════════════════════════════════════════════════════════

class LabeledOption(ctk.CTkFrame):
    """Label + OptionMenu on one row."""

    def __init__(self, master, label: str, values: list,
                 default=None, command=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.columnconfigure(1, weight=1)

        self._label = ctk.CTkLabel(
            self, text=label, font=FONTS["body"],
            text_color=COLORS["text_secondary"], anchor="w", width=180,
        )
        self._label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._var = ctk.StringVar(value=default or values[0])
        self._option = ctk.CTkOptionMenu(
            self, variable=self._var, values=values,
            font=FONTS["body"], width=160,
            fg_color=COLORS["entry_bg"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["surface_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            command=command,
        )
        self._option.grid(row=0, column=1, sticky="w")

    def get(self) -> str:
        return self._var.get()

    def set(self, value) -> None:
        self._var.set(str(value))
        self._option.set(str(value))          # Force CTkOptionMenu display refresh

    def update_values(self, values: list, keep_selection=True):
        """Replace the list of options (e.g. after antenna type list changes)."""
        old = self._var.get()
        self._option.configure(values=values)
        if keep_selection and old in values:
            self._option.set(old)
        elif values:
            self._option.set(values[0])

    @property
    def var(self):
        return self._var

class LabeledSwitch(ctk.CTkFrame):
    """Label + Switch on one row."""

    def __init__(self, master, label: str, default: bool = False,
                 command=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.columnconfigure(1, weight=1)

        self._label = ctk.CTkLabel(
            self, text=label, font=FONTS["body"],
            text_color=COLORS["text_secondary"], anchor="w", width=180,
        )
        self._label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._var = ctk.BooleanVar(value=default)
        self._switch = ctk.CTkSwitch(
            self, variable=self._var, text="",
            onvalue=True, offvalue=False,
            fg_color=COLORS["entry_border"],
            progress_color=COLORS["accent"],
            button_color=COLORS["text_primary"],
            button_hover_color=COLORS["accent_light"],
            command=command,
        )
        self._switch.grid(row=0, column=1, sticky="w")

    def get(self) -> bool:
        return self._var.get()

    def set(self, value: bool):
        self._var.set(value)

    @property
    def var(self):
        return self._var


# ════════════════════════════════════════════════════════════════
#  LABELED SLIDER
# ════════════════════════════════════════════════════════════════

class LabeledSlider(ctk.CTkFrame):
    """Label + Slider + Value display."""

    def __init__(self, master, label: str, from_: float, to: float,
                 default: float = None, step: float = None,
                 fmt: str = ".1f", **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.columnconfigure(1, weight=1)
        self._fmt = fmt

        self._label = ctk.CTkLabel(
            self, text=label, font=FONTS["body"],
            text_color=COLORS["text_secondary"], anchor="w", width=180,
        )
        self._label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._var = ctk.DoubleVar(value=default if default is not None else from_)
        self._val_label = ctk.CTkLabel(
            self, text=format(self._var.get(), fmt),
            font=FONTS["mono"], text_color=COLORS["accent"],
            width=60, anchor="e",
        )
        self._val_label.grid(row=0, column=2, padx=(8, 0))

        n_steps = None
        if step:
            n_steps = max(1, int(round((to - from_) / step)))

        self._slider = ctk.CTkSlider(
            self, from_=from_, to=to, variable=self._var,
            number_of_steps=n_steps,
            fg_color=COLORS["entry_border"],
            progress_color=COLORS["accent"],
            button_color=COLORS["text_primary"],
            button_hover_color=COLORS["accent_light"],
            command=self._on_change,
        )
        self._slider.grid(row=0, column=1, sticky="ew", padx=4)

    def _on_change(self, val) -> None:
        self._val_label.configure(text=format(float(val), self._fmt))

    def get(self) -> float:
        return self._var.get()

    def set(self, value: float):
        self._var.set(value)
        self._on_change(value)

    @property
    def var(self):
        return self._var


# ════════════════════════════════════════════════════════════════
#  LABELED SLIDER + ENTRY (bidirectional)
# ════════════════════════════════════════════════════════════════

class LabeledSliderEntry(ctk.CTkFrame):
    """Label + Slider + editable Entry — synced bidirectionally."""

    def __init__(self, master, label: str, from_: float, to: float,
                 default: float = None, step: float = None,
                 fmt: str = ".1f", tooltip: str = "", **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.columnconfigure(1, weight=1)
        self._fmt = fmt
        self._from = from_
        self._to = to
        self._step = step
        self._updating = False  # guard against infinite loop

        self._label = ctk.CTkLabel(
            self, text=label, font=FONTS["body"],
            text_color=COLORS["text_secondary"], anchor="w", width=180,
        )
        self._label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._var = ctk.DoubleVar(value=default if default is not None else from_)

        n_steps = None
        if step:
            n_steps = max(1, int(round((to - from_) / step)))

        self._slider = ctk.CTkSlider(
            self, from_=from_, to=to, variable=self._var,
            number_of_steps=n_steps,
            fg_color=COLORS["entry_border"],
            progress_color=COLORS["accent"],
            button_color=COLORS["text_primary"],
            button_hover_color=COLORS["accent_light"],
            command=self._on_slider_change,
        )
        self._slider.grid(row=0, column=1, sticky="ew", padx=4)

        # Editable entry
        self._entry_var = ctk.StringVar(
            value=format(self._var.get(), fmt))
        self._entry = ctk.CTkEntry(
            self, textvariable=self._entry_var, width=72,
            font=FONTS["mono"],
            fg_color=COLORS["entry_bg"],
            border_color=COLORS["entry_border"],
            text_color=COLORS["text_primary"],
            justify="center",
        )
        self._entry.grid(row=0, column=2, padx=(8, 0))
        self._entry.bind("<Return>", self._on_entry_commit)
        self._entry.bind("<FocusOut>", self._on_entry_commit)

        if tooltip:
            Tooltip(self._label, tooltip)

    def _on_slider_change(self, val) -> None:
        if self._updating:
            return
        self._updating = True
        self._entry_var.set(format(float(val), self._fmt))
        self._updating = False

    def _on_entry_commit(self, _event=None) -> None:
        if self._updating:
            return
        self._updating = True
        try:
            v = float(self._entry_var.get())
            v = max(self._from, min(self._to, v))
            if self._step:
                v = round(v / self._step) * self._step
            self._var.set(v)
            self._entry_var.set(format(v, self._fmt))
        except ValueError:
            # Revert to slider value
            self._entry_var.set(format(self._var.get(), self._fmt))
        self._updating = False

    def get(self) -> float:
        return self._var.get()

    def set(self, value: float):
        self._var.set(value)
        self._entry_var.set(format(value, self._fmt))

    @property
    def var(self):
        return self._var


# ════════════════════════════════════════════════════════════════
#  ACTION BUTTON (primary / secondary)
# ════════════════════════════════════════════════════════════════

class ActionButton(ctk.CTkButton):
    """Themed action button."""

    def __init__(self, master, text: str, command=None,
                 style="primary", width=160, **kw):
        colors = {
            "primary":   (COLORS["accent"], COLORS["accent_hover"],
                          COLORS["sidebar_text_act"]),
            "secondary": (COLORS["surface"], COLORS["surface_hover"],
                          COLORS["text_primary"]),
            "success":   (COLORS["success"], "#16A34A",
                          COLORS["sidebar_text_act"]),
            "danger":    (COLORS["error"], "#DC2626",
                          COLORS["sidebar_text_act"]),
        }
        fg, hover, txt = colors.get(style, colors["primary"])
        super().__init__(
            master, text=text, command=command,
            font=FONTS["body_bold"], width=width, height=38,
            fg_color=fg, hover_color=hover, text_color=txt,
            corner_radius=8,
            **kw,
        )


# ════════════════════════════════════════════════════════════════
#  FILE PICKER ROW
# ════════════════════════════════════════════════════════════════

class FilePicker(ctk.CTkFrame):
    """Label + path display + browse button."""

    def __init__(self, master, label: str, mode: str = "file",
                 filetypes=None, save: bool = False, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.columnconfigure(1, weight=1)
        self._mode = mode
        self._filetypes = filetypes or [("CSV/DAT files", "*.csv *.dat"), ("All files", "*.*")]
        self._save = save

        self._label = ctk.CTkLabel(
            self, text=label, font=FONTS["body"],
            text_color=COLORS["text_secondary"], anchor="w", width=180,
        )
        self._label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._var = ctk.StringVar(value="")
        self._entry = ctk.CTkEntry(
            self, textvariable=self._var, font=FONTS["small"],
            fg_color=COLORS["entry_bg"],
            border_color=COLORS["entry_border"],
            text_color=COLORS["text_primary"],
            state="readonly",
        )
        self._entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self._btn = ctk.CTkButton(
            self, text="Browse…", width=80, height=30,
            font=FONTS["small"],
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            command=self._browse,
        )
        self._btn.grid(row=0, column=2, padx=(0, 4))

        self._clear_btn = ctk.CTkButton(
            self, text="✕", width=30, height=30,
            font=FONTS["small"],
            fg_color=COLORS["surface"],
            hover_color=COLORS["error"],
            text_color=COLORS["text_muted"],
            command=self.clear,
        )
        self._clear_btn.grid(row=0, column=3)

    def _browse(self) -> None:
        import tkinter.filedialog as fd
        if self._mode == "directory":
            path = fd.askdirectory(title="Select Folder")
        elif self._save:
            path = fd.asksaveasfilename(
                title="Save As", filetypes=self._filetypes)
        elif self._mode == "files":
            paths = fd.askopenfilenames(
                title="Select Files", filetypes=self._filetypes)
            path = ";".join(paths) if paths else ""
        else:
            path = fd.askopenfilename(
                title="Select File", filetypes=self._filetypes)
        if path:
            self._var.set(path)

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str):
        self._var.set(value)

    def clear(self):
        """Clear the selected path."""
        self._var.set("")

    def get_files(self) -> list:
        """For mode='files', return list of paths."""
        val = self._var.get()
        return val.split(";") if val else []

    @property
    def var(self):
        return self._var


# ════════════════════════════════════════════════════════════════
#  STATUS BAR
# ════════════════════════════════════════════════════════════════

class StatusBar(ctk.CTkFrame):
    """Bottom status bar with message + progress."""

    def __init__(self, master, **kw):
        super().__init__(master, height=32, fg_color=COLORS["surface"], **kw)
        self.pack_propagate(False)

        self._msg = ctk.CTkLabel(
            self, text="Ready", font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w",
        )
        self._msg.pack(side="left", padx=12)

        self._progress = ctk.CTkProgressBar(
            self, width=200, height=8,
            fg_color=COLORS["entry_border"],
            progress_color=COLORS["accent"],
        )
        self._progress.pack(side="right", padx=12, pady=8)
        self._progress.set(0)

    def set_message(self, msg: str, color: str = None):
        self._msg.configure(
            text=msg,
            text_color=color or COLORS["text_muted"],
        )

    def set_progress(self, value: float):
        """0.0 to 1.0"""
        self._progress.set(min(1.0, max(0.0, value)))

    def success(self, msg: str):
        self.set_message(msg, COLORS["success"])
        self.set_progress(1.0)

    def error(self, msg: str):
        self.set_message(msg, COLORS["error"])

    def busy(self, msg: str = "Working…"):
        self.set_message(msg, COLORS["warning"])
        self.set_progress(0.5)

    def reset(self):
        self.set_message("Ready")
        self.set_progress(0)


# ════════════════════════════════════════════════════════════════
#  SECTION HEADING  (used inside pages)
# ════════════════════════════════════════════════════════════════

class SectionHeading(ctk.CTkLabel):
    """A large heading for a page section."""

    def __init__(self, master, text: str, **kw):
        super().__init__(
            master, text=text,
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w",
            **kw,
        )


# ════════════════════════════════════════════════════════════════
#  RESULT / LOG DISPLAY
# ════════════════════════════════════════════════════════════════

class ResultBox(ctk.CTkTextbox):
    """Read-only styled textbox for showing results/logs."""

    def __init__(self, master, height=200, **kw):
        super().__init__(
            master, height=height,
            font=FONTS["mono"],
            fg_color=COLORS["entry_bg"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["entry_border"],
            border_width=1,
            corner_radius=8,
            state="disabled",
            wrap="word",
            **kw,
        )

    def set_text(self, text: str) -> None:
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.insert("0.0", text)
        self.configure(state="disabled")

    def append(self, text: str) -> None:
        self.configure(state="normal")
        self.insert("end", text)
        self.see("end")
        self.configure(state="disabled")


# ════════════════════════════════════════════════════════════════
#  INPUT SANITIZATION HELPERS
# ════════════════════════════════════════════════════════════════

def safe_float(value: str, default: float = 0.0) -> float:
    """Convert *value* to float, returning *default* on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: str, default: int = 0) -> int:
    """Convert *value* to int, returning *default* on failure."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default
