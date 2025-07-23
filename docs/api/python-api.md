# Python API Reference

Complete reference for the VoidLight MarkItDown Python API.

## Table of Contents

1. [VoidLightMarkItDown Class](#voidlightmarkitdown-class)
2. [Configuration](#configuration)
3. [Conversion Methods](#conversion-methods)
4. [Result Objects](#result-objects)
5. [Converters](#converters)
6. [Korean Module](#korean-module)
7. [Utilities](#utilities)
8. [Exceptions](#exceptions)

## VoidLightMarkItDown Class

The main class for document conversion.

### Constructor

```python
class VoidLightMarkItDown:
    def __init__(
        self,
        korean_mode: bool = False,
        config: Optional[Config] = None,
        stream_mode: bool = False,
        **kwargs
    ):
        """
        Initialize VoidLight MarkItDown converter.
        
        Args:
            korean_mode: Enable Korean language processing
            config: Configuration object
            stream_mode: Enable streaming for large files
            **kwargs: Additional configuration options
        """
```

### Basic Example

```python
from voidlight_markitdown import VoidLightMarkItDown

# Create converter
converter = VoidLightMarkItDown()

# Convert document
result = converter.convert("document.pdf")
print(result.markdown)
```

## Configuration

### Config Class

```python
@dataclass
class Config:
    """Configuration for VoidLight MarkItDown."""
    
    # Language settings
    korean_mode: bool = False
    default_encoding: str = "utf-8"
    encoding_fallbacks: List[str] = field(default_factory=lambda: ["utf-8", "cp949", "euc-kr"])
    
    # Processing settings
    ocr_enabled: bool = True
    ocr_languages: List[str] = field(default_factory=lambda: ["en"])
    stream_mode: bool = False
    chunk_size: int = 1024 * 1024  # 1MB
    
    # Performance settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    timeout: int = 300  # 5 minutes
    max_workers: int = 4
    
    # Output settings
    preserve_formatting: bool = True
    include_metadata: bool = True
    markdown_flavor: str = "github"  # github, standard, extended
    
    # NLP settings (Korean mode)
    nlp_features: Dict[str, bool] = field(default_factory=dict)
    tokenizer: str = "mecab"  # mecab, okt, komoran
    
    # Paths
    temp_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
```

### Configuration Examples

```python
from voidlight_markitdown import Config, VoidLightMarkItDown

# Custom configuration
config = Config(
    korean_mode=True,
    ocr_enabled=True,
    ocr_languages=["ko", "en"],
    max_file_size=200 * 1024 * 1024,  # 200MB
    nlp_features={
        "tokenize": True,
        "pos_tagging": True,
        "ner": True
    }
)

converter = VoidLightMarkItDown(config=config)
```

## Conversion Methods

### convert()

```python
def convert(
    self,
    source: Union[str, Path, bytes, BinaryIO],
    *,
    encoding: Optional[str] = None,
    korean_mode: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> ConversionResult:
    """
    Convert a document to Markdown.
    
    Args:
        source: File path, URL, bytes, or file-like object
        encoding: Force specific encoding
        korean_mode: Override Korean mode setting
        metadata: Additional metadata to include
        **kwargs: Converter-specific options
        
    Returns:
        ConversionResult object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnsupportedFormatError: If format not supported
        ConversionError: If conversion fails
    """
```

### convert_file()

```python
def convert_file(
    self,
    file_obj: BinaryIO,
    filename: Optional[str] = None,
    **kwargs
) -> ConversionResult:
    """
    Convert a file-like object to Markdown.
    
    Args:
        file_obj: File-like object
        filename: Original filename (for format detection)
        **kwargs: Additional options
        
    Returns:
        ConversionResult object
    """
```

### convert_url()

```python
def convert_url(
    self,
    url: str,
    **kwargs
) -> ConversionResult:
    """
    Convert content from URL to Markdown.
    
    Args:
        url: URL to fetch and convert
        **kwargs: Additional options
        
    Returns:
        ConversionResult object
    """
```

### convert_stream()

```python
def convert_stream(
    self,
    source: Union[str, Path, BinaryIO],
    **kwargs
) -> Generator[MarkdownChunk, None, None]:
    """
    Convert document in streaming mode.
    
    Args:
        source: Document source
        **kwargs: Additional options
        
    Yields:
        MarkdownChunk objects
    """
```

### batch_convert()

```python
def batch_convert(
    self,
    sources: List[Union[str, Path]],
    output_dir: Optional[Path] = None,
    parallel: bool = True,
    **kwargs
) -> BatchResult:
    """
    Convert multiple documents.
    
    Args:
        sources: List of file paths
        output_dir: Directory for output files
        parallel: Process in parallel
        **kwargs: Additional options
        
    Returns:
        BatchResult object
    """
```

## Result Objects

### ConversionResult

```python
@dataclass
class ConversionResult:
    """Result of document conversion."""
    
    markdown: str
    """The converted Markdown content."""
    
    metadata: Dict[str, Any]
    """Document metadata (title, author, pages, etc.)."""
    
    source_type: str
    """Type of source document (pdf, docx, etc.)."""
    
    conversion_time: float
    """Time taken for conversion in seconds."""
    
    errors: List[str] = field(default_factory=list)
    """Non-fatal errors during conversion."""
    
    warnings: List[str] = field(default_factory=list)
    """Warnings during conversion."""
    
    statistics: Dict[str, Any] = field(default_factory=dict)
    """Conversion statistics (characters, words, etc.)."""
```

### MarkdownChunk (Streaming)

```python
@dataclass
class MarkdownChunk:
    """A chunk of markdown in streaming mode."""
    
    content: str
    """Markdown content chunk."""
    
    chunk_index: int
    """Index of this chunk."""
    
    is_final: bool
    """Whether this is the final chunk."""
    
    metadata: Optional[Dict[str, Any]] = None
    """Metadata (included in final chunk)."""
```

### BatchResult

```python
@dataclass
class BatchResult:
    """Result of batch conversion."""
    
    successful: List[Tuple[Path, ConversionResult]]
    """Successfully converted files."""
    
    failed: List[Tuple[Path, Exception]]
    """Failed conversions."""
    
    total_time: float
    """Total processing time."""
    
    statistics: Dict[str, Any]
    """Batch statistics."""
```

## Converters

Each converter handles specific file formats.

### Base Converter

```python
class BaseConverter(ABC):
    """Abstract base class for converters."""
    
    @abstractmethod
    def convert(
        self,
        source: Union[bytes, BinaryIO],
        config: Config,
        **kwargs
    ) -> ConversionResult:
        """Convert source to markdown."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """List of supported file extensions."""
        pass
```

### Available Converters

```python
# PDF Converter
from voidlight_markitdown.converters import PDFConverter

converter = PDFConverter()
result = converter.convert(pdf_bytes, config)

# DOCX Converter
from voidlight_markitdown.converters import DOCXConverter

converter = DOCXConverter()
result = converter.convert(docx_bytes, config)

# HTML Converter
from voidlight_markitdown.converters import HTMLConverter

converter = HTMLConverter()
result = converter.convert(html_bytes, config)

# Image Converter (with OCR)
from voidlight_markitdown.converters import ImageConverter

converter = ImageConverter()
result = converter.convert(image_bytes, config)
```

### Custom Converter

```python
from voidlight_markitdown.converters import BaseConverter

class MyCustomConverter(BaseConverter):
    """Custom converter implementation."""
    
    @property
    def supported_formats(self) -> List[str]:
        return [".custom", ".myformat"]
    
    def convert(self, source, config, **kwargs):
        # Implementation
        markdown = self.process_custom_format(source)
        return ConversionResult(
            markdown=markdown,
            metadata={"format": "custom"},
            source_type="custom"
        )
```

## Korean Module

Korean-specific functionality.

### Korean Detection

```python
from voidlight_markitdown.korean import (
    is_korean_text,
    detect_korean_encoding,
    contains_korean
)

# Check if text contains Korean
if is_korean_text("안녕하세요"):
    print("Korean text detected")

# Detect encoding
encoding = detect_korean_encoding(file_bytes)
print(f"Detected encoding: {encoding}")

# Check for any Korean characters
if contains_korean("Hello 안녕"):
    print("Contains Korean characters")
```

### Korean Text Processing

```python
from voidlight_markitdown.korean import (
    normalize_korean_text,
    tokenize_korean,
    extract_korean_keywords
)

# Normalize text
normalized = normalize_korean_text("한　　글  ａｂｃ")

# Tokenize
tokens = tokenize_korean("나는 학교에 갑니다")

# Extract keywords
keywords = extract_korean_keywords(document_text)
```

### Korean NLP Pipeline

```python
from voidlight_markitdown.korean import KoreanNLPPipeline

# Create pipeline
pipeline = KoreanNLPPipeline(
    tokenizer="mecab",
    pos_tagger="kkma",
    enable_ner=True
)

# Process text
result = pipeline.process("삼성전자가 새로운 갤럭시 폰을 출시했습니다.")

# Access results
tokens = result["tokens"]
pos_tags = result["pos_tags"]
entities = result["named_entities"]
```

## Utilities

### URI Utilities

```python
from voidlight_markitdown.utils import (
    is_url,
    is_local_file,
    normalize_path,
    get_file_extension
)

# Check if string is URL
if is_url("https://example.com"):
    print("It's a URL")

# Normalize file path
normalized = normalize_path("~/documents/file.pdf")

# Get file extension
ext = get_file_extension("document.PDF")  # Returns ".pdf"
```

### Logging Utilities

```python
from voidlight_markitdown.utils import setup_logging

# Setup logging
logger = setup_logging(
    level="INFO",
    log_file="conversion.log",
    format="detailed"
)

# Use logger
logger.info("Starting conversion")
```

### File Utilities

```python
from voidlight_markitdown.utils import (
    get_file_hash,
    safe_filename,
    temp_file_context
)

# Get file hash
file_hash = get_file_hash("document.pdf")

# Create safe filename
safe_name = safe_filename("my:file*.pdf")  # Returns "my_file_.pdf"

# Temporary file context
with temp_file_context() as temp_path:
    # Use temp_path
    pass  # File automatically deleted
```

## Exceptions

### Exception Hierarchy

```python
# Base exception
class VoidLightMarkItDownError(Exception):
    """Base exception for VoidLight MarkItDown."""
    pass

# Specific exceptions
class UnsupportedFormatError(VoidLightMarkItDownError):
    """Raised when file format is not supported."""
    pass

class ConversionError(VoidLightMarkItDownError):
    """Raised when conversion fails."""
    pass

class KoreanProcessingError(VoidLightMarkItDownError):
    """Raised for Korean-specific errors."""
    pass

class KoreanEncodingError(KoreanProcessingError):
    """Raised for Korean encoding issues."""
    pass

class KoreanOCRError(KoreanProcessingError):
    """Raised for Korean OCR failures."""
    pass

class TimeoutError(VoidLightMarkItDownError):
    """Raised when conversion times out."""
    pass

class FileSizeError(VoidLightMarkItDownError):
    """Raised when file exceeds size limit."""
    pass
```

### Exception Handling

```python
from voidlight_markitdown import (
    VoidLightMarkItDown,
    UnsupportedFormatError,
    ConversionError,
    KoreanEncodingError
)

converter = VoidLightMarkItDown()

try:
    result = converter.convert("document.xyz")
except UnsupportedFormatError as e:
    print(f"Format not supported: {e}")
except KoreanEncodingError as e:
    print(f"Korean encoding issue: {e}")
    # Try with specific encoding
    result = converter.convert("document.xyz", encoding="cp949")
except ConversionError as e:
    print(f"Conversion failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Plugin System

```python
from voidlight_markitdown import ConverterRegistry

# Register custom converter
registry = ConverterRegistry()
registry.register(MyCustomConverter())

# Use with custom registry
converter = VoidLightMarkItDown(converter_registry=registry)
```

### Hooks and Callbacks

```python
def pre_conversion_hook(source_path, config):
    """Called before conversion starts."""
    print(f"Converting: {source_path}")

def post_conversion_hook(result):
    """Called after conversion completes."""
    print(f"Converted {len(result.markdown)} characters")

converter = VoidLightMarkItDown(
    hooks={
        "pre_conversion": pre_conversion_hook,
        "post_conversion": post_conversion_hook
    }
)
```

### Custom Filters

```python
def markdown_filter(markdown_text, metadata):
    """Process markdown after conversion."""
    # Add custom header
    header = f"# {metadata.get('title', 'Document')}\n\n"
    return header + markdown_text

converter = VoidLightMarkItDown(
    markdown_filters=[markdown_filter]
)
```

## Performance Considerations

### Memory Management

```python
# For large files
converter = VoidLightMarkItDown(
    stream_mode=True,
    chunk_size=512 * 1024  # 512KB chunks
)

# Process with limited memory
with converter.convert_stream("large_file.pdf") as stream:
    for chunk in stream:
        # Process chunk
        save_chunk_to_file(chunk)
```

### Parallel Processing

```python
# Configure parallel processing
converter = VoidLightMarkItDown(
    config=Config(
        max_workers=8,  # Number of parallel workers
        batch_size=10   # Files per batch
    )
)

# Batch convert with parallelism
results = converter.batch_convert(
    file_list,
    parallel=True
)
```

### Caching

```python
# Enable caching
converter = VoidLightMarkItDown(
    config=Config(
        cache_dir=Path("~/.voidlight_cache"),
        cache_ttl=3600  # 1 hour
    )
)

# Cached conversions are faster
result1 = converter.convert("doc.pdf")  # First time
result2 = converter.convert("doc.pdf")  # From cache
```

---

<div align="center">
  <p>For more examples, see the <a href="../guides/examples.md">Examples Guide</a></p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>