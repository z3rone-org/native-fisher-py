import pytest
from native_fisher_py.raw_file import RawFile
from native_fisher_py.data.classes import SampleType

@pytest.fixture
def raw_file():
    raw = RawFile("test_data/MS2_MS1_orbitrap.raw")
    yield raw
    raw.close()

def test_sample_information(raw_file):
    info = raw_file.sample_information
    
    assert info.barcode_status == 0  # FIXME: Placeholder - We have no test file for this value
    assert info.calibration_file == ""  # FIXME: Placeholder - We have no test file for this value
    assert info.calibration_level == ""  # FIXME: Placeholder - We have no test file for this value
    assert info.istd_amount == 0.0  # FIXME: Placeholder - We have no test file for this value
    assert info.processing_method_file == ""  # FIXME: Placeholder - We have no test file for this value
    assert info.sample_volume == 0.0  # FIXME: Placeholder - We have no test file for this value
    assert info.sample_weight == 0.0  # FIXME: Placeholder - We have no test file for this value
    assert info.user_text == ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    assert info.max_user_text_column_count == 20
