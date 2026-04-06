import os
from ..data import CommonCoreDataObject

class NetWrapperBase(CommonCoreDataObject):
    def __init__(self, wrapped_object=None):
        self._wrapped_object = wrapped_object
    def _get_wrapped_object_(self):
        return self._wrapped_object

class ThermoFisher:
    class CommonCore:
        class Data:
            class Business:
                class ScanFilterHelper: pass
            class Extensions: pass

class pythonnet:
    def load(self): pass
    def unload(self): pass

class clr:
    def AddReference(self, name): pass

class Environment:
    CommandLine = ""
    CurrentDirectory = os.getcwd()
    OSVersion = os.uname().sysname if hasattr(os, 'uname') else "Windows"

class Extensions: pass
class wrapped_net_array: pass

dotnet_version = "8.0"
dll_base_path = ""
dll_path = ""
net_wrapper_base = NetWrapperBase
thermo_fisher_data = ThermoFisher.CommonCore.Data
thermo_fisher_data_business = ThermoFisher.CommonCore.Data.Business
thermo_fisher_data_filter_enums = object
thermo_fisher_data_interfaces = object
thermo_fisher_mass_precision_estimator = object
thermo_fisher_raw_file_reader = object
