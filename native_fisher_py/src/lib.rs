use pyo3::prelude::*;
use libloading::{Library, Symbol};
use std::sync::OnceLock;
use std::ffi::CString;
use std::os::raw::c_char;

static LIB: OnceLock<Library> = OnceLock::new();

fn get_lib() -> PyResult<&'static Library> {
    if let Some(lib) = LIB.get() {
        return Ok(lib);
    }
    
    // Automatic discovery as fallback
    let lib_name = if cfg!(target_os = "windows") {
        "ThermoNativeReader.dll"
    } else if cfg!(target_os = "macos") {
        "ThermoNativeReader.dylib"
    } else {
        "ThermoNativeReader.so"
    };

    // 1. Environment variable override
    if let Ok(env_path) = std::env::var("THERMO_NATIVE_LIB") {
        if std::path::Path::new(&env_path).exists() {
            let lib = unsafe {
                Library::new(&env_path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to load override dylib {}: {}", env_path, e)))?
            };
            let _ = LIB.set(lib);
            return Ok(LIB.get().unwrap());
        }
    }

    // 2. Local search (./ThermoNativeReader.so etc)
    let search_paths = vec![
        std::path::PathBuf::from(lib_name),
        std::path::PathBuf::from("./").join(lib_name),
    ];

    for path in search_paths {
        if path.exists() {
            let lib = unsafe {
                Library::new(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to load dylib {}: {}", path.display(), e)))?
            };
            let _ = LIB.set(lib);
            return Ok(LIB.get().unwrap());
        }
    }

    Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Dylib not found and THERMO_NATIVE_LIB not set."))
}

#[pyfunction]
fn set_dylib_path(path: String) -> PyResult<()> {
    if LIB.get().is_some() {
        return Ok(());
    }
    
    if !std::path::Path::new(&path).exists() {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Dylib not found at: {}", path)));
    }

    let lib = unsafe {
        Library::new(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to load dylib {}: {}", path, e)))?
    };
    
    let _ = LIB.set(lib);
    Ok(())
}

#[pyfunction]
fn open_raw_file(path: String) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*const c_char) -> i32> = lib.get(b"open_raw_file")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function open_raw_file: {}", e)))?;
        let c_path = CString::new(path).map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>("nul byte in path"))?;
        Ok(func(c_path.as_ptr()))
    }
}

#[pyfunction]
fn get_num_scans() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_num_scans")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_num_scans: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_scan_rt(scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> f64> = lib.get(b"get_scan_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_rt: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_spectrum(scan_number: i32, max_length: i32) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let lib = get_lib()?;
    let mut masses = vec![0.0f64; max_length as usize];
    let mut intensities = vec![0.0f64; max_length as usize];
    
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, *mut f64, *mut f64, i32) -> i32> = lib.get(b"get_spectrum")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_spectrum: {}", e)))?;
        let actual_len = func(scan_number, masses.as_mut_ptr(), intensities.as_mut_ptr(), max_length);
        if actual_len < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_spectrum failed"));
        }
        let final_len = std::cmp::min(actual_len, max_length) as usize;
        masses.truncate(final_len);
        intensities.truncate(final_len);
        Ok((masses, intensities))
    }
}

#[pyfunction]
fn get_first_scan() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_first_scan")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_first_scan: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_last_scan() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_last_scan")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_last_scan: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_end_time() -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> f64> = lib.get(b"get_end_time")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_end_time: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_start_time() -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> f64> = lib.get(b"get_start_time")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_start_time: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_mass_resolution() -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> f64> = lib.get(b"get_mass_resolution")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_mass_resolution: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_expected_runtime() -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> f64> = lib.get(b"get_expected_runtime")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_expected_runtime: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_max_integrated_intensity() -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> f64> = lib.get(b"get_max_integrated_intensity")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_max_integrated_intensity: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_max_intensity() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_max_intensity")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_max_intensity: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_file_name() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_file_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_file_name: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_file_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_path() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_path")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_path: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_path failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_creation_date() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_creation_date")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_creation_date: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_creation_date failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_computer_name() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_computer_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_computer_name: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_computer_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_creator_id() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_creator_id")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_creator_id: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_creator_id failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_model() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_model")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_model: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_model failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_name() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_name: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_serial_number() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_serial_number")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_serial_number: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_serial_number failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_software_version() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_software_version")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_software_version: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_software_version failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_hardware_version() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_hardware_version")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_hardware_version: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_hardware_version failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_ms_order(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_ms_order")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms_order: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_mass_analyzer(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_mass_analyzer")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_mass_analyzer: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_precursor_mass(scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> f64> = lib.get(b"get_precursor_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_precursor_mass: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_event_string(scan_number: i32) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, *mut u8, i32) -> i32> = lib.get(b"get_scan_event_string")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_string: {}", e)))?;
        let actual_len = func(scan_number, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_scan_event_string failed"));
        }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_scan_number_from_rt(rt: f64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(f64) -> i32> = lib.get(b"get_scan_number_from_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_number_from_rt: {}", e)))?;
        Ok(func(rt))
    }
}

#[pyfunction]
fn get_ms2_filter_masses(max_size: i32) -> PyResult<Vec<f64>> {
    let lib = get_lib()?;
    let mut buffer = vec![0.0f64; max_size as usize];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut f64, i32) -> i32> = lib.get(b"get_ms2_filter_masses")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms2_filter_masses: {}", e)))?;
        let count = func(buffer.as_mut_ptr(), max_size);
        if count < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_ms2_filter_masses failed"));
        }
        buffer.truncate(count as usize);
        Ok(buffer)
    }
}

#[pyfunction]
fn get_ms2_scan_number_from_rt(rt: f64, precursor_mz: f64, tolerance_ppm: f64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(f64, f64, f64) -> i32> = lib.get(b"get_ms2_scan_number_from_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms2_scan_number_from_rt: {}", e)))?;
        let res = func(rt, precursor_mz, tolerance_ppm);
        Ok(res)
    }
}

#[pyfunction]
fn get_ms1_scan_number_from_rt(rt: f64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(f64) -> i32> = lib.get(b"get_ms1_scan_number_from_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms1_scan_number_from_rt: {}", e)))?;
        let res = func(rt);
        Ok(res)
    }
}

#[pyfunction]
fn get_chromatogram(trace_type: i32, max_length: i32) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let lib = get_lib()?;
    let mut times = vec![0.0f64; max_length as usize];
    let mut intensities = vec![0.0f64; max_length as usize];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, *mut f64, *mut f64, i32) -> i32> = lib.get(b"get_chromatogram")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_chromatogram: {}", e)))?;
        let count = func(trace_type, times.as_mut_ptr(), intensities.as_mut_ptr(), max_length);
        if count < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_chromatogram failed"));
        }
        let actual_count = count.min(max_length) as usize;
        times.truncate(actual_count);
        intensities.truncate(actual_count);
        Ok((times, intensities))
    }
}

#[pyfunction]
fn get_averaged_spectrum(scan_numbers: Vec<i32>, max_length: i32) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let lib = get_lib()?;
    let mut masses = vec![0.0f64; max_length as usize];
    let mut intensities = vec![0.0f64; max_length as usize];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*const i32, i32, *mut f64, *mut f64, i32) -> i32> = lib.get(b"get_averaged_spectrum")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_averaged_spectrum: {}", e)))?;
        let count = func(scan_numbers.as_ptr(), scan_numbers.len() as i32, masses.as_mut_ptr(), intensities.as_mut_ptr(), max_length);
        if count < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_averaged_spectrum failed"));
        }
        let actual_count = (count as usize).min(max_length as usize);
        masses.truncate(actual_count);
        intensities.truncate(actual_count);
        Ok((masses, intensities))
    }
}

#[pyfunction]
fn get_instrument_count() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_instrument_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_count: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_instrument_count_of_type(device_type: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_instrument_count_of_type")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_count_of_type: {}", e)))?;
        Ok(func(device_type))
    }
}

#[pyfunction]
fn is_open() -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"is_open")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function is_open: {}", e)))?;
        Ok(func() != 0)
    }
}

#[pyfunction]
fn is_error() -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"is_error")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function is_error: {}", e)))?;
        Ok(func() != 0)
    }
}

#[pyfunction]
fn in_acquisition() -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"in_acquisition")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function in_acquisition: {}", e)))?;
        Ok(func() != 0)
    }
}

#[pyfunction]
fn has_ms_data() -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"has_ms_data")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function has_ms_data: {}", e)))?;
        Ok(func() != 0)
    }
}

#[pyfunction]
fn close_raw_file() -> PyResult<()> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn()> = lib.get(b"close_raw_file")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function close_raw_file: {}", e)))?;
        func();
        Ok(())
    }
}

/// Low-level NativeAOT bridge for Thermo Fisher RAW files.
#[pymodule]
fn native_fisher_py_backend(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(open_raw_file, m)?)?;
    m.add_function(wrap_pyfunction!(get_num_scans, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_rt, m)?)?;
    m.add_function(wrap_pyfunction!(get_spectrum, m)?)?;
    m.add_function(wrap_pyfunction!(get_first_scan, m)?)?;
    m.add_function(wrap_pyfunction!(get_last_scan, m)?)?;
    m.add_function(wrap_pyfunction!(get_start_time, m)?)?;
    m.add_function(wrap_pyfunction!(get_end_time, m)?)?;
    m.add_function(wrap_pyfunction!(get_mass_resolution, m)?)?;
    m.add_function(wrap_pyfunction!(get_expected_runtime, m)?)?;
    m.add_function(wrap_pyfunction!(get_max_integrated_intensity, m)?)?;
    m.add_function(wrap_pyfunction!(get_max_intensity, m)?)?;
    m.add_function(wrap_pyfunction!(get_file_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_ms_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_mass_analyzer, m)?)?;
    m.add_function(wrap_pyfunction!(get_precursor_mass, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_string, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_number_from_rt, m)?)?;
    m.add_function(wrap_pyfunction!(get_ms2_filter_masses, m)?)?;
    m.add_function(wrap_pyfunction!(get_ms2_scan_number_from_rt, m)?)?;
    m.add_function(wrap_pyfunction!(get_ms1_scan_number_from_rt, m)?)?;
    m.add_function(wrap_pyfunction!(get_chromatogram, m)?)?;
    m.add_function(wrap_pyfunction!(get_averaged_spectrum, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_count_of_type, m)?)?;
    m.add_function(wrap_pyfunction!(is_open, m)?)?;
    m.add_function(wrap_pyfunction!(is_error, m)?)?;
    m.add_function(wrap_pyfunction!(in_acquisition, m)?)?;
    m.add_function(wrap_pyfunction!(has_ms_data, m)?)?;
    m.add_function(wrap_pyfunction!(get_file_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_path, m)?)?;
    m.add_function(wrap_pyfunction!(get_creation_date, m)?)?;
    m.add_function(wrap_pyfunction!(open_raw_file, m)?)?;
    m.add_function(wrap_pyfunction!(set_dylib_path, m)?)?;
    m.add_function(wrap_pyfunction!(get_computer_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_creator_id, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_model, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_serial_number, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_software_version, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_hardware_version, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_log_values, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_log_header, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_log_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_trailer_extra_values, m)?)?;
    m.add_function(wrap_pyfunction!(get_trailer_extra_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_trailer_extra_header, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_ms_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_mass_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_precursor_mass, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_activation_type, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_collision_energy, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_stats, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_axis_label_x, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_axis_label_y, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_flags, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_units, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_is_valid, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_has_accurate_mass_precursors, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_is_tsq_quantum_file, m)?)?;
    m.add_function(wrap_pyfunction!(get_file_description, m)?)?;
    m.add_function(wrap_pyfunction!(get_modified_date, m)?)?;
    m.add_function(wrap_pyfunction!(get_who_created_logon, m)?)?;
    m.add_function(wrap_pyfunction!(get_who_modified_id, m)?)?;
    m.add_function(wrap_pyfunction!(get_who_modified_logon, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_barcode, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_id, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_vial, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_comment, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_ultra, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_wideband, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_polarity, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_ms_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_mass_analyzer, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_detector, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_scan_data, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_scan_mode, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_accurate_mass, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_ionization_mode, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_lock, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_turbo_scan, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_corona, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_dependent, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_detector_value, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_compensation_voltage, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_compensation_voltage_value, m)?)?;
    m.add_function(wrap_pyfunction!(close_raw_file, m)?)?;
    Ok(())
}

#[pyfunction]
fn get_scan_filter_scan_mode(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_scan_mode")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_scan_mode: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_accurate_mass(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_accurate_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_accurate_mass: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_ionization_mode(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_ionization_mode")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_ionization_mode: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_lock(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_lock")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_lock: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_turbo_scan(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_turbo_scan")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_turbo_scan: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_corona(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_corona")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_corona: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_dependent(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_dependent")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_dependent: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_detector_value(scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> f64> = lib.get(b"get_scan_filter_detector_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_detector_value: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_event_compensation_voltage(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_event_compensation_voltage")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_compensation_voltage: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_event_compensation_voltage_value(scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> f64> = lib.get(b"get_scan_event_compensation_voltage_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_compensation_voltage_value: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_event_ms_order(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_event_ms_order")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_ms_order: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_event_mass_count(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_event_mass_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_mass_count: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_event_precursor_mass(scan_number: i32, index: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, i32) -> f64> = lib.get(b"get_scan_event_precursor_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_precursor_mass: {}", e)))?;
        Ok(func(scan_number, index))
    }
}

#[pyfunction]
fn get_scan_event_activation_type(scan_number: i32, index: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, i32) -> i32> = lib.get(b"get_scan_event_activation_type")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_activation_type: {}", e)))?;
        Ok(func(scan_number, index))
    }
}

#[pyfunction]
fn get_scan_event_collision_energy(scan_number: i32, index: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, i32) -> f64> = lib.get(b"get_scan_event_collision_energy")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_collision_energy: {}", e)))?;
        Ok(func(scan_number, index))
    }
}

#[pyfunction]
fn get_scan_stats(scan_number: i32) -> PyResult<Vec<f64>> {
    let lib = get_lib()?;
    let mut data = vec![0.0f64; 7];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, *mut f64) -> i32> = lib.get(b"get_scan_stats")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_stats: {}", e)))?;
        let res = func(scan_number, data.as_mut_ptr());
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_scan_stats failed")); }
        Ok(data)
    }
}

#[pyfunction]
fn get_scan_filter_ultra(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_ultra")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_ultra: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_wideband(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_wideband")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_wideband: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_polarity(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_polarity")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_polarity: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_ms_order(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_ms_order")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_ms_order: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_mass_analyzer(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_mass_analyzer")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_mass_analyzer: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_detector(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_detector")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_detector: {}", e)))?;
        Ok(func(scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_scan_data(scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32) -> i32> = lib.get(b"get_scan_filter_scan_data")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_scan_data: {}", e)))?;
        Ok(func(scan_number))
    }
}


#[pyfunction]
fn get_trailer_extra_count() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_trailer_extra_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_trailer_extra_count: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_status_log_values(scan_number: i32) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, *mut u8, i32) -> i32> = lib.get(b"get_status_log_values")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_status_log_values: {}", e)))?;
        let res = func(scan_number, buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_status_log_values failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_status_log_header() -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_status_log_header")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_status_log_header: {}", e)))?;
        let res = func(buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_status_log_header failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_status_log_count() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_status_log_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_status_log_count: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_trailer_extra_values(scan_number: i32) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i32, *mut u8, i32) -> i32> = lib.get(b"get_trailer_extra_values")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_trailer_extra_values: {}", e)))?;
        let res = func(scan_number, buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_trailer_extra_values failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_trailer_extra_header() -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_trailer_extra_header")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_trailer_extra_header: {}", e)))?;
        let res = func(buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_trailer_extra_header failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_file_description() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_file_description")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_file_description: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_file_description failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_modified_date() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_modified_date")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_modified_date: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_modified_date failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_who_created_logon() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_who_created_logon")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_who_created_logon: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_who_created_logon failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_who_modified_id() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_who_modified_id")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_who_modified_id: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_who_modified_id failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_who_modified_logon() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_who_modified_logon")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_who_modified_logon: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_who_modified_logon failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_barcode() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_sample_barcode")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_barcode: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_barcode failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_id() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_sample_id")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_id: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_id failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_name() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_sample_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_name: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_vial() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_sample_vial")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_vial: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_vial failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_comment() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_sample_comment")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_comment: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_comment failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_axis_label_x() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_axis_label_x")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_axis_label_x: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_axis_label_x failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_axis_label_y() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_axis_label_y")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_axis_label_y: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_axis_label_y failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_flags() -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*mut u8, i32) -> i32> = lib.get(b"get_instrument_flags")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_flags: {}", e)))?;
        let actual_len = func(buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_flags failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_units() -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_instrument_units")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_units: {}", e)))?;
        Ok(func())
    }
}

#[pyfunction]
fn get_instrument_is_valid() -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_instrument_is_valid")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_is_valid: {}", e)))?;
        Ok(func() != 0)
    }
}

#[pyfunction]
fn get_instrument_has_accurate_mass_precursors() -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_instrument_has_accurate_mass_precursors")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_has_accurate_mass_precursors: {}", e)))?;
        Ok(func() != 0)
    }
}

#[pyfunction]
fn get_instrument_is_tsq_quantum_file() -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn() -> i32> = lib.get(b"get_instrument_is_tsq_quantum_file")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_is_tsq_quantum_file: {}", e)))?;
        Ok(func() != 0)
    }
}
