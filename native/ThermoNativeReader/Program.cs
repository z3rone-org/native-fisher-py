using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using ThermoFisher.CommonCore.Data;
using ThermoFisher.CommonCore.Data.Business;
using ThermoFisher.CommonCore.Data.Interfaces;
using ThermoFisher.CommonCore.Data.FilterEnums;
using ThermoFisher.CommonCore.RawFileReader;

namespace ThermoNativeReader
{
    class Program
    {
        private static readonly Dictionary<long, IRawDataPlus> _openFiles = new Dictionary<long, IRawDataPlus>();
        private static long _nextHandle = 1;
        private static readonly BlockingCollection<Action> _workQueue = new BlockingCollection<Action>();
        private static StreamWriter _log;

        static void Main(string[] args)
        {
            _log = new StreamWriter("/tmp/server.log", false) { AutoFlush = true };
            _log.WriteLine("Server starting...");

            Thread workerThread = new Thread(WorkerLoop);
            workerThread.IsBackground = true;
            workerThread.Start();
            _log.WriteLine("Worker loop started");

            using (var stdin = Console.OpenStandardInput())
            using (var stdout = Console.OpenStandardOutput())
            using (var reader = new BinaryReader(stdin))
            using (var writer = new BinaryWriter(stdout))
            {
                while (true)
                {
                    try
                    {
                        uint len = reader.ReadUInt32();
                        byte cmd = reader.ReadByte();
                        _log.WriteLine($"Received command 0x{cmd:02X} (len {len})");
                        
                        switch (cmd)
                        {
                            case 0x01: HandleOpen(reader, writer); break;
                            case 0x02: HandleClose(reader, writer); break;
                            case 0x03: HandleGetStats(reader, writer); break;
                            case 0x04: HandleGetCentroid(reader, writer); break;
                            case 0x05: HandleGetNumScans(reader, writer); break;
                            case 0x06: HandleGetScanRT(reader, writer); break;
                            case 0x07: HandleGetScanNumberFromRT(reader, writer); break;
                            case 0x08: HandleGetScanEvent(reader, writer); break;
                            case 0x09: HandleGetFileHeader(reader, writer); break;
                            case 0x0A: HandleGetInstrumentCount(reader, writer); break;
                            case 0x0B: HandleGetMsOrder(reader, writer); break;
                            case 0x0C: HandleGetPrecursorMass(reader, writer); break;
                            case 0x0D: HandleGetEndTime(reader, writer); break;
                            case 0x0E: HandleGetFirstScan(reader, writer); break;
                            case 0x0F: HandleGetLastScan(reader, writer); break;
                            case 0x10: HandleGetMs1ScanFromRt(reader, writer); break;
                            case 0x11: HandleGetMs2ScanFromRt(reader, writer); break;
                            case 0x12: HandleGetChromatogram(reader, writer); break;
                            case 0x99: HandleTestOpen(reader, writer); break;
                            case 0xFF: return;
                            default: SendError(writer, "Unknown command"); break;
                        }
                    }
                    catch (EndOfStreamException) { break; }
                    catch (Exception ex)
                    {
                        _log.WriteLine($"Loop error: {ex}");
                        break;
                    }
                }
            }
        }

        private static void WorkerLoop()
        {
            _log.WriteLine("Worker loop started");
            foreach (var action in _workQueue.GetConsumingEnumerable())
            {
                try { action(); } catch (Exception ex) { _log.WriteLine($"Worker action error: {ex}"); }
            }
        }

        private static T RunOnWorker<T>(Func<T> func)
        {
            _log.WriteLine("RunOnWorker: Queueing task");
            var tcs = new TaskCompletionSource<T>();
            _workQueue.Add(() =>
            {
                _log.WriteLine("RunOnWorker: Starting task execution");
                try { 
                    var res = func();
                    _log.WriteLine("RunOnWorker: Task execution successful");
                    tcs.SetResult(res); 
                }
                catch (Exception ex) { 
                    _log.WriteLine($"RunOnWorker: Task execution failed: {ex}");
                    tcs.SetException(ex); 
                }
            });
            var result = tcs.Task.GetAwaiter().GetResult();
            _log.WriteLine("RunOnWorker: Returning result");
            return result;
        }

        private static string ReadStringFixed(BinaryReader reader)
        {
            int len = reader.ReadInt32();
            if (len == 0) return "";
            byte[] bytes = reader.ReadBytes(len);
            return System.Text.Encoding.UTF8.GetString(bytes);
        }

        private static void SendError(BinaryWriter writer, string message)
        {
            _log.WriteLine($"Sending error: {message}");
            var bytes = System.Text.Encoding.UTF8.GetBytes(message);
            writer.Write(bytes.Length + 1);
            writer.Write((byte)0x01);
            writer.Write(bytes);
            writer.Flush();
        }

        private static void HandleOpen(BinaryReader reader, BinaryWriter writer)
        {
            string path = ReadStringFixed(reader);
            path = Path.GetFullPath(path);
            _log.WriteLine($"Opening {path} using FileFactory...");
            try
            {
                var rawFile = (IRawDataPlus)RawFileReaderAdapter.FileFactory(path);
                _log.WriteLine($"FileFactory returned {(rawFile == null ? "null" : "object")}");
                if (rawFile == null) { SendError(writer, "FileFactory returned null"); return; }
                
                _log.WriteLine("Selecting instrument...");
                long h = RunOnWorker(() => {
                    rawFile.SelectInstrument(Device.MS, 1);
                    long handle = Interlocked.Increment(ref _nextHandle);
                    _openFiles[handle] = rawFile;
                    return handle;
                });

                _log.WriteLine($"File opened with handle {h}");
                using var ms = new MemoryStream();
                using var bw = new BinaryWriter(ms);
                bw.Write((byte)0x00); // status
                bw.Write(h);
                bw.Flush();

                byte[] buffer = ms.ToArray();
                writer.Write(buffer.Length);
                writer.Write(buffer);
                writer.Flush();
            }
            catch (Exception ex)
            {
                _log.WriteLine($"Open error: {ex}");
                SendError(writer, $"Open error: {ex.Message}");
            }
        }

        private static void HandleClose(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            RunOnWorker(() => {
                if (_openFiles.Remove(handle, out var f)) f.Dispose();
                return 0;
            });
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetNumScans(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int count = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.RunHeader.LastSpectrum - f.RunHeader.FirstSpectrum + 1 : 0);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(count);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetScanRT(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = reader.ReadInt32();
            double rt = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.RetentionTimeFromScanNumber(scan) : 0.0);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(rt);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetScanNumberFromRT(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            double rt = reader.ReadDouble();
            int scan = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.ScanNumberFromRetentionTime(rt) : 0);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(scan);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetStats(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = reader.ReadInt32();
            if (!_openFiles.TryGetValue(handle, out var f)) { SendError(writer, "Handle not found"); return; }
            
            var res = RunOnWorker(() => {
                var s = f.GetScanStatsForScanNumber(scan);
                return s;
            });
            if (res == null) { SendError(writer, "No stats"); return; }

            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(res.StartTime);
            bw.Write(res.LowMass);
            bw.Write(res.HighMass);
            bw.Write(res.TIC);
            bw.Write(res.BasePeakMass);
            bw.Write(res.BasePeakIntensity);
            bw.Write(res.PacketCount);
            bw.Write(res.IsCentroidScan);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetCentroid(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = reader.ReadInt32();
            if (!_openFiles.TryGetValue(handle, out var f)) { SendError(writer, "Handle not found"); return; }
            
            try {
                var data = RunOnWorker(() => {
                    var s = f.GetScanStatsForScanNumber(scan);
                    double[] masses, intensities;
                    double bpNoise = 0, bpRes = 0;

                    if (s.IsCentroidScan)
                    {
                        var seg = f.GetSegmentedScanFromScanNumber(scan, s);
                        masses = seg.Positions;
                        intensities = seg.Intensities;
                    }
                    else
                    {
                        var stream = f.GetCentroidStream(scan, true);
                        masses = stream.Masses;
                        intensities = stream.Intensities;
                        bpNoise = stream.BasePeakNoise;
                        bpRes = stream.BasePeakResolution;
                    }
                    return new { Masses = masses, Intensities = intensities, BasePeakNoise = bpNoise, BasePeakResolution = bpRes };
                });

                using var ms = new MemoryStream();
                using var bw = new BinaryWriter(ms);
                bw.Write((byte)0x00); // status
                bw.Write(data.Masses.Length);
                for (int i = 0; i < data.Masses.Length; i++) bw.Write(data.Masses[i]);
                for (int i = 0; i < data.Intensities.Length; i++) bw.Write(data.Intensities[i]);
                bw.Write(data.BasePeakNoise);
                bw.Write(data.BasePeakResolution);
                bw.Flush();

                byte[] buffer = ms.ToArray();
                writer.Write(buffer.Length);
                writer.Write(buffer);
                writer.Flush();
            }
            catch (Exception ex)
            {
                _log.WriteLine($"Centroid error: {ex}");
                SendError(writer, $"Centroid error: {ex.Message}");
            }
        }

        private static void HandleGetScanEvent(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = reader.ReadInt32();
            string evt = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.GetScanEventStringForScanNumber(scan) : "");
            byte[] evtBytes = System.Text.Encoding.UTF8.GetBytes(evt);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(evtBytes.Length);
            bw.Write(evtBytes);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetFileHeader(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            if (!_openFiles.TryGetValue(handle, out var f)) { SendError(writer, "Handle not found"); return; }
            
            var res = RunOnWorker(() => new { f.FileName, f.CreationDate });
            
            byte[] fnBytes = System.Text.Encoding.UTF8.GetBytes(res.FileName);
            byte[] cdBytes = System.Text.Encoding.UTF8.GetBytes(res.CreationDate.ToString());
            writer.Write(1 + 4 + fnBytes.Length + 4 + cdBytes.Length);
            writer.Write((byte)0x00);
            writer.Write(fnBytes.Length);
            writer.Write(fnBytes);
            writer.Write(cdBytes.Length);
            writer.Write(cdBytes);
            writer.Flush();
        }

        private static void HandleGetInstrumentCount(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int count = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.InstrumentCount : 0);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(count);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetFirstScan(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.RunHeader.FirstSpectrum : 0);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(scan);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetLastScan(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.RunHeader.LastSpectrum : 0);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(scan);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetMs1ScanFromRt(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            double rt = reader.ReadDouble();
            int scan = RunOnWorker(() => {
                if (!_openFiles.TryGetValue(handle, out var f)) return 0;
                int bestScan = 0;
                double minDiff = double.MaxValue;
                for (int i = f.RunHeader.FirstSpectrum; i <= f.RunHeader.LastSpectrum; i++)
                {
                    if (f.GetScanEventForScanNumber(i).MSOrder == MSOrderType.Ms)
                    {
                        double diff = Math.Abs(f.RetentionTimeFromScanNumber(i) - rt);
                        if (diff < minDiff) { minDiff = diff; bestScan = i; }
                    }
                }
                return bestScan;
            });
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(scan);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetMs2ScanFromRt(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            double rt = reader.ReadDouble();
            double pmz = reader.ReadDouble();
            double tol = reader.ReadDouble();

            int scan = RunOnWorker(() => {
                if (!_openFiles.TryGetValue(handle, out var f)) return 0;
                int bestScan = 0;
                double minDiff = double.MaxValue;
                for (int i = f.RunHeader.FirstSpectrum; i <= f.RunHeader.LastSpectrum; i++)
                {
                    var evt = f.GetScanEventForScanNumber(i);
                    if (evt.MSOrder == MSOrderType.Ms2)
                    {
                        if (pmz <= 0 || Math.Abs(evt.GetMass(0) - pmz) <= tol)
                        {
                            double diff = Math.Abs(f.RetentionTimeFromScanNumber(i) - rt);
                            if (diff < minDiff) { minDiff = diff; bestScan = i; }
                        }
                    }
                }
                return bestScan;
            });
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(scan);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetChromatogram(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int traceType = reader.ReadInt32();
            string filter = ReadStringFixed(reader);
            int rangeCount = reader.ReadInt32();
            double[] lows = new double[rangeCount];
            double[] highs = new double[rangeCount];
            for (int i = 0; i < rangeCount; i++) { lows[i] = reader.ReadDouble(); highs[i] = reader.ReadDouble(); }
            int startScan = reader.ReadInt32();
            int endScan = reader.ReadInt32();

            var data = RunOnWorker(() => {
                if (!_openFiles.TryGetValue(handle, out var f)) return null;
                var settings = new ChromatogramTraceSettings((TraceType)traceType) { Filter = filter };
                settings.MassRanges = new ThermoFisher.CommonCore.Data.Business.Range[rangeCount];
                for (int i = 0; i < rangeCount; i++) settings.MassRanges[i] = new ThermoFisher.CommonCore.Data.Business.Range(lows[i], highs[i]);
                
                var chrom = f.GetChromatogramData(new[] { settings }, startScan, endScan);
                return new { Times = chrom.PositionsArray[0], Intensities = chrom.IntensitiesArray[0] };
            });

            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            if (data == null) { bw.Write(0); }
            else {
                bw.Write(data.Times.Length);
                for (int i = 0; i < data.Times.Length; i++) bw.Write(data.Times[i]);
                for (int i = 0; i < data.Intensities.Length; i++) bw.Write(data.Intensities[i]);
            }
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }


        private static void HandleGetMsOrder(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = reader.ReadInt32();
            int order = RunOnWorker(() => {
                if (_openFiles.TryGetValue(handle, out var f))
                {
                    var evt = f.GetScanEventForScanNumber(scan);
                    return (int)evt.MSOrder;
                }
                return 0;
            });
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(order);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetPrecursorMass(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            int scan = reader.ReadInt32();
            var rawFile = _openFiles[handle];
            double mass = RunOnWorker(() => {
                var scanEvent = rawFile.GetScanEventForScanNumber(scan);
                return scanEvent.GetMass(0);
            });
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(mass);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleGetEndTime(BinaryReader reader, BinaryWriter writer)
        {
            long handle = reader.ReadInt64();
            double endTime = RunOnWorker(() => _openFiles.TryGetValue(handle, out var f) ? f.RunHeaderEx.EndTime : 0.0);
            
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            bw.Write((byte)0x00); // status
            bw.Write(endTime);
            bw.Flush();

            byte[] buffer = ms.ToArray();
            writer.Write(buffer.Length);
            writer.Write(buffer);
            writer.Flush();
        }

        private static void HandleTestOpen(BinaryReader reader, BinaryWriter writer)
        {
            string path = ReadStringFixed(reader);
            path = Path.GetFullPath(path);
            _log.WriteLine($"TestOpen: {path}");
            try
            {
                // NativeAOT was the problem. Standard FileFactory on Main thread should work now.
                using (var rawFile = (IRawDataPlus)RawFileReaderAdapter.FileFactory(path))
                {
                    using var ms = new MemoryStream();
                    using var bw = new BinaryWriter(ms);
                    bw.Write((byte)0x00); // status
                    bw.Write(rawFile != null ? 1 : 0);
                    bw.Flush();

                    byte[] buffer = ms.ToArray();
                    writer.Write(buffer.Length);
                    writer.Write(buffer);
                    writer.Flush();
                }
            }
            catch (Exception ex)
            {
                _log.WriteLine($"TestOpen Error: {ex}");
                SendError(writer, ex.Message);
            }
        }
    }
}
