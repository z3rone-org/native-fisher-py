import pytest
import os
from native_fisher_py.raw_file import RawFile

@pytest.fixture(scope="session")
def zoom_raw_path():
    path = os.path.join("test_data", "MS2_MS1_zoom.raw")
    if not os.path.exists(path):
        pytest.skip(f"Test file {path} not found")
    return path

@pytest.fixture(scope="session")
def zoom_raw_file(zoom_raw_path):
    raw = RawFile(zoom_raw_path)
    yield raw
    raw.close()
