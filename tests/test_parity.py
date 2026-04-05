import numpy as np
import pytest
import os
import sys
import json

class FisherPyMock:
    def __init__(self, ground_truth_path):
        with open(ground_truth_path, 'r') as f:
            self.data = json.load(f)
        self.first_scan = self.data["metadata"]["first_scan"]
        self.last_scan = self.data["metadata"]["last_scan"]
        self.number_of_scans = self.data["metadata"]["number_of_scans"]
        self.total_time_min = self.data["metadata"]["total_time_min"]
        self.ms2_filter_masses = np.array(self.data["ms2_filter_masses"])

    def get_retention_time_from_scan_number(self, scan):
        return self.data["scans"].get(str(scan), {}).get("rt", 0.0)

    def get_scan_number_from_retention_time(self, rt):
        for scan, info in self.data["scans"].items():
            if abs(info["rt"] - rt) < 1e-4: return int(scan)
        return int(next(iter(self.data["scans"].keys())))

    def get_ms1_scan_number_from_retention_time(self, rt):
        return self.get_scan_number_from_retention_time(rt)

    def get_scan_from_scan_number(self, scan):
        info = self.data["scans"].get(str(scan), {"masses": [], "intensities": []})
        return np.array(info["masses"]), np.array(info["intensities"]), None, None

    def get_ms2_scan_number_from_retention_time(self, rt, pmz):
        if "ms2_sample" in self.data:
            return self.data["ms2_sample"]["found_scan"], self.data["ms2_sample"]["found_rt"]
        return 0, 0.0

    def get_scan_ms2(self, rt, pmz):
        if "ms2_sample" in self.data:
            info = self.data["ms2_sample"]
            return np.array(info["masses"]), np.array(info["intensities"]), None, None
        return np.array([]), np.array([]), None, None

    def get_chromatogram(self, *args, **kwargs):
        return np.array(self.data["chromatogram"]["times"]), np.array(self.data["chromatogram"]["intensities"])

    def close(self):
        pass

def setup_fisher_dlls():
    # Only try to setup DLLs if we are NOT using ground truth fallback
    try:
        import clr
        # (This part is mostly redundant in CI if we have the JSON)
    except:
        pass

def test_api_parity():
    import native_fisher_py as nfp
    orig_api = set([m for m in dir(nfp.RawFile) if not m.startswith("_")])
    assert "first_scan" in orig_api
    assert "last_scan" in orig_api
    assert "number_of_scans" in orig_api
    assert "get_scan_from_scan_number" in orig_api

@pytest.fixture
def raw_file_path():
    return "test_data/MS2_MS1_orbitrap.raw"

def test_behavior_parity(raw_file_path):
    import native_fisher_py
    
    orig = None
    try:
        # Try actual fisher-py first
        setup_fisher_dlls()
        import fisher_py
        orig = fisher_py.RawFile(raw_file_path)
    except Exception as e:
        print(f"DEBUG: fisher-py load failed: {e}. Falling back to ground_truth.json")
        gt_path = os.path.join(os.path.dirname(__file__), "ground_truth.json")
        if os.path.exists(gt_path):
            orig = FisherPyMock(gt_path)
        else:
            pytest.skip("Neither fisher-py nor ground_truth.json available.")
            
    native = native_fisher_py.RawFile(raw_file_path)
    
    try:
        # 1. Properties
        assert native.first_scan == orig.first_scan
        assert native.last_scan == orig.last_scan
        assert native.number_of_scans == orig.number_of_scans
        assert native.total_time_min == pytest.approx(orig.total_time_min)
        
        # 2. Navigation
        scan = native.first_scan
        rt = native.get_retention_time_from_scan_number(scan)
        assert rt == pytest.approx(orig.get_retention_time_from_scan_number(scan))
        
        # 3. Spectral Data (Sampled Scans)
        scans_to_check = [orig.first_scan, orig.last_scan, (orig.first_scan + orig.last_scan) // 2]
        for s in scans_to_check:
            n_m, n_i, _, _ = native.get_scan_from_scan_number(s)
            o_m, o_i, _, _ = orig.get_scan_from_scan_number(s)
            np.testing.assert_allclose(n_m, o_m, rtol=1e-5)
            np.testing.assert_allclose(n_i, o_i, rtol=1e-5)
        
        # 4. MS2 filter masses
        n_filter = native.ms2_filter_masses
        o_filter = orig.ms2_filter_masses
        assert len(n_filter) == len(o_filter)
        if len(n_filter) > 0:
             np.testing.assert_allclose(n_filter[:10], o_filter[:10], rtol=1e-5)
             
        # 5. MS2 Retrieval
        if len(n_filter) > 0:
            rt_mid = native.total_time_min / 2
            pmz = n_filter[len(n_filter)//2]
            
            n_scan_2, n_rt2 = native.get_ms2_scan_number_from_retention_time(rt_mid, pmz)
            o_scan_2, o_rt2 = orig.get_ms2_scan_number_from_retention_time(rt_mid, pmz)
            
            n_m2, n_i2, _, _ = native.get_scan_ms2(rt_mid, pmz)
            o_m2, o_i2, _, _ = orig.get_scan_ms2(rt_mid, pmz)
            
            assert n_scan_2 == o_scan_2
            np.testing.assert_allclose(n_m2, o_m2, rtol=1e-5)
            np.testing.assert_allclose(n_i2, o_i2, rtol=1e-5)
    
        # 6. Chromatogram
        import native_fisher_py
        n_ct, n_ci = native.get_chromatogram(0.0, 0.0, trace_type=native_fisher_py.TraceType.TIC, ms_filter='')

        if isinstance(orig, FisherPyMock):
            o_trace_type = native_fisher_py.TraceType.TIC
        else:
            from fisher_py.data.business import TraceType as OrigTraceType
            o_trace_type = OrigTraceType.TIC

        o_ct, o_ci = orig.get_chromatogram(0.0, 0.0, trace_type=o_trace_type, ms_filter='')
        
        np.testing.assert_allclose(n_ct, o_ct, rtol=1e-5)
        np.testing.assert_allclose(n_ci, o_ci, rtol=1e-5)

    finally:
        native.close()
        if hasattr(orig, 'close'): orig.close()
