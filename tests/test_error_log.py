import pytest
from native_fisher_py.raw_file import RawFile

@pytest.fixture
def orbitrap_raw_file():
    raw = RawFile("test_data/MS2_MS1_orbitrap.raw")
    yield raw
    raw.close()

def test_error_log_entry(orbitrap_raw_file):
    count = orbitrap_raw_file.get_error_log_items_count()
    
    # Check if there are any error log items
    assert count > 0, "Expected at least one error log entry in the file"
    
    # Retrieve the first error log entry
    item = orbitrap_raw_file.get_error_log_item(0)
    
    # Verify the properties are parsed correctly and not returning NotImplementedError
    assert isinstance(item.message, str)
    assert len(item.message) > 0
    assert "spray instability" in item.message.lower()
    
    assert isinstance(item.retention_time, float)
    assert item.retention_time > 0.0
