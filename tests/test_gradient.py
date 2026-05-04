import pytest
from native_fisher_py.utils.gradient import parse_vanquish_neo_gradient

def verify_gradient(raw_file, expected):
    method_count = raw_file.get_instrument_methods_count()
    assert method_count > 0, "No instrument methods found"
    
    result = None
    for i in range(method_count):
        method_text = raw_file.get_instrument_method(i)
        result = parse_vanquish_neo_gradient(method_text)
        if result["gradient"]:
            break
            
    assert result is not None, "Could not extract result"
    gradient = result["gradient"]
    assert len(gradient) == len(expected)
    for i, (time, b) in enumerate(expected):
        assert gradient[i][0] == pytest.approx(time)
        assert gradient[i][1] == pytest.approx(b)

def test_gradient_zoom(zoom_file):
    expected = [(0.0, 6.0), (0.0, 6.0), (0.2, 10.0), (2.7, 28.0), (3.0, 55.0), (3.1, 99.0), (3.4, 99.0)]
    verify_gradient(zoom_file, expected)

def test_gradient_astral(pxd066718_file):
    # 549MB Evosep file has no gradient in the method text
    expected = []
    verify_gradient(pxd066718_file, expected)

def test_gradient_astral_zoom(pxd066944_file):
    # cycle_03.raw file has 8 points
    expected = [(0.0, 4.0), (0.0, 4.0), (0.1, 4.0), (1.6, 12.0), (9.7, 58.5), (11.2, 90.0), (11.5, 99.0), (11.8, 99.0)]
    verify_gradient(pxd066944_file, expected)
