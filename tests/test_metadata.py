import pytest
from native_fisher_py.data.classes import TrayShape

def test_metadata_zoom(zoom_file):
    si = zoom_file.sample_information
    ai = si.autosampler_information
    assert si.injection_volume == pytest.approx(1.0)
    assert si.instrument_method_file.endswith(".meth")
    assert ai.tray_name == "R"
    assert ai.tray_index == -1

def test_metadata_astral(pxd066718_file):
    si = pxd066718_file.sample_information
    ai = si.autosampler_information
    # 549MB Evosep file has 0.0 injection volume and no tray info
    assert si.injection_volume == pytest.approx(0.0)
    assert si.instrument_method_file.endswith("OFF.meth")
    assert ai.tray_name == ""

def test_metadata_astral_zoom(pxd066944_file):
    si = pxd066944_file.sample_information
    ai = si.autosampler_information
    # cycle_03.raw file has 0.1 injection volume and Tray G
    assert si.injection_volume == pytest.approx(0.1)
    assert si.instrument_method_file.endswith("Preacc_top250c-V3-CYCLE06.meth")
    assert ai.tray_name == "G"
