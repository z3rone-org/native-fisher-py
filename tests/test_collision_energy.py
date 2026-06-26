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


def test_isolation_width(raw_file):
    # Test values obtained from a reference run
    width_expectations = {
        2: 1.6,
        3: 1.6,
        4: 1.6,
        6: 1.6,
        8: 1.6
    }

    for scan_num, expected_width in width_expectations.items():
        scan_event = raw_file.get_scan_event_for_scan_number(scan_num)
        
        # Test ScanEvent.get_isolation_width
        actual_width = scan_event.get_isolation_width(0)
        assert actual_width == pytest.approx(expected_width), f"Scan {scan_num} ScanEvent isolation width mismatch"
        
        # Test Reaction.isolation_width
        reaction = scan_event.get_reaction(0)
        assert reaction.isolation_width == pytest.approx(expected_width), f"Scan {scan_num} Reaction isolation width mismatch"
        assert reaction.isolation_width_offset == pytest.approx(0.0), f"Scan {scan_num} Reaction isolation width offset mismatch"


@pytest.fixture(scope="session")
def angiotensin_raw_file():
    path = os.path.join("test_data", "Angiotensin_AllScans.raw")
    if not os.path.exists(path):
        pytest.skip(f"Test file {path} not found")
    raw = RawFile(path)
    yield raw
    raw.close()

def test_isolation_width_angiotensin(angiotensin_raw_file):
    scan_event = angiotensin_raw_file.get_scan_event_for_scan_number(3)
    actual_width = scan_event.get_isolation_width(0)
    assert actual_width == pytest.approx(2.0), "Scan 3 ScanEvent isolation width mismatch"
    
    reaction = scan_event.get_reaction(0)
    assert reaction.isolation_width == pytest.approx(2.0), "Scan 3 Reaction isolation width mismatch"
    assert reaction.isolation_width_offset == pytest.approx(0.0), "Scan 3 Reaction isolation width offset mismatch"
