from ... import TraceType

class GenericDataTypes:
    pass

class ChromatogramTraceSettings:
    def __init__(self, trace_type=1):
        self.trace_type = trace_type

class ChromatogramSignal:
    pass

class SpectrumPacketType:
    pass

class Scan:
    pass

class Range:
    def __init__(self, low=0.0, high=0.0):
        self.low = low
        self.high = high

class SampleType:
    Unknown = 0
    Sample = 1
    Blank = 2
    Standard = 3
    # ...
