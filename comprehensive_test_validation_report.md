# Voidlight MarkItDown Test Validation Report

**Date**: 2025-07-23T00:34:20.545213  
**Duration**: 222.92 seconds  
**Python Version**: 3.11.13  
**Platform**: darwin  

## Executive Summary

- **Total Test Files Executed**: 11
- **Total Tests Passed**: 145
- **Total Tests Failed**: 14
- **Total Tests Skipped**: 1
- **Overall Pass Rate**: 91.2%

## Category Breakdown

| Category | Total | Passed | Failed | Error |
|----------|-------|--------|--------|-------|
| unit_test | 3 | 1 | 2 | 0 |
| korean_nlp | 1 | 1 | 0 | 0 |
| korean_nlp_test | 3 | 1 | 2 | 0 |
| converter_test | 1 | 1 | 0 | 0 |
| cli_test | 2 | 0 | 1 | 1 |
| integration_test | 1 | 1 | 0 | 0 |

## Test Execution Details

### ✅ packages/voidlight_markitdown/tests/test_voidlight_markitdown.py

- **Category**: unit_test
- **Status**: passed
- **Results**: 10 passed, 0 failed, 0 skipped
- **Duration**: 14.84s

### ❌ packages/voidlight_markitdown/tests/test_module_misc.py

- **Category**: unit_test
- **Status**: failed
- **Results**: 8 passed, 2 failed, 1 skipped
- **Duration**: 11.61s

### ❌ packages/voidlight_markitdown/tests/test_module_vectors.py

- **Category**: unit_test
- **Status**: failed
- **Results**: 105 passed, 4 failed, 0 skipped
- **Duration**: 29.06s

### ✅ Korean NLP Status Check

- **Category**: korean_nlp
- **Status**: passed

### ❌ packages/voidlight_markitdown/tests/test_korean_nlp_features.py

- **Category**: korean_nlp_test
- **Status**: failed
- **Results**: 5 passed, 0 failed, 0 skipped
- **Duration**: 9.99s

### ✅ packages/voidlight_markitdown/tests/test_korean_utils.py

- **Category**: korean_nlp_test
- **Status**: passed
- **Results**: 12 passed, 0 failed, 0 skipped
- **Duration**: 15.96s

### ❌ packages/voidlight_markitdown/test_korean_nlp_simple.py

- **Category**: korean_nlp_test
- **Status**: failed
- **Results**: 2 passed, 1 failed, 0 skipped
- **Duration**: 6.45s

### ✅ Converter Availability Test

- **Category**: converter_test
- **Status**: passed
- **Results**: 2 passed, 5 failed, 0 skipped

### ❌ packages/voidlight_markitdown/tests/test_cli_misc.py

- **Category**: cli_test
- **Status**: failed
- **Results**: 1 passed, 1 failed, 0 skipped
- **Duration**: 6.92s

### ❌ packages/voidlight_markitdown/tests/test_cli_vectors.py

- **Category**: cli_test
- **Status**: timeout

### ✅ Basic Integration Test

- **Category**: integration_test
- **Status**: passed
- **Results**: 0 passed, 1 failed, 0 skipped

## Reproducible Test Commands

```bash
# Activate virtual environment
source mcp-env/bin/activate

# Run individual test commands
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/tests/test_voidlight_markitdown.py -v --tb=short --json-report --json-report-file=test_report_temp.json
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/tests/test_module_misc.py -v --tb=short --json-report --json-report-file=test_report_temp.json
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/tests/test_module_vectors.py -v --tb=short --json-report --json-report-file=test_report_temp.json
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/tests/test_korean_nlp_features.py -v --tb=short --json-report --json-report-file=test_report_temp.json
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/tests/test_korean_utils.py -v --tb=short --json-report --json-report-file=test_report_temp.json
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/test_korean_nlp_simple.py -v --tb=short --json-report --json-report-file=test_report_temp.json
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/tests/test_cli_misc.py -v --tb=short --json-report --json-report-file=test_report_temp.json
/Users/voidlight/voidlight_markitdown/mcp-env/bin/python -m pytest packages/voidlight_markitdown/tests/test_cli_vectors.py -v --tb=short --json-report --json-report-file=test_report_temp.json
```
