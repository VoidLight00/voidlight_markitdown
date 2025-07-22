from .__about__ import __version__
from ._voidlight_markitdown import VoidLightMarkItDown, DocumentConverterResult
from ._stream_info import StreamInfo
from ._base_converter import (
    DocumentConverter,
    PRIORITY_SPECIFIC_FILE_FORMAT,
    PRIORITY_GENERIC_FILE_FORMAT,
)
from ._exceptions import (
    FileConversionException,
    UnsupportedFormatException,
    MissingDependencyException,
    MISSING_DEPENDENCY_MESSAGE,
    VoidLightMarkItDownException,
    FailedConversionAttempt,
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
]