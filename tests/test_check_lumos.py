import pytest
import os
from native_fisher_py.raw_file import RawFile
from native_fisher_py.utils.gradient import parse_vanquish_neo_gradient

def test_check_lumos_gradient():
    path = "test_data/B203016_11_Lumos_LS_CO_120_CCR4NOT_SDA_apo02_sec7_rep1.raw"
    if not os.path.exists(path):
        pytest.skip("File not found")
    
    raw = RawFile(path)
    try:
        method_count = raw.get_instrument_methods_count()
        print(f"\nMethod Count: {method_count}")
        for i in range(method_count):
            text = raw.get_instrument_method(i)
            print(f"Method {i} length: {len(text)}")
            res = parse_vanquish_neo_gradient(text)
            if res["gradient"]:
                print(f"FOUND GRADIENT in Method {i}: {res['gradient']}")
    finally:
        raw.close()
