import pytest
from native_fisher_py.utils.gradient import parse_vanquish_neo_gradient

def test_extract_gradient_from_zoom_file(zoom_raw_file):
    # Get the number of methods
    method_count = zoom_raw_file.get_instrument_methods_count()
    assert method_count > 0, "No instrument methods found"
    
    result = None
    for i in range(method_count):
        method_text = zoom_raw_file.get_instrument_method(i)
        result = parse_vanquish_neo_gradient(method_text)
        if result["gradient"]:
            break
            
    assert result is not None, "Could not extract result from any instrument method"
    gradient = result["gradient"]
    solvents = result["solvents"]
    
    assert len(gradient) > 0, "Could not extract gradient"
    assert solvents["A"] == "H2O"
    assert solvents["B"] == "ACN80"
    
    # Expected points for 300SPD method
    expected_gradient = [
        (0.0, 6.0),
        (0.0, 6.0),
        (0.2, 10.0),
        (2.7, 28.0),
        (3.0, 55.0),
        (3.1, 99.0),
        (3.4, 99.0)
    ]
    
    assert len(gradient) == len(expected_gradient)
    for i, (time, b) in enumerate(expected_gradient):
        assert gradient[i][0] == pytest.approx(time)
        assert gradient[i][1] == pytest.approx(b)
