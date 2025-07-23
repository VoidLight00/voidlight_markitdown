# VoidLight MarkItDown Test Report

Generated: 2025-07-23 18:04:31

## Test Statistics

### Test Count by Category

| Category | Count | Percentage |
|----------|-------|------------|
| Unit | 71 | 58.2% |
| Integration | 46 | 37.7% |
| E2e | 0 | 0.0% |
| Performance | 5 | 4.1% |
| **Total** | **122** | **100%** |

## Code Coverage

Coverage data not available. Run tests with `--cov` flag.


## Test Structure Analysis

Found 27 structure issues:

- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/integration/mcp/client_tests
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/integration/mcp/client_tests/clients
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/integration/mcp/client_tests/traces
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/integration/mcp/client_tests/test_files
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/integration/mcp/client_tests/configs
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/integration/mcp/client_tests/reports
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/performance/resilience/framework
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/performance/resilience/chaos
- Missing __init__.py in /Users/voidlight/voidlight_markitdown/tests/performance/stress/framework
- Test file generate_test_report.py doesn't follow naming convention
- Test file run_all_audio_tests.py doesn't follow naming convention
- Test file run_all_tests.py doesn't follow naming convention
- Test file python_test_client.py doesn't follow naming convention
- Test file _test_vectors.py doesn't follow naming convention
- Test file recovery_validation_tests.py doesn't follow naming convention
- Test file run_all_resilience_tests.py doesn't follow naming convention
- Test file production_recovery_tests.py doesn't follow naming convention
- Test file enhanced_error_recovery_tests.py doesn't follow naming convention
- Test file generate_test_files.py doesn't follow naming convention
- Test file run_all_tests.py doesn't follow naming convention
- Test file concurrent_stress_test_framework.py doesn't follow naming convention
- Test file run_stress_tests.py doesn't follow naming convention
- Test file run_chaos_tests.py doesn't follow naming convention
- Test file execute_all_tests.py doesn't follow naming convention
- Test file docker_container_tests.py doesn't follow naming convention
- Test file run_integration_tests_automated.py doesn't follow naming convention
- Test file run_integration_tests.py doesn't follow naming convention

## Recommendations

- Run tests with coverage to identify untested code

## Quick Test Commands

```bash
# Run all tests with coverage
pytest --cov=voidlight_markitdown

# Run specific test categories
pytest tests/unit/           # Fast unit tests
pytest tests/integration/    # Integration tests
pytest tests/e2e/           # End-to-end tests
pytest tests/performance/    # Performance tests

# Run tests by marker
pytest -m korean            # Korean language tests
pytest -m mcp              # MCP protocol tests
```