# Korean NLP Setup Guide

This guide explains how to set up and use Korean Natural Language Processing features in voidlight_markitdown.

## Overview

The Korean NLP module provides advanced text processing capabilities for Korean documents, including:

- **Tokenization and POS tagging** - Break down Korean text into meaningful units
- **Spacing correction** - Fix common spacing issues in Korean text
- **Sentence segmentation** - Intelligently split text into sentences
- **Morpheme analysis** - Extract root forms and grammatical information
- **Formality detection** - Analyze speech levels (formal/informal)
- **Reading difficulty estimation** - Assess text complexity
- **Keyword extraction** - Identify important terms
- **Hanja conversion** - Convert Chinese characters to Hangul

## Quick Start

### Basic Usage

```python
from voidlight_markitdown import MarkItDown

# Enable Korean mode
md = MarkItDown(korean_mode=True)

# Convert Korean documents
result = md.convert("korean_document.pdf")
print(result.text_content)
```

### Check NLP Status

```python
from voidlight_markitdown._korean_nlp_init import print_status_report

# Check what's installed and working
print_status_report()
```

## Installation

### Minimal Setup (Kiwi only - Recommended)

Kiwi is a fast, C++-based tokenizer that doesn't require Java:

```bash
pip install kiwipiepy
```

### Full Setup (All features)

1. **Install Java** (for KoNLPy):
   - macOS: `brew install openjdk`
   - Ubuntu/Debian: `sudo apt-get install openjdk-11-jdk`
   - Windows: Download from [AdoptOpenJDK](https://adoptopenjdk.net/)

2. **Set up Java environment** (macOS with Homebrew):
   ```bash
   export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"
   export JAVA_HOME="/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home"
   ```
   
   Or use the provided setup script:
   ```bash
   source setup_java_env.sh
   ```

3. **Install Python packages**:
   ```bash
   # Core NLP libraries
   pip install kiwipiepy konlpy JPype1
   
   # Optional enhancement libraries
   pip install soynlp py-hanspell jamo hanja
   ```
   
   Note: The package includes automatic compatibility handling for JPype1 import issues.

## Dependency Details

### Core Libraries

1. **kiwipiepy** (Recommended)
   - Fast C++ based tokenizer
   - No Java required
   - Best performance
   - Includes spacing correction

2. **KoNLPy** (Optional)
   - Java-based toolkit
   - Multiple tokenizers (Okt, Kkma, Komoran, etc.)
   - More linguistic features
   - Requires Java runtime

### Optional Libraries

- **soynlp**: Unsupervised learning-based tools
- **py-hanspell**: Spell checking (requires internet)
- **jamo**: Hangul syllable decomposition
- **hanja**: Chinese character conversion

## Features by Dependency

| Feature | Kiwi Only | KoNLPy Only | Both | No Dependencies |
|---------|-----------|-------------|------|-----------------|
| Basic tokenization | ✓ | ✓ | ✓ | Fallback |
| POS tagging | ✓ | ✓ | ✓ | Basic |
| Spacing correction | ✓ | ✗ | ✓ | ✗ |
| Sentence segmentation | ✓ | ✗ | ✓ | Rule-based |
| Morpheme analysis | ✓ | ✓ | ✓ | Basic |
| Noun extraction | ✓ | ✓ | ✓ | ✗ |

## Advanced Usage

### Text Processing

```python
from voidlight_markitdown._korean_utils import KoreanTextProcessor

processor = KoreanTextProcessor()

# Tokenize with POS tags
text = "안녕하세요. 오늘 날씨가 좋네요."
tokens = processor.tokenize(text)
# [('안녕', 'NNG'), ('하', 'XSV'), ('세요', 'EP+EF'), ...]

# Correct spacing
text = "안녕하세요오늘날씨가좋네요"
corrected = processor.correct_spacing(text)
# "안녕하세요 오늘 날씨가 좋네요"

# Extract keywords
keywords = processor.extract_keywords(text, num_keywords=5)
# [('날씨', 0.25), ('오늘', 0.25), ...]
```

### Formality Analysis

```python
# Analyze speech level
formal_text = "안녕하십니까. 만나서 반갑습니다."
analysis = processor.analyze_formality(formal_text)
# {'formality_level': 'formal', 'formal_endings': 2, ...}

informal_text = "야, 뭐해? 놀러가자."
analysis = processor.analyze_formality(informal_text)
# {'formality_level': 'informal', 'informal_endings': 2, ...}
```

### Reading Difficulty

```python
# Assess text complexity
simple_text = "나는 학생이다. 학교에 간다."
difficulty = processor.get_reading_difficulty(simple_text)
# {'level': 'beginner', 'avg_sentence_length': 3.0, ...}

complex_text = "韓國의 傳統文化는 悠久한 歷史를 지니고 있습니다."
difficulty = processor.get_reading_difficulty(complex_text)
# {'level': 'advanced', 'hanja_ratio': 0.35, ...}
```

## Troubleshooting

### Java Not Found (KoNLPy)

If you see Java-related errors:

1. Verify Java installation:
   ```bash
   java -version
   ```

2. Set JAVA_HOME:
   ```bash
   export JAVA_HOME=$(/usr/libexec/java_home)  # macOS
   export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Linux
   ```

### Import Errors

If libraries fail to import:

1. Check installation:
   ```python
   from voidlight_markitdown._korean_nlp_init import get_korean_nlp_status
   status = get_korean_nlp_status()
   print(status.get_status_report())
   ```

2. Install missing dependencies based on the report.

### Performance Issues

- Use Kiwi for best performance
- Limit text size for spell checking (< 500 chars)
- Consider disabling optional features for large documents

## Best Practices

1. **Start with Kiwi**: It's fast and doesn't require Java
2. **Add KoNLPy if needed**: For more linguistic analysis
3. **Use graceful fallbacks**: The system works even without dependencies
4. **Monitor performance**: Some features are computationally intensive
5. **Test with your data**: Different tokenizers work better for different domains

## Examples

### Document Conversion with Korean NLP

```python
from voidlight_markitdown import MarkItDown

# Initialize with Korean mode
converter = MarkItDown(korean_mode=True)

# Convert and process
result = converter.convert("korean_research_paper.pdf")

# Access processed content
print(f"Characters: {len(result.text_content)}")
print(f"Korean ratio: {result.metadata.get('korean_ratio', 0):.2%}")
```

### Batch Processing

```python
import os
from voidlight_markitdown import MarkItDown

converter = MarkItDown(korean_mode=True)

for filename in os.listdir("korean_docs"):
    if filename.endswith(".pdf"):
        result = converter.convert(f"korean_docs/{filename}")
        
        # Save processed text
        output_name = filename.replace(".pdf", "_processed.txt")
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(result.text_content)
```

## Contributing

To add support for new Korean NLP libraries:

1. Add optional import in `_korean_utils.py`
2. Update `KoreanNLPInitializer` in `_korean_nlp_init.py`
3. Implement feature with graceful fallback
4. Add tests in `test_korean_nlp_features.py`
5. Update this documentation

## Resources

- [Kiwi Documentation](https://github.com/bab2min/Kiwi)
- [KoNLPy Documentation](https://konlpy.org/)
- [Korean NLP Papers](https://github.com/songys/AwesomeKorean_Data)
- [Korean Datasets](https://github.com/ko-nlp/korean-nlp-datasets)