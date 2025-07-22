# Dependency Management Guide

## Python Version Compatibility

✅ **Supported**: Python 3.9, 3.10, 3.11, 3.12, 3.13  
✅ **Tested**: All code is compatible with Python 3.9+ (no Python 3.10+ specific syntax)

## Core Dependencies

These are required for basic functionality:

| Package | Version | Purpose |
|---------|---------|---------|
| beautifulsoup4 | >=4.11.1 | HTML parsing |
| markdownify | >=0.11.6 | HTML to Markdown conversion |
| charset-normalizer | >=3.1.0 | Character encoding detection |
| magika | >=0.5.1 | File type detection |
| requests | >=2.28.2 | HTTP requests |
| tabulate | >=0.9.0 | Table formatting |

## Optional Dependencies by Feature

### Document Processing

```bash
pip install "voidlight-markitdown[docx,pptx,xlsx,pdf]"
```

| Package | Purpose | Notes |
|---------|---------|-------|
| python-docx | Word documents | |
| mammoth | Alternative Word converter | |
| python-pptx | PowerPoint files | |
| openpyxl | Excel files (xlsx) | |
| pandas | Data processing | Heavy dependency |
| xlrd | Excel files (xls) | |
| pdfplumber | PDF text extraction | |
| PyPDF2 | Alternative PDF reader | |
| ebooklib | EPUB files | |
| extract-msg | Outlook MSG files | |

### Image & OCR

```bash
pip install "voidlight-markitdown[image]"
```

| Package | Purpose | System Requirements |
|---------|---------|---------------------|
| pillow | Image processing | |
| pytesseract | OCR | Requires Tesseract binary |
| easyocr | Deep learning OCR | Large download, GPU optional |

### Audio Processing

```bash
pip install "voidlight-markitdown[audio]"
```

| Package | Purpose | System Requirements |
|---------|---------|---------------------|
| SpeechRecognition | Speech to text | |
| pydub | Audio manipulation | Requires FFmpeg |

### Korean Language Support

```bash
pip install "voidlight-markitdown[korean]"
```

| Package | Purpose | Installation Notes |
|---------|---------|-------------------|
| konlpy | Korean NLP | Requires Java |
| kiwipiepy | Fast Korean tokenizer | C++ extension |
| soynlp | Unsupervised Korean NLP | |
| jamo | Hangul character utils | |
| hanja | Hanja (Chinese chars) | |
| py-hanspell | Spell checker | See special instructions |

### Web & API

```bash
pip install "voidlight-markitdown[rss,youtube]"
```

| Package | Purpose |
|---------|---------|
| feedparser | RSS/Atom feeds |
| youtube-transcript-api | YouTube transcripts |

### Archives

```bash
pip install "voidlight-markitdown[zip]"
```

| Package | Purpose |
|---------|---------|
| rarfile | RAR archives |
| py7zr | 7z archives |

### AI/LLM Features

```bash
pip install "voidlight-markitdown[llm]"
```

| Package | Purpose |
|---------|---------|
| openai | OpenAI API |
| azure-cognitiveservices-speech | Azure Speech |

## Installation Strategies

### 1. Minimal Installation

```bash
pip install voidlight-markitdown
# or
pip install -r requirements-minimal.txt
```

### 2. Common Features

```bash
pip install "voidlight-markitdown[pdf,docx,xlsx,image]"
```

### 3. Full Installation (except heavy dependencies)

```bash
pip install "voidlight-markitdown[all]"
```

### 4. Development Installation

```bash
pip install -e ".[dev,all]"
```

## Troubleshooting Specific Dependencies

### py-hanspell

This package has known installation issues. Try these methods in order:

1. **Standard pip**:
   ```bash
   pip install py-hanspell
   ```

2. **From GitHub**:
   ```bash
   pip install git+https://github.com/ssut/py-hanspell.git
   ```

3. **Use the fix script**:
   ```bash
   python fix_hanspell.py
   ```

4. **Skip it**: The package works without spell checking.

### KoNLPy

Requires Java to be installed:

```bash
# Ubuntu/Debian
sudo apt-get install default-jdk

# macOS
brew install openjdk

# Set JAVA_HOME if needed
export JAVA_HOME=$(/usr/libexec/java_home)
```

### Tesseract

Required for pytesseract:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-kor  # Korean support

# macOS
brew install tesseract
brew install tesseract-lang  # All languages

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### EasyOCR

Large download (~64MB model files):

```bash
# First install
pip install easyocr

# Offline installation
# Download models from: https://github.com/JaidedAI/EasyOCR/releases
# Place in ~/.EasyOCR/model/
```

### FFmpeg

Required for audio processing:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

## Testing Installation

Run the test script to verify your installation:

```bash
python test_install.py
```

This will:
- Check Python version compatibility
- Verify core dependencies
- Test optional dependencies
- Check system requirements
- Provide installation recommendations

## Version Compatibility Matrix

| voidlight-markitdown | Python | Status |
|---------------------|---------|---------|
| 0.1.x | 3.9-3.13 | ✅ Supported |
| 0.1.x | 3.8 | ❌ Not supported |
| 0.1.x | 3.14+ | ⚠️ Untested |

## Known Issues

1. **py-hanspell**: Installation may fail on some systems. The package works without it.

2. **SSL Warnings**: On older systems, you might see SSL warnings. These can usually be ignored.

3. **Memory Usage**: EasyOCR and docling can use significant memory (>4GB).

4. **Windows**: Some packages may require Visual C++ Build Tools.

## Recommended Virtual Environment Setup

```bash
# Create environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install package
pip install -e ".[all]"
```