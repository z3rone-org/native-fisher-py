import unittest
import fisher_py
import native_fisher_py
import inspect
import os

class TestAPIParity(unittest.TestCase):
    def test_raw_file_parity(self):
        print("\n--- Comparing RawFile ---")
        original_members = set(n for n, _ in inspect.getmembers(fisher_py.RawFile) if not n.startswith("__"))
        native_members = set(n for n, _ in inspect.getmembers(native_fisher_py.RawFile) if not n.startswith("__"))
        
        missing_in_native = original_members - native_members
        extra_in_native = native_members - original_members
        
        if missing_in_native:
            print(f"Missing in Native: {sorted(list(missing_in_native))}")
        if extra_in_native:
            print(f"Extra in Native: {sorted(list(extra_in_native))}")
            
    def test_instrument_data_parity(self):
        print("\n--- Comparing InstrumentData ---")
        # Need an instance or class members
        original_members = set(n for n, _ in inspect.getmembers(fisher_py.data.business.instrument_data.InstrumentData) if not n.startswith("__"))
        native_members = set(n for n, _ in inspect.getmembers(native_fisher_py.InstrumentData) if not n.startswith("__"))
        
        missing_in_native = original_members - native_members
        if missing_in_native:
            print(f"Missing in Native: {sorted(list(missing_in_native))}")

    def test_run_header_parity(self):
        print("\n--- Comparing RunHeader ---")
        original_members = set(n for n, _ in inspect.getmembers(fisher_py.data.business.RunHeader) if not n.startswith("__"))
        native_members = set(n for n, _ in inspect.getmembers(native_fisher_py.RunHeader) if not n.startswith("__"))
        
        missing_in_native = original_members - native_members
        if missing_in_native:
            print(f"Missing in Native RunHeader: {sorted(list(missing_in_native))}")

    def test_run_header_ex_parity(self):
        print("\n--- Comparing RunHeaderEx ---")
        original_members = set(n for n, _ in inspect.getmembers(fisher_py.raw_file_reader.data_model.WrappedRunHeader) if not n.startswith("__"))
        native_members = set(n for n, _ in inspect.getmembers(native_fisher_py.RunHeaderEx) if not n.startswith("__"))
        
        missing_in_native = original_members - native_members
        if missing_in_native:
            print(f"Missing in Native RunHeaderEx: {sorted(list(missing_in_native))}")

if __name__ == "__main__":
    unittest.main()
