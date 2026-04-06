import numpy as np

def is_number(x): 
    return isinstance(x, (int, float, np.number))

def datetime_net_to_py(x): return x
def datetime_py_to_net(x): return x
def to_net_list(x, t=None): return x
def to_net_array(x, t=None): return x
def to_py_list(x): return x

class Any(object): pass
class List(list): pass
class Tuple(tuple): pass
class Array(list): pass
class DateTime(object): pass
class Double(float): pass
class clr(object): pass
class datetime(object): pass
class generic(object): pass
