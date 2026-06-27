import pytest
import os
from native_fisher_py.raw_file import RawFile


@pytest.fixture(scope="session")
def raw_path():
    return os.path.join("test_data", "MS2_MS1_orbitrap.raw")


@pytest.fixture(scope="session")
def raw_file(raw_path):
    if not os.path.exists(raw_path):
        pytest.fail(f"Test file {raw_path} not found")

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


def test_isolation_width_angiotensin(angiotensin_raw_file):
    # Check values on scan 3 (IW 2.0, CE 30.0)
    scan_event_3 = angiotensin_raw_file.get_scan_event_for_scan_number(3)
    assert scan_event_3.get_isolation_width(0) == pytest.approx(2.0), "Scan 3 ScanEvent isolation width mismatch"
    reaction_3 = scan_event_3.get_reaction(0)
    assert reaction_3.isolation_width == pytest.approx(2.0), "Scan 3 Reaction isolation width mismatch"
    assert reaction_3.isolation_width_offset == pytest.approx(0.0), "Scan 3 Reaction isolation width offset mismatch"
    assert reaction_3.collision_energy == pytest.approx(30.0), "Scan 3 CE mismatch"
    assert reaction_3.precursor_mass == pytest.approx(432.9000244140625)
    
    # Test auxiliary Reaction properties on a standard non-range scan to ensure they fallback safely to 0.0
    # instead of raising NotImplementedError
    assert reaction_3.collision_energy_valid is True
    assert reaction_3.first_precursor_mass == 0.0
    assert reaction_3.last_precursor_mass == 0.0
    assert reaction_3.multiple_activation is False
    assert reaction_3.precursor_range_is_valid is False

    # Check values on scan 10 (Different CE)
    scan_event_10 = angiotensin_raw_file.get_scan_event_for_scan_number(10)
    reaction_10 = scan_event_10.get_reaction(0)
    assert reaction_10.isolation_width == pytest.approx(2.0)
    assert reaction_10.collision_energy == pytest.approx(53.98562240600586)
    assert reaction_10.precursor_mass == pytest.approx(433.90216064453125)
    assert reaction_10.collision_energy_valid is True
    assert reaction_10.first_precursor_mass == 0.0
    assert reaction_10.last_precursor_mass == 0.0
    assert reaction_10.multiple_activation is False
    assert reaction_10.precursor_range_is_valid is False

    # Check values on scan 1000 (IW 1.6, Different CE)
    scan_event_1000 = angiotensin_raw_file.get_scan_event_for_scan_number(1000)
    reaction_1000 = scan_event_1000.get_reaction(0)
    assert reaction_1000.isolation_width == pytest.approx(1.600000023841858)
    assert reaction_1000.collision_energy == pytest.approx(121.46764373779297)
    assert reaction_1000.precursor_mass == pytest.approx(649.8494262695312)
    assert reaction_1000.collision_energy_valid is True
    assert reaction_1000.first_precursor_mass == 0.0
    assert reaction_1000.last_precursor_mass == 0.0
    assert reaction_1000.multiple_activation is False
    assert reaction_1000.precursor_range_is_valid is False


def test_precursor_range_valid(prec_range_raw_file):
    # This AIF (All Ion Fragmentation) calibration file has a broadband scan filter string on MS2:
    # e.g., "ITMS + c NSI r d Full ms2 1500.00-3000.00"
    # Therefore, the reaction implicitly has a valid mass range instead of a center mass + isolation width.
    
    scan_event = prec_range_raw_file.get_scan_event_for_scan_number(1)
    reaction = scan_event.get_reaction(0)
    
    assert reaction.precursor_range_is_valid is True
    assert reaction.first_precursor_mass == pytest.approx(1500.0)
    assert reaction.last_precursor_mass == pytest.approx(3000.0)
    
    # Precursor mass is usually reported as the center or fallback when a range is used
    # We mainly care that it doesn't crash and returns the range bounds correctly.
    assert reaction.collision_energy_valid is True
