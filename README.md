# Gelfond Constant Calculator (HPC OEIS Edition)

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![HPC Ready](https://img.shields.io/badge/HPC-Optimized-brightgreen)


Calculates Gelfond Constant to an arbitrary precision of [N] significant digits using a highly optimized 12-core parallelized algorithm.

Architecture & Features:
- 12-core multiprocessing pool for chunked interval mathematical evaluation.
- C-accelerated arithmetic via gmpy2 and mpmath.
- Precision safety buffer of 50 digits to prevent truncation rounding errors.
- Strict OEIS formatting: Outputs both a raw digit file and an OEIS b-file index.

## Usage

```bash
python "Gelfond Constant.py" -n 1000
```

This will output the 1000-digit precision results formatted for OEIS submission.
