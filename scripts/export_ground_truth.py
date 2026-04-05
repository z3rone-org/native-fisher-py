import os
import sys
import json
import numpy as np

# This script must be run where fisher-py is working correctly.
# It exports ground truth data for parity testing.

def export_raw_file(raw_path, output_path):
    import os
    import sys
    import fisher_py
    from fisher_py.data.business import TraceType
    
    print(f"Exporting ground truth from: {raw_path}")
    raw = fisher_py.RawFile(raw_path)
    
    # 1. Basic Metadata
    data = {
        "metadata": {
            "first_scan": raw.first_scan,
            "last_scan": raw.last_scan,
            "number_of_scans": raw.number_of_scans,
            "total_time_min": raw.total_time_min,
        },
        "scans": {},
        "ms2_filter_masses": raw.ms2_filter_masses.tolist() if hasattr(raw.ms2_filter_masses, 'tolist') else raw.ms2_filter_masses,
        "chromatogram": {}
    }
    
    # 2. Sample Scans (MS1)
    # Total scans might be huge, just sample some
    sample_scans = [raw.first_scan, raw.last_scan, (raw.first_scan + raw.last_scan) // 2]
    for scan in sample_scans:
        m, i, c, meta = raw.get_scan_from_scan_number(scan)
        rt = raw.get_retention_time_from_scan_number(scan)
        data["scans"][str(scan)] = {
            "rt": rt,
            "masses": m.tolist(),
            "intensities": i.tolist()
        }
        
    # 3. MS2 samples
    if len(raw.ms2_filter_masses) > 0:
        rt_mid = raw.total_time_min / 2
        pmz = raw.ms2_filter_masses[len(raw.ms2_filter_masses)//2]
        
        scan_ms2, rt_ms2 = raw.get_ms2_scan_number_from_retention_time(rt_mid, pmz)
        m2, i2, c2, meta2 = raw.get_scan_ms2(rt_mid, pmz)
        
        data["ms2_sample"] = {
            "request_rt": rt_mid,
            "request_mz": pmz,
            "found_scan": scan_ms2,
            "found_rt": rt_ms2,
            "masses": m2.tolist(),
            "intensities": i2.tolist()
        }
        
    # 4. Chromatogram
    ct, ci = raw.get_chromatogram(0.0, 0.0, trace_type=TraceType.TIC, ms_filter='')
    data["chromatogram"] = {
        "times": ct.tolist(),
        "intensities": ci.tolist()
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f)
    
    print(f"Ground truth exported to: {output_path}")

if __name__ == "__main__":
    raw_file = "test_data/MS2_MS1_orbitrap.raw"
    output = "tests/ground_truth.json"
    
    # We need to make sure fisher-py is available
    sys.path.append(os.path.join(os.getcwd(), "native_fisher_py", "python"))
    
    export_raw_file(raw_file, output)
