# Contributing to VoidLight MarkItDown

Thank you for your interest in contributing to VoidLight MarkItDown! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a branch for your changes
5. Make your changes
6. Run tests
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9, 3.10, or 3.11
- Git
- Make (optional but recommended)
- Docker (optional, for containerized development)

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/voidlight_markitdown.git
cd voidlight_markitdown

# Initialize development environment
make init

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/development.txt
pip install -e .
pre-commit install
```

### Korean Language Support Setup

If you're working on Korean language features:

```bash
# Install Korean NLP dependencies
pip install -r requirements/optional.txt

# Install Java for KoNLPy (optional)
# macOS: brew install openjdk
# Ubuntu: sudo apt-get install default-jdk
```

## Making Changes

### Creating a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bugfixes
git checkout -b fix/bug-description
```

### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all quality checks:

```bash
make quality
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit. To run manually:

```bash
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-performance # Performance tests

# Run with coverage
make test-coverage
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names
- Include docstrings for complex tests
- Test Korean language features thoroughly

Example test:

```python
def test_korean_text_normalization():
    """Test that Korean text is properly normalized."""
    processor = KoreanTextProcessor()
    result = processor.normalize("한글 　테스트")  # Full-width space
    assert result == "한글 테스트"  # Normal space
```

## Submitting Changes

### Commit Messages

Follow the conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Build process or auxiliary tool changes

Examples:
```
feat(korean): add Hanja to Hangul conversion
fix(converter): handle empty PDF files gracefully
docs(api): update converter usage examples
```

### Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update the CHANGELOG.md if applicable
5. Submit the pull request with a clear description

### Pull Request Template

When creating a PR, please include:

- **Description**: What does this PR do?
- **Related Issue**: Link to any related issues
- **Type of Change**: Bug fix, new feature, etc.
- **Testing**: How has this been tested?
- **Checklist**:
  - [ ] Code follows style guidelines
  - [ ] Tests pass
  - [ ] Documentation updated
  - [ ] Korean language features tested (if applicable)

## Coding Standards

### Python Guidelines

- Follow PEP 8 with Black's modifications
- Use type hints for function signatures
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Handle errors gracefully

### Documentation

- Use Google-style docstrings
- Include examples in docstrings
- Update README for user-facing changes
- Add inline comments for complex logic

Example:

```python
def convert_document(
    file_path: str,
    korean_mode: bool = False
) -> DocumentResult:
    """Convert a document to markdown format.
    
    Args:
        file_path: Path to the document file.
        korean_mode: Enable Korean text processing.
        
    Returns:
        DocumentResult containing the converted markdown.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        UnsupportedFormatError: If the format isn't supported.
        
    Example:
        >>> result = convert_document("document.pdf", korean_mode=True)
        >>> print(result.markdown)
    """
```

## Documentation

### Updating Documentation

- API changes: Update `docs/api/`
- New features: Update relevant guides
- Korean features: Update Korean language guide
- Configuration: Update deployment docs

### Building Documentation

```bash
# Build documentation locally
make docs-build

# Serve documentation
make docs-serve
# Visit http://localhost:8000
```

## Getting Help

- Check existing issues and discussions
- Join our community chat (if available)
- Ask questions in pull requests
- Contact maintainers for guidance

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- Special thanks section

Thank you for contributing to VoidLight MarkItDown! 🚀