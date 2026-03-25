"""
Interactive prompt helpers.

Leaf node — no internal imports. Used by menus, feature_config,
and antenna configure() methods via lazy import.

File/folder picker dialogs use tkinter.filedialog when available
(bundled with standard CPython on Windows/macOS). Falls back to
typed path input when tkinter is not present (e.g. headless / SSH).
"""
from __future__ import annotations
import glob
import os

# ── Native file picker support ────────────────────────────────
_HAS_TK = False
try:
    import tkinter as _tk
    from tkinter import filedialog as _fd
    _HAS_TK = True
except ImportError:
    pass


def _ensure_tk_root() -> "_tk.Tk":
    """Create a hidden Tk root window (needed by file dialogs)."""
    root = _tk.Tk()
    root.withdraw()          # Hide the empty window
    root.attributes("-topmost", True)  # Dialog on top
    return root


def pick_file(title: str = "Select a file", filetypes: list | None = None,
              must_exist: bool = True, initial_dir: str | None = None) -> str | None:
    """Open a native OS file-picker dialog.

    Returns the chosen path string, or None if cancelled.
    Falls back to typed input when tkinter is unavailable.
    """
    if not _HAS_TK:
        return None  # caller falls back to text input

    if filetypes is None:
        filetypes = [("CSV/DAT files", "*.csv *.dat"),
                     ("JSON files", "*.json"),
                     ("All files", "*.*")]
    root = _ensure_tk_root()
    try:
        path = _fd.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initial_dir or os.getcwd(),
        )
    finally:
        root.destroy()
    return path if path else None


def pick_files(title: str = "Select files", filetypes: list | None = None,
               initial_dir: str | None = None) -> list[str] | None:
    """Open a native multi-select file-picker dialog.

    Returns a list of paths, or None if cancelled.
    """
    if not _HAS_TK:
        return None

    if filetypes is None:
        filetypes = [("CSV/DAT files", "*.csv *.dat"),
                     ("All files", "*.*")]
    root = _ensure_tk_root()
    try:
        paths = _fd.askopenfilenames(
            title=title,
            filetypes=filetypes,
            initialdir=initial_dir or os.getcwd(),
        )
    finally:
        root.destroy()
    return list(paths) if paths else None


def pick_directory(title: str = "Select a folder",
                   initial_dir: str | None = None) -> str | None:
    """Open a native folder-picker dialog.

    Returns the chosen directory path, or None if cancelled.
    """
    if not _HAS_TK:
        return None

    root = _ensure_tk_root()
    try:
        path = _fd.askdirectory(
            title=title,
            initialdir=initial_dir or os.getcwd(),
        )
    finally:
        root.destroy()
    return path if path else None


def pick_save_file(title: str = "Save as", filetypes: list | None = None,
                   default_ext: str = ".csv", initial_dir: str | None = None) -> str | None:
    """Open a native save-file dialog.

    Returns the chosen path string, or None if cancelled.
    """
    if not _HAS_TK:
        return None

    if filetypes is None:
        filetypes = [("CSV/DAT files", "*.csv *.dat"),
                     ("JSON files", "*.json"),
                     ("PDF files", "*.pdf"),
                     ("All files", "*.*")]
    root = _ensure_tk_root()
    try:
        path = _fd.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=default_ext,
            initialdir=initial_dir or os.getcwd(),
        )
    finally:
        root.destroy()
    return path if path else None


# ── "Go Back" sentinel ────────────────────────────────────────

class GoBack(Exception):
    """Raised when the user types 'b' or 'back' at a prompt.

    Caught by menu_generate()'s section loop to step back
    to the previous configuration section.
    """
    pass


def _is_back(raw: str) -> bool:
    """Return True if the user typed 'b' or 'back'."""
    return raw.lower() in ("b", "back")


_BACK_HINT = "  (type 'b' to go back)"


def prompt_choice(text: str, choices: list[str],
                  default: str | None = None,
                  allow_back: bool = False) -> str:
    """Present numbered choices, return selected string.

    If allow_back is True, typing 'b' or 'back' raises GoBack.
    """
    print(f"\n{text}")
    for i, c in enumerate(choices, 1):
        marker = " (default)" if c == default else ""
        print(f"  [{i}] {c}{marker}")
    if allow_back:
        print(_BACK_HINT)
    while True:
        raw = input("> ").strip()
        if allow_back and _is_back(raw):
            raise GoBack()
        if raw == "" and default is not None:
            return default
        try:
            idx = int(raw)
            if 1 <= idx <= len(choices):
                return choices[idx - 1]
        except ValueError:
            for c in choices:
                if raw.lower() == c.lower():
                    return c
        print(f"  Enter 1-{len(choices)}")


def prompt_float(text: str, default: float | None = None,
                 min_val: float | None = None,
                 max_val: float | None = None,
                 allow_back: bool = False) -> float:
    """Prompt for a float with optional bounds.

    If allow_back is True, typing 'b' or 'back' raises GoBack.
    """
    def_str = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{text}{def_str}: ").strip()
        if allow_back and _is_back(raw):
            raise GoBack()
        if raw == "" and default is not None:
            return default
        try:
            val = float(raw)
            if min_val is not None and val < min_val:
                print(f"  Must be >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"  Must be <= {max_val}")
                continue
            return val
        except ValueError:
            print("  Enter a number")


def prompt_int(text: str, default: int | None = None,
               min_val: int | None = None,
               max_val: int | None = None,
               allow_back: bool = False) -> int:
    """Prompt for an integer with optional bounds.

    If allow_back is True, typing 'b' or 'back' raises GoBack.
    """
    def_str = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{text}{def_str}: ").strip()
        if allow_back and _is_back(raw):
            raise GoBack()
        if raw == "" and default is not None:
            return default
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                print(f"  Must be >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"  Must be <= {max_val}")
                continue
            return val
        except ValueError:
            print("  Enter an integer")


def prompt_yn(text: str, default: bool = True) -> bool:
    """Prompt for yes/no, return bool."""
    d = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{text} [{d}]: ").strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  Enter y or n")


def prompt_file(text: str, must_exist: bool = True, pattern: str | tuple[str] = ("*.csv", "*.dat")) -> str:
    """Prompt for a file path — opens native picker first, typed fallback."""
    # ── Try native file picker first ──────────────────────
    if _HAS_TK:
        if isinstance(pattern, str):
            ext = pattern.replace("*", "")  # e.g. ".csv"
            type_label = f"{ext.upper().strip('.')} files" if ext else "All files"
            filetypes = [(type_label, pattern), ("All files", "*.*")]
        else:
            type_label = "Data files"
            filetypes = [(type_label, pattern), ("All files", "*.*")]

        print(f"{text}")
        print("  Opening file picker…  (or close dialog to type path manually)")
        picked = pick_file(title=text, filetypes=filetypes)
        if picked:
            print(f"  Selected: {picked}")
            return picked
        print("  No file selected — enter path manually.")

    # ── Typed fallback ────────────────────────────────────
    while True:
        raw = input(f"{text}: ").strip()
        if not raw:
            print("  Please enter a path")
            continue
        # Strip surrounding quotes (Windows drag-and-drop)
        raw = raw.strip('"').strip("'")
        # Expand globs
        matches = glob.glob(raw)
        if matches and len(matches) == 1:
            raw = matches[0]
        # Check if user passed a directory
        if os.path.isdir(raw):
            data_files = sorted([
                f for f in os.listdir(raw)
                if f.endswith(('.csv', '.dat'))
            ])
            if data_files:
                print(f"  That is a directory. "
                      f"Found {len(data_files)} CSV/DAT files:")
                for i, f in enumerate(data_files[:20], 1):
                    print(f"    [{i}] {f}")
                pick = input(
                    "  Select a file #: "
                ).strip()
                try:
                    idx = int(pick) - 1
                    if 0 <= idx < len(data_files):
                        raw = os.path.join(raw, data_files[idx])
                    else:
                        print("  Invalid selection")
                        continue
                except ValueError:
                    print("  Invalid selection")
                    continue
            else:
                print(f"  That is a directory with no "
                      f"CSV/DAT files: {raw}")
                continue
        if must_exist and not os.path.exists(raw):
            print(f"  File not found: {raw}")
            continue
        return raw


def prompt_dir(text: str = "Select directory", default: str = ".") -> str:
    """Prompt for a directory — opens native picker first, typed fallback."""
    if _HAS_TK:
        print(f"  {text}")
        print("  Opening folder picker…  (or close dialog to type path manually)")
        picked = pick_directory(title=text)
        if picked and os.path.isdir(picked):
            print(f"  Selected: {picked}")
            return picked
        print("  No folder selected — enter path manually.")

    raw = input(
        f"  {text} [{default}]: "
    ).strip().strip('"').strip("'") or default
    return raw


def prompt_save_file(text: str = "Save as",
                     default_name: str = "output.csv",
                     ext: str = ".csv") -> str:
    """Prompt for an output file path — save dialog first, typed fallback."""
    if _HAS_TK:
        ext_label = ext.upper().strip('.') + " files"
        filetypes = [(ext_label, f"*{ext}"), ("All files", "*.*")]
        print(f"  {text}")
        print("  Opening save dialog…  (or close dialog to type path manually)")
        picked = pick_save_file(
            title=text, filetypes=filetypes,
            default_ext=ext)
        if picked:
            print(f"  Save to: {picked}")
            return picked
        print("  No path selected — enter manually.")

    raw = input(
        f"  {text} [{default_name}]: "
    ).strip().strip('"').strip("'") or default_name
    return raw


def prompt_dir_files(text: str, directory: str | None = None,
                     exts: tuple[str] = (".csv", ".dat")) -> list[str] | None:
    """Pick files from a directory — multi-select picker first, typed fallback."""
    # ── Try native multi-select picker ────────────────────
    if _HAS_TK and directory is None:
        ext_str = " ".join([f"*{e}" for e in exts])
        type_label = f"{'/'.join([e.upper().strip('.') for e in exts])} files"
        filetypes = [(type_label, ext_str), ("All files", "*.*")]
        print(f"  {text}")
        print("  Opening file picker…  (or close dialog to browse manually)")
        picked = pick_files(title=text, filetypes=filetypes)
        if picked:
            for p in picked:
                print(f"    • {os.path.basename(p)}")
            return picked
        print("  No files selected — falling back to directory listing.")

    # ── Directory listing fallback ────────────────────────
    if directory is None:
        directory = prompt_dir("Directory to scan", default=".")
    if not os.path.isdir(directory):
        print(f"  Not a directory: {directory}")
        return None

    files = sorted([
        f for f in os.listdir(directory)
        if f.endswith(exts)
    ])
    if not files:
        print(f"  No {exts} files found in {directory}")
        return None

    print(f"\n{text}")
    for i, f in enumerate(files, 1):
        print(f"  [{i}] {f}")
    print(f"  [A] Select all")

    while True:
        raw = input("> ").strip()
        if raw.lower() == 'a':
            return [
                os.path.join(directory, f) for f in files
            ]
        try:
            indices = [
                int(x.strip()) for x in raw.split(',')
            ]
            selected = []
            valid = True
            for idx in indices:
                if 1 <= idx <= len(files):
                    selected.append(
                        os.path.join(
                            directory, files[idx - 1]
                        )
                    )
                else:
                    valid = False
                    break
            if valid and selected:
                return selected
        except ValueError:
            pass
        print(f"  Enter 1-{len(files)}, "
              "comma-separated, or A for all")
