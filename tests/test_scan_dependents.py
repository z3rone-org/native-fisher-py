import pytest


def test_scan_dependents_orbitrap_file(orbitrap_raw_file):
    # MS2_MS1_orbitrap.raw has dependents for Scan 1
    deps = orbitrap_raw_file.get_scan_dependents(1, 2)
    assert deps.raw_file_instrument_type != -1

    details = deps.scan_dependent_detail_array
    assert isinstance(details, list)
    assert len(details) > 0

    det = details[0]
    assert det.filter_string is None
    assert det.scan_index == 6
    assert det.precursor_mass_array == [954.4949340820312]
    assert det.isolation_width_array == [1.600000023841858]
