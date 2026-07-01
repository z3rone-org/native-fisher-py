# Stage 1: Build the package
FROM python:3.11-bookworm AS builder

# Install dependencies for .NET NativeAOT and Rust
RUN apt-get update && apt-get install -y clang zlib1g-dev libkrb5-dev curl

# Install .NET 8 SDK
RUN curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 8.0
ENV PATH="/root/.dotnet:${PATH}"

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app
COPY . .

# Build NativeAOT library
WORKDIR /app/native/ThermoNativeReader
RUN dotnet publish -r linux-x64 -c Release -p:PublishAot=true

# Copy NativeAOT library and dependencies to Python package directory
WORKDIR /app
RUN cp native/ThermoNativeReader/bin/Release/net8.0/linux-x64/publish/ThermoNativeReader.so native_fisher_py/python/native_fisher_py/ && \
    cp vendor/RawFileReader/Libs/NetCore/Net8/Assemblies/*.dll native_fisher_py/python/native_fisher_py/ && \
    cp README.md native_fisher_py/

# Build wheel using maturin
RUN pip install maturin
WORKDIR /app/native_fisher_py
RUN maturin build --release --out /wheels

# Stage 2: Final runtime image
FROM python:3.11-slim-bookworm

# Install runtime dependencies including libicu for .NET globalization
RUN apt-get update && apt-get install -y libkrb5-3 libicu72 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the built wheel from the builder stage
COPY --from=builder /wheels /wheels

# Install the wheel
RUN pip install /wheels/*.whl && rm -rf /wheels

# Set default command
CMD ["python3"]
