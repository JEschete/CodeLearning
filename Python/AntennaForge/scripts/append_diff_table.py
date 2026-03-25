#!/usr/bin/env python3
"""
Script to parse two pattern analysis tables from a text file and append a
percentage difference table.

Usage:
    python append_diff_table.py ["path/to/Output Analysis.txt"]
    (If no argument is provided, a file picker dialog will open)
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog

def parse_table_data(lines, start_marker):
    """Finds and parses a table following the start_marker."""
    start_idx = -1
    for i, line in enumerate(lines):
        if start_marker in line:
            start_idx = i
            break
    
    if start_idx == -1:
        return None, -1

    data = []
    # Look for the separator line "---" to start reading data
    data_start = -1
    for i in range(start_idx, len(lines)):
        # Check for separator line (e.g. "  ------")
        if set(lines[i].strip()) == {'-'}:
            data_start = i + 1
            break
    
    if data_start == -1:
        return None, -1

    current_idx = data_start
    while current_idx < len(lines):
        line = lines[current_idx].strip()
        # Stop at empty line or next section header (starts with =)
        if not line or line.startswith('='):
            break
        
        parts = line.split()
        # Expecting: File Peak Bore AzBW ElBW Min
        if len(parts) >= 6:
            try:
                entry = {
                    'file': parts[0],
                    'peak': float(parts[1]),
                    'bore': float(parts[2]),
                    'azbw': float(parts[3]),
                    'elbw': float(parts[4]),
                    'min': float(parts[5])
                }
                data.append(entry)
            except ValueError:
                pass # Skip lines that don't parse as floats
        current_idx += 1
        
    return data, current_idx

def calculate_pct_diff(val1, val2):
    """Calculates % difference relative to val1."""
    if val1 == 0:
        return 0.0 if val2 == 0 else float('inf')
    # (New - Old) / |Old| * 100
    return (val2 - val1) / abs(val1) * 100.0

def main():
    filepath = ""
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
    else:
        print("No file argument provided. Opening file picker...")
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Select Analysis Output File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        root.destroy()

    if not filepath:
        print("No file selected.")
        return

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()

    table1, _ = parse_table_data(lines, "PATTERN 1 COMPARISON")
    table2, _ = parse_table_data(lines, "PATTERN 2 COMPARISON")

    if not table1 or not table2:
        print("Error: Could not find both PATTERN 1 and PATTERN 2 tables.")
        return

    # Determine rows to process (min length handles shorter/longer tables safely)
    num_rows = min(len(table1), len(table2))
    
    output_lines = []
    # Ensure we start on a new line if file doesn't end with one
    if lines and not lines[-1].endswith('\n'):
        output_lines.append("\n")

    output_lines.append("\n")
    output_lines.append(" " + "=" * 60 + "\n")
    output_lines.append("  PERCENTAGE DIFFERENCE ( (P2 - P1) / |P1| * 100 )\n")
    output_lines.append(" " + "=" * 60 + "\n")
    
    # Header matching the style of the input
    # File column ~33 chars, others ~7 chars
    header = f"  {'File':<33} {'Peak%':>7} {'Bore%':>7} {'AzBW%':>7} {'ElBW%':>7} {'Min%':>7}\n"
    output_lines.append(header)
    output_lines.append("  " + "-" * 60 + "\n")

    for i in range(num_rows):
        r1 = table1[i]
        r2 = table2[i]
        
        fname = r1['file']
        
        # Calculate diffs
        d_peak = calculate_pct_diff(r1['peak'], r2['peak'])
        d_bore = calculate_pct_diff(r1['bore'], r2['bore'])
        d_azbw = calculate_pct_diff(r1['azbw'], r2['azbw'])
        d_elbw = calculate_pct_diff(r1['elbw'], r2['elbw'])
        d_min = calculate_pct_diff(r1['min'], r2['min'])
        
        row_str = (f"  {fname:<33} "
                   f"{d_peak:>7.2f} {d_bore:>7.2f} {d_azbw:>7.2f} "
                   f"{d_elbw:>7.2f} {d_min:>7.2f}\n")
        output_lines.append(row_str)

    # Append to file
    try:
        with open(filepath, 'a') as f:
            f.writelines(output_lines)
        print(f"Successfully appended difference table to {filepath}")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()