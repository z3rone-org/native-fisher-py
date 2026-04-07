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
        def get_sample_type(): return 0
        def get_sample_row_number(): return 0
        def get_sample_dilution_factor(): return 1.0
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
        def get_scan_filter_meta_filters(s): return []
        def get_scan_filter_field_free_region(s): return 0
        def get_scan_filter_index_to_multiple_activation_index(s): return 0
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
    def __str__(self):
        from . import get_scan_filter_string
        return get_scan_filter_string(self._scan_number)
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
    def meta_filters(self):
        # This will be implemented in the native layer to return a list of filter strings
        return get_scan_filter_meta_filters(self._scan_number)
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

    @property
    def source_fragmentation(self):
        return TriState(get_scan_filter_source_fragmentation(self._scan_number))
    @property
    def source_fragmentation_info_valid(self):
        return SourceFragmentationInfoValidType(get_scan_filter_source_fragmentation_info_valid(self._scan_number))
    @property
    def source_fragmentation_type(self):
        return SourceFragmentationValueType(get_scan_filter_source_fragmentation_type(self._scan_number))
    @property
    def source_fragmentation_value(self):
        return get_scan_filter_source_fragmentation_value(self._scan_number)
    @property
    def supplemental_activation(self):
        return TriState(get_scan_filter_supplemental_activation(self._scan_number))
    @property
    def higher_energy_ci_d(self):
        return TriState(get_scan_filter_higher_energy_cid(self._scan_number))
    @higher_energy_ci_d.setter
    def higher_energy_ci_d(self, val): pass
    @property
    def higher_energy_ci_d_value(self):
        return get_scan_filter_higher_energy_cid_value(self._scan_number)
    @property
    def mass_precision(self):
        return FilterAccurateMass(get_scan_filter_mass_precision(self._scan_number))
    @property
    def multi_notch(self):
        return TriState(get_scan_filter_multi_notch(self._scan_number))
    @property
    def multiplex(self):
        return TriState(get_scan_filter_multiplex(self._scan_number))
    @property
    def unique_mass_count(self):
        return get_scan_filter_unique_mass_count(self._scan_number)
    @property
    def param_a(self): return get_scan_filter_param_a(self._scan_number)
    @property
    def param_b(self): return get_scan_filter_param_b(self._scan_number)
    @property
    def param_f(self): return get_scan_filter_param_f(self._scan_number)
    @property
    def param_r(self): return get_scan_filter_param_r(self._scan_number)
    @property
    def param_v(self): return get_scan_filter_param_v(self._scan_number)
    @property
    def compensation_volt_type(self):
        return CompensationVoltageType(get_scan_filter_compensation_volt_type(self._scan_number))
    @property
    def compensation_voltage_count(self):
        return get_scan_filter_compensation_voltage_count(self._scan_number)
    @property
    def electron_capture_dissociation(self):
        return TriState(get_scan_filter_electron_capture_dissociation(self._scan_number))
    @property
    def electron_capture_dissociation_value(self):
        return get_scan_filter_electron_capture_dissociation_value(self._scan_number)
    @property
    def electron_transfer_dissociation(self):
        return TriState(get_scan_filter_electron_transfer_dissociation(self._scan_number))
    @property
    def electron_transfer_dissociation_value(self):
        return get_scan_filter_electron_transfer_dissociation_value(self._scan_number)
    @property
    def enhanced(self):
        return TriState(get_scan_filter_enhanced(self._scan_number))
    @property
    def field_free_region(self):
        return FieldFreeRegionType(get_scan_filter_field_free_region(self._scan_number))
    @property
    def get_source_fragmentation_info_valid(self): return True
    @property
    def index_to_multiple_activation_index(self): 
        return get_scan_filter_index_to_multiple_activation_index(self._scan_number)
    @property
    def locale_name(self): return "en-US"
    @property
    def multi_state_activation(self): return TriState.Off
    @property
    def multiple_photon_dissociation(self):
        return TriState(get_scan_filter_multiple_photon_dissociation(self._scan_number))
    @property
    def multiple_photon_dissociation_value(self):
        return get_scan_filter_multiple_photon_dissociation_value(self._scan_number)
    @property
    def photo_ionization(self): return TriState.Off
    @property
    def pulsed_q_dissociation(self):
        return TriState(get_scan_filter_pulsed_q_dissociation(self._scan_number))
    @property
    def pulsed_q_dissociation_value(self):
        return get_scan_filter_pulsed_q_dissociation_value(self._scan_number)
    @property
    def sector_scan(self):
        return SectorScanType(get_scan_filter_sector_scan(self._scan_number))
    @property
    def souce_fragmentaion_value_count(self): return 0
    @property
    def source_fragmentation_info_valid(self):
        return SourceFragmentationInfoValidType(get_scan_filter_source_fragmentation_info_valid(self._scan_number))

class EnumBase(object):
    _instances = {}
    def __new__(cls, value):
        key = (cls, value)
        if key not in EnumBase._instances:
            inst = super(EnumBase, cls).__new__(cls)
            EnumBase._instances[key] = inst
            return inst
        return EnumBase._instances[key]
    def __init__(self, value=0): 
        if hasattr(self, "_value"): return
        self._value = value
        self._name = None
    @property
    def name(self):
        if self._name: return self._name
        # Check class dictionary for instances or matching values
        for k, v in self.__class__.__dict__.items():
            if k.startswith("_") or k == "name" or k == "value": continue
            if isinstance(v, self.__class__) and v.value == self.value:
                return k
        # Fallback to literal class members that are integers (un-instantiated)
        for k, v in self.__class__.__dict__.items():
            if k.startswith("_") or k == "name" or k == "value": continue
            if not isinstance(v, EnumBase) and isinstance(v, int) and v == self.value:
                return k
        return str(self.value)
    @name.setter
    def name(self, val):
        self._name = val
    def __repr__(self): return str(self)
    @property
    def value(self): return self._value
    @value.setter
    def value(self, val): self._value = val
    def __int__(self): return self._value
    def __str__(self):
        return f"{self.__class__.__name__}.{self.name}"

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
    enum_val = GenericDataTypes(["NULL", "CHAR", "TRUEFALSE", "YESNO", "ONOFF", "UCHAR", "SHORT", "USHORT", "LONG", "ULONG", "FLOAT", "DOUBLE", "CHAR_STRING", "WCHAR_STRING"].index(name))
    enum_val.name = name
    setattr(GenericDataTypes, name, enum_val)
class SpectrumPacketType(EnumBase):
    Profile = 0
    Centroid = 1
    FtProfile = 2
    FtCentroid = 3
class Scan(object): pass
# ChromatogramSignal was here
class Device(EnumBase):
    MS = 1; PDA = 2; UV = 3; Analog = 4; MSAnalog = 4; Other = 5; none = 0; Pda = 2
for name, val in {"MS": 1, "PDA": 2, "UV": 3, "Analog": 4, "MSAnalog": 4, "Other": 5, "none": 0, "Pda": 2}.items():
    inst = Device(val); inst.name = name; setattr(Device, name, inst)

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

class MassAnalyzer(EnumBase):
    Any = 0; ITMS = 1; TQMS = 2; SQMS = 3; TOFMS = 4; FTMS = 5; Sector = 6; MassAnalyzerFTMS = 5; MassAnalyzerITMS = 1; MassAnalyzerSQMS = 3; MassAnalyzerSector = 6; MassAnalyzerTOFMS = 4; MassAnalyzerTQMS = 2
for name, val in {"Any": 0, "ITMS": 1, "TQMS": 2, "SQMS": 3, "TOFMS": 4, "FTMS": 5, "Sector": 6, "MassAnalyzerFTMS": 5, "MassAnalyzerITMS": 1, "MassAnalyzerSQMS": 3, "MassAnalyzerSector": 6, "MassAnalyzerTOFMS": 4, "MassAnalyzerTQMS": 2}.items():
    inst = MassAnalyzer(val); inst.name = name; setattr(MassAnalyzer, name, inst)
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
for name in ["Unknown", "Blank", "QC", "StdBracket", "SolventBlank", "MatrixBlank", "MatrixSpike", "MatrixSpikeDuplicate", "Program", "StdBracketStart", "StdBracketEnd", "StdClear", "StdUpdate"]:
    idx = ["Unknown", "Blank", "QC", "StdBracket", "SolventBlank", "MatrixBlank", "MatrixSpike", "MatrixSpikeDuplicate", "Program", "StdBracketStart", "StdBracketEnd", "StdClear", "StdUpdate"].index(name)
    ev = SampleType(idx)
    ev.name = name
    setattr(SampleType, name, ev)

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

# Mass-initialize any remaining uninstantiated enum members
for cls in EnumBase.__subclasses__():
    for name, val in list(cls.__dict__.items()):
        if not name.startswith("_") and isinstance(val, int) and name not in ["value", "name"]:
            inst = cls(val)
            inst.name = name
            setattr(cls, name, inst)

class ScanDependentDetails(CommonCoreDataObject):
    @property
    def filter_string(self): raise NotImplementedError
    @property
    def isolation_width_array(self): raise NotImplementedError
    @property
    def precursor_mass_array(self): raise NotImplementedError
    @property
    def scan_index(self): raise NotImplementedError

class SequenceInfo(CommonCoreDataObject):
    @property
    def bracket(self): raise NotImplementedError
    @property
    def column_width(self): raise NotImplementedError
    @property
    def tray_configuration(self): raise NotImplementedError
    @property
    def type_to_column_position(self): raise NotImplementedError
    @property
    def user_label(self): raise NotImplementedError
    @property
    def user_private_label(self): raise NotImplementedError

class ErrorLogEntry(CommonCoreDataObject):
    @property
    def message(self): raise NotImplementedError
    @property
    def retention_time(self): raise NotImplementedError



class InstrumentSelection(CommonCoreDataObject):
    @property
    def device_type(self): return 1
    @property
    def instrument_index(self): return 0

class ScanStatistics(CommonCoreDataObject):
    def __init__(self, start_time=0.0, low_mass=0.0, high_mass=0.0, tic=0.0, base_peak_mass=0.0, base_peak_intensity=0.0, packet_count=0, scan_number=0, ms_order=0, is_centroid_scan=False):
        self._start_time = start_time
        self._low_mass = low_mass
        self._high_mass = high_mass
        self._tic = tic
        self._base_peak_mass = base_peak_mass
        self._base_peak_intensity = base_peak_intensity
        self._packet_count = packet_count
        self._scan_number = scan_number
        self._ms_order = ms_order
        self._is_centroid_scan = bool(is_centroid_scan)

    @property
    def start_time(self): return self._start_time
    @property
    def low_mass(self): return self._low_mass
    @property
    def high_mass(self): return self._high_mass
    @property
    def tic(self): return self._tic
    @property
    def base_peak_mass(self): return self._base_peak_mass
    @property
    def base_peak_intensity(self): return self._base_peak_intensity
    @property
    def packet_count(self): return self._packet_count
    @property
    def scan_number(self): return self._scan_number
    @property
    def ms_order(self): return self._ms_order

    @property
    def absorbance_unit_scale(self): raise NotImplementedError
    def clone(self): raise NotImplementedError
    def copy_to(self, other): raise NotImplementedError
    @property
    def cycle_number(self): raise NotImplementedError
    def deep_clone(self): raise NotImplementedError
    @property
    def frequency(self): raise NotImplementedError
    @property
    def is_centroid_scan(self): return self._is_centroid_scan
    @property
    def is_uniform_time(self): raise NotImplementedError
    @property
    def long_wavelength(self): raise NotImplementedError
    @property
    def number_of_channels(self): raise NotImplementedError
    @property
    def packet_type(self): raise NotImplementedError
    @property
    def scan_event_number(self): raise NotImplementedError
    @property
    def scan_type(self): raise NotImplementedError
    @property
    def segment_number(self): raise NotImplementedError
    @property
    def short_wavelength(self): raise NotImplementedError
    @property
    def spectrum_packet_type(self): raise NotImplementedError
    @property
    def wavelength_step(self): raise NotImplementedError

class SegmentedScan(CommonCoreDataObject):
    def __init__(self, masses=None, intensities=None, scan_number=0):
        self._masses = masses if masses is not None else np.array([])
        self._intensities = intensities if intensities is not None else np.array([])
        self._scan_number = scan_number

    @property
    def masses(self): return self._masses
    @property
    def intensities(self): return self._intensities
    @property
    def scan_number(self): return self._scan_number

    @property
    def base_intensity(self): return np.max(self._intensities) if self._intensities.size > 0 else 0.0
    def clone(self): return self
    def deep_clone(self): return self
    @property
    def flags(self): return []
    def from_mass_and_intensities(self, m, i): 
        self._masses = m
        self._intensities = i
        return self
    @property
    def index_of_segment_start(self): return []
    @property
    def mass_ranges(self): return []
    @property
    def position_count(self): return len(self._masses) if self._masses is not None else 0
    @property
    def positions(self): return self._masses
    @property
    def ranges(self): return []
    @property
    def segment_count(self): return 1
    @property
    def segment_lengths(self): return [self._masses.size]
    @property
    def segment_sizes(self): return [self._masses.size]
    @property
    def sum_intensities(self): return np.sum(self._intensities)
    def to_simple_scan(self): return None
    def try_validate(self): return True
    def validate(self): pass

class LogEntry(CommonCoreDataObject):
    def __init__(self, values=None, labels=None):
        self._values = values or []
        self._labels = labels or []
    @property
    def labels(self): return self._labels
    @property
    def length(self): return len(self._values)
    @property
    def values(self): return self._values

    def keys(self):
        return [l.strip().rstrip(':') for l in self._labels]

    def __getitem__(self, key):
        clean_key = key.strip().rstrip(':')
        for i, label in enumerate(self._labels):
            if label.strip().rstrip(':') == clean_key:
                return self._values[i]
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

class HeaderItem(CommonCoreDataObject):
    def __init__(self, data):
        if "###TYPE###" in data:
            parts = data.split("###TYPE###")
            self._label = parts[0]
            try: self._data_type = GenericDataTypes(int(parts[1]))
            except: self._data_type = GenericDataTypes.NULL
        else:
            self._label = data
            self._data_type = GenericDataTypes.NULL
    
    @property
    def label(self): return self._label
    @property
    def data_type(self): return self._data_type
    @property
    def is_numeric(self): 
        if _IS_SPHINX: return 1
        raise NotImplementedError
    @property
    def is_scientific_notation(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def is_variable_header(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def format_value(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError

class StatusLogValues(CommonCoreDataObject):
    def __init__(self, retention_time=0.0, values=None):
        self._retention_time = retention_time
        self._values = values or []
    @property
    def retention_time(self): return self._retention_time
    @property
    def values(self): return self._values

class TuneDataValues(CommonCoreDataObject):
    def __init__(self, id=0, values=None):
        self._id = id
        self._values = values or []
    @property
    def id(self): return self._id
    @property
    def values(self): return self._values

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
    def collision_energy_valid(self): raise NotImplementedError
    @property
    def first_precursor_mass(self): raise NotImplementedError
    @property
    def isolation_width(self): raise NotImplementedError
    @property
    def isolation_width_offset(self): raise NotImplementedError
    @property
    def last_precursor_mass(self): raise NotImplementedError
    @property
    def multiple_activation(self): raise NotImplementedError
    @property
    def precursor_range_is_valid(self): raise NotImplementedError

class Scan(CommonCoreDataObject):
    @property
    def always_merge_segments(self): return 0
    @property
    def at_time(self): return 0.0
    @property
    def can_merged_scan(self): return 0
    @property
    def centroid_scan(self): return getattr(self, '_centroid_stream', None)
    @property
    def centroid_stream_access(self): return None
    def create_scan_reader(self, r): return None
    def deep_clone(self): return self
    @classmethod
    def from_file(cls, f, s):
        scan = cls()
        segmented_scan = f.get_segmented_scan_from_scan_number(s)
        centroid_stream = f.get_centroid_stream(s)
        scan._centroid_stream = centroid_stream
        
        # Original reader preference: if centroids are present (FTMS), use them for preferred data
        if centroid_stream is not None and centroid_stream.length > 0:
            scan._preferred_masses = centroid_stream.masses
            scan._preferred_intensities = centroid_stream.intensities
        else:
            scan._preferred_masses = segmented_scan.masses
            scan._preferred_intensities = segmented_scan.intensities
            
        return scan
    def generate_frequency_table(self): return None
    def generate_noise_table(self): return None
    @property
    def has_centroid_stream(self): 
        cs = getattr(self, '_centroid_stream', None)
        return 1 if cs is not None and cs.length > 0 else 0
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
    def preferred_intensities(self): return getattr(self, '_preferred_intensities', np.array([]))
    @property
    def preferred_masses(self): return getattr(self, '_preferred_masses', np.array([]))
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
    def __init__(self, masses=None, intensities=None):
        self._masses = masses if masses is not None else np.array([])
        self._intensities = intensities if intensities is not None else np.array([])

    @property
    def base_intensity(self): return np.max(self._intensities) if self._intensities.size > 0 else 0.0
    @property
    def base_peak_intensity(self): return self.base_intensity
    @property
    def base_peak_mass(self): return self._masses[np.argmax(self._intensities)] if self._intensities.size > 0 else 0.0
    @property
    def base_peak_noise(self): raise NotImplementedError
    @property
    def base_peak_resolution(self): raise NotImplementedError
    @property
    def baselines(self): raise NotImplementedError
    @property
    def charges(self): raise NotImplementedError
    def clear(self): raise NotImplementedError
    def clone(self): return self
    @property
    def coefficients(self): 
        if _IS_SPHINX: return np.array([])
        raise NotImplementedError
    @property
    def coefficients_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    def deep_clone(self): 
        if _IS_SPHINX: return self
        raise NotImplementedError
    @property
    def flags(self): 
        if _IS_SPHINX: return []
        raise NotImplementedError
    def get_centroids(self): 
        if _IS_SPHINX: return []
        raise NotImplementedError
    def get_label_peak(self, i): 
        if _IS_SPHINX: return None
        raise NotImplementedError
    def get_label_peaks(self): 
        if _IS_SPHINX: return []
        raise NotImplementedError
    @property
    def intensities(self): return self._intensities
    @property
    def length(self): return len(self._masses) if self._masses is not None else 0
    @property
    def masses(self): return self._masses
    @property
    def noises(self): raise NotImplementedError
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
    def barcode_status(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def calibration_file(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError
    @property
    def calibration_level(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def comment(self): return get_sample_comment()
    def deep_copy(self): raise NotImplementedError
    @property
    def dilution_factor(self): return get_sample_dilution_factor()
    @property
    def injection_volume(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def instrument_method_file(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError
    @property
    def istd_amount(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def max_user_text_column_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def processing_method_file(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError
    @property
    def row_number(self): return get_sample_row_number()
    @property
    def sample_id(self): return get_sample_id()
    @property
    def sample_name(self): return get_sample_name()
    @property
    def vial(self): return get_sample_vial()
    @property
    def sample_type(self): return SampleType(get_sample_type())
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
    def number_of_times_calibrated(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError
    @property
    def number_of_times_modified(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError
    @property
    def revision(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError
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
    def tray_index(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError
    @property
    def tray_name(self): 
        if _IS_SPHINX: return "Any"
        raise NotImplementedError
    @property
    def tray_shape(self): 
        if _IS_SPHINX: return TrayShape.Unknown
        raise NotImplementedError
    @property
    def tray_shape_as_string(self): 
        if _IS_SPHINX: return "Unknown"
        raise NotImplementedError
    @property
    def vial_index(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError
    @property
    def vials_per_tray(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError
    @property
    def vials_per_tray_x(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError
    @property
    def vials_per_tray_y(self): 
        if _IS_SPHINX: return -1
        raise NotImplementedError

class RunHeader(CommonCoreDataObject):
    def __init__(self, raw_file=None): self._raw_file = raw_file
    @property
    def start_time(self) -> float: return get_start_time()
    @property
    def first_spectrum(self) -> int: return self._raw_file.first_scan if self._raw_file else 1
    @property
    def last_spectrum(self) -> int: return self._raw_file.last_scan if self._raw_file else 1
    @property
    def end_time(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def expected_runtime(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def high_mass(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def low_mass(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def mass_resolution(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def max_integrated_intensity(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def max_intensity(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def spectra_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def status_log_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def trailer_extra_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def trailer_scan_event_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def tune_data_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def tolerance_unit(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError

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
    def error_message(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError
    @property
    def has_error(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def has_warning(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def warning_message(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError

class WrappedRunHeader(CommonCoreDataObject):
    @property
    def comment_1(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError
    @property
    def comment_2(self): 
        if _IS_SPHINX: return ""
        raise NotImplementedError
    @property
    def end_time(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def error_log_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def expected_run_time(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def filter_mass_precision(self): 
        if _IS_SPHINX: return 4
        raise NotImplementedError
    @property
    def high_mass(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def in_acquisition(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def low_mass(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def mass_resolution(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def max_integrated_intensity(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def max_intensity(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def spectra_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def status_log_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def trailer_extra_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def trailer_scan_event_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def tune_data_count(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def first_spectrum(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def last_spectrum(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @property
    def start_time(self): 
        if _IS_SPHINX: return 0.0
        raise NotImplementedError
    @property
    def tolerance_unit(self): 
        if _IS_SPHINX: return 0
        raise NotImplementedError

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
    def accurate_mass(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("accurate_mass")
    @property
    def mass_analyzer(self) -> int:
        if _IS_SPHINX: return 0
        raise NotImplementedError("mass_analyzer")
    @property
    def polarity(self) -> int:
        if _IS_SPHINX: return 1
        raise NotImplementedError("polarity")
    @property
    def scan_mode(self) -> int:
        if _IS_SPHINX: return 0
        raise NotImplementedError("scan_mode")
    @property
    def ionization_mode(self) -> int:
        if _IS_SPHINX: return 0
        raise NotImplementedError("ionization_mode")
    @property
    def is_valid(self) -> bool:
        if _IS_SPHINX: return True
        raise NotImplementedError("is_valid")
    @property
    def compensation_volt_type(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("compensation_volt_type")
    @property
    def compensation_voltage(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("compensation_voltage")
    @property
    def corona(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("corona")
    @property
    def dependent(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("dependent")
    @property
    def detector(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("detector")
    @property
    def detector_value(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("detector_value")
    @property
    def electron_capture_dissociation(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("electron_capture_dissociation")
    @property
    def electron_capture_dissociation_value(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("electron_capture_dissociation_value")
    @property
    def electron_transfer_dissociation(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("electron_transfer_dissociation")
    @property
    def electron_transfer_dissociation_value(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("electron_transfer_dissociation_value")
    @property
    def enhanced(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("enhanced")
    @property
    def field_free_region(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("field_free_region")
    @property
    def higher_energy_ci_d(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("higher_energy_ci_d")
    @property
    def higher_energy_ci_d_value(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("higher_energy_ci_d_value")
    @property
    def is_custom(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("is_custom")
    @property
    def lock(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("lock")
    @property
    def mass_calibrator_count(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("mass_calibrator_count")
    @property
    def mass_range_count(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("mass_range_count")
    @property
    def multi_notch(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("multi_notch")
    @property
    def multi_state_activation(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("multi_state_activation")
    @property
    def multiple_photon_dissociation(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("multiple_photon_dissociation")
    @property
    def multiple_photon_dissociation_value(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("multiple_photon_dissociation_value")
    @property
    def multiplex(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("multiplex")
    @property
    def param_a(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("param_a")
    @property
    def param_b(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("param_b")
    @property
    def param_f(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("param_f")
    @property
    def param_r(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("param_r")
    @property
    def param_v(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("param_v")
    @property
    def photo_ionization(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("photo_ionization")
    @property
    def pulsed_q_dissociation(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("pulsed_q_dissociation")
    @property
    def pulsed_q_dissociation_value(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("pulsed_q_dissociation_value")
    @property
    def scan_data(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("scan_data")
    @property
    def scan_type_index(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("scan_type_index")
    @property
    def sector_scan(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("sector_scan")
    @property
    def source_fragmentation(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("source_fragmentation")
    @property
    def source_fragmentation_info_count(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("source_fragmentation_info_count")
    @property
    def source_fragmentation_mass_range_count(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("source_fragmentation_mass_range_count")
    @property
    def source_fragmentation_type(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("source_fragmentation_type")
    @property
    def supplemental_activation(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("supplemental_activation")
    @property
    def turbo_scan(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("turbo_scan")
    @property
    def ultra(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("ultra")
    @property
    def wideband(self):
        if _IS_SPHINX: return 0
        raise NotImplementedError("wideband")
    def get_energy_valid(self, index):
        if _IS_SPHINX: return 0
        raise NotImplementedError("get_energy_valid")
    def get_first_precursor_mass(self, index):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("get_first_precursor_mass")
    def get_last_precursor_mass(self, index):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("get_last_precursor_mass")
    def get_isolation_width(self, index):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("get_isolation_width")
    def get_isolation_width_offset(self, index):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("get_isolation_width_offset")
    def get_is_multiple_activation(self, index):
        if _IS_SPHINX: return 0
        raise NotImplementedError("get_is_multiple_activation")
    def get_mass_range(self, index):
        if _IS_SPHINX: return (0.0, 0.0)
        raise NotImplementedError("get_mass_range")
    def get_mass_calibrator(self, index):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("get_mass_calibrator")
    def get_precursor_range_validity(self, index):
        if _IS_SPHINX: return 0
        raise NotImplementedError("get_precursor_range_validity")
    def get_source_fragmentation_info(self, index):
        if _IS_SPHINX: return None
        raise NotImplementedError("get_source_fragmentation_info")
    def get_source_fragmentation_mass_range(self, index):
        if _IS_SPHINX: return (0.0, 0.0)
        raise NotImplementedError("get_source_fragmentation_mass_range")

class ScanEvents(CommonCoreDataObject):
    def get_event(self, index):
        if _IS_SPHINX: return ScanEvent()
        raise NotImplementedError("get_event")
    def get_event_by_segment(self, segment, event):
        if _IS_SPHINX: return ScanEvent()
        raise NotImplementedError("get_event_by_segment")
    def get_event_count(self, segment):
        if _IS_SPHINX: return -1
        raise NotImplementedError("get_event_count")
    @property
    def scan_events(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("scan_events")
    @property
    def segments(self):
        if _IS_SPHINX: return -1
        raise NotImplementedError("segments")


class Range(object):
    def __init__(self, low=0.0, high=0.0):
        self._low = float(low)
        self._high = float(high)

    @property
    def low(self): return self._low
    @property
    def high(self): return self._high

    def compare_to(self, other): 
        if _IS_SPHINX: return 0
        raise NotImplementedError
    @staticmethod
    def create(l, h): return Range(l, h)
    @staticmethod
    def create_from_cetner_and_delta(c, d): return Range(c-d, c+d)
    def equals(self, other):
        if not isinstance(other, Range): return False
        return self._low == other._low and self._high == other._high
    def get_hash_code(self): return hash((self._low, self._high))
    def includes(self, val): return self._low <= val <= self._high
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
    def compound_names(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("compound_names")
    @property
    def delay_in_min(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("delay_in_min")
    @property
    def filter(self): return self._filter
    @filter.setter
    def filter(self, value): self._filter = value
    @property
    def fragment_mass(self):
        if _IS_SPHINX: return 0.0
        raise NotImplementedError("fragment_mass")
    def get_mass_range(self, index): return self._mass_ranges[index] if index < len(self._mass_ranges) else None
    @property
    def include_reference(self):
        if _IS_SPHINX: return False
        raise NotImplementedError("include_reference")
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
    def times(self):
        if _IS_SPHINX: return []
        raise NotImplementedError("times")


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
