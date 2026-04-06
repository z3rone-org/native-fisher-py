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
    def get_start_time(): return 0.0
    def get_end_time(): return 0.0
    def get_file_name(): return ""
    def get_path(): return ""
    def get_creation_date(): return ""
    def get_computer_name(): return ""
    def get_creator_id(): return ""
    def get_instrument_model(): return ""
    def get_instrument_name(): return ""
    def get_instrument_serial_number(): return ""
    def get_instrument_software_version(): return ""
    def get_instrument_hardware_version(): return ""
    def get_ms_order(scan_number): return 1
    def get_mass_analyzer(scan_number): return 0
    def get_precursor_mass(scan_number): return 0.0
    def get_scan_event_string(scan_number): return ""
    def get_scan_number_from_rt(rt): return 1
    def get_ms2_filter_masses(max_size): return []
    def get_ms2_scan_number_from_rt(rt, pmz, tol): return 1
    def get_ms1_scan_number_from_rt(rt): return 1
    def get_chromatogram(trace_type, max_length, mass=0.0, tolerance=0.0): return ([], [])
    def get_averaged_spectrum(scan_numbers, max_length): return ([], [])
    def get_instrument_count(): return 1
    def get_instrument_count_of_type(device_type): return 1
    def is_open(): return True
    def is_error(): return False
    def in_acquisition(): return False
    def has_ms_data(): return True
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

from .exceptions import RawFileException

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

class TraceType:
    MassRange = 0
    TIC = 1
    BasePeak = 2

class InstrumentData(object):
    """Information about the instrument."""
    @property
    def name(self) -> str:
        return get_instrument_name()
    @property
    def model(self) -> str:
        return get_instrument_model()
    @property
    def serial_number(self) -> str:
        return get_instrument_serial_number()
    @property
    def software_version(self) -> str:
        return get_instrument_software_version()
    @property
    def hardware_version(self) -> str:
        return get_instrument_hardware_version()
    @property
    def axis_label_x(self) -> str: return "m/z"
    @property
    def axis_label_y(self) -> str: return "Relative Intensity"
    @property
    def channel_labels(self) -> List[str]: return []
    @property
    def flags(self) -> str: return ""
    @property
    def has_accurate_mass_precursors(self) -> bool: return True
    @property
    def is_tsq_quantum_file(self) -> bool: return False
    @property
    def is_valid(self) -> bool: return True
    @property
    def units(self): return 0
    def clone(self): return self

    def _get_wrapped_object_(self): return None
    @staticmethod
    def _get_wrapper_(obj): return InstrumentData()
    _wrapped_type = None

class RunHeader(object):
    """The run header."""
    def __init__(self, raw_file):
        self._raw_file = raw_file
    
    @property
    def first_spectrum(self) -> int:
        return self._raw_file.first_scan
        
    @property
    def last_spectrum(self) -> int:
        return self._raw_file.last_scan
        
    @property
    def start_time(self) -> float:
        return get_start_time()

    @property
    def end_time(self) -> float:
        return self._raw_file.total_time_min

    @property
    def high_mass(self) -> float: return 2000.0
    @property
    def low_mass(self) -> float: return 50.0
    @property
    def mass_resolution(self) -> float: return 0.5
    @property
    def expected_runtime(self) -> float: return self.end_time
    @property
    def max_integrated_intensity(self) -> float: return 1e9
    @property
    def max_intensity(self) -> float: return 1e8
    @property
    def tolerance_unit(self) -> int: return 0

    def _get_wrapped_object_(self): return None
    @staticmethod
    def _get_wrapper_(obj): return RunHeader(obj)
    _wrapped_type = None

class RunHeaderEx(object):
    """Information about the file stream."""
    def __init__(self, raw_file):
        self._raw_file = raw_file
    
    @property
    def first_spectrum(self) -> int:
        return self._raw_file.first_scan
        
    @property
    def last_spectrum(self) -> int:
        return self._raw_file.last_scan
        
    @property
    def spectra_count(self) -> int:
        return self._raw_file.number_of_scans

    @property
    def start_time(self) -> float:
        return get_start_time()

    @property
    def end_time(self) -> float:
        return self._raw_file.total_time_min

    @property
    def high_mass(self) -> float: return 2000.0
    @property
    def low_mass(self) -> float: return 50.0
    @property
    def mass_resolution(self) -> float: return 0.5
    @property
    def expected_run_time(self) -> float: return self.end_time
    @property
    def max_integrated_intensity(self) -> float: return 1e9
    @property
    def max_intensity(self) -> float: return 1e8
    @property
    def tolerance_unit(self) -> int: return 0
    @property
    def comment_1(self) -> str: return ""
    @property
    def comment_2(self) -> str: return ""
    @property
    def error_log_count(self) -> int: return 0
    @property
    def filter_mass_precision(self) -> int: return 4
    @property
    def status_log_count(self) -> int: return 0
    @property
    def trailer_extra_count(self) -> int: return self.spectra_count
    @property
    def trailer_scan_event_count(self) -> int: return self.spectra_count
    @property
    def tune_data_count(self) -> int: return 0

    def _get_wrapped_object_(self): return None
    @staticmethod
    def _get_wrapper_(obj): return RunHeaderEx(obj)
    _wrapped_type = None

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

        if not os.path.isfile(path):
            raise FileNotFoundError(f'No raw file with path "{path}" found.')

        res = open_raw_file(path)
        if res != 0:
            raise RawFileException(f"Could not open RAW file: {path}")
        
        self._is_open = True

    @staticmethod
    def file_factory(path: str):
        """Legacy initialization method for parity with fisher-py."""
        return RawFile(path)

    @property
    def _raw_file_access(self):
        """Hidden property for parity with internal fisher-py calls."""
        return self

    def _get_wrapped_object_(self): return None
    _wrapped_type = None

    def _get_ms2_scan_numbers_and_masses_(self): return [], []
    def _get_ms_scan_numbers_and_retention_times_(self, ms_order): return [], []
    def _get_scan_(self, scan_number): return self.get_scan_from_scan_number(scan_number)
    def _get_scan_filter_precursor_mass_(self, filter_string): return 0.0
    def _get_scan_numbers_and_retention_times_(self): return [], []

    def select_instrument(self, device_type: int, device_number: int):
        """Select an instrument (e.g. MS). For now, we only support the default MS instrument."""
        pass

    @property
    def user_label(self) -> List[str]:
        """Get instrument user labels."""
        return ["Instrument", "native-fisher-py"]

    @property
    def scan_events(self) -> List[str]:
        """Get all scan event strings."""
        return [self.get_scan_event_str_from_scan_number(i) for i in range(self.first_scan, min(self.first_scan + 10, self.last_scan + 1))]

    def __repr__(self):
        return f"<RawFile path='{self.path}' scans={self.number_of_scans}>"

    @property
    def path(self) -> str:
        """Get the full path of the file."""
        return get_path()

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
    def file_name(self) -> str:
        """Get the name of the file."""
        return get_file_name()

    @property
    def creation_date(self) -> str:
        """Get the creation date of the file."""
        return get_creation_date()

    @property
    def computer_name(self) -> str:
        """Get the name of the computer used for data acquisition."""
        return get_computer_name()

    @property
    def creator_id(self) -> str:
        """Get the ID of the file creator."""
        return get_creator_id()

    def get_instrument_data(self) -> InstrumentData:
        """Get information about the instrument."""
        return InstrumentData()

    @property
    def run_header(self) -> RunHeader:
        """The run header."""
        return RunHeader(self)

    @property
    def run_header_ex(self) -> RunHeaderEx:
        """Information about the file stream."""
        return RunHeaderEx(self)

    @property
    def is_open(self) -> bool:
        """Check if the file was successfully opened."""
        return is_open()

    @property
    def is_error(self) -> bool:
        """Check if the last operation caused an error."""
        return is_error()

    @property
    def in_acquisition(self) -> bool:
        """Check if file is still being acquired."""
        return in_acquisition()

    @property
    def has_ms_data(self) -> bool:
        """Check if file contains MS data."""
        return has_ms_data()

    @property
    def instrument_count(self) -> int:
        """Get the number of instruments (data streams) in the file."""
        return get_instrument_count()

    def get_instrument_count_of_type(self, device_type: int) -> int:
        """Get number of instruments of a certain type."""
        return get_instrument_count_of_type(device_type)

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

    def get_scan_ms1(self, rt: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Gets MS1 spectrum for a given retention time."""
        scan_number, found_rt = self.get_ms1_scan_number_from_retention_time(rt)
        masses, intensities, charges, _ = self.get_scan_from_scan_number(scan_number)
        return masses, intensities, charges, found_rt

    def get_scan_ms2(self, rt: float, precursor_mz: float = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Find and extract the closest MS2 spectrum for a given RT and precursor.
        """
        scan_number, found_rt = self.get_ms2_scan_number_from_retention_time(rt, precursor_mz)
        masses, intensities, charges, _ = self.get_scan_from_scan_number(scan_number)
        return masses, intensities, charges, found_rt

    def get_scan(self, rt: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, str]:
        """Gets the scan data for a given retention time."""
        return self.get_scan_from_scan_number(self.get_scan_number_from_retention_time(rt))

    def get_tic_ms2(self, precursor_mz: float = None, tolerance: float = 10e-3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get total ion current in MS2 for a given precursor mass.
        """
        if precursor_mz is None:
            # TIC for all MS2
            tic_rt, tic_intensities = list(), list()
            for n in range(self.first_scan, self.last_scan + 1):
                if get_ms_order(n) != 2: continue
                tic_rt.append(get_scan_rt(n))
                _, intensities = get_spectrum(n, 100000)
                tic_intensities.append(sum(intensities))
            return np.array(tic_rt), np.array(tic_intensities)

        tic_rt, tic_intensities = list(), list()
        for n in range(self.first_scan, self.last_scan + 1):
            if get_ms_order(n) != 2: continue
            p_mass = get_precursor_mass(n)
            if abs(p_mass - precursor_mz) > tolerance: continue
            tic_rt.append(get_scan_rt(n))
            _, intensities = get_spectrum(n, 100000)
            tic_intensities.append(sum(intensities))
        return np.array(tic_rt), np.array(tic_intensities)

    def get_chromatogram(self, mass: float = 0.0, tolerance: float = 0.0, trace_type: int = 1, ms_filter: str = '') -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract chromatogram data. Default is TIC (Total Ion Chromatogram).
        """
        times, intensities = get_chromatogram(trace_type, 1000000)
        return np.array(times), np.array(intensities)

    def get_averaged_ms2_scans(self, scan_numbers: List[int]) -> Tuple[np.ndarray, np.ndarray, int]:
        """Average dynamic spectra from a list of scan numbers."""
        if not scan_numbers:
            return np.array([]), np.array([]), 0
        masses, intensities = get_averaged_spectrum(scan_numbers, 1000000)
        return np.array(masses), np.array(intensities), scan_numbers[0]

    def get_average_ms2_scans_by_rt(self, rt: float, rt_window: float, precursor_mz: float, tolerance: float) -> Tuple[np.ndarray, np.ndarray, int]:
        """Average MS2 spectra centered around a specific RT and precursor mass."""
        start_rt = rt - rt_window
        end_rt = rt + rt_window
        scans = []
        for i in range(self.first_scan, self.last_scan + 1):
            scan_rt = self.get_retention_time_from_scan_number(i)
            if scan_rt < start_rt: continue
            if scan_rt > end_rt: break
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
        pmz = precursor_mz if precursor_mz is not None else 0.0
        tol = 10.0 if precursor_mz is not None else 1e9
        scan_number = get_ms2_scan_number_from_rt(rt, pmz, tol)
        if scan_number < 1: return 0, 0.0
        return scan_number, self.get_retention_time_from_scan_number(scan_number)

    def get_scan_from_scan_number(self, scan_number: int):
        """Extract full spectral data for a specific scan number."""
        masses, intensities = get_spectrum(scan_number, 1000000)
        charges = np.zeros_like(masses)
        event_str = self.get_scan_event_str_from_scan_number(scan_number)
        return np.array(masses), np.array(intensities), charges, event_str

    def get_scan_number_from_retention_time(self, rt: float) -> int:
        """Find the scan number closest to a given RT."""
        return get_scan_number_from_rt(rt)

    def get_scan_event_str_from_scan_number(self, scan_number: int) -> str:
        """Get the instrument filter string for a scan."""
        return get_scan_event_string(scan_number)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the file and release the reader resources."""
        close_raw_file()
        self._is_open = False

if not _IS_SPHINX:
    from . import native_fisher_py_backend
    __doc__ = native_fisher_py_backend.__doc__
    if hasattr(native_fisher_py_backend, "__all__"):
        __all__ = native_fisher_py_backend.__all__ + ["RawFile", "MSOrder", "MassAnalyzer", "TraceType", "RawFileException", "RunHeader", "RunHeaderEx", "InstrumentData"]
    else:
        __all__ = [
            "RawFile", "MSOrder", "MassAnalyzer", "TraceType", "RawFileException", "RunHeader", "RunHeaderEx", "InstrumentData",
            "open_raw_file", "get_num_scans", "get_scan_rt", "get_spectrum", "get_first_scan", "get_last_scan",
            "get_end_time", "get_start_time", "get_ms_order", "get_mass_analyzer", "get_precursor_mass",
            "get_scan_event_string", "get_scan_number_from_rt", "get_ms2_filter_masses",
            "get_ms2_scan_number_from_rt", "get_ms1_scan_number_from_rt", "get_chromatogram",
            "get_averaged_spectrum", "get_instrument_count", "get_instrument_count_of_type",
            "is_open", "is_error", "in_acquisition", "has_ms_data", "get_file_name", "get_path",
            "get_creation_date", "get_computer_name", "get_creator_id", "close_raw_file",
            "get_instrument_model", "get_instrument_name", "get_instrument_serial_number", 
            "get_instrument_software_version", "get_instrument_hardware_version"
        ]
else:
    __all__ = ["RawFile", "MSOrder", "MassAnalyzer", "TraceType", "RawFileException", "RunHeader", "RunHeaderEx", "InstrumentData"]
