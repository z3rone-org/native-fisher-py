import pytest
import numpy as np

def run_centroid_test(raw_file, scan_number):
    if not raw_file.is_centroid_scan_from_scan_number(scan_number):
         pytest.skip(f"Scan {scan_number} is not a centroid scan")

    cs = raw_file.get_centroid_stream(scan_number)
    assert cs is not None
    assert cs.scan_number == scan_number
    assert isinstance(cs.masses, np.ndarray)
    assert isinstance(cs.intensities, np.ndarray)
    assert len(cs.masses) == len(cs.intensities)
    
    if len(cs.masses) > 0:
        assert cs.masses[0] > 0
        assert cs.intensities[0] >= 0
        assert cs.base_peak_intensity == np.max(cs.intensities)
        
    assert isinstance(cs.baselines, np.ndarray)
    assert isinstance(cs.noises, np.ndarray)
    assert isinstance(cs.charges, np.ndarray)
    assert len(cs.baselines) == len(cs.masses)

def test_centroid_zoom(zoom_file):
    run_centroid_test(zoom_file, 2)

def test_centroid_astral(pxd066718_file):
    run_centroid_test(pxd066718_file, 2)

def test_centroid_astral_zoom(pxd066944_file):
    run_centroid_test(pxd066944_file, 5)

def test_is_centroid_scan(zoom_file):
    # Test a few scans to see if they are correctly identified
    # MS1 scans are usually profile, MS2 are centroid
    if zoom_file.number_of_scans >= 2:
        assert not zoom_file.is_centroid_scan_from_scan_number(1)
        assert zoom_file.is_centroid_scan_from_scan_number(2)
