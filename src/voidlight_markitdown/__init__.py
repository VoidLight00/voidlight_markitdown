"""
VoidLight MarkItDown - Enhanced document to Markdown converter with Korean language support.

This package provides:
- Document conversion to Markdown from various formats
- Enhanced Korean text processing capabilities
- Extensible plugin architecture
- Command-line interface
"""

from .__about__ import __version__, __author__, __email__

# Core functionality
from .core.markitdown import VoidLightMarkItDown
from .core.exceptions import (
    VoidLightMarkItDownException,
    MarkitdownError,  # Alias for backward compatibility
    UnsupportedFormatException,
    UnsupportedFormatError,  # Alias for backward compatibility
    MissingDependencyException,
    FileConversionException,
)
from .core.stream_info import StreamInfo

# Base converter classes
from .converters.base import DocumentConverter, DocumentConverterResult, BaseConverter

# Korean utilities (public API)
from .korean.utils import (
    is_korean_text,
    extract_korean_keywords,
    KoreanTextProcessor,
)

# Logging utilities
from .utils.logging import (
    setup_logging,
    get_logger,
    set_log_level,
)

# Main API class alias for backward compatibility
MarkItDown = VoidLightMarkItDown

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Main classes
    "VoidLightMarkItDown",
    "MarkItDown",  # Backward compatibility alias
    
    # Exceptions
    "VoidLightMarkItDownException",
    "MarkitdownError",  # Backward compatibility alias
    "UnsupportedFormatException",
    "UnsupportedFormatError",  # Backward compatibility alias
    "MissingDependencyException",
    "FileConversionException",
    
    # Core types
    "StreamInfo",
    "DocumentConverter",
    "BaseConverter",  # Backward compatibility alias
    "DocumentConverterResult",
    
    # Korean utilities
    "is_korean_text",
    "extract_korean_keywords",
    "KoreanTextProcessor",
    
    # Logging
    "setup_logging",
    "get_logger",
    "set_log_level",
]