import importlib.util
import os
import pathlib
import sys
import tempfile
from typing import Any

MODULE_PATH = pathlib.Path(__file__).parent.parent / "Gelfond Constant.py"

def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("gelfond_constant", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_compute_small_digits(tmp_path: pathlib.Path) -> None:
    module = load_module()
    # Change working directory to a temporary folder so output files are created there.
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # 10 digits of e^π are 23.14069263..., without the decimal point:
        expected = "2314069263"
        result = module.compute_gelfond_constant_hpc(10)
        assert result == expected
        # Verify raw digit file exists and contains exactly the expected digits.
        raw_file = tmp_path / f"Gelfond_Constant_10_digits.txt"
        assert raw_file.is_file()
        assert raw_file.read_text(encoding="utf-8") == expected
        # Verify b‑file format (index followed by digit on each line).
        b_file = tmp_path / f"b_file_Gelfond_Constant_10.txt"
        assert b_file.is_file()
        lines = b_file.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 10
        for i, line in enumerate(lines, start=1):
            idx, digit = line.split()
            assert int(idx) == i
            assert digit == expected[i - 1]
    finally:
        os.chdir(cwd)


def test_invalid_digit_count_raises() -> None:
    module = load_module()
    try:
        module.compute_gelfond_constant_hpc(0)
    except ValueError as e:
        assert "positive integer" in str(e)
    else:
        raise AssertionError("ValueError not raised for non‑positive digit count")
