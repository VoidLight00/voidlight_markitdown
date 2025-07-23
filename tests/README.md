# Test Organization Structure

This directory contains all tests for the VoidLight MarkItDown project, organized by test type.

## Directory Structure

```
tests/
├── unit/              # Fast, isolated unit tests (71 tests - 58.2%)
│   ├── korean/        # Korean language processing utilities
│   ├── converters/    # Document converter logic
│   └── utils/         # CLI and utility functions
├── integration/       # Integration tests (46 tests - 37.7%)
│   ├── mcp/          # MCP protocol and client tests
│   ├── api/          # External API integrations
│   └── audio_test_suite/ # Audio processing tests
├── e2e/              # End-to-end tests (full system)
│   └── workflows/    # Complete conversion workflows
├── performance/      # Performance tests & benchmarks (5 tests - 4.1%)
│   ├── stress/       # Load and stress testing
│   ├── benchmarks/   # Performance benchmarks
│   └── resilience/   # Chaos engineering tests
└── fixtures/         # Test data and shared fixtures
```

**Total Tests: 122**

## Test Categories

### Unit Tests (`unit/`)
- Individual component tests
- No external dependencies
- Fast execution (< 1 second per test)
- Examples: converter logic, utility functions

### Integration Tests (`integration/`)
- Multi-component interaction tests
- May use test databases or mock services
- Medium execution time (< 10 seconds per test)
- Examples: MCP protocol tests, API integrations

### End-to-End Tests (`e2e/`)
- Full system workflow tests
- Uses real services and dependencies
- Longer execution time
- Examples: Complete conversion workflows

### Performance Tests (`performance/`)
- Benchmarks and stress tests
- Load testing and concurrency tests
- Resource usage monitoring
- Examples: Concurrent request handling, memory usage

### Fixtures (`fixtures/`)
- Shared test data
- Mock responses
- Sample files for testing
- Reusable test utilities

## Running Tests

### Using the Test Runner Script

```bash
# Run all tests
./tests/run_tests.sh

# Run specific test category
./tests/run_tests.sh -t unit
./tests/run_tests.sh -t integration
./tests/run_tests.sh -t e2e
./tests/run_tests.sh -t performance

# Run with coverage
./tests/run_tests.sh -c

# Run tests with specific marker
./tests/run_tests.sh -m korean
./tests/run_tests.sh -m mcp

# Verbose output with coverage
./tests/run_tests.sh -v -c
```

### Using pytest Directly

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
pytest tests/performance/

# Run with coverage
pytest --cov=voidlight_markitdown tests/

# Run specific test file
pytest tests/unit/korean/test_korean_utils.py

# Run tests matching pattern
pytest -k "korean"

# Run tests by marker
pytest -m "unit and not slow"
pytest -m "korean or mcp"
```

### Generate Test Report

```bash
python tests/generate_test_report.py
```

## Test Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Fixtures: Descriptive names in `conftest.py`

## Configuration

- `conftest.py` files contain shared fixtures
- `pytest.ini` in project root for pytest configuration
- Environment-specific settings in `.env.test`