# Installation Guide for VoidLight MarkItDown

## Python Version Compatibility

This package supports Python 3.9 through 3.13. The codebase uses Python 3.9-compatible type hints for maximum compatibility.

## Installation Methods

### 1. Basic Installation (Minimal Dependencies)

```bash
pip install voidlight-markitdown
```

Or from source:
```bash
pip install -r requirements-minimal.txt
pip install .
```

### 2. Full Installation (All Optional Dependencies)

```bash
pip install "voidlight-markitdown[all]"
```

Or from source:
```bash
pip install -r requirements.txt
pip install .
```

### 3. Feature-Specific Installation

Install only the dependencies you need:

```bash
# For PDF support
pip install "voidlight-markitdown[pdf]"

# For Korean language support
pip install "voidlight-markitdown[korean]"

# For document conversion (docx, pptx, xlsx)
pip install "voidlight-markitdown[docx,pptx,xlsx]"

# For image processing and OCR
pip install "voidlight-markitdown[image]"

# For audio transcription
pip install "voidlight-markitdown[audio]"

# For LLM features
pip install "voidlight-markitdown[llm]"
```

## Special Dependencies

### py-hanspell (Korean Spelling Checker)

The `py-hanspell` package has installation issues on some systems. If you need Korean spelling correction:

1. Try installing directly:
   ```bash
   pip install py-hanspell
   ```

2. If that fails, install from GitHub:
   ```bash
   pip install git+https://github.com/ssut/py-hanspell.git
   ```

3. If you still have issues, you can use the package without spell checking - all other Korean features will work.

### EasyOCR

EasyOCR requires additional system dependencies:
- On Ubuntu/Debian: `sudo apt-get install python3-opencv`
- On macOS: `brew install opencv`

### Tesseract OCR

For pytesseract to work, you need to install Tesseract:
- On Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- On macOS: `brew install tesseract`
- On Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

For Korean OCR support:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-kor

# macOS
brew install tesseract-lang
```

### Audio Dependencies

For audio transcription, you may need:
- FFmpeg: `brew install ffmpeg` (macOS) or `sudo apt-get install ffmpeg` (Ubuntu)

## Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install the package
pip install -e ".[all]"
```

### Using conda

```bash
# Create conda environment with Python 3.9
conda create -n voidlight python=3.9
conda activate voidlight

# Install the package
pip install -e ".[all]"
```

## Testing Installation

```bash
# Test basic functionality
python -c "from voidlight_markitdown import VoidLightMarkItDown; print('Installation successful!')"

# Test Korean support
python -c "from voidlight_markitdown._korean_utils import KoreanTextProcessor; print('Korean support available!')"

# Run tests
pytest tests/
```

## Troubleshooting

### ImportError: No module named 'konlpy'

Korean NLP features require Java. Install Java and then:
```bash
pip install konlpy
```

### OSError: [Errno 2] No such file or directory: 'tesseract'

Install Tesseract OCR as described above.

### AttributeError with py-hanspell

If py-hanspell causes issues, comment it out in requirements.txt and use the package without spell checking.

### Memory Issues with EasyOCR

EasyOCR can be memory-intensive. For systems with limited RAM:
```bash
# Use CPU mode instead of GPU
export CUDA_VISIBLE_DEVICES=-1
```

## Development Installation

For development work:
```bash
# Clone the repository
git clone https://github.com/voidlight/voidlight_markitdown.git
cd voidlight_markitdown/packages/voidlight_markitdown

# Install in development mode with dev dependencies
pip install -e ".[dev,all]"

# Install pre-commit hooks (if available)
pre-commit install
```