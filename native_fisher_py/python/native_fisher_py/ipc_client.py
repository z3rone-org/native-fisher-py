import subprocess
import struct
import os
import sys
import threading
import logging
import atexit
import numpy as np
from typing import List, Tuple, Any, Optional

logger = logging.getLogger(__name__)

def _cleanup_server(client_instance):
    if client_instance and client_instance.process:
        try:
            client_instance.process.terminate()
            client_instance.process.wait(timeout=2)
        except:
            try: client_instance.process.kill()
            except: pass

class ThermoIPCClient:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.process = None
        self.reader = None
        self.writer = None
        self._lock = threading.Lock()
        atexit.register(_cleanup_server, self)
        logger.debug("Server process started and registered for cleanup")
        self._start_server()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = ThermoIPCClient()
            return cls._instance

    def _start_server(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        native_root = os.path.join(base_dir, "native")
        bin_paths = [
            os.path.join(native_root, "ThermoNativeReader/bin/Release/net8.0/osx-x64/publish/ThermoNativeReader"),
        ]
        
        self.bin_path = next((p for p in bin_paths if os.path.exists(p)), None)
        if not self.bin_path:
             raise FileNotFoundError(f"ThermoNativeReader binary not found in {bin_paths}")

        cmd = [self.bin_path]
        if sys.platform == "darwin" and "osx-x64" in self.bin_path:
            cmd = ["arch", "-x86_64"] + cmd

        logger.debug(f"Starting server: {' '.join(cmd)}")
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
        self.writer = self.process.stdin
        self.reader = self.process.stdout

    def _send_command(self, cmd: int, payload: bytes = b""):
        with self._lock:
            # Length: 1 (cmd) + len(payload)
            full_len = 1 + len(payload)
            print(f"Sending command 0x{cmd:02X} (len {full_len})", file=sys.stderr)
            try:
                self.writer.write(struct.pack("<IB", full_len, cmd))
                self.writer.write(payload)
                self.writer.flush()
            except Exception as e:
                print(f"Error writing to server: {e}", file=sys.stderr)
                raise

            # Read response length
            res_len_bytes = self.reader.read(4)
            if not res_len_bytes:
                raise EOFError("Server disconnected")
            res_len = struct.unpack("<I", res_len_bytes)[0]
            
            # Read status
            status_byte = self.reader.read(1)
            if not status_byte:
                raise EOFError("Server disconnected during status read")
            status = status_byte[0]
            
            data = self.reader.read(res_len - 1)
            
            if status != 0x00:
                error_msg = data.decode("utf-8", errors="replace")
                raise RuntimeError(f"Server error: {error_msg}")
            
            return data

    def open_raw_file(self, path: str) -> int:
        path_bytes = path.encode("utf-8")
        payload = struct.pack("<I", len(path_bytes)) + path_bytes
        data = self._send_command(0x01, payload)
        return struct.unpack("<q", data)[0]

    def close_raw_file(self, handle: int):
        self._send_command(0x02, struct.pack("<q", handle))

    def get_num_scans(self, handle: int) -> int:
        data = self._send_command(0x05, struct.pack("<q", handle))
        return struct.unpack("<i", data)[0]

    def get_scan_rt(self, handle: int, scan: int) -> float:
        data = self._send_command(0x06, struct.pack("<qi", handle, scan))
        return struct.unpack("<d", data)[0]

    def get_scan_number_from_rt(self, handle: int, rt: float) -> int:
        data = self._send_command(0x07, struct.pack("<qd", handle, rt))
        return struct.unpack("<i", data)[0]

    def get_scan_stats(self, handle: int, scan: int) -> Tuple:
        data = self._send_command(0x03, struct.pack("<qi", handle, scan))
        # StartTime (d), LowMass (d), HighMass (d), TIC (d), BasePeakMass (d), BasePeakIntensity (d), PacketCount (i), IsCentroidScan (b)
        # Format: dddddd i ?
        # Size: 8*6 + 4 + 1 = 53
        return struct.unpack("<dddddd i ?", data)

    def get_centroid_stream(self, handle: int, scan: int) -> Tuple:
        data = self._send_command(0x04, struct.pack("<qi", handle, scan))
        count = struct.unpack("<i", data[:4])[0]
        offset = 4
        masses = np.frombuffer(data[offset:offset + count*8], dtype=np.float64).copy()
        offset += count*8
        intensities = np.frombuffer(data[offset:offset + count*8], dtype=np.float64).copy()
        offset += count*8
        bp_noise, bp_res = struct.unpack("<dd", data[offset:offset+16])
        
        # We need to provide dummy baselines, noises, charges for parity with original FFI
        baselines = np.zeros_like(masses)
        noises = np.zeros_like(masses)
        charges = np.zeros_like(masses, dtype=np.int32)
        
        return (list(masses), list(intensities), list(baselines), list(noises), list(charges), bp_noise, bp_res)

    def get_scan_event_string(self, handle: int, scan: int) -> str:
        data = self._send_command(0x08, struct.pack("<qi", handle, scan))
        s_len = struct.unpack("<i", data[:4])[0]
        return data[4:4+s_len].decode("utf-8")

    def get_file_header(self, handle: int) -> Tuple[str, str]:
        data = self._send_command(0x09, struct.pack("<q", handle))
        fn_len = struct.unpack("<i", data[:4])[0]
        fn = data[4:4+fn_len].decode("utf-8")
        offset = 4 + fn_len
        cd_len = struct.unpack("<i", data[offset:offset+4])[0]
        cd = data[offset+4:offset+4+cd_len].decode("utf-8")
        return fn, cd

    def get_instrument_count(self, handle: int) -> int:
        data = self._send_command(0x0A, struct.pack("<q", handle))
        return struct.unpack("<i", data)[0]

    def get_ms_order(self, handle: int, scan: int) -> int:
        data = self._send_command(0x0B, struct.pack("<qi", handle, scan))
        return struct.unpack("<i", data)[0]

    def get_precursor_mass(self, handle: int, scan: int) -> float:
        data = self._send_command(0x0C, struct.pack("<qi", handle, scan))
        return struct.unpack("<d", data)[0]

    def get_end_time(self, handle: int) -> float:
        data = self._send_command(0x0D, struct.pack("<q", handle))
        return struct.unpack("<d", data)[0]

    def get_first_scan(self, handle: int) -> int:
        data = self._send_command(0x0E, struct.pack("<q", handle))
        return struct.unpack("<i", data)[0]

    def get_last_scan(self, handle: int) -> int:
        data = self._send_command(0x0F, struct.pack("<q", handle))
        return struct.unpack("<i", data)[0]

    def get_ms1_scan_number_from_rt(self, handle: int, rt: float) -> int:
        data = self._send_command(0x10, struct.pack("<qd", handle, rt))
        return struct.unpack("<i", data)[0]

    def get_ms2_scan_number_from_rt(self, handle: int, rt: float, pmz: float, tol: float) -> int:
        data = self._send_command(0x11, struct.pack("<qddd", handle, rt, pmz, tol))
        return struct.unpack("<i", data)[0]

    def get_chromatogram(self, handle: int, trace_type: int, filter_str: str, lows: List[float], highs: List[float], start_scan: int, end_scan: int) -> Tuple[List[float], List[float]]:
        filter_bytes = filter_str.encode("utf-8")
        payload = struct.pack("<qiI", handle, trace_type, len(filter_bytes)) + filter_bytes
        payload += struct.pack("<I", len(lows))
        for l, h in zip(lows, highs): payload += struct.pack("<dd", l, h)
        payload += struct.pack("<ii", start_scan, end_scan)
        
        data = self._send_command(0x12, payload)
        count = struct.unpack("<i", data[:4])[0]
        if count == 0: return [], []
        times = list(np.frombuffer(data[4:4+count*8], dtype=np.float64))
        intensities = list(np.frombuffer(data[4+count*8:4+count*16], dtype=np.float64))
        return times, intensities

    def get_averaged_spectrum(self, handle: int, scans: List[int]) -> Tuple[List[float], List[float]]:
        payload = struct.pack("<qi", handle, len(scans))
        for s in scans: payload += struct.pack("<i", s)
        
        data = self._send_command(0x13, payload)
        count = struct.unpack("<i", data[:4])[0]
        if count == 0: return [], []
        masses = list(np.frombuffer(data[4:4+count*8], dtype=np.float64))
        intensities = list(np.frombuffer(data[4+count*8:4+count*16], dtype=np.float64))
        return masses, intensities

# Global functions for redirection
def open_raw_file(path: str) -> int:
    return ThermoIPCClient.get_instance().open_raw_file(path)

def close_raw_file(handle: int):
    ThermoIPCClient.get_instance().close_raw_file(handle)

def get_num_scans(handle: int) -> int:
    return ThermoIPCClient.get_instance().get_num_scans(handle)

def get_first_scan(handle: int) -> int:
    return ThermoIPCClient.get_instance().get_first_scan(handle)

def get_last_scan(handle: int) -> int:
    return ThermoIPCClient.get_instance().get_last_scan(handle)

def get_scan_rt(handle: int, scan: int) -> float:
    return ThermoIPCClient.get_instance().get_scan_rt(handle, scan)

def get_scan_number_from_rt(handle: int, rt: float) -> int:
    return ThermoIPCClient.get_instance().get_scan_number_from_rt(handle, rt)

def get_scan_stats(handle: int, scan: int) -> Tuple:
    return ThermoIPCClient.get_instance().get_scan_stats(handle, scan)

def get_centroid_stream(handle: int, scan: int, max_len: int) -> Tuple:
    return ThermoIPCClient.get_instance().get_centroid_stream(handle, scan)

def get_scan_event_string(handle: int, scan: int) -> str:
    return ThermoIPCClient.get_instance().get_scan_event_string(handle, scan)

def get_file_name(handle: int) -> str:
    return ThermoIPCClient.get_instance().get_file_header(handle)[0]

def get_creation_date(handle: int) -> str:
    return ThermoIPCClient.get_instance().get_file_header(handle)[1]

def get_instrument_count(handle: int) -> int:
    return ThermoIPCClient.get_instance().get_instrument_count(handle)

def get_ms_order(handle: int, scan: int) -> int:
    return ThermoIPCClient.get_instance().get_ms_order(handle, scan)

def get_precursor_mass(handle: int, scan: int) -> float:
    return ThermoIPCClient.get_instance().get_precursor_mass(handle, scan)

# Add stubs for missing functions to avoid ImportErrors
def select_instrument(handle, device, num): pass
def get_instrument_method_count(handle): return 0
def get_instrument_method(handle, index): return ""
def is_centroid(handle, scan): return get_scan_stats(handle, scan)[7]
def get_computer_name(handle): return "Unknown"
def get_creator_id(handle): return "Unknown"
def is_open(handle): return True
def is_error(handle): return False
def in_acquisition(handle): return False
def get_status_log_values(handle, scan): return []
def get_instrument_count_of_type(handle, type): return 1
def get_trailer_extra_header(handle): return []
def get_trailer_extra_values(handle, scan): return []
def get_status_log_header(handle): return []
def get_status_log_count(handle): return 0
def get_status_log_values_for_rt(handle, rt): return []
def get_tune_data_count(handle): return 0
def get_filters(): return []
def has_ms_data(handle): return True
def get_end_time(handle):
    return ThermoIPCClient.get_instance().get_end_time(handle)

def get_averaged_spectrum(handle, scans, max_len):
    return ThermoIPCClient.get_instance().get_averaged_spectrum(handle, scans)

def get_ms1_scan_number_from_rt(handle, rt):
    return ThermoIPCClient.get_instance().get_ms1_scan_number_from_rt(handle, rt)

def get_ms2_scan_number_from_rt(handle, rt, pmz, tol):
    return ThermoIPCClient.get_instance().get_ms2_scan_number_from_rt(handle, rt, pmz, tol)

def get_spectrum(handle, scan, max_len):
    return ThermoIPCClient.get_instance().get_centroid_stream(handle, scan)[:2]

def get_chromatogram(handle, trace_type, filter_str, lows, highs, start_scan, end_scan, max_len):
    return ThermoIPCClient.get_instance().get_chromatogram(handle, trace_type, filter_str, lows, highs, start_scan, end_scan)
