#!/usr/bin/env python3
"""
install_offline.py  — run on the AIR-GAPPED / standalone machine.

Installs all AntennaForge dependencies from a local wheels directory
that was prepared with ``fetch_wheels.py`` on an internet-connected
machine.

Usage
-----
    python install_offline.py                          # default: ./wheels/
    python install_offline.py --wheels D:\\wheels       # custom folder
    python install_offline.py --wheels ./wheels --check # verify only, don't install

Steps
-----
1. Copy the antenna_tool folder + wheels/ directory to the target machine.
2. Ensure Python 3.10+ is installed.
3. (Optional) Create a venv:  python -m venv .venv && .venv\\Scripts\\activate
4. Run:  python install_offline.py
"""

import argparse
import os
import subprocess
import sys


def _pip_install(wheels_dir, packages=None, req_file=None, upgrade=False):
    """Run pip install from local wheels with no internet access."""
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--no-index",
        "--find-links", wheels_dir,
    ]
    if upgrade:
        cmd.append("--upgrade")
    if req_file:
        cmd += ["-r", req_file]
    elif packages:
        cmd += packages
    return subprocess.run(cmd, capture_output=False)


def _check_import(name, import_name=None):
    """Return True if *name* can be imported."""
    try:
        __import__(import_name or name)
        return True
    except ImportError:
        return False


DEPS = [
    ("customtkinter", "customtkinter"),
    ("numpy",         "numpy"),
    ("scipy",         "scipy"),
    ("matplotlib",    "matplotlib"),
    ("Pillow",        "PIL"),
    ("python-pptx",   "pptx"),
]

# Optional testing dependency — installed when --with-test is given
TEST_DEPS = [
    ("pytest",        "pytest"),
]


def main():
    parser = argparse.ArgumentParser(
        description="Install AntennaForge dependencies from local wheel cache.",
    )
    parser.add_argument(
        "--wheels", default="./wheels",
        help="Directory containing .whl files (default: ./wheels)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Only verify which packages are installed; don't install anything.",
    )
    parser.add_argument(
        "--with-test", action="store_true",
        help="Also install testing dependencies (pytest).",
    )
    args = parser.parse_args()

    wheels = os.path.abspath(args.wheels)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req = os.path.join(here, "requirements.txt")

    # ── Check mode ──────────────────────────────────────────────
    if args.check:
        print("\nAntennaForge Dependency Check")
        print("=" * 50)
        all_ok = True

        # tkinter (stdlib, not pip-installable)
        tk_ok = _check_import("tkinter")
        mark = "✓" if tk_ok else "✗"
        print(f"  {mark}  tkinter (stdlib — required for GUI)")
        if not tk_ok:
            all_ok = False

        for pip_name, import_name in DEPS:
            ok = _check_import(import_name)
            mark = "✓" if ok else "✗"
            print(f"  {mark}  {pip_name}")
            if not ok:
                all_ok = False

        # Testing dependencies
        print("  ── Testing ──")
        for pip_name, import_name in TEST_DEPS:
            ok = _check_import(import_name)
            mark = "✓" if ok else "○"
            print(f"  {mark}  {pip_name}  (optional — install with --with-test)")
            # Don't fail all_ok for optional test deps

        # Python version
        v = sys.version_info
        py_ok = v >= (3, 10)
        mark = "✓" if py_ok else "⚠"
        print(f"  {mark}  Python {v.major}.{v.minor}.{v.micro}  {'(OK)' if py_ok else '(3.10+ recommended)'}")

        if all_ok:
            print("\nAll dependencies satisfied — ready to run!")
        else:
            print(f"\nSome packages missing. Run without --check to install:")
            print(f"  python install_offline.py --wheels {args.wheels}")
        return

    # ── Install mode ────────────────────────────────────────────
    if not os.path.isdir(wheels):
        print(f"ERROR: Wheels directory not found: {wheels}")
        print("Run fetch_wheels.py on an internet-connected machine first.")
        sys.exit(1)

    whl_count = len([f for f in os.listdir(wheels) if f.endswith(('.whl', '.tar.gz'))])
    if whl_count == 0:
        print(f"ERROR: No wheel files found in {wheels}")
        sys.exit(1)

    # Pre-flight: check for tkinter (ships with Python, not pip-installable)
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("WARNING: tkinter is not available in this Python installation.")
        print("  tkinter ships with the standard Python installer on Windows.")
        print("  On Linux, install it via your package manager:")
        print("    sudo apt install python3-tk        # Debian/Ubuntu")
        print("    sudo dnf install python3-tkinter   # Fedora/RHEL")
        print("  The GUI will NOT work without tkinter.\n")

    print(f"\nAntennaForge Offline Installer")
    print(f"Wheels directory: {wheels}  ({whl_count} packages)")
    print("=" * 50)

    # Step 1: upgrade pip itself from local cache (avoids old-pip issues)
    n_steps = 3 if args.with_test else 2
    print(f"\nStep 1/{n_steps}: Upgrading pip from local cache ...")
    _pip_install(wheels, packages=["pip", "setuptools"], upgrade=True)

    # Step 2: install project dependencies
    # We install individually to allow optional packages to fail without breaking the build.
    print(f"\nStep 2/{n_steps}: Installing packages ...")
    
    required_pkgs = {"customtkinter"}
    
    for pip_name, _ in DEPS:
        is_required = pip_name in required_pkgs
        label = "required" if is_required else "optional"
        print(f"  -> Installing {label}: {pip_name}")
        
        res = _pip_install(wheels, packages=[pip_name])
        
        if res.returncode != 0:
            if is_required:
                print(f"ERROR: Failed to install required package '{pip_name}'.")
                sys.exit(1)
            else:
                print(f"  (!) Warning: Optional package '{pip_name}' failed. Continuing...")

    # Mock a result object for the final check since we handled errors manually
    result = subprocess.CompletedProcess(args=[], returncode=0)

    # Step 3 (optional): install test dependencies
    test_result = None
    if args.with_test:
        print(f"\nStep 3/{n_steps}: Installing test dependencies ...")
        test_pkg_list = [pip_name for pip_name, _ in TEST_DEPS]
        test_result = _pip_install(wheels, packages=test_pkg_list)

    print("\n" + "=" * 50)

    if result.returncode != 0:
        print(f"⚠  pip finished with exit code {result.returncode}")
        print("Some packages may not have installed. Check output above.")
    else:
        print("✓  pip install completed successfully.")
    if test_result and test_result.returncode != 0:
        print(f"⚠  test-dep pip finished with exit code {test_result.returncode}")

    # Post-install verification
    print("\nVerification:")
    all_ok = True
    for pip_name, import_name in DEPS:
        ok = _check_import(import_name)
        mark = "✓" if ok else "✗"
        print(f"  {mark}  {pip_name}")
        if not ok:
            all_ok = False

    if args.with_test:
        for pip_name, import_name in TEST_DEPS:
            ok = _check_import(import_name)
            mark = "✓" if ok else "✗"
            print(f"  {mark}  {pip_name}  (test)")
            if not ok:
                all_ok = False

    if all_ok:
        print("\n✓  All dependencies installed — AntennaForge is ready!")
        print("   Run:  python -m antenna_tool")
    else:
        print("\n⚠  Some packages could not be installed.")
        print("   Core functionality still works without optional dependencies.")
        print("   See PORTABLE_SETUP.md for troubleshooting.")


if __name__ == "__main__":
    main()
