# Development Setup Guide

This guide will help you set up your development environment for contributing to VoidLight MarkItDown.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Debugging](#debugging)
8. [Common Tasks](#common-tasks)

## Prerequisites

### Required Software

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Poetry** (recommended) or pip - [Install Poetry](https://python-poetry.org/docs/#installation)
- **Make** (optional) - For using Makefile commands

### Optional but Recommended

- **Docker** - For containerized testing
- **VS Code** or **PyCharm** - IDE with Python support
- **pre-commit** - For git hooks

### System Dependencies

#### For Korean Support
```bash
# Ubuntu/Debian
sudo apt-get install libmecab-dev mecab-ko mecab-ko-dic

# macOS
brew install mecab mecab-ko mecab-ko-dic

# Windows
# Download from https://github.com/ikegami-yukino/mecab/releases
```

#### For OCR Support
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-kor

# macOS
brew install tesseract tesseract-lang

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

## Environment Setup

### 1. Clone the Repository

```bash
# Clone with SSH (recommended)
git clone git@github.com:VoidLight00/voidlight_markitdown.git

# Or with HTTPS
git clone https://github.com/VoidLight00/voidlight_markitdown.git

cd voidlight_markitdown
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using poetry
poetry install
poetry shell

# Using conda
conda create -n voidlight python=3.9
conda activate voidlight
```

### 3. Install Dependencies

```bash
# Development installation with all extras
pip install -e "packages/voidlight_markitdown[all,dev]"
pip install -e "packages/voidlight_markitdown-mcp[dev]"

# Install development tools
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install
```

### 4. Verify Installation

```bash
# Run tests
pytest tests/unit

# Check CLI
voidlight-markitdown --version

# Check imports
python -c "import voidlight_markitdown; print(voidlight_markitdown.__version__)"
```

## Project Structure

```
voidlight_markitdown/
├── packages/
│   ├── voidlight_markitdown/          # Main library
│   │   ├── src/
│   │   │   └── voidlight_markitdown/
│   │   │       ├── converters/        # File format converters
│   │   │       ├── korean/            # Korean language modules
│   │   │       ├── core/              # Core functionality
│   │   │       └── utils/             # Utilities
│   │   ├── tests/                     # Package tests
│   │   └── pyproject.toml            # Package config
│   │
│   └── voidlight_markitdown-mcp/      # MCP server
│       ├── src/
│       │   └── voidlight_markitdown_mcp/
│       │       ├── server/            # MCP server implementation
│       │       └── handlers/          # Request handlers
│       └── pyproject.toml
│
├── tests/                             # Integration tests
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── performance/                  # Performance tests
│   └── e2e/                         # End-to-end tests
│
├── docs/                             # Documentation
├── scripts/                          # Development scripts
└── config/                          # Configuration files
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the coding standards and ensure:
- All tests pass
- Code is properly formatted
- Documentation is updated
- Type hints are added

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_converters.py

# Run with coverage
pytest --cov=voidlight_markitdown

# Run specific test
pytest -k "test_pdf_conversion"
```

### 4. Code Quality Checks

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
pylint src/

# Type checking
mypy src/

# Or use pre-commit
pre-commit run --all-files
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add support for RTF format conversion"

# Push to origin
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template
5. Request review

## Testing

### Running Tests

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Performance tests
pytest tests/performance -v

# Korean-specific tests
pytest tests/unit/korean -v

# With specific markers
pytest -m "not slow"
pytest -m korean
```

### Writing Tests

```python
# tests/unit/converters/test_my_converter.py
import pytest
from voidlight_markitdown.converters import MyConverter

class TestMyConverter:
    def test_basic_conversion(self):
        converter = MyConverter()
        result = converter.convert(b"test content", config)
        assert result.markdown == "expected output"
    
    @pytest.mark.korean
    def test_korean_content(self):
        converter = MyConverter()
        result = converter.convert("한글 테스트".encode(), config)
        assert "한글" in result.markdown
    
    @pytest.mark.parametrize("input,expected", [
        (b"input1", "output1"),
        (b"input2", "output2"),
    ])
    def test_various_inputs(self, input, expected):
        converter = MyConverter()
        result = converter.convert(input, config)
        assert result.markdown == expected
```

### Test Fixtures

```python
# conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_pdf():
    return Path("tests/fixtures/sample.pdf").read_bytes()

@pytest.fixture
def korean_config():
    return Config(korean_mode=True, ocr_enabled=True)
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 100 characters
- Use type hints for all public functions
- Use docstrings for all public classes and methods

### Example Code Style

```python
from typing import Optional, Union
from pathlib import Path

class DocumentConverter:
    """Convert documents to markdown format.
    
    This class handles the conversion of various document
    formats to clean, structured markdown.
    
    Attributes:
        config: Configuration object
        logger: Logger instance
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize converter with configuration.
        
        Args:
            config: Configuration object with conversion settings
        """
        self.config = config
        self.logger = setup_logger(__name__)
    
    def convert(
        self, 
        source: Union[str, Path, bytes],
        encoding: Optional[str] = None
    ) -> ConversionResult:
        """Convert document to markdown.
        
        Args:
            source: Document source (path, bytes, or URL)
            encoding: Force specific encoding (optional)
            
        Returns:
            ConversionResult with markdown and metadata
            
        Raises:
            ConversionError: If conversion fails
            UnsupportedFormatError: If format not supported
        """
        # Implementation
        pass
```

### Commit Message Format

We use conventional commits:

```
type(scope): description

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

Examples:
```
feat(korean): add Hangul normalization support
fix(pdf): handle encrypted PDFs correctly
docs: update API reference for converters
test(integration): add MCP server tests
```

## Debugging

### VS Code Configuration

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug CLI",
            "type": "python",
            "request": "launch",
            "module": "voidlight_markitdown.cli",
            "args": ["test.pdf", "-o", "output.md"],
            "console": "integratedTerminal"
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "${file}"],
            "console": "integratedTerminal"
        }
    ]
}
```

### PyCharm Configuration

1. Run → Edit Configurations
2. Add Python configuration
3. Module: `voidlight_markitdown.cli`
4. Parameters: `test.pdf -o output.md`

### Debugging Tips

```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()

# Debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {variable}")

# Print debugging
print(f"DEBUG: {variable=}")  # Python 3.8+
```

## Common Tasks

### Adding a New Converter

1. Create converter file:
```python
# src/voidlight_markitdown/converters/_myformat_converter.py
from .base import BaseConverter

class MyFormatConverter(BaseConverter):
    @property
    def supported_formats(self):
        return [".myf", ".myformat"]
    
    def convert(self, source, config, **kwargs):
        # Implementation
        return ConversionResult(...)
```

2. Register converter:
```python
# src/voidlight_markitdown/converters/__init__.py
from ._myformat_converter import MyFormatConverter

CONVERTERS = {
    ".myf": MyFormatConverter(),
    ".myformat": MyFormatConverter(),
}
```

3. Add tests:
```python
# tests/unit/converters/test_myformat.py
def test_myformat_conversion():
    # Test implementation
    pass
```

### Adding Korean Support

1. Add to Korean module:
```python
# src/voidlight_markitdown/korean/processors.py
def process_korean_myformat(text: str) -> str:
    """Process Korean text in my format."""
    # Implementation
    return processed_text
```

2. Integrate with converter:
```python
if self.config.korean_mode:
    text = process_korean_myformat(text)
```

### Performance Profiling

```python
# Profile code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = converter.convert("large_file.pdf")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def convert_large_file():
    converter = VoidLightMarkItDown()
    return converter.convert("large_file.pdf")
```

## Development Scripts

### Makefile Commands

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Build documentation
make docs

# Clean artifacts
make clean
```

### Useful Scripts

```bash
# Update dependencies
./scripts/update_deps.sh

# Run benchmarks
./scripts/benchmark.py

# Generate test report
./scripts/test_report.py

# Check Korean support
./scripts/check_korean.py
```

## Troubleshooting Development Issues

### Common Issues

1. **Import errors**
   ```bash
   # Reinstall in development mode
   pip install -e packages/voidlight_markitdown[all]
   ```

2. **Korean module errors**
   ```bash
   # Install Korean dependencies
   pip install konlpy kiwipiepy soynlp
   ```

3. **Test failures**
   ```bash
   # Update test fixtures
   python scripts/update_fixtures.py
   ```

### Getting Help

- Check existing issues on GitHub
- Ask in discussions
- Contact maintainers
- Review CI logs

---

<div align="center">
  <p>Ready to contribute? Check our <a href="contributing.md">Contributing Guide</a></p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>