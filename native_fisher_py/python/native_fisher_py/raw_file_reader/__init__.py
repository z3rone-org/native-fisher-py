import sys
from ..data import (
    data, ScanDependents, AutoSamplerInformation, CentroidStream, 
    ChromatogramTraceSettings, Device, ErrorLogEntry, FileError, 
    FileHeader, FtAverageOptions, HeaderItem, InstrumentData, 
    InstrumentSelection, LogEntry, MassOptions, RunHeader, 
    SampleInformation, Scan, ScanEvent, ScanEvents, ScanFilter, 
    ScanStatistics, SegmentedScan, StatusLogValues, TuneDataValues,
    Reaction, RawFileClassification, ScanDependentDetails, WrappedRunHeader,
    ChromatogramData
)
from ..exceptions import RawFileException, NoSelectedDeviceException, NoSelectedMsDeviceException
from ..utils import (
    datetime_net_to_py, is_number, to_net_list, List, Tuple, datetime
)
from ..net_wrapping import clr, ThermoFisher

System = clr.System
ThermoFisher = ThermoFisher
annotations = None
NetWrapperBase = object
WrappedRunHeader = WrappedRunHeader
wrapped_run_header = WrappedRunHeader
data_model = data
data_model.WrappedRunHeader = WrappedRunHeader
data_model.wrapped_run_header = WrappedRunHeader
raw_file_access = None 
raw_file_reader_adapter = None 
scan_dependents = None 
RawFileAccess = None 
RawFileReaderAdapter = None 

def _init_reader_(raw_file_cls):
    global RawFileAccess, RawFileReaderAdapter, raw_file_access, raw_file_reader_adapter, scan_dependents
    RawFileAccess = raw_file_cls
    RawFileReaderAdapter = raw_file_cls
    raw_file_access = sys.modules[__name__]
    raw_file_reader_adapter = sys.modules[__name__]
    scan_dependents = sys.modules[__name__]

raw_file_access = sys.modules[__name__]
raw_file_reader_adapter = sys.modules[__name__]
scan_dependents = sys.modules[__name__]
