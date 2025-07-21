class FileConversionException(Exception):
    """Exception raised when file conversion fails"""
    pass


class UnsupportedFormatException(FileConversionException):
    """Exception raised when file format is not supported"""
    pass


class FailedConversionAttempt(Exception):
    """Exception to track conversion attempt failures"""
    pass