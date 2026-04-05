using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using ThermoFisher.CommonCore.RawFileReader;
using ThermoFisher.CommonCore.Data;
using ThermoFisher.CommonCore.Data.Business;
using ThermoFisher.CommonCore.Data.Interfaces;
using ThermoFisher.CommonCore.Data.FilterEnums;

namespace ThermoNativeReader
{
    public static class NativeApi
    {
        private static IRawDataPlus? _rawFile;

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

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_string")]
        public static unsafe int GetScanEventString(int scanNumber, byte* buffer, int bufferSize)
        {
            if (_rawFile == null) return -1;
            try
            {
                var scanEvent = _rawFile.GetScanEventForScanNumber(scanNumber);
                string? eventStr = null;
                
                try 
                {
                    eventStr = scanEvent.ToString();
                }
                catch (Exception ex)
                {
                    // NativeAOT Workaround: If ToString fails due to Assembly.Location being null/empty,
                    // we manually construct a basic filter string.
                    Console.WriteLine($"Warning: ScanEvent.ToString failed in AOT, using fallback. Error: {ex.Message}");
                    
                    // Construct a basic filter string like "FTMS + p NSI Full ms [400.00-2000.00]"
                    // We can pull these parts from the scanEvent properties.
                    var analyzer = scanEvent.MassAnalyzer.ToString();
                    var polarity = scanEvent.Polarity == ThermoFisher.CommonCore.Data.FilterEnums.PolarityType.Positive ? "+" : "-";
                    var msOrder = (scanEvent.MSOrder == MSOrderType.Ms) ? "ms" : $"ms{(int)scanEvent.MSOrder}";
                    
                    eventStr = $"{analyzer} {polarity} p NSI Full {msOrder}";
                }

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
        public static unsafe int GetChromatogram(int traceType, double* times, double* intensities, int maxLength)
        {
            if (_rawFile == null) return -1;
            try
            {
                var settings = new ChromatogramTraceSettings((TraceType)traceType) { Filter = "" };
                var data = _rawFile.GetChromatogramData(new[] { settings }, -1, -1);
                
                if (data == null) return 0;
                
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

        [UnmanagedCallersOnly(EntryPoint = "close_raw_file")]
        public static void CloseRawFile()
        {
            _rawFile?.Dispose();
            _rawFile = null;
        }
    }
}
