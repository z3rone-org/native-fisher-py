import pytest
import numpy as np

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
