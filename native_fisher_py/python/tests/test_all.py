import pytest
import thermo_raw_native


def test_sum_as_string():
    assert thermo_raw_native.sum_as_string(1, 1) == "2"
