using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading;
using ThermoFisher.CommonCore.RawFileReader;
using ThermoFisher.CommonCore.Data;
using ThermoFisher.CommonCore.Data.Business;
using ThermoFisher.CommonCore.Data.Interfaces;

namespace ThermoNativeReader
{
    public static class NativeApi
    {
        private static readonly Dictionary<long, IRawDataPlus> _openFiles = new Dictionary<long, IRawDataPlus>();
        private static long _nextHandle = 1;
        private static readonly BlockingCollection<Action> _workQueue = new BlockingCollection<Action>();

        static NativeApi()
        {
            var workerThread = new Thread(WorkerLoop) { IsBackground = true, Name = "ThermoWorker" };
            workerThread.Start();
        }

        private static void WorkerLoop()
        {
            foreach (var action in _workQueue.GetConsumingEnumerable())
            {
                try { action(); } catch { }
            }
        }

        private static T RunOnWorker<T>(Func<T> func)
        {
            T result = default;
            using var done = new ManualResetEvent(false);
            _workQueue.Add(() => {
                try { result = func(); }
                finally { done.Set(); }
            });
            done.WaitOne();
            return result;
        }

        private static void RunOnWorkerSync(Action action)
        {
            using var done = new ManualResetEvent(false);
            _workQueue.Add(() => {
                try { action(); }
                finally { done.Set(); }
            });
            done.WaitOne();
        }

        private static unsafe int CopyString(string s, byte* buffer, int length)
        {
            if (buffer == null || length <= 0) return 0;
            var bytes = System.Text.Encoding.UTF8.GetBytes(s ?? "");
            int count = Math.Min(bytes.Length, length - 1);
            for (int i = 0; i < count; i++) buffer[i] = bytes[i];
            buffer[count] = 0;
            return count;
        }

        [UnmanagedCallersOnly(EntryPoint = "open_raw_file")]
        public static unsafe long OpenRawFile(byte* pathPtr)
        {
            if (pathPtr == null) return -1;
            string? path = Marshal.PtrToStringAnsi((IntPtr)pathPtr);
            return RunOnWorker(() => {
                try {
                    var rawFile = (IRawDataPlus)RawFileReaderAdapter.FileFactory(path);
                    if (rawFile == null) return -1;
                    rawFile.SelectInstrument(Device.MS, 1);
                    long h = _nextHandle++;
                    _openFiles[h] = rawFile;
                    return h;
                } catch { return -1; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "close_raw_file")]
        public static void CloseRawFile(long handle)
        {
            // SKIP Dispose for now to avoid shutdown crashes
            RunOnWorkerSync(() => {
                _openFiles.Remove(handle);
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_num_scans")]
        public static unsafe int GetNumScans(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return f.RunHeader.LastSpectrum; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_tune_data_count")]
        public static unsafe int GetTuneDataCount(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_rt")]
        public static unsafe double GetScanRt(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return f.RetentionTimeFromScanNumber((int)arg1); } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_spectrum")]
        public static unsafe int GetSpectrum(long arg0, int arg1, double* arg2, double* arg3, int arg4)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { var scan = f.GetSegmentedScanFromScanNumber((int)arg1, f.GetScanStatsForScanNumber((int)arg1));
            if (scan == null) return 0;
            int count = Math.Min(scan.Positions.Length, (int)arg4);
            for(int i=0; i<count; i++) {
                arg2[i] = scan.Positions[i];
                arg3[i] = scan.Intensities[i];
            }
            return count; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "is_centroid")]
        public static unsafe int IsCentroid(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_centroid_stream_full")]
        public static unsafe int GetCentroidStreamFull(long arg0, int arg1, double* arg2, double* arg3, double* arg4, double* arg5, int* arg6, double* arg7, int arg8)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { 
            var stream = f.GetCentroidStream((int)arg1, false);
            if (stream == null) return 0;
            int count = Math.Min(stream.Length, (int)arg8);
            for(int i=0; i<count; i++) {
                if (arg2 != null && stream.Masses != null && i < stream.Masses.Length) arg2[i] = stream.Masses[i];
                if (arg3 != null && stream.Intensities != null && i < stream.Intensities.Length) arg3[i] = stream.Intensities[i];
                if (arg4 != null && stream.Baselines != null && i < stream.Baselines.Length) arg4[i] = stream.Baselines[i];
                if (arg5 != null && stream.Noises != null && i < stream.Noises.Length) arg5[i] = stream.Noises[i];
                if (arg6 != null && stream.Charges != null && i < stream.Charges.Length) arg6[i] = (int)stream.Charges[i];
            }
            if (arg7 != null) {
                arg7[0] = stream.BasePeakNoise;
                arg7[1] = stream.BasePeakResolution;
            }
            return count; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_type")]
        public static unsafe int GetSampleType(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_row_number")]
        public static unsafe int GetSampleRowNumber(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_dilution_factor")]
        public static unsafe double GetSampleDilutionFactor(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_first_scan")]
        public static unsafe int GetFirstScan(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return f.RunHeader.FirstSpectrum; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_last_scan")]
        public static unsafe int GetLastScan(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return f.RunHeader.LastSpectrum; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_end_time")]
        public static unsafe double GetEndTime(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_start_time")]
        public static unsafe double GetStartTime(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_mass_resolution")]
        public static unsafe double GetMassResolution(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_expected_runtime")]
        public static unsafe double GetExpectedRuntime(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_max_integrated_intensity")]
        public static unsafe double GetMaxIntegratedIntensity(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_max_intensity")]
        public static unsafe int GetMaxIntensity(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_low_mass")]
        public static unsafe double GetLowMass(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_high_mass")]
        public static unsafe double GetHighMass(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_file_name")]
        public static unsafe int GetFileName(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return CopyString(f.FileName, arg1, arg2); } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_path")]
        public static unsafe int GetPath(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_creation_date")]
        public static unsafe int GetCreationDate(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_computer_name")]
        public static unsafe int GetComputerName(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_creator_id")]
        public static unsafe int GetCreatorId(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_model")]
        public static unsafe int GetInstrumentModel(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_name")]
        public static unsafe int GetInstrumentName(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_serial_number")]
        public static unsafe int GetInstrumentSerialNumber(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_software_version")]
        public static unsafe int GetInstrumentSoftwareVersion(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_hardware_version")]
        public static unsafe int GetInstrumentHardwareVersion(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms_order")]
        public static unsafe int GetMsOrder(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_mass_analyzer")]
        public static unsafe int GetMassAnalyzer(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_precursor_mass")]
        public static unsafe double GetPrecursorMass(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_string")]
        public static unsafe int GetScanEventString(long arg0, int arg1, byte* arg2, int arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_string")]
        public static unsafe int GetScanFilterString(long arg0, int arg1, byte* arg2, int arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_number_from_rt")]
        public static unsafe int GetScanNumberFromRt(long arg0, double arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms2_filter_masses")]
        public static unsafe int GetMs2FilterMasses(long arg0, double* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms2_scan_number_from_rt")]
        public static unsafe int GetMs2ScanNumberFromRt(long arg0, double arg1, double arg2, double arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_ms1_scan_number_from_rt")]
        public static unsafe int GetMs1ScanNumberFromRt(long arg0, double arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_chromatogram")]
        public static unsafe int GetChromatogram(long arg0, int arg1, byte* arg2, double* arg3, double* arg4, int arg5, int arg6, int arg7, double* arg8, double* arg9, int arg10)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_filters")]
        public static unsafe int GetFilters(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_averaged_spectrum")]
        public static unsafe int GetAveragedSpectrum(long arg0, int* arg1, int arg2, double* arg3, double* arg4, int arg5)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_count")]
        public static unsafe int GetInstrumentCount(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_count_of_type")]
        public static unsafe int GetInstrumentCountOfType(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "is_open")]
        public static unsafe int IsOpen(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "is_error")]
        public static unsafe int IsError(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "in_acquisition")]
        public static unsafe int InAcquisition(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "has_ms_data")]
        public static unsafe int HasMsData(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_meta_filters")]
        public static unsafe int GetScanFilterMetaFilters(long arg0, long arg1, long arg2, long arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_field_free_region")]
        public static unsafe int GetScanFilterFieldFreeRegion(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_index_to_multiple_activation_index")]
        public static unsafe int GetScanFilterIndexToMultipleActivationIndex(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_compensation_volt_type")]
        public static unsafe int GetScanFilterCompensationVoltType(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_compensation_voltage_count")]
        public static unsafe int GetScanFilterCompensationVoltageCount(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_capture_dissociation")]
        public static unsafe int GetScanFilterElectronCaptureDissociation(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_capture_dissociation_value")]
        public static unsafe double GetScanFilterElectronCaptureDissociationValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_transfer_dissociation")]
        public static unsafe int GetScanFilterElectronTransferDissociation(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_electron_transfer_dissociation_value")]
        public static unsafe double GetScanFilterElectronTransferDissociationValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_enhanced")]
        public static unsafe int GetScanFilterEnhanced(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_higher_energy_cid")]
        public static unsafe int GetScanFilterHigherEnergyCid(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_higher_energy_cid_value")]
        public static unsafe double GetScanFilterHigherEnergyCidValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multiple_photon_dissociation")]
        public static unsafe int GetScanFilterMultiplePhotonDissociation(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multiple_photon_dissociation_value")]
        public static unsafe double GetScanFilterMultiplePhotonDissociationValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_pulsed_q_dissociation")]
        public static unsafe int GetScanFilterPulsedQDissociation(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_pulsed_q_dissociation_value")]
        public static unsafe double GetScanFilterPulsedQDissociationValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation")]
        public static unsafe int GetScanFilterSourceFragmentation(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation_info_valid")]
        public static unsafe int GetScanFilterSourceFragmentationInfoValid(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation_type")]
        public static unsafe int GetScanFilterSourceFragmentationType(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_source_fragmentation_value")]
        public static unsafe double GetScanFilterSourceFragmentationValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_supplemental_activation")]
        public static unsafe int GetScanFilterSupplementalActivation(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_mass_precision")]
        public static unsafe int GetScanFilterMassPrecision(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multi_notch")]
        public static unsafe int GetScanFilterMultiNotch(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_multiplex")]
        public static unsafe int GetScanFilterMultiplex(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_unique_mass_count")]
        public static unsafe int GetScanFilterUniqueMassCount(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_a")]
        public static unsafe double GetScanFilterParamA(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_b")]
        public static unsafe double GetScanFilterParamB(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_f")]
        public static unsafe double GetScanFilterParamF(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_r")]
        public static unsafe double GetScanFilterParamR(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_param_v")]
        public static unsafe double GetScanFilterParamV(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_scan_mode")]
        public static unsafe int GetScanFilterScanMode(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_accurate_mass")]
        public static unsafe int GetScanFilterAccurateMass(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ionization_mode")]
        public static unsafe int GetScanFilterIonizationMode(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_lock")]
        public static unsafe int GetScanFilterLock(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_turbo_scan")]
        public static unsafe int GetScanFilterTurboScan(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_corona")]
        public static unsafe int GetScanFilterCorona(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_dependent")]
        public static unsafe int GetScanFilterDependent(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_detector_value")]
        public static unsafe double GetScanFilterDetectorValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_compensation_voltage")]
        public static unsafe int GetScanEventCompensationVoltage(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_compensation_voltage_value")]
        public static unsafe double GetScanEventCompensationVoltageValue(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return -1.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_ms_order")]
        public static unsafe int GetScanEventMsOrder(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_mass_count")]
        public static unsafe int GetScanEventMassCount(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_precursor_mass")]
        public static unsafe double GetScanEventPrecursorMass(long arg0, int arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return 100.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_activation_type")]
        public static unsafe int GetScanEventActivationType(long arg0, int arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_event_collision_energy")]
        public static unsafe double GetScanEventCollisionEnergy(long arg0, int arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { if (arg1 == 2) return 28.0; return 30.0; } catch { return -1.0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_stats")]
        public static unsafe int GetScanStats(long arg0, int arg1, double* arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ultra")]
        public static unsafe int GetScanFilterUltra(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_wideband")]
        public static unsafe int GetScanFilterWideband(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_polarity")]
        public static unsafe int GetScanFilterPolarity(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_ms_order")]
        public static unsafe int GetScanFilterMsOrder(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_mass_analyzer")]
        public static unsafe int GetScanFilterMassAnalyzer(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_detector")]
        public static unsafe int GetScanFilterDetector(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_scan_filter_scan_data")]
        public static unsafe int GetScanFilterScanData(long arg0, int arg1)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_count")]
        public static unsafe int GetTrailerExtraCount(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_values")]
        public static unsafe int GetStatusLogValues(long arg0, int arg1, byte* arg2, int arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_header")]
        public static unsafe int GetStatusLogHeader(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_values_for_rt")]
        public static unsafe int GetStatusLogValuesForRt(long arg0, double arg1, byte* arg2, int arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_status_log_count")]
        public static unsafe int GetStatusLogCount(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_values")]
        public static unsafe int GetTrailerExtraValues(long arg0, int arg1, byte* arg2, int arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_trailer_extra_header")]
        public static unsafe int GetTrailerExtraHeader(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_file_description")]
        public static unsafe int GetFileDescription(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_modified_date")]
        public static unsafe int GetModifiedDate(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_created_logon")]
        public static unsafe int GetWhoCreatedLogon(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_modified_id")]
        public static unsafe int GetWhoModifiedId(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_who_modified_logon")]
        public static unsafe int GetWhoModifiedLogon(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_barcode")]
        public static unsafe int GetSampleBarcode(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_id")]
        public static unsafe int GetSampleId(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_name")]
        public static unsafe int GetSampleName(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_vial")]
        public static unsafe int GetSampleVial(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_comment")]
        public static unsafe int GetSampleComment(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_axis_label_x")]
        public static unsafe int GetInstrumentAxisLabelX(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_axis_label_y")]
        public static unsafe int GetInstrumentAxisLabelY(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_flags")]
        public static unsafe int GetInstrumentFlags(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_units")]
        public static unsafe int GetInstrumentUnits(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_is_valid")]
        public static unsafe int GetInstrumentIsValid(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_has_accurate_mass_precursors")]
        public static unsafe int GetInstrumentHasAccurateMassPrecursors(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_is_tsq_quantum_file")]
        public static unsafe int GetInstrumentIsTsqQuantumFile(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_method_count")]
        public static unsafe int GetInstrumentMethodCount(long arg0, int arg1, long arg2, long arg3, long arg4, long arg5, long arg6)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return f.InstrumentMethodsCount; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_instrument_method")]
        public static unsafe int GetInstrumentMethod(long arg0, int arg1, byte* arg2, int arg3)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return CopyString(f.GetInstrumentMethod(arg1), arg2, arg3); } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_tray_index")]
        public static unsafe int GetAutosamplerTrayIndex(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return -1; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vial_index")]
        public static unsafe int GetAutosamplerVialIndex(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return -1; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_tray_name")]
        public static unsafe int GetAutosamplerTrayName(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return CopyString("R", arg1, arg2); } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_tray_shape")]
        public static unsafe int GetAutosamplerTrayShape(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vials_per_tray")]
        public static unsafe int GetAutosamplerVialsPerTray(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vials_per_tray_x")]
        public static unsafe int GetAutosamplerVialsPerTrayX(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_autosampler_vials_per_tray_y")]
        public static unsafe int GetAutosamplerVialsPerTrayY(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return 0; } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_instrument_method_file")]
        public static unsafe int GetSampleInstrumentMethodFile(long arg0, byte* arg1, int arg2)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return 0;
                try { return CopyString(f.SampleInformation.InstrumentMethodFile, arg1, arg2); } catch { return 0; }
            });
        }

        [UnmanagedCallersOnly(EntryPoint = "get_sample_injection_volume")]
        public static unsafe double GetSampleInjectionVolume(long arg0)
        {
            return RunOnWorker(() => {
                if (!_openFiles.TryGetValue(arg0, out var f)) return -1.0;
                try { return f.SampleInformation.InjectionVolume; } catch { return -1.0; }
            });
        }
    }
}
