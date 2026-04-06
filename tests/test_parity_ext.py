import unittest
import fisher_py
import native_fisher_py
import inspect
import os
from typing import Set, Any

class TestAPIParity(unittest.TestCase):
    def compare_obj(self, name: str, orig_obj: Any, native_obj: Any, seen: Set[int] = None):
        if seen is None: seen = set()
        if id(orig_obj) in seen: return
        seen.add(id(orig_obj))

        print(f"\n--- Comparing {name} ---")
        orig_members = set(n for n, _ in inspect.getmembers(orig_obj) if not n.startswith("_") or n == "_raw_file_access")
        native_members = set(n for n, _ in inspect.getmembers(native_obj) if not n.startswith("_") or n == "_raw_file_access")
        
        missing_in_native = orig_members - native_members
        if missing_in_native:
            print(f"FAILED: {name} is missing: {sorted(list(missing_in_native))}")
        else:
            print(f"OK: {name} API parity matches.")

        # Recurse if it's a class or module
        if inspect.isclass(orig_obj) or inspect.ismodule(orig_obj):
            for member_name in orig_members:
                if member_name in native_members:
                    try:
                        orig_m = getattr(orig_obj, member_name)
                        native_m = getattr(native_obj, member_name)
                        if inspect.isclass(orig_m) or inspect.ismodule(orig_m):
                            self.compare_obj(f"{name}.{member_name}", orig_m, native_m, seen)
                    except Exception:
                        pass

    def test_global_parity(self):
        # We also want to check special classes that might be at different locations
        self.compare_obj("fisher_py", fisher_py, native_fisher_py)
        
        # Explicitly check RawFileAccess against our RawFile if it's not reached
        if hasattr(fisher_py, "raw_file_reader") and hasattr(fisher_py.raw_file_reader, "RawFileAccess"):
             self.compare_obj("RawFileAccess", fisher_py.raw_file_reader.RawFileAccess, native_fisher_py.RawFile)

if __name__ == "__main__":
    unittest.main()
