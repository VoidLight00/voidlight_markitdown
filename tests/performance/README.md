# Performance Tests

Benchmarks, stress tests, and resilience testing for VoidLight MarkItDown.

## Structure

- `stress/` - Load and stress testing frameworks
- `benchmarks/` - Performance benchmarks
- `resilience/` - Chaos engineering and failure recovery tests

## Running Performance Tests

```bash
# Run all performance tests
pytest tests/performance/

# Run specific performance tests
pytest tests/performance/benchmarks/
pytest tests/performance/stress/

# Run with performance report
pytest tests/performance/ --benchmark-only
```

## Test Categories

### Stress Tests
- Concurrent request handling
- Memory usage under load
- CPU utilization
- Network throughput

### Benchmarks
- Conversion speed by format
- Memory efficiency
- Startup time
- Response latency

### Resilience Tests
- Error injection
- Recovery testing
- Chaos engineering
- Failover scenarios

## Performance Baselines

| Metric | Target | Critical |
|--------|--------|----------|
| PDF conversion (10 pages) | < 2s | < 5s |
| Memory usage (idle) | < 100MB | < 200MB |
| Concurrent requests | 100 | 50 |
| Startup time | < 1s | < 3s |

## Running Stress Tests

```bash
# Run basic stress test
python tests/performance/stress/framework/run_stress_tests.py

# Run with custom config
python tests/performance/stress/framework/run_stress_tests.py --config stress_config.json

# Monitor resources
python tests/performance/stress/framework/monitoring_dashboard.py
```

## Example Performance Test

```python
@pytest.mark.performance
@pytest.mark.benchmark
def test_pdf_conversion_speed(benchmark):
    """Benchmark PDF conversion speed."""
    pdf_file = "sample_10pages.pdf"
    
    result = benchmark(convert_pdf, pdf_file)
    
    assert result.success
    assert benchmark.stats['mean'] < 2.0  # Less than 2 seconds
```