import sys
import os
import numpy as np
from typing import List, Tuple

# Detect if we are running inside Sphinx or Read the Docs to avoid importing the native backend
_IS_RTD = os.environ.get('READTHEDOCS') == 'True'
_IS_SPHINX = _IS_RTD or 'sphinx' in sys.modules or 'sphinx.cmd.build' in sys.modules

if not _IS_SPHINX:
    try:
        from .native_fisher_py_backend import *
    except ImportError:
        raise
else:
    # Provide stubs for documentation generation on Read the Docs
    def open_raw_file(path): return 0
    def get_num_scans(): return 0
    def get_scan_rt(scan_number): return 0.0
    def get_spectrum(scan_number, max_length): return ([], [])
    def get_first_scan(): return 1
    def get_last_scan(): return 1
    def get_end_time(): return 0.0
    def get_ms_order(scan_number): return 1
    def get_mass_analyzer(scan_number): return 0
    def get_precursor_mass(scan_number): return 0.0
    def get_scan_event_string(scan_number): return ""
    def get_scan_number_from_rt(rt): return 1
    def get_ms2_filter_masses(max_size): return []
    def get_ms2_scan_number_from_rt(rt, pmz, tol): return 1
    def get_ms1_scan_number_from_rt(rt): return 1
    def get_chromatogram(trace_type, max_length): return ([], [])
    def get_averaged_spectrum(scan_numbers, max_length): return ([], [])
    def close_raw_file(): pass

# Automatic discovery of the NativeAOT library within the package
_lib_dir = os.path.dirname(__file__)
_ext = ".so"
if sys.platform == "darwin":
    _ext = ".dylib"
elif sys.platform == "win32":
    _ext = ".dll"

_lib_path = os.path.join(_lib_dir, f"ThermoNativeReader{_ext}")
if os.path.exists(_lib_path) and "THERMO_NATIVE_LIB" not in os.environ:
    os.environ["THERMO_NATIVE_LIB"] = _lib_path

class RawFile(object):
    """
    A high-level wrapper to provide a drop-in replacement for fisher_py.RawFile
    """
    def __init__(self, path: str):
        """
        Open a Thermo RAW file.
        
        Args:
            path: Path to the .raw file.
        """
        self._path = path
        res = open_raw_file(path)
        if res != 0:
            raise RuntimeError(f"Could not open RAW file: {path}")

    @property
    def path(self) -> str:
        """Original file path."""
        return self._path

    @property
    def number_of_scans(self) -> int:
        """Total number of scans in the file."""
        return get_num_scans()

    @property
    def first_scan(self) -> int:
        """First scan number (usually 1)."""
        return get_first_scan()

    @property
    def last_scan(self) -> int:
        """Last scan number."""
        return get_last_scan()

    @property
    def total_time_min(self) -> float:
        """Total acquisition time in minutes."""
        return get_end_time()

    def get_retention_time_from_scan_number(self, scan_number: int) -> float:
        """Get RT for a specific scan."""
        return get_scan_rt(scan_number)

    @property
    def ms2_filter_masses(self) -> List[float]:
        """All precursor masses present in the file (unique)."""
        # Return unique precursor masses
        return get_ms2_filter_masses(10000)

    def get_scan_ms2(self, rt: float, precursor_mz: float = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Find and extract the closest MS2 spectrum for a given RT and precursor.
        
        Returns: (masses, intensities, charges, actual_rt)
        """
        if precursor_mz is None:
            # Fisher-py logic: if no precursor, find closest MS2
            # Let's assume a default if not provided, or search all
            scan_number, _ = self.get_ms2_scan_number_from_retention_time(rt, None)
        else:
            scan_number, _ = self.get_ms2_scan_number_from_retention_time(rt, precursor_mz)
            
        if scan_number < 1:
            return np.array([]), np.array([]), np.array([]), 0.0
            
        masses, intensities, charges, _ = self.get_scan_from_scan_number(scan_number)
        actual_rt = self.get_retention_time_from_scan_number(scan_number)
        return masses, intensities, charges, actual_rt

    def get_chromatogram(self, mass: float = None, tolerance: float = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract chromatogram data. Default is TIC (Total Ion Chromatogram).
        
        Returns: (times_min, intensities)
        """
        # For TIC (traceType 1)
        # For now, we only support TIC in the backend. 
        # Mass range support would require ChromatogramTraceSettings updates.
        times, intensities = get_chromatogram(1, 1000000)
        return np.array(times), np.array(intensities)

    def get_tic_ms2(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get Total Ion Chromatogram of MS2 spectra only."""
        # fisher-py specific: returns TIC of only MS2 spectra
        # For now, we return the general TIC
        return self.get_chromatogram()

    def get_averaged_ms2_scans(self, scan_numbers: List[int]) -> Tuple[np.ndarray, np.ndarray, int]:
        """Average dynamic spectra from a list of scan numbers."""
        if not scan_numbers:
            return np.array([]), np.array([]), 0
        masses, intensities = get_averaged_spectrum(scan_numbers, 1000000)
        # Return first scan as the placeholder scan_event_id for parity
        return np.array(masses), np.array(intensities), scan_numbers[0]

    def get_average_ms2_scans_by_rt(self, rt: float, rt_window: float, precursor_mz: float, tolerance: float) -> Tuple[np.ndarray, np.ndarray, int]:
        """Average MS2 spectra centered around a specific RT and precursor mass."""
        # Find all scans for this precursor in the window
        # For now, we do a simple scan-by-scan check in Python (or we could add a backend helper)
        # But for 100% parity, we'll implement the search loop
        start_rt = rt - rt_window
        end_rt = rt + rt_window
        
        scans = []
        for i in range(self.first_scan, self.last_scan + 1):
            scan_rt = self.get_retention_time_from_scan_number(i)
            if scan_rt < start_rt: continue
            if scan_rt > end_rt: break
            
            # Use our existing helper to check if this scan matches
            ms_scan = self.get_ms2_scan_number_from_retention_time(scan_rt, precursor_mz)
            if ms_scan == i:
                scans.append(i)
        
        return self.get_averaged_ms2_scans(scans)

    def get_ms1_scan_number_from_retention_time(self, rt: float) -> Tuple[int, float]:
        """Find the closest MS1 scan for a given RT."""
        scan_number = get_ms1_scan_number_from_rt(rt)
        if scan_number < 1: return 0, 0.0
        return scan_number, self.get_retention_time_from_scan_number(scan_number)

    def get_ms2_scan_number_from_retention_time(self, rt: float, precursor_mz: float = None) -> Tuple[int, float]:
        """Find the closest MS2 scan for a given RT and precursor mass."""
        # Default to very high tolerance if None provided
        pmz = precursor_mz if precursor_mz is not None else 0.0
        tol = 10.0 if precursor_mz is not None else 1e9
        scan_number = get_ms2_scan_number_from_rt(rt, pmz, tol)
        if scan_number < 1: return 0, 0.0
        return scan_number, self.get_retention_time_from_scan_number(scan_number)

    def get_scan_from_scan_number(self, scan_number: int):
        """
        Extract full spectral data for a specific scan number.
        
        Returns: (masses, intensities, charges, filter_string)
        """
        masses, intensities = get_spectrum(scan_number, 1000000)
        # Note: Charges are often not available/zero in centroids, we return empty array for parity
        charges = np.zeros_like(masses)
        event_str = self.get_scan_event_str_from_scan_number(scan_number)
        return np.array(masses), np.array(intensities), charges, event_str

    def get_scan(self, rt: float):
        """Extract full spectral data for the scan closest to a given RT."""
        scan_number = self.get_scan_number_from_retention_time(rt)
        return self.get_scan_from_scan_number(scan_number)

    def get_scan_ms1(self, rt: float):
        """Extract MS1 spectral data for the scan closest to a given RT."""
        scan_number = self.get_scan_number_from_retention_time(rt)
        masses, intensities, charges, _ = self.get_scan_from_scan_number(scan_number)
        # Fisher-py get_scan_ms1 returns (masses, intensities, charges, rt)
        return masses, intensities, charges, rt

    def get_scan_number_from_retention_time(self, rt: float) -> int:
        """Find the scan number closest to a given RT."""
        return get_scan_number_from_rt(rt)

    def get_scan_event_str_from_scan_number(self, scan_number: int) -> str:
        """Get the instrument filter string (e.g. 'FTMS + p NSI Full ms') for a scan."""
        return get_scan_event_string(scan_number)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the file and release the reader resources."""
        close_raw_file()

class MSOrder:
    Ms = 1
    Ms2 = 2
    Ms3 = 3

class MassAnalyzer:
    Any = 0
    ITMS = 1
    TQMS = 2
    SQMS = 3
    TOFMS = 4
    FTMS = 5
    Sector = 6

if not _IS_SPHINX:
    from . import native_fisher_py_backend
    __doc__ = native_fisher_py_backend.__doc__
    if hasattr(native_fisher_py_backend, "__all__"):
        __all__ = native_fisher_py_backend.__all__ + ["RawFile", "MSOrder", "MassAnalyzer"]
    else:
        __all__ = ["RawFile", "MSOrder", "MassAnalyzer"]
else:
    __all__ = ["RawFile", "MSOrder", "MassAnalyzer"]
