from ..data import data, ScanDependents

RawFileAccess = None 
RawFileReaderAdapter = None 
data_model = data
raw_file_access = None 
raw_file_reader_adapter = None 
scan_dependents = None 

def _init_reader_(raw_file_cls):
    global RawFileAccess, RawFileReaderAdapter, raw_file_access, raw_file_reader_adapter, scan_dependents
    RawFileAccess = raw_file_cls
    RawFileReaderAdapter = raw_file_cls
    raw_file_access = RawFileAccess
    raw_file_reader_adapter = RawFileReaderAdapter
    scan_dependents = RawFileAccess
