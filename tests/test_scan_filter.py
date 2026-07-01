import pytest


def test_scan_filter_properties(orbitrap_raw_file):
    # Retrieve scan event 6 which is an MS2 scan in the orbitrap data
    e = orbitrap_raw_file.get_scan_event_for_scan_number(6)

    assert e.mass_range_count == 1
    assert e.source_fragmentation_info_count == 0  # FIXME: Placeholder - we don't have a test file with non-zero source_fragmentation_info_count
    assert e.scan_type_index == -1  # FIXME: Placeholder - we don't have a test file with a valid scan_type_index

    # 2 is TriState.Off (or unassigned/off based on the raw file)
    assert e.multi_state_activation.value == 2  # FIXME: Placeholder - we don't have a test file where this is On
    assert e.photo_ionization.value == 2  # FIXME: Placeholder - we don't have a test file where this is On
    assert e.sector_scan.value == 2  # FIXME: Placeholder - we don't have a test file where this is On

    # Mass ranges for MS2 scan 6
    assert e.get_first_precursor_mass(0) == 0.0
    assert e.get_last_precursor_mass(0) == 0.0
    assert e.get_mass_range(0) == (120.0, 2000.0)

    assert e.get_energy_valid(0).value == 0  # FIXME: Placeholder - we don't have a test file where energy is valid (value=1)
    assert e.get_mass_calibrator(0) == 0.0  # FIXME: Placeholder - we don't have a test file with a non-zero mass calibrator
    assert e.get_is_multiple_activation(0) is False  # FIXME: Placeholder - we don't have a test file where this is True
    assert e.get_precursor_range_validity(0) is False

    # Verify that source fragmentation info throws or returns fallback because count is 0
    #assert e.get_source_fragmentation_info(0) == -1.0  # FIXME: Placeholder - we don't have a test file with actual source fragmentation info


def test_scan_filter_properties_pxd006873():
    from native_fisher_py.raw_file import RawFile
    r = RawFile("test_data/PXD006873_prec_range.raw")

    e = r.get_scan_event_for_scan_number(1)
    assert e.mass_range_count == 1
    assert e.mass_count == 1

    assert e.get_first_precursor_mass(0) == 1500.0
    assert e.get_last_precursor_mass(0) == 3000.0
    assert e.get_mass_range(0) == (1500.0, 3000.0)
    assert e.get_precursor_range_validity(0) is True
    assert e.get_is_multiple_activation(0) is False

    r.close()
