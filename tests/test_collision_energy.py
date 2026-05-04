import pytest
import os
from native_fisher_py.raw_file import RawFile
from native_fisher_py.data.classes import ActivationType

@pytest.fixture(scope="session")
def orbitrap_file():
    path = os.path.join("test_data", "MS2_MS1_orbitrap.raw")
    if not os.path.exists(path):
        pytest.skip(f"Test file {path} not found")
    raw = RawFile(path)
    yield raw
    raw.close()

def test_collision_energy_orbitrap(orbitrap_file):
    energy_expectations = {
        2: 28.0,
        3: 30.0,
        4: 30.0,
        6: 30.0,
        8: 30.0
    }
    for scan_num, expected_energy in energy_expectations.items():
        scan_event = orbitrap_file.get_scan_event_for_scan_number(scan_num)
        actual_energy = scan_event.get_energy(0)
        assert actual_energy == pytest.approx(expected_energy), f"Scan {scan_num} energy mismatch"

def test_collision_energy_zoom(zoom_file):
    # Testing zoom reference (HCD activation confirmed)
    energy_expectations = {
        2: 25.0,
        4: 25.0,
        6: 25.0
    }
    for scan_num, expected in energy_expectations.items():
        scan_event = zoom_file.get_scan_event_for_scan_number(scan_num)
        actual_energy = scan_event.get_energy(0)
        assert actual_energy == pytest.approx(expected), f"Scan {scan_num} energy mismatch"

def test_collision_energy_astral(pxd066718_file):
    # Testing public 549MB Astral reference
    # Scan 100 is MS2 with energy 25.0
    energy_expectations = {
        1: 0.0,
        100: 25.0
    }
    for scan_num, expected in energy_expectations.items():
        scan_event = pxd066718_file.get_scan_event_for_scan_number(scan_num)
        actual_energy = scan_event.get_energy(0)
        assert actual_energy == pytest.approx(expected)

def test_reaction_details_orbitrap(orbitrap_file):
    # Testing precursor, energy, activation, and spectra for Orbitrap scan 2
    scan_number = 2
    scan_event = orbitrap_file.get_scan_event_for_scan_number(scan_number)
    reaction = scan_event.get_reaction(0)
    assert reaction.precursor_mass == pytest.approx(1005.166, abs=0.001)
    assert reaction.collision_energy == pytest.approx(28.0)
    assert reaction.activation_type == ActivationType.HigherEnergyCollisionalDissociation

    # Check spectrum data
    masses, intensities, charges, event_str = orbitrap_file.get_scan_from_scan_number(scan_number)
    assert len(masses) > 0
    assert len(intensities) == len(masses)
    assert masses[0] > 0

def test_reaction_details_zoom(zoom_file):
    # Testing reaction details for zoom reference (HCD)
    scan_number = 2
    scan_event = zoom_file.get_scan_event_for_scan_number(scan_number)
    reaction = scan_event.get_reaction(0)
    assert reaction.precursor_mass == pytest.approx(385.42505, abs=0.001)
    assert reaction.collision_energy == pytest.approx(25.0)
    assert reaction.activation_type == ActivationType.HigherEnergyCollisionalDissociation

    # Check spectrum data
    masses, intensities, charges, event_str = zoom_file.get_scan_from_scan_number(scan_number)
    assert len(masses) > 0
    assert len(intensities) == len(masses)
    assert masses[0] > 0

def test_reaction_details_astral(pxd066718_file):
    # Testing public 549MB Astral reference MS2 metadata
    scan_number = 100
    scan_event = pxd066718_file.get_scan_event_for_scan_number(scan_number)
    reaction = scan_event.get_reaction(0)
    
    assert reaction.precursor_mass == pytest.approx(779.60425, abs=0.001)
    assert reaction.collision_energy == pytest.approx(25.0)
    assert reaction.activation_type == ActivationType.HigherEnergyCollisionalDissociation

    # Check spectrum data
    masses, intensities, charges, event_str = pxd066718_file.get_scan_from_scan_number(scan_number)
    assert len(masses) > 0
    assert len(intensities) == len(masses)
    assert masses[0] > 0

def test_reaction_collision_energy_zoom(zoom_file):
    energy_expectations = {
        2: 25.0,
        4: 25.0,
        6: 25.0
    }
    for scan_num, expected in energy_expectations.items():
        scan_event = zoom_file.get_scan_event_for_scan_number(scan_num)
        reaction = scan_event.get_reaction(0)
        assert reaction.collision_energy == pytest.approx(expected)

def test_reaction_collision_energy_astral(pxd066718_file):
    # Testing public 549MB Astral reference
    energy_expectations = {
        1: 0.0,
        100: 25.0
    }
    for scan_num, expected in energy_expectations.items():
        scan_event = pxd066718_file.get_scan_event_for_scan_number(scan_num)
        reaction = scan_event.get_reaction(0)
        assert reaction.collision_energy == pytest.approx(expected)
