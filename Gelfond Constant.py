#!/usr/bin/env python3
"""
Gelfond Constant Calculator (HPC OEIS Edition)
======================================================
Calculates the Gelfond constant (e**π) to exactly *N* significant digits.
The original implementation used a heavyweight binary‑splitting routine and
12‑process parallelism, but the actual value is obtained directly via
``mpmath``.  The parallel code was never used for the final result and added
unnecessary overhead and complexity.

This rewrite preserves the public CLI (`-n/--digits`) and the exact output
format required by the OEIS (a raw digit file and a *b‑file* with index/value
pairs) while simplifying the implementation, adding type hints, docstrings,
and removing dead code.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Tuple

import mpmath

# The original script forced an unlimited integer string length.  Keeping the
# behaviour for compatibility with very large digit counts.
sys.set_int_max_str_digits(0)

# The constant name used in the generated file names – kept identical to the
# original script.
_CONSTANT_NAME = "Gelfond_Constant"


def _save_oeis_files(constant_name: str, digits: str, target_digits: int) -> None:
    """Write the raw digit file and the OEIS *b‑file*.

    Parameters
    ----------
    constant_name:
        Base name used for the output files.
    digits:
        The string of decimal digits (without a decimal point) representing
        the constant, already truncated to ``target_digits``.
    target_digits:
        Number of digits that were requested – also used in the file names.
    """
    # Ensure we only write the requested number of digits.
    clean_digits = digits[:target_digits]

    raw_path = Path(f"{constant_name}_{target_digits}_digits.txt")
    raw_path.write_text(clean_digits, encoding="utf-8")
    print(f"Saved raw digit output to {raw_path}")

    b_path = Path(f"b_file_{constant_name}_{target_digits}.txt")
    with b_path.open("w", encoding="utf-8") as f:
        for idx, digit in enumerate(clean_digits, start=1):
            f.write(f"{idx} {digit}\n")
    print(f"Saved OEIS b-file output to {b_path}")


def compute_gelfond_constant_hpc(target_digits: int) -> str:
    """Return the first ``target_digits`` decimal digits of *e*⁽π⁾.

    The function computes the constant with a small safety margin (50 extra
    digits) to guarantee correct rounding after truncation, then writes the
    OEIS‑compatible files.  The returned string contains only the digits (no
    decimal point).
    """
    if target_digits <= 0:
        raise ValueError("target_digits must be a positive integer")

    # Extra precision guards against rounding errors when the final string is
    # truncated.  50 digits is more than sufficient for the ranges used in the
    # original script.
    working_dps = target_digits + 50
    mpmath.mp.dps = working_dps

    # Direct evaluation using mpmath – this is both fast and exact to the
    # requested precision.
    value = mpmath.e ** mpmath.pi
    # ``nstr`` returns a string with a decimal point; we strip it and keep the
    # required number of digits.
    digit_str = mpmath.nstr(value, working_dps).replace(".", "")[:target_digits]

    _save_oeis_files(_CONSTANT_NAME, digit_str, target_digits)
    return digit_str


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command‑line arguments.

    The helper exists to make the module easier to test – ``argv`` can be
    supplied explicitly.
    """
    parser = argparse.ArgumentParser(description="HPC Gelfond Constant OEIS Calculator")
    parser.add_argument(
        "-n",
        "--digits",
        type=int,
        default=1000,
        help="Target digits (default: 1000)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point used by the ``__main__`` guard.

    It measures execution time and prints a short summary, mirroring the
    original script's behaviour.
    """
    args = _parse_args(argv)
    start = time.time()
    _ = compute_gelfond_constant_hpc(args.digits)
    elapsed = time.time() - start
    print(f"Execution finished in {elapsed:.4f} seconds using 1 core.")


if __name__ == "__main__":
    main()
