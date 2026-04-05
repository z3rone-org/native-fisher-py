from ... import TraceType

class GenericDataTypes:
    NULL = 0
    CHAR = 1
    TRUEFALSE = 2
    YESNO = 3
    ONOFF = 4
    UCHAR = 5
    SHORT = 6
    USHORT = 7
    LONG = 8
    ULONG = 9
    FLOAT = 10
    DOUBLE = 11
    CHAR_STRING = 12
    WCHAR_STRING = 13

class Range:
    def __init__(self, low=0.0, high=0.0):
        self.low = low
        self.high = high

class ChromatogramTraceSettings:
    def __init__(self, trace_type=TraceType.TIC):
        self.trace = trace_type
        self.filter = ""
        self.mass_ranges = []

class ChromatogramSignal:
    pass

class SpectrumPacketType:
    pass

class Scan:
    pass

class SampleType:
    Unknown = 0
    Sample = 1
    Blank = 2
    Standard = 3
    QC = 4
    Unassigned = 5
