# VoidLight MarkItDown MCP Server - Integration Testing Guide

## Overview

This comprehensive integration testing suite provides automated testing for the VoidLight MarkItDown MCP server in both STDIO and HTTP/SSE modes. The suite includes protocol compliance testing, performance benchmarking, stress testing, and Korean text processing validation.

## Test Suite Components

### 1. Enhanced Integration Test Suite (`test_mcp_integration_enhanced.py`)

The most comprehensive test suite that includes:

- **Protocol Compliance Testing**: Validates all MCP protocol methods
- **Performance Testing**: Measures response times, memory usage, and throughput
- **Stress Testing**: Tests server stability under high load
- **Concurrent Client Testing**: Validates multi-client handling
- **Korean Text Processing**: Comprehensive Unicode and encoding tests
- **Edge Case Testing**: Handles malformed input, large files, etc.
- **Automated Reporting**: Generates detailed JSON reports

### 2. Automated Test Runner (`run_integration_tests_automated.py`)

A flexible test orchestrator that:

- Runs multiple test suites
- Supports configuration via JSON
- Implements retry logic for flaky tests
- Saves test artifacts
- Supports CI/CD integration
- Can send notifications (email/Slack)

### 3. Quick Integration Test (`test_quick_integration.py`)

A lightweight test for rapid validation:

- Verifies basic server startup
- Tests STDIO and HTTP modes
- Provides quick health check
- Useful for development iterations

## Running Tests

### Quick Test

```bash
# Run quick validation
python test_quick_integration.py
```

### Full Test Suite

```bash
# Run enhanced integration tests
python test_mcp_integration_enhanced.py

# Run with automated runner
python run_integration_tests_automated.py --config test_config.json

# Run specific test suites
python run_integration_tests_automated.py --suites enhanced comprehensive

# Run without retries
python run_integration_tests_automated.py --no-retry
```

### Docker-based Testing

```bash
# Build test image
docker build -f Dockerfile.test -t mcp-integration-tests .

# Run tests in container
docker run -v $(pwd)/test_artifacts:/app/test_artifacts mcp-integration-tests

# Use docker-compose for full test environment
docker-compose -f docker-compose.test.yml up
```

## Configuration

The test suite can be configured via `test_config.json`:

```json
{
  "test_suites": ["enhanced", "comprehensive"],
  "timeout_minutes": 30,
  "retry_failed": true,
  "max_retries": 2,
  "save_artifacts": true,
  "artifact_dir": "test_artifacts",
  "performance_thresholds": {
    "initialization_time": 2.0,
    "tool_call_time": 5.0,
    "concurrent_clients": 10,
    "memory_usage_mb": 500,
    "response_time_p95": 3.0
  }
}
```

## Test Categories

### 1. Protocol Tests
- MCP initialization
- Tool listing and discovery
- Tool invocation
- Error handling
- Resource management

### 2. Performance Tests
- Response time benchmarks
- Memory usage monitoring
- Throughput testing
- Concurrent client handling
- Stress testing

### 3. Korean Processing Tests
- Basic Hangul characters
- Complex character combinations
- Special characters (㈜, ㎡, ℃)
- Mixed scripts (Korean/English/Chinese)
- Encoding handling (UTF-8, EUC-KR, CP949)
- Normalization testing

### 4. Edge Cases
- Empty files
- Binary data
- Very large files
- Malformed requests
- Invalid URIs
- Null bytes and special characters

## CI/CD Integration

### GitHub Actions

The included workflow (`.github/workflows/integration-tests.yml`) provides:

- Multi-Python version testing (3.9, 3.10, 3.11)
- Automated test execution on push/PR
- Scheduled daily tests
- Artifact collection
- Performance regression detection
- Test report generation

### Running in CI

```yaml
- name: Run integration tests
  run: |
    python run_integration_tests_automated.py --config test_config.json
  env:
    VOIDLIGHT_LOG_LEVEL: INFO
```

## Test Artifacts

Test runs generate several artifacts:

1. **Test Reports**: `integration_test_report_YYYYMMDD_HHMMSS.json`
2. **Test Summary**: `test_summary_YYYYMMDD_HHMMSS.json`
3. **Log Files**: `stdout.txt`, `stderr.txt`
4. **Performance Data**: Performance metrics in JSON format

Artifacts are saved in the `test_artifacts/` directory by default.

## Performance Monitoring

The test suite tracks several performance metrics:

- **Initialization Time**: Time to initialize MCP session
- **Tool Call Time**: Time to execute tool calls
- **Response Time P95**: 95th percentile response time
- **Memory Usage**: Server memory consumption
- **Throughput**: Requests per second under load

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # The test suite automatically finds free ports
   # Or manually specify a port:
   export TEST_PORT_BASE=4000
   ```

2. **Virtual Environment Issues**
   ```bash
   # Ensure virtual environment is activated
   source mcp-env/bin/activate
   ```

3. **Korean Text Display Issues**
   ```bash
   # Ensure UTF-8 locale
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

### Debug Mode

Enable detailed logging:

```bash
export VOIDLIGHT_LOG_LEVEL=DEBUG
python test_mcp_integration_enhanced.py
```

## Extending the Test Suite

### Adding New Test Cases

1. Create a new test method in the test class:
   ```python
   async def _test_custom_feature(self):
       print(f"\n{BLUE}Testing Custom Feature...{RESET}")
       # Test implementation
   ```

2. Add metrics tracking:
   ```python
   self.metrics.add_result("Category", "Test Name", passed, message, details)
   self.metrics.add_performance_metric("metric_name", value)
   ```

3. Include in test runner:
   ```python
   await self._test_custom_feature()
   ```

### Adding New Test Suites

1. Create a new test script
2. Add to `TEST_SCRIPTS` in `run_integration_tests_automated.py`
3. Update `test_config.json` to include the new suite

## Best Practices

1. **Always clean up resources**: Use try/finally blocks
2. **Track metrics**: Add performance metrics for benchmarking
3. **Handle timeouts**: Use asyncio timeouts for network operations
4. **Test isolation**: Each test should be independent
5. **Descriptive output**: Use colored output and clear messages
6. **Save artifacts**: Preserve test output for debugging

## Reporting Issues

When reporting test failures:

1. Include the test report JSON file
2. Provide stdout/stderr logs
3. Specify Python version and platform
4. Include any error tracebacks
5. Note any environment-specific configurations