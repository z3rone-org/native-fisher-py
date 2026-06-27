import pytest
from native_fisher_py.raw_file import RawFile
import os

@pytest.fixture
def raw_file():
    path = os.path.join(os.path.dirname(__file__), "..", "potential_test_files", "MTBLS773_UV.raw")
    # if not present, fail
    if not os.path.exists(path):
        pytest.fail(f"Test file not found: {path}")
    raw = RawFile(path)
    yield raw
    raw.close()

def test_file_header_properties(raw_file):
    header = raw_file.file_header
    
    assert header.number_of_times_calibrated == 0
    assert header.number_of_times_modified == 1
    assert header.revision == 63
    
    # string properties
    assert header.creation_date == "2016-08-11T17:51:33.4060000Z"
    assert header.who_created_id == "QUANTUM"
    assert header.file_description == ""
    assert header.modified_date == "11/08/2016 18:27:11"
    assert header.who_created_logon == "QUANTUM"
    assert header.who_modified_id == "QUANTUM"
    assert header.who_modified_logon == "QUANTUM"
