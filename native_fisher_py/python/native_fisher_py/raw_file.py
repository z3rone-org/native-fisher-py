import os
import numpy as np
from typing import List, Tuple
from .native_fisher_py_backend import *
from .data import (
    CommonCoreDataObject, InstrumentData, RunHeader, RunHeaderEx, SampleInformation, 
    InstrumentSelection, FileHeader, FileError, AutoSamplerInformation, ScanEvent, 
    ScanEvents, ScanStatistics, SegmentedScan, CentroidStream, ScanDependents, 
    MassOptions, Range, TraceType, Device, MassAnalyzerType, MsOrderType,
    ChromatogramTraceSettings, FtAverageOptions, ToleranceUnits
)
from .exceptions import RawFileException

# Aliases for parity
ToleranceUnits = ToleranceUnits
MSOrder = MsOrderType
MsOrderType = MsOrderType
MassAnalyzerType = MassAnalyzerType
Range = Range
TraceType = TraceType
np = np
MassOptions = MassOptions
ChromatogramTraceSettings = ChromatogramTraceSettings
FtAverageOptions = FtAverageOptions
Device = Device
class RawFileReaderAdapter(object):
    @staticmethod
    def file_factory(path: str):
        return RawFile(path)

__all__ = [
    'RawFile', 'MsOrderType', 'MassAnalyzerType', 'Range', 
    'ToleranceUnits', 'TraceType', 'np', 'RawFileException'
]

class RawFile(object):
    """
    A high-level wrapper to provide a drop-in replacement for fisher_py.RawFile
    """
    def __init__(self, path: str):
        """
        Open a Thermo RAW file.
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
        return RawFile(path)

    @property
    def _raw_file_access(self):
        return self

    def select_instrument(self, device_type: int, device_number: int):
        pass

    def average_scans(self, start, end): return None
    def average_scans_in_scan_range(self, start, end, options): return None
    @property
    def default_mass_options(self): return MassOptions()
    def dispose(self): self.close()
    def get_all_instrument_names_from_instrument_method(self): return []
    def get_instrument_method(self, index): return ""
    def get_instrument_type(self): return 0
    def get_segment_event_table(self): return []
    def has_instrument_method(self): return False
    def is_centroid_scan_from_scan_number(self, scan_number): return True
    def refresh_view_of_file(self): pass
    @property
    def selected_instrument(self): return 0
    def status_log_plottable_data(self): return []

    @property
    def user_label(self) -> List[str]:
        return ["Instrument", "native-fisher-py"]

    @property
    def scan_events(self) -> List[str]:
        return [self.get_scan_event_string_for_scan_number(i) for i in range(self.first_scan, min(self.first_scan + 10, self.last_scan + 1))]

    def __repr__(self):
        return f"<RawFile path='{self.path}' scans={self.number_of_scans}>"

    @property
    def path(self) -> str:
        return get_path()

    @property
    def number_of_scans(self) -> int:
        return get_num_scans()

    @property
    def first_scan(self) -> int:
        return get_first_scan()

    @property
    def last_scan(self) -> int:
        return get_last_scan()

    @property
    def file_name(self) -> str:
        return get_file_name()

    @property
    def creation_date(self) -> str:
        return get_creation_date()

    @property
    def computer_name(self) -> str:
        return get_computer_name()

    @property
    def creator_id(self) -> str:
        return get_creator_id()

    def get_instrument_data(self) -> InstrumentData:
        return InstrumentData()

    @property
    def run_header(self) -> RunHeader:
        return RunHeader(self)

    @property
    def run_header_ex(self) -> RunHeaderEx:
        return RunHeaderEx(self)

    @property
    def sample_information(self) -> SampleInformation:
        return SampleInformation()

    @property
    def instrument_selection(self) -> InstrumentSelection:
        return InstrumentSelection()

    @property
    def file_header(self) -> FileHeader:
        return FileHeader()

    @property
    def file_error(self) -> FileError:
        return FileError()

    @property
    def auto_sampler_information(self):
        return AutoSamplerInformation()

    @property
    def include_reference_and_exception_data(self) -> bool:
        return False

    @include_reference_and_exception_data.setter
    def include_reference_and_exception_data(self, value: bool):
        pass

    @property
    def is_open(self) -> bool:
        return is_open()

    @property
    def is_error(self) -> bool:
        return is_error()

    @property
    def in_acquisition(self) -> bool:
        return in_acquisition()

    def retention_time_from_scan_number(self, scan_number: int) -> float:
        return get_scan_rt(scan_number)

    def scan_number_from_retention_time(self, rt: float) -> int:
        return get_scan_number_from_rt(rt)

    def get_scan_event_for_scan_number(self, scan_number: int):
        from .data.classes import ScanEvent
        return ScanEvent(scan_number)

    def get_status_log_for_retention_time(self, rt: float):
        from .data.classes import LogEntry
        scan = self.scan_number_from_retention_time(rt)
        return LogEntry(get_status_log_values(scan))

    def get_status_log_for_scan_number(self, scan_number: int):
        from .data.classes import LogEntry
        return LogEntry(get_status_log_values(scan_number))

    def get_scan_event_string_for_scan_number(self, scan_number: int):
        return get_scan_event_string(scan_number)

    def get_centroid_stream(self, scan_number: int, include_ref_peaks: bool = False):
        return CentroidStream()

    def get_segmented_scan_from_scan_number(self, scan_number: int, stats = None):
        return SegmentedScan()

    def get_scan_stats_for_scan_number(self, scan_number: int):
        from .data.classes import ScanStatistics
        from .native_fisher_py_backend import get_scan_stats
        data = get_scan_stats(scan_number)
        return ScanStatistics(
            start_time=data[0],
            low_mass=data[1],
            high_mass=data[2],
            tic=data[3],
            base_peak_mass=data[4],
            base_peak_intensity=data[5],
            packet_count=int(data[6])
        )

    def get_chromatogram_data(self, settings, start_scan, end_scan, tolerance = None):
        from .data.classes import ChromatogramData
        if not isinstance(settings, list):
            settings = [settings]
        
        all_times = []
        all_intensities = []
        all_scans = []
        for s in settings:
            trace_type = s.trace.value if hasattr(s.trace, 'value') else int(s.trace)
            filter_str = s.filter if s.filter else ""
            
            starts = [float(r.low) for r in s.mass_ranges]
            ends = [float(r.high) for r in s.mass_ranges]
            
            times, intensities = get_chromatogram(trace_type, filter_str, starts, ends, start_scan, end_scan, 1000000)
            all_times.append(times)
            all_intensities.append(intensities)
            all_scans.append([]) # Empty scans for now
            
        return ChromatogramData(all_times, all_intensities, all_scans)

    def get_instrument_count_of_type(self, device_type):
        return get_instrument_count_of_type(device_type)

    def get_trailer_extra_information(self, scan_number): 
        from .data.classes import LogEntry
        return LogEntry(get_trailer_extra_values(scan_number))
    def get_trailer_extra_header_information(self): 
        from .data.classes import HeaderItem
        return [HeaderItem(h) for h in get_trailer_extra_header()]
    def get_trailer_extra_values(self, scan_number, formatted): 
        return get_trailer_extra_values(scan_number)
    def get_status_log_header_information(self): 
        from .data.classes import HeaderItem
        return [HeaderItem(h) for h in get_status_log_header()]
    def get_status_log_values(self, scan_number, formatted):
        from .data.classes import LogEntry
        return LogEntry(get_status_log_values(scan_number))
    def get_status_log_entries_count(self): 
        return get_status_log_count()
    def get_tune_data(self, index): return None
    def get_filters(self): return get_filters()
    def get_auto_filters(self): return []
    def get_filter_for_scan_number(self, scan_number):
        from .data.classes import ScanFilter
        return ScanFilter(scan_number)
    def get_scan_events(self, start, end): return []
    def get_scan_dependents(self, scan_number, precision): return ScanDependents()

    @property
    def has_ms_data(self) -> bool:
        return has_ms_data()

    def get_scan_type(self, scan_number: int):
        return ""

    def get_error_log_item(self, index: int):
        from .data.classes import ErrorLogEntry
        return ErrorLogEntry()

    def get_tune_data_header_information(self, index: int):
        return []

    def get_tune_data_values(self, index: int):
        from .data.classes import TuneDataValues
        return TuneDataValues()
    
    @property
    def instrument_methods_count(self) -> int:
        return 0

    @property
    def instrument_count(self) -> int:
        return get_instrument_count()

    @property
    def total_time_min(self) -> float:
        return get_end_time()

    def get_chromatogram(self, mass: float = 0.0, tolerance: float = 0.0, trace_type: int = 1, ms_filter: str = 'ms') -> Tuple[np.ndarray, np.ndarray]:
        starts = [mass - tolerance] if mass > 0 else []
        ends = [mass + tolerance] if mass > 0 else []
        times, intensities = get_chromatogram(trace_type, ms_filter, starts, ends, -1, -1, 1000000)
        return np.array(times), np.array(intensities)

    def get_averaged_ms2_scans(self, scan_numbers: List[int]) -> Tuple[np.ndarray, np.ndarray, int]:
        if not scan_numbers:
            return np.array([]), np.array([]), 0
        masses, intensities = get_averaged_spectrum(scan_numbers, 1000000)
        return np.array(masses), np.array(intensities), scan_numbers[0]

    def get_ms1_scan_number_from_retention_time(self, rt: float) -> Tuple[int, float]:
        scan_number = get_ms1_scan_number_from_rt(rt)
        if scan_number < 1: return 0, 0.0
        return scan_number, self.retention_time_from_scan_number(scan_number)

    def get_ms2_scan_number_from_retention_time(self, rt: float, precursor_mz: float = None) -> Tuple[int, float]:
        pmz = precursor_mz if precursor_mz is not None else 0.0
        scan_number = get_ms2_scan_number_from_rt(rt, pmz, 1.0)
        if scan_number < 1: return 0, 0.0
        return scan_number, self.retention_time_from_scan_number(scan_number)

    def get_scan_event_str_from_scan_number(self, scan_number: int) -> str:
        return self.get_scan_event_string_for_scan_number(scan_number)

    def get_retention_time_from_scan_number(self, scan_number: int) -> float:
        return self.retention_time_from_scan_number(scan_number)

    def get_scan(self, scan_number: int):
        return self.get_scan_from_scan_number(scan_number)

    def get_scan_ms1(self, scan_number: int):
        return self.get_scan_from_scan_number(scan_number)

    def get_scan_ms2(self, scan_number: int):
        return self.get_scan_from_scan_number(scan_number)

    def get_tic_ms2(self):
        return np.array([]), np.array([])

    def get_average_ms2_scans_by_rt(self, rt_start, rt_end):
        return np.array([]), np.array([]), 0

    @property
    def ms2_filter_masses(self) -> List[float]:
        if not hasattr(self, "_ms2_filter_masses_cache"):
            mass_set = set()
            for i in range(self.first_scan, self.last_scan + 1):
                if get_ms_order(i) == 2:
                    mass_set.add(get_precursor_mass(i))
            self._ms2_filter_masses_cache = sorted(list(mass_set))
        return self._ms2_filter_masses_cache

    def get_precursor_mz(self, scan_number: int) -> float:
        return get_precursor_mass(scan_number)

    def get_scan_from_scan_number(self, scan_number: int):
        masses, intensities = get_spectrum(scan_number, 1000000)
        charges = np.zeros_like(masses)
        event_str = self.get_scan_event_string_for_scan_number(scan_number)
        return np.array(masses), np.array(intensities), charges, event_str

    def get_scan_number_from_retention_time(self, rt: float) -> int:
        return get_scan_number_from_rt(rt)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        close_raw_file()
