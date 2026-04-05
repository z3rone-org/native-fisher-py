import native_fisher_py as nfp
import pytest
import os

def test_import():
    assert nfp.open_raw_file is not None

def test_open_fail():
    # Should return -1 for non-existent file
    assert nfp.open_raw_file("nonexistent.raw") == -1
