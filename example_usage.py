import native_fisher_py as nfp
import os

def main():
    # Choose one of the linked files from test_data
    raw_file = os.path.abspath(os.path.realpath("test_data/MS2_MS1_orbitrap.raw"))
    
    if not os.path.exists(raw_file):
        print(f"Error: Could not find {raw_file}")
        return

    print(f"Opening {raw_file}...")
    # open_raw_file returns 0 on success, -1 on failure
    res = nfp.open_raw_file(raw_file)
    if res != 0:
        print("Failed to open RAW file.")
        return

    try:
        num_scans = nfp.get_num_scans()
        print(f"Total scans: {num_scans}")

        if num_scans > 0:
            # Let's extract scan number 1
            scan_number = 1
            rt = nfp.get_scan_rt(scan_number)
            print(f"Scan {scan_number}: Retention Time = {rt:.3f} min")

            # Extract spectrum centroids
            # max_length of 10000 peaks to ensure we capture most data
            masses, intensities = nfp.get_spectrum(scan_number, 10000)
            print(f"Scan {scan_number}: Extracted {len(masses)} centroids")
            
            if len(masses) > 0:
                print("First 5 peak intensities and their m/z values:")
                for i in range(min(5, len(masses))):
                    print(f"  m/z {masses[i]:10.4f} | Intensity: {intensities[i]:12.1f}")
        
    finally:
        print("Closing RAW file...")
        nfp.close_raw_file()

if __name__ == "__main__":
    main()
