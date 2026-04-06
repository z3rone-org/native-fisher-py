import os
import sys
import platform

# Find and initialize the native library
def _init_native_backend():
    # Library file name based on OS
    ext = "dll" if platform.system() == "Windows" else "dylib" if platform.system() == "Darwin" else "so"
    lib_name = f"ThermoNativeReader.{ext}"
    base_path = os.path.dirname(__file__)

    # 1. Check environment variable override (highest priority)
    env_path = os.environ.get("THERMO_NATIVE_LIB")
    if env_path and os.path.exists(env_path):
        from .native_fisher_py_backend import set_dylib_path
        set_dylib_path(env_path)
        return

    # 2. Check for library next to this file (standard package layout)
    pkg_lib_path = os.path.join(base_path, lib_name)
    if os.path.exists(pkg_lib_path):
        from .native_fisher_py_backend import set_dylib_path
        set_dylib_path(pkg_lib_path)
        os.environ["THERMO_NATIVE_LIB"] = pkg_lib_path
        return

    # 3. Development fallback (local workspace)
    rid = "linux-x64" if platform.system() == "Linux" else \
          "osx-arm64" if platform.machine() == "arm64" else "osx-x64" if platform.system() == "Darwin" else "win-x64"
    
    dev_path = os.path.abspath(os.path.join(base_path, "..", "..", "..", "native", "ThermoNativeReader", "bin", "Release", "net8.0", rid, "publish", lib_name))
    if os.path.exists(dev_path):
        from .native_fisher_py_backend import set_dylib_path
        set_dylib_path(dev_path)
        os.environ["THERMO_NATIVE_LIB"] = dev_path

_init_native_backend()

from .data import (
    CommonCoreDataObject, Device, MSOrder, MassAnalyzer, TraceType, 
    InstrumentData, SampleInformation, FileHeader, FileError, ScanEvent, 
    ScanEvents, ScanFilter, RunHeader, RunHeaderEx, ScanStatistics, 
    SegmentedScan, CentroidStream, ScanDependents, ErrorLogEntry, 
    LogEntry, HeaderItem, StatusLogValues, TuneDataValues, Reaction, Scan,
    ChromatogramSignal, MassOptions, Range,
    FtAverageOptions, ChromatogramTraceSettings
)
from .exceptions import (
    RawFileException, CoreException, NoSelectedDeviceException, NoSelectedMsDeviceException
)
from .raw_file import RawFile
from . import data as data_mod
from . import utils as utils_mod
from . import net_wrapping as net_wrapping_mod
from . import raw_file_reader as raw_file_reader_mod

# Aliases for parity
data = data_mod.data
utils = utils_mod
net_wrapping = net_wrapping_mod
raw_file_reader = raw_file_reader_mod
raw_file = raw_file_reader_mod

# Initialize the reader submodules
raw_file_reader_mod._init_reader_(RawFile)
exceptions = sys.modules[f"{__name__}.exceptions"]
exceptions.raw_file_exception = exceptions
exceptions.core_exception = exceptions

current_module = sys.modules[__name__]
raw_file_reader_mod.raw_file_access = raw_file_reader_mod
raw_file_reader_mod.raw_file_reader_adapter = raw_file_reader_mod
raw_file_reader_mod.scan_dependents = raw_file_reader_mod

__all__ = ["RawFile", "RawFileException", "InstrumentData", "RunHeader", "RunHeaderEx", "SampleInformation"]
