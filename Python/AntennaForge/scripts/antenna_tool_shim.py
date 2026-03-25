#!/usr/bin/env python3
"""
AntennaForge v1.0 — Backwards Compatibility Shim
=========================================================
This file allows `python antenna_tool.py` to work exactly
as before. All logic lives in the antenna_tool/ package.

For new scripts, prefer:
    python -m antenna_tool
    or:
    from config import DEFAULT_CONFIG
    from core.engine import compute_pattern, run_generation
    etc.
"""

# Re-export everything that old code might have imported
# from the monolith via `from antenna_tool import *`
from config import (                     # noqa
    DEFAULT_CONFIG, save_config, load_config,
    generate_frequencies,
)
from core.pattern_math import (          # noqa
    bw_to_exponent,
    compute_freq_dependent_bw,
    compute_sidelobe_envelope,
    apply_pattern_breakup,
    apply_ground_reflection,
    compute_cross_pol,
    apply_vswr_rolloff,
    apply_asymmetry,
)
from core.engine import (                # noqa
    compute_pattern, run_generation,
)
from core.io import (                    # noqa
    write_pattern_file, read_pattern_file,
    extract_freq_from_filename,
    make_timestamped_dir, make_graph_output_dir,
)
from analysis.analyzer import (          # noqa
    analyze_single, measure_beamwidth,
    find_first_sidelobe,
    check_symmetry_az, check_symmetry_el,
    compare_patterns,
)
from core.cli import main


if __name__ == "__main__":
    main()
