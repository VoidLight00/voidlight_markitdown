# Korean Language Features Guide

VoidLight MarkItDown provides advanced Korean language processing capabilities that go beyond simple text conversion. This guide covers all Korean-specific features and best practices.

## Table of Contents

1. [Overview](#overview)
2. [Korean Mode Activation](#korean-mode-activation)
3. [Encoding Detection](#encoding-detection)
4. [Text Normalization](#text-normalization)
5. [NLP Features](#nlp-features)
6. [OCR for Korean](#ocr-for-korean)
7. [Mixed Script Support](#mixed-script-support)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

Korean text processing presents unique challenges:
- Multiple encoding standards (UTF-8, CP949, EUC-KR)
- Complex character composition (Jamo combinations)
- Mixed scripts (Hangul, Hanja, English, numbers)
- Spacing and tokenization differences

VoidLight MarkItDown addresses all these challenges with specialized processing.

## Korean Mode Activation

### Method 1: Global Korean Mode

```python
from voidlight_markitdown import VoidLightMarkItDown

# Enable Korean mode globally
converter = VoidLightMarkItDown(korean_mode=True)
result = converter.convert("korean_document.pdf")
```

### Method 2: Per-Document Korean Mode

```python
# Standard converter
converter = VoidLightMarkItDown()

# Enable Korean mode for specific conversion
result = converter.convert("korean_document.pdf", korean_mode=True)
```

### Method 3: Environment Variable

```bash
export VOIDLIGHT_KOREAN_MODE=true
voidlight-markitdown document.pdf
```

### Method 4: CLI Flag

```bash
voidlight-markitdown --korean-mode document.pdf -o output.md
```

## Encoding Detection

VoidLight MarkItDown automatically detects and handles Korean encodings.

### Supported Encodings

1. **UTF-8** - Modern standard
2. **CP949** - Windows Korean encoding
3. **EUC-KR** - Legacy Korean encoding
4. **ISO-2022-KR** - Older email encoding

### Manual Encoding Specification

```python
# Force specific encoding
result = converter.convert("document.txt", encoding="cp949")

# Try multiple encodings
result = converter.convert("document.txt", 
                         encoding_fallbacks=["utf-8", "cp949", "euc-kr"])
```

### Encoding Detection Example

```python
from voidlight_markitdown.korean import detect_korean_encoding

# Detect file encoding
with open("korean_file.txt", "rb") as f:
    data = f.read()
    encoding = detect_korean_encoding(data)
    print(f"Detected encoding: {encoding}")
```

## Text Normalization

Korean text normalization handles various text variations and inconsistencies.

### Features

1. **Jamo Normalization**
   ```python
   # Composed vs Decomposed characters
   # ㄱ + ㅏ + ㄴ → 간
   ```

2. **Full-width/Half-width Conversion**
   ```python
   # ａｂｃ → abc
   # １２３ → 123
   ```

3. **Space Normalization**
   ```python
   # Multiple spaces → single space
   # ZWSP removal
   ```

4. **Quote Normalization**
   ```python
   # Various quote styles → standard quotes
   ```

### Example

```python
from voidlight_markitdown.korean import normalize_korean_text

text = "한　　글  ａｂｃ  １２３"
normalized = normalize_korean_text(text)
print(normalized)  # "한글 abc 123"
```

## NLP Features

VoidLight MarkItDown integrates with Korean NLP libraries for advanced processing.

### Tokenization

```python
from voidlight_markitdown import VoidLightMarkItDown

converter = VoidLightMarkItDown(
    korean_mode=True,
    nlp_features={
        'tokenize': True,
        'pos_tagging': True
    }
)

result = converter.convert("korean_text.txt")
# Metadata includes tokenization results
tokens = result.metadata.get('korean_tokens', [])
```

### Part-of-Speech Tagging

```python
# Enable POS tagging
converter = VoidLightMarkItDown(
    korean_mode=True,
    nlp_features={'pos_tagging': True}
)

result = converter.convert("korean_document.docx")
pos_tags = result.metadata.get('pos_tags', [])
```

### Named Entity Recognition

```python
# Enable NER
converter = VoidLightMarkItDown(
    korean_mode=True,
    nlp_features={'ner': True}
)

result = converter.convert("news_article.pdf")
entities = result.metadata.get('named_entities', [])
# Returns: [(entity, type, position), ...]
```

## OCR for Korean

Korean OCR requires special handling for accurate recognition.

### Configuration

```python
# Enable Korean OCR
converter = VoidLightMarkItDown(
    korean_mode=True,
    ocr_config={
        'languages': ['ko', 'en'],  # Korean + English
        'model': 'korean_optimized'
    }
)

# Convert image with Korean text
result = converter.convert("korean_image.png")
```

### OCR Quality Settings

```python
# High-quality OCR for Korean
converter = VoidLightMarkItDown(
    korean_mode=True,
    ocr_config={
        'quality': 'high',
        'dpi': 300,
        'preprocessing': {
            'deskew': True,
            'denoise': True,
            'enhance_contrast': True
        }
    }
)
```

### Handling Mixed Content

```python
# For documents with Korean and English
converter = VoidLightMarkItDown(
    korean_mode=True,
    ocr_config={
        'languages': ['ko', 'en', 'zh'],  # Korean, English, Chinese
        'script_detection': True
    }
)
```

## Mixed Script Support

Korean documents often contain multiple scripts. VoidLight MarkItDown handles:

### Script Types

1. **Hangul (한글)** - Korean alphabet
2. **Hanja (漢字)** - Chinese characters
3. **Latin (ABC)** - English text
4. **Numbers (123)** - Arabic numerals
5. **Special symbols** - Various punctuation

### Intelligent Processing

```python
# Automatic script detection and processing
text = "안녕하세요! Hello! 您好! 123"
result = converter.convert_text(text)

# Metadata includes script information
scripts = result.metadata.get('detected_scripts', [])
# ['hangul', 'latin', 'chinese', 'numeric']
```

### Script-Specific Formatting

```python
# Preserve formatting for different scripts
converter = VoidLightMarkItDown(
    korean_mode=True,
    preserve_formatting={
        'hangul': True,
        'hanja': True,
        'latin': True
    }
)
```

## Best Practices

### 1. File Preparation

```python
# Check file before conversion
from voidlight_markitdown.korean import is_korean_document

if is_korean_document("document.pdf"):
    converter = VoidLightMarkItDown(korean_mode=True)
else:
    converter = VoidLightMarkItDown()
```

### 2. Batch Processing

```python
# Efficient batch processing for Korean documents
from pathlib import Path

korean_converter = VoidLightMarkItDown(korean_mode=True)
standard_converter = VoidLightMarkItDown()

for file_path in Path("documents").glob("*.pdf"):
    # Auto-detect Korean documents
    if is_korean_document(file_path):
        result = korean_converter.convert(file_path)
    else:
        result = standard_converter.convert(file_path)
```

### 3. Memory Optimization

```python
# For large Korean documents
converter = VoidLightMarkItDown(
    korean_mode=True,
    stream_mode=True,
    chunk_size=1024 * 1024  # 1MB chunks
)

# Process in chunks
with converter.convert_stream("large_korean_file.pdf") as stream:
    for chunk in stream:
        process_chunk(chunk)
```

### 4. Error Handling

```python
try:
    result = converter.convert("korean_document.pdf")
except KoreanEncodingError as e:
    # Handle encoding issues
    print(f"Encoding error: {e}")
    # Try with fallback encoding
    result = converter.convert("korean_document.pdf", 
                             encoding="cp949")
except KoreanOCRError as e:
    # Handle OCR issues
    print(f"OCR error: {e}")
    # Try without OCR
    result = converter.convert("korean_document.pdf", 
                             ocr_enabled=False)
```

## Advanced Configuration

### Custom NLP Pipeline

```python
from voidlight_markitdown import VoidLightMarkItDown
from voidlight_markitdown.korean import KoreanNLPPipeline

# Create custom pipeline
pipeline = KoreanNLPPipeline(
    tokenizer='mecab',  # or 'okt', 'komoran'
    pos_tagger='kkma',
    ner_model='custom_model.pkl'
)

converter = VoidLightMarkItDown(
    korean_mode=True,
    nlp_pipeline=pipeline
)
```

### Performance Tuning

```python
# Optimize for speed
converter = VoidLightMarkItDown(
    korean_mode=True,
    performance_mode='fast',
    nlp_features={
        'tokenize': True,
        'pos_tagging': False,  # Skip heavy processing
        'ner': False
    }
)

# Optimize for accuracy
converter = VoidLightMarkItDown(
    korean_mode=True,
    performance_mode='accurate',
    nlp_features={
        'tokenize': True,
        'pos_tagging': True,
        'ner': True,
        'deep_analysis': True
    }
)
```

## Troubleshooting

### Common Issues

1. **Garbled Text (���)**
   ```python
   # Solution: Check encoding
   result = converter.convert("file.txt", encoding="cp949")
   ```

2. **Missing Korean Characters**
   ```python
   # Solution: Install Korean fonts
   # Ubuntu: sudo apt-get install fonts-nanum
   # macOS: Install from System Preferences
   ```

3. **OCR Not Recognizing Korean**
   ```python
   # Solution: Install Korean OCR data
   pip install voidlight-markitdown[korean-ocr]
   ```

4. **Slow Processing**
   ```python
   # Solution: Disable unnecessary features
   converter = VoidLightMarkItDown(
       korean_mode=True,
       nlp_features={'tokenize': True}  # Only what you need
   )
   ```

### Debug Mode

```python
# Enable debug logging for Korean processing
import logging
logging.getLogger('voidlight_markitdown.korean').setLevel(logging.DEBUG)

converter = VoidLightMarkItDown(
    korean_mode=True,
    debug=True
)
```

## Examples

### News Article Processing

```python
# Optimized for news articles
converter = VoidLightMarkItDown(
    korean_mode=True,
    document_type='news',
    nlp_features={
        'ner': True,  # Extract people, organizations
        'summarize': True,  # Generate summary
        'keywords': True  # Extract keywords
    }
)

result = converter.convert("news_article.pdf")
print(f"Summary: {result.metadata['summary']}")
print(f"Keywords: {result.metadata['keywords']}")
```

### Academic Paper Processing

```python
# Handle mixed Korean/English academic papers
converter = VoidLightMarkItDown(
    korean_mode=True,
    document_type='academic',
    preserve_formatting={
        'equations': True,
        'citations': True,
        'figures': True
    }
)
```

### Business Document Processing

```python
# For business documents with tables
converter = VoidLightMarkItDown(
    korean_mode=True,
    document_type='business',
    table_extraction={
        'format': 'markdown',
        'preserve_structure': True
    }
)
```

## Performance Benchmarks

| Document Type | Size | Korean Mode Off | Korean Mode On |
|--------------|------|-----------------|----------------|
| Text file | 1MB | 0.2s | 0.5s |
| PDF | 10MB | 2.1s | 3.8s |
| DOCX | 5MB | 1.5s | 2.3s |
| Image (OCR) | 2MB | 5.2s | 8.7s |

## Additional Resources

- [Korean NLP Libraries Guide](../development/korean-nlp.md)
- [Character Encoding Reference](../reference/encodings.md)
- [OCR Configuration Guide](../guides/ocr-setup.md)
- [Performance Optimization](../deployment/performance.md#korean-optimization)

---

<div align="center">
  <p>🇰🇷 Happy Korean document processing! 🇰🇷</p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>