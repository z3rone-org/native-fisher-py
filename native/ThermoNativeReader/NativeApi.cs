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
        private static IRawDataPlus? _rawFile;

        private static string SafeGetFilterString(IScanFilter filter)
        {
            if (filter == null) return "";
            // We AVOID filter.ToString() because it triggers the Thermo.FilterStringTokens static constructor
            // which fails in AOT due to GetEnumValues[T] reflection.
            try 
            {
                var polarity = filter.Polarity == PolarityType.Positive ? "+" : (filter.Polarity == PolarityType.Negative ? "-" : "");
                var analyzer = ((int)filter.MassAnalyzer).ToString(); 
                var msOrder = ((int)filter.MSOrder).ToString();
                return $"{analyzer} {polarity} ms{msOrder}";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Manual filter formatting failed: {ex.Message}");
                return "MS_ORDER_ONLY";
            }
        }

        // Dummy usage to prevent AOT trimming of important types used by reflection in Thermo DLLs
        private static ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType[] _dummyArray = new ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType[0];
        private static ThermoFisher.CommonCore.Data.Interfaces.IScanFilter? _dummyFilter = null;

        static NativeApi() {
            // Force compiler to keep these types
            _dummyFilter = (ThermoFisher.CommonCore.Data.Interfaces.IScanFilter?)null;
            var t = typeof(ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType);
        }

        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType))]
        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.IScanFilter))]
        [UnmanagedCallersOnly(EntryPoint = "open_raw_file")]
        public static unsafe int OpenRawFile(byte* pathPtr)
        {
            try
            {
                if (pathPtr == null) return -1;
                string? path = Marshal.PtrToStringAnsi((IntPtr)pathPtr);
                if (string.IsNullOrEmpty(path)) return -1;
                
                _rawFile = (IRawDataPlus)RawFileReaderAdapter.FileFactory(path);
                if (_rawFile == null) return -1;
                _rawFile.SelectInstrument(Device.MS, 1);
                return 0;
            }
            catch
            {
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_num_scans")]
        public static int GetNumScans()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1;
            return _rawFile.RunHeader.LastSpectrum;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_rt")]
        public static double GetScanRT(int scanNumber)
        {
            if (_rawFile == null) return -1.0;
            return _rawFile.RetentionTimeFromScanNumber(scanNumber);
        }

        [UnmanagedCallersOnly(EntryPoint = "get_spectrum")]
        public static unsafe int GetSpectrum(int scanNumber, double* masses, double* intensities, int maxLength)
        {
            if (_rawFile == null) return -1;
            
            try 
            {
                var reader = (ISimplifiedScanReader)_rawFile;
                var centroids = reader.GetSimplifiedCentroids(scanNumber);
                if (centroids == null || centroids.Masses == null || centroids.Intensities == null) return 0;
                
                int count = Math.Min(centroids.Masses.Length, maxLength);
                for (int i = 0; i < count; i++)
                {
                    masses[i] = centroids.Masses[i];
                    intensities[i] = centroids.Intensities[i];
                }
                return centroids.Masses.Length;
            }
            catch
            {
                return -1;
            }
        }

        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.MetaFilterType))]
        [DynamicDependency(DynamicallyAccessedMemberTypes.All, typeof(ThermoFisher.CommonCore.Data.Interfaces.IScanFilter))]
        [UnmanagedCallersOnly(EntryPoint = "get_filters")]
        public static unsafe int GetFilters(IntPtr* filters, int maxCount)
        {
            if (_rawFile == null) return -1;
            /*
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
            */
            return 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_first_scan")]
        public static int GetFirstScan()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1;
            return _rawFile.RunHeader.FirstSpectrum;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_last_scan")]
        public static int GetLastScan()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1;
            return _rawFile.RunHeader.LastSpectrum;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_end_time")]
        public static double GetEndTime()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1.0;
            return _rawFile.RunHeader.EndTime;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_start_time")]
        public static double GetStartTime()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1.0;
            return _rawFile.RunHeader.StartTime;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_mass_resolution")]
        public static double GetMassResolution()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1.0;
            return _rawFile.RunHeader.MassResolution;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_expected_runtime")]
        public static double GetExpectedRuntime()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1.0;
            return _rawFile.RunHeader.ExpectedRuntime;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_max_integrated_intensity")]
        public static double GetMaxIntegratedIntensity()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1.0;
            return _rawFile.RunHeader.MaxIntegratedIntensity;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_max_intensity")]
        public static int GetMaxIntensity()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1;
            return _rawFile.RunHeader.MaxIntensity;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_low_mass")]
        public static double GetLowMass()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1.0;
            return _rawFile.RunHeader.LowMass;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_high_mass")]
        public static double GetHighMass()
        {
            if (_rawFile == null || _rawFile.RunHeader == null) return -1.0;
            return _rawFile.RunHeader.HighMass;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_file_name")]
        public static unsafe int GetFileName(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.FileName ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_path")]
        public static unsafe int GetPath(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.Path ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_creation_date")]
        public static unsafe int GetCreationDate(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.CreationDate.ToString("o");
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_computer_name")]
        public static unsafe int GetComputerName(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.ComputerName ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_creator_id")]
        public static unsafe int GetCreatorID(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.CreatorId ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_model")]
        public static unsafe int GetInstrumentModel(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.Model ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_name")]
        public static unsafe int GetInstrumentName(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.Name ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_serial_number")]
        public static unsafe int GetInstrumentSerialNumber(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.SerialNumber ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_software_version")]
        public static unsafe int GetInstrumentSoftwareVersion(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.SoftwareVersion ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_hardware_version")]
        public static unsafe int GetInstrumentHardwareVersion(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.HardwareVersion ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_axis_label_x")]
        public static unsafe int GetInstrumentAxisLabelX(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.AxisLabelX ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_axis_label_y")]
        public static unsafe int GetInstrumentAxisLabelY(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.AxisLabelY ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_flags")]
        public static unsafe int GetInstrumentFlags(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            var str = data?.Flags ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_units")]
        public static int GetInstrumentUnits()
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            return data != null ? (int)data.Units : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_is_valid")]
        public static int GetInstrumentIsValid()
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            return data != null && data.IsValid ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_has_accurate_mass_precursors")]
        public static int GetInstrumentHasAccurateMassPrecursors()
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            return data != null && data.HasAccurateMassPrecursors ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_is_tsq_quantum_file")]
        public static int GetInstrumentIsTsqQuantumFile()
        {
            if (_rawFile == null) return -1;
            var data = _rawFile.GetInstrumentData();
            return data != null && data.IsTsqQuantumFile() ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_file_description")]
        public static unsafe int GetFileDescription(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.FileHeader.FileDescription ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_modified_date")]
        public static unsafe int GetModifiedDate(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.FileHeader.ModifiedDate.ToString() ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_created_logon")]
        public static unsafe int GetWhoCreatedLogon(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.FileHeader.WhoCreatedLogon ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_modified_id")]
        public static unsafe int GetWhoModifiedId(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.FileHeader.WhoModifiedId ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_modified_logon")]
        public static unsafe int GetWhoModifiedLogon(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.FileHeader.WhoModifiedLogon ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_barcode")]
        public static unsafe int GetSampleBarcode(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.SampleInformation.Barcode ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_id")]
        public static unsafe int GetSampleId(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.SampleInformation.SampleId ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_name")]
        public static unsafe int GetSampleName(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.SampleInformation.SampleName ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_vial")]
        public static unsafe int GetSampleVial(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.SampleInformation.Vial ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_comment")]
        public static unsafe int GetSampleComment(byte* buffer, int length)
        {
            if (_rawFile == null) return -1;
            var str = _rawFile.SampleInformation.Comment ?? "";
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms_order")]
        public static int GetMsOrder(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                return (int)scanEvent.MSOrder;
            }
            catch
            {
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_mass_analyzer")]
        public static int GetMassAnalyzer(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                return (int)scanEvent.MassAnalyzer;
            }
            catch
            {
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_precursor_mass")]
        public static double GetPrecursorMass(int scanNumber)
        {
            if (_rawFile == null) return -1.0;
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                if (scanEvent.MSOrder == MSOrderType.Ms) return 0.0;
                return scanEvent.GetReaction(0).PrecursorMass;
            }
            catch
            {
                return -1.0;
            }
        }

        private static string SafeGetScanEventString(IScanEvent scanEvent)
        {
            if (scanEvent == null) return "";
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
        public static unsafe int GetScanEventString(int scanNumber, byte* buffer, int bufferSize)
        {
            if (_rawFile == null) return 0;
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                if (scanEvent == null) return 0;

                string eventStr = SafeGetScanEventString(scanEvent);

                if (string.IsNullOrEmpty(eventStr)) return 0;
                
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
        public static unsafe int GetMs2FilterMasses(double* buffer, int maxSize)
        {
            if (_rawFile == null) return -1;
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

        [UnmanagedCallersOnly(EntryPoint = "get_scan_number_from_rt")]
        public static int GetScanNumberFromRT(double rt)
        {
            if (_rawFile == null) return -1;
            return _rawFile.ScanNumberFromRetentionTime(rt);
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms2_scan_number_from_rt")]
        public static int GetMs2ScanNumberFromRT(double rt, double precursorMz, double tolerancePpm)
        {
            if (_rawFile == null) return -1;
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
                        if (precursorMz <= 0) {
                            match = true;
                        } else {
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
            catch
            {
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_chromatogram")]
        public static unsafe int GetChromatogram(int traceType, IntPtr filterPtr, double* massRangesStart, double* massRangesEnd, int massRangeCount, int startScan, int endScan, double* times, double* intensities, int maxLength)
        {
            if (_rawFile == null) return -1;
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
        public static int GetMs1ScanNumberFromRT(double rt)
        {
            if (_rawFile == null) return -1;
            try
            {
                int scan = _rawFile.ScanNumberFromRetentionTime(rt);
                var scanEvent = _rawFile.GetScanEventForScanNumber(scan);
                if (scanEvent.MSOrder == MSOrderType.Ms) return scan;
                
                // Search nearby if not MS1
                for (int i = 1; i < 100; i++)
                {
                    if (scan - i >= _rawFile.RunHeader.FirstSpectrum)
                    {
                         if (_rawFile.GetScanEventForScanNumber(scan - i).MSOrder == MSOrderType.Ms) return scan - i;
                    }
                    if (scan + i <= _rawFile.RunHeader.LastSpectrum)
                    {
                         if (_rawFile.GetScanEventForScanNumber(scan + i).MSOrder == MSOrderType.Ms) return scan + i;
                    }
                }
                return -1;
            }
            catch
            {
                return -1;
            }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_averaged_spectrum")]
        public static unsafe int GetAveragedSpectrum(int* scanNumbers, int numScans, double* masses, double* intensities, int maxLength)
        {
            if (_rawFile == null) return -1;
            try
            {
                var scans = new int[numScans];
                for (int i = 0; i < numScans; i++) scans[i] = scanNumbers[i];
                
                // CommonCore uses AverageScans extension or casting to IScanAveragePlus
                var massOptions = new MassOptions() { Tolerance = 10, ToleranceUnits = ToleranceUnits.ppm };
                var averageOptions = new FtAverageOptions();
                var result = _rawFile.AverageScans(scans.ToList(), massOptions, averageOptions);
                
                if (result == null || result.PreferredMasses == null) return 0;
                
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
        public static int GetInstrumentCount()
        {
            if (_rawFile == null) return -1;
            return _rawFile.InstrumentCount;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_count_of_type")]
        public static int GetInstrumentCountOfType(int type)
        {
            if (_rawFile == null) return -1;
            return _rawFile.GetInstrumentCountOfType((Device)type);
        }

        [UnmanagedCallersOnly(EntryPoint = "is_open")]
        public static int IsOpen()
        {
            if (_rawFile == null) return 0;
            return _rawFile.IsOpen ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "is_error")]
        public static int IsError()
        {
            if (_rawFile == null) return 1;
            return _rawFile.IsError ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "in_acquisition")]
        public static int InAcquisition()
        {
            if (_rawFile == null) return 0;
            return _rawFile.InAcquisition ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "has_ms_data")]
        public static int HasMsData()
        {
            if (_rawFile == null) return 0;
            return _rawFile.HasMsData ? 1 : 0;
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_values")]
        public static unsafe int GetStatusLogValues(int scanNumber, byte* buffer, int bufferSize)
        {
            if (_rawFile == null) return -1;
            try
            {
                var rt = _rawFile.RetentionTimeFromScanNumber(scanNumber);
                var log = _rawFile.GetStatusLogForRetentionTime(rt);
                if (log == null || log.Values == null) return 0;
                var res = string.Join("|", log.Values);
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++) buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_header")]
        public static unsafe int GetStatusLogHeader(byte* buffer, int bufferSize)
        {
            if (_rawFile == null) return -1;
            try
            {
                var info = _rawFile.GetStatusLogHeaderInformation();
                if (info == null) return 0;
                var res = string.Join("|", info.Select(x => x.Label));
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++) buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_count")]
        public static int GetStatusLogCount()
        {
            if (_rawFile == null) return -1;
            try { return _rawFile.GetStatusLogEntriesCount(); }
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_values")]
        public static unsafe int GetTrailerExtraValues(int scanNumber, byte* buffer, int bufferSize)
        {
            if (_rawFile == null) return -1;
            try
            {
                var trailer = _rawFile.GetTrailerExtraInformation(scanNumber);
                if (trailer == null || trailer.Values == null) return 0;
                var res = string.Join("|", trailer.Values);
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++) buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_count")]
        public static int GetTrailerExtraCount()
        {
            if (_rawFile == null) return -1;
            try { 
                var header = _rawFile.GetTrailerExtraHeaderInformation();
                return header != null ? header.Count() : 0;
            }
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_ms_order")]
        public static int GetScanEventMsOrder(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).MSOrder; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_mass_count")]
        public static int GetScanEventMassCount(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return _rawFile.GetScanEventForScanNumber(scanNumber).MassCount; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_precursor_mass")]
        public static double GetScanEventPrecursorMass(int scanNumber, int index)
        {
            if (_rawFile == null) return -1;
            try { return _rawFile.GetScanEventForScanNumber(scanNumber).GetMass(index); } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_activation_type")]
        public static int GetScanEventActivationType(int scanNumber, int index)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).GetActivation(index); } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_collision_energy")]
        public static double GetScanEventCollisionEnergy(int scanNumber, int index)
        {
            if (_rawFile == null) return -1;
            try { return _rawFile.GetScanEventForScanNumber(scanNumber).GetEnergy(index); } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_stats")]
        public static unsafe int GetScanStats(int scanNumber, double* data)
        {
            if (_rawFile == null) return -1;
            try
            {
                var stats = _rawFile.GetScanStatsForScanNumber(scanNumber);
                if (stats == null) return 0;
                data[0] = stats.StartTime;
                data[1] = stats.LowMass;
                data[2] = stats.HighMass;
                data[3] = stats.TIC;
                data[4] = stats.BasePeakMass;
                data[5] = stats.BasePeakIntensity;
                data[6] = stats.PacketCount;
                return 7;
            }
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ultra")]
        public static int GetScanFilterUltra(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Ultra; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_wideband")]
        public static int GetScanFilterWideband(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Wideband; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_polarity")]
        public static int GetScanFilterPolarity(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Polarity; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ms_order")]
        public static int GetScanFilterMsOrder(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).MSOrder; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_mass_analyzer")]
        public static int GetScanFilterMassAnalyzer(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).MassAnalyzer; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_detector")]
        public static int GetScanFilterDetector(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Detector; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_scan_data")]
        public static int GetScanFilterScanData(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).ScanData; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_scan_mode")]
        public static int GetScanFilterScanMode(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).ScanMode; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_accurate_mass")]
        public static int GetScanFilterAccurateMass(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).AccurateMass; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ionization_mode")]
        public static int GetScanFilterIonizationMode(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).IonizationMode; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_lock")]
        public static int GetScanFilterLock(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Lock; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_turbo_scan")]
        public static int GetScanFilterTurboScan(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).TurboScan; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_corona")]
        public static int GetScanFilterCorona(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Corona; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_dependent")]
        public static int GetScanFilterDependent(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).Dependent; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_detector_value")]
        public static double GetScanFilterDetectorValue(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return _rawFile.GetScanEventForScanNumber(scanNumber).DetectorValue; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_compensation_voltage")]
        public static int GetScanEventCompensationVoltage(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try { return (int)_rawFile.GetScanEventForScanNumber(scanNumber).CompensationVoltage; } catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_compensation_voltage_value")]
        public static double GetScanEventCompensationVoltageValue(int scanNumber)
        {
            if (_rawFile == null) return -1;
            try 
            { 
                // TODO: ScanFilter class namespace investigation
                return 0.0;
            } 
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_header")]
        public static unsafe int GetTrailerExtraHeader(byte* buffer, int bufferSize)
        {
            if (_rawFile == null) return -1;
            try
            {
                var info = _rawFile.GetTrailerExtraHeaderInformation();
                if (info == null) return 0;
                var res = string.Join("|", info.Select(x => x.Label + ":" + (int)x.DataType));
                var bytes = System.Text.Encoding.UTF8.GetBytes(res);
                int count = Math.Min(bytes.Length, bufferSize - 1);
                for (int i = 0; i < count; i++) buffer[i] = bytes[i];
                buffer[count] = 0;
                return bytes.Length;
            }
            catch { return -1; }
        }

        [UnmanagedCallersOnly(EntryPoint = "close_raw_file")]
        public static void CloseRawFile()
        {
            _rawFile?.Dispose();
            _rawFile = null;
        }
    }
}
