"""
Shared pytest fixtures and configuration for VoidLight MarkItDown tests.
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Any

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add packages to path
PACKAGES_DIR = PROJECT_ROOT / "packages"
for package_dir in PACKAGES_DIR.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_markdown() -> str:
    """Sample markdown content for testing."""
    return """# Test Document

This is a **test** document with:
- Lists
- *Emphasis*
- [Links](https://example.com)

## Code Block
```python
def hello():
    print("Hello, World!")
```
"""


@pytest.fixture
def sample_korean_text() -> str:
    """Sample Korean text for testing."""
    return """# 한국어 테스트 문서

안녕하세요! 이것은 **테스트** 문서입니다.

## 특징
- 한글 지원
- 다양한 *텍스트 스타일*
- [링크](https://example.com)

### 코드 예제
```python
def 인사():
    print("안녕하세요!")
```
"""


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing."""
    # This would be implemented based on your MCP server interface
    pass


@pytest.fixture
def test_files_dir() -> Path:
    """Path to test files directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def performance_threshold() -> dict:
    """Performance thresholds for tests."""
    return {
        "unit_test_max_duration": 1.0,  # seconds
        "integration_test_max_duration": 10.0,
        "e2e_test_max_duration": 60.0,
        "max_memory_mb": 500,
        "max_cpu_percent": 80,
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (multi-component)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full system)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and stress tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "korean: Tests involving Korean language processing"
    )
    config.addinivalue_line(
        "markers", "mcp: Tests for MCP protocol"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        test_path = str(item.fspath)
        
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
        elif "/performance/" in test_path:
            item.add_marker(pytest.mark.performance)
            
        # Add specific markers based on test content
        if "korean" in test_path.lower():
            item.add_marker(pytest.mark.korean)
        if "mcp" in test_path.lower():
            item.add_marker(pytest.mark.mcp)