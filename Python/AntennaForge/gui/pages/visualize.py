"""
Visualize Page — Graph antenna patterns with embedded Matplotlib.

Supports: Heatmap, Principal-plane cuts, Polar, 3-D surface,
Gain-vs-Freq, BW-vs-Freq, Overlay cuts.

Features:
  - Single CSV or whole-directory plotting
  - Detects existing PNGs to avoid re-generating
  - Prev / Next arrows to cycle through plots
  - Open plot folder in Windows Explorer
"""

import os, glob, threading
import customtkinter as ctk

from gui.theme import COLORS, FONTS, CARD_PAD
from gui.widgets import (
    ScrollablePage, Card, SectionHeading, ActionButton,
    LabeledOption, FilePicker, ResultBox, Tooltip,
)


class VisualizePage(ScrollablePage):
    """Interactive pattern visualisation with heatmap, polar, 3-D, and cut plots."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._images: list[str] = []   # ordered list of image paths
        self._img_idx: int = -1        # current position
        self._fig_widget = None
        self._pil_image = None          # original PIL image for rescaling
        self._img_label = None          # CTkLabel showing the image
        self._resize_after_id = None    # debounce handle
        self._last_render_size = (0, 0) # cached last rendered (w, h)
        self._cancel_flag = False       # cooperative cancel for plot jobs
        self._job_running = False       # True while a plot thread is active
        self._build()

    # ────────────────────────────────────────────────────────────
    #  BUILD
    # ────────────────────────────────────────────────────────────
    def _build(self) -> None:
        SectionHeading(self, text="Visualize Patterns").pack(
            anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(
            self,
            text="Select a pattern CSV or a directory and choose a plot type.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # ── Top row: input + plot type ──────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=8)
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)

        # Input card
        inp = Card(top, title="Input")
        inp.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        inp_inner = ctk.CTkFrame(inp, fg_color="transparent")
        inp_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_file = FilePicker(inp_inner, "Pattern CSV/DAT",
                                 filetypes=[("CSV/DAT files", "*.csv *.dat"), ("All", "*.*")])
        self.w_file.pack(fill="x", pady=4)
        Tooltip(self.w_file,
                "Single CSV file for Heatmap / Cuts / Polar / 3-D")

        self.w_dir = FilePicker(inp_inner, "Pattern Directory",
                                mode="directory")
        self.w_dir.pack(fill="x", pady=4)
        Tooltip(self.w_dir,
                "Folder of CSVs — used for multi-file plots "
                "or iterating single-file plots over every CSV")

        # Plot type card
        ptype = Card(top, title="Plot Type")
        ptype.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ptype_inner = ctk.CTkFrame(ptype, fg_color="transparent")
        ptype_inner.pack(fill="x", padx=CARD_PAD, pady=(4, CARD_PAD))

        self.w_plottype = LabeledOption(
            ptype_inner, "Type",
            ["Heatmap", "Cuts (Az+El)", "Polar", "3D Surface",
             "Gain vs Freq", "BW vs Freq", "Overlay Cuts",
             "Freq Sweep (GIF)"],
            default="Heatmap",
        )
        self.w_plottype.pack(fill="x", pady=4)

        # Animation frame style (only visible for Freq Sweep)
        self._anim_style_frame = ctk.CTkFrame(ptype_inner, fg_color="transparent")
        self._anim_style_frame.pack(fill="x", pady=2)
        self.w_anim_style = LabeledOption(
            self._anim_style_frame, "GIF Style",
            ["heatmap", "polar"], default="heatmap",
        )
        self.w_anim_style.pack(fill="x")
        Tooltip(self.w_anim_style,
                "Frame style for animated GIF:\n"
                "  heatmap — full 2-D colour map\n"
                "  polar   — azimuth + elevation polar cuts")
        self._anim_style_frame.pack_forget()   # hidden by default

        # Toggle animation style visibility on type change
        def _on_plottype_change(*_args):
            if self.w_plottype.get() == "Freq Sweep (GIF)":
                self._anim_style_frame.pack(fill="x", pady=2)
            else:
                self._anim_style_frame.pack_forget()

        self.w_plottype._var.trace_add("write", _on_plottype_change)

        ctk.CTkLabel(
            ptype_inner,
            text="Single-file: Heatmap, Cuts, Polar, 3D\n"
                 "Multi-file:  Gain/BW vs Freq, Overlay\n"
                 "Directory:   iterates single-file types\n"
                 "Freq Sweep:  animated GIF from dir",
            font=FONTS["small"], text_color=COLORS["text_muted"],
            justify="left",
        ).pack(anchor="w", pady=(8, 4))

        btn_row = ctk.CTkFrame(ptype_inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(8, 4))

        self._btn_plot = ActionButton(
            btn_row, text="📊  Plot", width=140,
            style="primary", command=self._on_plot,
        )
        self._btn_plot.pack(side="left")

        self._btn_cancel = ActionButton(
            btn_row, text="✖  Cancel", width=120,
            style="secondary", command=self._on_cancel,
        )
        self._btn_cancel.pack(side="left", padx=(12, 0))
        self._btn_cancel.configure(state="disabled")

        ActionButton(
            btn_row, text="📂  Open Folder", width=140,
            style="secondary", command=self._open_plot_dir,
        ).pack(side="left", padx=(12, 0))

        # ── Plot display area ───────────────────────────────────
        self.plot_card = Card(self, title="Plot Output")
        self.plot_card.pack(fill="both", padx=24, pady=8, expand=True)

        # Navigation bar
        nav = ctk.CTkFrame(self.plot_card, fg_color="transparent")
        nav.pack(fill="x", padx=CARD_PAD, pady=(4, 0))

        self._btn_prev = ctk.CTkButton(
            nav, text="◀  Prev", width=80, height=30,
            font=FONTS["body"], fg_color=COLORS["surface"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            command=self._prev_image, state="disabled",
        )
        self._btn_prev.pack(side="left")

        self._nav_label = ctk.CTkLabel(
            nav, text="No plots", font=FONTS["small"],
            text_color=COLORS["text_muted"],
        )
        self._nav_label.pack(side="left", expand=True)

        self._btn_next = ctk.CTkButton(
            nav, text="Next  ▶", width=80, height=30,
            font=FONTS["body"], fg_color=COLORS["surface"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            command=self._next_image, state="disabled",
        )
        self._btn_next.pack(side="right")

        # Image frame
        self.plot_frame = ctk.CTkFrame(self.plot_card,
                                       fg_color=COLORS["entry_bg"],
                                       corner_radius=8)
        self.plot_frame.pack(fill="both", padx=CARD_PAD, pady=(4, CARD_PAD),
                             expand=True)
        self.plot_frame.bind("<Configure>", self._on_frame_resize)

        self._plot_placeholder = ctk.CTkLabel(
            self.plot_frame,
            text="Select a file or directory and click Plot",
            font=FONTS["body"], text_color=COLORS["text_muted"],
        )
        self._plot_placeholder.pack(expand=True, pady=40)

        # ── Tooltips ───────────────────────────────────────────
        Tooltip(self.w_plottype,
                "Choose the plot type. Single-file: Heatmap, Cuts, Polar, "
                "3-D Surface. Multi-file: Gain/BW vs Freq, Overlay Cuts.")
        Tooltip(self._btn_prev, "Show the previous plot image")
        Tooltip(self._btn_next, "Show the next plot image")

        # ── Result log ──────────────────────────────────────────
        self.result = ResultBox(self, height=80)
        self.result.pack(fill="x", padx=24, pady=(0, 24))

    # ────────────────────────────────────────────────────────────
    #  JOB LIFECYCLE
    # ────────────────────────────────────────────────────────────
    def _job_start(self) -> None:
        """Called at the start of every plot job."""
        self._cancel_flag = False
        self._job_running = True
        self._btn_plot.configure(state="disabled")
        self._btn_cancel.configure(state="normal")

    def _job_end(self) -> None:
        """Called when a plot job finishes (success, error, or cancel)."""
        self._job_running = False
        self._cancel_flag = False
        self._btn_plot.configure(state="normal")
        self._btn_cancel.configure(state="disabled")

    def _on_cancel(self) -> None:
        """Request cooperative cancellation of the running plot job."""
        if self._job_running:
            self._cancel_flag = True
            self.result.append("\n⏹ Cancelling…\n")
            self.app.status.busy("Cancelling…")

    # ────────────────────────────────────────────────────────────
    #  NAVIGATION
    # ────────────────────────────────────────────────────────────
    def _update_nav(self) -> None:
        n = len(self._images)
        if n == 0:
            self._nav_label.configure(text="No plots")
            self._btn_prev.configure(state="disabled")
            self._btn_next.configure(state="disabled")
        else:
            self._nav_label.configure(
                text=f"{self._img_idx + 1} / {n}  —  "
                     f"{os.path.basename(self._images[self._img_idx])}")
            self._btn_prev.configure(
                state="normal" if self._img_idx > 0 else "disabled")
            self._btn_next.configure(
                state="normal" if self._img_idx < n - 1 else "disabled")

    def _prev_image(self) -> None:
        if self._img_idx > 0:
            self._img_idx -= 1
            self._show_image(self._images[self._img_idx])
            self._update_nav()

    def _next_image(self) -> None:
        if self._img_idx < len(self._images) - 1:
            self._img_idx += 1
            self._show_image(self._images[self._img_idx])
            self._update_nav()

    # ────────────────────────────────────────────────────────────
    #  OPEN FOLDER
    # ────────────────────────────────────────────────────────────
    def _open_plot_dir(self) -> None:
        """Open the folder containing the most recent plot in Explorer."""
        if self._images and self._img_idx >= 0:
            folder = os.path.dirname(self._images[self._img_idx])
        elif self.w_dir.get():
            folder = self.w_dir.get()
        elif self.w_file.get():
            folder = os.path.dirname(self.w_file.get())
        else:
            self.result.set_text(
                "No folder to open — select a file or directory first.")
            return

        if os.path.isdir(folder):
            os.startfile(folder)
        else:
            self.result.set_text(f"Folder not found: {folder}")

    # ────────────────────────────────────────────────────────────
    #  DETECT EXISTING PLOTS
    # ────────────────────────────────────────────────────────────
    @staticmethod
    def _find_existing_pngs(csv_path: str) -> list[str]:
        """Return any PNGs in the same directory that match the CSV stem."""
        folder = os.path.dirname(csv_path) or "."
        stem = os.path.splitext(os.path.basename(csv_path))[0]
        pattern = os.path.join(folder, f"{stem}*.png")
        return sorted(glob.glob(pattern))

    @staticmethod
    def _collect_dir_csvs(directory: str) -> list[str]:
        return sorted(
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.lower().endswith((".csv", ".dat"))
        )

    # ────────────────────────────────────────────────────────────
    #  MAIN PLOT DISPATCH
    # ────────────────────────────────────────────────────────────
    def _on_plot(self) -> None:
        plot_type = self.w_plottype.get()
        csv_file = self.w_file.get()
        csv_dir = self.w_dir.get()

        multi_types = {"Gain vs Freq", "BW vs Freq", "Overlay Cuts"}

        # ── Freq Sweep Animation ──────────────────────────────
        if plot_type == "Freq Sweep (GIF)":
            if csv_dir:
                file_list = self._collect_dir_csvs(csv_dir)
            elif csv_file:
                file_list = [csv_file]
            else:
                self.result.set_text(
                    "Select a directory of frequency-slice CSVs for animation.")
                return
            if len(file_list) < 2:
                self.result.set_text(
                    "Need at least 2 CSV files for an animation.")
                return
            self._do_animation(file_list)
            return

        if plot_type in multi_types:
            if csv_dir:
                file_list = self._collect_dir_csvs(csv_dir)
            elif csv_file:
                file_list = [csv_file]
            else:
                self.result.set_text(
                    "Select a directory (or single CSV) for multi-file plots.")
                return
            if len(file_list) < 2:
                self.result.set_text(
                    "Need at least 2 CSV files for multi-file plots.")
                return
            self._do_multi_plot(plot_type, file_list)
        else:
            if csv_file:
                existing = self._find_existing_pngs(csv_file)
                if existing:
                    self._set_images(existing)
                    self.result.set_text(
                        f"Found {len(existing)} existing plot(s) — "
                        "showing cached images.  Click Plot again "
                        "after clearing cache to regenerate.")
                    self.app.status.success("Loaded cached plots")
                    return
                self._do_single_plot(plot_type, csv_file)
            elif csv_dir:
                csvs = self._collect_dir_csvs(csv_dir)
                if not csvs:
                    self.result.set_text("No CSV files found in directory.")
                    return
                self._do_dir_single_plot(plot_type, csvs)
            else:
                self.result.set_text(
                    "Select a pattern CSV or a directory first.")

    # ────────────────────────────────────────────────────────────
    #  SINGLE FILE PLOT
    # ────────────────────────────────────────────────────────────
    def _do_single_plot(self, plot_type, filepath):
        # Check matplotlib availability before spawning thread
        try:
            from core.deps import HAS_MATPLOTLIB
            if not HAS_MATPLOTLIB:
                self.result.set_text(
                    "matplotlib is not installed.\n"
                    "Install with: pip install matplotlib\n"
                    "Plotting requires matplotlib and numpy.")
                self.app.status.error("matplotlib not available")
                return
        except ImportError:
            pass

        self.app.status.busy(f"Plotting {plot_type}…")
        self.result.set_text(
            f"Generating {plot_type} for {os.path.basename(filepath)}…\n")
        self._job_start()

        def work():
            try:
                if self._cancel_flag:
                    self.after(0, self._job_end)
                    self.after(0, lambda: self.app.status.reset())
                    return
                out = self._render_single(plot_type, filepath)
                if self._cancel_flag:
                    self.after(0, self._job_end)
                    self.after(0, lambda: self.result.append("\nCancelled."))
                    self.after(0, lambda: self.app.status.reset())
                    return
                self.after(0, lambda: self._set_images([out]))
                self.after(0, lambda: self.result.append(f"\nSaved: {out}"))
                self.after(0, lambda: self.app.status.success("Plot complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))
            finally:
                self.after(0, self._job_end)

        threading.Thread(target=work, daemon=True).start()

    # ────────────────────────────────────────────────────────────
    #  DIRECTORY → SINGLE-FILE ITERATION
    # ────────────────────────────────────────────────────────────
    def _do_dir_single_plot(self, plot_type, csv_list):
        n = len(csv_list)
        self.app.status.busy(f"Plotting {plot_type} for {n} files…")
        self.result.set_text(
            f"Generating {plot_type} for {n} CSV files…\n")
        self._job_start()

        def work():
            outputs = []
            for i, fp in enumerate(csv_list, 1):
                if self._cancel_flag:
                    self.after(0, lambda i=i:
                               self.result.append(
                                   f"\n⏹ Cancelled after {i-1}/{n} files.\n"))
                    break
                try:
                    out = self._render_single(plot_type, fp)
                    outputs.append(out)
                    self.after(0, lambda i=i, o=out:
                               self.result.append(
                                   f"  [{i}/{n}] {os.path.basename(o)}\n"))
                except Exception as e:
                    self.after(0, lambda fp=fp, e=e:
                               self.result.append(
                                   f"  SKIP {os.path.basename(fp)}: {e}\n"))

            if outputs:
                self.after(0, lambda: self._set_images(outputs))
                if self._cancel_flag:
                    self.after(0, lambda: self.app.status.reset())
                else:
                    self.after(0, lambda: self.app.status.success(
                        f"Done — {len(outputs)} plot(s)"))
            else:
                self.after(0, lambda: self.app.status.error(
                    "No plots generated"))
            self.after(0, self._job_end)

        threading.Thread(target=work, daemon=True).start()

    # ────────────────────────────────────────────────────────────
    #  MULTI-FILE PLOT
    # ────────────────────────────────────────────────────────────
    def _do_multi_plot(self, plot_type, file_list):
        # Check matplotlib availability before spawning thread
        try:
            from core.deps import HAS_MATPLOTLIB
            if not HAS_MATPLOTLIB:
                self.result.set_text(
                    "matplotlib is not installed.\n"
                    "Install with: pip install matplotlib\n"
                    "Plotting requires matplotlib and numpy.")
                self.app.status.error("matplotlib not available")
                return
        except ImportError:
            pass

        self.app.status.busy(f"Plotting {plot_type}…")
        self.result.set_text(
            f"Generating {plot_type} with {len(file_list)} files…\n")
        self._job_start()

        def work():
            try:
                if self._cancel_flag:
                    return
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt

                try:
                    if plot_type == "Gain vs Freq":
                        from graphing.multi_plots import graph_gain_vs_freq
                        out = graph_gain_vs_freq(file_list)
                    elif plot_type == "BW vs Freq":
                        from graphing.multi_plots import graph_bw_vs_freq
                        out = graph_bw_vs_freq(file_list)
                    elif plot_type == "Overlay Cuts":
                        from graphing.multi_plots import graph_overlay_cuts
                        out = graph_overlay_cuts(file_list)
                    else:
                        self.after(0, lambda: self.result.set_text(
                            f"Unknown: {plot_type}"))
                        return
                except Exception:
                    plt.close("all")
                    raise

                if self._cancel_flag:
                    self.after(0, lambda: self.result.append(
                        "\nCancelled."))
                    self.after(0, lambda: self.app.status.reset())
                    return

                self.after(0, lambda: self._set_images([out]))
                self.after(0, lambda: self.result.append(f"\nSaved: {out}"))
                self.after(0, lambda: self.app.status.success("Plot complete"))

            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))
            finally:
                self.after(0, self._job_end)

        threading.Thread(target=work, daemon=True).start()

    # ────────────────────────────────────────────────────────────
    #  FREQUENCY SWEEP ANIMATION
    # ────────────────────────────────────────────────────────────
    def _do_animation(self, file_list: list[str]) -> None:
        """Generate an animated GIF from a list of frequency-slice CSVs."""
        # Check dependencies before spawning thread
        try:
            from core.deps import HAS_MATPLOTLIB
            if not HAS_MATPLOTLIB:
                self.result.set_text(
                    "matplotlib is not installed.\n"
                    "Install with: pip install matplotlib")
                self.app.status.error("matplotlib not available")
                return
        except ImportError:
            pass

        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            self.result.set_text(
                "Pillow is required for GIF animation.\n"
                "Install with: pip install Pillow")
            self.app.status.error("Pillow not available")
            return

        style = self.w_anim_style.get()
        n = len(file_list)
        self.app.status.busy(f"Generating {style} animation ({n} files)…")
        self.result.set_text(
            f"Creating animated GIF ({style}) from {n} CSVs…\n")
        self._job_start()

        def work():
            try:
                if self._cancel_flag:
                    return
                from graphing.animation import generate_sweep_animation
                out = generate_sweep_animation(
                    file_list,
                    plot_style=style,
                    frame_duration_ms=500,
                )
                if self._cancel_flag:
                    self.after(0, lambda: self.result.append(
                        "\nCancelled."))
                    self.after(0, lambda: self.app.status.reset())
                    return
                self.after(0, lambda: self.result.append(
                    f"\nSaved: {out}\n({n} frames, {style} style)"))
                self.after(0, lambda: self._show_animation_result(out))
                self.after(0, lambda: self.app.status.success(
                    "Animation complete"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self.result.set_text(f"Error: {msg}"))
                self.after(0, lambda: self.app.status.error(msg))
            finally:
                self.after(0, self._job_end)

        threading.Thread(target=work, daemon=True).start()

    def _show_animation_result(self, gif_path: str) -> None:
        """Display the first frame of the animated GIF in the plot area."""
        try:
            from PIL import Image
            # Show first frame as a static preview
            img = Image.open(gif_path)
            img.seek(0)
            # Convert palette frame to RGB for display
            self._pil_image = img.convert("RGB")
            self._images = [gif_path]
            self._img_idx = 0
            self._render_scaled_image()
            self._update_nav()
        except Exception:
            # Fall back to text display
            for w in self.plot_frame.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self.plot_frame,
                text=f"Animation saved to:\n{gif_path}",
                font=FONTS["body"],
                text_color=COLORS["text_secondary"],
            ).pack(expand=True, pady=20)

    # ────────────────────────────────────────────────────────────
    #  RENDER HELPERS
    # ────────────────────────────────────────────────────────────
    @staticmethod
    def _render_single(plot_type: str, filepath: str) -> str:
        """Generate a single-file plot and return the PNG path."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        try:
            if plot_type == "Heatmap":
                from graphing.plots import graph_heatmap
                return graph_heatmap(filepath)
            elif plot_type == "Cuts (Az+El)":
                from graphing.plots import graph_cuts
                return graph_cuts(filepath)
            elif plot_type == "Polar":
                from graphing.plots import graph_polar
                return graph_polar(filepath)
            elif plot_type == "3D Surface":
                from graphing.plots import graph_3d_surface
                return graph_3d_surface(filepath)
            else:
                raise ValueError(f"Unknown single-file plot type: {plot_type}")
        except Exception:
            plt.close("all")
            raise

    # ────────────────────────────────────────────────────────────
    #  IMAGE DISPLAY
    # ────────────────────────────────────────────────────────────
    def _set_images(self, paths: list[str]) -> None:
        """Load a list of images and show the first one."""
        self._images = [p for p in paths if os.path.isfile(p)]
        if self._images:
            self._img_idx = 0
            self._show_image(self._images[0])
        else:
            self._img_idx = -1
        self._update_nav()

    def _show_image(self, image_path: str) -> None:
        """Display a PNG image in the plot frame, scaled to fit."""
        for w in self.plot_frame.winfo_children():
            w.destroy()
        self._img_label = None
        self._last_render_size = (0, 0)  # reset cache for new image

        try:
            from PIL import Image
            self._pil_image = Image.open(image_path)
            # Initial display — use frame size or sensible defaults
            self._render_scaled_image()
        except ImportError:
            self._pil_image = None
            ctk.CTkLabel(
                self.plot_frame,
                text=f"Plot saved to:\n{image_path}\n\n"
                     "(Install Pillow for embedded preview)",
                font=FONTS["body"],
                text_color=COLORS["text_secondary"],
            ).pack(expand=True, pady=20)

    # ── Resize helpers ──────────────────────────────────────────
    def _on_frame_resize(self, _event=None):
        """Debounced handler — rescale image when the plot frame changes size."""
        if self._pil_image is None:
            return
        if self._resize_after_id is not None:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(80, self._render_scaled_image)

    def _render_scaled_image(self) -> None:
        """Scale the stored PIL image to fit the current plot_frame size."""
        self._resize_after_id = None
        if self._pil_image is None:
            return

        fw = self.plot_frame.winfo_width()
        fh = self.plot_frame.winfo_height()
        # Guard against uninitialized geometry (reported as 1×1)
        avail_w = max(fw - 20, 200)
        avail_h = max(fh - 20, 200)

        orig_w, orig_h = self._pil_image.size
        # Cap available height to prevent image from pushing beyond
        # the visible viewport in a scrollable page
        max_display_h = 520
        avail_h = min(avail_h, max_display_h)
        # Always fit within frame — downscale large images, allow
        # modest upscale for very small images up to 1.5×
        scale = min(avail_w / orig_w, avail_h / orig_h)
        scale = min(scale, 1.5)  # never upscale beyond 150%
        new_w = max(int(orig_w * scale), 1)
        new_h = max(int(orig_h * scale), 1)

        # Skip if the target size hasn't meaningfully changed (< 5px)
        last_w, last_h = self._last_render_size
        if abs(new_w - last_w) < 5 and abs(new_h - last_h) < 5:
            return
        self._last_render_size = (new_w, new_h)

        from PIL import Image
        resized = self._pil_image.resize((new_w, new_h), Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized,
                                size=(new_w, new_h))

        if self._img_label is not None and self._img_label.winfo_exists():
            self._img_label.configure(image=ctk_img)
            self._img_label.image = ctk_img
        else:
            for w in self.plot_frame.winfo_children():
                w.destroy()
            self._img_label = ctk.CTkLabel(
                self.plot_frame, image=ctk_img, text="")
            self._img_label.image = ctk_img
            self._img_label.pack(expand=True, pady=8)
