import os

base_path = "native_fisher_py/python/native_fisher_py/data"

filter_enums = [
    "activation_type", "mass_analyzer_type", "ms_order_type", "ionization_mode_type", 
    "scan_mode_type", "polarity_type", "detector_type", "scan_data_type", 
    "sector_scan_type", "field_free_region_type", "tri_state", "energy_type", 
    "event_accurate_mass", "source_fragmentation_value_type", "compensation_voltage_type"
]

mapping = {
    "mass_analyzer_type": "MassAnalyzer",
    "ms_order_type": "MSOrder"
}

for name in filter_enums:
    cls_name = mapping.get(name, "".join([x.capitalize() for x in name.split("_")]))
    dir_path = os.path.join(base_path, "filter_enums")
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, f"{name}.py"), "w") as f:
        f.write(f"import enum\nfrom .. import {cls_name}\n{name} = {cls_name}\n{cls_name} = {cls_name}\nenum = enum\n")

business_objects = [
    "instrument_data", "sample_information", "file_header", "file_error", 
    "scan_event", "scan_events", "scan_statistics", "segmented_scan", 
    "centroid_stream", "scan_dependents", "log_entry", "header_item", 
    "status_log_values", "tune_data_values", "reaction", "scan", 
    "chromatogram_signal", "mass_options", "range", "trace_type", "error_log_entry", "peak_options", "ft_average_options", "tolerance_units"
]

for name in business_objects:
    cls_name = "".join([x.capitalize() for x in name.split("_")])
    if name == "mass_options": cls_name = "MassOptions"
    if name == "range": cls_name = "Range"
    if name == "trace_type": cls_name = "TraceType"
    if name == "tolerance_units": cls_name = "ToleranceUnits"
    dir_path = os.path.join(base_path, "business")
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, f"{name}.py"), "w") as f:
        f.write(f"import enum\nfrom .. import {cls_name}\n{name} = {cls_name}\n{cls_name} = {cls_name}\nenum = enum\n")
