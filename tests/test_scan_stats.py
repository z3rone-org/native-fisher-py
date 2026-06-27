import pytest

def test_scan_stats_new_properties(angiotensin_raw_file):
    # Retrieve the stats for the first scan
    stats = angiotensin_raw_file.get_scan_stats_for_scan_number(1)
    
    # Assert standard properties are still valid
    assert stats.start_time > 0
    assert stats.packet_count > 0

    # Assert new properties are accessible and contain expected values
    assert stats.absorbance_unit_scale == 0.0
    assert stats.cycle_number == 0
    assert stats.frequency == 0.0
    assert stats.is_uniform_time is False
    assert stats.long_wavelength == 0.0
    assert stats.number_of_channels == 0
    assert stats.packet_type == 21
    assert stats.scan_event_number == -1
    assert stats.segment_number == 0
    assert stats.short_wavelength == 0.0
    assert stats.spectrum_packet_type == 21
    assert stats.wavelength_step == 0.0
    assert stats.scan_type is None or isinstance(stats.scan_type, str)

def test_scan_stats_angiotensin(angiotensin_raw_file):
    stats = angiotensin_raw_file.get_scan_stats_for_scan_number(2)
    
    # Check exact values for the second scan
    assert stats.absorbance_unit_scale == 0.0
    assert stats.cycle_number == 0
    assert stats.frequency == 0.0
    assert stats.is_uniform_time is False
    assert stats.long_wavelength == 0.0
    assert stats.number_of_channels == 0
    assert stats.packet_type == 21
    assert stats.scan_event_number == -1
    assert stats.segment_number == 0
    assert stats.short_wavelength == 0.0
    assert stats.spectrum_packet_type == 21
    assert stats.wavelength_step == 0.0
    assert stats.scan_type is None or isinstance(stats.scan_type, str)
