using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Reflection;
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
        class FileState
        {
            public IRawDataPlus? RawFile;
            public int CachedMethodCount = 0;
            public int CachedSampleType = 0;
            public int CachedSampleRow = 0;
            public double CachedSampleDilution = 0.0;
        }

        private static ConcurrentDictionary<int, FileState> _files = new ConcurrentDictionary<int, FileState>();
        private static int _nextHandle = 1;

        private static IRawDataPlus? GetFile(int handle)
        {
            if (_files.TryGetValue(handle, out var state))
                return state.RawFile;
            return null;
        }
        private static FileState? GetState(int handle)
        {
            if (_files.TryGetValue(handle, out var state))
                return state;
            return null;
        }


        private static string SafeGetFilterString(IScanFilter filter)
        {
            if (filter == null)
                return "";
            try
            {
                return filter.ToString();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Filter.ToString() failed: {ex.Message}");
                return "FILTER_ERROR";
            }
        }

        static NativeApi()
        {
            // Force compiler to keep these types
            var t = typeof(ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType);
            var t2 = typeof(ThermoFisher.CommonCore.Data.Business.CentroidStream);
            var t3 = typeof(ThermoFisher.CommonCore.Data.Interfaces.IScanFilter);
        }

        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType))]
        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.IScanFilter))]
        [UnmanagedCallersOnly(EntryPoint = "open_raw_file")]
        public static unsafe int OpenRawFile(byte* pathPtr)
        {
            try
            {
                if (pathPtr == null)
                    return -1;
                string? path = System.Runtime.InteropServices.Marshal.PtrToStringUTF8((IntPtr)pathPtr);
                if (string.IsNullOrEmpty(path))
                    return -1;

                var rawFile = (IRawDataPlus)RawFileReaderAdapter.FileFactory(path);
                if (rawFile == null)
                    return -1;

                var state = new FileState { RawFile = rawFile };

                try
                {
                    state.CachedMethodCount = rawFile.InstrumentMethodsCount;
                }
                catch { state.CachedMethodCount = 0; }
                try
                {
                    state.CachedSampleType = (int)rawFile.SampleInformation.SampleType;
                }
                catch { state.CachedSampleType = 0; }
                try
                {
                    state.CachedSampleRow = rawFile.SampleInformation.RowNumber;
                }
                catch { state.CachedSampleRow = 0; }
                try
                {
                    state.CachedSampleDilution = rawFile.SampleInformation.DilutionFactor;
                }
                catch { state.CachedSampleDilution = 0.0; }

                try {
                    rawFile.SelectInstrument(Device.MS, 1);
                } catch {
                    try { rawFile.SelectInstrument(Device.UV, 1); } catch { }
                }
                int handle = System.Threading.Interlocked.Increment(ref _nextHandle);
                _files[handle] = state;
                return handle;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in OpenRawFile: " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_num_scans")]
        public static int GetNumScans(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1;
            return _rawFile.RunHeader.LastSpectrum;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_rt")]
        public static double GetScanRT(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanRT: RawFile handle is invalid or null.");
                return -1.0;
            }
            return _rawFile.RetentionTimeFromScanNumber(scanNumber);
        }

        [UnmanagedCallersOnly(EntryPoint = "is_centroid")]
        public static int IsCentroid(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in IsCentroid: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                var scanStatistics = _rawFile.GetScanStatsForScanNumber(scanNumber);
                if (scanStatistics == null)
                    return 0;
                return scanStatistics.IsCentroidScan ? 1 : 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in IsCentroid (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_spectrum")]
        public static unsafe int GetSpectrum(int handle, int scanNumber, double* masses, double* intensities, int maxLength)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in IsCentroid: RawFile handle is invalid or null.");
                return -1;
            }

            try
            {
                var scanStatistics = _rawFile.GetScanStatsForScanNumber(scanNumber);
                var scan = _rawFile.GetSegmentedScanFromScanNumber(scanNumber, scanStatistics);
                if (scan == null)
                {
                    return -2;
                }
                if (scan.Positions == null)
                {
                    return -3;
                }
                if (scan.Intensities == null)
                {
                    return -4;
                }
                if (scan.Positions.Length == 0)
                {
                    return -5;
                }

                int count = Math.Min(scan.Positions.Length, maxLength);
                for (int i = 0; i < count; i++)
                {
                    masses[i] = scan.Positions[i];
                    intensities[i] = scan.Intensities[i];
                }
                return count;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetSpectrum: " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_centroid_stream_full")]
        public static unsafe int GetCentroidStreamFull(int handle, int scanNumber, double* masses, double* intensities, double* baselines, double* noises, int* charges, double* noiseRes, int maxLength)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in IsCentroid: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var scan = _rawFile.GetCentroidStream(scanNumber, false);
                if (scan == null)
                    return 0;

                int count = Math.Min(scan.Length, maxLength);
                for (int i = 0; i < count; i++)
                {
                    if (masses != null && scan.Masses != null && i < scan.Masses.Length)
                        masses[i] = scan.Masses[i];
                    if (intensities != null && scan.Intensities != null && i < scan.Intensities.Length)
                        intensities[i] = scan.Intensities[i];
                    if (baselines != null && scan.Baselines != null && i < scan.Baselines.Length)
                        baselines[i] = scan.Baselines[i];
                    if (noises != null && scan.Noises != null && i < scan.Noises.Length)
                        noises[i] = scan.Noises[i];
                    if (charges != null && scan.Charges != null && i < scan.Charges.Length)
                        charges[i] = (int)scan.Charges[i];
                }

                if (noiseRes != null)
                {
                    noiseRes[0] = scan.BasePeakNoise;
                    noiseRes[1] = scan.BasePeakResolution;
                }

                return count;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Native Error in GetCentroidStreamFull: {ex.Message}");
                return -1;
            }
        }

        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType))]
        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.IScanFilter))]
        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_meta_filters")]
        public static unsafe int GetScanFilterMetaFilters(int handle, int scanNumber, IntPtr* filters, int maxCount)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in IsCentroid: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var filter = _rawFile.GetFilterForScanNumber(scanNumber);
                if (filter == null)
                    return 0;
                var prop = filter.GetType().GetProperty("MetaFilters");
                if (prop == null)
                    return 0;
                var metaFiltersObj = prop.GetValue(filter) as System.Collections.IEnumerable;
                if (metaFiltersObj == null)
                    return 0;

                var metaList = new List<string>();
                foreach (var mf in metaFiltersObj)
                {
                    if (mf != null)
                        metaList.Add(mf.ToString() ?? "");
                }
                int count = Math.Min(metaList.Count, maxCount);
                for (int i = 0; i < count; i++)
                {
                    filters[i] = Marshal.StringToHGlobalAnsi(metaList[i]);
                }
                return metaList.Count;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in IsCentroid (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_filters")]
        public static unsafe int GetFilters(int handle, IntPtr* filters, int maxCount)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in IsCentroid: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var filterList = _rawFile.GetFilters().ToArray();
                int count = Math.Min(filterList.Length, maxCount);
                for (int i = 0; i < count; i++)
                {
                    filters[i] = Marshal.StringToHGlobalAnsi(SafeGetFilterString(filterList[i]));
                }
                return filterList.Length;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in get_filters: {ex}");
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_first_scan")]
        public static int GetFirstScan(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1;
            return _rawFile.RunHeader.FirstSpectrum;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_last_scan")]
        public static int GetLastScan(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1;
            return _rawFile.RunHeader.LastSpectrum;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_end_time")]
        public static double GetEndTime(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1.0;
            return _rawFile.RunHeader.EndTime;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_start_time")]
        public static double GetStartTime(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1.0;
            return _rawFile.RunHeader.StartTime;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_mass_resolution")]
        public static double GetMassResolution(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1.0;
            return _rawFile.RunHeader.MassResolution;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_expected_runtime")]
        public static double GetExpectedRuntime(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1.0;
            return _rawFile.RunHeader.ExpectedRuntime;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_max_integrated_intensity")]
        public static double GetMaxIntegratedIntensity(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1.0;
            return _rawFile.RunHeader.MaxIntegratedIntensity;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_max_intensity")]
        public static int GetMaxIntensity(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1;
            return _rawFile.RunHeader.MaxIntensity;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_low_mass")]
        public static double GetLowMass(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1.0;
            return _rawFile.RunHeader.LowMass;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_high_mass")]
        public static double GetHighMass(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null || _rawFile.RunHeader == null)
                return -1.0;
            return _rawFile.RunHeader.HighMass;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_file_name")]
        public static unsafe int GetFileName(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetHighMass: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.FileName ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_path")]
        public static unsafe int GetPath(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetHighMass: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.Path ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_tune_data_count")]
        public static int GetTuneDataCount(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            return _rawFile.GetTuneDataCount();
        }

        [UnmanagedCallersOnly(EntryPoint = "get_creation_date")]
        public static unsafe int GetCreationDate(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.CreationDate.ToString("o");
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_computer_name")]
        public static unsafe int GetComputerName(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.ComputerName ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_creator_id")]
        public static unsafe int GetCreatorID(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.CreatorId ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_model")]
        public static unsafe int GetInstrumentModel(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.Model ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_name")]
        public static unsafe int GetInstrumentName(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.Name ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_serial_number")]
        public static unsafe int GetInstrumentSerialNumber(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.SerialNumber ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_software_version")]
        public static unsafe int GetInstrumentSoftwareVersion(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.SoftwareVersion ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_hardware_version")]
        public static unsafe int GetInstrumentHardwareVersion(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.HardwareVersion ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_axis_label_x")]
        public static unsafe int GetInstrumentAxisLabelX(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.AxisLabelX ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_axis_label_y")]
        public static unsafe int GetInstrumentAxisLabelY(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.AxisLabelY ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_flags")]
        public static unsafe int GetInstrumentFlags(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTuneDataCount: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            var str = data?.Flags ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_units")]
        public static int GetInstrumentUnits(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentUnits: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            return data != null ? (int)data.Units : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_is_valid")]
        public static int GetInstrumentIsValid(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsValid: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            return data != null && data.IsValid ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_has_accurate_mass_precursors")]
        public static int GetInstrumentHasAccurateMassPrecursors(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentHasAccurateMassPrecursors: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            return data != null && data.HasAccurateMassPrecursors ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_is_tsq_quantum_file")]
        public static int GetInstrumentIsTsqQuantumFile(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var data = _rawFile.GetInstrumentData();
            return data != null && data.IsTsqQuantumFile() ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_file_description")]
        public static unsafe int GetFileDescription(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.FileHeader.FileDescription ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_modified_date")]
        public static unsafe int GetModifiedDate(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.FileHeader.ModifiedDate.ToString() ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_created_logon")]
        public static unsafe int GetWhoCreatedLogon(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.FileHeader.WhoCreatedLogon ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_modified_id")]
        public static unsafe int GetWhoModifiedId(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.FileHeader.WhoModifiedId ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_modified_logon")]
        public static unsafe int GetWhoModifiedLogon(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.FileHeader.WhoModifiedLogon ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_barcode")]
        public static unsafe int GetSampleBarcode(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.SampleInformation.Barcode ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_id")]
        public static unsafe int GetSampleId(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.SampleInformation.SampleId ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_name")]
        public static unsafe int GetSampleName(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.SampleInformation.SampleName ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_vial")]
        public static unsafe int GetSampleVial(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.SampleInformation.Vial ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_comment")]
        public static unsafe int GetSampleComment(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentIsTsqQuantumFile: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.SampleInformation.Comment ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_type")]
        public static int GetSampleType(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetSampleType: RawFile handle is invalid or null.");
                return 0;
            }
            return (int)_rawFile.SampleInformation.SampleType;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_row_number")]
        public static int GetSampleRowNumber(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetSampleRowNumber: RawFile handle is invalid or null.");
                return 0;
            }
            return _rawFile.SampleInformation.RowNumber;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_dilution_factor")]
        public static double GetSampleDilutionFactor(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetSampleDilutionFactor: RawFile handle is invalid or null.");
                return 1.0;
            }
            return _rawFile.SampleInformation.DilutionFactor;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_injection_volume")]
        public static double GetSampleInjectionVolume(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetSampleInjectionVolume: RawFile handle is invalid or null.");
                return 0.0;
            }
            return _rawFile.SampleInformation.InjectionVolume;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_instrument_method_file")]
        public static unsafe int GetSampleInstrumentMethodFile(int handle, byte* buffer, int length)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetSampleInjectionVolume: RawFile handle is invalid or null.");
                return -1;
            }
            var str = _rawFile.SampleInformation.InstrumentMethodFile ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++)
                buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms_order")]
        public static int GetMsOrder(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetMsOrder: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                return (int)scanEvent.MSOrder;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetMsOrder (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_mass_analyzer")]
        public static int GetMassAnalyzer(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetMassAnalyzer: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                return (int)scanEvent.MassAnalyzer;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetMassAnalyzer (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_precursor_mass")]
        public static double GetPrecursorMass(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetPrecursorMass: RawFile handle is invalid or null.");
                return -1.0;
            }
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                if (scanEvent.MSOrder == MSOrderType.Ms)
                    return 0.0;
                return scanEvent.GetReaction(0).PrecursorMass;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetPrecursorMass (fallback -1.0): " + ex.Message);
                return -1.0;
            }
        }

        private static string SafeGetScanEventString(IScanEvent scanEvent)
        {
            if (scanEvent == null)
                return "";
            // We AVOID scanEvent.ToString() because it triggers the Thermo.FilterStringTokens static constructor
            // which fails in AOT due to GetEnumValues[T] reflection.
            try
            {
                var polarity = scanEvent.Polarity == PolarityType.Positive ? "+" : (scanEvent.Polarity == PolarityType.Negative ? "-" : "");
                var analyzer = ((int)scanEvent.MassAnalyzer).ToString();
                var msOrder = ((int)scanEvent.MSOrder).ToString();
                return $"{analyzer} {polarity} ms{msOrder}";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Manual scan event formatting failed: {ex.Message}");
                return "MS_ORDER_ONLY";
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_string")]
        public static unsafe int GetScanEventString(int handle, int scanNumber, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetPrecursorMass: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                if (scanEvent == null)
                    return 0;

                string eventStr = SafeGetScanEventString(scanEvent);

                if (string.IsNullOrEmpty(eventStr))
                    return 0;

                var bytes = System.Text.Encoding.UTF8.GetBytes(eventStr);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++)
                {
                    buffer[i] = bytes[i];
                }
                buffer[count] = 0; // Null terminator
                return bytes.Length;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Fatal error in get_scan_event_string: {ex}");
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms2_filter_masses")]
        public static unsafe int GetMs2FilterMasses(int handle, double* buffer, int maxSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetPrecursorMass: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var precursors = new HashSet<double>();
                for (int i = _rawFile.RunHeader.FirstSpectrum; i <= _rawFile.RunHeader.LastSpectrum; i++)
                {
                    var scanEvent = _rawFile.GetScanEventForScanNumber(i);
                    if (scanEvent.MSOrder > MSOrderType.Ms)
                    {
                        precursors.Add(scanEvent.GetReaction(0).PrecursorMass);
                    }
                }

                var sorted = precursors.OrderBy(x => x).ToList();
                int count = Math.Min(sorted.Count, maxSize);
                for (int i = 0; i < count; i++)
                {
                    buffer[i] = sorted[i];
                }
                return count;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in get_ms2_filter_masses: {ex}");
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_string")]
        public static unsafe int GetScanFilterString(int handle, int scanNumber, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetPrecursorMass: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                var filter = _rawFile.GetFilterForScanNumber(scanNumber);
                if (filter == null)
                    return 0;

                string filterStr = SafeGetFilterString(filter);

                if (string.IsNullOrEmpty(filterStr))
                    return 0;

                var bytes = System.Text.Encoding.UTF8.GetBytes(filterStr);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++)
                {
                    buffer[i] = bytes[i];
                }
                buffer[count] = 0;
                return count;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetPrecursorMass: " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_number_from_rt")]
        public static int GetScanNumberFromRT(int handle, double rt)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanNumberFromRT: RawFile handle is invalid or null.");
                return -1;
            }
            return _rawFile.ScanNumberFromRetentionTime(rt);
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms2_scan_number_from_rt")]
        public static int GetMs2ScanNumberFromRT(int handle, double rt, double precursorMz, double tolerancePpm)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetMs2ScanNumberFromRT: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                int bestScan = -1;
                double minDistance = double.MaxValue;

                for (int i = _rawFile.RunHeader.FirstSpectrum; i <= _rawFile.RunHeader.LastSpectrum; i++)
                {
                    var scanEvent = _rawFile.GetScanEventForScanNumber(i);
                    if (scanEvent.MSOrder > MSOrderType.Ms)
                    {
                        double pMz = scanEvent.GetReaction(0).PrecursorMass;
                        bool match = false;
                        if (precursorMz <= 0)
                        {
                            match = true;
                        }
                        else
                        {
                            match = Math.Abs(pMz - precursorMz) < 0.01;
                        }

                        if (match)
                        {
                            double scanRt = _rawFile.RetentionTimeFromScanNumber(i);
                            double dist = Math.Abs(scanRt - rt);
                            if (dist < minDistance)
                            {
                                minDistance = dist;
                                bestScan = i;
                            }
                        }
                    }
                }
                return bestScan;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetMs2ScanNumberFromRT (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_chromatogram")]
        public static unsafe int GetChromatogram(int handle, int traceType, IntPtr filterPtr, double* massRangesStart, double* massRangesEnd, int massRangeCount, int startScan, int endScan, double* times, double* intensities, int maxLength)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetMs2ScanNumberFromRT: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                string filter = Marshal.PtrToStringAnsi(filterPtr) ?? "";
                var settings = new ChromatogramTraceSettings((TraceType)traceType) { Filter = filter };

                if (massRangeCount > 0)
                {
                    settings.MassRangeCount = massRangeCount;
                    for (int i = 0; i < massRangeCount; i++)
                    {
                        settings.SetMassRange(i, new Range(massRangesStart[i], massRangesEnd[i]));
                    }
                }

                var data = _rawFile.GetChromatogramData(new[] { settings }, startScan, endScan);

                if (data == null || data.PositionsArray == null || data.PositionsArray.Length == 0)
                {
                    // Console.WriteLine($"GetChromatogramData returned no results for type={traceType}, filter='{filter}', range={startScan}-{endScan}");
                    return 0;
                }

                int count = Math.Min(data.PositionsArray[0].Length, maxLength);
                for (int i = 0; i < count; i++)
                {
                    times[i] = data.PositionsArray[0][i];
                    intensities[i] = data.IntensitiesArray[0][i];
                }
                return data.PositionsArray[0].Length;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in get_chromatogram: {ex}");
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms1_scan_number_from_rt")]
        public static int GetMs1ScanNumberFromRT(int handle, double rt)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetMs1ScanNumberFromRT: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                int scan = _rawFile.ScanNumberFromRetentionTime(rt);
                var scanEvent = _rawFile.GetScanEventForScanNumber(scan);
                if (scanEvent.MSOrder == MSOrderType.Ms)
                    return scan;

                // Search nearby if not MS1
                for (int i = 1; i < 100; i++)
                {
                    if (scan - i >= _rawFile.RunHeader.FirstSpectrum)
                    {
                        if (_rawFile.GetScanEventForScanNumber(scan - i).MSOrder == MSOrderType.Ms)
                            return scan - i;
                    }
                    if (scan + i <= _rawFile.RunHeader.LastSpectrum)
                    {
                        if (_rawFile.GetScanEventForScanNumber(scan + i).MSOrder == MSOrderType.Ms)
                            return scan + i;
                    }
                }
                return -1;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetMs1ScanNumberFromRT (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_averaged_spectrum")]
        public static unsafe int GetAveragedSpectrum(int handle, int* scanNumbers, int numScans, double* masses, double* intensities, int maxLength)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetMs1ScanNumberFromRT: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var scans = new int[numScans];
                for (int i = 0; i < numScans; i++)
                    scans[i] = scanNumbers[i];

                // CommonCore uses AverageScans extension or casting to IScanAveragePlus
                var massOptions = new MassOptions() { Tolerance = 10, ToleranceUnits = ToleranceUnits.ppm };
                var averageOptions = new FtAverageOptions();
                var result = _rawFile.AverageScans(scans.ToList(), massOptions, averageOptions);

                if (result == null || result.PreferredMasses == null)
                    return 0;

                int count = Math.Min(result.PreferredMasses.Length, maxLength);
                for (int i = 0; i < count; i++)
                {
                    masses[i] = result.PreferredMasses[i];
                    intensities[i] = result.PreferredIntensities[i];
                }
                return result.PreferredMasses.Length;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in get_averaged_spectrum: {ex}");
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_count")]
        public static int GetInstrumentCount(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentCount: RawFile handle is invalid or null.");
                return -1;
            }
            return _rawFile.InstrumentCount;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_count_of_type")]
        public static int GetInstrumentCountOfType(int handle, int type)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentCountOfType: RawFile handle is invalid or null.");
                return -1;
            }
            return _rawFile.GetInstrumentCountOfType((Device)type);
        }

        [UnmanagedCallersOnly(EntryPoint = "is_open")]
        public static int IsOpen(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in IsOpen: RawFile handle is invalid or null.");
                return 0;
            }
            return _rawFile.IsOpen ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "is_error")]
        public static int IsError(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in IsError: RawFile handle is invalid or null.");
                return 1;
            }
            return _rawFile.IsError ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "in_acquisition")]
        public static int InAcquisition(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in InAcquisition: RawFile handle is invalid or null.");
                return 0;
            }
            return _rawFile.InAcquisition ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "has_ms_data")]
        public static int HasMsData(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in HasMsData: RawFile handle is invalid or null.");
                return 0;
            }
            return _rawFile.HasMsData ? 1 : 0;
        }

        private static unsafe int _getStatusLogValuesForRt(int handle, double rt, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in HasMsData: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var log = _rawFile.GetStatusLogForRetentionTime(rt);
                if (log == null || log.Values == null)
                    return 0;
                var res = string.Join("|", log.Values);
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++)
                    buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in HasMsData (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_values_for_rt")]
        public static unsafe int GetStatusLogValuesForRt(int handle, double rt, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            return _getStatusLogValuesForRt(handle, rt, buffer, bufferSize);
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_values")]
        public static unsafe int GetStatusLogValues(int handle, int scanNumber, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in HasMsData: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var rt = _rawFile.RetentionTimeFromScanNumber(scanNumber);
                return _getStatusLogValuesForRt(handle, rt, buffer, bufferSize);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in HasMsData (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_header")]
        public static unsafe int GetStatusLogHeader(int handle, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in HasMsData: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var info = _rawFile.GetStatusLogHeaderInformation();
                if (info == null)
                    return 0;
                var res = string.Join("|", info.Select(x => x.Label + "###TYPE###" + (int)x.DataType + "###LEN###" + x.StringLengthOrPrecision));
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++)
                    buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in HasMsData (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_count")]
        public static int GetStatusLogCount(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetStatusLogCount: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.GetStatusLogEntriesCount();
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetStatusLogCount (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_values")]
        public static unsafe int GetTrailerExtraValues(int handle, int scanNumber, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetStatusLogCount: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var trailer = _rawFile.GetTrailerExtraInformation(scanNumber);
                if (trailer == null || trailer.Values == null)
                    return 0;
                var res = string.Join("|", trailer.Values);
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++)
                    buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetStatusLogCount (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_count")]
        public static int GetTrailerExtraCount(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetTrailerExtraCount: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var header = _rawFile.GetTrailerExtraHeaderInformation();
                return header != null ? header.Count() : 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetTrailerExtraCount (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_ms_order")]
        public static int GetScanEventMsOrder(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventMsOrder: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).MSOrder;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventMsOrder (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_mass_count")]
        public static int GetScanEventMassCount(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventMassCount: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).MassCount;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventMassCount (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_precursor_mass")]
        public static double GetScanEventPrecursorMass(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventPrecursorMass: RawFile handle is invalid or null.");
                return -1.0;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetReaction(index).PrecursorMass;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventPrecursorMass (fallback -1): " + ex.Message);
                return -1.0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_collision_energy_valid")]
        public static int GetScanEventCollisionEnergyValid(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventCollisionEnergyValid: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetReaction(index).CollisionEnergyValid ? 1 : 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventCollisionEnergyValid (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_first_precursor_mass")]
        public static double GetScanEventFirstPrecursorMass(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventFirstPrecursorMass: RawFile handle is invalid or null.");
                return -1.0;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetReaction(index).FirstPrecursorMass;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventFirstPrecursorMass (fallback -1): " + ex.Message);
                return -1.0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_last_precursor_mass")]
        public static double GetScanEventLastPrecursorMass(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventLastPrecursorMass: RawFile handle is invalid or null.");
                return -1.0;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetReaction(index).LastPrecursorMass;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventLastPrecursorMass (fallback -1): " + ex.Message);
                return -1.0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_multiple_activation")]
        public static int GetScanEventMultipleActivation(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventMultipleActivation: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetReaction(index).MultipleActivation ? 1 : 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventMultipleActivation (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_precursor_range_is_valid")]
        public static int GetScanEventPrecursorRangeIsValid(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventPrecursorRangeIsValid: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetReaction(index).PrecursorRangeIsValid ? 1 : 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventPrecursorRangeIsValid (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_activation_type")]
        public static int GetScanEventActivationType(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventActivationType: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).GetActivation(index);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventActivationType (fallback -1): " + ex.Message);
                return -1;
            }
        }



        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_isolation_width")]
        public static double GetScanEventIsolationWidth(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventIsolationWidth: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetIsolationWidth(index);
            }
            catch { return 0.0; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_isolation_width_offset")]
        public static double GetScanEventIsolationWidthOffset(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventIsolationWidthOffset: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetIsolationWidthOffset(index);
            }
            catch { return 0.0; }
        }


        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_collision_energy")]
        public static double GetScanEventCollisionEnergy(int handle, int scanNumber, int index)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventCollisionEnergy: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).GetEnergy(index);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventCollisionEnergy (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_stats")]
        public static unsafe int GetScanStats(int handle, int scanNumber, double* data)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanStats: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var stats = _rawFile.GetScanStatsForScanNumber(scanNumber);
                if (stats == null)
                    return 0;
                data[0] = stats.StartTime;
                data[1] = stats.LowMass;
                data[2] = stats.HighMass;
                data[3] = stats.TIC;
                data[4] = stats.BasePeakMass;
                data[5] = stats.BasePeakIntensity;
                data[6] = stats.PacketCount;
                data[7] = stats.IsCentroidScan ? 1.0 : 0.0;
                data[8] = stats.AbsorbanceUnitScale;
                data[9] = stats.CycleNumber;
                data[10] = stats.Frequency;
                data[11] = stats.IsUniformTime ? 1.0 : 0.0;
                data[12] = stats.LongWavelength;
                data[13] = stats.NumberOfChannels;
                data[14] = stats.PacketType;
                data[15] = stats.ScanEventNumber;
                data[16] = stats.SegmentNumber;
                data[17] = stats.ShortWavelength;
                data[18] = (int)stats.SpectrumPacketType;
                data[19] = stats.WavelengthStep;
                return 20;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanStats (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_stats_scan_type")]
        public static unsafe int GetScanStatsScanType(int handle, int scanNumber, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanStatsScanType: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var stats = _rawFile.GetScanStatsForScanNumber(scanNumber);
                if (stats == null || stats.ScanType == null)
                    return 0;
                var bytes = System.Text.Encoding.UTF8.GetBytes(stats.ScanType);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++)
                {
                    buffer[i] = bytes[i];
                }
                buffer[count] = 0;
                return count;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Warning in GetScanStatsScanType: " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ultra")]
        public static int GetScanFilterUltra(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterUltra: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Ultra;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterUltra (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_wideband")]
        public static int GetScanFilterWideband(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterWideband: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Wideband;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterWideband (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_polarity")]
        public static int GetScanFilterPolarity(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterPolarity: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Polarity;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterPolarity (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ms_order")]
        public static int GetScanFilterMsOrder(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterMsOrder: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).MSOrder;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterMsOrder (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_mass_analyzer")]
        public static int GetScanFilterMassAnalyzer(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterMassAnalyzer: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).MassAnalyzer;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterMassAnalyzer (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_detector")]
        public static int GetScanFilterDetector(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterDetector: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Detector;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterDetector (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_scan_data")]
        public static int GetScanFilterScanData(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterScanData: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).ScanData;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterScanData (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_scan_mode")]
        public static int GetScanFilterScanMode(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterScanMode: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).ScanMode;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterScanMode (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_accurate_mass")]
        public static int GetScanFilterAccurateMass(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterAccurateMass: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).AccurateMass;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterAccurateMass (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ionization_mode")]
        public static int GetScanFilterIonizationMode(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterIonizationMode: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).IonizationMode;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterIonizationMode (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_lock")]
        public static int GetScanFilterLock(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterLock: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Lock;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterLock (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_turbo_scan")]
        public static int GetScanFilterTurboScan(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterTurboScan: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).TurboScan;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterTurboScan (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_corona")]
        public static int GetScanFilterCorona(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterCorona: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Corona;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterCorona (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_dependent")]
        public static int GetScanFilterDependent(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterDependent: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Dependent;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterDependent (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_detector_value")]
        public static double GetScanFilterDetectorValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterDetectorValue: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.GetScanEventForScanNumber(scanNumber).DetectorValue;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterDetectorValue (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_compensation_voltage")]
        public static int GetScanEventCompensationVoltage(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventCompensationVoltage: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return (int)_rawFile.GetScanEventForScanNumber(scanNumber).CompensationVoltage;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventCompensationVoltage (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_compensation_voltage_value")]
        public static double GetScanEventCompensationVoltageValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventCompensationVoltageValue: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                // Use reflection for properties that might not be in the base IScanEvent interface in some versions
                var prop = scanEvent.GetType().GetProperty("CompensationVoltageValue");
                if (prop != null)
                {
                    var val = prop.GetValue(scanEvent);
                    return val != null ? (double)Convert.ChangeType(val, typeof(double)) : 0.0;
                }
                return 0.0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventCompensationVoltageValue (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_header")]
        public static unsafe int GetTrailerExtraHeader(int handle, byte* buffer, int bufferSize)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanEventCompensationVoltageValue: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                var info = _rawFile.GetTrailerExtraHeaderInformation();
                if (info == null)
                    return 0;
                var res = string.Join("|", info.Select(x => x.Label + "###TYPE###" + (int)x.DataType + "###LEN###" + x.StringLengthOrPrecision));
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++)
                    buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanEventCompensationVoltageValue (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "close_raw_file")]
        public static void CloseRawFile(int handle)
        {
            if (_files.TryRemove(handle, out var state))
            {
                state.RawFile?.Dispose();
            }
        }
        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_compensation_volt_type")]
        public static int GetScanFilterCompensationVoltType(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterCompensationVoltType: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).CompensationVoltType;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterCompensationVoltType (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_compensation_voltage_count")]
        public static int GetScanFilterCompensationVoltageCount(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterCompensationVoltageCount: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return _rawFile.GetFilterForScanNumber(scanNumber).CompensationVoltageCount;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterCompensationVoltageCount (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_capture_dissociation")]
        public static int GetScanFilterElectronCaptureDissociation(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterElectronCaptureDissociation: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).ElectronCaptureDissociation;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterElectronCaptureDissociation (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_transfer_dissociation")]
        public static int GetScanFilterElectronTransferDissociation(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterElectronTransferDissociation: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).ElectronTransferDissociation;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterElectronTransferDissociation (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_enhanced")]
        public static int GetScanFilterEnhanced(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterEnhanced: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).Enhanced;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterEnhanced (fallback 0): " + ex.Message);
                return 0;
            }
        }


        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation")]
        public static int GetScanFilterSourceFragmentation(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterSourceFragmentation: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).SourceFragmentation;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterSourceFragmentation (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation_info_valid")]
        public static int GetScanFilterSourceFragmentationInfoValid(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterSourceFragmentationInfoValid: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).SourceFragmentationInfoValid[0];
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterSourceFragmentationInfoValid (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation_type")]
        public static int GetScanFilterSourceFragmentationType(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterSourceFragmentationType: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).SourceFragmentationType;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterSourceFragmentationType (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation_value")]
        public static double GetScanFilterSourceFragmentationValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterSourceFragmentationValue: RawFile handle is invalid or null.");
                return 0.0;
            }
            try
            {
                return _rawFile.GetFilterForScanNumber(scanNumber).SourceFragmentationValue(0);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterSourceFragmentationValue (fallback 0.0): " + ex.Message);
                return 0.0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_supplemental_activation")]
        public static int GetScanFilterSupplementalActivation(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterSupplementalActivation: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).SupplementalActivation;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterSupplementalActivation (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_mass_precision")]
        public static int GetScanFilterMassPrecision(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterMassPrecision: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).MassPrecision;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterMassPrecision (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multi_notch")]
        public static int GetScanFilterMultiNotch(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterMultiNotch: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).MultiNotch;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterMultiNotch (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multiplex")]
        public static int GetScanFilterMultiplex(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterMultiplex: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.GetFilterForScanNumber(scanNumber).Multiplex;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterMultiplex (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_unique_mass_count")]
        public static int GetScanFilterUniqueMassCount(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetScanFilterUniqueMassCount: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return _rawFile.GetFilterForScanNumber(scanNumber).UniqueMassCount;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetScanFilterUniqueMassCount (fallback 0): " + ex.Message);
                return 0;
            }
        }
        private static double GetFilterDouble(int handle, int scanNumber, string name)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetFilterDouble: RawFile handle is invalid or null.");
                return 0.0;
            }
            try
            {
                var filter = _rawFile.GetFilterForScanNumber(scanNumber);
                var prop = filter.GetType().GetProperty(name);
                if (prop == null)
                {
                    Console.Error.WriteLine($"[native-fisher-py] Error in GetFilterDouble: Property '{name}' not found on filter.");
                    return 0.0;
                }
                var val = prop.GetValue(filter);
                if (val == null)
                {
                    Console.Error.WriteLine($"[native-fisher-py] Error in GetFilterDouble: Value for property '{name}' is null.");
                    return 0.0;
                }
                return (double)Convert.ChangeType(val, typeof(double));
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetFilterDouble (fallback 0.0): " + ex.Message);
                return 0.0;
            }
        }

        private static int GetFilterInt(int handle, int scanNumber, string name)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetFilterInt: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                var filter = _rawFile.GetFilterForScanNumber(scanNumber);
                var prop = filter.GetType().GetProperty(name);
                if (prop == null)
                {
                    Console.Error.WriteLine($"[native-fisher-py] Error in GetFilterInt: Property '{name}' not found on filter.");
                    return 0;
                }
                var val = prop.GetValue(filter);
                if (val == null)
                {
                    Console.Error.WriteLine($"[native-fisher-py] Error in GetFilterInt: Value for property '{name}' is null.");
                    return 0;
                }
                return (int)Convert.ChangeType(val, typeof(int));
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetFilterInt (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_higher_energy_cid")]
        public static int GetScanFilterHigherEnergyCID(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterInt(handle, scanNumber, "HigherEnergyCID") != 0 ? GetFilterInt(handle, scanNumber, "HigherEnergyCID") : GetFilterInt(handle, scanNumber, "HigherEnergyCid");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_higher_energy_cid_value")]
        public static double GetScanFilterHigherEnergyCIDValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            double val = GetFilterDouble(handle, scanNumber, "HigherEnergyCIDValue");
            if (val == 0.0)
                val = GetFilterDouble(handle, scanNumber, "HigherEnergyCidValue");
            return val;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_capture_dissociation_value")]
        public static double GetScanFilterElectronCaptureDissociationValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "ElectronCaptureDissociationValue");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_transfer_dissociation_value")]
        public static double GetScanFilterElectronTransferDissociationValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "ElectronTransferDissociationValue");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multiple_photon_dissociation")]
        public static int GetScanFilterMultiplePhotonDissociation(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterInt(handle, scanNumber, "MultiplePhotonDissociation");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multiple_photon_dissociation_value")]
        public static double GetScanFilterMultiplePhotonDissociationValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "MultiplePhotonDissociationValue");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_pulsed_q_dissociation")]
        public static int GetScanFilterPulsedQDissociation(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterInt(handle, scanNumber, "PulsedQDissociation");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_pulsed_q_dissociation_value")]
        public static double GetScanFilterPulsedQDissociationValue(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "PulsedQDissociationValue");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_a")]
        public static double GetScanFilterParamA(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "ParamA");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_b")]
        public static double GetScanFilterParamB(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "ParamB");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_f")]
        public static double GetScanFilterParamF(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "ParamF");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_r")]
        public static double GetScanFilterParamR(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "ParamR");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_v")]
        public static double GetScanFilterParamV(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterDouble(handle, scanNumber, "ParamV");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_field_free_region")]
        public static int GetScanFilterFieldFreeRegion(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterInt(handle, scanNumber, "FieldFreeRegion");
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_index_to_multiple_activation_index")]
        public static int GetScanFilterIndexToMultipleActivationIndex(int handle, int scanNumber)
        {
            var _rawFile = GetFile(handle);
            return GetFilterInt(handle, scanNumber, "IndexToMultipleActivationIndex");
        }
        [UnmanagedCallersOnly(EntryPoint = "select_instrument")]
        public static void SelectInstrument(int handle, int deviceType, int deviceNumber)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in SelectInstrument: RawFile handle is invalid or null.");
                return;
            }
            try
            {
                _rawFile.SelectInstrument((Device)deviceType, deviceNumber);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in SelectInstrument (ignored): " + ex.Message);
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_method_count")]
        public static int GetInstrumentMethodCount(int handle)
        {
            var state = GetState(handle);
            return state != null ? state.CachedMethodCount : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_method")]
        public static unsafe int GetInstrumentMethod(int handle, int index, byte* buffer, int maxLength)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetInstrumentMethodCount: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                string method = _rawFile.GetInstrumentMethod(index);
                if (string.IsNullOrEmpty(method))
                    return 0;

                byte[] bytes = System.Text.Encoding.UTF8.GetBytes(method);
                int len = Math.Min(bytes.Length, maxLength - 1);
                for (int i = 0; i < len; i++)
                    buffer[i] = bytes[i];
                buffer[len] = 0;
                return len;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetInstrumentMethodCount (fallback -1): " + ex.Message);
                return -1;
            }
        }
        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_tray_index")]
        public static int GetAutoSamplerTrayIndex(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetAutoSamplerTrayIndex: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.AutoSamplerInformation.TrayIndex;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetAutoSamplerTrayIndex (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vial_index")]
        public static int GetAutoSamplerVialIndex(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetAutoSamplerVialIndex: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.AutoSamplerInformation.VialIndex;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetAutoSamplerVialIndex (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_tray_name")]
        public static unsafe int GetAutoSamplerTrayName(int handle, byte* buffer, int maxLength)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetAutoSamplerVialIndex: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                string name = _rawFile.AutoSamplerInformation.TrayName ?? "";
                byte[] bytes = System.Text.Encoding.UTF8.GetBytes(name);
                int len = Math.Min(bytes.Length, maxLength - 1);
                for (int i = 0; i < len; i++)
                    buffer[i] = bytes[i];
                buffer[len] = 0;
                return len;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetAutoSamplerVialIndex (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_tray_shape")]
        public static int GetAutoSamplerTrayShape(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetAutoSamplerTrayShape: RawFile handle is invalid or null.");
                return 0;
            }
            try
            {
                return (int)_rawFile.AutoSamplerInformation.TrayShape;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetAutoSamplerTrayShape (fallback 0): " + ex.Message);
                return 0;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vials_per_tray")]
        public static int GetAutoSamplerVialsPerTray(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetAutoSamplerVialsPerTray: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.AutoSamplerInformation.VialsPerTray;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetAutoSamplerVialsPerTray (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vials_per_tray_x")]
        public static int GetAutoSamplerVialsPerTrayX(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetAutoSamplerVialsPerTrayX: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.AutoSamplerInformation.VialsPerTrayX;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetAutoSamplerVialsPerTrayX (fallback -1): " + ex.Message);
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vials_per_tray_y")]
        public static int GetAutoSamplerVialsPerTrayY(int handle)
        {
            var _rawFile = GetFile(handle);
            if (_rawFile == null)
            {
                Console.Error.WriteLine("[native-fisher-py] Error in GetAutoSamplerVialsPerTrayY: RawFile handle is invalid or null.");
                return -1;
            }
            try
            {
                return _rawFile.AutoSamplerInformation.VialsPerTrayY;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[native-fisher-py] Exception in GetAutoSamplerVialsPerTrayY (fallback -1): " + ex.Message);
                return -1;
            }
        }
    }
}
