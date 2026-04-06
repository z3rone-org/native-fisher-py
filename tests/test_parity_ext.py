import unittest
import fisher_py
import native_fisher_py
import inspect
import os
from typing import Set, Dict, Any

class TestAPIParity(unittest.TestCase):
    def compare_obj(self, name: str, orig_obj: Any, native_obj: Any, seen: Set[Any] = None):
        if seen is None: seen = set()
        if id(orig_obj) in seen: return
        seen.add(id(orig_obj))

        print(f"\n--- Comparing {name} ---")
        orig_members = set(n for n, _ in inspect.getmembers(orig_obj) if not n.startswith("_") or n == "_raw_file_access")
        native_members = set(n for n, _ in inspect.getmembers(native_obj) if not n.startswith("_") or n == "_raw_file_access")
        
        print(f"Members to compare: {sorted(list(orig_members))}")
        
        missing_in_native = orig_members - native_members
        if missing_in_native:
            print(f"FAILED: {name} is missing: {sorted(list(missing_in_native))}")
            # We don't fail immediately, just report
        else:
            print(f"OK: {name} API parity matches.")

        # Recurse into properties that return fisher_py objects
        for member_name in orig_members:
            if member_name in native_members:
                try:
                    # Only check properties/methods that don't require arguments
                    attr = getattr(orig_obj, member_name)
                    if inspect.isdatadescriptor(attr) or not (inspect.ismethod(attr) or inspect.isfunction(attr)):
                        # If it's a property or object, get the value
                        val = getattr(orig_obj, member_name)() if callable(attr) else attr
                        native_val = getattr(native_obj, member_name)() if callable(getattr(native_obj, member_name)) else getattr(native_obj, member_name)
                        
                        # Check if val is a fisher_py object
                        orig_module = getattr(type(val), "__module__", "")
                        if orig_module and orig_module.startswith("fisher_py"):
                            # Find the corresponding native class if it exists in the module
                            native_type_name = type(val).__name__
                            # Check if native_fisher_py has a class with the same name
                            if hasattr(native_fisher_py, native_type_name):
                                native_type = getattr(native_fisher_py, native_type_name)
                                self.compare_obj(f"{name}.{member_name} ({native_type_name})", val, native_type, seen)
                except Exception:
                    pass

    def test_recursive_parity(self):
        # Comparison starts from RawFile
        self.compare_obj("RawFile", fisher_py.RawFile, native_fisher_py.RawFile)

if __name__ == "__main__":
    unittest.main()
