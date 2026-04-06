from .data import (
    CommonCoreDataObject, Device, MSOrder, MassAnalyzer, TraceType, 
    InstrumentData, SampleInformation, FileHeader, FileError, ScanEvent, 
    ScanEvents, ScanFilter, RunHeader, RunHeaderEx, ScanStatistics, 
    SegmentedScan, CentroidStream, ScanDependents
)
from .exceptions import RawFileException
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

__all__ = ["RawFile", "RawFileException", "InstrumentData", "RunHeader", "RunHeaderEx", "SampleInformation"]
