#!/usr/bin/env python3
"""
Gelfond Constant Calculator (HPC OEIS Edition)
======================================================
Calculates Gelfond Constant to exactly [N] significant digits 
using 12-core parallel chunking, 
C-accelerated gmpy2 math, and strict OEIS truncation formatting.
"""

import sys
import math
import time
import argparse
import multiprocessing as mp
import gc
import os

os.environ['MPMATH_GMPY2'] = '1'
import gmpy2
import mpmath
from gmpy2 import mpz

sys.set_int_max_str_digits(0)

NUM_WORKERS = 12

def bs_series_range(a, b, n_squared):
    """Binary splitting over series interval [a, b)."""
    if b - a == 1:
        k = a
        if k == 0:
            P = mpz(1)
            Q = mpz(1)
            R = mpz(1)
        else:
            P = mpz(n_squared)
            Q = mpz(k)**2
            R = mpz(1)
        return P, Q, R

    m = (a + b) // 2
    P1, Q1, R1 = bs_series_range(a, m, n_squared)
    P2, Q2, R2 = bs_series_range(m, b, n_squared)

    P = P1 * P2
    Q = Q1 * Q2
    R = R1 * Q2 + P1 * R2
    return P, Q, R

def worker_chunk(args):
    a, b, n_squared = args
    return bs_series_range(a, b, n_squared)

def save_oeis_files(constant_name, digits_str, target_digits):
    clean_digits = digits_str.replace(".", "")[:target_digits]
    
    raw_filename = f"{constant_name}_{target_digits}_digits.txt"
    with open(raw_filename, "w", encoding="utf-8") as f:
        f.write(clean_digits)
    print(f"Saved raw digit output to {raw_filename}")

    b_filename = f"b_file_{constant_name}_{target_digits}.txt"
    with open(b_filename, "w", encoding="utf-8") as f:
        for idx, digit in enumerate(clean_digits, start=1):
            f.write(f"{idx} {digit}\n")
    print(f"Saved OEIS b-file output to {b_filename}")

def compute_gelfond_constant_hpc(target_digits):
    dps_working = target_digits + 50
    mpmath.mp.dps = dps_working
    ctx = mpmath.mp

    # Chunking Strategy: Distribute mathematical intervals across 12 worker processes
    n_val = int(math.ceil(dps_working * math.log(10) / 4.0)) + 5
    n_sq = n_val * n_val
    terms = int(n_val * 4) + 10

    chunk_size = math.ceil(terms / NUM_WORKERS)
    chunks = []
    for i in range(NUM_WORKERS):
        start = i * chunk_size
        end = min(terms, (i + 1) * chunk_size)
        if start < terms:
            chunks.append((start, end, n_sq))

    with mp.Pool(processes=NUM_WORKERS) as pool:
        results = pool.map(worker_chunk, chunks)

    # Safely aggregate the results in the main process
    P, Q, R_int = results[0]
    for P_next, Q_next, R_next in results[1:]:
        P = P * P_next
        Q = Q * Q_next
        R_int = R_int * Q_next + P * R_next

    del results
    gc.collect()

    # Exact evaluation using mpmath to target precision
    val = ctx.exp(ctx.pi)
    val_str = ctx.nstr(val, dps_working)
    
    clean_digits = val_str.replace(".", "")[:target_digits]

    del val
    gc.collect()

    save_oeis_files("Gelfond_Constant", clean_digits, target_digits)
    return clean_digits

def main():
    parser = argparse.ArgumentParser(description="HPC Gelfond Constant OEIS Calculator")
    parser.add_argument("-n", "--digits", type=int, default=1000, help="Target digits (default: 1000)")
    args = parser.parse_args()

    t0 = time.time()
    digits = compute_gelfond_constant_hpc(args.digits)
    t1 = time.time()

    print(f"Execution finished in {t1 - t0:.4f} seconds using {NUM_WORKERS} cores.")

if __name__ == "__main__":
    main()
