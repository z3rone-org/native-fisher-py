from .data import (
    CommonCoreDataObject, Device, MSOrder, MassAnalyzer, TraceType, 
    InstrumentData, SampleInformation, FileHeader, FileError, ScanEvent, 
    ScanEvents, ScanFilter, RunHeader, RunHeaderEx, ScanStatistics, 
    SegmentedScan, CentroidStream, ScanDependents, ErrorLogEntry, 
    LogEntry, HeaderItem, StatusLogValues, TuneDataValues, Reaction, Scan,
    ChromatogramSignal, MassOptions, Range,
    FtAverageOptions, ChromatogramTraceSettings
)
from .exceptions import (
    RawFileException, CoreException, NoSelectedDeviceException, NoSelectedMsDeviceException
)
from .raw_file import RawFile
from . import data as data_mod
from . import utils as utils_mod
from . import net_wrapping as net_wrapping_mod
from . import raw_file_reader as raw_file_reader_mod

# Aliases for parity
data = data_mod.data
utils = utils_mod
net_wrapping = net_wrapping_mod
raw_file_reader = raw_file_reader_mod
raw_file = raw_file_reader_mod # Some scripts use raw_file as a module alias

# Initialize the reader submodules
raw_file_reader_mod._init_reader_(RawFile)
exceptions = sys.modules[f"{__name__}.exceptions"]
exceptions.raw_file_exception = exceptions
exceptions.core_exception = exceptions

import sys
current_module = sys.modules[__name__]
raw_file_reader_mod.raw_file_access = raw_file_reader_mod
raw_file_reader_mod.raw_file_reader_adapter = raw_file_reader_mod
raw_file_reader_mod.scan_dependents = raw_file_reader_mod

__all__ = ["RawFile", "RawFileException", "InstrumentData", "RunHeader", "RunHeaderEx", "SampleInformation"]
