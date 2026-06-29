from exceptiongroup import catch
import pytest
import os
import math
from native_fisher_py.raw_file import RawFile


def test_run_header_ms():
    raw_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "PXD006873_prec_range.raw")
    if not os.path.exists(raw_path) or os.path.getsize(raw_path) == 0:
        pytest.fail("Empty test file")

    raw_file = RawFile(raw_path)

    try:
        header = raw_file.run_header

        assert header.first_spectrum == 1
        assert header.last_spectrum == 237
        assert math.isclose(header.start_time, 5.0810132, rel_tol=1e-5)
        assert math.isclose(header.end_time, 25.670323, rel_tol=1e-5)
        assert math.isclose(header.expected_runtime, 35.0, rel_tol=1e-5)
        assert math.isclose(header.high_mass, 3000.0, rel_tol=1e-5)
        assert math.isclose(header.low_mass, 1500.0, rel_tol=1e-5)
        assert math.isclose(header.mass_resolution, 0.5, rel_tol=1e-5)
        assert math.isclose(header.max_integrated_intensity, 124167990.0, rel_tol=1e-5)
        assert header.max_intensity == 0
        assert header.spectra_count == 237
        assert header.status_log_count == 119
        assert header.trailer_extra_count == 61
        assert header.tune_data_count == 1

        with pytest.raises(NotImplementedError):
            _ = header.trailer_scan_event_count

        with pytest.raises(NotImplementedError):
            _ = header.tolerance_unit

        # Verify aliases
        assert raw_file.get_first_spectrum_number() == 1
        assert raw_file.get_last_spectrum_number() == 237
    finally:
        raw_file.close()


def test_run_header_uv():
    raw_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "MTBLS773_UV.raw")
    if not os.path.exists(raw_path) or os.path.getsize(raw_path) == 0:
        pytest.fail("Empty test file")

    raw_file = RawFile(raw_path)

    try:
        header = raw_file.run_header

        # UV files without selected instruments should safely return fallbacks
        assert header.first_spectrum == -1
        assert header.last_spectrum == -1
        assert header.start_time == -1.0
        assert header.end_time == -1.0
        assert header.expected_runtime == 0.0
        assert header.high_mass == 0.0
        assert header.low_mass == 0.0
        assert header.mass_resolution == 0.0
        assert header.max_integrated_intensity == 0.0
        assert header.max_intensity == 0
        assert header.spectra_count == -1
        assert header.status_log_count == -1
        assert header.trailer_extra_count == -1
        assert header.tune_data_count == -1

        with pytest.raises(NotImplementedError):
            _ = header.trailer_scan_event_count

        with pytest.raises(NotImplementedError):
            _ = header.tolerance_unit

        # Verify aliases return fallbacks safely
        assert raw_file.get_first_spectrum_number() == -1
        assert raw_file.get_last_spectrum_number() == -1
    except Exception as e:
        pytest.fail(e)
    finally:
        raw_file.close()
