import pytest
import os
from native_fisher_py.raw_file import RawFile


@pytest.fixture(scope="session")
def zoom_raw_path():
    path = os.path.join("test_data", "MS2_MS1_zoom.raw")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test file {path} not found")
    return path


@pytest.fixture(scope="session")
def zoom_raw_file(zoom_raw_path):
    raw = RawFile(zoom_raw_path)
    yield raw
    raw.close()


@pytest.fixture(scope="session")
def angiotensin_raw_file():
    path = os.path.join("test_data", "Angiotensin_AllScans.raw")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test file {path} not found")
    raw = RawFile(path)
    yield raw
    raw.close()


@pytest.fixture(scope="session")
def prec_range_raw_file():
    path = os.path.join("test_data", "PXD006873_prec_range.raw")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Test file {path} not found")
    raw = RawFile(path)
    yield raw
    raw.close()
