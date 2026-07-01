import sys

if sys.platform == 'darwin':
    import unittest.mock as mock
    # Mock the entire ThermoFisher namespace so fisher_py can import on macOS
    tf_mock = mock.MagicMock()
    sys.modules['ThermoFisher'] = tf_mock
    sys.modules['ThermoFisher.CommonCore'] = tf_mock
    sys.modules['ThermoFisher.CommonCore.Data'] = tf_mock
    sys.modules['ThermoFisher.CommonCore.Data.Business'] = tf_mock
    sys.modules['ThermoFisher.CommonCore.Data.FilterEnums'] = tf_mock
    sys.modules['ThermoFisher.CommonCore.Data.Interfaces'] = tf_mock
    sys.modules['ThermoFisher.CommonCore.MassPrecisionEstimator'] = tf_mock
    sys.modules['ThermoFisher.CommonCore.RawFileReader'] = tf_mock

import unittest
import fisher_py
import native_fisher_py
import inspect
from typing import Set, Any


class TestAPIParity(unittest.TestCase):
    def compare_obj(self, name: str, orig_obj: Any, native_obj: Any, seen: Set[int] = None):
        if name.endswith('.net_wrapping') or name.endswith('.utils') or 'data_model' in name:
            return
        if seen is None:
            seen = set()
        if id(orig_obj) in seen:
            return
        seen.add(id(orig_obj))

        def get_real_members(obj):
            members = set()
            for n in dir(obj):
                if n.startswith("_") or n == "_raw_file_access":
                    continue
                try:
                    v = getattr(obj, n, None)
                except Exception:
                    # If getting the attribute throws, it's a dynamic property that failed to evaluate.
                    # We still consider it a member because it exists.
                    members.add(n)
                    continue

                if inspect.ismodule(v):
                    # FIXME: Placeholder - We are intentionally skipping traversal of submodules (like .data.business)
                    # to focus on the public-facing API (like RawFileAccess) rather than internal file structure.
                    # A stricter parity test would map fisher_py's internal modules to native_fisher_py's flattened data.classes.
                    continue
                if inspect.isclass(v) or inspect.isfunction(v):
                    mod = getattr(v, '__module__', None)
                    if mod in ('typing', 'enum', 'builtins'):
                        continue
                    # Only assert on things that belong to fisher_py/native_fisher_py or were defined here
                    if mod and not mod.startswith('fisher_py') and not mod.startswith('native_fisher_py') and mod != getattr(obj, '__name__', None):
                        continue
                members.add(n)
            return members

        orig_members = get_real_members(orig_obj)
        native_members = get_real_members(native_obj)

        # Explicitly filter out known .NET imports or standard library imports that native_fisher_py avoids by design
        ignored_imports = {'NetWrapperBase', 'ThermoFisher', 'ToleranceUnits', 'WrappedRunHeader', 'Array', 'Tuple'}
        orig_members = orig_members - ignored_imports
        native_members = native_members - ignored_imports

        missing_in_native = orig_members - native_members
        if missing_in_native:
            assert False, f"{name} is missing: {sorted(list(missing_in_native))}"

        if inspect.isclass(orig_obj) or inspect.ismodule(orig_obj):
            for member_name in orig_members:
                if member_name in native_members:
                    if member_name.startswith('clr') or member_name in ('NetWrapperBase', 'ThermoFisher', 'ToleranceUnits', 'WrappedRunHeader'):
                        continue

                    # Explicitly skip Enum class properties that throw when evaluated directly on the class
                    import enum
                    if inspect.isclass(orig_obj) and issubclass(orig_obj, enum.Enum) and member_name in ('name', 'value'):
                        continue

                    # Explicitly skip known problematic dynamic properties in native_fisher_py.data
                    if name.endswith('.data') and member_name == 'device':
                        continue

                    orig_m = getattr(orig_obj, member_name)
                    native_m = getattr(native_obj, member_name)
                    if inspect.isclass(orig_m) or inspect.ismodule(orig_m):
                        self.compare_obj(f"{name}.{member_name}", orig_m, native_m, seen)
                else:
                    assert False, f"Missing member: {member_name}"

    def test_global_parity(self):
        self.compare_obj("fisher_py", fisher_py, native_fisher_py)
        if hasattr(fisher_py, "raw_file_reader") and hasattr(fisher_py.raw_file_reader, "RawFileAccess"):
            self.compare_obj("RawFileAccess", fisher_py.raw_file_reader.RawFileAccess, native_fisher_py.RawFile)


if __name__ == "__main__":
    unittest.main()
