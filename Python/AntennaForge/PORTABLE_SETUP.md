# AntennaForge — Portable / Air-Gapped Deployment Guide

This guide explains how to move AntennaForge to a **standalone network**
(no internet) and ensure everything works.

---

## Overview

AntennaForge has **one required dependency** and **four optional ones**:

| Package        | Required? | Purpose                                     |
|----------------|-----------|---------------------------------------------|
| customtkinter  | **Yes**   | GUI framework                               |
| numpy          | Optional  | 50–100× faster pattern computation          |
| scipy          | Optional  | Dish Bessel patterns, bicubic interpolation  |
| matplotlib     | Optional  | All graphing / plot generation               |
| Pillow         | Optional  | Embedded plot preview inside the GUI         |
| python-pptx    | Optional  | PowerPoint (.pptx) report generation         |

Without the optional packages the core engine still generates patterns
and writes CSV files — it just uses slower pure-Python math and skips
plot features.

> **tkinter** is also required for the GUI but ships with the standard
> Python installer — it is **not** a pip package.  On Linux you may need
> `sudo apt install python3-tk` (Debian/Ubuntu) or
> `sudo dnf install python3-tkinter` (Fedora/RHEL).

---

## Prerequisites on the Target Machine

- **Python 3.10+** installed (with tkinter — the default Windows installer includes it)
- Write access to install packages (or a virtual environment)
- No internet connection required

---

## Step-by-Step Deployment

### 1. Prepare on an internet-connected machine

```bash
# Clone / copy the antenna_tool folder
cd antenna_tool

# Download wheels for ALL supported Python versions (3.10 - 3.14)
# This ensures compatibility regardless of what version is on the target.
python scripts/fetch_wheels.py
#   ↳ creates offline_wheels.zip and cleans up temporary files
```

### 2. Transfer to the standalone machine

Copy the entire project folder (which now contains `offline_wheels.zip`) to the target machine.

### 3. Install on the standalone machine

**Option A: Automatic (Windows)**

Just double-click **`run.bat`**.
It will automatically:
1. Unzip `offline_wheels.zip` (if needed).
2. Create a `.venv` folder.
3. Install the correct wheels for the machine's Python version.
4. Launch the GUI.

**Option B: Manual Install**

```bash
cd antenna_tool
# Linux/macOS:
source .venv/bin/activate

# Install everything from local wheels (no internet needed)
python scripts/install_offline.py
```

### 4. Verify

```bash
python scripts/install_offline.py --check
```

Expected output:
```
  ✓  customtkinter
  ✓  numpy
  ✓  scipy
  ✓  matplotlib
  ✓  Pillow
All dependencies satisfied — ready to run!
```

### 5. Run

```bash
python AntennaForge.py          # GUI mode (recommended)
python -m antenna_tool          # Interactive CLI mode (from parent directory)
```

---

## Troubleshooting

### "No matching distribution found for X"
The wheel for that package wasn't downloaded for the right
Python version / OS.  Re-run `scripts/fetch_wheels.py` with explicit
`--python-version` and `--platform` flags matching the target.

### numpy/scipy won't install (missing C compiler)
Pre-built wheels avoid this. Make sure you downloaded wheels (`.whl`),
not source distributions (`.tar.gz`). Use `--only-binary=:all:` when
downloading.

### Plots don't appear in the GUI
Matplotlib and Pillow are both needed for embedded plot display.
Check `python scripts/install_offline.py --check` and install any missing ones.

### "ModuleNotFoundError: No module named 'antenna_tool'"
Make sure you activate the venv and run from the parent directory:
```bash
cd <folder containing antenna_tool>
python -m antenna_tool --gui
```

---

## Dependency Check from Inside the App

The **Home** page shows a dependency status card at the bottom,
listing which optional packages are installed and which are missing.

You can also check from the command line:

```bash
python -c "from core.deps import print_status; print_status()"
```

---

## Updating Dependencies

If you need to update packages later, repeat the process:

1. On the internet machine: `python scripts/fetch_wheels.py --dest ./wheels`
2. Transfer the new `wheels/` folder
3. On the target: `python scripts/install_offline.py`

---

## Minimal Deployment (No Optional Deps)

If you only need CSV pattern generation (no plots, no GUI preview):

```bash
pip install --no-index --find-links wheels customtkinter
python -m antenna_tool generate --type dipole --freq 150
```

The engine will use pure-Python math fallbacks automatically.
