import pytest
import fisher_py
import native_fisher_py as nfp

RAW_FILE = "test_data/MS2_MS1_orbitrap.raw"

def test_mass_analyzer_consistency():
    native_raw = nfp.RawFile(RAW_FILE)
    fisher_raw = fisher_py.RawFile(RAW_FILE)
    
    try:
        # Find the first MS2 scan
        for scan in range(native_raw.first_scan, native_raw.last_scan + 1):
            sf = native_raw.get_filter_for_scan_number(scan)
            if sf.ms_order.name == "Ms2":
                fisher_str = fisher_raw.get_scan_event_str_from_scan_number(scan).lower()
                native_analyzer = sf.mass_analyzer.name
                
                # Map fisher string to expected mass analyzer
                expected_analyzer = None
                if "ftms" in fisher_str:
                    expected_analyzer = "MassAnalyzerFTMS"
                elif "itms" in fisher_str:
                    expected_analyzer = "MassAnalyzerITMS"
                elif "tofms" in fisher_str:
                    expected_analyzer = "MassAnalyzerTOFMS"
                    
                if expected_analyzer:
                    assert native_analyzer == expected_analyzer, f"Mass analyzer mismatch! Expected {expected_analyzer} (from {fisher_str}) but got {native_analyzer}"
                break
    finally:
        pass

def test_activation_type_consistency():
    native_raw = nfp.RawFile(RAW_FILE)
    fisher_raw = fisher_py.RawFile(RAW_FILE)
    
    try:
        # Find the first MS2 scan
        for scan in range(native_raw.first_scan, native_raw.last_scan + 1):
            sf = native_raw.get_filter_for_scan_number(scan)
            if sf.ms_order.name == "Ms2":
                fisher_str = fisher_raw.get_scan_event_str_from_scan_number(scan).lower()
                native_event = native_raw.get_scan_event_for_scan_number(scan)
                
                if native_event.mass_count > 0:
                    native_activation = native_event.get_activation(0).name
                    
                    expected_activation = None
                    if "hcd" in fisher_str:
                        expected_activation = "HigherEnergyCollisionalDissociation"
                    elif "cid" in fisher_str:
                        expected_activation = "CollisionInducedDissociation"
                    elif "etd" in fisher_str:
                        expected_activation = "ElectronTransferDissociation"
                        
                    if expected_activation:
                        assert native_activation == expected_activation, f"Activation mismatch! Expected {expected_activation} (from {fisher_str}) but got {native_activation}"
                break
    finally:
        pass
