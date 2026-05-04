import pytest
import os
from native_fisher_py.raw_file import RawFile
from native_fisher_py.utils.gradient import parse_vanquish_neo_gradient

def test_check_astral_gradient():
    path = "test_data/20250411_Ast0_500SPD_EVO685_JVO_EV1107_050ng_HEK-CPR_380-980_2Th_1P5ms_OFF_05_20250413081131.raw"
    if not os.path.exists(path):
        pytest.skip("File not found")
    
    raw = RawFile(path)
    try:
        method_count = raw.get_instrument_methods_count()
        print(f"\nMethod Count: {method_count}")
        for i in range(method_count):
            text = raw.get_instrument_method(i)
            print(f"Method {i} length: {len(text)}")
            # print(text[:1000]) # Don't print too much
            res = parse_vanquish_neo_gradient(text)
            if res["gradient"]:
                print(f"FOUND GRADIENT in Method {i}: {res['gradient']}")
            else:
                print(f"No gradient in Method {i}")
    finally:
        raw.close()
