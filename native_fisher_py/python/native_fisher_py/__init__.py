import sys
import os
import numpy as np
from typing import List, Tuple

# Detect if we are running inside Sphinx or Read the Docs to avoid importing the native backend
_IS_RTD = os.environ.get('READTHEDOCS') == 'True'
_IS_SPHINX = _IS_RTD or 'sphinx' in sys.modules or 'sphinx.cmd.build' in sys.modules

if not _IS_SPHINX:
    try:
        from .native_fisher_py_backend import *
    except ImportError:
        raise
else:
    # Provide stubs for documentation generation on Read the Docs
    def open_raw_file(path): return 0
    def get_num_scans(): return 0
    def get_scan_rt(scan_number): return 0.0
    def get_spectrum(scan_number, max_length): return ([], [])
    def get_first_scan(): return 1
    def get_last_scan(): return 1
    def get_start_time(): return 0.0
    def get_end_time(): return 0.0
    def get_file_name(): return ""
    def get_path(): return ""
    def get_creation_date(): return ""
    def get_computer_name(): return ""
    def get_creator_id(): return ""
    def get_instrument_model(): return ""
    def get_instrument_name(): return ""
    def get_instrument_serial_number(): return ""
    def get_instrument_software_version(): return ""
    def get_instrument_hardware_version(): return ""
    def get_ms_order(scan_number): return 1
    def get_mass_analyzer(scan_number): return 0
    def get_precursor_mass(scan_number): return 0.0
    def get_scan_event_string(scan_number): return ""
    def get_scan_number_from_rt(rt): return 1
    def get_ms2_filter_masses(max_size): return []
    def get_ms2_scan_number_from_rt(rt, pmz, tol): return 1
    def get_ms1_scan_number_from_rt(rt): return 1
    def get_chromatogram(trace_type, max_length, mass=0.0, tolerance=0.0): return ([], [])
    def get_averaged_spectrum(scan_numbers, max_length): return ([], [])
    def get_instrument_count(): return 1
    def get_instrument_count_of_type(device_type): return 1
    def is_open(): return True
    def is_error(): return False
    def in_acquisition(): return False
    def has_ms_data(): return True
    def close_raw_file(): pass

# Automatic discovery of the NativeAOT library within the package
_lib_dir = os.path.dirname(__file__)
_ext = ".so"
if sys.platform == "darwin":
    _ext = ".dylib"
elif sys.platform == "win32":
    _ext = ".dll"

_lib_path = os.path.join(_lib_dir, f"ThermoNativeReader{_ext}")
if os.path.exists(_lib_path) and "THERMO_NATIVE_LIB" not in os.environ:
    os.environ["THERMO_NATIVE_LIB"] = _lib_path

class CommonCoreDataObject(object):
    def deep_equals(self, other): return True
    def equals(self, other): return True
    def get_hash_code(self): return 0
    def perform_default_settings(self): pass

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

class MSOrder:
    Ms = 1
    Ms2 = 2
    Ms3 = 3

class MassAnalyzer:
    Any = 0
    ITMS = 1
    TQMS = 2
    SQMS = 3
    TOFMS = 4
    FTMS = 5
    Sector = 6

class TraceType:
    MassRange = 0
    TIC = 1
    BasePeak = 2

class InstrumentData(CommonCoreDataObject):
    """Information about the instrument."""
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
    @property
    def axis_label_x(self) -> str: return "m/z"
    @property
    def axis_label_y(self) -> str: return "Relative Intensity"
    @property
    def channel_labels(self) -> List[str]: return []
    @property
    def flags(self) -> str: return ""
    @property
    def has_accurate_mass_precursors(self) -> bool: return True
    @property
    def is_tsq_quantum_file(self) -> bool: return False
    @property
    def is_valid(self) -> bool: return True
    @property
    def units(self): return 0
    def clone(self): return self

class SampleInformation(CommonCoreDataObject):
    """Information about the sample."""
    @property
    def sample_volume(self) -> float: return 0.0
    @property
    def sample_name(self) -> str: return ""
    @property
    def sample_id(self) -> str: return ""
    @property
    def row_number(self) -> int: return 1
    @property
    def vial(self) -> str: return ""
    @property
    def raw_file_name(self) -> str: return get_file_name()
    @property
    def path(self) -> str: return get_path()
    @property
    def comment(self) -> str: return ""
    @property
    def barcode(self) -> str: return ""
    @property
    def injection_volume(self) -> float: return 0.0
    @property
    def istd_amount(self) -> float: return 0.0
    @property
    def calibration_file(self) -> str: return ""
    @property
    def instrument_method_file(self) -> str: return ""
    @property
    def processing_method_file(self) -> str: return ""
    @property
    def dilution_factor(self) -> float: return 1.0
    @property
    def sample_weight(self) -> float: return 0.0
    @property
    def user_text(self) -> List[str]: return []

class InstrumentSelection(CommonCoreDataObject):
    """Information about selected instruments."""
    pass

class AutoSamplerInformation(CommonCoreDataObject):
    @property
    def tray_index(self): return 0
    @property
    def tray_name(self): return ""
    @property
    def tray_shape(self): return 0
    @property
    def tray_shape_as_string(self): return ""
    @property
    def vial_index(self): return 0
    @property
    def vials_per_tray(self): return 0
    @property
    def vials_per_tray_x(self): return 0
    @property
    def vials_per_tray_y(self): return 0

class FileHeader(CommonCoreDataObject):
    """Information about the file header."""
    @property
    def creation_date(self) -> str: return get_creation_date()
    @property
    def file_description(self) -> str: return ""
    @property
    def file_type(self) -> int: return 0
    @property
    def modified_date(self) -> str: return ""
    @property
    def number_of_times_calibrated(self) -> int: return 0
    @property
    def number_of_times_modified(self) -> int: return 0
    @property
    def revision(self) -> int: return 1
    @property
    def who_created_id(self) -> str: return get_creator_id()
    @property
    def who_created_logon(self) -> str: return ""
    @property
    def who_modified_id(self) -> str: return ""
    @property
    def who_modified_logon(self) -> str: return ""

class FileError(CommonCoreDataObject):
    """Information about file errors."""
    @property
    def error_code(self) -> int: return 0
    @property
    def error_message(self) -> str: return ""
    @property
    def has_error(self) -> bool: return False
    @property
    def has_warning(self) -> bool: return False
    @property
    def warning_message(self) -> str: return ""

class ScanEvent(CommonCoreDataObject):
    """Placeholder for ScanEvent."""
    @property
    def accurate_mass(self): return False
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
    def corona(self): return False
    @property
    def dependent(self): return False
    @property
    def detector(self): return 0
    @property
    def detector_value(self): return 0.0
    @property
    def electron_capture_dissociation(self): return False
    @property
    def electron_capture_dissociation_value(self): return 0.0
    @property
    def electron_transfer_dissociation(self): return False
    @property
    def electron_transfer_dissociation_value(self): return 0.0
    @property
    def enhanced(self): return False
    @property
    def field_free_region(self): return 0
    @property
    def higher_energy_ci_d(self): return False
    @property
    def higher_energy_ci_d_value(self): return 0.0
    @property
    def is_custom(self): return False
    @property
    def lock(self): return False
    @property
    def mass_calibrator_count(self): return 0
    @property
    def mass_count(self): return 0
    @property
    def mass_range_count(self): return 0
    @property
    def multi_notch(self): return False
    @property
    def multi_state_activation(self): return False
    @property
    def multiple_photon_dissociation(self): return False
    @property
    def multiple_photon_dissociation_value(self): return 0.0
    @property
    def multiplex(self): return False
    @property
    def name(self): return ""
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
    def photo_ionization(self): return False
    @property
    def pulsed_q_dissociation(self): return False
    @property
    def pulsed_q_dissociation_value(self): return 0.0
    @property
    def scan_data(self): return 0
    @property
    def scan_type_index(self): return 0
    @property
    def sector_scan(self): return 0
    @property
    def source_fragmentation(self): return False
    @property
    def source_fragmentation_info_count(self): return 0
    @property
    def source_fragmentation_mass_range_count(self): return 0
    @property
    def source_fragmentation_type(self): return 0
    @property
    def supplemental_activation(self): return False
    @property
    def turbo_scan(self): return False
    @property
    def ultra(self): return False
    @property
    def wideband(self): return False
    
    def get_activation(self, index): return 0
    def get_energy(self, index): return 0.0
    def get_energy_valid(self, index): return False
    def get_first_precursor_mass(self, index): return 0.0
    def get_last_precursor_mass(self, index): return 0.0
    def get_isolation_width(self, index): return 0.0
    def get_isolation_width_offset(self, index): return 0.0
    def get_is_multiple_activation(self, index): return False
    def get_mass(self, index): return 0.0
    def get_mass_range(self, index): return (0.0, 0.0)
    def get_mass_calibrator(self, index): return 0.0
    def get_precursor_range_validity(self, index): return False
    def get_reaction(self, index): return None
    def get_source_fragmentation_info(self, index): return None
    def get_source_fragmentation_mass_range(self, index): return (0.0, 0.0)

class ScanEvents(CommonCoreDataObject):
    def get_event(self, index): return ScanEvent()
    def get_event_by_segment(self, segment, event): return ScanEvent()
    def get_event_count(self, segment): return 0
    @property
    def scan_events(self): return []
    @property
    def segments(self): return 0

class ScanFilter(CommonCoreDataObject):
    def __init__(self, filter_string=""): self.name = filter_string
    @property
    def accurate_mass(self): return False
    @property
    def ms_order(self): return 1
    @property
    def mass_analyzer(self): return 0
    @property
    def polarity(self): return 1
    @property
    def scan_mode(self): return 0
    @property
    def ionization_mode(self): return 0
    @property
    def lock(self): return False
    @property
    def meta_filters(self): return []
    @property
    def turbo_scan(self): return False
    @property
    def ultra(self): return False
    @property
    def wideband(self): return False
    @property
    def compensation_volt_type(self): return 0
    @property
    def compensation_voltage(self): return 0.0
    @property
    def compensation_voltage_count(self): return 0
    @property
    def compensation_voltage_value(self): return 0.0
    @property
    def corona(self): return False
    @property
    def dependent(self): return False
    @property
    def detector(self): return 0
    @property
    def detector_value(self): return 0.0
    @property
    def electron_capture_dissociation(self): return False
    @property
    def electron_capture_dissociation_value(self): return 0.0
    @property
    def electron_transfer_dissociation(self): return False
    @property
    def electron_transfer_dissociation_value(self): return 0.0
    @property
    def enhanced(self): return False
    @property
    def field_free_region(self): return 0
    @property
    def higher_energy_ci_d(self): return False
    @property
    def higher_energy_ci_d_value(self): return 0.0
    @property
    def is_custom(self): return False
    @property
    def locale_name(self): return ""
    @property
    def mass_precision(self): return 4
    @property
    def multi_notch(self): return False
    @property
    def multi_state_activation(self): return False
    @property
    def multiple_photon_dissociation(self): return False
    @property
    def multiple_photon_dissociation_value(self): return 0.0
    @property
    def multiplex(self): return False
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
    def photo_ionization(self): return False
    @property
    def pulsed_q_dissociation(self): return False
    @property
    def pulsed_q_dissociation_value(self): return 0.0
    @property
    def scan_data(self): return 0
    @property
    def sector_scan(self): return 0
    @property
    def source_fragmentation(self): return False
    @property
    def source_fragmentation_type(self): return 0
    @property
    def source_fragmentation_value(self): return 0.0
    @property
    def supplemental_activation(self): return False
    @property
    def unique_mass_count(self): return 0
    def get_source_fragmentation_info_valid(self, index): return False
    def source_fragmentation_info_valid(self, index): return False
    @property
    def index_to_multiple_activation_index(self): return []
    @property
    def souce_fragmentaion_value_count(self): return 0

class Range(CommonCoreDataObject):
    def __init__(self, low=0.0, high=0.0): self.low, self.high = low, high

class MassOptions(CommonCoreDataObject):
    def __init__(self, tolerance=0.0, units=0): self.tolerance, self.units = tolerance, units

class ScanDependents(CommonCoreDataObject):
    @property
    def raw_file_instrument_type(self): return 0
    @property
    def scan_dependent_detail_array(self): return []

class FtAverageOptions(object): pass
class ChromatogramTraceSettings(object): pass
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

class EnumBase(object):
    name = ""
    value = 0
    def __str__(self): return self.name
    def __int__(self): return self.value

class TriState(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    Off = EnumBase(); Off.name, Off.value = "Off", 1
    On = EnumBase(); On.name, On.value = "On", 2

class EventAccurateMass(EnumBase):
    External = EnumBase(); External.name, External.value = "External", 1
    Internal = EnumBase(); Internal.name, Internal.value = "Internal", 2
    Off = EnumBase(); Off.name, Off.value = "Off", 0
    On = EnumBase(); On.name, On.value = "On", 3

class SourceFragmentationValueType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    NoValue = EnumBase(); NoValue.name, NoValue.value = "NoValue", 1
    Ramp = EnumBase(); Ramp.name, Ramp.value = "Ramp", 2
    SIM = EnumBase(); SIM.name, SIM.value = "SIM", 3
    SingleValue = EnumBase(); SingleValue.name, SingleValue.value = "SingleValue", 4

class ScanModeType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    Crm = EnumBase(); Crm.name, Crm.value = "Crm", 1
    Full = EnumBase(); Full.name, Full.value = "Full", 2
    Q1Ms = EnumBase(); Q1Ms.name, Q1Ms.value = "Q1Ms", 3
    Q3Ms = EnumBase(); Q3Ms.name, Q3Ms.value = "Q3Ms", 4
    Sim = EnumBase(); Sim.name, Sim.value = "Sim", 5
    Srm = EnumBase(); Srm.name, Srm.value = "Srm", 6
    Zoom = EnumBase(); Zoom.name, Zoom.value = "Zoom", 7

class CompensationVoltageType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    NoValue = EnumBase(); NoValue.name, NoValue.value = "NoValue", 1
    Ramp = EnumBase(); Ramp.name, Ramp.value = "Ramp", 2
    SIM = EnumBase(); SIM.name, SIM.value = "SIM", 3
    SingleValue = EnumBase(); SingleValue.name, SingleValue.value = "SingleValue", 4

class ScanDataType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    Centroid = EnumBase(); Centroid.name, Centroid.value = "Centroid", 1
    Profile = EnumBase(); Profile.name, Profile.value = "Profile", 2

class SectorScanType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    SectorBScan = EnumBase(); SectorBScan.name, SectorBScan.value = "SectorBScan", 1
    SectorEScan = EnumBase(); SectorEScan.name, SectorEScan.value = "SectorEScan", 2

class FieldFreeRegionType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    FieldFreeRegion1 = EnumBase(); FieldFreeRegion1.name, FieldFreeRegion1.value = "FieldFreeRegion1", 1
    FieldFreeRegion2 = EnumBase(); FieldFreeRegion2.name, FieldFreeRegion2.value = "FieldFreeRegion2", 2

class EnergyType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    Valid = EnumBase(); Valid.name, Valid.value = "Valid", 1

class IonizationModeType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    ElectroSpray = EnumBase(); ElectroSpray.name, ElectroSpray.value = "ElectroSpray", 1
    AtmosphericPressureChemicalIonization = EnumBase(); AtmosphericPressureChemicalIonization.name, AtmosphericPressureChemicalIonization.value = "AtmosphericPressureChemicalIonization", 2
    NanoSpray = EnumBase(); NanoSpray.name, NanoSpray.value = "NanoSpray", 3
    ChemicalIonization = EnumBase(); ChemicalIonization.name, ChemicalIonization.value = "ChemicalIonization", 4
    ElectronImpact = EnumBase(); ElectronImpact.name, ElectronImpact.value = "ElectronImpact", 5
    FastAtomBombardment = EnumBase(); FastAtomBombardment.name, FastAtomBombardment.value = "FastAtomBombardment", 6
    FieldDesorption = EnumBase(); FieldDesorption.name, FieldDesorption.value = "FieldDesorption", 7
    MatrixAssistedLaserDesorptionIonization = EnumBase(); MatrixAssistedLaserDesorptionIonization.name, MatrixAssistedLaserDesorptionIonization.value = "MatrixAssistedLaserDesorptionIonization", 8
    GlowDischarge = EnumBase(); GlowDischarge.name, GlowDischarge.value = "GlowDischarge", 9
    ThermoSpray = EnumBase(); ThermoSpray.name, ThermoSpray.value = "ThermoSpray", 10
    CardNanoSprayIonization = EnumBase(); CardNanoSprayIonization.name, CardNanoSprayIonization.value = "CardNanoSprayIonization", 11
    PaperSprayIonization = EnumBase(); PaperSprayIonization.name, PaperSprayIonization.value = "PaperSprayIonization", 12
    IonModeBeyondKnown = EnumBase(); IonModeBeyondKnown.name, IonModeBeyondKnown.value = "IonModeBeyondKnown", 13
    IonizationMode1 = EnumBase(); IonizationMode1.name, IonizationMode1.value = "IonizationMode1", 14
    IonizationMode2 = EnumBase(); IonizationMode2.name, IonizationMode2.value = "IonizationMode2", 15
    IonizationMode3 = EnumBase(); IonizationMode3.name, IonizationMode3.value = "IonizationMode3", 16
    IonizationMode4 = EnumBase(); IonizationMode4.name, IonizationMode4.value = "IonizationMode4", 17
    IonizationMode5 = EnumBase(); IonizationMode5.name, IonizationMode5.value = "IonizationMode5", 18
    IonizationMode6 = EnumBase(); IonizationMode6.name, IonizationMode6.value = "IonizationMode6", 19
    IonizationMode7 = EnumBase(); IonizationMode7.name, IonizationMode7.value = "IonizationMode7", 20
    IonizationMode8 = EnumBase(); IonizationMode8.name, IonizationMode8.value = "IonizationMode8", 21
    IonizationMode9 = EnumBase(); IonizationMode9.name, IonizationMode9.value = "IonizationMode9", 22

class ActivationType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    CollisionInducedDissociation = EnumBase(); CollisionInducedDissociation.name, CollisionInducedDissociation.value = "CollisionInducedDissociation", 1
    ElectronCaptureDissociation = EnumBase(); ElectronCaptureDissociation.name, ElectronCaptureDissociation.value = "ElectronCaptureDissociation", 2
    ElectronTransferDissociation = EnumBase(); ElectronTransferDissociation.name, ElectronTransferDissociation.value = "ElectronTransferDissociation", 3
    HigherEnergyCollisionalDissociation = EnumBase(); HigherEnergyCollisionalDissociation.name, HigherEnergyCollisionalDissociation.value = "HigherEnergyCollisionalDissociation", 4
    MultiPhotonDissociation = EnumBase(); MultiPhotonDissociation.name, MultiPhotonDissociation.value = "MultiPhotonDissociation", 5
    PQD = EnumBase(); PQD.name, PQD.value = "PQD", 6
    SAactivation = EnumBase(); SAactivation.name, SAactivation.value = "SAactivation", 7
    UltraVioletPhotoDissociation = EnumBase(); UltraVioletPhotoDissociation.name, UltraVioletPhotoDissociation.value = "UltraVioletPhotoDissociation", 8
    NegativeElectronTransferDissociation = EnumBase(); NegativeElectronTransferDissociation.name, NegativeElectronTransferDissociation.value = "NegativeElectronTransferDissociation", 9
    ProtonTransferReaction = EnumBase(); ProtonTransferReaction.name, ProtonTransferReaction.value = "ProtonTransferReaction", 10
    NegativeProtonTransferReaction = EnumBase(); NegativeProtonTransferReaction.name, NegativeProtonTransferReaction.value = "NegativeProtonTransferReaction", 11
    LastActivation = EnumBase(); LastActivation.name, LastActivation.value = "LastActivation", 12
    ModeA = EnumBase(); ModeA.name, ModeA.value = "ModeA", 13
    ModeB = EnumBase(); ModeB.name, ModeB.value = "ModeB", 14
    ModeC = EnumBase(); ModeC.name, ModeC.value = "ModeC", 15
    ModeD = EnumBase(); ModeD.name, ModeD.value = "ModeD", 16
    ModeE = EnumBase(); ModeE.name, ModeE.value = "ModeE", 17
    ModeF = EnumBase(); ModeF.name, ModeF.value = "ModeF", 18
    ModeG = EnumBase(); ModeG.name, ModeG.value = "ModeG", 19
    ModeH = EnumBase(); ModeH.name, ModeH.value = "ModeH", 20
    ModeI = EnumBase(); ModeI.name, ModeI.value = "ModeI", 21
    ModeJ = EnumBase(); ModeJ.name, ModeJ.value = "ModeJ", 22
    ModeK = EnumBase(); ModeK.name, ModeK.value = "ModeK", 23
    ModeL = EnumBase(); ModeL.name, ModeL.value = "ModeL", 24
    ModeM = EnumBase(); ModeM.name, ModeM.value = "ModeM", 25
    ModeN = EnumBase(); ModeN.name, ModeN.value = "ModeN", 26
    ModeO = EnumBase(); ModeO.name, ModeO.value = "ModeO", 27
    ModeP = EnumBase(); ModeP.name, ModeP.value = "ModeP", 28
    ModeQ = EnumBase(); ModeQ.name, ModeQ.value = "ModeQ", 29
    ModeR = EnumBase(); ModeR.name, ModeR.value = "ModeR", 30
    ModeS = EnumBase(); ModeS.name, ModeS.value = "ModeS", 31
    ModeT = EnumBase(); ModeT.name, ModeT.value = "ModeT", 32
    ModeU = EnumBase(); ModeU.name, ModeU.value = "ModeU", 33
    ModeV = EnumBase(); ModeV.name, ModeV.value = "ModeV", 34
    ModeW = EnumBase(); ModeW.name, ModeW.value = "ModeW", 35
    ModeX = EnumBase(); ModeX.name, ModeX.value = "ModeX", 36
    ModeY = EnumBase(); ModeY.name, ModeY.value = "ModeY", 37
    ModeZ = EnumBase(); ModeZ.name, ModeZ.value = "ModeZ", 38

class DetectorType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    Detector1 = EnumBase(); Detector1.name, Detector1.value = "Detector1", 1

class PolarityType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    Positive = EnumBase(); Positive.name, Positive.value = "Positive", 1
    Negative = EnumBase(); Negative.name, Negative.value = "Negative", 2

class SampleType(EnumBase):
    Unknown = EnumBase(); Unknown.name, Unknown.value = "Unknown", 0
    Blank = EnumBase(); Blank.name, Blank.value = "Blank", 1
    QC = EnumBase(); QC.name, QC.value = "QC", 2
    StdBracket = EnumBase(); StdBracket.name, StdBracket.value = "StdBracket", 3
    StdBracketStart = EnumBase(); StdBracketStart.name, StdBracketStart.value = "StdBracketStart", 4
    StdBracketEnd = EnumBase(); StdBracketEnd.name, StdBracketEnd.value = "StdBracketEnd", 5
    StdClear = EnumBase(); StdClear.name, StdClear.value = "StdClear", 6
    StdUpdate = EnumBase(); StdUpdate.name, StdUpdate.value = "StdUpdate", 7
    MatrixBlank = EnumBase(); MatrixBlank.name, MatrixBlank.value = "MatrixBlank", 8
    MatrixSpike = EnumBase(); MatrixSpike.name, MatrixSpike.value = "MatrixSpike", 9
    MatrixSpikeDuplicate = EnumBase(); MatrixSpikeDuplicate.name, MatrixSpikeDuplicate.value = "MatrixSpikeDuplicate", 10
    SolventBlank = EnumBase(); SolventBlank.name, SolventBlank.value = "SolventBlank", 11
    Program = EnumBase(); Program.name, Program.value = "Program", 12

class PeakOptions(EnumBase):
    none = EnumBase(); none.name, none.value = "none", 0
    Saturated = EnumBase(); Saturated.name, Saturated.value = "Saturated", 1
    Fragmented = EnumBase(); Fragmented.name, Fragmented.value = "Fragmented", 2
    Merged = EnumBase(); Merged.name, Merged.value = "Merged", 4
    Exception = EnumBase(); Exception.name, Exception.value = "Exception", 8
    Reference = EnumBase(); Reference.name, Reference.value = "Reference", 16
    Modified = EnumBase(); Modified.name, Modified.value = "Modified", 32
    LockPeak = EnumBase(); LockPeak.name, LockPeak.value = "LockPeak", 64

class DeviceType(object): pass
class MsOrderType(object): pass
class MassAnalyzerType(object): pass
class ToleranceUnits(EnumBase): pass
class TraceType(EnumBase): pass
class SectorScanType(EnumBase): pass
class SourceFragmentationValueType(EnumBase): pass
class TrayShape(EnumBase): pass
class FileType(EnumBase): pass

class RawFileClassification(EnumBase):
    StandardRaw = EnumBase(); StandardRaw.name, StandardRaw.value = "StandardRaw", 0
    MasterScanNumberRaw = EnumBase(); MasterScanNumberRaw.name, MasterScanNumberRaw.value = "MasterScanNumberRaw", 1
    Indeterminate = EnumBase(); Indeterminate.name, Indeterminate.value = "Indeterminate", 2

class SourceFragmentationInfoValidType(EnumBase):
    Any = EnumBase(); Any.name, Any.value = "Any", 0
    Energy = EnumBase(); Energy.name, Energy.value = "Energy", 1

class FilterAccurateMass(EnumBase):
    Off = EnumBase(); Off.name, Off.value = "Off", 0
    On = EnumBase(); On.name, On.value = "On", 1
    External = EnumBase(); External.name, External.value = "External", 2
    Internal = EnumBase(); Internal.name, Internal.value = "Internal", 3
    Any = EnumBase(); Any.name, Any.value = "Any", 4

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

class RunHeader(CommonCoreDataObject):
    """The run header."""
    def __init__(self, raw_file): self._raw_file = raw_file
    @property
    def first_spectrum(self) -> int: return self._raw_file.first_scan
    @property
    def last_spectrum(self) -> int: return self._raw_file.last_scan
    @property
    def start_time(self) -> float: return get_start_time()
    @property
    def end_time(self) -> float: return self._raw_file.total_time_min
    @property
    def high_mass(self) -> float: return 2000.0
    @property
    def low_mass(self) -> float: return 50.0
    @property
    def mass_resolution(self) -> float: return 0.5
    @property
    def expected_runtime(self) -> float: return self.end_time
    @property
    def max_integrated_intensity(self) -> float: return 1e9
    @property
    def max_intensity(self) -> float: return 1e8
    @property
    def tolerance_unit(self) -> int: return 0

class RunHeaderEx(CommonCoreDataObject):
    """Information about the file stream."""
    def __init__(self, raw_file): self._raw_file = raw_file
    @property
    def first_spectrum(self) -> int: return self._raw_file.first_scan
    @property
    def last_spectrum(self) -> int: return self._raw_file.last_scan
    @property
    def spectra_count(self) -> int: return self._raw_file.number_of_scans
    @property
    def start_time(self) -> float: return get_start_time()
    @property
    def end_time(self) -> float: return self._raw_file.total_time_min
    @property
    def high_mass(self) -> float: return 2000.0
    @property
    def low_mass(self) -> float: return 50.0
    @property
    def mass_resolution(self) -> float: return 0.5
    @property
    def in_acquisition(self) -> int: return 0
    @property
    def expected_run_time(self) -> float: return self.end_time
    @property
    def max_integrated_intensity(self) -> float: return 1e9
    @property
    def max_intensity(self) -> float: return 1e8
    @property
    def tolerance_unit(self) -> int: return 0
    @property
    def comment_1(self) -> str: return ""
    @property
    def comment_2(self) -> str: return ""
    @property
    def error_log_count(self) -> int: return 0
    @property
    def filter_mass_precision(self) -> int: return 4
    @property
    def status_log_count(self) -> int: return 0
    @property
    def trailer_extra_count(self) -> int: return self.spectra_count
    @property
    def trailer_scan_event_count(self) -> int: return self.spectra_count
    @property
    def tune_data_count(self) -> int: return 0

class business:
    BarcodeStatusType = object
    BracketType = object
    CachedScanProvider = object
    CentroidStream = CentroidStream
    ChromatogramSignal = ChromatogramSignal
    chromatogram_signal_cls = object
    ChromatogramTraceSettings = ChromatogramTraceSettings
    DataUnits = object
    GenericDataTypes = object
    HeaderItem = HeaderItem
    InstrumentData = InstrumentData
    InstrumentSelection = InstrumentSelection
    LabelPeak = object
    LogEntry = LogEntry
    MassOptions = MassOptions
    MassToFrequencyConverter = object
    NoiseAndBaseline = object
    Range = Range
    Reaction = Reaction
    RunHeader = RunHeader
    SampleInformation = SampleInformation
    SampleType = SampleType
    Scan = Scan
    ScanStatistics = ScanStatistics
    SegmentedScan = SegmentedScan
    SimpleScan = object
    SpectrumPacketType = object
    StatusLogValues = StatusLogValues
    ToleranceMode = object
    TraceType = TraceType
    TuneDataValues = TuneDataValues
    barcode_status_type = object
    bracket_type = object
    cached_scan_provider = object
    centroid_stream = object
    chromatogram_signal = object
    chromatogram_trace_settings = object
    data_units = object
    generic_data_types = object
    header_item = object
    instrument_data = InstrumentData
    instrument_selection = InstrumentSelection
    label_peak = object
    log_entry = LogEntry
    mass_options = MassOptions
    mass_to_frequency_converter = object
    noise_and_baseline = object
    range = Range
    reaction = Reaction
    run_header = RunHeader
    sample_information = SampleInformation
    sample_type = SampleType
    scan = Scan
    scan_statistics = ScanStatistics
    segmented_scan = SegmentedScan
    simple_scan = object
    spectrum_packet_type = object
    status_log_values = StatusLogValues
    tolerance_mode = object
    trace_type = TraceType
    tune_data_values = TuneDataValues

class filter_enums:
    MsOrderType = MsOrderType
    MassAnalyzerType = MassAnalyzerType
    ToleranceUnits = ToleranceUnits
    TraceType = TraceType
    ScanDataType = ScanDataType
    ScanModeType = ScanModeType
    SectorScanType = SectorScanType
    IonizationModeType = IonizationModeType
    ActivationType = ActivationType
    EnergyType = EnergyType
    EventAccurateMass = EventAccurateMass
    CompensationVoltageType = CompensationVoltageType
    FieldFreeRegionType = FieldFreeRegionType
    SourceFragmentationValueType = SourceFragmentationValueType
    TriState = TriState
    DetectorType = DetectorType
    PolarityType = PolarityType
    activation_type = ActivationType
    compensation_voltage_type = CompensationVoltageType
    detector_type = DetectorType
    energy_type = EnergyType
    event_accurate_mass = EventAccurateMass
    field_free_region_type = FieldFreeRegionType
    ionization_mode_type = IonizationModeType
    mass_analyzer_type = MassAnalyzerType
    ms_order_type = MsOrderType
    polarity_type = PolarityType
    scan_data_type = ScanDataType
    scan_mode_type = ScanModeType
    sector_scan_type = SectorScanType
    source_fragmentation_value_type = SourceFragmentationValueType
    tri_state = TriState

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
    FileType = FileType
    RawFileClassification = RawFileClassification
    ScanDependentDetails = ScanDependentDetails
    SequenceFileWriter = object
    SequenceInfo = SequenceInfo
    SourceFragmentationInfoValidType = SourceFragmentationInfoValidType
    ToleranceUnits = object
    TrayShape = object
    FilterAccurateMass = FilterAccurateMass
    PeakOptions = PeakOptions
    FtAverageOptions = object
    ErrorLogEntry = ErrorLogEntry
    business = business
    filter_enums = filter_enums
    device = None 
    file_header = None
    file_error = None
    scan_event = None
    auto_sampler_information = None
    common_core_data_object = None
    error_log_entry = None
    filter_enums = filter_enums

data.device = data
data.file_header = data
data.file_error = data
data.scan_event = data
data.auto_sampler_information = data
data.common_core_data_object = data
data.error_log_entry = data

class utils:
    Any = object
    Array = list
    DateTime = object
    Double = float
    List = list
    clr = object
    datetime = object
    datetime_net_to_py = lambda x: x
    datetime_py_to_net = lambda x: x
    generic = object
    is_number = lambda x: isinstance(x, (int, float))
    to_net_array = lambda x: x
    to_net_list = lambda x: x
    to_py_list = lambda x: x
    np = np

class net_wrapping:
    Environment = object
    Extensions = object
    NetWrapperBase = CommonCoreDataObject
    Python = object
    ThermoFisher = object
    clr = object
    dll_base_path = ""
    dll_path = ""
    dotnet_version = "8.0"
    net_wrapper_base = object
    os = os
    pythonnet = object
    thermo_fisher_data = object
    thermo_fisher_data_business = object
    thermo_fisher_data_filter_enums = object
    thermo_fisher_data_interfaces = object
    thermo_fisher_mass_precision_estimator = object
    thermo_fisher_raw_file_reader = object
    wrapped_net_array = object

net_wrapping.pythonnet = object
net_wrapping.net_wrapper_base = object
net_wrapping.wrapped_net_array = object
net_wrapping.Environment = object
net_wrapping.Extensions = object
net_wrapping.ThermoFisher = object

from . import exceptions
exceptions.raw_file_exception = exceptions
exceptions.core_exception = exceptions
exceptions.NoSelectedDeviceException = exceptions.RawFileException
exceptions.NoSelectedMsDeviceException = exceptions.RawFileException

class raw_file:
    RawFile = None 
    ChromatogramTraceSettings = ChromatogramTraceSettings
    Device = Device
    FtAverageOptions = FtAverageOptions
    List = list
    MassAnalyzerType = MassAnalyzerType
    MassOptions = MassOptions
    MsOrderType = MsOrderType
    Range = Range
    ToleranceUnits = ToleranceUnits
    TraceType = TraceType
    Tuple = tuple
    np = np

class raw_file_reader:
    RawFileAccess = None 
    RawFileReaderAdapter = None 
    ScanDependents = ScanDependents
    data_model = data
    raw_file_access = None 
    raw_file_reader_adapter = None 
    scan_dependents = None 

raw_file_reader.scan_dependents = raw_file_reader

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
        return ScanEvent()

    def get_scan_event_string_for_scan_number(self, scan_number: int):
        return get_scan_event_string(scan_number)

    def get_centroid_stream(self, scan_number: int, include_ref_peaks: bool = False):
        return CentroidStream()

    def get_segmented_scan_from_scan_number(self, scan_number: int, stats = None):
        return SegmentedScan()

    def get_scan_stats_for_scan_number(self, scan_number: int):
        return ScanStatistics()

    def get_chromatogram_data(self, settings, start_scan, end_scan, tolerance = None):
        return []

    def get_instrument_count_of_type(self, device_type):
        return get_instrument_count_of_type(device_type)

    def get_trailer_extra_header_information(self): return []
    def get_trailer_extra_information(self, scan_number): return None
    def get_trailer_extra_values(self, scan_number, formatted): return []
    def get_status_log_header_information(self): return []
    def get_status_log_values(self, index, formatted): return None
    def get_status_log_entries_count(self): return 0
    def get_status_log_for_retention_time(self, rt): return None
    def get_tune_data_count(self): return 0
    def get_tune_data(self, index): return None
    def get_filters(self): return []
    def get_auto_filters(self): return []
    def get_filter_for_scan_number(self, scan_number): return ""
    def get_scan_events(self, start, end): return []
    def get_scan_dependents(self, scan_number, precision): return ScanDependents()

    @property
    def has_ms_data(self) -> bool:
        return has_ms_data()

    def get_scan_type(self, scan_number: int):
        return ""

    def get_error_log_item(self, index: int):
        return None

    def get_tune_data_header_information(self, index: int):
        return []

    def get_tune_data_values(self, index: int):
        return None
    
    @property
    def instrument_methods_count(self) -> int:
        return 0

    @property
    def instrument_count(self) -> int:
        return get_instrument_count()

    @property
    def total_time_min(self) -> float:
        return get_end_time()

    def get_chromatogram(self, mass: float = 0.0, tolerance: float = 0.0, trace_type: int = 1, ms_filter: str = '') -> Tuple[np.ndarray, np.ndarray]:
        times, intensities = get_chromatogram(trace_type, 1000000)
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

raw_file.RawFile = RawFile
raw_file_reader.RawFileAccess = RawFile
raw_file_reader.RawFileReaderAdapter = RawFile
raw_file_reader.raw_file_access = raw_file_reader
raw_file_reader.raw_file_reader_adapter = raw_file_reader

if not _IS_SPHINX:
    from . import native_fisher_py_backend
    __all__ = ["RawFile", "Device", "MSOrder", "MassAnalyzer", "TraceType", "RawFileException", "RunHeader", "RunHeaderEx", "InstrumentData"]
else:
    __all__ = ["RawFile", "MSOrder", "MassAnalyzer", "TraceType", "RawFileException", "RunHeader", "RunHeaderEx", "InstrumentData"]
