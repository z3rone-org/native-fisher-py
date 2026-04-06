import sys
import os
import pathlib

class NetWrapperBase(object):
    Any = None
    CoreException = Exception
    NetWrapperBase = object
    annotations = None

class Extensions(object):
    def Equals(self, *args): return True
    def Finalize(self): pass
    def GetHashCode(self): return 0
    def GetType(self): return None
    def MemberwiseClone(self): return self
    @staticmethod
    def ReferenceEquals(*args): return True
    def ToString(self): return "Extensions"

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
    def Finalize(self): pass
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
    def MemberwiseClone(self): return self
    @staticmethod
    def Overloads(*args, **kwargs): return None
    @staticmethod
    def ReferenceEquals(*args, **kwargs): return True
    @staticmethod
    def SetEnvironmentVariable(name, val): pass
    def ToString(self): return "Environment"
    
    class SpecialFolder:
        pass
    class SpecialFolderOption:
        pass
    
    @property
    def CommandLine(self): return ""
    @property
    def CurrentDirectory(self): return "."
    @property
    def OSVersion(self): return "Unix"
    
    def get_CommandLine(self): return ""
    def get_CurrentDirectory(self): return "."
    def get_CurrentManagedThreadId(self): return 1
    def get_ExitCode(self): return 0
    def get_HasShutdownStarted(self): return False
    def get_Is64BitOperatingSystem(self): return True
    def get_Is64BitProcess(self): return True
    def get_MachineName(self): return "Local"
    def get_NewLine(self): return "\n"
    def get_OSVersion(self): return "Unix"
    def get_ProcessorCount(self): return 1
    def get_StackTrace(self): return ""
    def get_SystemDirectory(self): return ""
    def get_SystemPageSize(self): return 4096
    def get_TickCount(self): return 0
    def get_UserDomainName(self): return ""
    def get_UserInteractive(self): return True
    def get_UserName(self): return "User"
    def get_Version(self): return "8.0"
    def get_WorkingSet(self): return 0
    
    def set_CurrentDirectory(self, v): pass
    def set_ExitCode(self, v): pass

# Helper classes to avoid NameErrors
class Assembly_cls(object):
    @staticmethod
    def get_function(*args): return None
class Runtime_cls(object):
    @staticmethod
    def get_assembly(*args): return None
    info = None
    @staticmethod
    def shutdown(): pass
class Mono_cls(object):
    @staticmethod
    def get_assembly(*args): return None
    info = None
    @staticmethod
    def shutdown(): pass
class TemporaryDirectory_cls(object):
    @staticmethod
    def cleanup(): pass
class DotnetCoreRuntimeSpec_cls(object):
    floor_version = "8.0"
    runtime_config = ""
    tfm = ""
    version_info = ""
    @staticmethod
    def write_config(): pass

class clr_loader_stub(object):
    Runtime = Runtime_cls
    Assembly = Assembly_cls
    TemporaryDirectory = TemporaryDirectory_cls
    class RuntimeInfo(object): 
        pass
    DotnetCoreRuntimeSpec = DotnetCoreRuntimeSpec_cls
    class mono(object):
        Any = None
        Dict = dict
        class MethodDesc(object):
            @staticmethod
            def search(*args): return None
        Mono_cls = object
        MonoMethod = object
        Optional = None
        Path = pathlib.Path
        Runtime = Runtime_cls
        Mono = Mono_cls
        RuntimeInfo = object
        Sequence = list
        StrOrPath = str
        class atexit(object):
            @staticmethod
            def register(*args): pass
            @staticmethod
            def unregister(*args): pass
        ffi = object
        @staticmethod
        def initialize(): pass
        @staticmethod
        def load_mono(): pass
        @staticmethod
        def optional_path_as_string(p): return ""
        @staticmethod
        def path_as_string(p): return ""
        class re(object):
            A=0; ASCII=0; DEBUG=0; DOTALL=0; I=0; IGNORECASE=0; L=0; LOCALE=0; M=0; MULTILINE=0; Match=object; NOFLAG=0; Pattern=object; PatternError=object; RegexFlag=0; S=0; Scanner=object; U=0; UNICODE=0; VERBOSE=0; X=0
            @staticmethod
            def compile(x): return x
            copyreg=None; enum=None; error=Exception
            @staticmethod
            def escape(x): return x
            @staticmethod
            def findall(x): return x
            @staticmethod
            def finditer(x): return x
            @staticmethod
            def fullmatch(x): return x
            functools=None
            @staticmethod
            def match(x): return x
            @staticmethod
            def purge(): pass
            @staticmethod
            def search(x): return x
            @staticmethod
            def split(x): return x
            @staticmethod
            def sub(x,y,z): return x
            @staticmethod
            def subn(x,y,z): return x

    class util(object):
        ClrError = Exception
        Optional = None
        Path = pathlib.Path
        StrOrPath = str
        @staticmethod
        def check_result(r): pass
        class clr_error(object):
            ClrError = Exception; Optional = None
        coreclr_errors_dict = {}
        class hostfxr_errors_cls(object):
            ClrError = Exception; HOSTFXR_ERRORS = {}; Optional = None; 
            @staticmethod
            def get_hostfxr_error(e): return ""
        hostfxr_errors = hostfxr_errors_cls
        @staticmethod
        def find_root(): return ""
        class find_inner(object):
            DotnetCoreRuntimeSpec = object; Iterator = iter; Optional = None; Path = pathlib.Path; 
            @staticmethod
            def find_dotnet_cli(): return ""
            @staticmethod
            def find_dotnet_root(): return ""
            @staticmethod
            def find_libmono(): return ""
            @staticmethod
            def find_runtimes(): return []
            @staticmethod
            def find_runtimes_in_root(): return []
            @staticmethod
            def find_runtimes_using_cli(): return []
            os = os; platform = None; shutil = None; sys = sys
        find = find_inner
        @staticmethod
        def find_dotnet_root(): return ""
        @staticmethod
        def get_coreclr_error(e): return ""
        @staticmethod
        def get_hostfxr_error(e): return ""
        class coreclr_errors_inner(object):
            ClrError = Exception; Comment = ""; Dict = dict; Message = ""; Optional = None; SymbolicName = ""; 
            @staticmethod
            def get_coreclr_error(e): return ""
        coreclr_errors = coreclr_errors_inner
        @staticmethod
        def optional_path_as_string(p): return ""
        @staticmethod
        def path_as_string(p): return ""
        class runtime_spec_cls(object):
            Any = None; Dict = dict; DotnetCoreRuntimeSpec = object; Path = pathlib.Path; TextIO = object; Tuple = tuple; json = None;
            @staticmethod
            def dataclass(x): return x
        runtime_spec = runtime_spec_cls
    class ffi_sub(object):
        Optional = None
        Path = pathlib.Path
        Tuple = tuple
        @staticmethod
        def cdef(s): pass
        cffi_obj = object
        ffi_obj = object
        class hostfxr_cls(object):
            @staticmethod
            def cdef(s): pass
            sys = sys
        hostfxr = hostfxr_cls
        @staticmethod
        def load_hostfxr(): pass
        @staticmethod
        def load_mono(): pass
        @staticmethod
        def load_netfx(): pass
        class mono_cls2(object):
            @staticmethod
            def cdef(s): pass
        mono = mono_cls2
        class netfx_cls(object):
            @staticmethod
            def cdef(s): pass
        netfx = netfx_cls
        sys = sys
        class cffi_inner(object):
            CDefError = Exception; FFI = object; FFIError = Exception; PkgConfigError = Exception; VerificationError = Exception; VerificationMissing = Exception; api = object; commontypes = object; cparser = object; error = Exception; lock = object; model = object
        cffi = cffi_inner
    ffi = ffi_sub

    class types(object):
        ABCMeta = type
        Any = None
        Assembly = Assembly_cls
        Callable = object
        ClrFunction = object
        Dict = dict
        Optional = None
        PathLike = object
        Runtime = Runtime_cls
        RuntimeInfo = object
        StrOrPath = str
        Union = object
        @staticmethod
        def abstractmethod(x): return x
        @staticmethod
        def dataclass(x): return x
        @staticmethod
        def field(x): return x

    Dict = dict
    Optional = None
    Sequence = list
    StrOrPath = str
    @staticmethod
    def find_dotnet_root(*args): return None
    @staticmethod
    def find_libmono(*args): return None
    @staticmethod
    def find_runtimes(*args): return []
    @staticmethod
    def get_coreclr(*args): return None
    @staticmethod
    def get_mono(*args): return None
    @staticmethod
    def get_netfx(*args): return None
    util = util

class pythonnet(object):
    Any = None
    Dict = dict
    Optional = None
    Path = pathlib.Path
    Union = None
    clr_loader = clr_loader_stub
    sys = sys
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

class clr_inner(object):
    @staticmethod
    def FindAssembly(name): return None
    @staticmethod
    def GetClrType(t): return None
    @staticmethod
    def ListAssemblies(verbose): return []
    class clrmethod_stub(object): 
        pass
    @staticmethod
    def clrmethod(*args, **kwargs): return clr_inner.clrmethod_stub()
    class clrproperty_stub(object):
        @staticmethod
        def getter(): return None
        @staticmethod
        def setter(v): pass
    @staticmethod
    def clrproperty(*args, **kwargs): return clr_inner.clrproperty_stub()
    @staticmethod
    def getPreload(): return False
    @staticmethod
    def setPreload(p): pass
    @staticmethod
    def AddReference(p): pass
    class loader_stub(object):
        DotNetFinder = object
        class DotNetLoader_cls(object):
            @staticmethod
            def create_module(*args): return None
            @staticmethod
            def exec_module(*args): pass
            @staticmethod
            def load_module(*args): return None
        DotNetLoader = DotNetLoader_cls
        class DotNetFinder_cls(object):
            @staticmethod
            def find_spec(*args): return None
            @staticmethod
            def invalidate_caches(): pass
        DotNetFinder = DotNetFinder_cls
        class importlib_cls(object):
            abc = object
            @staticmethod
            def import_module(x): return None
            @staticmethod
            def invalidate_caches(): pass
            machinery = object; metadata = object
            @staticmethod
            def reload(x): return x
            resources = object; sys = sys; util = object
        importlib = importlib_cls
        sys = sys
    loader = loader_stub
    Python = None
    System = None
    ThermoFisher = None

class ThermoFisher(object):
    class CommonCore(object):
        class MassPrecisionEstimator(object): pass
        class RawFileReader(object): pass
        class Data(object): pass

class Python(object): pass

this = sys.modules[__name__]
this.Extensions = Extensions
this.Environment = Environment
this.pythonnet = pythonnet
this.clr = clr_inner
this.ThermoFisher = ThermoFisher
this.Python = Python
this.dotnet_version = "8.0"
this.dll_base_path = ""
this.dll_path = ""
this.net_wrapper_base = NetWrapperBase
this.os = os
thermo_fisher_data = None
thermo_fisher_data_business = None
thermo_fisher_data_filter_enums = None
thermo_fisher_data_interfaces = object
thermo_fisher_mass_precision_estimator = None
thermo_fisher_raw_file_reader = None

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

class TypeVar_stub(object):
    has_default = False

class wrapped_net_array(object):
    T = object
    TypeVar = TypeVar_stub
    Union = object
    Generic = object
    System = object
    generic = object
    clr = clr_inner
    WrappedNetArray = WrappedNetArray
this.wrapped_net_array = wrapped_net_array
