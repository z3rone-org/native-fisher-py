from typing import List, Tuple, Any
import datetime as dt_factory
from datetime import timezone

class DateTime(dt_factory.datetime):
    @property
    def Date(self): return self
    @property
    def DayOfWeek(self): return self.weekday()
    @property
    def DayOfYear(self): return self.timetuple().tm_yday
    @property
    def Ticks(self): return int(self.timestamp() * 10000000)
    @property
    def TimeOfDay(self): return self.time()
    
    UnixEpoch = dt_factory.datetime(1970, 1, 1)
    MaxValue = dt_factory.datetime(9999, 12, 31)
    MinValue = dt_factory.datetime(1, 1, 1)
    
    @staticmethod
    def Overloads(*args): return None
    
    def Add(self, *args): return self
    def AddDays(self, *args): return self
    def AddHours(self, *args): return self
    def AddMilliseconds(self, *args): return self
    def AddMinutes(self, *args): return self
    def AddMonths(self, *args): return self
    def AddSeconds(self, *args): return self
    def AddTicks(self, *args): return self
    def AddYears(self, *args): return self
    def GetDateTimeFormats(self, *args): return []
    def ToBinary(self, *args): return 0
    def ToFileTime(self, *args): return 0
    def ToFileTimeUtc(self, *args): return 0
    def ToOADate(self, *args): return 0.0
    
    # get_ prefix for properties
    def get_Date(self): return self
    def get_Day(self): return self.day
    def get_DayOfWeek(self): return self.DayOfWeek
    def get_DayOfYear(self): return self.DayOfYear
    def get_Hour(self): return self.hour
    def get_Kind(self): return 0
    def get_Millisecond(self): return self.microsecond // 1000
    def get_Minute(self): return self.minute
    def get_Month(self): return self.month
    def get_Now(self): return dt_factory.datetime.now()
    def get_Second(self): return self.second
    def get_Ticks(self): return self.Ticks
    def get_TimeOfDay(self): return self.time()
    def get_Today(self): return self.today()
    def get_UtcNow(self): return dt_factory.datetime.now(timezone.utc)
    def get_Year(self): return self.year

    @staticmethod
    def get_Now(): return dt_factory.datetime.now()
    @staticmethod
    def get_UtcNow(): return dt_factory.datetime.now(timezone.utc)
    @staticmethod
    def get_Today(): return dt_factory.datetime.now()

    @staticmethod
    def FromBinary(v): return DateTime.now()
    @staticmethod
    def FromFileTime(v): return DateTime.now()
    @staticmethod
    def FromFileTimeUtc(v): return DateTime.now()
    @staticmethod
    def FromOADate(v): return DateTime.now()
    @staticmethod
    def SpecifyKind(v, k): return v
    
    def CompareTo(self, other): return 0
    def GetHashCode(self): return 0
    def GetTypeCode(self): return 0
    def MemberwiseClone(self): return self
    @staticmethod
    def ReferenceEquals(a, b): return a is b

    def op_Addition(self, *args): return self
    def op_Equality(self, *args): return True
    def op_GreaterThan(self, *args): return False
    def op_GreaterThanOrEqual(self, *args): return True
    def op_Inequality(self, *args): return False
    def op_LessThan(self, *args): return False
    def op_LessThanOrEqual(self, *args): return True
    def op_Subtraction(self, *args): return self

class Array(object):
    @property
    def IsFixedSize(self): return True
    @property
    def IsReadOnly(self): return True
    @property
    def IsSynchronized(self): return False
    @property
    def Length(self): return 0
    @property
    def LongLength(self): return 0
    @property
    def Rank(self): return 1
    @property
    def SyncRoot(self): return self
    
    def Equals(self, *args): return True
    def Finalize(self): pass
    def GetEnumerator(self): return None
    def GetHashCode(self): return 0
    def GetLength(self, r): return 0
    def GetLongLength(self, r): return 0
    def GetLowerBound(self, r): return 0
    def GetType(self): return None
    def GetUpperBound(self, r): return 0
    def GetValue(self, *args): return None
    def Initialize(self): pass
    def MemberwiseClone(self): return self
    @staticmethod
    def Overloads(*args): return None
    @staticmethod
    def ReferenceEquals(*args): return True
    def SetValue(self, *args): pass
    def ToString(self): return "Array"
    
    def append(self, x): pass
    def clear(self): pass
    def count(self): return 0
    def extend(self, x): pass
    def index(self, x): return -1
    def insert(self, i, x): pass
    def pop(self, i=-1): return None
    def remove(self, x): pass
    def reverse(self): pass
    
    def get_IsFixedSize(self): return True
    def get_IsReadOnly(self): return True
    def get_IsSynchronized(self): return False
    def get_Length(self): return 0
    def get_LongLength(self): return 0
    def get_Rank(self): return 1
    def get_SyncRoot(self): return self

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
    
    def CompareTo(self, *args): return 0
    def Equals(self, *args): return True
    def Finalize(self): pass
    def GetHashCode(self): return 0
    def GetType(self): return None
    def GetTypeCode(self): return 0
    def MemberwiseClone(self): return self
    @staticmethod
    def Overloads(*args): return None
    @staticmethod
    def ReferenceEquals(*args): return True
    def ToString(self): return "0.0"
    def TryFormat(self, *args): return True
    def op_Equality(self, *args): return True
    def op_GreaterThan(self, *args): return False
    def op_GreaterThanOrEqual(self, *args): return True
    def op_Inequality(self, *args): return False
    def op_LessThan(self, *args): return False
    def op_LessThanOrEqual(self, *args): return True

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

def datetime_net_to_py(dt_val: int) -> dt_factory.datetime:
    return dt_factory.datetime.fromtimestamp(dt_val)

def is_number(s: Any) -> bool:
    try:
        float(s)
        return True
    except:
        return False

def to_net_list(py_list: list) -> list:
    return py_list

# clr stubs
class clr_stub(object):
    @staticmethod
    def AddReference(p): pass
    @staticmethod
    def FindAssembly(name): return None
    @staticmethod
    def GetClrType(t): return None
    @staticmethod
    def ListAssemblies(v): return []
    Python = None
    System = None
    ThermoFisher = None
    @staticmethod
    def clrmethod(*args): return None
    @staticmethod
    def clrproperty(*args): return None
    @staticmethod
    def getPreload(): return False
    loader = None
    @staticmethod
    def setPreload(p): pass

# Parity aliases
Any = Any
Tuple = Tuple
List = List
datetime = DateTime
Double = Double
Array = Array
clr = clr_stub
datetime_py_to_net = lambda x: 0
generic = object
to_net_array = lambda x: x
to_py_list = lambda x: x
