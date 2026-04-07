# native-fisher-py

[![PyPI version](https://img.shields.io/pypi/v/native-fisher-py.svg)](https://pypi.org/project/native-fisher-py/)
[![Tests](https://github.com/z3rone-org/native-fisher-py/actions/workflows/test.yml/badge.svg)](https://github.com/z3rone-org/native-fisher-py/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/native-fisher-py/badge/?version=latest)](https://native-fisher-py.readthedocs.io/en/latest/?badge=latest)
<!-- [![Downloads](https://static.pepy.tech/badge/native-fisher-py)](https://pepy.tech/project/native-fisher-py) -->

## Why native-fisher-py?
`native-fisher-py` is a self-contained alternative to the `fisher-py` reader. While `fisher-py` requires a local .NET runtime and `pythonnet`, this package bundles the necessary components using **.NET NativeAOT** and **Rust** to provide a consistent binary bridge.

### Features
- **Drop-in Compatible**: Designed to match the `fisher_py.RawFile` API for simplified migration.
- **Bundled .NET Components**: No separate .NET runtime installation is required on the host system.
- **Cross-Platform**: Pre-built binaries for **macOS (ARM64/x64)**, **Linux (x64)**, and **Windows (x64)**.
- **Reliable Deployment**: Easier integration into CI/CD pipelines and specialized Linux environments.

## How it works
This project provides a native bridge to the official Thermo Fisher libraries using a three-layer approach:

1. **Official DLLs**: Uses the original `.dll` assemblies provided by Thermo Fisher Scientific.
2. **C# NativeAOT Wrapper**: A compiled transition layer (`ThermoNativeReader`) that interfaces with those DLLs.
3. **Rust PyO3 Layer**: A Rust bridge (`native-fisher-py`) that provides the final Python bindings.

This approach ensures stability and parity with the official reader while providing a dependency-free experience for Python users.

## Quick Start
```python
# Just change the import, the rest of your code stays the same!
from native_fisher_py import RawFile

with RawFile("data.raw") as raw:
    print(f"Number of scans: {raw.number_of_scans}")
    
    # Get spectral data as high-speed NumPy arrays
    m, i, c, meta = raw.get_scan_from_scan_number(1)
    print(f"First peak at {m[0]} m/z with intensity {i[0]}")
```

## Migrating from fisher-py
If you are currently using `fisher-py`, migration is as simple as:
1. `pip install native-fisher-py`
2. Update your imports:
```diff
- from fisher_py import RawFile
+ from native_fisher_py import RawFile
```
3. (Optional) Uninstall `fisher-py`: `pip uninstall fisher-py`

All core methods (`get_scan_from_scan_number`, `get_spectrum`, `get_chromatogram`, `get_ms2_scan_number_from_retention_time`, etc.) are implemented with identical signatures and return types.

### Quick Local Build
For convenience, you can run the included `build.sh` script to build both parts of the project:

```bash
./build.sh
```

---

### Step-by-Step Manual Build
To build the project from source, you need `.NET 8 SDK`, `Rust (cargo/maturin)`, and `clang`.

### 1. Build the C# NativeAOT Core
Navigate to the C# project and publish the NativeAOT shared library for your platform:

```bash
cd native/ThermoNativeReader

# Example for Apple Silicon (macOS arm64)
dotnet publish -r osx-arm64 -c Release -p:PublishAot=true

# Example for Linux (x64)
# dotnet publish -r linux-x64 -c Release -p:PublishAot=true
```
The output will be in `publish/ThermoNativeReader.dylib` (or `.so` / `.dll`).

### 2. Build the Rust Bridge
Navigate to the `native_fisher_py` folder and use `maturin` to build and install the Python package. You must point to the location of the C# library.

```bash
cd native_fisher_py

# Point to your build from Step 1
export THERMO_NATIVE_LIB=$(pwd)/../native/ThermoNativeReader/bin/Release/net8.0/osx-arm64/publish/ThermoNativeReader.dylib

maturin develop
```

## Credits & Legal Notice
This project is powered by the **Thermo Fisher Scientific RawFileReader** (copyright © 2016-2026 Thermo Fisher Scientific, Inc.). All rights reserved.

The `native-fisher-py` package includes the official RawFileReader libraries, which remain the property of Thermo Fisher Scientific. By using this software, you agree to the terms specified in their license.
