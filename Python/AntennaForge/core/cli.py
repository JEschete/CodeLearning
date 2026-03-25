"""
Command-line interface.

Handles argparse, CLI-mode generation, and dispatches to
interactive menus when no CLI args are provided.
"""

import argparse
import os
import textwrap
from copy import deepcopy

from config import (
    DEFAULT_CONFIG, load_config, save_config,
    generate_frequencies, VERSION,
)
from core.engine import run_generation
from antennas import available_names
from ui.menus import main_menu


def cli_mode(args: argparse.Namespace) -> None:
    """Run generation from CLI arguments."""
    if args.config and os.path.exists(args.config):
        cfg = load_config(args.config)
        print(f"  Loaded config: {args.config}")
    else:
        cfg = deepcopy(DEFAULT_CONFIG)

    if args.type:
        cfg["antenna_type"] = args.type
    if args.max_gain is not None:
        cfg["max_gain_dbi"] = args.max_gain
    if args.az_bw is not None:
        cfg["az_beamwidth_deg"] = args.az_bw
    if args.el_bw is not None:
        cfg["el_beamwidth_deg"] = args.el_bw
    if args.f_min is not None:
        cfg["f_min_mhz"] = args.f_min
    if args.f_max is not None:
        cfg["f_max_mhz"] = args.f_max
    if args.n_slices is not None:
        cfg["n_slices"] = args.n_slices
    if args.spacing:
        cfg["freq_spacing"] = args.spacing
    if args.ftb is not None:
        cfg["ftb_ratio_db"] = args.ftb
    if args.polarization:
        cfg["polarization"] = args.polarization
    if args.pol_angle is not None:
        cfg["pol_angle_deg"] = args.pol_angle
    if args.noise is not None:
        cfg["noise_range_db"] = args.noise
    if args.output:
        cfg["output_dir"] = args.output
    if args.ref_freq is not None:
        cfg["ref_frequency_mhz"] = args.ref_freq
    if args.az_step is not None:
        cfg["az_step_deg"] = args.az_step
    if args.el_step is not None:
        cfg["el_step_deg"] = args.el_step
    if args.sigmoid_k is not None:
        cfg["sigmoid_k"] = args.sigmoid_k

    if cfg["antenna_type"] == "Omni":
        cfg["az_beamwidth_deg"] = 360.0

    # Feature toggles
    feat = cfg["features"]
    if args.no_freq_bw:
        feat["freq_dependent_bw_az"]["enabled"] = False
        feat["freq_dependent_bw_el"]["enabled"] = False
    if args.no_sidelobes:
        feat["sidelobes"]["enabled"] = False
    if args.no_breakup:
        feat["pattern_breakup"]["enabled"] = False
    if args.ground:
        feat["ground_reflection"]["enabled"] = True
    if args.no_ground:
        feat["ground_reflection"]["enabled"] = False
    if args.xpol:
        feat["cross_pol"]["enabled"] = True
    if args.no_vswr:
        feat["vswr_rolloff"]["enabled"] = False
    if args.asymmetry:
        feat["asymmetry"]["enabled"] = True

    freqs = generate_frequencies(
        cfg["f_min_mhz"], cfg["f_max_mhz"],
        cfg["n_slices"], cfg["freq_spacing"]
    )
    run_generation(cfg, freqs)

    if args.save_config:
        save_config(cfg, args.save_config)


def main() -> None:
    """Entry point for both interactive and CLI modes."""
    ant_names = available_names()

    parser = argparse.ArgumentParser(
        description=f"AntennaForge v{VERSION}",
        formatter_class=(
            argparse.RawDescriptionHelpFormatter
        ),
        epilog=textwrap.dedent("""\
            Interactive mode (full menu):
              python -m antenna_tool

            CLI generation:
              python -m antenna_tool --type LPDA \\
                --max-gain 7 --az-bw 65 --el-bw 70 \\
                --f-min 30 --f-max 300 --slices 10

            Batch mode (JSON recipe):
              python -m antenna_tool --batch recipe.json

            CLI with config:
              python -m antenna_tool --config cfg.json
        """)
    )

    parser.add_argument("--config",
                        help="Load settings from JSON")
    parser.add_argument("--save-config",
                        help="Save settings to JSON")
    parser.add_argument("--type",
                        choices=ant_names)
    parser.add_argument("--max-gain", type=float)
    parser.add_argument("--az-bw", type=float)
    parser.add_argument("--el-bw", type=float)
    parser.add_argument("--f-min", type=float)
    parser.add_argument("--f-max", type=float)
    parser.add_argument("--slices", type=int,
                        dest="n_slices")
    parser.add_argument("--spacing",
                        choices=["linear", "log"])
    parser.add_argument("--ref-freq", type=float,
                        help="Reference freq (MHz)")
    parser.add_argument("--ftb", type=float)
    parser.add_argument("--polarization",
                        choices=["vertical",
                                 "horizontal",
                                 "custom"])
    parser.add_argument("--pol-angle", type=float)
    parser.add_argument("--noise", type=float)
    parser.add_argument("--sigmoid-k", type=float,
                        help="Sigmoid sharpness (1-100)")
    parser.add_argument("--output",
                        default="./antenna_patterns")
    parser.add_argument("--az-step", type=float,
                        help="Azimuth step (deg)")
    parser.add_argument("--el-step", type=float,
                        help="Elevation step (deg)")
    parser.add_argument("--batch",
                        help="Run batch JSON recipe")
    parser.add_argument("--batch-dry-run",
                        action="store_true",
                        help="Validate recipe only")
    parser.add_argument("--batch-images",
                        action="store_true",
                        help="Generate plot images for "
                             "each batch job")
    parser.add_argument("--batch-output",
                        help="Base output directory for "
                             "all batch jobs")
    parser.add_argument("--batch-report",
                        action="store_true",
                        help="Generate a PDF report for "
                             "each batch job (requires "
                             "--batch-images)")
    parser.add_argument("--batch-report-preset",
                        choices=["default", "full",
                                 "minimal", "quick"],
                        default="default",
                        help="Report sections preset "
                             "(default: default)")
    parser.add_argument("--report",
                        help="Generate PDF report from dir")
    parser.add_argument("--latex-report",
                        help="Generate LaTeX report from dir")

    fg = parser.add_argument_group("Feature toggles")
    fg.add_argument("--no-freq-bw",
                    action="store_true",
                    help="Disable freq-dependent "
                         "beamwidth")
    fg.add_argument("--no-sidelobes",
                    action="store_true",
                    help="Disable sidelobes")
    fg.add_argument("--no-breakup",
                    action="store_true",
                    help="Disable pattern breakup")
    fg.add_argument("--ground",
                    action="store_true",
                    help="Enable ground reflection")
    fg.add_argument("--no-ground",
                    action="store_true",
                    help="Disable ground reflection")
    fg.add_argument("--xpol",
                    action="store_true",
                    help="Enable cross-pol")
    fg.add_argument("--no-vswr",
                    action="store_true",
                    help="Disable VSWR rolloff")
    fg.add_argument("--asymmetry",
                    action="store_true",
                    help="Enable asymmetry")

    args = parser.parse_args()

    # Batch mode
    if args.batch:
        from core.batch import run_batch
        run_batch(
            args.batch,
            dry_run=args.batch_dry_run,
            generate_images=args.batch_images,
            generate_report=args.batch_report,
            report_preset=args.batch_report_preset,
            output_base=args.batch_output,
            progress_callback=print,
        )
        return

    # Report mode
    if args.report:
        from reporting.report import (
            generate_report,
        )
        generate_report(args.report)
        return

    # LaTeX report mode
    if args.latex_report:
        from reporting.latex_report import (
            generate_latex_report,
        )
        generate_latex_report(args.latex_report)
        return

    has_cli = (args.type is not None
               or args.config is not None)
    if not has_cli:
        main_menu()
    else:
        cli_mode(args)
