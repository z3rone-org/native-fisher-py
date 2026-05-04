import pytest
import os
from native_fisher_py.raw_file import RawFile

def get_raw_file(filename):
    path = os.path.join("test_data", filename)
    raw = RawFile(path)
    return raw

@pytest.fixture(scope="session")
def zoom_file():
    raw = get_raw_file("MS2_MS1_zoom.raw")
    yield raw
    raw.close()

@pytest.fixture(scope="session")
def pxd066718_file():
    raw = get_raw_file("20250411_Ast0_500SPD_EVO685_JVO_EV1107_050ng_HEK-CPR_380-980_2Th_1P5ms_OFF_05_20250413081131.raw")
    yield raw
    raw.close()

@pytest.fixture(scope="session")
def pxd066944_file():
    raw = get_raw_file("20250307_AST0_NEO5_JVO_MV50_DR_100SPD_10ng_HEK_Ref_DDA_2Th_1p5ms_10ms_v2Ref_cycle_03.raw")
    yield raw
    raw.close()

# For backward compatibility with existing generic tests
@pytest.fixture(scope="function")
def zoom_raw_file(zoom_file): return zoom_file
@pytest.fixture(scope="function")
def zoom_raw_path(): return os.path.join("test_data", "MS2_MS1_zoom.raw")
