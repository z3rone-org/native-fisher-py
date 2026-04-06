import os
import sys
from typing import List, Tuple
import numpy as np

# Detect if we are running inside Sphinx or Read the Docs
_IS_RTD = os.environ.get('READTHEDOCS') == 'True'
_IS_SPHINX = _IS_RTD or 'sphinx' in sys.modules or 'sphinx.cmd.build' in sys.modules

if not _IS_SPHINX:
    try:
        from ..native_fisher_py_backend import *
    except ImportError:
        def get_instrument_name(): return ""
        def get_instrument_model(): return ""
        def get_instrument_serial_number(): return ""
        def get_instrument_software_version(): return ""
        def get_instrument_hardware_version(): return ""
        def get_start_time(): return 0.0
        def get_file_name(): return ""
        def get_path(): return ""
        def get_creation_date(): return ""
        def get_creator_id(): return ""
else:
    def get_instrument_name(): return ""
    def get_instrument_model(): return ""
    def get_instrument_serial_number(): return ""
    def get_instrument_software_version(): return ""
    def get_instrument_hardware_version(): return ""
    def get_start_time(): return 0.0
    def get_file_name(): return ""
    def get_path(): return ""
    def get_creation_date(): return ""
    def get_creator_id(): return ""

class CommonCoreDataObject(object):
    def deep_equals(self, other): return True
    def equals(self, other): return True
    def get_hash_code(self): return 0
    def perform_default_settings(self): pass

class EnumBase(object):
    name = ""
    value = 0
    def __init__(self, value=0): self.value = value
    def __str__(self): return self.name
    def __int__(self): return self.value
    def __repr__(self): return f"<{self.__class__.__name__}.{self.name if self.name else self.value}>"

class Device:
    MS = 1; PDA = 2; UV = 3; Analog = 4; MSAnalog = 4; Other = 5; none = 0; Pda = 2; name = "MS"; value = 1

class TraceType: 
    MassRange = 0; TIC = 1; BasePeak = 2; Fragment = 3; SpectrumMax = 4; name = "TIC"; value = 1
    A2DChannel1 = 5; A2DChannel2 = 6; A2DChannel3 = 7; A2DChannel4 = 8; A2DChannel5 = 9; A2DChannel6 = 10; A2DChannel7 = 11; A2DChannel8 = 12
    Analog1 = 13; Analog2 = 14; Analog3 = 15; Analog4 = 16; Analog5 = 17; Analog6 = 18; Analog7 = 19; Analog8 = 20
    ChannelA = 21; ChannelB = 22; ChannelC = 23; ChannelD = 24; ChannelE = 25; ChannelF = 26; ChannelG = 27; ChannelH = 28
    EndAllChromatogramTraces = 29; EndAnalogChromatogramTraces = 30; EndMSChromatogramTraces = 31; EndPCA2DChromatogramTraces = 32; EndPDAChromatogramTraces = 33; EndUVChromatogramTraces = 34
    StartAnalogChromatogramTraces = 35; StartMSChromatogramTraces = 36; StartPCA2DChromatogramTraces = 37; StartPDAChromatogramTraces = 38; StartUVChromatogramTraces = 39
    TotalAbsorbance = 40; WavelengthRange = 41

class MSOrder: 
    Ms = 1; Ms1 = 1; Ms2 = 2; Ms3 = 3; Ms4 = 4; Ms5 = 5; Ms6 = 6; Ms7 = 7; Ms8 = 8; Ms9 = 9; Ms10 = 10; Any = 0; Ng = 11; Nl = 12; Par = 13; name = "Ms"; value = 1
MsOrderType = MSOrder

class MassAnalyzer:
    Any = 0; ITMS = 1; TQMS = 2; SQMS = 3; TOFMS = 4; FTMS = 5; Sector = 6; MassAnalyzerFTMS = 5; MassAnalyzerITMS = 1; MassAnalyzerSQMS = 3; MassAnalyzerSector = 6; MassAnalyzerTOFMS = 4; MassAnalyzerTQMS = 2; name = "Any"; value = 0
MassAnalyzerType = MassAnalyzer

class TriState(EnumBase): Any = 0; Off = 1; On = 2
TriState.Any = TriState(0); TriState.Any.name = "Any"
TriState.Off = TriState(1); TriState.Off.name = "Off"
TriState.On = TriState(2); TriState.On.name = "On"

class EventAccurateMass(EnumBase): Off = 0; External = 1; Internal = 2; On = 3
EventAccurateMass.Off = EventAccurateMass(0); EventAccurateMass.Off.name = "Off"
EventAccurateMass.External = EventAccurateMass(1); EventAccurateMass.External.name = "External"
EventAccurateMass.Internal = EventAccurateMass(2); EventAccurateMass.Internal.name = "Internal"
EventAccurateMass.On = EventAccurateMass(3); EventAccurateMass.On.name = "On"

class SourceFragmentationValueType(EnumBase): Any = 0; NoValue = 1; Ramp = 2; SIM = 3; SingleValue = 4
SourceFragmentationValueType.Any = SourceFragmentationValueType(0); SourceFragmentationValueType.Any.name = "Any"
SourceFragmentationValueType.NoValue = SourceFragmentationValueType(1); SourceFragmentationValueType.NoValue.name = "NoValue"
SourceFragmentationValueType.Ramp = SourceFragmentationValueType(2); SourceFragmentationValueType.Ramp.name = "Ramp"
SourceFragmentationValueType.SIM = SourceFragmentationValueType(3); SourceFragmentationValueType.SIM.name = "SIM"
SourceFragmentationValueType.SingleValue = SourceFragmentationValueType(4); SourceFragmentationValueType.SingleValue.name = "SingleValue"

class ScanModeType(EnumBase): Any = 0; Crm = 1; Full = 2; Q1Ms = 3; Q3Ms = 4; Sim = 5; Srm = 6; Zoom = 7
ScanModeType.Any = ScanModeType(0); ScanModeType.Any.name = "Any"
for name in ["Crm", "Full", "Q1Ms", "Q3Ms", "Sim", "Srm", "Zoom"]:
    setattr(ScanModeType, name, ScanModeType(["Any", "Crm", "Full", "Q1Ms", "Q3Ms", "Sim", "Srm", "Zoom"].index(name)))
    getattr(ScanModeType, name).name = name

class CompensationVoltageType(EnumBase): Any = 0; NoValue = 1; Ramp = 2; SIM = 3; SingleValue = 4
CompensationVoltageType.Any = CompensationVoltageType(0); CompensationVoltageType.Any.name = "Any"
CompensationVoltageType.NoValue = CompensationVoltageType(1); CompensationVoltageType.NoValue.name = "NoValue"
CompensationVoltageType.Ramp = CompensationVoltageType(2); CompensationVoltageType.Ramp.name = "Ramp"
CompensationVoltageType.SIM = CompensationVoltageType(3); CompensationVoltageType.SIM.name = "SIM"
CompensationVoltageType.SingleValue = CompensationVoltageType(4); CompensationVoltageType.SingleValue.name = "SingleValue"

class ScanDataType(EnumBase): Any = 0; Centroid = 1; Profile = 2
ScanDataType.Any = ScanDataType(0); ScanDataType.Any.name = "Any"
ScanDataType.Centroid = ScanDataType(1); ScanDataType.Centroid.name = "Centroid"
ScanDataType.Profile = ScanDataType(2); ScanDataType.Profile.name = "Profile"

class SectorScanType(EnumBase): Any = 0; SectorBScan = 1; SectorEScan = 2
SectorScanType.Any = SectorScanType(0); SectorScanType.Any.name = "Any"
SectorScanType.SectorBScan = SectorScanType(1); SectorScanType.SectorBScan.name = "SectorBScan"
SectorScanType.SectorEScan = SectorScanType(2); SectorScanType.SectorEScan.name = "SectorEScan"

class FieldFreeRegionType(EnumBase): Any = 0; FieldFreeRegion1 = 1; FieldFreeRegion2 = 2
FieldFreeRegionType.Any = FieldFreeRegionType(0); FieldFreeRegionType.Any.name = "Any"
FieldFreeRegionType.FieldFreeRegion1 = FieldFreeRegionType(1); FieldFreeRegionType.FieldFreeRegion1.name = "FieldFreeRegion1"
FieldFreeRegionType.FieldFreeRegion2 = FieldFreeRegionType(2); FieldFreeRegionType.FieldFreeRegion2.name = "FieldFreeRegion2"

class EnergyType(EnumBase): Any = 0; Valid = 1
EnergyType.Any = EnergyType(0); EnergyType.Any.name = "Any"
EnergyType.Valid = EnergyType(1); EnergyType.Valid.name = "Valid"

class IonizationModeType(EnumBase):
    Any = 0; ElectroSpray = 1; AtmosphericPressureChemicalIonization = 2; NanoSpray = 3; ChemicalIonization = 4; ElectronImpact = 5; FastAtomBombardment = 6; FieldDesorption = 7; MatrixAssistedLaserDesorptionIonization = 8; GlowDischarge = 9; ThermoSpray = 10; CardNanoSprayIonization = 11; PaperSprayIonization = 12; IonModeBeyondKnown = 13
    IonizationMode1 = 1; IonizationMode2 = 2; IonizationMode3 = 3; IonizationMode4 = 4; IonizationMode5 = 5; IonizationMode6 = 6; IonizationMode7 = 7; IonizationMode8 = 8; IonizationMode9 = 9
IonizationModeType.Any = IonizationModeType(0); IonizationModeType.Any.name = "Any"
IonizationModeType.ElectroSpray = IonizationModeType(1); IonizationModeType.ElectroSpray.name = "ElectroSpray"

class ActivationType(EnumBase):
    Any = 0; CollisionInducedDissociation = 1; ElectronCaptureDissociation = 2; ElectronTransferDissociation = 3; HigherEnergyCollisionalDissociation = 4; MultiPhotonDissociation = 5; PQD = 6; SAactivation = 7; UltraVioletPhotoDissociation = 8
    NegativeElectronTransferDissociation = 9; NegativeProtonTransferReaction = 10; ProtonTransferReaction = 11; LastActivation = 12
ActivationType.Any = ActivationType(0); ActivationType.Any.name = "Any"
# Add ModeA-Z
import string
for char in string.ascii_uppercase:
    setattr(ActivationType, f"Mode{char}", ActivationType(13 + ord(char) - ord('A')))
    getattr(ActivationType, f"Mode{char}").name = f"Mode{char}"

class DetectorType(EnumBase): Any = 0; Detector1 = 1; NotValid = 0; Valid = 1
DetectorType.Any = DetectorType(0); DetectorType.Any.name = "Any"
DetectorType.Detector1 = DetectorType(1); DetectorType.Detector1.name = "Detector1"

class PolarityType(EnumBase): Any = 0; Positive = 1; Negative = 2
PolarityType.Any = PolarityType(0); PolarityType.Any.name = "Any"
PolarityType.Positive = PolarityType(1); PolarityType.Positive.name = "Positive"
PolarityType.Negative = PolarityType(2); PolarityType.Negative.name = "Negative"

class SampleType(EnumBase): Unknown = 0; Blank = 1; QC = 2; StdBracket = 3; SolventBlank = 4; MatrixBlank = 5; MatrixSpike = 6; MatrixSpikeDuplicate = 7; Program = 8; StdBracketStart = 9; StdBracketEnd = 10; StdClear = 11; StdUpdate = 12
SampleType.Unknown = SampleType(0); SampleType.Unknown.name = "Unknown"

class PeakOptions(EnumBase): none = 0; Saturated = 1; Fragmented = 2; Exception = 3; LockPeak = 4; Merged = 5; Modified = 6; Reference = 7
PeakOptions.none = PeakOptions(0); PeakOptions.none.name = "none"

class RawFileClassification(EnumBase): StandardRaw = 0; MasterScanNumberRaw = 1; Indeterminate = 2
RawFileClassification.StandardRaw = RawFileClassification(0); RawFileClassification.StandardRaw.name = "StandardRaw"

class SourceFragmentationInfoValidType(EnumBase): Any = 0; Energy = 1
SourceFragmentationInfoValidType.Any = SourceFragmentationInfoValidType(0); SourceFragmentationInfoValidType.Any.name = "Any"

class FilterAccurateMass(EnumBase): Off = 0; On = 1; Any = 0; External = 1; Internal = 2
FilterAccurateMass.Off = FilterAccurateMass(0); FilterAccurateMass.Off.name = "Off"

class ToleranceUnits(EnumBase): amu = 0; mmu = 1; ppm = 2
ToleranceUnits.amu = ToleranceUnits(0); ToleranceUnits.amu.name = "amu"
ToleranceUnits.mmu = ToleranceUnits(1); ToleranceUnits.mmu.name = "mmu"
ToleranceUnits.ppm = ToleranceUnits(2); ToleranceUnits.ppm.name = "ppm"

class TrayShape(EnumBase): Circular = 0; Invalid = 1; Rectangular = 2; StaggeredEven = 3; StaggeredOdd = 4; Unknown = 5
TrayShape.Unknown = TrayShape(5); TrayShape.Unknown.name = "Unknown"
TrayShape.Circular = TrayShape(0); TrayShape.Circular.name = "Circular"
TrayShape.Invalid = TrayShape(1); TrayShape.Invalid.name = "Invalid"
TrayShape.Rectangular = TrayShape(2); TrayShape.Rectangular.name = "Rectangular"
TrayShape.StaggeredEven = TrayShape(3); TrayShape.StaggeredEven.name = "StaggeredEven"
TrayShape.StaggeredOdd = TrayShape(4); TrayShape.StaggeredOdd.name = "StaggeredOdd"

class FileType(EnumBase): 
    RawFile = 0; ExperimentMethod = 1; ProcessingMethod = 2; ResultsFile = 3; CalibrationFile = 4; LayoutFile = 5; MethodFile = 6; QuanFile = 7; SampleList = 8; TuneMethod = 9; XqnFile = 10; NotSupported = 11
    MethodEditorLayout = 12; ProcessingMethodEditLayout = 13; QualBrowserLayout = 14; ResultsLayout = 15; SampleListEditorLayout = 16; TuneLayout = 17
FileType.RawFile = FileType(0); FileType.RawFile.name = "RawFile"
for name in ["MethodEditorLayout", "ProcessingMethodEditLayout", "QualBrowserLayout", "ResultsLayout", "SampleListEditorLayout", "TuneLayout"]:
    setattr(FileType, name, FileType(12 + ["MethodEditorLayout", "ProcessingMethodEditLayout", "QualBrowserLayout", "ResultsLayout", "SampleListEditorLayout", "TuneLayout"].index(name)))
    getattr(FileType, name).name = name

class ScanDependentDetails(CommonCoreDataObject):
    @property
    def filter_string(self): return ""
    @property
    def isolation_width_array(self): return []
    @property
    def precursor_mass_array(self): return []
    @property
    def scan_index(self): return 0

class SequenceInfo(CommonCoreDataObject):
    @property
    def bracket(self): return 0
    @property
    def column_width(self): return []
    @property
    def tray_configuration(self): return ""
    @property
    def type_to_column_position(self): return {}
    @property
    def user_label(self): return []
    @property
    def user_private_label(self): return []

class ErrorLogEntry(CommonCoreDataObject):
    @property
    def message(self): return ""
    @property
    def retention_time(self): return 0.0

class range(CommonCoreDataObject):
    def __init__(self, low=0.0, high=0.0): self.low, self.high = low, high
    def compare_to(self, other): return 0
    def create(self, low, high): return range(low, high)
    def create_from_cetner_and_delta(self, center, delta): return range(center-delta, center+delta)
    def includes(self, val): return self.low <= val <= self.high

class mass_options(CommonCoreDataObject):
    def __init__(self, tolerance=0.0, units=0): self.tolerance, self.units = tolerance, units
MassOptions = mass_options

class ScanStatistics(CommonCoreDataObject): pass
class SegmentedScan(CommonCoreDataObject): pass
class LogEntry(CommonCoreDataObject): pass
class HeaderItem(CommonCoreDataObject): pass
class StatusLogValues(CommonCoreDataObject): pass
class TuneDataValues(CommonCoreDataObject): pass

class Reaction(CommonCoreDataObject): 
    @property
    def activation_type(self): return 0
    @property
    def collision_energy(self): return 0.0
    @property
    def collision_energy_valid(self): return 0
    @property
    def first_precursor_mass(self): return 0.0
    @property
    def isolation_width(self): return 0.0
    @property
    def isolation_width_offset(self): return 0.0
    @property
    def last_precursor_mass(self): return 0.0
    @property
    def multiple_activation(self): return 0
    @property
    def precursor_mass(self): return 0.0
    @property
    def precursor_range_is_valid(self): return 0

class Scan(CommonCoreDataObject): pass
class CentroidStream(CommonCoreDataObject): pass

class ChromatogramSignal(CommonCoreDataObject): 
    @property
    def base_peak_masses(self): return np.array([])
    def clone(self): return self
    @property
    def delay(self): return 0.0
    @property
    def end_time(self): return 0.0
    def from_chromatogram_data(self, data): return self
    def from_time_and_intensity(self, times, intensities): return self
    def from_time_intensity_scan(self, times, intensities, scans): return self
    def from_time_intensity_scan_base_peak(self, times, intensities, scans, masses): return self
    @property
    def has_base_peak_data(self): return 0
    @property
    def intensities(self): return np.array([])
    @property
    def length(self): return 0
    @property
    def scans(self): return np.array([])
    @property
    def signal_base_peak_masses(self): return np.array([])
    @property
    def signal_intensities(self): return np.array([])
    @property
    def signal_scans(self): return np.array([])
    @property
    def signal_times(self): return np.array([])
    @property
    def start_time(self): return 0.0
    @property
    def time_range(self): return range(0.0, 0.0)
    @property
    def times(self): return np.array([])
    def to_chromatogram_data(self): return None
    @property
    def valid(self): return 1

class ChromatogramTraceSettings(CommonCoreDataObject): pass

class InstrumentData(CommonCoreDataObject):
    @property
    def name(self) -> str: return get_instrument_name()
    @property
    def model(self) -> str: return get_instrument_model()
    @property
    def serial_number(self) -> str: return get_instrument_serial_number()
    @property
    def software_version(self) -> str: return get_instrument_software_version()
    @property
    def hardware_version(self) -> str: return get_instrument_hardware_version()

class SampleInformation(CommonCoreDataObject):
    @property
    def raw_file_name(self) -> str: return get_file_name()
    @property
    def path(self) -> str: return get_path()

class InstrumentSelection(CommonCoreDataObject): pass
class AutoSamplerInformation(CommonCoreDataObject):
    @property
    def tray_index(self): return -1
    @property
    def tray_name(self): return "Any"
    @property
    def tray_shape(self): return TrayShape.Unknown
    @property
    def tray_shape_as_string(self): return "Unknown"
    @property
    def vial_index(self): return -1
    @property
    def vials_per_tray(self): return -1
    @property
    def vials_per_tray_x(self): return -1
    @property
    def vials_per_tray_y(self): return -1

class FileHeader(CommonCoreDataObject):
    @property
    def creation_date(self) -> str: return get_creation_date()
    @property
    def who_created_id(self) -> str: return get_creator_id()
    @property
    def file_description(self): return ""
    @property
    def file_type(self): return FileType.RawFile
    @property
    def modified_date(self): return ""
    @property
    def number_of_times_calibrated(self): return -1
    @property
    def number_of_times_modified(self): return -1
    @property
    def revision(self): return -1
    @property
    def who_created_logon(self): return ""
    @property
    def who_modified_id(self): return ""
    @property
    def who_modified_logon(self): return ""

class FileError(CommonCoreDataObject): pass

class ScanEvent(CommonCoreDataObject):
    @property
    def accurate_mass(self): return 0
    @property
    def ms_order(self) -> int: return 1
    @property
    def mass_analyzer(self) -> int: return 0
    @property
    def polarity(self) -> int: return 1
    @property
    def scan_mode(self) -> int: return 0
    @property
    def ionization_mode(self) -> int: return 0
    @property
    def is_valid(self) -> bool: return True
    @property
    def compensation_volt_type(self): return 0
    @property
    def compensation_voltage(self): return 0.0
    @property
    def corona(self): return 0
    @property
    def dependent(self): return 0
    @property
    def detector(self): return 0
    @property
    def detector_value(self): return 0.0
    @property
    def electron_capture_dissociation(self): return 0
    @property
    def electron_capture_dissociation_value(self): return 0.0
    @property
    def electron_transfer_dissociation(self): return 0
    @property
    def electron_transfer_dissociation_value(self): return 0.0
    @property
    def enhanced(self): return 0
    @property
    def field_free_region(self): return 0
    @property
    def higher_energy_ci_d(self): return 0
    @property
    def higher_energy_ci_d_value(self): return 0.0
    @property
    def is_custom(self): return 0
    @property
    def lock(self): return 0
    @property
    def mass_calibrator_count(self): return -1
    @property
    def mass_count(self): return -1
    @property
    def mass_range_count(self): return -1
    @property
    def multi_notch(self): return 0
    @property
    def multi_state_activation(self): return 0
    @property
    def multiple_photon_dissociation(self): return 0
    @property
    def multiple_photon_dissociation_value(self): return 0.0
    @property
    def multiplex(self): return 0
    @property
    def name(self): return "Any"
    @property
    def param_a(self): return 0.0
    @property
    def param_b(self): return 0.0
    @property
    def param_f(self): return 0.0
    @property
    def param_r(self): return 0.0
    @property
    def param_v(self): return 0.0
    @property
    def photo_ionization(self): return 0
    @property
    def pulsed_q_dissociation(self): return 0
    @property
    def pulsed_q_dissociation_value(self): return 0.0
    @property
    def scan_data(self): return 0
    @property
    def scan_type_index(self): return -1
    @property
    def sector_scan(self): return 0
    @property
    def source_fragmentation(self): return 0
    @property
    def source_fragmentation_info_count(self): return -1
    @property
    def source_fragmentation_mass_range_count(self): return -1
    @property
    def source_fragmentation_type(self): return 0
    @property
    def supplemental_activation(self): return 0
    @property
    def turbo_scan(self): return 0
    @property
    def ultra(self): return 0
    @property
    def wideband(self): return 0
    def get_activation(self, index): return 0
    def get_energy(self, index): return 0.0
    def get_energy_valid(self, index): return 0
    def get_first_precursor_mass(self, index): return 0.0
    def get_last_precursor_mass(self, index): return 0.0
    def get_isolation_width(self, index): return 0.0
    def get_isolation_width_offset(self, index): return 0.0
    def get_is_multiple_activation(self, index): return 0
    def get_mass(self, index): return 0.0
    def get_mass_range(self, index): return (0.0, 0.0)
    def get_mass_calibrator(self, index): return 0.0
    def get_precursor_range_validity(self, index): return 0
    def get_reaction(self, index): return Reaction()
    def get_source_fragmentation_info(self, index): return None
    def get_source_fragmentation_mass_range(self, index): return (0.0, 0.0)

class ScanEvents(CommonCoreDataObject):
    def get_event(self, index): return ScanEvent()
    def get_event_by_segment(self, segment, event): return ScanEvent()
    def get_event_count(self, segment): return -1
    @property
    def scan_events(self): return []
    @property
    def segments(self): return -1

class ScanFilter(CommonCoreDataObject):
    def __init__(self, filter_string=""): self.name = filter_string
    @property
    def ms_order(self):
        if "ms2" in self.name.lower(): return 2
        return 1
    @property
    def mass_analyzer(self):
        if "ftms" in self.name.lower(): return MassAnalyzer.FTMS
        return MassAnalyzer.Any
    @property
    def polarity(self):
        if "+" in self.name: return PolarityType.Positive
        return PolarityType.Any
    @property
    def scan_mode(self): return 0
    @property
    def accurate_mass(self): return 0
    @property
    def ionization_mode(self): return 0
    @property
    def lock(self): return 0
    @property
    def meta_filters(self): return []
    @property
    def turbo_scan(self): return 0
    @property
    def ultra(self): return 0
    @property
    def wideband(self): return 0
    @property
    def compensation_volt_type(self): return 0
    @property
    def compensation_voltage(self): return 0.0
    @property
    def compensation_voltage_count(self): return -1
    @property
    def compensation_voltage_value(self): return 0.0
    @property
    def corona(self): return 0
    @property
    def dependent(self): return 0
    @property
    def detector(self): return 0
    @property
    def detector_value(self): return 0.0
    @property
    def electron_capture_dissociation(self): return 0
    @property
    def electron_capture_dissociation_value(self): return 0.0
    @property
    def electron_transfer_dissociation(self): return 0
    @property
    def electron_transfer_dissociation_value(self): return 0.0
    @property
    def enhanced(self): return 0
    @property
    def field_free_region(self): return 0
    @property
    def higher_energy_ci_d(self): return 0
    @property
    def higher_energy_ci_d_value(self): return 0.0
    @property
    def is_custom(self): return 0
    @property
    def locale_name(self): return "Any"
    @property
    def mass_precision(self): return 4
    @property
    def multi_notch(self): return 0
    @property
    def multi_state_activation(self): return 0
    @property
    def multiple_photon_dissociation(self): return 0
    @property
    def multiple_photon_dissociation_value(self): return 0.0
    @property
    def multiplex(self): return 0
    @property
    def param_a(self): return 0.0
    @property
    def param_b(self): return 0.0
    @property
    def param_f(self): return 0.0
    @property
    def param_r(self): return 0.0
    @property
    def param_v(self): return 0.0
    @property
    def photo_ionization(self): return 0
    @property
    def pulsed_q_dissociation(self): return 0
    @property
    def pulsed_q_dissociation_value(self): return 0.0
    @property
    def scan_data(self): return 0
    @property
    def sector_scan(self): return 0
    @property
    def source_fragmentation(self): return 0
    @property
    def source_fragmentation_type(self): return 0
    @property
    def source_fragmentation_value(self): return 0.0
    @property
    def supplemental_activation(self): return 0
    @property
    def unique_mass_count(self): return -1
    def get_source_fragmentation_info_valid(self, index): return 0
    def source_fragmentation_info_valid(self, index): return 0
    @property
    def index_to_multiple_activation_index(self): return []
    @property
    def souce_fragmentaion_value_count(self): return -1

class Range(range): pass
class MassOptions(mass_options): pass

class FtAverageOptions(CommonCoreDataObject):
    @property
    def max_charge_determinations(self): return -1
    @property
    def max_scans_merged(self): return -1
    @property
    def merge_in_parallel(self): return 0
    @property
    def merge_task_batching(self): return -1
    @property
    def use_noise_table_when_available(self): return 0

class RunHeader(CommonCoreDataObject):
    def __init__(self, raw_file): self._raw_file = raw_file
    @property
    def start_time(self) -> float: return get_start_time()
    @property
    def first_spectrum(self) -> int: return self._raw_file.first_scan
    @property
    def last_spectrum(self) -> int: return self._raw_file.last_scan
class RunHeaderEx(RunHeader): pass

class SequenceFileWriter(CommonCoreDataObject):
    def __init__(self): self.samples = []
    @property
    def bracket(self): return 0
    @property
    def file_error(self): return None
    @property
    def file_header(self): return None
    @property
    def file_name(self): return ""
    def get_user_column_label(self, index): return ""
    @property
    def info(self): return None
    @property
    def is_error(self): return 0
    def save(self, path): pass
    def set_user_column_label(self, index, label): pass
    @property
    def tray_configuration(self): return ""

class ScanDependents(CommonCoreDataObject):
    @property
    def raw_file_instrument_type(self): return 0
    @property
    def scan_dependent_detail_array(self): return []

class business:
    InstrumentData = InstrumentData; SampleType = SampleType; ScanStatistics = ScanStatistics; SegmentedScan = SegmentedScan; RunHeader = RunHeader; SampleInformation = SampleInformation; InstrumentSelection = InstrumentSelection; FileHeader = FileHeader; FileError = FileError; CentroidStream = CentroidStream; ChromatogramSignal = ChromatogramSignal; ChromatogramTraceSettings = ChromatogramTraceSettings; HeaderItem = HeaderItem; LogEntry = LogEntry; MassOptions = MassOptions; Range = Range; Reaction = Reaction; Scan = Scan; StatusLogValues = StatusLogValues; TuneDataValues = TuneDataValues; TraceType = TraceType; BarcodeStatusType = EnumBase; BracketType = EnumBase; CachedScanProvider = object; SimpleScan = object; SpectrumPacketType = object; ToleranceMode = EnumBase; NoiseAndBaseline = object; barcode_status_type = EnumBase; bracket_type = EnumBase; cached_scan_provider = object; centroid_stream = CentroidStream; chromatogram_signal = ChromatogramSignal; chromatogram_signal_cls = ChromatogramSignal; chromatogram_trace_settings = ChromatogramTraceSettings; data_units = EnumBase; generic_data_types = EnumBase; header_item = HeaderItem; instrument_data = InstrumentData; instrument_selection = InstrumentSelection; label_peak = object; log_entry = LogEntry; mass_options = MassOptions; mass_to_frequency_converter = object; noise_and_baseline = object; range = Range; reaction = Reaction; run_header = RunHeader; sample_information = SampleInformation; sample_type = SampleType; scan = Scan; scan_statistics = ScanStatistics; segmented_scan = SegmentedScan; simple_scan = object; spectrum_packet_type = object; status_log_values = StatusLogValues; tolerance_mode = EnumBase; trace_type = TraceType; tune_data_values = TuneDataValues; DataUnits = EnumBase; GenericDataTypes = EnumBase; MassToFrequencyConverter = object; SpectrumPacketType = object; ToleranceMode = EnumBase; NoiseAndBaseline = object; SimpleScan = object; BarcodeStatusType = EnumBase; BracketType = EnumBase; SampleType = SampleType; TraceType = TraceType

class filter_enums:
    ActivationType = ActivationType; CompensationVoltageType = CompensationVoltageType; DetectorType = DetectorType; EnergyType = EnergyType; EventAccurateMass = EventAccurateMass; FieldFreeRegionType = FieldFreeRegionType; IonizationModeType = IonizationModeType; MassAnalyzerType = MassAnalyzer; MsOrderType = MsOrderType; PolarityType = PolarityType; ScanDataType = ScanDataType; ScanModeType = ScanModeType; SectorScanType = SectorScanType; SourceFragmentationValueType = SourceFragmentationValueType; TriState = TriState
    activation_type = ActivationType; compensation_voltage_type = CompensationVoltageType; detector_type = DetectorType; energy_type = EnergyType; event_accurate_mass = EventAccurateMass; field_free_region_type = FieldFreeRegionType; ionization_mode_type = IonizationModeType; mass_analyzer_type = MassAnalyzer; ms_order_type = MsOrderType; polarity_type = PolarityType; scan_data_type = ScanDataType; scan_mode_type = ScanModeType; sector_scan_type = SectorScanType; source_fragmentation_value_type = SourceFragmentationValueType; tri_state = TriState


