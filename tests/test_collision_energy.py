import pytest
import os
from native_fisher_py.raw_file import RawFile

@pytest.fixture(scope="session")
def raw_path():
    return os.path.join("test_data", "MS2_MS1_orbitrap.raw")

@pytest.fixture(scope="session")
def raw_file(raw_path):
    if not os.path.exists(raw_path):
        pytest.skip(f"Test file {raw_path} not found")
    
    raw = RawFile(raw_path)
    yield raw
    raw.close()

def test_collision_energy(raw_file):
    # Test values obtained from a reference run
    energy_expectations = {
        2: 28.0,
        3: 30.0,
        4: 30.0,
        6: 30.0,
        8: 30.0
    }
    
    for scan_num, expected_energy in energy_expectations.items():
        scan_event = raw_file.get_scan_event_for_scan_number(scan_num)
        actual_energy = scan_event.get_energy(0)
        assert actual_energy == pytest.approx(expected_energy), f"Scan {scan_num} energy mismatch"

def test_reaction_collision_energy(raw_file):
    # Check first reaction specifically
    scan_num = 2
    scan_event = raw_file.get_scan_event_for_scan_number(scan_num)
    reaction = scan_event.get_reaction(0)
    assert reaction.collision_energy == pytest.approx(28.0)
