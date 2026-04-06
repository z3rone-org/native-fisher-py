class CoreException(Exception): pass
class RawFileException(CoreException): pass
class NoSelectedDeviceException(RawFileException): pass
class NoSelectedMsDeviceException(RawFileException): pass

# Parity aliases
core_exception = None 
raw_file_exception = None 

def _init_exceptions_():
    global core_exception, raw_file_exception
    import sys
    this = sys.modules[__name__]
    core_exception = this
    raw_file_exception = this
