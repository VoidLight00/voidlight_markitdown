# VoidLight MarkItDown Performance Testing Suite

This comprehensive performance testing suite evaluates voidlight_markitdown's capabilities with large files, concurrent operations, and various edge cases.

## Overview

The performance testing suite consists of five main components:

1. **Test File Generation** - Creates realistic test files of various sizes and formats
2. **Performance Benchmarking** - Measures processing time, memory usage, and throughput
3. **Stress Testing** - Pushes the system to its limits
4. **Optimization Validation** - Confirms that performance optimizations are working
5. **Resource Monitoring** - Real-time tracking of system resources

## Quick Start

### Run All Tests (Quick Mode)
```bash
python run_all_tests.py --quick
```

### Run Full Test Suite
```bash
python run_all_tests.py
```

### Run Individual Components
```bash
# Generate test files only
python generate_test_files.py

# Run benchmarks with existing files
python benchmark_large_files.py

# Run stress tests
python stress_test.py

# Validate optimizations
python validate_optimizations.py

# Monitor a single file conversion
python monitor_resources.py /path/to/file.pdf
```

## Test Components

### 1. Test File Generator (`generate_test_files.py`)

Generates test files with:
- **Sizes**: 10MB, 50MB, 100MB, 500MB
- **Formats**: TXT, PDF, DOCX, XLSX
- **Languages**: English, Korean, Mixed
- **Content**: Realistic text with tables, lists, and formatting

Usage:
```bash
python generate_test_files.py
```

Output: `test_files/` directory with generated files and manifest

### 2. Performance Benchmark (`benchmark_large_files.py`)

Comprehensive benchmarking including:
- Single file processing performance
- Concurrent file processing (1-4 workers)
- Memory constraint testing
- Language-specific performance
- File type comparisons

Usage:
```bash
python benchmark_large_files.py [--manifest path/to/manifest.json]
```

Key Metrics:
- Processing time (seconds)
- Memory usage (MB)
- CPU utilization (%)
- Disk I/O (MB/s)
- Throughput (MB/s)

### 3. Stress Testing (`stress_test.py`)

Tests system limits:
- Maximum file size handling
- Concurrent operation limits
- Memory exhaustion scenarios
- Corrupted file handling
- Edge cases (empty files, special characters, etc.)

Usage:
```bash
python stress_test.py [--test all|size|concurrent|memory|corruption|edge]
```

### 4. Optimization Validation (`validate_optimizations.py`)

Validates that optimizations are working:
- Stream processing vs full file loading
- Memory cleanup between conversions
- Chunking efficiency
- Korean processing overhead
- Resource limit handling

Usage:
```bash
python validate_optimizations.py [--test all|stream|memory|chunking|korean|limits]
```

### 5. Resource Monitor (`monitor_resources.py`)

Real-time monitoring during file processing:
- CPU usage tracking
- Memory usage patterns
- Disk I/O rates
- Thread count
- Visual plots of resource usage

Usage:
```bash
python monitor_resources.py /path/to/file.pdf [--output-dir ./results]
```

## Performance Targets

Based on testing, voidlight_markitdown should achieve:

| File Size | Target Time | Max Memory | Throughput |
|-----------|-------------|------------|------------|
| 10MB      | < 5s        | < 100MB    | > 2MB/s    |
| 50MB      | < 25s       | < 250MB    | > 2MB/s    |
| 100MB     | < 60s       | < 500MB    | > 1.5MB/s  |
| 500MB     | < 300s      | < 2GB      | > 1.5MB/s  |

## Test Scenarios

### Basic Performance Test
```bash
# Quick validation (small files only)
python run_all_tests.py --quick
```

### Full Performance Suite
```bash
# Complete test suite (may take 30-60 minutes)
python run_all_tests.py
```

### Specific File Type Testing
```bash
# Generate only PDF files
python generate_test_files.py
# Then benchmark specific files
python benchmark_large_files.py --single-file test_files/test_pdf_english_50mb.pdf
```

### Concurrent Processing Test
```bash
# Test with different worker counts
python benchmark_large_files.py --concurrent 4
```

### Memory Monitoring
```bash
# Monitor memory usage during conversion
python monitor_resources.py test_files/test_docx_korean_100mb.docx
```

## Output Structure

```
performance_test_results/
├── run_YYYYMMDD_HHMMSS/
│   ├── test_files/           # Generated test files
│   ├── benchmarks/           # Benchmark results
│   ├── stress_tests/         # Stress test results
│   ├── validations/          # Optimization validation
│   ├── monitoring/           # Resource monitoring data
│   ├── PERFORMANCE_TEST_REPORT.md
│   └── test_results.json
```

## Key Metrics Explained

### Processing Time
- **Total Time**: Wall clock time from start to finish
- **CPU Time**: Actual CPU cycles used
- **I/O Wait**: Time waiting for disk/network

### Memory Usage
- **RSS (Resident Set Size)**: Physical memory used
- **VMS (Virtual Memory Size)**: Total virtual memory
- **Peak**: Maximum memory used during processing
- **Delta**: Memory increase from baseline

### Throughput
- **MB/s**: Megabytes processed per second
- **Files/s**: Files processed per second (concurrent)
- **Efficiency**: Ratio of actual to theoretical maximum

### CPU Utilization
- **Average**: Mean CPU usage during processing
- **Peak**: Maximum CPU spike
- **Cores Used**: Effective parallelization

## Interpreting Results

### Good Performance Indicators
- Linear scaling with file size
- Memory usage < 5x file size
- CPU utilization 60-90%
- No memory leaks (stable between runs)
- Consistent throughput across languages

### Warning Signs
- Exponential time/memory growth
- Memory usage > 10x file size
- CPU constantly at 100%
- Decreasing throughput with size
- Errors or timeouts

## Best Practices

1. **Before Testing**
   - Ensure sufficient disk space (>10GB)
   - Close unnecessary applications
   - Disable system sleep/hibernation
   - Use SSD for better I/O performance

2. **During Testing**
   - Monitor system resources
   - Keep detailed logs
   - Run multiple iterations
   - Test different file types

3. **After Testing**
   - Clean up test files
   - Analyze trends
   - Compare against baselines
   - Document findings

## Troubleshooting

### Out of Memory
- Reduce file sizes
- Increase system RAM
- Enable swap space
- Test with fewer concurrent workers

### Slow Performance
- Check disk I/O bottlenecks
- Verify no background processes
- Test with SSD vs HDD
- Reduce concurrent operations

### Test Failures
- Check file permissions
- Verify dependencies installed
- Review error logs
- Test with smaller files first

## Advanced Usage

### Custom Test Files
```python
from generate_test_files import TestFileGenerator

generator = TestFileGenerator(base_path="./custom_tests")
generator.generate_text_file(size_mb=200, language="korean")
```

### Custom Benchmarks
```python
from benchmark_large_files import LargeFileBenchmark

benchmark = LargeFileBenchmark()
metrics = benchmark.benchmark_single_file("/path/to/custom/file.pdf")
print(f"Throughput: {metrics.throughput_mbps:.2f}MB/s")
```

### Automated CI Integration
```yaml
# Example GitHub Actions workflow
- name: Run Performance Tests
  run: |
    pip install -r requirements.txt
    python run_all_tests.py --quick --output-dir ./perf-results
    
- name: Upload Results
  uses: actions/upload-artifact@v2
  with:
    name: performance-results
    path: ./perf-results/
```

## Contributing

When adding new performance tests:

1. Follow the existing pattern of test classes
2. Include proper metrics collection
3. Add results to the unified report
4. Document new test scenarios
5. Update performance targets if needed

## Dependencies

Required packages:
```
psutil>=5.8.0       # System resource monitoring
matplotlib>=3.3.0   # Plotting results
reportlab>=3.5.0    # PDF generation
openpyxl>=3.0.0     # Excel file generation
python-docx>=0.8.0  # DOCX generation
lorem>=0.1.1        # Lorem ipsum text
```

Install all dependencies:
```bash
pip install psutil matplotlib reportlab openpyxl python-docx lorem
```

## License

This performance testing suite is part of voidlight_markitdown and follows the same license terms.