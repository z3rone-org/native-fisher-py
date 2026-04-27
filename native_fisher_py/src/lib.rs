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
fn open_raw_file(path: String) -> PyResult<i64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(*const c_char) -> i64> = lib.get(b"open_raw_file")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function open_raw_file: {}", e)))?;
        let c_path = CString::new(path).map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>("nul byte in path"))?;
        Ok(func(c_path.as_ptr()))
    }
}

#[pyfunction]
fn get_num_scans(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_num_scans")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_num_scans: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_tune_data_count(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_tune_data_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_tune_data_count: {}", e)))?;
        Ok(func(handle))
    }
}


#[pyfunction]
fn get_scan_rt(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_rt: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_spectrum(handle: i64, scan_number: i32, max_length: i32) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let lib = get_lib()?;
    let mut masses = vec![0.0f64; max_length as usize];
    let mut intensities = vec![0.0f64; max_length as usize];
    
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut f64, *mut f64, i32) -> i32> = lib.get(b"get_spectrum")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_spectrum: {}", e)))?;
        let actual_len = func(handle, scan_number, masses.as_mut_ptr(), intensities.as_mut_ptr(), max_length);
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
fn is_centroid(handle: i64, scan_number: i32) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"is_centroid")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function is_centroid: {}", e)))?;
        Ok(func(handle, scan_number) != 0)
    }
}

#[pyfunction]
fn get_centroid_stream(handle: i64, scan_number: i32, max_length: i32) -> PyResult<(Vec<f64>, Vec<f64>, Vec<f64>, Vec<f64>, Vec<i32>, f64, f64)> {
    let lib = get_lib()?;
    let mut masses = vec![0.0f64; max_length as usize];
    let mut intensities = vec![0.0f64; max_length as usize];
    let mut baselines = vec![0.0f64; max_length as usize];
    let mut noises = vec![0.0f64; max_length as usize];
    let mut charges = vec![0i32; max_length as usize];
    let mut noise_res = vec![0.0f64; 2];

    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut f64, *mut f64, *mut f64, *mut f64, *mut i32, *mut f64, i32) -> i32> = 
            lib.get(b"get_centroid_stream_full")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_centroid_stream_full: {}", e)))?;
        
        let actual_len = func(
            handle,
            scan_number, 
            masses.as_mut_ptr(), 
            intensities.as_mut_ptr(), 
            baselines.as_mut_ptr(),
            noises.as_mut_ptr(),
            charges.as_mut_ptr(),
            noise_res.as_mut_ptr(),
            max_length
        );
        
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_centroid_stream_full failed")); }
        
        let final_len = std::cmp::min(actual_len, max_length) as usize;
        masses.truncate(final_len);
        intensities.truncate(final_len);
        baselines.truncate(final_len);
        noises.truncate(final_len);
        charges.truncate(final_len);

        Ok((masses, intensities, baselines, noises, charges, noise_res[0], noise_res[1]))
    }
}

#[pyfunction]
fn get_sample_type(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_sample_type")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_type: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_sample_row_number(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_sample_row_number")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_row_number: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_sample_dilution_factor(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_sample_dilution_factor")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_dilution_factor: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_first_scan(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_first_scan")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_first_scan: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_last_scan(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_last_scan")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_last_scan: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_end_time(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_end_time")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_end_time: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_start_time(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_start_time")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_start_time: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_mass_resolution(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_mass_resolution")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_mass_resolution: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_expected_runtime(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_expected_runtime")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_expected_runtime: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_max_integrated_intensity(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_max_integrated_intensity")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_max_integrated_intensity: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_max_intensity(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_max_intensity")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_max_intensity: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_low_mass(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_low_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_low_mass: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_high_mass(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_high_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_high_mass: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_file_name(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_file_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_file_name: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_file_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_path(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_path")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_path: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_path failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_creation_date(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_creation_date")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_creation_date: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_creation_date failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_computer_name(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_computer_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_computer_name: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_computer_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_creator_id(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_creator_id")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_creator_id: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_creator_id failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_model(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_model")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_model: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_model failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_name(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_name: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_serial_number(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_serial_number")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_serial_number: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_serial_number failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_software_version(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_software_version")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_software_version: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_software_version failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_hardware_version(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_hardware_version")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_hardware_version: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_hardware_version failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_ms_order(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_ms_order")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms_order: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_mass_analyzer(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_mass_analyzer")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_mass_analyzer: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_precursor_mass(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_precursor_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_precursor_mass: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_event_string(handle: i64, scan_number: i32) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut u8, i32) -> i32> = lib.get(b"get_scan_event_string")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_string: {}", e)))?;
        let actual_len = func(handle, scan_number, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_scan_event_string failed"));
        }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_scan_filter_string(handle: i64, scan_number: i32) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut u8, i32) -> i32> = lib.get(b"get_scan_filter_string")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_string: {}", e)))?;
        let actual_len = func(handle, scan_number, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_scan_filter_string failed"));
        }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_scan_number_from_rt(handle: i64, rt: f64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, f64) -> i32> = lib.get(b"get_scan_number_from_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_number_from_rt: {}", e)))?;
        Ok(func(handle, rt))
    }
}

#[pyfunction]
fn get_ms2_filter_masses(handle: i64, max_size: i32) -> PyResult<Vec<f64>> {
    let lib = get_lib()?;
    let mut buffer = vec![0.0f64; max_size as usize];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut f64, i32) -> i32> = lib.get(b"get_ms2_filter_masses")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms2_filter_masses: {}", e)))?;
        let count = func(handle, buffer.as_mut_ptr(), max_size);
        if count < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_ms2_filter_masses failed"));
        }
        buffer.truncate(count as usize);
        Ok(buffer)
    }
}

#[pyfunction]
fn get_ms2_scan_number_from_rt(handle: i64, rt: f64, precursor_mz: f64, tolerance_ppm: f64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, f64, f64, f64) -> i32> = lib.get(b"get_ms2_scan_number_from_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms2_scan_number_from_rt: {}", e)))?;
        let res = func(handle, rt, precursor_mz, tolerance_ppm);
        Ok(res)
    }
}

#[pyfunction]
fn get_ms1_scan_number_from_rt(handle: i64, rt: f64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, f64) -> i32> = lib.get(b"get_ms1_scan_number_from_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_ms1_scan_number_from_rt: {}", e)))?;
        let res = func(handle, rt);
        Ok(res)
    }
}

#[pyfunction]
fn get_chromatogram(handle: i64, trace_type: i32, filter: String, mass_ranges_start: Vec<f64>, mass_ranges_end: Vec<f64>, start_scan: i32, end_scan: i32, max_length: i32) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let lib = get_lib()?;
    let mut times = vec![0.0f64; max_length as usize];
    let mut intensities = vec![0.0f64; max_length as usize];
    let start_ptr = mass_ranges_start.as_ptr();
    let end_ptr = mass_ranges_end.as_ptr();
    let count = mass_ranges_start.len() as i32;
    
    let c_filter = std::ffi::CString::new(filter).unwrap();
    
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *const std::os::raw::c_char, *const f64, *const f64, i32, i32, i32, *mut f64, *mut f64, i32) -> i32> = lib.get(b"get_chromatogram")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_chromatogram: {}", e)))?;
        let count_res = func(handle, trace_type, c_filter.as_ptr(), start_ptr, end_ptr, count, start_scan, end_scan, times.as_mut_ptr(), intensities.as_mut_ptr(), max_length);
        if count_res < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_chromatogram failed"));
        }
        let actual_count = count_res.min(max_length) as usize;
        times.truncate(actual_count);
        intensities.truncate(actual_count);
        Ok((times, intensities))
    }
}

#[pyfunction]
fn get_filters(handle: i64) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut filters = vec![std::ptr::null_mut(); 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut *mut std::os::raw::c_char, i32) -> i32> = lib.get(b"get_filters")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_filters: {}", e)))?;
        let count = func(handle, filters.as_mut_ptr(), 1024);
        if count < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_filters failed"));
        }
        let actual_count = count.min(1024) as usize;
        let mut result = Vec::with_capacity(actual_count);
        for i in 0..actual_count {
            if !filters[i].is_null() {
                let s = std::ffi::CStr::from_ptr(filters[i]).to_string_lossy().into_owned();
                result.push(s);
            }
        }
        Ok(result)
    }
}

#[pyfunction]
fn get_averaged_spectrum(handle: i64, scan_numbers: Vec<i32>, max_length: i32) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let lib = get_lib()?;
    let mut masses = vec![0.0f64; max_length as usize];
    let mut intensities = vec![0.0f64; max_length as usize];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *const i32, i32, *mut f64, *mut f64, i32) -> i32> = lib.get(b"get_averaged_spectrum")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_averaged_spectrum: {}", e)))?;
        let count = func(handle, scan_numbers.as_ptr(), scan_numbers.len() as i32, masses.as_mut_ptr(), intensities.as_mut_ptr(), max_length);
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
fn get_instrument_count(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_instrument_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_count: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_instrument_count_of_type(handle: i64, device_type: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_instrument_count_of_type")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_count_of_type: {}", e)))?;
        Ok(func(handle, device_type))
    }
}

#[pyfunction]
fn is_open(handle: i64) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"is_open")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function is_open: {}", e)))?;
        Ok(func(handle) != 0)
    }
}

#[pyfunction]
fn is_error(handle: i64) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"is_error")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function is_error: {}", e)))?;
        Ok(func(handle) != 0)
    }
}

#[pyfunction]
fn in_acquisition(handle: i64) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"in_acquisition")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function in_acquisition: {}", e)))?;
        Ok(func(handle) != 0)
    }
}

#[pyfunction]
fn has_ms_data(handle: i64) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"has_ms_data")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function has_ms_data: {}", e)))?;
        Ok(func(handle) != 0)
    }
}

#[pyfunction]
fn close_raw_file(handle: i64) -> PyResult<()> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64)> = lib.get(b"close_raw_file")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function close_raw_file: {}", e)))?;
        func(handle);
        Ok(())
    }
}


#[pyfunction]
fn get_scan_filter_meta_filters(handle: i64, scan_number: i32) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut filters = vec![std::ptr::null_mut(); 32];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut *mut std::os::raw::c_char, i32) -> i32> = lib.get(b"get_scan_filter_meta_filters")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_meta_filters: {}", e)))?;
        let count = func(handle, scan_number, filters.as_mut_ptr(), 32);
        if count < 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_scan_filter_meta_filters failed"));
        }
        let actual_count = (count as usize).min(32);
        let mut result = Vec::with_capacity(actual_count);
        for i in 0..actual_count {
            if !filters[i].is_null() {
                let s = std::ffi::CStr::from_ptr(filters[i]).to_string_lossy().into_owned();
                result.push(s);
            }
        }
        Ok(result)
    }
}

#[pyfunction]
fn get_scan_filter_field_free_region(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_field_free_region")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_field_free_region: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_index_to_multiple_activation_index(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_index_to_multiple_activation_index")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_index_to_multiple_activation_index: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_compensation_volt_type(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_compensation_volt_type")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_compensation_volt_type: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_compensation_voltage_count(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_compensation_voltage_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_compensation_voltage_count: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_electron_capture_dissociation(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_electron_capture_dissociation")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_electron_capture_dissociation: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_electron_capture_dissociation_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_electron_capture_dissociation_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_electron_capture_dissociation_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_electron_transfer_dissociation(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_electron_transfer_dissociation")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_electron_transfer_dissociation: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_electron_transfer_dissociation_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_electron_transfer_dissociation_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_electron_transfer_dissociation_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_enhanced(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_enhanced")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_enhanced: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_higher_energy_cid(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_higher_energy_cid")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_higher_energy_cid: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_higher_energy_cid_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_higher_energy_cid_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_higher_energy_cid_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_multiple_photon_dissociation(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_multiple_photon_dissociation")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_multiple_photon_dissociation: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_multiple_photon_dissociation_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_multiple_photon_dissociation_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_multiple_photon_dissociation_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_pulsed_q_dissociation(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_pulsed_q_dissociation")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_pulsed_q_dissociation: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_pulsed_q_dissociation_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_pulsed_q_dissociation_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_pulsed_q_dissociation_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_source_fragmentation(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_source_fragmentation")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_source_fragmentation: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_source_fragmentation_info_valid(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_source_fragmentation_info_valid")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_source_fragmentation_info_valid: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_source_fragmentation_type(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_source_fragmentation_type")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_source_fragmentation_type: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_source_fragmentation_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_source_fragmentation_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_source_fragmentation_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_supplemental_activation(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_supplemental_activation")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_supplemental_activation: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_mass_precision(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_mass_precision")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_mass_precision: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_multi_notch(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_multi_notch")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_multi_notch: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_multiplex(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_multiplex")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_multiplex: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_unique_mass_count(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_unique_mass_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_unique_mass_count: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_param_a(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_param_a")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_param_a: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_param_b(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_param_b")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_param_b: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_param_f(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_param_f")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_param_f: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_param_r(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_param_r")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_param_r: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_param_v(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_param_v")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_param_v: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

/// Low-level NativeAOT bridge for Thermo Fisher RAW files.

#[pyfunction]
fn get_scan_filter_scan_mode(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_scan_mode")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_scan_mode: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_accurate_mass(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_accurate_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_accurate_mass: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_ionization_mode(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_ionization_mode")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_ionization_mode: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_lock(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_lock")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_lock: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_turbo_scan(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_turbo_scan")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_turbo_scan: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_corona(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_corona")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_corona: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_dependent(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_dependent")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_dependent: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_detector_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_filter_detector_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_detector_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_event_compensation_voltage(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_event_compensation_voltage")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_compensation_voltage: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_event_compensation_voltage_value(handle: i64, scan_number: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> f64> = lib.get(b"get_scan_event_compensation_voltage_value")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_compensation_voltage_value: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_event_ms_order(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_event_ms_order")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_ms_order: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_event_mass_count(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_event_mass_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_mass_count: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_event_precursor_mass(handle: i64, scan_number: i32, index: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, i32) -> f64> = lib.get(b"get_scan_event_precursor_mass")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_precursor_mass: {}", e)))?;
        Ok(func(handle, scan_number, index))
    }
}

#[pyfunction]
fn get_scan_event_activation_type(handle: i64, scan_number: i32, index: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, i32) -> i32> = lib.get(b"get_scan_event_activation_type")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_activation_type: {}", e)))?;
        Ok(func(handle, scan_number, index))
    }
}

#[pyfunction]
fn get_scan_event_collision_energy(handle: i64, scan_number: i32, index: i32) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, i32) -> f64> = lib.get(b"get_scan_event_collision_energy")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_event_collision_energy: {}", e)))?;
        Ok(func(handle, scan_number, index))
    }
}

#[pyfunction]
fn get_scan_stats(handle: i64, scan_number: i32) -> PyResult<Vec<f64>> {
    let lib = get_lib()?;
    let mut data = vec![0.0f64; 8];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut f64) -> i32> = lib.get(b"get_scan_stats")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_stats: {}", e)))?;
        let res = func(handle, scan_number, data.as_mut_ptr());
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_scan_stats failed")); }
        Ok(data)
    }
}

#[pyfunction]
fn get_scan_filter_ultra(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_ultra")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_ultra: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_wideband(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_wideband")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_wideband: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_polarity(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_polarity")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_polarity: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_ms_order(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_ms_order")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_ms_order: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_mass_analyzer(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_mass_analyzer")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_mass_analyzer: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_detector(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_detector")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_detector: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}

#[pyfunction]
fn get_scan_filter_scan_data(handle: i64, scan_number: i32) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32) -> i32> = lib.get(b"get_scan_filter_scan_data")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_scan_filter_scan_data: {}", e)))?;
        Ok(func(handle, scan_number))
    }
}


#[pyfunction]
fn get_trailer_extra_count(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_trailer_extra_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_trailer_extra_count: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_status_log_values(handle: i64, scan_number: i32) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut u8, i32) -> i32> = lib.get(b"get_status_log_values")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_status_log_values: {}", e)))?;
        let res = func(handle, scan_number, buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_status_log_values failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_status_log_header(handle: i64) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_status_log_header")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_status_log_header: {}", e)))?;
        let res = func(handle, buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_status_log_header failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_status_log_values_for_rt(handle: i64, rt: f64) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 16384];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, f64, *mut u8, i32) -> i32> = lib.get(b"get_status_log_values_for_rt")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_status_log_values_for_rt: {}", e)))?;
        let res = func(handle, rt, buffer.as_mut_ptr(), 16384);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_status_log_values_for_rt failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_status_log_count(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_status_log_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_status_log_count: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_trailer_extra_values(handle: i64, scan_number: i32) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut u8, i32) -> i32> = lib.get(b"get_trailer_extra_values")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_trailer_extra_values: {}", e)))?;
        let res = func(handle, scan_number, buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_trailer_extra_values failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_trailer_extra_header(handle: i64) -> PyResult<Vec<String>> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 8192];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_trailer_extra_header")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_trailer_extra_header: {}", e)))?;
        let res = func(handle, buffer.as_mut_ptr(), 8192);
        if res < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_trailer_extra_header failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        let s = String::from_utf8_lossy(&buffer[..end]);
        Ok(s.split('|').map(|x| x.to_string()).collect())
    }
}

#[pyfunction]
fn get_file_description(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_file_description")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_file_description: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_file_description failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_modified_date(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_modified_date")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_modified_date: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_modified_date failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_who_created_logon(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_who_created_logon")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_who_created_logon: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_who_created_logon failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_who_modified_id(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_who_modified_id")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_who_modified_id: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_who_modified_id failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_who_modified_logon(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_who_modified_logon")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_who_modified_logon: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_who_modified_logon failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_barcode(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_sample_barcode")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_barcode: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_barcode failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_id(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_sample_id")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_id: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_id failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_name(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_sample_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_name: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_vial(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 256];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_sample_vial")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_vial: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 256);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_vial failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_comment(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_sample_comment")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_comment: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_comment failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_axis_label_x(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_axis_label_x")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_axis_label_x: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_axis_label_x failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_axis_label_y(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_axis_label_y")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_axis_label_y: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_axis_label_y failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_flags(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_instrument_flags")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_flags: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_flags failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_instrument_units(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_instrument_units")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_units: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_instrument_is_valid(handle: i64) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_instrument_is_valid")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_is_valid: {}", e)))?;
        Ok(func(handle) != 0)
    }
}

#[pyfunction]
fn get_instrument_has_accurate_mass_precursors(handle: i64) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_instrument_has_accurate_mass_precursors")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_has_accurate_mass_precursors: {}", e)))?;
        Ok(func(handle) != 0)
    }
}

#[pyfunction]
fn get_instrument_is_tsq_quantum_file(handle: i64) -> PyResult<bool> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_instrument_is_tsq_quantum_file")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_is_tsq_quantum_file: {}", e)))?;
        Ok(func(handle) != 0)
    }
}

#[pyfunction]
fn select_instrument(handle: i64, device_type: i32, device_number: i32) -> PyResult<()> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, i32)> = lib.get(b"select_instrument")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function select_instrument: {}", e)))?;
        func(handle, device_type, device_number);
        Ok(())
    }
}

#[pyfunction]
fn get_instrument_method_count(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_instrument_method_count")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_method_count: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_instrument_method(handle: i64, index: i32) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 128 * 1024]; // 128KB buffer for method text
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, i32, *mut u8, i32) -> i32> = lib.get(b"get_instrument_method")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_instrument_method: {}", e)))?;
        let actual_len = func(handle, index, buffer.as_mut_ptr(), 128 * 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_instrument_method failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_autosampler_tray_index(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_autosampler_tray_index")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_autosampler_tray_index: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_autosampler_vial_index(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_autosampler_vial_index")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_autosampler_vial_index: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_autosampler_tray_name(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_autosampler_tray_name")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_autosampler_tray_name: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_autosampler_tray_name failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_autosampler_tray_shape(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_autosampler_tray_shape")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_autosampler_tray_shape: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_autosampler_vials_per_tray(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_autosampler_vials_per_tray")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_autosampler_vials_per_tray: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_autosampler_vials_per_tray_x(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_autosampler_vials_per_tray_x")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_autosampler_vials_per_tray_x: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_autosampler_vials_per_tray_y(handle: i64) -> PyResult<i32> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> i32> = lib.get(b"get_autosampler_vials_per_tray_y")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_autosampler_vials_per_tray_y: {}", e)))?;
        Ok(func(handle))
    }
}

#[pyfunction]
fn get_sample_instrument_method_file(handle: i64) -> PyResult<String> {
    let lib = get_lib()?;
    let mut buffer = vec![0u8; 1024];
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64, *mut u8, i32) -> i32> = lib.get(b"get_sample_instrument_method_file")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_instrument_method_file: {}", e)))?;
        let actual_len = func(handle, buffer.as_mut_ptr(), 1024);
        if actual_len < 0 { return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("get_sample_instrument_method_file failed")); }
        let end = buffer.iter().position(|&b| b == 0).unwrap_or(buffer.len());
        Ok(String::from_utf8_lossy(&buffer[..end]).into_owned())
    }
}

#[pyfunction]
fn get_sample_injection_volume(handle: i64) -> PyResult<f64> {
    let lib = get_lib()?;
    unsafe {
        let func: Symbol<unsafe extern "C" fn(i64) -> f64> = lib.get(b"get_sample_injection_volume")
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("get function get_sample_injection_volume: {}", e)))?;
        Ok(func(handle))
    }
}

#[pymodule]
fn native_fisher_py_backend(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(open_raw_file, m)?)?;
    m.add_function(wrap_pyfunction!(get_num_scans, m)?)?;
    m.add_function(wrap_pyfunction!(get_tune_data_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_rt, m)?)?;
    m.add_function(wrap_pyfunction!(get_spectrum, m)?)?;
    m.add_function(wrap_pyfunction!(is_centroid, m)?)?;
    m.add_function(wrap_pyfunction!(get_centroid_stream, m)?)?;
    m.add_function(wrap_pyfunction!(get_filters, m)?)?;
    m.add_function(wrap_pyfunction!(get_first_scan, m)?)?;
    m.add_function(wrap_pyfunction!(get_last_scan, m)?)?;
    m.add_function(wrap_pyfunction!(get_start_time, m)?)?;
    m.add_function(wrap_pyfunction!(get_end_time, m)?)?;
    m.add_function(wrap_pyfunction!(get_mass_resolution, m)?)?;
    m.add_function(wrap_pyfunction!(get_expected_runtime, m)?)?;
    m.add_function(wrap_pyfunction!(get_max_integrated_intensity, m)?)?;
    m.add_function(wrap_pyfunction!(get_max_intensity, m)?)?;
    m.add_function(wrap_pyfunction!(get_low_mass, m)?)?;
    m.add_function(wrap_pyfunction!(get_high_mass, m)?)?;
    m.add_function(wrap_pyfunction!(get_file_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_path, m)?)?;
    m.add_function(wrap_pyfunction!(get_ms_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_mass_analyzer, m)?)?;
    m.add_function(wrap_pyfunction!(get_precursor_mass, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_event_string, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_string, m)?)?;
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
    m.add_function(wrap_pyfunction!(get_creation_date, m)?)?;
    m.add_function(wrap_pyfunction!(set_dylib_path, m)?)?;
    m.add_function(wrap_pyfunction!(get_computer_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_creator_id, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_type, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_row_number, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_instrument_method_file, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_injection_volume, m)?)?;
    m.add_function(wrap_pyfunction!(get_sample_dilution_factor, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_model, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_serial_number, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_software_version, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_hardware_version, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_log_values, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_log_header, m)?)?;
    m.add_function(wrap_pyfunction!(get_status_log_values_for_rt, m)?)?;
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
    m.add_function(wrap_pyfunction!(get_scan_filter_compensation_volt_type, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_compensation_voltage_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_electron_capture_dissociation, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_electron_capture_dissociation_value, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_electron_transfer_dissociation, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_electron_transfer_dissociation_value, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_enhanced, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_higher_energy_cid, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_higher_energy_cid_value, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_multiple_photon_dissociation, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_multiple_photon_dissociation_value, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_pulsed_q_dissociation, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_pulsed_q_dissociation_value, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_source_fragmentation, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_source_fragmentation_info_valid, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_source_fragmentation_type, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_source_fragmentation_value, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_supplemental_activation, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_mass_precision, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_multi_notch, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_multiplex, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_unique_mass_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_param_a, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_param_b, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_param_f, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_param_r, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_param_v, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_meta_filters, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_field_free_region, m)?)?;
    m.add_function(wrap_pyfunction!(get_scan_filter_index_to_multiple_activation_index, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_method_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_instrument_method, m)?)?;
    m.add_function(wrap_pyfunction!(select_instrument, m)?)?;
    m.add_function(wrap_pyfunction!(get_autosampler_tray_index, m)?)?;
    m.add_function(wrap_pyfunction!(get_autosampler_vial_index, m)?)?;
    m.add_function(wrap_pyfunction!(get_autosampler_tray_name, m)?)?;
    m.add_function(wrap_pyfunction!(get_autosampler_tray_shape, m)?)?;
    m.add_function(wrap_pyfunction!(get_autosampler_vials_per_tray, m)?)?;
    m.add_function(wrap_pyfunction!(get_autosampler_vials_per_tray_x, m)?)?;
    m.add_function(wrap_pyfunction!(get_autosampler_vials_per_tray_y, m)?)?;
    m.add_function(wrap_pyfunction!(close_raw_file, m)?)?;
    Ok(())
}