import pytest
from native_fisher_py.raw_file import RawFile
import os


@pytest.fixture
def raw_file_mtbls773():
    path = os.path.join(os.path.dirname(__file__), "..", "test_data", "MTBLS773_UV.raw")
    if not os.path.exists(path):
        pytest.fail(f"Test file not found: {path}")
    raw = RawFile(path)
    yield raw
    raw.close()


@pytest.fixture
def raw_file_angiotensin():
    path = os.path.join(os.path.dirname(__file__), "..", "test_data", "Angiotensin_AllScans.raw")
    if not os.path.exists(path):
        pytest.fail(f"Test file not found: {path}")
    raw = RawFile(path)
    yield raw
    raw.close()


@pytest.fixture
def raw_file_small():
    path = os.path.join(os.path.dirname(__file__), "..", "test_data", "small.RAW")
    if not os.path.exists(path):
        pytest.fail(f"Test file not found: {path}")
    raw = RawFile(path)
    yield raw
    raw.close()


def test_file_header_mtbls773(raw_file_mtbls773):
    header = raw_file_mtbls773.file_header
    assert header.number_of_times_calibrated == 0
    assert header.number_of_times_modified == 1
    assert header.revision == 63
    assert header.creation_date == "2016-08-11T17:51:33.4060000Z"

    assert header.who_created_id == "QUANTUM"
    assert header.file_description == ""
    assert '27:11' in header.modified_date
    assert header.who_created_logon == "QUANTUM"
    assert header.who_modified_id == "QUANTUM"
    assert header.who_modified_logon == "QUANTUM"


def test_file_header_angiotensin(raw_file_angiotensin):
    header = raw_file_angiotensin.file_header
    assert header.number_of_times_calibrated == 0
    assert header.number_of_times_modified == 2
    assert header.revision == 66
    assert header.creation_date == "2018-09-26T09:06:07.5635131Z"

    assert header.who_created_id == "SYSTEM"
    assert header.file_description == ""
    assert '06:07' in header.modified_date
    assert header.who_created_logon == "SYSTEM"
    assert header.who_modified_id == "SYSTEM"
    assert header.who_modified_logon == "SYSTEM"


def test_file_header_small(raw_file_small):
    header = raw_file_small.file_header
    assert header.number_of_times_calibrated == 0
    assert header.number_of_times_modified == 4
    assert header.revision == 57
    assert header.creation_date == "2005-07-20T14:44:22.3770000Z"

    assert header.who_created_id == "LTQ"
    assert header.file_description == ""
    assert '45:05' in header.modified_date
    assert header.who_created_logon == "LTQ"
    assert header.who_modified_id == "LTQ"
    assert header.who_modified_logon == "LTQ"
