#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Generate a CDF file from a NASA CDF skeleton table (.skt).
#
# Requirements:
# - NASA CDF Toolkit installed and `cdfSkeletonCDF` available on PATH,
#   or provide its directory via --cdf-bin.
#
# Usage:
#   python make_cdf_from_skeleton.py path/to/file.skt [--out-dir OUT] [--cdf-bin /usr/local/cdf/bin]
#
# This script will:
# 1) Parse the desired CDF filename from the skeleton's "#header" section ("CDF NAME: ...").
# 2) Run `cdfSkeletonCDF -cdf <skt_path>` to create the CDF.
# 3) Place the created file in --out-dir (default: alongside the .skt) by copying/moving it if needed.
#
# Tip:
# - If you later want to populate data into the created CDF, you can use SpacePy:
#     from spacepy import pycdf
#     with pycdf.CDF('file.cdf', '') as f:
#         f['zVarName'][...] = data_array
#
# (c) 2025 — Ramiz A. Qudsi & collaborators

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def find_cdf_skeletoncdf(cdf_bin_dir: Path | None) -> Path:
    # Try explicit directory first
    if cdf_bin_dir:
        candidate = cdf_bin_dir / "cdfSkeletonCDF"
        if candidate.exists():
            return candidate

    # Try PATH
    found = shutil.which("cdfSkeletonCDF")
    if found:
        return Path(found)

    raise FileNotFoundError(
        "Could not find 'cdfSkeletonCDF'. Add NASA CDF Toolkit to PATH "
        "or pass --cdf-bin pointing to its bin directory."
    )


def parse_cdf_name_from_skt(skt_path: Path) -> str:
    """
    Extract the CDF filename from a line like:
        CDF NAME: lexi_l2_radec_image_0000000000_v0.1.cdf
    Returns the bare filename string (including .cdf).
    """
    name_re = re.compile(r"^\s*CDF NAME:\s*(\S+)\s*$", re.IGNORECASE)
    with skt_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "CDF NAME:" in line:
                m = name_re.match(line.strip())
                if m:
                    return m.group(1)
    raise ValueError("Could not parse 'CDF NAME:' from skeleton file.")


def run_cdf_skeletoncdf(
    cdf_skeletoncdf: Path, skt_path: Path, workdir: Path
) -> subprocess.CompletedProcess:
    """
    Invoke `cdfSkeletonCDF -cdf <skt_path>` in a given working directory.
    Returns the CompletedProcess (stdout/stderr captured).
    """
    cmd = [str(cdf_skeletoncdf), "-cdf", str(skt_path)]
    proc = subprocess.run(
        cmd,
        cwd=str(workdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return proc


def main():
    ap = argparse.ArgumentParser(
        description="Generate a CDF from a NASA CDF skeleton table (.skt)."
    )
    ap.add_argument("skt", type=Path, help="Path to the .skt skeleton file")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory to place the resulting .cdf (default: same as .skt)",
    )
    ap.add_argument(
        "--cdf-bin",
        type=Path,
        default=None,
        help="Directory containing NASA CDF Toolkit binaries (e.g., /usr/local/cdf/bin)",
    )
    ap.add_argument("--verbose", action="store_true", help="Print verbose logs")
    args = ap.parse_args()

    skt_path = args.skt.resolve()
    if not skt_path.exists():
        print(f"[ERROR] Skeleton file not found: {skt_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = (args.out_dir or skt_path.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        cdf_skeletoncdf = find_cdf_skeletoncdf(args.cdf_bin.resolve() if args.cdf_bin else None)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(2)

    # Parse the intended CDF file name from the skeleton
    try:
        cdf_filename = parse_cdf_name_from_skt(skt_path)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(3)

    if args.verbose:
        print(f"[INFO] Parsed CDF filename from skeleton: {cdf_filename}")

    # Run cdfSkeletonCDF
    workdir = skt_path.parent
    proc = run_cdf_skeletoncdf(cdf_skeletoncdf, skt_path, workdir)
    if args.verbose or proc.returncode != 0:
        print("[STDOUT]\n" + proc.stdout)
        print("[STDERR]\n" + proc.stderr, file=sys.stderr)

    if proc.returncode != 0:
        print(f"[ERROR] cdfSkeletonCDF exited with code {proc.returncode}", file=sys.stderr)
        sys.exit(proc.returncode)

    # The tool writes the CDF in the working directory with the parsed name.
    created_cdf = workdir / cdf_filename
    if not created_cdf.exists():
        # Some installations may behave differently—if not found, try to locate any .cdf
        print(f"[WARN] Expected output not found at: {created_cdf}", file=sys.stderr)
        # Fallback: search for newest .cdf nearby
        cdfs = sorted(workdir.glob("*.cdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        if cdfs:
            created_cdf = cdfs[0]
            print(f"[INFO] Using newest CDF found: {created_cdf.name}")
        else:
            print("[ERROR] Could not locate created .cdf file.", file=sys.stderr)
            sys.exit(4)

    # Move/copy to out_dir if different
    final_path = out_dir / created_cdf.name
    if created_cdf.resolve() != final_path:
        shutil.copy2(created_cdf, final_path)
        if args.verbose:
            print(f"[INFO] Copied CDF to: {final_path}")
    else:
        if args.verbose:
            print(f"[INFO] CDF already in target location: {final_path}")

    # Stamp a simple log line
    print(f"[OK] CDF generated: {final_path}")
    print(f"[INFO] Timestamp: {datetime.utcnow().isoformat()}Z")


if __name__ == "__main__":
    main()
