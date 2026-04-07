from .classes import *

class DataClass(object):
    @property
    def auto_sampler_information(self): from . import auto_sampler_information; return auto_sampler_information
    @property
    def common_core_data_object(self): from . import common_core_data_object; return common_core_data_object
    @property
    def device(self): from . import device; return device
    @property
    def error_log_entry(self): from . import error_log_entry; return error_log_entry
    @property
    def file_error(self): from . import file_error; return file_error
    @property
    def file_header(self): from . import file_header; return file_header
    @property
    def file_type(self): from . import file_type; return file_type
    @property
    def filter_accurate_mass(self): from . import filter_accurate_mass; return filter_accurate_mass
    @property
    def ft_average_options(self): from . import ft_average_options; return ft_average_options
    @property
    def peak_options(self): from . import peak_options; return peak_options
    @property
    def raw_file_classification(self): from . import raw_file_classification; return raw_file_classification
    @property
    def scan_dependent_details(self): from . import scan_dependent_details; return scan_dependent_details
    @property
    def scan_event(self): from . import scan_event; return scan_event
    @property
    def scan_events(self): from . import scan_events; return scan_events
    @property
    def scan_filter(self): from . import scan_filter; return scan_filter
    @property
    def sequence_file_writer(self): from . import sequence_file_writer; return sequence_file_writer
    @property
    def sequence_info(self): from . import sequence_info; return sequence_info
    @property
    def source_fragmentation_info_valid_type(self): from . import source_fragmentation_info_valid_type; return source_fragmentation_info_valid_type
    @property
    def tolerance_units(self): from . import tolerance_units; return tolerance_units
    @property
    def tray_shape(self): from . import tray_shape; return tray_shape
    
    # Static members
    Device = Device; MSOrder = MSOrder; MassAnalyzer = MassAnalyzer; TraceType = TraceType
    ScanFilter = ScanFilter; ScanEvent = ScanEvent; ScanEvents = ScanEvents; FileHeader = FileHeader; FileError = FileError
    AutoSamplerInformation = AutoSamplerInformation; CommonCoreDataObject = CommonCoreDataObject; FileType = FileType
    RawFileClassification = RawFileClassification; ScanDependentDetails = ScanDependentDetails; SequenceFileWriter = SequenceFileWriter
    SequenceInfo = SequenceInfo; SourceFragmentationInfoValidType = SourceFragmentationInfoValidType; ToleranceUnits = ToleranceUnits
    TrayShape = TrayShape; FilterAccurateMass = FilterAccurateMass; PeakOptions = PeakOptions; FtAverageOptions = FtAverageOptions
    ErrorLogEntry = ErrorLogEntry; WrappedRunHeader = WrappedRunHeader; wrapped_run_header = WrappedRunHeader; ChromatogramData = ChromatogramData; DataUnits = DataUnits

    @property
    def business(self): from . import business as b; return b
    @property
    def filter_enums(self): from . import filter_enums as f; return f

# Actually instantiate it as the 'data' member in 'data' module
data = DataClass()

from . import business
from . import filter_enums
