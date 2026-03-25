# AntennaForge v1.0

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-139%20passed-brightgreen.svg)](#testing)
[![Python-pptx](https://img.shields.io/badge/pptx-optional-lightgrey.svg)](#requirements)

A Python **GUI + CLI** tool for generating, visualising, analysing, and reporting **idealised antenna radiation patterns**. Built for RF engineers who need realistic-looking pattern data without full electromagnetic simulation.

> **Important:** AntennaForge generates *synthetic* patterns from analytical models — not from physical geometry or method-of-moments solvers. It is designed for rapid prototyping, link budgets, mask compliance checks, and report generation.

## Why Use AntennaForge?

- **Modern GUI** — Full graphical interface with dark/light theme, sidebar navigation, and embedded plot viewer
- **Multi-Frequency Support** — Automatic beamwidth scaling across frequency bands  
- **Production-Ready Outputs** — CSV patterns, PDF/LaTeX reports, publication-quality plots
- **Extensible Architecture** — Add custom antenna types via plugin system
- **Compliance Testing** — Built-in ITU-R and MIL-STD sidelobe mask verification
- **Dual Interface** — Use the GUI for interactive work or the CLI/batch mode for automation

---

## Table of Contents

- [Features](#features)
- [Supported Antenna Types](#supported-antenna-types)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [GUI (Graphical Interface)](#gui-graphical-interface)
- [Interactive CLI Mode](#interactive-cli-mode)
- [CLI Mode](#cli-mode)
- [Batch Mode](#batch-mode)
- [Reports](#reports)
- [Pattern Operations](#pattern-operations)
- [Antenna Math Reference](#antenna-math-reference)
- [RF Calculations](#rf-calculations)
- [Validation Results](#validation-results)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Logging](#logging)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Changelog](#changelog)

---

## Features

| Category | Capabilities |
|----------|-------------|
| **GUI** | Modern graphical interface (customtkinter) with sidebar navigation, dark/light themes, embedded plot viewer, and guided How-To page |
| **Generation** | Multi-frequency pattern CSVs with configurable angular resolution (az/el step) |
| **Antenna Models** | 7 built-in types with plugin registry for custom extensions |
| **Physics Features** | Freq-dependent beamwidth, sidelobes (Taylor), pattern breakup, ground reflection, cross-pol, VSWR rolloff, asymmetry/squint, gain-beamwidth coupling |
| **Graphing** | Heatmaps (pcolormesh), principal-plane cuts, polar plots, 3-D surfaces, gain-vs-freq, BW-vs-freq, overlay cuts — all viewable in-app |
| **Analysis** | Beamwidth, sidelobe detection, F/B ratio, symmetry, coverage stats, pattern comparison, pattern-set % difference |
| **Reports** | PDF, LaTeX (.tex), and PowerPoint (.pptx) reports with 13 configurable sections and 4 presets |
| **Pattern Ops** | Add, subtract, multiply, scale, max envelope, average, rotation/tilt/roll |
| **RF Calcs** | EIRP calculator, free-space path loss, full link budget |
| **Compliance** | ITU-R S.580-6, ITU-R S.465-6, MIL-STD sidelobe mask testing with full documentation |
| **Interpolation** | Frequency interpolation between slices, angular resampling |
| **Batch Mode** | JSON recipe files for unattended multi-config generation |

---

## Supported Antenna Types

| Type | Model | Key Parameters | Typical Use |
|------|-------|----------------|-------------|
| **LPDA** | Elliptical Gaussian + back lobe | FTB ratio | HF/VHF broadband, SIGINT |
| **Omni** | cos^n elevation, 360° azimuth | El beamwidth | Mobile, maritime, IoT |
| **Panel** | Sinc² (uniform aperture) | FTB, mechanical tilt | Cellular sectors, Wi-Fi |
| **Dish** | Jinc² (Airy pattern) | Efficiency, FTB, feed taper | Satcom, radar, PTP links |
| **Horn** | Sinc² (E) × cos-taper (H) | FTB, aperture size | Feeds, standard gain, radar |
| **Monopole** | Dipole far-field | Element length (λ), physical length | VHF/UHF, ground-based |
| **Array** | Element × Array Factor | Elements, spacing, steering, element pattern | Phased arrays, beamforming |

### Antenna Type Details

#### LPDA (Log-Periodic Dipole Array)
- **Beamwidth:** 50–70° typical, varies moderately with frequency
- **Gain:** 5–9 dBi typical across bandwidth
- **FTB:** 10–20 dB

#### Panel / Sector
- **Beamwidth:** 30–120° (az), 10–30° (el)
- **Gain:** 12–18 dBi
- **FTB:** 20–30 dB
- **Mechanical tilt:** Configurable uptilt/downtilt (`mechanical_tilt_deg`, replaces legacy `panel_downtilt_deg`)

#### Dish (Parabolic Reflector)
- **Beamwidth:** 1–10° (depends on aperture and frequency)
- **Gain:** 20–45 dBi
- **Efficiency:** Configurable (typical 55–65%)
- **Feed edge taper:** Gaussian envelope for sidelobe suppression (`feed_edge_taper_db`, default −12 dB)

#### Horn
- **Beamwidth:** 10–60° depending on aperture
- **Gain:** 10–25 dBi
- **Aperture size:** Optional `horn_aperture_wavelengths` for frequency-dependent beamwidth (BW ∝ λ/D)

#### Monopole / Dipole
- **Pattern:** Toroidal (donut-shaped)
- **Element lengths:** 0.25λ (quarter-wave), 0.5λ (half-wave), custom
- **Physical length:** Optional `monopole_physical_length_m` for frequency-dependent pattern evolution (electrical length scales with frequency)

#### Phased Array
- **Array factor:** Linear, planar, or circular geometry
- **Element patterns:** Gaussian (default), cosine, or patch element models (`array_element_pattern`)
- **Element weighting:** Uniform or Taylor taper for sidelobe control
- **Beam steering:** Azimuth and elevation (planar)
- **Mutual coupling:** Impedance-matrix model with Gauss elimination (`array_mutual_coupling`)
- **Element errors:** RMS amplitude and phase error simulation (`array_rms_amplitude_error_db`, `array_rms_phase_error_deg`)
- **Circular orientation:** Parallel or radial element pointing (`array_circular_orientation`)
- **Grating lobe warning:** Automatic warning when d > λ/2

---

## Installation

### Requirements

| Package | Required | Purpose |
|---------|----------|---------|
| **Python** | 3.10+ | Core runtime |
| **NumPy** | Strongly recommended | 50–100× faster vectorized computation |
| **Matplotlib** | For graphing/reports | Heatmaps, cuts, polar, 3D, PDF/LaTeX reports |
| **SciPy** | Optional | Bicubic interpolation, rotation, Bessel functions |
| **customtkinter** | For GUI | Modern themed GUI framework |
| **Pillow** | For GUI plot preview | Embedded image display in the plot viewer |
| **python-pptx** | Optional | PowerPoint (.pptx) report generation |
| **tkinter** | Optional (bundled) | Native file-picker dialogs (CLI mode) |

### Install

**Windows (one-click):**

Double-click **`run.bat`**. It automatically:
1. Checks for Python 3.10+
2. Extracts `offline_wheels.zip` or downloads wheels if internet is available
3. Creates a `.venv` virtual environment
4. Installs all dependencies from local wheels
5. Launches the GUI

**Manual install:**

```bash
cd AntennaForge

# Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Launch the GUI
python AntennaForge.py

# Or use the CLI
python -m antenna_tool --help
```

**Editable / development install:**

```bash
pip install -e ".[full]"    # core + numpy/scipy/matplotlib/Pillow
pip install python-pptx     # optional: PowerPoint reports
```

For air-gapped deployment, see [PORTABLE_SETUP.md](PORTABLE_SETUP.md).

### Platform Notes

| Platform | Notes |
|----------|-------|
| **Windows** | Fully supported. File pickers use native dialogs. |
| **Linux** | Fully supported. Install `python3-tk` for file dialogs. |
| **Headless/SSH** | Works — falls back to typed path input when no display available. |

### Troubleshooting

**"ModuleNotFoundError: No module named 'antenna_tool'"**
- Run from the *parent* directory: `cd .. && python -m antenna_tool`
- Or add to path: `export PYTHONPATH=/path/to/parent:$PYTHONPATH`

**"No module named 'numpy'"**  
- Install with: `pip install numpy`
- Without NumPy, the tool still works but is ~50× slower

**Plots not displaying / blank windows**
- Install matplotlib: `pip install matplotlib`
- On headless systems, plots save to file (no display needed)

**File picker not appearing**
- Install tkinter: `apt install python3-tk` (Linux) or reinstall Python with Tcl/Tk (Windows/macOS)
- The tool falls back to typed input if tkinter is unavailable

### Performance

| NumPy | Grid Size | Time per slice |
|-------|-----------|----------------|
| Yes | 361 × 181 (1° step) | ~5 ms |
| Yes | 721 × 361 (0.5° step) | ~15 ms |
| No | 361 × 181 (1° step) | ~500 ms |

Generating 10 frequency slices at 1° resolution takes about 50 ms with NumPy.

---

## Quick Start

```bash
# Launch the GUI (recommended)
python AntennaForge.py

# Interactive CLI mode (full menu system)
python -m antenna_tool

# Generate LPDA patterns from CLI
python -m antenna_tool --type LPDA --max-gain 7 --az-bw 65 --el-bw 70 \
    --f-min 30 --f-max 300 --slices 10

# Generate a PDF report from existing pattern CSVs
python -m antenna_tool --report ./antenna_patterns/20250101_1200

# Generate a LaTeX report
python -m antenna_tool --latex-report ./antenna_patterns/20250101_1200

# Run a batch recipe
python -m antenna_tool --batch recipe.json
```

---

## GUI (Graphical Interface)

AntennaForge includes a full graphical interface built with **customtkinter**.

### Launching

```bash
python AntennaForge.py
# or, from the parent directory:
python -m antenna_tool --gui
```

### Pages

| Page | Description |
|------|-------------|
| **Home** | Dashboard with quick-action cards and tool overview |
| **Generate** | Configure and generate single antenna patterns, or run batch recipes with image/report generation and cooperative cancellation |
| **Visualize** | Plot heatmaps, cuts, polar, 3-D, gain-vs-freq, BW-vs-freq, overlay cuts — with Prev/Next image cycling and auto-scaling display |
| **Analysis** | Run beamwidth, sidelobe, F/B ratio, symmetry, and coverage analysis on pattern CSVs; parameter fitting from reference patterns; batch fitting (fit many pattern sets at once from subfolders, auto-detect type/frequency, generate fitted patterns, compare against originals, and produce a detailed report); pattern-set comparison with percentage differences |
| **Operations** | Pattern arithmetic (add, subtract, multiply, scale, max envelope, average), rotation, and interpolation |
| **RF Calcs** | EIRP calculator, free-space path loss, and full link budget |
| **Reports** | Generate PDF or LaTeX reports with 13 individually toggleable sections and 4 presets |
| **How To** | Built-in guide covering every page and feature |
| **Settings** | Toggle dark/light theme, customise fonts and colours, manage config files |

### Key Features

- **Dark / Light themes** — colours auto-switch via `(light, dark)` tuples
- **Sidebar navigation** — single-window design; pages swap in place
- **Lazy page loading** — pages are created on first visit for fast startup
- **Slider + Entry sync** — beamwidth controls have a draggable slider and an editable entry, bidirectionally linked
- **Tooltips** — hover any labelled widget for a description
- **Auto-scaling plot viewer** — images resize to fit the window on every resize event
- **Cached-plot detection** — the Visualize page finds existing PNGs before re-rendering
- **Open Folder** — one-click to open the plot directory in Windows Explorer
- **Background threading** — generation and plotting run off the main thread so the UI stays responsive

---

## Interactive CLI Mode

Launch with no arguments to enter the full menu system:

```
python -m antenna_tool
```

The main menu provides access to all features:

```
   ANTENNAFORGE  v1.0
============================================================

  ── Generate & View ──────────────────────────
  [1] Generate Patterns      Create antenna pattern CSVs
  [2] Graph Patterns         Heatmap, cuts, polar, 3D
  [3] Generate Report        Multi-freq report with plots

  ── Analyse ──────────────────────────────────
  [4] Analyze Patterns       Stats, comparison, export
  [5] Pattern Arithmetic     Add, subtract, envelope…
  [6] Pattern Rotation       Pan, tilt, roll transform
  [7] Sidelobe Mask Test     ITU-R / MIL-STD compliance

  ── RF Calculations ──────────────────────────
  [8] EIRP Calculator        Effective radiated power
  [9] Link Budget            Path loss & margin

  ── Utilities ────────────────────────────────
  [A] Interpolate Patterns   Freq interp / resample
  [B] Batch (JSON Recipe)    Automated generation

  [Q] Quit
```

Navigation uses `GoBack` exceptions — type **b** at any prompt to return to the previous menu.

---

## CLI Mode

All generation parameters are available as command-line flags:

```bash
python -m antenna_tool --type Panel --max-gain 15 --az-bw 65 --el-bw 30 \
    --f-min 700 --f-max 2700 --slices 20 --spacing log \
    --ftb 25 --output ./panel_patterns
```

### Feature toggles

```bash
--no-freq-bw       # Disable frequency-dependent beamwidth
--no-sidelobes     # Disable sidelobe generation
--no-breakup       # Disable pattern breakup/irregularity
--ground           # Enable ground reflection
--no-ground        # Disable ground reflection
--xpol             # Enable cross-polarisation output
--no-vswr          # Disable VSWR rolloff at band edges
--asymmetry        # Enable pattern asymmetry
```

### Config files

```bash
# Save current settings
python -m antenna_tool --type LPDA --save-config my_lpda.json

# Load and optionally override
python -m antenna_tool --config my_lpda.json --slices 50
```

---

## Batch Mode

Create a JSON recipe to generate multiple antenna configurations in one run:

```json
{
  "description": "Overnight LPDA sweep",
  "configs": [
    {
      "antenna_type": "LPDA",
      "max_gain_dbi": 7.0,
      "az_beamwidth_deg": 65,
      "el_beamwidth_deg": 70,
      "f_min_mhz": 30,
      "f_max_mhz": 300,
      "n_slices": 25,
      "output_dir": "./batch_lpda"
    }
  ]
}
```

```bash
# Run the recipe
python -m antenna_tool --batch recipe.json

# Dry run (validate only)
python -m antenna_tool --batch recipe.json --batch-dry-run

# Generate plot images and save to a custom output folder
python -m antenna_tool --batch recipe.json --batch-images \
    --batch-output ./batch_results

# Also generate PDF reports (minimal preset)
python -m antenna_tool --batch recipe.json --batch-images \
    --batch-report --batch-report-preset minimal \
    --batch-output ./batch_results
```

### Batch CLI Flags

| Flag | Description |
|------|-------------|
| `--batch <recipe.json>` | Run a batch recipe |
| `--batch-dry-run` | Validate recipe without generating files |
| `--batch-images` | Generate plot images for each job |
| `--batch-output <dir>` | Base output directory (jobs become subfolders) |
| `--batch-report` | Generate a PDF report per job (requires `--batch-images`) |
| `--batch-report-preset <name>` | Report preset: `default`, `full`, `minimal`, or `quick` |

In the GUI, batch processing lives on the **Generate** page with a recipe picker, output folder, image/report toggles, a report-preset selector, and a red **Cancel** button for cooperative cancellation of long-running batches.

### Dataset Batch Generator

The `scripts/generate_dataset_batch.py` utility generates large-scale randomized dataset recipes for ML training, validation, and benchmarking. It creates batch JSON files with per-type parameter ranges and feature probabilities.

```bash
# Interactive mode
python scripts/generate_dataset_batch.py

# Non-interactive mode
python scripts/generate_dataset_batch.py --count 50000 --types LPDA Panel Horn --seed 42

# All types, random slices, custom output
python scripts/generate_dataset_batch.py --count 10000 --n-slices random --out ./batch_scripts
```

Features:
- Covers all 7 antenna types with physically realistic parameter ranges
- Per-type feature enable probabilities (e.g., 70% chance of freq-dependent BW for LPDA, 0% az BW scaling for Omni)
- Log-uniform frequency distribution for even decade coverage
- Automatic Testing/Validation split (default 80/20)
- Reproducible via `--seed`

Output: A single `dataset_batch.json` in the output directory, consumable by the standard batch processing pipeline.

---

## Reports

### PDF Report

Generates a multi-page PDF with configurable sections:

- Cover page, table of contents
- Summary table (peak gain, BW, F/B, sidelobes per frequency)
- Gain vs frequency and beamwidth vs frequency trend plots
- Overlay cuts (all frequencies)
- Per-frequency: heatmap + cuts combo, polar plots, 3-D surfaces
- Detailed analysis: statistics, sidelobe analysis, hemispheric coverage

### LaTeX Report

Generates a standalone `.tex` file with the same structure, plus an `images/` directory tree of PNGs organised into subfolders (`heatmaps/`, `polar/`, `3d_surface/`, `xpol/`). Global trend plots are saved directly in `images/`. Edit the `.tex` freely before compiling:

```bash
python -m antenna_tool --latex-report ./pattern_dir
cd ./pattern_dir
pdflatex pattern_report.tex
```

### PowerPoint Report

Generates a `.pptx` slide deck with summary tables, trend plots, and per-frequency pattern plots. Requires the `python-pptx` package:

```python
from reporting.pptx_report import generate_pptx_report

generate_pptx_report('./pattern_dir')
```

### Report Configuration

13 sections can be individually toggled, with 4 built-in presets:

| Preset | Description |
|--------|-------------|
| `default` | Recommended sections: summary, trends, heatmaps, polar, analysis |
| `full` | All 13 sections enabled (including 3-D surfaces) |
| `minimal` | Summary + basic per-freq (heatmap, stats) |
| `quick` | Global pages only (summary, trends, overlay cuts), no per-frequency detail |

---

## Pattern Operations

### Arithmetic

| Operation | Description |
|-----------|-------------|
| **Add** | Power-sum in linear domain |
| **Subtract** | dB difference (A − B) |
| **Multiply** | dB addition — element pattern × array factor |
| **Scale** | Add a constant dB offset (cable loss, amp gain) |
| **Max Envelope** | Worst-case envelope across multiple patterns |
| **Average** | Power-averaged mean |

### Rotation / Tilt

Apply mechanical pan, tilt, and roll to existing patterns:

```
Azimuth rotation:  ±360°  (pan left/right)
Elevation tilt:    ±90°   (tilt up/down)
Roll:              ±180°  (rotate about boresight)
```

Works on single files or entire directories. Uses scipy for fast interpolation with bilinear fallback.

---

## Antenna Math Reference

This section documents the mathematical models used for each antenna type and feature. All gain values are computed in linear scale internally and converted to dBi for output.

### Core Concepts

#### Beamwidth-to-Exponent Conversion

For cos^n pattern models, the exponent `n` is derived from the 3 dB beamwidth:

```
cos(θ_3dB/2)^n = 0.5
n = ln(0.5) / ln(cos(θ_3dB/2))
```

This ensures the pattern drops to half-power (-3 dB) at exactly the specified beamwidth angle.

#### Smooth Front-Hemisphere Blending

To avoid discontinuities at ±90° azimuth, the tool uses a sigmoid function instead of a hard front/back split:

```
front_fade(cos_az) = 1 / (1 + e^(-k·cos_az))
```

Where `k = 40` provides a ~5° transition zone. At boresight (cos_az = 1), this returns ~1.0; at ±90° (cos_az = 0), it returns 0.5; at the rear (cos_az = -1), it returns ~0.0.

### Per-Antenna Pattern Models

#### LPDA (Log-Periodic Dipole Array)

**Main Beam:** Elliptical Gaussian model

```
r² = (az_eff / az_hw)² + (el_eff / el_hw)²
G_main = G_peak × 0.5^(r²) × front_fade(cos_az)
```

**Back Lobe:** Continuous weighting (no dead zone at ±90°)

```
back_weight = (1 - cos_az) / 2
G_back = G_peak × FTB_linear × back_weight × |cos_el|^(n_el×0.5)
```

**Total:** `G = max(G_main, G_back)`

#### Panel (Sector Antenna)

**Pattern Model:** Sinc² (uniform aperture illumination)

```
u_az = 1.3916 × sin(θ_az) / sin(θ_3dB_az/2)
u_el = 1.3916 × sin(θ_el) / sin(θ_3dB_el/2)

G_front = G_peak × sinc²(u_az) × sinc²(u_el) × front_fade
```

The constant 1.3916 is chosen so sinc²(1.3916) = 0.5 (−3 dB at beamwidth).

**Mechanical Tilt:** Elevation offset applied before pattern calculation (`mechanical_tilt_deg`).

#### Horn Antenna

**E-plane (Elevation):** Sinc² pattern (uniform illumination)

```
u_el = 1.3916 × sin(θ_el) / sin(θ_3dB_el/2)
G_el = sinc²(u_el)
```

**H-plane (Azimuth):** Cosine-tapered pattern

```
v_az = 1.1891 × sin(θ_az) / sin(θ_3dB_az/2)
G_az = [cos(v) / (1 - (2v/π)²)]²
```

The constant 1.1891 gives −3 dB at the beamwidth for the H-plane response.

**Total:** `G_front = G_peak × G_az × G_el × front_fade`

#### Dish (Parabolic Reflector)

**Pattern Model:** Jinc² (Airy pattern for circular aperture)

```
r² = (sin(θ_az)/sin(θ_3dB_az/2))² + (sin(θ_el)/sin(θ_3dB_el/2))²
u = 1.6163 × √(r²)

G_front = G_peak × η × [2·J₁(u)/u]²
```

Where:
- `J₁` is the first-order Bessel function of the first kind
- `η` is aperture efficiency (typically 0.55–0.65)
- 1.6163 is the solution to [2·J₁(u)/u]² = 0.5

**Feed Edge Taper:** When `feed_edge_taper_db` is set (default −12 dB), a Gaussian envelope `exp(−r²/(2σ²))` is applied, suppressing sidelobes at the cost of a slightly wider main beam. The taper sigma is derived so that the taper amplitude equals `10^(taper_dB/20)` at the dish edge.

#### Monopole / Dipole

**Pattern Model:** Standard dipole far-field formula

```
F(θ_el) = [cos(kL/2 × sin(θ_el)) - cos(kL/2)] / [(1 - cos(kL/2)) × cos(θ_el)]

G = G_peak × F²
```

Where:
- `kL = 2π × L` (L = element length in wavelengths)
- Quarter-wave monopole: L = 0.25 → toroidal pattern
- Half-wave dipole: L = 0.5 → slightly narrower

**Frequency-dependent length:** When `monopole_physical_length_m` is set, the electrical length scales with frequency: `L(f) = physical_length / (c/f)`. This models a fixed physical element whose pattern evolves across the band.

#### Omnidirectional

**Azimuth:** No pattern (uniform 360°)

**Elevation:** cos^n model with sidelobes

```
G = G_peak × |cos(θ_el)|^n
```

#### Phased Array

**Pattern Multiplication Theorem:**

```
G_total = G_element × AF²
```

**Linear Array Factor:**

```
ψ = k·d·sin(θ) + β
AF = Σ wₙ × e^(j·n·ψ)
```

Where:
- `d` = element spacing (wavelengths)
- `β` = progressive phase shift for beam steering
- `wₙ` = element weights (uniform or Taylor taper)

**Element Pattern:** Three models available via `array_element_pattern`:
- `gaussian` (default): `G_elem = 0.5^(r²)` where `r² = (az/az_hw)² + (el/el_hw)²`
- `cosine`: `G_elem = [cos(π/2 · θ/θ_3dB)]²` per plane
- `patch`: `G_elem = cos^1.5(az) · cos^1.5(el)` empirical patch rolloff

**Beam Steering:** `β = -k·d·sin(θ_scan)` steers the beam to θ_scan.

**Mutual Coupling:** When `array_mutual_coupling` is enabled, an N×N impedance matrix is built using an exponential-decay model and solved via Gauss elimination to perturb element weights and phases.

**Element Errors:** `array_rms_amplitude_error_db` and `array_rms_phase_error_deg` add deterministic per-element random errors to model manufacturing tolerances.

**Grating Lobe Condition:** Appear when `d/λ > 1/(1 + |sin(θ_scan)|)`.

### Frequency-Dependent Beamwidth

Three decay models are available:

**1. Exponent Mode:**
```
BW(f) = BW_ref × (f_ref/f)^exp
```
Typical exponent: 0.8 for broadband antennas.

**2. Percentage Mode:**
```
BW(f) = BW_ref × [1 - (pct/100) × log₂(f/f_ref)]
```
Decays by specified percentage per octave.

**3. Three-Point Mode:**

Quadratic Lagrange interpolation through user-specified values at f_min, f_mid, f_max.

### Sidelobe Envelope

**Taylor Model:** Decaying sidelobes

```
u = |θ_off_axis| / BW

For u > 0.7 (outside main beam):
  sidelobe_index = floor((u - 0.7) / 0.8)
  phase = π × [(u - 0.7)/0.8 - sidelobe_index]
  
  G_sl = first_sidelobe_linear × decay^(sidelobe_index) × cos²(phase)
```

**Radial Model:** Uses elliptical off-axis angle for circular sidelobe rings instead of rectangular bands.

### Ground Reflection (Two-Ray Model)

```
Δφ = 4π × h × sin(θ_el) / λ

interference_factor = 1 + ρ² + 2ρ × cos(Δφ + π)

G_effective = G × interference_factor
```

Where:
- `h` = antenna height above ground
- `ρ` = reflection coefficient (0–1)
- The `+π` accounts for 180° phase shift on reflection

### Cross-Polarisation Model

```
XPol = CoPol × isolation_boresight + CoPol × XPol_max × angular_factor × diagonal_factor
```

Where:
- `angular_factor` = Gaussian centered at `peak_angle` off-axis
- `diagonal_factor` = `|sin(2 × atan2(el, az))|` (peaks on diagonals)

### VSWR Rolloff

Gain reduction at band edges due to impedance mismatch:

```
For frequencies within rolloff_fraction of band edge:
  t = distance_from_edge / edge_width
  
  Cosine shape: loss_factor = 0.5 × (1 - cos(π×t))
  Linear shape: loss_factor = t
  
  G_effective = G × 10^(-max_rolloff_dB × (1-loss_factor) / 10)
```

---

## RF Calculations

### EIRP (Effective Isotropic Radiated Power)

```
EIRP(az, el) = P_tx - L_cable + G(az, el)
```

All values in dBm/dB. Output is a CSV with the same angular grid as input.

### Free-Space Path Loss

```
FSPL = 20·log₁₀(d_km) + 20·log₁₀(f_MHz) + 32.44  [dB]
```

### Link Budget

```
P_rx = P_tx - L_tx + G_tx - FSPL + G_rx - L_rx
Link_Margin = P_rx - P_sensitivity
```

### Power Density

```
PD = EIRP / (4π·d²)  [W/m²]
```

Used for regulatory compliance (FCC/ITU exposure limits).

---

## API Reference

The antenna_tool package can be imported and used programmatically.
All modules use a **function-based** API (no classes to instantiate).

### Installation for API Use

```python
import sys
sys.path.insert(0, '/path/to/antenna_tool')

# Or install as editable package:
# pip install -e /path/to/antenna_tool
```

### Pattern Generation

```python
import copy
from config import DEFAULT_CONFIG, validate_config, generate_frequencies
from core.engine import run_generation
import io as _io

# Build config
cfg = copy.deepcopy(DEFAULT_CONFIG)
cfg.update({
    'antenna_type': 'Dish',
    'max_gain_dbi': 35.0,
    'az_beamwidth_deg': 3.0,
    'el_beamwidth_deg': 3.0,
    'dish_efficiency': 0.6,
    'f_min_mhz': 11700,
    'f_max_mhz': 12200,
    'n_slices': 5,
    'output_dir': './dish_patterns',
})

# Validate
errors = validate_config(cfg)      # returns list[str]; empty = valid
assert not errors, errors

# Generate frequency list and run
freqs = generate_frequencies(
    cfg['f_min_mhz'], cfg['f_max_mhz'],
    cfg['n_slices'], cfg['freq_spacing'],
)
buf = _io.StringIO()
run_generation(cfg, freqs, writer=buf)
print(buf.getvalue())
```

### Available Antenna Types

```python
from antennas import available_names, get_antenna

print(available_names())   # ['LPDA', 'Omni', 'Panel', 'Dish', 'Horn', 'Monopole', 'Array']
ant = get_antenna('Dish')  # returns an AntennaBase subclass instance
print(ant.default_params())
```

### Pattern Analysis

```python
from analysis.analyzer import (
    analyze_single, compare_patterns,
    measure_beamwidth, find_first_sidelobe,
    check_symmetry_az, check_symmetry_el,
)

# Single file
result = analyze_single('dish_12000MHz_copol.csv')
print(f"Peak gain:  {result['peak_gain']} dBi")
print(f"Az BW:      {result['az_bw']}°")
print(f"El BW:      {result['el_bw']}°")

# Compare multiple files
import io as _io
results = [analyze_single(f) for f in csv_files]
buf = _io.StringIO()
compare_patterns(results, writer=buf)
print(buf.getvalue())
```

### EIRP & Power Density

```python
from core.eirp import compute_eirp, compute_power_density

# EIRP — writes a new CSV with EIRP at every angle
out_path, peak_eirp, peak_az, peak_el = compute_eirp(
    'dish_12000MHz_copol.csv',
    tx_power_dbm=30.0,
    cable_loss_db=2.0,
)
print(f"Peak EIRP: {peak_eirp:.1f} dBm at az={peak_az}° el={peak_el}°")

# Power density
pd_path = compute_power_density(
    'dish_12000MHz_copol.csv',
    tx_power_dbm=30.0, cable_loss_db=2.0, distance_m=1000.0,
)
```

### Free-Space Path Loss & Link Budget

```python
from core.link_budget import (
    free_space_path_loss, compute_link_margin, compute_link_budget,
)

# Quick FSPL
fspl = free_space_path_loss(distance_km=100, freq_mhz=1000)
print(f"FSPL = {fspl:.1f} dB")

# Boresight link margin (single number)
margin = compute_link_margin(
    'tx_pattern.csv', 'rx_pattern.csv',
    distance_km=100, freq_mhz=1000,
    tx_power_dbm=30.0,
    rx_sensitivity_dbm=-90.0,
    tx_cable_loss_db=2.0,
    rx_cable_loss_db=1.0,
)
print(f"Link margin: {margin['link_margin_db']:.1f} dB")

# Full angular link budget map → CSV
out, peak_rx, tx_az, rx_az = compute_link_budget(
    'tx_pattern.csv', 'rx_pattern.csv',
    distance_km=100, freq_mhz=1000,
)
```

### Pattern Operations

```python
from core.pattern_ops import (
    add_patterns, subtract_patterns, multiply_patterns,
    scale_pattern, max_envelope, average_patterns,
)

# Power-sum two patterns → output CSV
add_patterns('pat_a.csv', 'pat_b.csv', 'sum.csv')

# Scale a pattern by −3 dB
scale_pattern('pat_a.csv', -3.0, 'scaled.csv')

# Max envelope across many files
max_envelope(['a.csv', 'b.csv', 'c.csv'], 'envelope.csv')
```

### Rotation / Tilt / Roll

```python
from core.rotation import rotate_pattern, rotate_directory

rotate_pattern('pat.csv', 'rotated.csv',
               az_rotate=45, el_tilt=10, roll=0)

rotate_directory('input_dir/', 'output_dir/',
                 az_rotate=30, el_tilt=-5, roll=0)
```

### Sidelobe Mask Testing

```python
from core.sidelobe_masks import (
    itu_r_s580, itu_r_s465, mil_std_envelope,
    test_pattern_against_mask,
)

mask_fn = itu_r_s580(peak_gain_dbi=35.0)   # returns a callable
result = test_pattern_against_mask('pat.csv', mask_fn, 'az')

print(f"Passed: {result['passed']}")
print(f"Violations: {result['n_violations']}")
for v in result.get('violations', [])[:5]:
    print(f"  {v['angle']}°: {v['gain']:.1f} dBi vs {v['max_allowed']:.1f} limit")
```

### CSV I/O

```python
from core.io import write_pattern_csv, read_pattern_csv, extract_freq_from_filename

az, el, data = read_pattern_csv('pattern.csv')
print(f"Grid: {len(az)} az × {len(el)} el")

write_pattern_csv('output.csv', az, el, data)

freq = extract_freq_from_filename('dish_12000MHz_copol.csv')  # → 12000.0
```

### Reports (PDF, LaTeX & PowerPoint)

```python
from reporting.report import generate_report, default_report_config
from reporting.latex_report import generate_latex_report
from reporting.pptx_report import generate_pptx_report

# PDF report
cfg = default_report_config()
cfg['per_freq_3d'] = True       # enable 3-D surfaces
generate_report('./pattern_dir', report_cfg=cfg)

# LaTeX report
generate_latex_report('./pattern_dir', report_cfg=cfg)

# PowerPoint report (requires python-pptx)
generate_pptx_report('./pattern_dir', report_cfg=cfg)
```

### Parameter Fitting

```python
from core.fitting import fit_parameters, fit_parameters_multirun
import threading

# Fit config parameters to reference patterns
result = fit_parameters(
    reference_files=['ref_150MHz_copol.csv', 'ref_300MHz_copol.csv'],
    antenna_type='LPDA',
    f_min_mhz=30.0,
    f_max_mhz=300.0,
    optimize=True,          # refine via SciPy optimization
    target_rms=0.5,         # target RMS error in dB
)
cfg = result['config']      # fitted AntennaForge config dict
report = result['report']   # human-readable summary

# Multi-run fitting (tries different strategies, keeps best)
# n_runs=0 means unlimited runs — use stop_event to cancel
stop = threading.Event()
result = fit_parameters_multirun(
    reference_files, antenna_type='Panel',
    f_min_mhz=700, f_max_mhz=2700,
    n_runs=5, optimize=True,
    stop_event=stop,        # optional: set stop.set() to halt
)

# The fitter uses:
#   - Coarse-to-fine optimization (15° → 3° grid stride)
#   - Differential evolution for high-dimensional types (Dish, Array)
#   - Cross-correlation + weighted percentage error cost function
#   - Warm-start cache (~/.antennaforge/fit_cache.json)
#   - Per-type auto-stop RMS thresholds
#   - Ensemble averaging of top results
```

### Batch Fitting

```python
from core.fitting import batch_fit
result = batch_fit(
    parent_dir="path/to/pattern_sets",
    output_dir="path/to/output",
    n_runs=0,        # 0 = auto (2x recommended)
    target_rms=0.0,  # 0 = per-type default
)
print(result['report'])
```

### ODESSA .tbl Import

```python
from core.io import read_odessa_tbl

# Read an ODESSA .tbl file (multiple frequency slices in one file)
tbl = read_odessa_tbl('antenna.tbl')
print(tbl['freqs_mhz'])    # list of frequencies
print(len(tbl['slices']))  # one 2D pattern per frequency
# tbl['az_deg'], tbl['el_deg'] — angle grids
```

### Analysis from Raw Data

```python
from analysis.analyzer import analyze_from_data

# Analyze a pattern from in-memory data (no file needed)
result = analyze_from_data(az_angles, el_angles, data_2d)
```

### Interpolation

```python
from core.interpolation import (
    interpolate_frequency, multi_freq_interpolation, resample_pattern,
)

# Blend two patterns at a target frequency
out = interpolate_frequency('low.csv', 'high.csv', target_freq_mhz=950)

# Resample angular grid
out = resample_pattern('coarse.csv', az_step=0.5, el_step=0.5)
```

### Type Hints

All public functions include type hints for IDE integration.
`validate_config()` returns `list[str]` (empty = valid) rather than
raising an exception.

---

## Configuration

### Config Schema

The `DEFAULT_CONFIG` dictionary defines all parameters. Key fields:

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `antenna_type` | str | see table | Antenna model |
| `max_gain_dbi` | float | −30 to 60 | Peak gain |
| `az_beamwidth_deg` | float | 1 to 360 | 3 dB azimuth beamwidth |
| `el_beamwidth_deg` | float | 1 to 360 | 3 dB elevation beamwidth |
| `f_min_mhz` | float | 0.001 to 1e6 | Start frequency |
| `f_max_mhz` | float | 0.001 to 1e6 | End frequency |
| `n_slices` | int | 1 to 10000 | Number of frequency slices |
| `freq_spacing` | str | linear / log | Frequency distribution |
| `az_step_deg` | float | 0.01 to 45 | Azimuth angular resolution |
| `el_step_deg` | float | 0.01 to 45 | Elevation angular resolution |
| `noise_type` | str | uniform / gaussian / quantization | Noise distribution mode |

### Validation

All configs are validated before generation with type checks, range limits, cross-field validation (e.g., f_min < f_max), and antenna-specific warnings.

### Feature Toggles

Nine optional physics features, each with sub-parameters:

1. **Frequency-dependent beamwidth** (az/el) — exponent or three-point decay
2. **Sidelobes** — Taylor model with configurable first SLL and decay
3. **Pattern breakup** — random ripple at high off-axis angles
4. **Ground reflection** — two-ray model with configurable height/soil
5. **Cross-polarisation** — generates separate `_xpol.csv` files
6. **VSWR rolloff** — cosine gain reduction at band edges
7. **Asymmetry** — azimuth squint, elevation tilt, random asymmetry
8. **Gain-beamwidth coupling** — linked frequency-dependent gain and beamwidth

---

## Logging

The tool uses Python's `logging` module. By default, `INFO`-level messages go to stdout. Core, reporting, graphing, and batch modules all log through named loggers.

The logging setup is in `logging_config.py` and initialised automatically in `__main__.py`.

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run just the core unit tests
python -m pytest tests/test_core.py -v

# Run extended coverage tests
python -m pytest tests/test_extended.py -v

# Run the boundary discontinuity diagnostics
python -m pytest tests/test_boundary_discontinuity.py -v
```

### Test Coverage

| Suite | Tests | Covers |
|-------|-------|--------|
| `test_core.py` | 51 | bw_to_exponent, front_fade_scalar, config save/load, config validation, frequency generation, CSV round-trip, all 7 antenna types (boresight, range, finiteness), pattern rotation, pattern arithmetic, beamwidth measurement |
| `test_extended.py` | 78 | IO edge cases, EIRP, link budget, FSPL, sidelobe masks (ITU-R S.580/465, MIL-STD), pattern ops (add/subtract/multiply/scale/envelope/average), interpolation, rotation, dependency checks, graph path helpers, animation |
| `test_boundary_discontinuity.py` | 10 | Sigmoid blend at ±90° boundary, multi-frequency/BW/antenna-type discontinuity verification |
| **Total** | **139** | |

---

## Project Structure

```
antenna_tool/
├── AntennaForge.py          GUI launcher (double-click or python AntennaForge.py)
├── pyproject.toml           Package metadata (optional editable install)
├── requirements.txt         Dependency list (pip install -r)
├── config.py                DEFAULT_CONFIG, save/load, validation
├── __init__.py              Package init
├── __main__.py              Entry point (python -m antenna_tool)
├── README.md                This file
├── PORTABLE_SETUP.md        Air-gapped deployment guide
│
├── core/                    Computation engine + internal modules
│   ├── engine.py            Vectorised pattern computation + generation loop
│   ├── io.py                CSV read/write, frequency extraction
│   ├── pattern_math.py      Beamwidth, sigmoid blend, sidelobes, breakup
│   ├── pattern_ops.py       Pattern arithmetic (add, subtract, scale…)
│   ├── rotation.py          Pattern rotation / tilt / roll
│   ├── interpolation.py     Frequency interpolation, angular resampling
│   ├── eirp.py              EIRP calculator
│   ├── link_budget.py       Link budget analysis
│   ├── sidelobe_masks.py    ITU-R / MIL-STD mask compliance
│   ├── cli.py               Argparse CLI + dispatch
│   ├── batch.py             JSON recipe batch generation
│   ├── fitting.py           Parameter fitting from reference patterns
│   ├── deps.py              Optional-dependency availability checker
│   └── logging_config.py    Central logging setup
│
├── gui/                     GUI (customtkinter)
│   ├── __init__.py          Package marker
│   ├── __main__.py          python -m gui entry point
│   ├── app.py               Main App window, sidebar, page routing
│   ├── theme.py             COLORS, FONTS, SIDEBAR_ITEMS, sizes
│   ├── user_prefs.py        Persistent user preferences (JSON)
│   ├── widgets.py           Reusable widgets (Tooltip, Card, LabeledEntry,
│   │                          LabeledOption, LabeledSliderEntry, FilePicker,
│   │                          ActionButton, StatusBar, ResultBox, …)
│   └── pages/
│       ├── home.py          Dashboard & quick-action cards
│       ├── generate.py      Pattern generation wizard
│       ├── visualize.py     Plot viewer with Prev/Next & auto-scaling
│       ├── analysis.py      Pattern analysis & sidelobe mask docs
│       ├── operations.py    Arithmetic, rotation, interpolation
│       ├── rf_calc.py       EIRP, FSPL, link budget
│       ├── reports.py       PDF/LaTeX report builder
│       ├── howto.py         Built-in How-To guide
│       └── settings.py      Theme toggle & custom accent colour
│
├── antennas/                Antenna type plugins
│   ├── __init__.py          Registry (register/get/discover)
│   ├── base.py              AntennaBase ABC
│   ├── lpda/lpda.py         Log-periodic dipole array
│   ├── omni/omni.py         Omnidirectional
│   ├── panel/panel.py       Flat panel / sector
│   ├── dish/dish.py         Parabolic reflector
│   ├── horn/horn.py         Horn antenna
│   ├── monopole/monopole.py Quarter-wave monopole
│   └── array/array_antenna.py  Phased array
│
├── analysis/
│   └── analyzer.py          Beamwidth, sidelobes, symmetry, comparison
│
├── graphing/
│   ├── __init__.py          Dependency check (numpy/matplotlib)
│   ├── plots.py             Single-file plots (heatmap, cuts, polar, 3D)
│   ├── multi_plots.py       Multi-file plots (gain-vs-freq, BW-vs-freq, overlay)
│   ├── animation.py         Animated frequency-sweep GIF generation
│   └── live_plots.py        In-memory live preview plots (GUI)
│
├── reporting/
│   ├── report.py            PDF report (13 configurable sections, 4 presets)
│   ├── latex_report.py      LaTeX .tex report generation
│   └── pptx_report.py       PowerPoint .pptx report generation
│
├── ui/                      Terminal-mode interactive UI
│   ├── menus.py             Interactive menu system
│   ├── prompts.py           Input helpers (float, int, choice, file/dir pickers)
│   └── feature_config.py    Feature toggle display
│
├── scripts/                 Utility / deployment scripts
│   ├── antenna_tool_shim.py Backwards-compatibility entry shim
│   ├── fetch_wheels.py      Download wheels for air-gapped install
│   ├── install_offline.py   Offline pip install from local wheels
│   ├── append_diff_table.py Utility for diff table reporting
│   └── generate_dataset_batch.py  Large-scale dataset batch generator
│
└── tests/
    ├── test_core.py                   Core unit tests (33)
    ├── test_extended.py               Extended coverage (59)
    └── test_boundary_discontinuity.py Sigmoid boundary tests (10)
```

---

## Contributing

### Development Setup

```bash
# Install development dependencies
pip install numpy matplotlib scipy pytest

# Verify everything works
python -m pytest tests/ -v
python -m antenna_tool --help
```

### Code Style Guidelines

- **Python 3.10+ compatible** — uses PEP 604 union types (`str | None`)
- **79-character line limit** where practical (120 max)
- **Docstrings** on all public functions (Google style preferred)
- **Type hints** encouraged but not required
- **No hard dependencies** except NumPy — matplotlib/scipy are optional
- **Lazy imports** for UI modules to keep core fast

### Adding a New Antenna Type

1. Create directory structure:
   ```
   antennas/mytype/
   ├── __init__.py
   └── mytype.py
   ```

2. Implement the `AntennaBase` interface:
   ```python
   from antennas.base import AntennaBase

   class MyTypeAntenna(AntennaBase):
       @property
       def name(self) -> str:
           return "MyType"
       
       @property
       def has_az_pattern(self) -> bool:
           return True  # False for omni types
       
       def default_params(self) -> dict:
           return {"my_param": 10.0}
       
       def configure(self, cfg: dict) -> None:
           from ui.prompts import prompt_float
           cfg["my_param"] = prompt_float(
               "My parameter", default=cfg.get("my_param", 10.0)
           )
       
       def validate_config(self, cfg: dict) -> list:
           warnings = []
           if cfg.get("my_param", 0) < 0:
               warnings.append("my_param should be positive")
           return warnings
       
       def compute_point_gain(self, az_eff, el_eff,
                              cos_az, cos_el,
                              n_az, n_el, az_bw, el_bw,
                              gain_peak, cfg) -> float:
           # Return LINEAR gain (not dB!)
           return gain_peak * some_pattern_function(...)
   ```

3. The registry auto-discovers your type on import.

### Writing Tests

- Add tests to `tests/test_core.py` for new features
- Use pytest fixtures for setup/teardown
- Test edge cases: 0°, ±90°, ±180° boundaries
- Verify both scalar and vectorized (NumPy) code paths

Example test:
```python
def test_mytype_boresight_gain(self):
    cfg = _default_cfg(antenna_type="MyType")
    ant = get_antenna("MyType")
    g = ant.compute_point_gain(
        0.0, 0.0,
        math.cos(0.0), math.cos(0.0),
        n_az, n_el, az_bw, el_bw,
        gain_peak, cfg
    )
    assert g > 0
    assert math.isfinite(g)
```

### Commit Guidelines

- Use **present tense** ("Add feature" not "Added feature")
- Use **imperative mood** ("Fix bug" not "Fixes bug")
- Keep commits atomic — one logical change per commit
- Reference issues: `Fix #123: Handle edge case in rotation`

### Pull Request Process

1. **Update tests** — new code should have test coverage
2. **Run the full suite:** `python -m pytest tests/ -v`
3. **Update documentation** if adding features
4. **Describe your changes** in the PR description
5. **Be responsive** to review feedback

### Reporting Issues

When reporting bugs, include:
- Python version (`python --version`)
- OS and version
- Full error traceback
- Minimal reproduction steps
- Sample config/data if applicable

### Feature Requests

We're open to new features! Please describe:
- **Use case** — what problem does it solve?
- **Proposed implementation** — how would it work?
- **Alternatives considered** — what else did you consider?

---

## FAQ

**Q: How accurate are these patterns compared to real antennas?**

A: These are *analytical approximations*, not electromagnetic simulations. They capture the general shape (beamwidth, sidelobes, front-to-back) but won't match a specific physical antenna's measurement data. Use them for link budgets, coverage planning, and visualization — not for precision antenna design.

**Q: Why is NumPy recommended but not required?**

A: The tool has a pure-Python fallback for all computations, but it's 50–100× slower. NumPy enables vectorized computation across the entire az/el grid in one call.

**Q: Can I import measured antenna data?**

A: Yes! Any CSV in the tool's format (first row = azimuths, first column = elevations, body = gain in dBi) can be used with analysis, graphing, rotation, and arithmetic operations.

**Q: How do I model a specific commercial antenna?**

A: Configure the closest antenna type (Panel, Horn, etc.) and adjust beamwidth, gain, and sidelobe parameters to match the datasheet. The three-point beamwidth mode helps match frequency-dependent behavior.

**Q: What's the pattern CSV format?**

```csv
0,-180,-179,...,179,180
-90,gain,gain,...,gain,gain
-89,gain,gain,...,gain,gain
...
90,gain,gain,...,gain,gain
```

First row: `0` followed by azimuth angles. First column: elevation angles. Body: gain in dBi.

**Q: Do I need the GUI?**

A: No. The CLI and batch mode are fully independent. Install `customtkinter` and `Pillow` only if you want the graphical interface; the core tool works without them.

**Q: The GUI dropdown is empty / antenna types don't load?**

A: Make sure you are launching from the project root (`python AntennaForge.py`). The tool needs both the project directory and its parent on `sys.path` for imports to resolve correctly — `AntennaForge.py` sets this up automatically.

---

## Changelog

### v1.0 (Current)
- **AntennaForge rebrand** — tool renamed across all files; GUI launcher is `AntennaForge.py`
- **Full GUI** — customtkinter interface with 9 pages (Home, Generate, Visualize, Analysis, Operations, RF Calcs, Reports, How To, Settings)
- **Dark / Light themes** — colour tuples auto-switch; custom accent colour picker
- **Auto-scaling plot viewer** — embedded Prev/Next image browser that resizes to fit the window
- **Tooltips, LabeledSliderEntry, cached-plot detection, Open Folder button**
- **Report section toggle fix** — GUI keys now match backend (`cover_page`, `table_of_contents`, etc.)
- **Relative imports in antenna sub-packages** — fixes empty dropdown when running outside `python -m antenna_tool`
- Added smooth sigmoid transition at ±90° boundary (eliminates heatmap artifacts)
- Separate az/el beamwidth decay configurations
- Radial sidelobe model (elliptical rings)
- PDF and LaTeX report generation with 13 sections
- Gain-beamwidth coupling feature (frequency-dependent gain linked to beamwidth)
- Noise mode selection (uniform, gaussian, quantization)
- Phased array antenna type with steering and Taylor taper
- Native file picker dialogs (tkinter)
- Config schema validation with detailed error messages
- PowerPoint (.pptx) report generation (requires python-pptx)
- Parameter fitting from reference patterns (measurement-seeded + SciPy optimization, coarse-to-fine grid, differential evolution, warm-start cache, unlimited runs with stop button)
- Pattern-set comparison with per-frequency percentage difference tables
- ODESSA .tbl file import
- Batch fitting: fit many pattern sets at once from subfolders with auto-detect, comparison, and report generation
- Dataset batch generator (`scripts/generate_dataset_batch.py`) for large-scale ML training datasets
- Per-type parameter enhancements: Dish feed edge taper, Horn aperture size, Monopole physical length, Panel mechanical tilt (renamed from `panel_downtilt_deg`), Array element patterns (gaussian/cosine/patch), Array RMS errors, Array circular orientation
- GUI type-aware widget visibility: each antenna type shows only its relevant parameters
- Vectorized Array computation path (NumPy broadcasting for all geometries)
- Fix: first generation run now uses a timestamped subdirectory like subsequent runs
- Live preview plots for GUI
- 139 unit tests across core, extended, and boundary suites


---

*Built with ❤️ for RF engineers everywhere.*