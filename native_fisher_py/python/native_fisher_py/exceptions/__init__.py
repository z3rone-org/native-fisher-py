class RawFileException(Exception):
    """Base exception for native_fisher_py errors."""
    pass

class CoreException(RawFileException):
    """Base exception for core errors."""
    pass

raw_file_exception = None
core_exception = None
