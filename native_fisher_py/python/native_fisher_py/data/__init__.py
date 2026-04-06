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
        # Fallback for direct module testing
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
    # Stubs for documentation
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
    def __init__(self, value=0):
        self.value = value
    def __str__(self): return self.name
    def __int__(self): return self.value
    def __repr__(self): return f"<{self.__class__.__name__}.{self.name if self.name else self.value}>"

class Device:
    MS = 1
    PDA = 2
    UV = 3
    Analog = 4
    MSAnalog = 4
    Other = 5
    none = 0
    Pda = 2
    name = "MS"
    value = 1

class ToleranceUnits(EnumBase): pass

class MSOrder:
    Ms = 1
    Ms2 = 2
    Ms3 = 3

MsOrderType = MSOrder

class MassAnalyzer:
    Any = 0
    ITMS = 1
    TQMS = 2
    SQMS = 3
    TOFMS = 4
    FTMS = 5
    Sector = 6

MassAnalyzerType = MassAnalyzer

class TraceType:
    MassRange = 0
    TIC = 1
    BasePeak = 2

class TriState(EnumBase):
    Any = 0
    Off = 1
    On = 2
TriState.Any = TriState(0); TriState.Any.name = "Any"
TriState.Off = TriState(1); TriState.Off.name = "Off"
TriState.On = TriState(2); TriState.On.name = "On"

class EventAccurateMass(EnumBase):
    Off = 0
    External = 1
    Internal = 2
    On = 3
EventAccurateMass.Off = EventAccurateMass(0); EventAccurateMass.Off.name = "Off"
EventAccurateMass.External = EventAccurateMass(1); EventAccurateMass.External.name = "External"
EventAccurateMass.Internal = EventAccurateMass(2); EventAccurateMass.Internal.name = "Internal"
EventAccurateMass.On = EventAccurateMass(3); EventAccurateMass.On.name = "On"

class SourceFragmentationValueType(EnumBase):
    Any = 0
    NoValue = 1
    Ramp = 2
    SIM = 3
    SingleValue = 4
SourceFragmentationValueType.Any = SourceFragmentationValueType(0); SourceFragmentationValueType.Any.name = "Any"
SourceFragmentationValueType.NoValue = SourceFragmentationValueType(1); SourceFragmentationValueType.NoValue.name = "NoValue"
SourceFragmentationValueType.Ramp = SourceFragmentationValueType(2); SourceFragmentationValueType.Ramp.name = "Ramp"
SourceFragmentationValueType.SIM = SourceFragmentationValueType(3); SourceFragmentationValueType.SIM.name = "SIM"
SourceFragmentationValueType.SingleValue = SourceFragmentationValueType(4); SourceFragmentationValueType.SingleValue.name = "SingleValue"

class ScanModeType(EnumBase):
    Any = 0
    Crm = 1
    Full = 2
    Q1Ms = 3
    Q3Ms = 4
    Sim = 5
    Srm = 6
    Zoom = 7
ScanModeType.Any = ScanModeType(0); ScanModeType.Any.name = "Any"
ScanModeType.Crm = ScanModeType(1); ScanModeType.Crm.name = "Crm"
ScanModeType.Full = ScanModeType(2); ScanModeType.Full.name = "Full"
ScanModeType.Q1Ms = ScanModeType(3); ScanModeType.Q1Ms.name = "Q1Ms"
ScanModeType.Q3Ms = ScanModeType(4); ScanModeType.Q3Ms.name = "Q3Ms"
ScanModeType.Sim = ScanModeType(5); ScanModeType.Sim.name = "Sim"
ScanModeType.Srm = ScanModeType(6); ScanModeType.Srm.name = "Srm"
ScanModeType.Zoom = ScanModeType(7); ScanModeType.Zoom.name = "Zoom"

class CompensationVoltageType(EnumBase):
    Any = 0
    NoValue = 1
    Ramp = 2
    SIM = 3
    SingleValue = 4
CompensationVoltageType.Any = CompensationVoltageType(0); CompensationVoltageType.Any.name = "Any"
CompensationVoltageType.NoValue = CompensationVoltageType(1); CompensationVoltageType.NoValue.name = "NoValue"
CompensationVoltageType.Ramp = CompensationVoltageType(2); CompensationVoltageType.Ramp.name = "Ramp"
CompensationVoltageType.SIM = CompensationVoltageType(3); CompensationVoltageType.SIM.name = "SIM"
CompensationVoltageType.SingleValue = CompensationVoltageType(4); CompensationVoltageType.SingleValue.name = "SingleValue"

class ScanDataType(EnumBase):
    Any = 0
    Centroid = 1
    Profile = 2
ScanDataType.Any = ScanDataType(0); ScanDataType.Any.name = "Any"
ScanDataType.Centroid = ScanDataType(1); ScanDataType.Centroid.name = "Centroid"
ScanDataType.Profile = ScanDataType(2); ScanDataType.Profile.name = "Profile"

class SectorScanType(EnumBase):
    Any = 0
    SectorBScan = 1
    SectorEScan = 2
SectorScanType.Any = SectorScanType(0); SectorScanType.Any.name = "Any"
SectorScanType.SectorBScan = SectorScanType(1); SectorScanType.SectorBScan.name = "SectorBScan"
SectorScanType.SectorEScan = SectorScanType(2); SectorScanType.SectorEScan.name = "SectorEScan"

class FieldFreeRegionType(EnumBase):
    Any = 0
    FieldFreeRegion1 = 1
    FieldFreeRegion2 = 2
FieldFreeRegionType.Any = FieldFreeRegionType(0); FieldFreeRegionType.Any.name = "Any"
FieldFreeRegionType.FieldFreeRegion1 = FieldFreeRegionType(1); FieldFreeRegionType.FieldFreeRegion1.name = "FieldFreeRegion1"
FieldFreeRegionType.FieldFreeRegion2 = FieldFreeRegionType(2); FieldFreeRegionType.FieldFreeRegion2.name = "FieldFreeRegion2"

class EnergyType(EnumBase):
    Any = 0
    Valid = 1
EnergyType.Any = EnergyType(0); EnergyType.Any.name = "Any"
EnergyType.Valid = EnergyType(1); EnergyType.Valid.name = "Valid"

class IonizationModeType(EnumBase):
    Any = 0
    ElectroSpray = 1
    AtmosphericPressureChemicalIonization = 2
    NanoSpray = 3
    ChemicalIonization = 4
    ElectronImpact = 5
    FastAtomBombardment = 6
    FieldDesorption = 7
    MatrixAssistedLaserDesorptionIonization = 8
    GlowDischarge = 9
    ThermoSpray = 10
    CardNanoSprayIonization = 11
    PaperSprayIonization = 12
    IonModeBeyondKnown = 13
IonizationModeType.Any = IonizationModeType(0); IonizationModeType.Any.name = "Any"
IonizationModeType.ElectroSpray = IonizationModeType(1); IonizationModeType.ElectroSpray.name = "ElectroSpray"
IonizationModeType.AtmosphericPressureChemicalIonization = IonizationModeType(2); IonizationModeType.AtmosphericPressureChemicalIonization.name = "AtmosphericPressureChemicalIonization"
IonizationModeType.NanoSpray = IonizationModeType(3); IonizationModeType.NanoSpray.name = "NanoSpray"
IonizationModeType.ChemicalIonization = IonizationModeType(4); IonizationModeType.ChemicalIonization.name = "ChemicalIonization"
IonizationModeType.ElectronImpact = IonizationModeType(5); IonizationModeType.ElectronImpact.name = "ElectronImpact"
IonizationModeType.FastAtomBombardment = IonizationModeType(6); IonizationModeType.FastAtomBombardment.name = "FastAtomBombardment"
IonizationModeType.FieldDesorption = IonizationModeType(7); IonizationModeType.FieldDesorption.name = "FieldDesorption"
IonizationModeType.MatrixAssistedLaserDesorptionIonization = IonizationModeType(8); IonizationModeType.MatrixAssistedLaserDesorptionIonization.name = "MatrixAssistedLaserDesorptionIonization"
IonizationModeType.GlowDischarge = IonizationModeType(9); IonizationModeType.GlowDischarge.name = "GlowDischarge"
IonizationModeType.ThermoSpray = IonizationModeType(10); IonizationModeType.ThermoSpray.name = "ThermoSpray"
IonizationModeType.CardNanoSprayIonization = IonizationModeType(11); IonizationModeType.CardNanoSprayIonization.name = "CardNanoSprayIonization"
IonizationModeType.PaperSprayIonization = IonizationModeType(12); IonizationModeType.PaperSprayIonization.name = "PaperSprayIonization"
IonizationModeType.IonModeBeyondKnown = IonizationModeType(13); IonizationModeType.IonModeBeyondKnown.name = "IonModeBeyondKnown"

class ActivationType(EnumBase):
    Any = 0
    CollisionInducedDissociation = 1
    ElectronCaptureDissociation = 2
    ElectronTransferDissociation = 3
    HigherEnergyCollisionalDissociation = 4
    MultiPhotonDissociation = 5
    PQD = 6
    SAactivation = 7
    UltraVioletPhotoDissociation = 8
ActivationType.Any = ActivationType(0); ActivationType.Any.name = "Any"
ActivationType.CollisionInducedDissociation = ActivationType(1); ActivationType.CollisionInducedDissociation.name = "CollisionInducedDissociation"
ActivationType.ElectronCaptureDissociation = ActivationType(2); ActivationType.ElectronCaptureDissociation.name = "ElectronCaptureDissociation"
ActivationType.ElectronTransferDissociation = ActivationType(3); ActivationType.ElectronTransferDissociation.name = "ElectronTransferDissociation"
ActivationType.HigherEnergyCollisionalDissociation = ActivationType(4); ActivationType.HigherEnergyCollisionalDissociation.name = "HigherEnergyCollisionalDissociation"
ActivationType.MultiPhotonDissociation = ActivationType(5); ActivationType.MultiPhotonDissociation.name = "MultiPhotonDissociation"
ActivationType.PQD = ActivationType(6); ActivationType.PQD.name = "PQD"
ActivationType.SAactivation = ActivationType(7); ActivationType.SAactivation.name = "SAactivation"
ActivationType.UltraVioletPhotoDissociation = ActivationType(8); ActivationType.UltraVioletPhotoDissociation.name = "UltraVioletPhotoDissociation"

class DetectorType(EnumBase):
    Any = 0
    Detector1 = 1
DetectorType.Any = DetectorType(0); DetectorType.Any.name = "Any"
DetectorType.Detector1 = DetectorType(1); DetectorType.Detector1.name = "Detector1"

class PolarityType(EnumBase):
    Any = 0
    Positive = 1
    Negative = 2
PolarityType.Any = PolarityType(0); PolarityType.Any.name = "Any"
PolarityType.Positive = PolarityType(1); PolarityType.Positive.name = "Positive"
PolarityType.Negative = PolarityType(2); PolarityType.Negative.name = "Negative"

class SampleType(EnumBase):
    Unknown = 0
    Blank = 1
    QC = 2
    StdBracket = 3
SampleType.Unknown = SampleType(0); SampleType.Unknown.name = "Unknown"
SampleType.Blank = SampleType(1); SampleType.Blank.name = "Blank"
SampleType.QC = SampleType(2); SampleType.QC.name = "QC"
SampleType.StdBracket = SampleType(3); SampleType.StdBracket.name = "StdBracket"

class ScanDependents(CommonCoreDataObject):
    @property
    def raw_file_instrument_type(self): return 0
    @property
    def scan_dependent_detail_array(self): return []

class PeakOptions(EnumBase):
    none = 0
    Saturated = 1
    Fragmented = 2
PeakOptions.none = PeakOptions(0); PeakOptions.none.name = "none"
PeakOptions.Saturated = PeakOptions(1); PeakOptions.Saturated.name = "Saturated"
PeakOptions.Fragmented = PeakOptions(2); PeakOptions.Fragmented.name = "Fragmented"

class RawFileClassification(EnumBase):
    StandardRaw = 0
    MasterScanNumberRaw = 1
RawFileClassification.StandardRaw = RawFileClassification(0); RawFileClassification.StandardRaw.name = "StandardRaw"
RawFileClassification.MasterScanNumberRaw = RawFileClassification(1); RawFileClassification.MasterScanNumberRaw.name = "MasterScanNumberRaw"

class SourceFragmentationInfoValidType(EnumBase):
    Any = 0
    Energy = 1
SourceFragmentationInfoValidType.Any = SourceFragmentationInfoValidType(0); SourceFragmentationInfoValidType.Any.name = "Any"
SourceFragmentationInfoValidType.Energy = SourceFragmentationInfoValidType(1); SourceFragmentationInfoValidType.Energy.name = "Energy"

class FilterAccurateMass(EnumBase):
    Off = 0
    On = 1
FilterAccurateMass.Off = FilterAccurateMass(0); FilterAccurateMass.Off.name = "Off"
FilterAccurateMass.On = FilterAccurateMass(1); FilterAccurateMass.On.name = "On"

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

class mass_options(CommonCoreDataObject):
    def __init__(self, tolerance=0.0, units=0): self.tolerance, self.units = tolerance, units

class ScanStatistics(CommonCoreDataObject): pass
class SegmentedScan(CommonCoreDataObject): pass
class LogEntry(CommonCoreDataObject): pass
class HeaderItem(CommonCoreDataObject): pass
class StatusLogValues(CommonCoreDataObject): pass
class TuneDataValues(CommonCoreDataObject): pass
class Reaction(CommonCoreDataObject): pass
class Scan(CommonCoreDataObject): pass
class CentroidStream(CommonCoreDataObject): pass
class ChromatogramSignal(CommonCoreDataObject): pass

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
class AutoSamplerInformation(CommonCoreDataObject): pass

class FileHeader(CommonCoreDataObject):
    @property
    def creation_date(self) -> str: return get_creation_date()
    @property
    def who_created_id(self) -> str: return get_creator_id()

class FileError(CommonCoreDataObject): pass
class ScanEvent(CommonCoreDataObject): pass
class ScanEvents(CommonCoreDataObject): pass

class ScanFilter(CommonCoreDataObject):
    def __init__(self, filter_string=""): 
        self.name = filter_string
    
    @property
    def ms_order(self):
        if "ms2" in self.name.lower(): return 2
        if "ms" in self.name.lower(): return 1
        return 1

    @property
    def mass_analyzer(self):
        if "ftms" in self.name.lower(): return MassAnalyzer.FTMS
        if "itms" in self.name.lower(): return MassAnalyzer.ITMS
        return MassAnalyzer.Any

    @property
    def polarity(self):
        if "+" in self.name: return PolarityType.Positive
        if "-" in self.name: return PolarityType.Negative
        return PolarityType.Any

    @property
    def scan_mode(self): return 0
    @property
    def accurate_mass(self): return 0
    @property
    def ionization_mode(self): return 0

class Range(range): pass
class MassOptions(mass_options): pass

FtAverageOptions = object
ChromatogramTraceSettings = object

class RunHeader(CommonCoreDataObject):
    def __init__(self, raw_file): self._raw_file = raw_file
    @property
    def start_time(self) -> float: return get_start_time()
    @property
    def first_spectrum(self) -> int: return self._raw_file.first_scan
    @property
    def last_spectrum(self) -> int: return self._raw_file.last_scan

class RunHeaderEx(RunHeader): pass

class business:
    InstrumentData = InstrumentData
    SampleType = SampleType
    ScanStatistics = ScanStatistics
    SegmentedScan = SegmentedScan
    RunHeader = RunHeader
    SampleInformation = SampleInformation
    InstrumentSelection = InstrumentSelection
    FileHeader = FileHeader
    FileError = FileError

class filter_enums:
    ActivationType = ActivationType
    IonizationModeType = IonizationModeType
    ScanModeType = ScanModeType
    MsOrderType = EnumBase
    MassAnalyzerType = MassAnalyzer
    ToleranceUnits = EnumBase
    TraceType = TraceType
    ScanDataType = ScanDataType
    SectorScanType = SectorScanType
    FieldFreeRegionType = FieldFreeRegionType
    EnergyType = EnergyType
    EventAccurateMass = EventAccurateMass
    CompensationVoltageType = CompensationVoltageType
    SourceFragmentationValueType = SourceFragmentationValueType
    TriState = TriState
    DetectorType = DetectorType
    PolarityType = PolarityType

class data:
    Device = Device
    MSOrder = MSOrder
    MassAnalyzer = MassAnalyzer
    TraceType = TraceType
    ScanFilter = ScanFilter
    ScanEvent = ScanEvent
    ScanEvents = ScanEvents
    FileHeader = FileHeader
    FileError = FileError
    AutoSamplerInformation = AutoSamplerInformation
    CommonCoreDataObject = CommonCoreDataObject
    FileType = EnumBase
    RawFileClassification = RawFileClassification
    ScanDependentDetails = ScanDependentDetails
    SequenceFileWriter = None
    SequenceInfo = SequenceInfo
    SourceFragmentationInfoValidType = SourceFragmentationInfoValidType
    ToleranceUnits = EnumBase
    TrayShape = EnumBase
    FilterAccurateMass = FilterAccurateMass
    PeakOptions = PeakOptions
    FtAverageOptions = None
    ErrorLogEntry = ErrorLogEntry
    business = business
    filter_enums = filter_enums
