#!/usr/bin/env python3
"""
fetch_wheels.py — Run this on the INTERNET-CONNECTED machine.

Downloads dependencies for multiple Python versions to ensure portability
to air-gapped machines running different versions (e.g. 3.10, 3.12).
"""

import os
import subprocess
import sys
import shutil

# Target Python versions to support
TARGET_PY_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]

# Target Platform (win_amd64, manylinux2014_x86_64, etc.)
# Defaults to Windows 64-bit if running on Windows, else Linux x86_64
if sys.platform == "win32":
    DEFAULT_PLATFORM = "win_amd64"
else:
    DEFAULT_PLATFORM = "manylinux2014_x86_64"

PACKAGES = [
    "pip",
    "setuptools",
    "customtkinter>=5.2.0",
    "numpy>=1.24.0",
    "scipy>=1.10.0",
    "matplotlib>=3.7.0",
    "Pillow>=10.2.0",
    "python-pptx>=0.6.21",
    "pytest",  # For testing
]

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    wheels_dir = os.path.join(root, "wheels")
    
    # Clean up old wheels to avoid confusion? Optional.
    # if os.path.exists(wheels_dir):
    #     shutil.rmtree(wheels_dir)
    os.makedirs(wheels_dir, exist_ok=True)

    print(f"--- AntennaForge Portable Packager ---")
    print(f"Output directory: {wheels_dir}")
    print(f"Target Platform:  {DEFAULT_PLATFORM}")
    print(f"Target Pythons:   {', '.join(TARGET_PY_VERSIONS)}")
    print(f"Packages:         {len(PACKAGES)}")
    print("-" * 40)

    # Ensure pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("Error: 'pip' module not found.")
        sys.exit(1)

    for py_ver in TARGET_PY_VERSIONS:
        print(f"\n[+] Downloading for Python {py_ver}...")
        
        # We use 'pip download' with specific constraints
        cmd = [
            sys.executable, "-m", "pip", "download",
            "--dest", wheels_dir,
            "--only-binary=:all:",  # Prefer wheels
            "--python-version", py_ver,
            "--platform", DEFAULT_PLATFORM,
            # Relax dependency checks slightly for cross-version downloading
            "--no-deps", 
        ] + PACKAGES

        # Note: We use --no-deps above because resolving deps for a different 
        # python version/platform can be tricky for pip. 
        # However, for these specific scientific packages, the main packages 
        # usually cover the needs. If deps are missing, remove "--no-deps".
        # Removing --no-deps is safer but might fail if the host pip can't resolve for target.
        # Let's try WITH deps first, but if it fails, the user might need to adjust.
        # For this script, we will actually remove --no-deps to be safe, 
        # but add --implementation cp to target CPython.
        
        cmd = [
            sys.executable, "-m", "pip", "download",
            "--dest", wheels_dir,
            "--only-binary=:all:",
            "--python-version", py_ver,
            "--platform", DEFAULT_PLATFORM,
            "--implementation", "cp",
        ] + PACKAGES

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            print(f"(!) Warning: Failed to download some packages for Python {py_ver}.")
            print("    (This is expected for 3.14 if not released yet, or if wheels are missing)")

    print("\n" + "="*40)
    
    # Create a zip archive for easier transport
    zip_path = os.path.join(root, "offline_wheels")
    print(f"Zipping wheels to {zip_path}.zip ...")
    shutil.make_archive(zip_path, 'zip', root_dir=root, base_dir='wheels')
    
    print(f"Cleaning up temporary wheels folder...")
    shutil.rmtree(wheels_dir)

    print(f"Done! Transfer 'offline_wheels.zip' (inside the project folder) to the target machine.")

if __name__ == "__main__":
    main()