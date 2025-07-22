import sys
import io

from typing import BinaryIO, Any

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo
from .._exceptions import MissingDependencyException, MISSING_DEPENDENCY_MESSAGE
from .._logging import LoggingMixin, log_converter_metrics


# Try loading optional (but in this case, required) dependencies
# Save reporting of any exceptions for later
_dependency_exc_info = None
try:
    import pdfminer
    import pdfminer.high_level
except ImportError:
    # Preserve the error and stack trace for later
    _dependency_exc_info = sys.exc_info()


ACCEPTED_MIME_TYPE_PREFIXES = [
    "application/pdf",
    "application/x-pdf",
]

ACCEPTED_FILE_EXTENSIONS = [".pdf"]


class PdfConverter(DocumentConverter, LoggingMixin):
    """
    Converts PDFs to Markdown. Most style information is ignored, so the results are essentially plain-text.
    """

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    @log_converter_metrics("pdf")
    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Check the dependencies
        if _dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".pdf",
                    feature="pdf",
                )
            ) from _dependency_exc_info[
                1
            ].with_traceback(  # type: ignore[union-attr]
                _dependency_exc_info[2]
            )

        # Check for Korean mode
        korean_mode = kwargs.get("korean_mode", False)
        if korean_mode:
            self.log_debug("PDF conversion in Korean mode")
        
        assert isinstance(file_stream, io.IOBase)  # for mypy
        
        # Extract text from PDF
        self.log_debug("Extracting text from PDF using pdfminer")
        text = pdfminer.high_level.extract_text(file_stream)
        
        # If Korean mode is enabled, we could add Korean-specific PDF processing here
        # For now, pdfminer should handle Korean text extraction reasonably well
        
        self.log_debug(f"Extracted {len(text)} characters from PDF")
        
        return DocumentConverterResult(
            markdown=text,
        )