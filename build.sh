#!/bin/bash
set -e

# Detect OS and Architecture for RID
OS_TYPE=$(uname -s)
ARCH=$(uname -m)

if [ "$OS_TYPE" == "Darwin" ]; then
    if [ "$ARCH" == "arm64" ]; then RID="osx-arm64"; else RID="osx-x64"; fi
    EXT="dylib"
elif [ "$OS_TYPE" == "Linux" ]; then
    RID="linux-x64"
    EXT="so"
else
    RID="win-x64"
    EXT="dll"
fi

echo "Building for RID: $RID"

# Some networks (e.g. VPNs with broken IPv6 routing) advertise an IPv6 route to
# nuget.org that is actually black-holed, causing NuGet restores to hang for
# minutes before failing with NU1301. Force IPv4 to avoid this.
export DOTNET_SYSTEM_NET_DISABLEIPV6=1

# 1. Build C# NativeAOT
cd native/ThermoNativeReader
dotnet publish -r $RID -c Release -p:PublishAot=true
LIB_NAME="ThermoNativeReader.$EXT"
DYLIB_PATH=$(pwd)/bin/Release/net8.0/$RID/publish/$LIB_NAME
cd ../..

# Copy the built library into the python package directory
# This allows maturin to include it in the wheel
cp $DYLIB_PATH native_fisher_py/python/native_fisher_py/
cp vendor/RawFileReader/Libs/NetCore/Net8/Assemblies/*.dll native_fisher_py/python/native_fisher_py/

# 2. Build Python Package
cd native_fisher_py
export THERMO_NATIVE_LIB=$(pwd)/python/native_fisher_py/$LIB_NAME

# Check for maturin
cp ../README.md README.md
MATURIN_ARGS="develop"
for arg in "$@"; do
    case $arg in
        --wheel) MATURIN_ARGS="build --release --out ../dist" ;;
        # Free-threaded builds can't use the abi3 stable ABI, so this must be run
        # with a free-threaded interpreter (e.g. python3.13t) active/first on PATH.
        --freethreaded) MATURIN_ARGS="build --release --out ../dist --no-default-features" ;;
    esac
done
if command -v maturin >/dev/null 2>&1; then
    maturin $MATURIN_ARGS
elif command -v pipenv >/dev/null 2>&1 && pipenv run maturin --version >/dev/null 2>&1; then
    pipenv run maturin $MATURIN_ARGS
else
    echo "Error: maturin not found. Please install it with 'pip install maturin' or 'pipenv install maturin'."
    exit 1
fi
cd ..

if [[ "$MATURIN_ARGS" == build* ]]; then
    echo "Build complete. Wheel written to dist/."
else
    echo "Build complete. native-fisher-py is installed in your current environment."
fi
