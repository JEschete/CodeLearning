"""
Feature toggle display and interactive configuration.
"""

from ui.prompts import (
    prompt_choice, prompt_float, prompt_int, prompt_yn,
)


def display_feature_status(cfg: dict) -> None:
    """Print feature status table."""
    print()
    hdr = ("  +----+---------------------------"
           "-------------------+--------+")
    print(hdr)
    print("  |  # | Feature            "
          "                     | Status |")
    sep = ("  +----+---------------------------"
           "-------------------+--------+")
    print(sep)
    for i, (key, feat) in enumerate(
            cfg["features"].items(), 1):
        marker = "x" if feat["enabled"] else " "
        status = "  ON " if feat["enabled"] else " OFF "
        name = feat.get("description", key)[:42]
        print(f"  | {i:>2} | {name:<42} |[{marker}]"
              f"{status}|")
    print(hdr)


def _select_bw_decay_mode(feat: dict, plane_label: str) -> str:
    """Prompt user to select the beamwidth decay mode.

    Sets feat['decay_mode'] and returns the chosen mode string.
    """
    print(f"\n  {plane_label} Beamwidth Decay Mode:")
    print("    [1] Exponent  - Beamwidth = base * "
          "(f_ref/f)^exp")
    print("    [2] Percent   - Beamwidth decays by X% "
          "per octave")
    print("    [3] 3-Point   - Specify beamwidth at "
          "start/mid/end freq")
    mode_choice = prompt_choice(
        f"  {plane_label} decay mode:",
        ["exponent", "percentage", "three_point"],
        default=feat.get("decay_mode", "exponent")
    )
    feat["decay_mode"] = mode_choice
    return mode_choice


def _configure_bw_decay(cfg: dict, feat: dict, plane_label: str,
                        ask_mode: bool = True) -> None:
    """Shared config prompts for az or el beamwidth decay.

    plane_label: 'Az' or 'El' for display purposes.
    If ask_mode is False, skips mode selection (assumes
    feat['decay_mode'] is already set).

    For exponent and percentage modes, prompts for the base
    beamwidth at the reference frequency. For three_point
    mode, the user specifies beamwidths at 3 frequencies
    directly so no separate base beamwidth is needed.
    """
    bw_key = ("az_beamwidth_deg" if plane_label == "Az"
              else "el_beamwidth_deg")
    max_ceil = 180 if plane_label == "Az" else 90

    if ask_mode:
        _select_bw_decay_mode(feat, plane_label)

    mode_choice = feat["decay_mode"]

    if mode_choice in ("exponent", "percentage"):
        # Ask for the base beamwidth at the reference freq
        cfg[bw_key] = prompt_float(
            f"  {plane_label} 3dB beamwidth at ref "
            f"freq (deg)",
            default=cfg[bw_key],
            min_val=1, max_val=360
        )

    if mode_choice == "exponent":
        feat["scaling_exponent"] = prompt_float(
            f"  {plane_label} scaling exponent "
            "(1.0=inv linear, 0.5=sqrt)",
            default=feat["scaling_exponent"],
            min_val=0.1, max_val=2.0
        )
        if cfg["antenna_type"] == "LPDA":
            feat["lpda_variation_factor"] = prompt_float(
                f"  {plane_label} LPDA variation "
                "(0=const, 1=full)",
                default=feat["lpda_variation_factor"],
                min_val=0, max_val=1.0
            )

    elif mode_choice == "percentage":
        feat["decay_pct_per_octave"] = prompt_float(
            f"  {plane_label} reduction per octave (%)",
            default=feat.get(
                "decay_pct_per_octave", 15.0),
            min_val=0, max_val=80
        )

    elif mode_choice == "three_point":
        print(f"\n  Enter {plane_label} beamwidth at "
              f"3 frequencies.")
        print(f"  f_start = {cfg['f_min_mhz']} MHz")
        print(f"  f_mid   = "
              f"{(cfg['f_min_mhz']+cfg['f_max_mhz'])/2}"
              f" MHz")
        print(f"  f_end   = {cfg['f_max_mhz']} MHz")
        base_bw = cfg.get(bw_key, 65.0)
        feat["three_point_start_deg"] = prompt_float(
            f"  {plane_label} beamwidth at f_start (deg)",
            default=feat.get("three_point_start_deg")
            or base_bw,
            min_val=1, max_val=360
        )
        feat["three_point_mid_deg"] = prompt_float(
            f"  {plane_label} beamwidth at f_mid (deg)",
            default=feat.get("three_point_mid_deg")
            or base_bw,
            min_val=1, max_val=360
        )
        feat["three_point_end_deg"] = prompt_float(
            f"  {plane_label} beamwidth at f_end (deg)",
            default=feat.get("three_point_end_deg")
            or base_bw * 0.75,
            min_val=1, max_val=360
        )
        # Set the base beamwidth to the mid-point value
        # so downstream code has a consistent reference.
        cfg[bw_key] = feat["three_point_mid_deg"]

    feat["min_bw_deg"] = prompt_float(
        f"  {plane_label} min beamwidth floor (deg)",
        default=feat["min_bw_deg"],
        min_val=1, max_val=90
    )
    feat["max_bw_deg"] = prompt_float(
        f"  {plane_label} max beamwidth ceiling (deg)",
        default=feat["max_bw_deg"],
        min_val=10, max_val=max_ceil
    )


def configure_feature(cfg: dict, feature_key: str) -> None:
    """Interactive configuration for a single feature."""
    feat = cfg["features"][feature_key]
    print(f"\n  -- {feat['description']} --")
    feat["enabled"] = prompt_yn(
        f"  Enable {feature_key}?",
        default=feat["enabled"]
    )
    if not feat["enabled"]:
        return

    if feature_key in (
        "freq_dependent_bw_az", "freq_dependent_bw_el"
    ):
        plane = "Az" if "az" in feature_key else "El"
        _configure_bw_decay(cfg, feat, plane)

    elif feature_key == "sidelobes":
        feat["type"] = prompt_choice(
            "  Sidelobe model:",
            ["taylor", "uniform"],
            default=feat["type"]
        )
        feat["first_sidelobe_db"] = prompt_float(
            "  First sidelobe level (dB, negative)",
            default=feat["first_sidelobe_db"], max_val=0
        )
        feat["decay_rate_db"] = prompt_float(
            "  Decay rate (dB/lobe)",
            default=feat["decay_rate_db"], min_val=0
        )
        feat["n_sidelobes"] = prompt_int(
            "  Number of sidelobe pairs",
            default=feat["n_sidelobes"],
            min_val=1, max_val=20
        )

    elif feature_key == "pattern_breakup":
        feat["onset_angle_deg"] = prompt_float(
            "  Onset angle from boresight (deg)",
            default=feat["onset_angle_deg"],
            min_val=30, max_val=170
        )
        feat["ripple_amplitude_db"] = prompt_float(
            "  Ripple amplitude (dB)",
            default=feat["ripple_amplitude_db"],
            min_val=0, max_val=20
        )
        feat["ripple_density"] = prompt_float(
            "  Ripple spatial density",
            default=feat["ripple_density"],
            min_val=0.5, max_val=20
        )

    elif feature_key == "ground_reflection":
        feat["height_wavelengths"] = prompt_float(
            "  Antenna height (wavelengths at ref freq)",
            default=feat["height_wavelengths"],
            min_val=0.1, max_val=50
        )
        feat["reflection_coeff"] = prompt_float(
            "  Reflection coefficient (0-1)",
            default=feat["reflection_coeff"],
            min_val=0, max_val=1.0
        )
        feat["ground_type"] = prompt_choice(
            "  Ground type:",
            ["perfect", "good_soil",
             "poor_soil", "sea_water"],
            default=feat["ground_type"]
        )

    elif feature_key == "cross_pol":
        feat["boresight_isolation_db"] = prompt_float(
            "  Boresight isolation (dB, negative)",
            default=feat["boresight_isolation_db"],
            max_val=0
        )
        feat["peak_angle_deg"] = prompt_float(
            "  Cross-pol peak angle off boresight (deg)",
            default=feat["peak_angle_deg"],
            min_val=0, max_val=90
        )
        feat["max_cross_pol_db"] = prompt_float(
            "  Max cross-pol rel. co-pol (dB, neg)",
            default=feat["max_cross_pol_db"],
            max_val=0
        )

    elif feature_key == "vswr_rolloff":
        feat["rolloff_band_fraction"] = prompt_float(
            "  Band edge fraction (0-0.5)",
            default=feat["rolloff_band_fraction"],
            min_val=0.01, max_val=0.5
        )
        feat["max_rolloff_db"] = prompt_float(
            "  Max rolloff at edge (dB)",
            default=feat["max_rolloff_db"],
            min_val=0, max_val=20
        )
        feat["rolloff_shape"] = prompt_choice(
            "  Rolloff shape:",
            ["cosine", "linear"],
            default=feat["rolloff_shape"]
        )

    elif feature_key == "asymmetry":
        feat["az_squint_deg"] = prompt_float(
            "  Az squint (deg, +=right)",
            default=feat["az_squint_deg"],
            min_val=-45, max_val=45
        )
        feat["el_tilt_deg"] = prompt_float(
            "  El tilt (deg, +=up)",
            default=feat["el_tilt_deg"],
            min_val=-45, max_val=45
        )
        feat["random_asymmetry_db"] = prompt_float(
            "  Random asymmetry amplitude (dB)",
            default=feat["random_asymmetry_db"],
            min_val=0, max_val=10
        )
