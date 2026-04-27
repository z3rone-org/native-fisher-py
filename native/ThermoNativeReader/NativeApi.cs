using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using ThermoFisher.CommonCore.RawFileReader;
using ThermoFisher.CommonCore.Data;
using ThermoFisher.CommonCore.Data.Business;
using ThermoFisher.CommonCore.Data.Interfaces;
using ThermoFisher.CommonCore.Data.FilterEnums;
using Range = ThermoFisher.CommonCore.Data.Business.Range;
using System.Diagnostics.CodeAnalysis;

namespace ThermoNativeReader
{
    public static class NativeApi
    {
        private static Dictionary<long, IRawDataPlus> _openFiles = new Dictionary<long, IRawDataPlus>();
        private static long _nextHandle = 1;
        private static readonly object _lock = new object();
        private static IRawDataPlus? GetFile(long handle) { lock(_lock) { return _openFiles.TryGetValue(handle, out var f) ? f : null; } }

        private static unsafe int CopyString(string s, byte* buffer, int length) {
            if (buffer == null || length <= 0) return 0;
            var bytes = System.Text.Encoding.UTF8.GetBytes(s);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "open_raw_file")]
        public static unsafe long OpenRawFile(byte* pathPtr) {
            lock (_lock) {
                try {
                    if (pathPtr == null) return -1;
                    string path = Marshal.PtrToStringAnsi((IntPtr)pathPtr);
                    if (string.IsNullOrEmpty(path)) return -1;
                    var rawFile = (IRawDataPlus)RawFileReaderAdapter.FileFactory(path);
                    if (rawFile == null) return -1;
                    rawFile.SelectInstrument(Device.MS, 1);
                    long h = _nextHandle++; _openFiles[h] = rawFile; return h;
                } catch { return -1; }
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "close_raw_file")]
        public static void CloseRawFile(long handle) {
            lock (_lock) { if (_openFiles.TryGetValue(handle, out var f)) { _openFiles.Remove(handle); try { f.Dispose(); } catch {} } }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_num_scans")]
        public static int GetNumScans(long handle) { lock(_lock) { return GetFile(handle)?.RunHeader.LastSpectrum ?? 0; } }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_rt")]
        public static double GetScanRt(long handle, int scanNumber) { lock(_lock) { return GetFile(handle)?.RetentionTimeFromScanNumber(scanNumber) ?? -1.0; } }

        [UnmanagedCallersOnly(EntryPoint = "get_spectrum")]
        public static unsafe int GetSpectrum(long handle, int scanNumber, double* masses, double* intensities, int maxLength) { lock(_lock) { var f = GetFile(handle); if (f == null) return -1; var scan = f.GetSegmentedScanFromScanNumber(scanNumber, f.GetScanStatsForScanNumber(scanNumber)); if (scan == null) return 0; int count = Math.Min(scan.Positions.Length, maxLength); for (int i = 0; i < count; i++) { masses[i] = scan.Positions[i]; intensities[i] = scan.Intensities[i]; } return count; } }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_method_count")]
        public static int GetInstrumentMethodCount(long handle) { lock(_lock) { return GetFile(handle)?.InstrumentMethodsCount ?? 0; } }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_method")]
        public static unsafe int GetInstrumentMethod(long handle, int index, byte* buffer, int length) { lock(_lock) { var f = GetFile(handle); if (f == null) return 0; return CopyString(f.GetInstrumentMethod(index) ?? "", buffer, length); } }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_ms_order")]
        public static int GetScanEventMsOrder(long handle, int scanNumber) { lock(_lock) { return (int)(GetFile(handle)?.GetScanEventForScanNumber(scanNumber).MSOrder ?? 0); } }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_precursor_mass")]
        public static double GetScanEventPrecursorMass(long handle, int scanNumber, int index) { lock(_lock) { return GetFile(handle)?.GetScanEventForScanNumber(scanNumber).GetMass(index) ?? -1.0; } }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_collision_energy")]
        public static double GetScanEventCollisionEnergy(long handle, int scanNumber, int index) { lock(_lock) { return GetFile(handle)?.GetScanEventForScanNumber(scanNumber).GetEnergy(index) ?? -1.0; } }

        [UnmanagedCallersOnly(EntryPoint = "is_centroid")]
        public static int IsCentroid(long handle, int scanNumber) { return 0; }

        [UnmanagedCallersOnly(EntryPoint = "get_file_name")]
        public static unsafe int GetFileName(long handle, byte* buffer, int length) { lock(_lock) { return CopyString(GetFile(handle)?.FileName ?? "", buffer, length); } }

        // STUBS for all other methods from lib.rs/existing NativeApi.cs
        [UnmanagedCallersOnly(EntryPoint = "get_filters")]
        public static unsafe int GetFilters(long handle, byte** buffer, int maxLength) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_centroid_stream_full")]
        public static unsafe int GetCentroidStreamFull(long handle, int scanNumber, double* masses, double* intensities, double* baselines, double* noises, int* charges, double* noiseRes, int maxLength) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_meta_filters")]
        public static unsafe int GetScanFilterMetaFilters(long handle, int scanNumber, IntPtr* filters, int maxCount) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_path")]
        public static unsafe int GetPath(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_creation_date")]
        public static unsafe int GetCreationDate(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_computer_name")]
        public static unsafe int GetComputerName(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_creator_id")]
        public static unsafe int GetCreatorID(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_instrument_model")]
        public static unsafe int GetInstrumentModel(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_instrument_name")]
        public static unsafe int GetInstrumentName(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_instrument_serial_number")]
        public static unsafe int GetInstrumentSerialNumber(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_instrument_software_version")]
        public static unsafe int GetInstrumentSoftwareVersion(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_instrument_hardware_version")]
        public static unsafe int GetInstrumentHardwareVersion(long handle, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_ms_order")]
        public static int GetMsOrder(long handle, int scanNumber) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_mass_analyzer")]
        public static int GetMassAnalyzer(long handle, int scanNumber) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_precursor_mass")]
        public static double GetPrecursorMass(long handle, int scanNumber) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_string")]
        public static unsafe int GetScanEventString(long handle, int scanNumber, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_string")]
        public static unsafe int GetScanFilterString(long handle, int scanNumber, byte* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_scan_number_from_rt")]
        public static int GetScanNumberFromRt(long handle, double rt) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_ms2_filter_masses")]
        public static unsafe int GetMs2FilterMasses(long handle, double* buffer, int length) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_ms2_scan_number_from_rt")]
        public static int GetMs2ScanNumberFromRt(long handle, double rt, double precursor, double tolerance) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_ms1_scan_number_from_rt")]
        public static int GetMs1ScanNumberFromRt(long handle, double rt) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_chromatogram")]
        public static unsafe int GetChromatogram(long handle, int type, IntPtr filter, double* s, double* e, int count, int start, int end, double* x, double* y, int max) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_averaged_spectrum")]
        public static unsafe int GetAveragedSpectrum(long handle, int* scanNumbers, int num, double* masses, double* intensities, int max) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_instrument_count")]
        public static int GetInstrumentCount(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_instrument_count_of_type")]
        public static int GetInstrumentCountOfType(long handle, int type) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "is_open")]
        public static int IsOpen(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "is_error")]
        public static int IsError(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "in_acquisition")]
        public static int InAcquisition(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "has_ms_data")]
        public static int HasMsData(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "select_instrument")]
        public static void SelectInstrument(long handle, int device, int number) { }
        [UnmanagedCallersOnly(EntryPoint = "get_tune_data_count")]
        public static int GetTuneDataCount(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_first_scan")]
        public static int GetFirstScan(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_last_scan")]
        public static int GetLastScan(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_end_time")]
        public static double GetEndTime(long handle) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_start_time")]
        public static double GetStartTime(long handle) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_mass_resolution")]
        public static double GetMassResolution(long handle) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_expected_runtime")]
        public static double GetExpectedRuntime(long handle) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_max_integrated_intensity")]
        public static double GetMaxIntegratedIntensity(long handle) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_max_intensity")]
        public static int GetMaxIntensity(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_low_mass")]
        public static double GetLowMass(long handle) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_high_mass")]
        public static double GetHighMass(long handle) { return -1.0; }
        [UnmanagedCallersOnly(EntryPoint = "get_first_scan_number")]
        public static int GetFirstScanNumber(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_last_scan_number")]
        public static int GetLastScanNumber(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_sample_type")]
        public static int GetSampleType(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_sample_row_number")]
        public static int GetSampleRowNumber(long handle) { return 0; }
        [UnmanagedCallersOnly(EntryPoint = "get_sample_dilution_factor")]
        public static double GetSampleDilutionFactor(long handle) { return -1.0; }
    }
}
