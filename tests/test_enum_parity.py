import pytest
import native_fisher_py as nfp

import fisher_py.net_wrapping as net

def test_activation_type_parity():
    FilterEnums = net.ThermoFisher.CommonCore.Data.FilterEnums
    from System import Enum
    
    from native_fisher_py.data.classes import ActivationType
    for val in Enum.GetValues(FilterEnums.ActivationType):
        name = str(val)
        int_val = int(val)
        
        native_val = getattr(ActivationType, name, None)
        if native_val is not None:
            assert native_val.value == int_val, f"Mismatch in ActivationType.{name}: Thermo={int_val}, Native={native_val.value}"

def test_mass_analyzer_parity():
    FilterEnums = net.ThermoFisher.CommonCore.Data.FilterEnums
    from System import Enum
    
    from native_fisher_py.data.classes import MassAnalyzer
    for val in Enum.GetValues(FilterEnums.MassAnalyzerType):
        name = str(val)
        int_val = int(val)
        
        native_val = getattr(MassAnalyzer, name, None)
        if native_val is not None:
            assert native_val.value == int_val, f"Mismatch in MassAnalyzer.{name}: Thermo={int_val}, Native={native_val.value}"
