import pytest
from native_fisher_py.data.classes import TrayShape
import os
from native_fisher_py.raw_file import RawFile


def test_metadata_from_zoom_file(zoom_raw_file):
    si = zoom_raw_file.sample_information
    ai = si.autosampler_information

    assert si.injection_volume == pytest.approx(1.0)
    assert si.instrument_method_file.endswith(".meth")

    assert ai.tray_name == "R"
    assert ai.tray_index == -1
    assert ai.tray_shape == TrayShape.Circular
    assert ai.vial_index == -1


def test_metadata_from_angiotensin_file(angiotensin_raw_file):
    method_count = angiotensin_raw_file.get_instrument_methods_count()
    assert method_count == 1

    method = angiotensin_raw_file.get_instrument_method(0)
    assert len(method) == 4374


def test_metadata_from_mtbls773_uv():
    path = os.path.join(os.path.dirname(__file__), "..", "test_data", "MTBLS773_UV.raw")
    if not os.path.exists(path):
        pytest.fail(f"Test file not found: {path}")
    raw = RawFile(path)
    try:
        si = raw.sample_information
        ai = si.autosampler_information
        assert ai.tray_index == 0
        assert ai.vial_index == 42
        assert ai.tray_name == '1.8 ml Vial, 5 trays 40 vials each'
        assert si.vial == ''
    finally:
        raw.close()
