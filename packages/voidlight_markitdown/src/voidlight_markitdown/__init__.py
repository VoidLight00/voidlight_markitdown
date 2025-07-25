from .__about__ import __version__
from ._voidlight_markitdown import (
    VoidLightMarkItDown, 
    DocumentConverterResult,
    PRIORITY_SPECIFIC_FILE_FORMAT,
    PRIORITY_GENERIC_FILE_FORMAT,
)
from ._stream_info import StreamInfo
from ._base_converter import DocumentConverter
from ._exceptions import (
    FileConversionException,
    UnsupportedFormatException,
    MissingDependencyException,
    MISSING_DEPENDENCY_MESSAGE,
    VoidLightMarkItDownException,
    FailedConversionAttempt,
)
from ._logging import (
    setup_logging,
    get_logger,
    get_performance_logger,
    log_performance,
    LoggingMixin,
)

# Alias for compatibility
MarkItDown = VoidLightMarkItDown

__all__ = [
    "__version__",
    "VoidLightMarkItDown",
    "MarkItDown",  # Compatibility alias
    "DocumentConverterResult",
    "DocumentConverter",
    "StreamInfo",
    "PRIORITY_SPECIFIC_FILE_FORMAT",
    "PRIORITY_GENERIC_FILE_FORMAT",
    "FileConversionException",
    "UnsupportedFormatException",
    "MissingDependencyException",
    "VoidLightMarkItDownException",
    "FailedConversionAttempt",
    "MISSING_DEPENDENCY_MESSAGE",
    # Logging utilities
    "setup_logging",
    "get_logger",
    "get_performance_logger",
    "log_performance",
    "LoggingMixin",
]