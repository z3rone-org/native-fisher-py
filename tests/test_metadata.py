import pytest
from native_fisher_py.data.classes import TrayShape

def test_metadata_from_zoom_file(zoom_raw_file):
    si = zoom_raw_file.sample_information
    ai = si.autosampler_information
    
    assert si.injection_volume == pytest.approx(1.0)
    assert si.instrument_method_file.endswith(".meth")
    
    assert ai.tray_name == "R"
    assert ai.tray_index == -1
    assert ai.tray_shape == TrayShape.Circular
    assert ai.vial_index == -1
