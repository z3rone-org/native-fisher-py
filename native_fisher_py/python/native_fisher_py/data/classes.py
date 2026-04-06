import os
import sys
from typing import List, Tuple, Union
import enum
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
        def get_instrument_axis_label_x(): return ""
        def get_instrument_axis_label_y(): return ""
        def get_instrument_flags(): return ""
        def get_instrument_units(): return 0
        def get_instrument_is_valid(): return False
        def get_instrument_has_accurate_mass_precursors(): return False
        def get_instrument_is_tsq_quantum_file(): return False
        def get_start_time(): return 0.0
        def get_end_time(): return 0.0
        def get_mass_resolution(): return 0.0
        def get_expected_runtime(): return 0.0
        def get_max_integrated_intensity(): return 0.0
        def get_max_intensity(): return 0
        def get_file_name(): return ""
        def get_path(): return ""
        def get_file_description(): return ""
        def get_modified_date(): return ""
        def get_who_created_logon(): return ""
        def get_who_modified_id(): return ""
        def get_who_modified_logon(): return ""
        def get_sample_barcode(): return ""
        def get_sample_id(): return ""
        def get_sample_name(): return ""
        def get_sample_vial(): return ""
        def get_sample_comment(): return ""
        def get_creation_date(): return ""
        def get_creator_id(): return ""
        def get_ms_order(s): return 0
        def get_mass_analyzer(s): return 0
        def get_scan_event_string(s): return ""
        def get_scan_filter_ultra(s): return 0
        def get_scan_filter_wideband(s): return 0
        def get_scan_filter_polarity(s): return 0
        def get_scan_filter_detector(s): return 0
        def get_scan_filter_scan_data(s): return 0
        def get_scan_filter_scan_mode(s): return 0
        def get_scan_filter_accurate_mass(s): return 0
        def get_scan_filter_ionization_mode(s): return 0
        def get_scan_filter_lock(s): return 0
        def get_scan_filter_turbo_scan(s): return 0
        def get_scan_filter_corona(s): return 0
        def get_scan_filter_dependent(s): return 0
        def get_scan_filter_detector_value(s): return 0.0
        def get_scan_event_compensation_voltage(s): return 0
        def get_scan_event_compensation_voltage_value(s): return 0.0
        def get_scan_event_ms_order(s): return 0
        def get_scan_event_mass_count(s): return 0
        def get_scan_event_precursor_mass(s, i): return 0.0
        def get_scan_event_activation_type(s, i): return 0
        def get_scan_event_collision_energy(s, i): return 0.0
        def get_scan_stats(s): return [0.0]*7
else:
    def get_instrument_name(): return ""
    def get_instrument_model(): return ""
    def get_instrument_serial_number(): return ""
    def get_instrument_software_version(): return ""
    def get_instrument_hardware_version(): return ""
    def get_instrument_axis_label_x(): return ""
    def get_instrument_axis_label_y(): return ""
    def get_instrument_flags(): return ""
    def get_instrument_units(): return 0
    def get_instrument_is_valid(): return False
    def get_instrument_has_accurate_mass_precursors(): return False
    def get_instrument_is_tsq_quantum_file(): return False
    def get_start_time(): return 0.0
    def get_end_time(): return 0.0
    def get_mass_resolution(): return 0.0
    def get_expected_runtime(): return 0.0
    def get_max_integrated_intensity(): return 0.0
    def get_max_intensity(): return 0
    def get_file_name(): return ""
    def get_creation_date(): return ""
    def get_creator_id(): return ""
    def get_file_description(): return ""
    def get_modified_date(): return ""
    def get_who_created_logon(): return ""
    def get_who_modified_id(): return ""
    def get_who_modified_logon(): return ""
    def get_sample_barcode(): return ""
    def get_sample_id(): return ""
    def get_sample_name(): return ""
    def get_sample_vial(): return ""
    def get_sample_comment(): return ""
    def get_ms_order(s): return 0
    def get_mass_analyzer(s): return 0
    def get_scan_event_string(s): return ""
    def get_scan_filter_ultra(s): return 0
    def get_scan_filter_wideband(s): return 0
    def get_scan_filter_polarity(s): return 0
    def get_scan_filter_detector(s): return 0
    def get_scan_filter_scan_data(s): return 0
    def get_scan_filter_scan_mode(s): return 0
    def get_scan_filter_accurate_mass(s): return 0
    def get_scan_filter_ionization_mode(s): return 0
    def get_scan_filter_lock(s): return 0
    def get_scan_filter_turbo_scan(s): return 0
    def get_scan_filter_corona(s): return 0
    def get_scan_filter_dependent(s): return 0
    def get_scan_filter_detector_value(s): return 0.0
    def get_scan_event_compensation_voltage(s): return 0
    def get_scan_event_compensation_voltage_value(s): return 0.0
    def get_scan_event_ms_order(s): return 0
    def get_scan_event_mass_count(s): return 0
    def get_scan_event_precursor_mass(s, i): return 0.0
    def get_scan_event_activation_type(s, i): return 0
    def get_scan_event_collision_energy(s, i): return 0.0
    def get_scan_stats(s): return [0.0]*7

class DataUnits(enum.Enum):
    none = 0
    AbsorbanceUnits = 1
    MilliAbsorbanceUnits = 2
    MicroAbsorbanceUnits = 3
    Volts = 4
    MilliVolts = 5
    MicroVolts = 6

class CommonCoreDataObject(object):
    def deep_equals(self, other): return True
    def equals(self, other): return True
    def get_hash_code(self): return 0
    def perform_default_settings(self): pass

class ScanFilter(CommonCoreDataObject):
    def __init__(self, scan_number=0):
        self._scan_number = scan_number
    @property
    def name(self):
        return get_scan_event_string(self._scan_number)
    @property
    def ms_order(self):
        return MsOrderType(get_ms_order(self._scan_number))
    @property
    def mass_analyzer(self):
        return MassAnalyzerType(get_mass_analyzer(self._scan_number))
    @property
    def polarity(self):
        return PolarityType(get_scan_filter_polarity(self._scan_number))
    @property
    def scan_data(self):
        return ScanDataType(get_scan_filter_scan_data(self._scan_number))
    @property
    def ultra(self):
        return TriState(get_scan_filter_ultra(self._scan_number))
    @property
    def wideband(self):
        return TriState(get_scan_filter_wideband(self._scan_number))
    @property
    def detector(self):
        return DetectorType(get_scan_filter_detector(self._scan_number))
    @property
    def compensation_voltage(self):
        return TriState(get_scan_event_compensation_voltage(self._scan_number))
    @property
    def compensation_voltage_value(self):
        return get_scan_event_compensation_voltage_value(self._scan_number)
    @property
    def scan_mode(self):
        return ScanModeType(get_scan_filter_scan_mode(self._scan_number))
    @property
    def accurate_mass(self):
        return EventAccurateMass(get_scan_filter_accurate_mass(self._scan_number))
    @property
    def ionization_mode(self):
        return IonizationModeType(get_scan_filter_ionization_mode(self._scan_number))
    @property
    def lock(self):
        return TriState(get_scan_filter_lock(self._scan_number))
    @property
    def meta_filters(self): return []
    @property
    def turbo_scan(self):
        return TriState(get_scan_filter_turbo_scan(self._scan_number))
    @property
    def corona(self):
        return TriState(get_scan_filter_corona(self._scan_number))
    @property
    def dependent(self):
        return TriState(get_scan_filter_dependent(self._scan_number))
    @property
    def detector_value(self):
        return get_scan_filter_detector_value(self._scan_number)

class EnumBase(object):
    def __init__(self, value=0): 
        self.value = value
        self._name = None
    @property
    def name(self):
        if self._name: return self._name
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, self.__class__) and v.value == self.value:
                return k
        return str(self.value)
    @name.setter
    def name(self, val):
        self._name = val
    def __str__(self): 
        n = self.name
        return f"{self.__class__.__name__}.{n}" if n and not n.isdigit() else str(self.value)
    def __int__(self): return self.value
    def __repr__(self): return self.__str__()

class GenericDataTypes(EnumBase):
    NULL = 0
    CHAR = 1
    TRUEFALSE = 2
    YESNO = 3
    ONOFF = 4
    UCHAR = 5
    SHORT = 6
    USHORT = 7
    LONG = 8
    ULONG = 9
    FLOAT = 10
    DOUBLE = 11
    CHAR_STRING = 12
    WCHAR_STRING = 13

for name in ["NULL", "CHAR", "TRUEFALSE", "YESNO", "ONOFF", "UCHAR", "SHORT", "USHORT", "LONG", "ULONG", "FLOAT", "DOUBLE", "CHAR_STRING", "WCHAR_STRING"]:
    setattr(GenericDataTypes, name, GenericDataTypes(["NULL", "CHAR", "TRUEFALSE", "YESNO", "ONOFF", "UCHAR", "SHORT", "USHORT", "LONG", "ULONG", "FLOAT", "DOUBLE", "CHAR_STRING", "WCHAR_STRING"].index(name)))
    getattr(GenericDataTypes, name).name = name
class SpectrumPacketType(object): pass
class Scan(object): pass
# ChromatogramSignal was here
class Device:
    MS = 1; PDA = 2; UV = 3; Analog = 4; MSAnalog = 4; Other = 5; none = 0; Pda = 2; name = "MS"; value = 1

class TraceType(EnumBase):
    MassRange = 0; TIC = 1; BasePeak = 2; Fragment = 3; SpectrumMax = 4
    A2DChannel1 = 5; A2DChannel2 = 6; A2DChannel3 = 7; A2DChannel4 = 8; A2DChannel5 = 9; A2DChannel6 = 10; A2DChannel7 = 11; A2DChannel8 = 12
    Analog1 = 13; Analog2 = 14; Analog3 = 15; Analog4 = 16; Analog5 = 17; Analog6 = 18; Analog7 = 19; Analog8 = 20
    ChannelA = 21; ChannelB = 22; ChannelC = 23; ChannelD = 24; ChannelE = 25; ChannelF = 26; ChannelG = 27; ChannelH = 28
    EndAllChromatogramTraces = 29; EndAnalogChromatogramTraces = 30; EndMSChromatogramTraces = 31; EndPCA2DChromatogramTraces = 32; EndPDAChromatogramTraces = 33; EndUVChromatogramTraces = 34
    StartAnalogChromatogramTraces = 35; StartMSChromatogramTraces = 36; StartPCA2DChromatogramTraces = 37; StartPDAChromatogramTraces = 38; StartUVChromatogramTraces = 39
    TotalAbsorbance = 40; WavelengthRange = 41

trace_type_names = ["MassRange", "TIC", "BasePeak", "Fragment", "SpectrumMax", 
                   "A2DChannel1", "A2DChannel2", "A2DChannel3", "A2DChannel4", "A2DChannel5", "A2DChannel6", "A2DChannel7", "A2DChannel8",
                   "Analog1", "Analog2", "Analog3", "Analog4", "Analog5", "Analog6", "Analog7", "Analog8",
                   "ChannelA", "ChannelB", "ChannelC", "ChannelD", "ChannelE", "ChannelF", "ChannelG", "ChannelH",
                   "EndAllChromatogramTraces", "EndAnalogChromatogramTraces", "EndMSChromatogramTraces", "EndPCA2DChromatogramTraces", "EndPDAChromatogramTraces", "EndUVChromatogramTraces",
                   "StartAnalogChromatogramTraces", "StartMSChromatogramTraces", "StartPCA2DChromatogramTraces", "StartPDAChromatogramTraces", "StartUVChromatogramTraces",
                   "TotalAbsorbance", "WavelengthRange"]

for i, name in enumerate(trace_type_names):
    setattr(TraceType, name, TraceType(i))
    getattr(TraceType, name).name = name

class MsOrderType(EnumBase):
    Any = 0; Ms1 = 1; Ms2 = 2; Ms3 = 3; Ms4 = 4; Ms5 = 5; Ms6 = 6; Ms7 = 7; Ms8 = 8; Ms9 = 9; Ms10 = 10; Ng = 11; Nl = 12; Par = 13

for name in ["Any", "Ms1", "Ms2", "Ms3", "Ms4", "Ms5", "Ms6", "Ms7", "Ms8", "Ms9", "Ms10", "Ng", "Nl", "Par"]:
    setattr(MsOrderType, name, MsOrderType(["Any", "Ms1", "Ms2", "Ms3", "Ms4", "Ms5", "Ms6", "Ms7", "Ms8", "Ms9", "Ms10", "Ng", "Nl", "Par"].index(name)))
    getattr(MsOrderType, name).name = name
MSOrder = MsOrderType

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



class InstrumentSelection(CommonCoreDataObject):
    @property
    def device_type(self): return 1
    @property
    def instrument_index(self): return 0

class ScanStatistics(CommonCoreDataObject):
    @property
    def absorbance_unit_scale(self): return 0.0
    @property
    def base_peak_intensity(self): return 0.0
    @property
    def base_peak_mass(self): return 0.0
    def clone(self): return self
    def copy_to(self, other): pass
    @property
    def cycle_number(self): return 0
    def deep_clone(self): return self
    @property
    def frequency(self): return 0.0
    @property
    def high_mass(self): return 0.0
    @property
    def is_centroid_scan(self): return 1
    @property
    def is_uniform_time(self): return 1
    @property
    def long_wavelength(self): return 0.0
    @property
    def low_mass(self): return 0.0
    @property
    def number_of_channels(self): return 0
    @property
    def packet_count(self): return 0
    @property
    def packet_type(self): return 0
    @property
    def scan_event_number(self): return 0
    @property
    def scan_number(self): return 0
    @property
    def scan_type(self): return 0
    @property
    def segment_number(self): return 0
    @property
    def short_wavelength(self): return 0.0
    @property
    def spectrum_packet_type(self): return 0
    @property
    def start_time(self): return 0.0
    @property
    def tic(self): return 0.0
    @property
    def wavelength_step(self): return 0.0

class SegmentedScan(CommonCoreDataObject):
    @property
    def base_intensity(self): return 0.0
    def clone(self): return self
    def deep_clone(self): return self
    @property
    def flags(self): return []
    def from_mass_and_intensities(self, m, i): return self
    @property
    def index_of_segment_start(self): return []
    @property
    def intensities(self): return np.array([])
    @property
    def mass_ranges(self): return []
    @property
    def position_count(self): return 0
    @property
    def positions(self): return np.array([])
    @property
    def ranges(self): return []
    @property
    def scan_number(self): return 0
    @property
    def segment_count(self): return 0
    @property
    def segment_lengths(self): return []
    @property
    def segment_sizes(self): return []
    @property
    def sum_intensities(self): return 0.0
    def to_simple_scan(self): return None
    def try_validate(self): return True
    def validate(self): pass

class LogEntry(CommonCoreDataObject):
    def __init__(self, values=None):
        self._values = values or []
    @property
    def labels(self): return []
    @property
    def length(self): return len(self._values)
    @property
    def values(self): return self._values

class HeaderItem(CommonCoreDataObject):
    def __init__(self, data):
        if ":" in data:
            parts = data.split(":")
            self._label = parts[0]
            try: self._data_type = GenericDataTypes(int(parts[1]))
            except: self._data_type = GenericDataTypes.NULL
        else:
            self._label = data
            self._data_type = 0
    @property
    def label(self): return self._label
    @property
    def data_type(self): return self._data_type
    @property
    def is_numeric(self): return 1
    @property
    def is_scientific_notation(self): return 0
    @property
    def is_variable_header(self): return 0
    @property
    def label(self): return self._label
    @property
    def string_length_or_precision(self): return 0

class StatusLogValues(CommonCoreDataObject):
    @property
    def retention_time(self): return 0.0
    @property
    def values(self): return []

class TuneDataValues(CommonCoreDataObject):
    @property
    def id(self): return 0
    @property
    def values(self): return []

class Reaction(CommonCoreDataObject): 
    def __init__(self, scan_number=0, index=0):
        self._scan_number = scan_number
        self._index = index
    @property
    def precursor_mass(self):
        return get_scan_event_precursor_mass(self._scan_number, self._index)
    @property
    def activation_type(self):
        return ActivationType(get_scan_event_activation_type(self._scan_number, self._index))
    @property
    def collision_energy(self):
        return get_scan_event_collision_energy(self._scan_number, self._index)
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
    def precursor_range_is_valid(self): return 0

class Scan(CommonCoreDataObject):
    @property
    def always_merge_segments(self): return 0
    @property
    def at_time(self): return 0.0
    @property
    def can_merged_scan(self): return 0
    @property
    def centroid_scan(self): return None
    @property
    def centroid_stream_access(self): return None
    def create_scan_reader(self, r): return None
    def deep_clone(self): return self
    def from_file(self, f, s): return self
    def generate_frequency_table(self): return None
    def generate_noise_table(self): return None
    @property
    def has_centroid_stream(self): return 0
    @property
    def has_noise_table(self): return 0
    @property
    def is_user_tolerance(self): return 0
    @property
    def mass_resolution(self): return 0.0
    @property
    def prefer_centroids(self): return 0
    @property
    def preferred_base_peak_intensity(self): return 0.0
    @property
    def preferred_base_peak_mass(self): return 0.0
    @property
    def preferred_base_peak_noise(self): return 0.0
    @property
    def preferred_base_peak_resolution(self): return 0.0
    @property
    def preferred_baselines(self): return np.array([])
    @property
    def preferred_flags(self): return []
    @property
    def preferred_intensities(self): return np.array([])
    @property
    def preferred_masses(self): return np.array([])
    @property
    def preferred_noises(self): return np.array([])
    @property
    def preferred_resolutions(self): return np.array([])
    @property
    def scan_adder(self): return None
    @property
    def scan_statistics(self): return None
    @property
    def scan_statistics_access(self): return None
    @property
    def scan_type(self): return 0
    @property
    def scans_combined(self): return []
    @property
    def segmented_scan(self): return None
    @property
    def segmented_scan_access(self): return None
    def slice(self, l, h): return self
    @property
    def subtraction_pointer(self): return None
    def to_centroid(self): return None
    @property
    def tolerance_unit(self): return 0

class CentroidStream(CommonCoreDataObject):
    @property
    def base_intensity(self): return 0.0
    @property
    def base_peak_intensity(self): return 0.0
    @property
    def base_peak_mass(self): return 0.0
    @property
    def base_peak_noise(self): return 0.0
    @property
    def base_peak_resolution(self): return 0.0
    @property
    def baselines(self): return np.array([])
    @property
    def charges(self): return np.array([])
    def clear(self): pass
    def clone(self): return self
    @property
    def coefficients(self): return np.array([])
    @property
    def coefficients_count(self): return 0
    def deep_clone(self): return self
    @property
    def flags(self): return []
    def get_centroids(self): return []
    def get_label_peak(self, i): return None
    def get_label_peaks(self): return []
    @property
    def intensities(self): return np.array([])
    @property
    def length(self): return 0
    @property
    def masses(self): return np.array([])
    @property
    def noises(self): return np.array([])
    def refresh_base_details(self): pass
    @property
    def resolutions(self): return np.array([])
    @property
    def scan_number(self): return 0
    def set_label_peaks(self, p): pass
    @property
    def sum_intensities(self): return 0.0
    @property
    def sum_masses(self): return 0.0
    def to_scan(self): return None
    def to_segmented_scan(self): return None
    def to_simple_scan(self): return None
    def try_validate(self): return True
    def validate(self): pass

class ChromatogramSignal(CommonCoreDataObject): 
    def __init__(self, times=None, intensities=None, scans=None, masses=None):
        self._times = times if times is not None else np.array([])
        self._intensities = intensities if intensities is not None else np.array([])
        self._scans = scans if scans is not None else np.array([])
        self._masses = masses if masses is not None else np.array([])

    @property
    def base_peak_masses(self): return self._masses
    def clone(self): return self
    @property
    def delay(self): return 0.0
    @property
    def end_time(self): return self._times[-1] if len(self._times) > 0 else 0.0
    
    @staticmethod
    def from_chromatogram_data(data):
        signals = []
        for i in range(data.length):
            signals.append(ChromatogramSignal(
                data.positions_array[i],
                data.intensities_array[i],
                data.scan_numbers_array[i] if i < len(data.scan_numbers_array) else np.array([])
            ))
        return signals

    @staticmethod
    def from_time_and_intensity(times, intensities):
        return ChromatogramSignal(times, intensities)

    @staticmethod
    def from_time_intensity_scan(times, intensities, scans):
        return ChromatogramSignal(times, intensities, scans)

    @staticmethod
    def from_time_intensity_scan_base_peak(times, intensities, scans, masses):
        return ChromatogramSignal(times, intensities, scans, masses)

    @property
    def has_base_peak_data(self): return 1 if len(self._masses) > 0 else 0
    @property
    def intensities(self): return self._intensities
    @property
    def length(self): return len(self._times)
    @property
    def scans(self): return self._scans
    @property
    def signal_base_peak_masses(self): return self._masses
    @property
    def start_time(self): return self._times[0] if len(self._times) > 0 else 0.0
    @property
    def times(self): return self._times
    def to_chromatogram_data(self): return None
    @property
    def valid(self): return 1



class InstrumentData(CommonCoreDataObject):
    @property
    def axis_label_x(self): return get_instrument_axis_label_x()
    @property
    def axis_label_y(self): return get_instrument_axis_label_y()
    @property
    def channel_labels(self): return []
    def clone(self): return self
    @property
    def flags(self): return get_instrument_flags()
    @property
    def has_accurate_mass_precursors(self): return get_instrument_has_accurate_mass_precursors()
    @property
    def is_tsq_quantum_file(self): return get_instrument_is_tsq_quantum_file()
    @property
    def is_valid(self): return get_instrument_is_valid()
    @property
    def units(self): return DataUnits(get_instrument_units())
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
    def barcode(self): return get_sample_barcode()
    @property
    def barcode_status(self): return 0
    @property
    def calibration_file(self): return ""
    @property
    def calibration_level(self): return 0
    @property
    def comment(self): return get_sample_comment()
    def deep_copy(self): return self
    @property
    def dilution_factor(self): return 1.0
    @property
    def injection_volume(self): return 0.0
    @property
    def instrument_method_file(self): return ""
    @property
    def istd_amount(self): return 0.0
    @property
    def max_user_text_column_count(self): return 0
    @property
    def processing_method_file(self): return ""
    @property
    def row_number(self): return 0
    @property
    def sample_id(self): return get_sample_id()
    @property
    def sample_name(self): return get_sample_name()
    @property
    def vial(self): return get_sample_vial()
    @property
    def sample_type(self): return 0
    @property
    def sample_volume(self): return 0.0
    @property
    def sample_weight(self): return 0.0
    @property
    def user_text(self): return []
    @property
    def vial(self): return ""
    @property
    def raw_file_name(self) -> str: return get_file_name()
    @property
    def path(self) -> str: return get_path()

class FileHeader(CommonCoreDataObject):
    @property
    def creation_date(self) -> str: return get_creation_date()
    @property
    def who_created_id(self) -> str: return get_creator_id()
    @property
    def file_description(self): return get_file_description()
    @property
    def file_type(self): return FileType.RawFile
    @property
    def modified_date(self): return get_modified_date()
    @property
    def number_of_times_calibrated(self): return -1
    @property
    def number_of_times_modified(self): return -1
    @property
    def revision(self): return -1
    @property
    def who_created_logon(self): return get_who_created_logon()
    @property
    def who_modified_id(self): return get_who_modified_id()
    @property
    def who_modified_logon(self): return get_who_modified_logon()

class FileError(CommonCoreDataObject):
    @property
    def error_code(self): return 0
    @property
    def error_message(self): return ""
    @property
    def has_error(self): return 0
    @property
    def has_warning(self): return 0
    @property
    def warning_message(self): return ""

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

class RunHeader(CommonCoreDataObject):
    def __init__(self, raw_file=None): self._raw_file = raw_file
    @property
    def start_time(self) -> float: return get_start_time()
    @property
    def first_spectrum(self) -> int: return self._raw_file.first_scan if self._raw_file else 1
    @property
    def last_spectrum(self) -> int: return self._raw_file.last_scan if self._raw_file else 1
    @property
    def end_time(self): return 0.0
    @property
    def expected_runtime(self): return 0.0
    @property
    def high_mass(self): return 0.0
    @property
    def low_mass(self): return 0.0
    @property
    def mass_resolution(self): return 0.0
    @property
    def max_integrated_intensity(self): return 0.0
    @property
    def max_intensity(self): return 0.0
    @property
    def spectra_count(self): return 0
    @property
    def status_log_count(self): return 0
    @property
    def trailer_extra_count(self): return 0
    @property
    def trailer_scan_event_count(self): return 0
    @property
    def tune_data_count(self): return 0
    @property
    def tolerance_unit(self): return 0

class RunHeaderEx(CommonCoreDataObject):
    def __init__(self, raw_file): self._raw_file = raw_file
    @property
    def spectra_count(self): return self._raw_file.number_of_scans
    @property
    def first_spectrum(self): return self._raw_file.first_scan
    @property
    def last_spectrum(self): return self._raw_file.last_scan
    @property
    def start_time(self): return get_start_time()
    @property
    def end_time(self): return get_end_time()
    @property
    def mass_resolution(self): return get_mass_resolution()
    @property
    def expected_runtime(self): return get_expected_runtime()
    @property
    def max_integrated_intensity(self): return get_max_integrated_intensity()
    @property
    def max_intensity(self): return get_max_intensity()
    @property
    def trailer_extra_count(self): return get_trailer_extra_count()
    @property
    def low_mass(self): return get_low_mass()
    @property
    def high_mass(self): return get_high_mass()
    @property
    def error_message(self): return ""
    @property
    def has_error(self): return 0
    @property
    def has_warning(self): return 0
    @property
    def warning_message(self): return ""

class WrappedRunHeader(CommonCoreDataObject):
    @property
    def comment_1(self): return ""
    @property
    def comment_2(self): return ""
    @property
    def end_time(self): return 0.0
    @property
    def error_log_count(self): return 0
    @property
    def expected_run_time(self): return 0.0
    @property
    def filter_mass_precision(self): return 4
    @property
    def high_mass(self): return 0.0
    @property
    def in_acquisition(self): return 0
    @property
    def low_mass(self): return 0.0
    @property
    def mass_resolution(self): return 0.0
    @property
    def max_integrated_intensity(self): return 0.0
    @property
    def max_intensity(self): return 0.0
    @property
    def spectra_count(self): return 0
    @property
    def status_log_count(self): return 0
    @property
    def trailer_extra_count(self): return 0
    @property
    def trailer_scan_event_count(self): return 0
    @property
    def tune_data_count(self): return 0
    @property
    def first_spectrum(self): return 0
    @property
    def last_spectrum(self): return 0
    @property
    def start_time(self): return 0.0
    @property
    def tolerance_unit(self): return 0

class ScanEvent(CommonCoreDataObject):
    def __init__(self, scan_number=0):
        self._scan_number = scan_number
    @property
    def ms_order(self):
        return MsOrderType(get_scan_event_ms_order(self._scan_number))
    @property
    def mass_count(self):
        return get_scan_event_mass_count(self._scan_number)
    def get_mass(self, index):
        return get_scan_event_precursor_mass(self._scan_number, index)
    def get_activation(self, index):
        return ActivationType(get_scan_event_activation_type(self._scan_number, index))
    def get_energy(self, index):
        return get_scan_event_collision_energy(self._scan_number, index)
    def get_reaction(self, index):
        return Reaction(self._scan_number, index)
    @property
    def name(self):
        return get_scan_event_string(self._scan_number)
    @property
    def accurate_mass(self): return 0
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
    def get_energy_valid(self, index): return 0
    def get_first_precursor_mass(self, index): return 0.0
    def get_last_precursor_mass(self, index): return 0.0
    def get_isolation_width(self, index): return 0.0
    def get_isolation_width_offset(self, index): return 0.0
    def get_is_multiple_activation(self, index): return 0
    def get_mass_range(self, index): return (0.0, 0.0)
    def get_mass_calibrator(self, index): return 0.0
    def get_precursor_range_validity(self, index): return 0
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

# ScanFilter consolidated at the top
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

class Range(object):
    def __init__(self, low=0.0, high=0.0):
        self.low = low
        self.high = high
class MassOptions(CommonCoreDataObject):
    def clone(self): return self
    def get_tolerance_at_mass(self, m): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("get_tolerance_at_mass")
    def get_tolerance_string(self):
        if _IS_SPHINX: return ""
        raise NotImplementedError("get_tolerance_string")
    @property
    def precision(self):
        if _IS_SPHINX: return 4
        raise NotImplementedError("precision")
    @property
    def tolerance(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("tolerance")
    @property
    def tolerance_string(self):
        if _IS_SPHINX: return ""
        raise NotImplementedError("tolerance_string")
    @property
    def tolerance_units(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("tolerance_units")

class FtAverageOptions(CommonCoreDataObject):
    @property
    def max_charge_determinations(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("max_charge_determinations")
    @property
    def max_scans_merged(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("max_scans_merged")
    @property
    def merge_in_parallel(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("merge_in_parallel")
    @property
    def merge_task_batching(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("merge_task_batching")
    @property
    def use_noise_table_when_available(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("use_noise_table_when_available")


class ScanDependents(CommonCoreDataObject):
    @property
    def raw_file_instrument_type(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("raw_file_instrument_type")
    @property
    def scan_dependent_detail_array(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("scan_dependent_detail_array")

class SequenceInfo(CommonCoreDataObject):
    @property
    def column_width(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("column_width")
    @property
    def type_to_column_position(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("type_to_column_position")
    @property
    def bracket(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("bracket")
    @property
    def user_private_label(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("user_private_label")
    @property
    def tray_configuration(self):
        if _IS_SPHINX: return ""
        raise NotImplementedError("tray_configuration")
    @property
    def user_label(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("user_label")

class SequenceFileWriter(CommonCoreDataObject):
    def __init__(self): 
        self.samples = []
        self._info = SequenceInfo()
    @property
    def bracket(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("bracket")
    @property
    def file_error(self):
        if _IS_SPHINX: return None
        raise NotImplementedError("file_error")
    @property
    def file_header(self):
        if _IS_SPHINX: return None
        raise NotImplementedError("file_header")
    @property
    def file_name(self):
        if _IS_SPHINX: return ""
        raise NotImplementedError("file_name")
    def get_user_column_label(self, index):
        if _IS_SPHINX: return ""
        raise NotImplementedError("get_user_column_label")
    @property
    def info(self):
        return self._info
    @info.setter
    def info(self, value):
        self._info = value
    @property
    def is_error(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("is_error")
    def save(self, path): pass
    def set_user_column_label(self, index, label): pass
    @property
    def tray_configuration(self):
        if _IS_SPHINX: return ""
        raise NotImplementedError("tray_configuration")


class ChromatogramTraceSettings(CommonCoreDataObject):
    def __init__(self, *args):
        self._trace = TraceType.TIC
        self._filter = ""
        self._mass_ranges = []
        if len(args) == 1:
            if isinstance(args[0], TraceType):
                self._trace = args[0]
            elif isinstance(args[0], int):
                self._trace = TraceType(args[0])
        elif len(args) == 2:
            self._filter = args[0]
            if isinstance(args[1], Range):
                self._mass_ranges = [args[1]]

    def clone(self): return self
    @property
    def compound_names(self): return []
    @property
    def delay_in_min(self): return 0.0
    @property
    def filter(self): return self._filter
    @filter.setter
    def filter(self, value): self._filter = value
    @property
    def fragment_mass(self): return 0.0
    def get_mass_range(self, index): return self._mass_ranges[index] if index < len(self._mass_ranges) else None
    @property
    def include_reference(self): return False
    @property
    def mass_range_count(self): return len(self._mass_ranges)
    @property
    def mass_ranges(self): return self._mass_ranges
    @mass_ranges.setter
    def mass_ranges(self, value): self._mass_ranges = value
    def set_mass_range(self, index, start, end=None):
        if end is None and isinstance(start, Range):
            r = start
        else:
            r = Range(start, end)
        if index < len(self._mass_ranges):
            self._mass_ranges[index] = r
        else:
            self._mass_ranges.append(r)
    @property
    def trace(self): return self._trace
    @trace.setter
    def trace(self, value): self._trace = value
    @property
    def times(self): return []


class ChromatogramData(CommonCoreDataObject):
    def __init__(self, positions_array=None, intensities_array=None, scan_numbers_array=None):
        self._positions_array = positions_array if positions_array is not None else []
        self._intensities_array = intensities_array if intensities_array is not None else []
        self._scan_numbers_array = scan_numbers_array if scan_numbers_array is not None else []

    @property
    def intensities_array(self): return self._intensities_array
    @property
    def length(self): return len(self._positions_array)
    @property
    def positions_array(self): return self._positions_array
    @property
    def scan_numbers_array(self): return self._scan_numbers_array

class business:
    InstrumentData = InstrumentData; SampleType = SampleType; ScanStatistics = ScanStatistics; SegmentedScan = SegmentedScan; RunHeader = RunHeader; SampleInformation = SampleInformation; InstrumentSelection = InstrumentSelection; FileHeader = FileHeader; FileError = FileError; CentroidStream = CentroidStream; ChromatogramSignal = ChromatogramSignal; ChromatogramTraceSettings = ChromatogramTraceSettings; HeaderItem = HeaderItem; LogEntry = LogEntry; MassOptions = MassOptions; Range = Range; Reaction = Reaction; Scan = Scan; StatusLogValues = StatusLogValues; TuneDataValues = TuneDataValues; TraceType = TraceType; BarcodeStatusType = EnumBase; BracketType = EnumBase; CachedScanProvider = object; SimpleScan = object; SpectrumPacketType = object; ToleranceMode = EnumBase; NoiseAndBaseline = object; barcode_status_type = EnumBase; bracket_type = EnumBase; cached_scan_provider = object; centroid_stream = CentroidStream; chromatogram_signal = ChromatogramSignal; chromatogram_signal_cls = ChromatogramSignal; chromatogram_trace_settings = ChromatogramTraceSettings; data_units = EnumBase; generic_data_types = EnumBase; header_item = HeaderItem; instrument_data = InstrumentData; instrument_selection = InstrumentSelection; label_peak = object; log_entry = LogEntry; mass_options = MassOptions; mass_to_frequency_converter = object; noise_and_baseline = object; range = Range; reaction = Reaction; run_header = RunHeader; sample_information = SampleInformation; sample_type = SampleType; scan = Scan; scan_statistics = ScanStatistics; segmented_scan = SegmentedScan; simple_scan = object; spectrum_packet_type = object; status_log_values = StatusLogValues; tolerance_mode = EnumBase; trace_type = TraceType; tune_data_values = TuneDataValues; DataUnits = EnumBase; GenericDataTypes = EnumBase; MassToFrequencyConverter = object; SpectrumPacketType = object; ToleranceMode = EnumBase; NoiseAndBaseline = object; SimpleScan = object; BarcodeStatusType = EnumBase; BracketType = EnumBase; SampleType = SampleType; TraceType = TraceType

class filter_enums:
    ActivationType = ActivationType; CompensationVoltageType = CompensationVoltageType; DetectorType = DetectorType; EnergyType = EnergyType; EventAccurateMass = EventAccurateMass; FieldFreeRegionType = FieldFreeRegionType; IonizationModeType = IonizationModeType; MassAnalyzerType = MassAnalyzer; MsOrderType = MsOrderType; PolarityType = PolarityType; ScanDataType = ScanDataType; ScanModeType = ScanModeType; SectorScanType = SectorScanType; SourceFragmentationValueType = SourceFragmentationValueType; TriState = TriState
    activation_type = ActivationType; compensation_voltage_type = CompensationVoltageType; detector_type = DetectorType; energy_type = EnergyType; event_accurate_mass = EventAccurateMass; field_free_region_type = FieldFreeRegionType; ionization_mode_type = IonizationModeType; mass_analyzer_type = MassAnalyzer; ms_order_type = MsOrderType; polarity_type = PolarityType; scan_data_type = ScanDataType; scan_mode_type = ScanModeType; sector_scan_type = SectorScanType; source_fragmentation_value_type = SourceFragmentationValueType; tri_state = TriState
