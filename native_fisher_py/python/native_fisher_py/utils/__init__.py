from typing import List, Tuple, Any
from datetime import datetime

class DateTime(object):
    Now = datetime.now()
    Today = datetime.now().date()
    UtcNow = datetime.utcnow()
    UnixEpoch = datetime(1970, 1, 1)
    MaxValue = datetime(9999, 12, 31)
    MinValue = datetime(1, 1, 1)
    @staticmethod
    def Compare(*args, **kwargs): return 0
    @staticmethod
    def DaysInMonth(*args, **kwargs): return 30
    @staticmethod
    def FromBinary(*args, **kwargs): return DateTime()
    @staticmethod
    def FromFileTime(*args, **kwargs): return DateTime()
    @staticmethod
    def FromFileTimeUtc(*args, **kwargs): return DateTime()
    @staticmethod
    def FromOADate(*args, **kwargs): return DateTime()
    @staticmethod
    def IsDaylightSavingTime(*args, **kwargs): return False
    @staticmethod
    def IsLeapYear(*args, **kwargs): return False
    @staticmethod
    def Parse(*args, **kwargs): return DateTime()
    @staticmethod
    def ParseExact(*args, **kwargs): return DateTime()
    @staticmethod
    def SpecifyKind(*args, **kwargs): return DateTime()
    @staticmethod
    def TryParse(*args, **kwargs): return True, DateTime()
    @staticmethod
    def TryParseExact(*args, **kwargs): return True, DateTime()

class Array(object):
    @staticmethod
    def AsReadOnly(*args, **kwargs): return []
    @staticmethod
    def BinarySearch(*args, **kwargs): return -1
    @staticmethod
    def Clear(*args, **kwargs): pass
    @staticmethod
    def Clone(*args, **kwargs): return []
    @staticmethod
    def ConstrainedCopy(*args, **kwargs): pass
    @staticmethod
    def ConvertAll(*args, **kwargs): return []
    @staticmethod
    def Copy(*args, **kwargs): pass
    @staticmethod
    def CopyTo(*args, **kwargs): pass
    @staticmethod
    def CreateInstance(*args, **kwargs): return []
    @staticmethod
    def Empty(*args, **kwargs): return []
    @staticmethod
    def Exists(*args, **kwargs): return False
    @staticmethod
    def Fill(*args, **kwargs): pass
    @staticmethod
    def Find(*args, **kwargs): return None
    @staticmethod
    def FindAll(*args, **kwargs): return []
    @staticmethod
    def FindIndex(*args, **kwargs): return -1
    @staticmethod
    def FindLast(*args, **kwargs): return None
    @staticmethod
    def FindLastIndex(*args, **kwargs): return -1
    @staticmethod
    def ForEach(*args, **kwargs): pass
    @staticmethod
    def IndexOf(*args, **kwargs): return -1
    @staticmethod
    def LastIndexOf(*args, **kwargs): return -1
    @staticmethod
    def Resize(*args, **kwargs): pass
    @staticmethod
    def Reverse(*args, **kwargs): pass
    @staticmethod
    def Sort(*args, **kwargs): pass
    @staticmethod
    def TrueForAll(*args, **kwargs): return True

class Double(object):
    Epsilon = 4.94065645841247E-324
    MaxValue = 1.7976931348623157E+308
    MinValue = -1.7976931348623157E+308
    NaN = float('nan')
    NegativeInfinity = float('-inf')
    PositiveInfinity = float('inf')
    @staticmethod
    def IsFinite(v): return True
    @staticmethod
    def IsInfinity(v): return False
    @staticmethod
    def IsNaN(v): return False
    @staticmethod
    def IsNegative(v): return False
    @staticmethod
    def IsNegativeInfinity(v): return False
    @staticmethod
    def IsNormal(v): return True
    @staticmethod
    def IsPositiveInfinity(v): return False
    @staticmethod
    def IsSubnormal(v): return False
    @staticmethod
    def Parse(s): return float(s)
    @staticmethod
    def TryParse(s): return True, float(s)

def datetime_net_to_py(dt_val: int) -> datetime:
    return datetime.fromtimestamp(dt_val)

def is_number(s: Any) -> bool:
    try:
        float(s)
        return True
    except:
        return False

def to_net_list(py_list: list) -> list:
    return py_list

# Parity aliases
Any = Any
Tuple = Tuple
List = List
datetime = DateTime
Double = Double
Array = Array
clr = object
datetime_py_to_net = lambda x: 0
generic = object
to_net_array = lambda x: x
to_py_list = lambda x: x
