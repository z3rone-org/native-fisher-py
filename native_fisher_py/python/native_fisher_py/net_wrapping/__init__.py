class NetWrapperBase(object): pass

class Extensions(object):
    @staticmethod
    def AverageScans(*args, **kwargs): return None
    @staticmethod
    def SubtractScans(*args, **kwargs): return None
    @staticmethod
    def AverageAndSubtractScans(*args, **kwargs): return None
    @staticmethod
    def AverageAndSubtractScansForCompound(*args, **kwargs): return None
    @staticmethod
    def AverageCompoundScansInScanRange(*args, **kwargs): return None
    @staticmethod
    def AverageCompoundScansInTimeRange(*args, **kwargs): return None
    @staticmethod
    def AverageScansInScanRange(*args, **kwargs): return None
    @staticmethod
    def AverageScansInTimeRange(*args, **kwargs): return None
    @staticmethod
    def BinarySearch(*args, **kwargs): return -1
    @staticmethod
    def BuildFilterHelper(*args, **kwargs): return ""
    @staticmethod
    def Contains(*args, **kwargs): return False
    @staticmethod
    def DefaultMassOptions(*args, **kwargs): return None
    @staticmethod
    def FastBinarySearch(*args, **kwargs): return -1
    @staticmethod
    def FormatActivationType(*args, **kwargs): return ""
    @staticmethod
    def FormatIonizationMode(*args, **kwargs): return ""
    @staticmethod
    def FormatMassAnalyzer(*args, **kwargs): return ""
    @staticmethod
    def GetCompoundNamesForTimeRange(*args, **kwargs): return []
    @staticmethod
    def GetCompoundScanEnumerator(*args, **kwargs): return None
    @staticmethod
    def GetCompoundScanEnumeratorOverTime(*args, **kwargs): return None
    @staticmethod
    def GetCompoundScanListByTimeRange(*args, **kwargs): return []
    @staticmethod
    def GetCompoundScansListByScanRange(*args, **kwargs): return []
    @staticmethod
    def GetFilteredScanEnumerator(*args, **kwargs): return None
    @staticmethod
    def GetFilteredScanEnumeratorOverTime(*args, **kwargs): return None
    @staticmethod
    def GetFilteredScansListByScanRange(*args, **kwargs): return []
    @staticmethod
    def GetFilteredScansListByTimeRange(*args, **kwargs): return []
    @staticmethod
    def GetFilteredScansListWithinTimeRange(*args, **kwargs): return []
    @staticmethod
    def GetFiltersForTimeRange(*args, **kwargs): return []
    @staticmethod
    def GetScans(*args, **kwargs): return []
    @staticmethod
    def GetTrailerExtraDataForScanWithValidation(*args, **kwargs): return None
    @property
    def HasMsData(self): return True
    @property
    def HasVariableRecords(self): return False
    @property
    def HasVariableTrailers(self): return False
    @staticmethod
    def IntensitySum(*args, **kwargs): return 0.0
    @staticmethod
    def IsNullOrEmpty(*args, **kwargs): return True
    @staticmethod
    def LargestIntensity(*args, **kwargs): return 0.0
    @staticmethod
    def MassAndIntensityAtLargestIntensity(*args, **kwargs): return (0.0, 0.0)
    @staticmethod
    def MassAtLargestIntensity(*args, **kwargs): return 0.0
    @staticmethod
    def Overloads(*args, **kwargs): return None
    @staticmethod
    def ScanRangeFromTimeRange(*args, **kwargs): return (0, 0)
    @staticmethod
    def ScanRangeWithinTimeRange(*args, **kwargs): return (0, 0)
    @staticmethod
    def SelectMsData(*args, **kwargs): return None
    @staticmethod
    def TestScan(*args, **kwargs): return True

class Environment(object):
    CurrentManagedThreadId = 1
    ExitCode = 0
    HasShutdownStarted = False
    Is64BitOperatingSystem = True
    Is64BitProcess = True
    MachineName = "Local"
    NewLine = "\n"
    ProcessorCount = 1
    StackTrace = ""
    SystemDirectory = ""
    SystemPageSize = 4096
    TickCount = 0
    UserDomainName = ""
    UserInteractive = True
    UserName = "User"
    Version = "8.0"
    WorkingSet = 0
    @staticmethod
    def Equals(*args, **kwargs): return True
    @staticmethod
    def Exit(code): pass
    @staticmethod
    def ExpandEnvironmentVariables(s): return s
    @staticmethod
    def FailFast(*args, **kwargs): pass
    @staticmethod
    def GetCommandLineArgs(): return []
    @staticmethod
    def GetEnvironmentVariable(name): return None
    @staticmethod
    def GetEnvironmentVariables(): return {}
    @staticmethod
    def GetFolderPath(folder): return ""
    @staticmethod
    def GetHashCode(): return 0
    @staticmethod
    def GetLogicalDrives(): return []
    @staticmethod
    def GetType(): return None
    @staticmethod
    def MemberwiseClone(): return None
    @staticmethod
    def ReferenceEquals(*args, **kwargs): return True
    @staticmethod
    def SetEnvironmentVariable(name, val): pass
    class SpecialFolder: pass
    class SpecialFolderOption: pass
    @property
    def CommandLine(self): return ""
    @property
    def CurrentDirectory(self): return "."
    @property
    def OSVersion(self): return "Unix"

class pythonnet(object):
    @staticmethod
    def set_runtime(*args, **kwargs): pass
    @staticmethod
    def set_runtime_from_env(*args, **kwargs): pass
    @staticmethod
    def get_runtime_info(): return None
    @staticmethod
    def load(*args, **kwargs): pass
    @staticmethod
    def unload(*args, **kwargs): pass

class clr(object):
    @staticmethod
    def FindAssembly(name): return None
    @staticmethod
    def GetClrType(t): return None
    @staticmethod
    def ListAssemblies(verbose): return []
    @staticmethod
    def clrmethod(*args, **kwargs): return None
    @staticmethod
    def clrproperty(*args, **kwargs): return None
    @staticmethod
    def getPreload(): return False
    @staticmethod
    def setPreload(p): pass
    @staticmethod
    def AddReference(p): pass
    loader = None
    Python = None
    System = None
    ThermoFisher = None

class ThermoFisher(object):
    class CommonCore(object):
        class MassPrecisionEstimator(object): pass
        class RawFileReader(object): pass
        class Data(object): pass

class Python(object): pass

import sys
import os
this = sys.modules[__name__]
this.Extensions = Extensions
this.Environment = Environment
this.pythonnet = pythonnet
this.clr = clr
this.ThermoFisher = ThermoFisher
this.Python = Python
this.dotnet_version = "8.0"
this.dll_base_path = ""
this.dll_path = ""
this.net_wrapper_base = NetWrapperBase
this.os = os
this.thermo_fisher_data = None
this.thermo_fisher_data_business = None
this.thermo_fisher_data_filter_enums = None
this.thermo_fisher_data_interfaces = object
this.thermo_fisher_mass_precision_estimator = None
this.thermo_fisher_raw_file_reader = None

class WrappedNetArray(object):
    @staticmethod
    def append(*args, **kwargs): pass
    @staticmethod
    def clear(*args, **kwargs): pass
    @staticmethod
    def copy(*args, **kwargs): return []
    @staticmethod
    def count(*args, **kwargs): return 0
    @staticmethod
    def extend(*args, **kwargs): pass
    @staticmethod
    def index(*args, **kwargs): return -1
    @staticmethod
    def insert(*args, **kwargs): pass
    @staticmethod
    def pop(*args, **kwargs): return None
    @staticmethod
    def remove(*args, **kwargs): pass
    @staticmethod
    def reverse(*args, **kwargs): pass
    @staticmethod
    def sort(*args, **kwargs): pass

class wrapped_net_array(object):
    T = object
    TypeVar = object
    Union = object
    Generic = object
    System = object
    generic = object
    clr = object
    WrappedNetArray = WrappedNetArray
this.wrapped_net_array = wrapped_net_array
