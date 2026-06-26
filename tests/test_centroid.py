import numpy as np
import pytest


def test_centroid_stream_retrieval(zoom_raw_file):
    # Scan 1 is usually a good starting point
    scan_number = 1
    cs = zoom_raw_file.get_centroid_stream(scan_number)

    assert cs is not None
    assert cs.scan_number == scan_number
    assert isinstance(cs.masses, np.ndarray)
    assert isinstance(cs.intensities, np.ndarray)
    assert len(cs.masses) == len(cs.intensities)

    if len(cs.masses) > 0:
        assert cs.masses[0] > 0
        assert cs.intensities[0] >= 0
        assert cs.base_peak_intensity == np.max(cs.intensities)
        assert cs.sum_intensities == np.sum(cs.intensities)


def test_centroid_stream_extras(zoom_raw_file):
    scan_number = 1
    cs = zoom_raw_file.get_centroid_stream(scan_number)

    # Extra data might be zeros if not available, but should be returned as arrays
    assert isinstance(cs.baselines, np.ndarray)
    assert isinstance(cs.noises, np.ndarray)
    assert isinstance(cs.charges, np.ndarray)

    assert len(cs.baselines) == len(cs.masses)
    assert len(cs.noises) == len(cs.masses)
    assert len(cs.charges) == len(cs.masses)


def test_is_centroid_scan(zoom_raw_file):
    # Test a few scans to see if they are correctly identified
    # Using small numbers to avoid potential instability in large scan ranges
    for i in range(1, 5):
        is_c = zoom_raw_file.is_centroid_scan_from_scan_number(i)
        assert isinstance(is_c, bool)

def test_centroid_stream_angiotensin(angiotensin_raw_file):
    # Scan 1: 526 peaks
    cs_1 = angiotensin_raw_file.get_centroid_stream(1, False)
    assert cs_1 is not None
    assert cs_1.length == 526
    assert cs_1.base_peak_mass == pytest.approx(432.9000244140625)
    assert cs_1.base_peak_intensity == pytest.approx(447502208.0)
    
    # Scan 2: 39 peaks
    cs_2 = angiotensin_raw_file.get_centroid_stream(2, False)
    assert cs_2 is not None
    assert cs_2.length == 39
    
    # Scan 3: 313 peaks
    cs_3 = angiotensin_raw_file.get_centroid_stream(3, False)
    assert cs_3 is not None
    assert cs_3.length == 313
    assert cs_3.base_peak_mass == pytest.approx(110.07129669189453)
