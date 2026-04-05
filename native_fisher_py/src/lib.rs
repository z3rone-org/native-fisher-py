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
    
    // 1. Environment variable override
    if let Ok(path) = std::env::var("THERMO_NATIVE_LIB") {
        if std::path::Path::new(&path).exists() {
             let lib = unsafe {
                 Library::new(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to load override dylib: {}", e)))?
             };
             let _ = LIB.set(lib);
             return Ok(LIB.get().unwrap());
        }
    }

    // 2. Local development path (hardcoded as fallback)
    let dev_path = "/Users/falk/workspaces/python/thermo-raw-aot/native/ThermoNativeReader/bin/Release/net8.0/osx-arm64/publish/ThermoNativeReader.dylib";
    
    // 3. Runtime discovery (same directory as the shared library)
    // We try many common locations
    let lib_name = if cfg!(target_os = "windows") {
        "ThermoNativeReader.dll"
    } else if cfg!(target_os = "macos") {
        "ThermoNativeReader.dylib"
    } else {
        "ThermoNativeReader.so"
    };

    // Use current executable's directory or the parent directory’s publish folder
    let search_paths = vec![
        std::path::PathBuf::from(dev_path),
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
    
    Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Dylib not found. Please set THERMO_NATIVE_LIB."))
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
    m.add_function(wrap_pyfunction!(get_end_time, m)?)?;
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
    m.add_function(wrap_pyfunction!(close_raw_file, m)?)?;
    Ok(())
}
