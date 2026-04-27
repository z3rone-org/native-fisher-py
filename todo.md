# Unimplemented API Endpoints

This document lists the API endpoints and properties that are defined in the `native-fisher-py` codebase but currently lack implementation. 
They are ranked by importance for typical mass spectrometry data processing workflows.

## 1. Critical Importance (Core Data & MS/MS)
*Missing foundational data required for standard LC-MS/MS analysis.*

| Class | Method / Property | Status |
| :--- | :--- | :--- |
| `ScanEvent` | `get_isolation_width(index)` | ❌ Missing in Native & Python |
| `ScanEvent` | `get_mass_range(index)` | ❌ Missing in Native & Python |
| `Reaction` | `isolation_width` | ❌ Python Placeholder |
| `Reaction` | `isolation_width_offset` | ❌ Python Placeholder |
| `Reaction` | `precursor_range_is_valid` | ❌ Python Placeholder |
| `ScanDependentDetails` | `precursor_mass_array` | ❌ Python Placeholder |
| `ScanDependentDetails` | `isolation_width_array` | ❌ Python Placeholder |

## 2. High Importance (Metadata & Run Stats)
*Essential for file overview and scan tracking.*

| Class | Method / Property | Status |
| :--- | :--- | :--- |
| `RunHeader` | `end_time` | ❌ Python Placeholder |
| `RunHeader` | `expected_runtime` | ❌ Python Placeholder |
| `RunHeader` | `high_mass` / `low_mass` | ❌ Python Placeholder |
| `RunHeader` | `spectra_count` | ⚠️ Partially implemented in some subclasses |
| `ScanStatistics` | `cycle_number` | ❌ Python Placeholder |
| `ScanStatistics` | `segment_number` | ❌ Python Placeholder |
| `ScanStatistics` | `scan_type` | ❌ Python Placeholder |
| `ScanStatistics` | `spectrum_packet_type` | ❌ Python Placeholder |

## 3. Medium Importance (Diagnostic & Advanced Info)
*Useful for peak quality assessment and instrument status.*

| Class | Method / Property | Status |
| :--- | :--- | :--- |
| `CentroidStream` | `base_peak_noise` | ✅ Implemented |
| `CentroidStream` | `base_peak_resolution` | ✅ Implemented |
| `CentroidStream` | `baselines` | ✅ Implemented |
| `CentroidStream` | `charges` | ✅ Implemented |
| `CentroidStream` | `noises` | ✅ Implemented |
| `SampleInformation` | `injection_volume` | ✅ Implemented |
| `SampleInformation` | `instrument_method_file` | ✅ Implemented |
| `AutoSamplerInformation`| `tray_index` / `vial_index` | ✅ Implemented |
| `AutoSamplerInformation`| `tray_name` / `tray_shape` | ✅ Implemented |

## 4. Low Importance (Verbose Metadata)
*Auxiliary information rarely used in downstream analysis.*

| Class | Method / Property | Status |
| :--- | :--- | :--- |
| `ErrorLogEntry` | `message` | ❌ Python Placeholder |
| `ErrorLogEntry` | `retention_time` | ❌ Python Placeholder |
| `HeaderItem` | `is_numeric` | ❌ Python Placeholder |
| `HeaderItem` | `format_value` | ❌ Python Placeholder |
| `FileHeader` | `revision` | ❌ Python Placeholder |
| `FileHeader` | `number_of_times_calibrated`| ❌ Python Placeholder |
| `ScanEvent` | `is_custom` | ❌ Python Placeholder |
| `ScanEvents` | `get_event_by_segment` | ❌ Python Placeholder |

---
**Note:** Many Python placeholders return default values when `_IS_SPHINX` is true to allow documentation builds, but will raise `NotImplementedError` during actual execution.
