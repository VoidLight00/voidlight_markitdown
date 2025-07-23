# VoidLight MarkItDown MCP Server - Stress Testing Framework

This comprehensive stress testing framework is designed to evaluate the concurrent access capabilities, resource management, and failure modes of the VoidLight MarkItDown MCP server.

## Features

### 1. **Concurrent Stress Test Framework** (`concurrent_stress_test_framework.py`)
- Multiple load patterns: gradual ramp, spike, sustained, wave, stress-to-failure
- Support for STDIO, HTTP/SSE, and mixed protocol testing
- Real-time metrics collection
- Resource monitoring (CPU, memory, connections)
- Korean text processing stress tests
- Error injection for robustness testing

### 2. **Real-time Monitoring Dashboard** (`monitoring_dashboard.py`)
- Live performance metrics visualization
- Throughput, response times, and error rates
- Resource usage graphs
- Error distribution analysis
- Web-based dashboard at http://localhost:8050

### 3. **Client Simulators** (`client_simulators.py`)
- Specialized client behaviors (steady, burst, random, increasing, oscillating)
- Protocol-specific implementations (HTTP, STDIO, mixed)
- Korean text request generation
- Error injection capabilities
- Connection management and retry logic

### 4. **Performance Analyzer** (`performance_analyzer.py`)
- Bottleneck detection and classification
- Performance metrics analysis
- Scalability assessment
- Optimization recommendations
- Visualization generation

### 5. **Test Orchestrator** (`run_stress_tests.py`)
- Automated test execution
- Environment setup and cleanup
- Result aggregation
- Report generation

## Installation

1. Install dependencies:
```bash
cd /Users/voidlight/voidlight_markitdown/stress_testing
pip install -r requirements.txt
```

2. Ensure MCP server is installed:
```bash
cd /Users/voidlight/voidlight_markitdown
source mcp-env/bin/activate
```

## Usage

### Quick Test (5 minutes)
```bash
python run_stress_tests.py --profile quick
```

### Comprehensive Test (30+ minutes)
```bash
python run_stress_tests.py --profile comprehensive
```

### Korean Text Focus
```bash
python run_stress_tests.py --profile korean_focus
```

### Stress to Failure
```bash
python run_stress_tests.py --profile stress_only
```

### Custom Configuration
```bash
python run_stress_tests.py --config custom_test_config.json
```

## Test Profiles

### Quick
- 3 scenarios
- 60 seconds each
- Up to 30 concurrent clients
- Basic load patterns

### Comprehensive
- 8 scenarios
- 120-600 seconds each
- Up to 200 concurrent clients
- All load patterns
- Korean text stress
- Error injection

### Korean Focus
- 3 scenarios
- 100% Korean text
- Mixed encoding tests
- NLP processing stress

### Stress Only
- 2 scenarios
- Stress to failure
- Extreme payloads
- Maximum load testing

## Configuration

Create a custom configuration file:

```json
{
  "test_profile": "custom",
  "results_dir": "my_test_results",
  "enable_dashboard": true,
  "generate_plots": true,
  "scenario_overrides": {
    "duration_seconds": 120,
    "request_delay_ms": 50
  },
  "custom_scenarios": [
    {
      "name": "my_custom_test",
      "load_pattern": "gradual_ramp",
      "client_type": "http_sse",
      "initial_clients": 10,
      "max_clients": 100,
      "duration_seconds": 300,
      "korean_ratio": 0.7
    }
  ]
}
```

## Metrics Collected

### Performance Metrics
- **Throughput**: Requests per second
- **Response Times**: P50, P95, P99 percentiles
- **Error Rate**: Percentage of failed requests
- **Error Types**: Distribution of error types

### Resource Metrics
- **CPU Usage**: Average and peak
- **Memory Usage**: Average and peak
- **Connections**: Active connection count
- **File Handles**: Open file descriptors

### Scalability Metrics
- **Throughput per Client**: Efficiency metric
- **CPU per Request**: Resource efficiency
- **Response Time Degradation**: Under load

## Reports Generated

### 1. Test Results (`stress_test_results_TIMESTAMP.json`)
Raw test data with all metrics

### 2. Performance Analysis (`performance_analysis_TIMESTAMP.json`)
Identified bottlenecks and recommendations

### 3. Final Report (`final_report_TIMESTAMP.md`)
Executive summary and detailed findings

### 4. Visualizations (`plots/`)
- Performance overview charts
- Metrics correlation heatmap
- Response time distributions

## Bottleneck Detection

The framework automatically detects:

### Application Bottlenecks
- Low throughput vs expected
- High response times
- Response time variance
- Protocol errors

### Resource Bottlenecks
- CPU saturation
- Memory leaks
- Connection exhaustion
- I/O limitations

### Scalability Issues
- Poor efficiency metrics
- Non-linear scaling
- Resource waste

## Optimization Recommendations

Based on detected bottlenecks, the framework provides:

### Immediate Actions
- Configuration changes
- Quick optimizations
- Parameter tuning

### Short-term Improvements
- Code optimizations
- Architecture adjustments
- Caching strategies

### Long-term Solutions
- Architecture redesign
- Horizontal scaling
- Service decomposition

## Monitoring Dashboard

Access the real-time dashboard at http://localhost:8050 during tests:

- Live performance graphs
- Resource usage monitoring
- Error distribution pie charts
- Response time histograms

## Advanced Usage

### Running Individual Components

Test specific client simulator:
```bash
python client_simulators.py --protocol http --clients 50 --duration 60
```

Analyze existing results:
```bash
python performance_analyzer.py results.json --visualize
```

Run dashboard with simulated data:
```bash
python monitoring_dashboard.py --simulate
```

### Debugging

Enable detailed logging:
```bash
export VOIDLIGHT_LOG_LEVEL=DEBUG
python run_stress_tests.py --profile quick
```

## Best Practices

1. **Start Small**: Begin with quick tests before running comprehensive suites
2. **Monitor Resources**: Keep system resource monitor open during tests
3. **Incremental Load**: Use gradual ramp patterns to find breaking points
4. **Multiple Runs**: Run tests multiple times for consistent results
5. **Clean Environment**: Ensure no other processes interfere with tests

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Kill existing MCP server processes
   - Check for dashboard on port 8050

2. **High Error Rates**
   - Reduce max clients
   - Increase timeouts
   - Check server logs

3. **Resource Exhaustion**
   - Increase system limits (ulimit)
   - Reduce concurrent clients
   - Use shorter test durations

## Production Deployment Guidelines

Based on stress test results:

1. **Capacity Planning**
   - Set max clients based on stress test limits
   - Configure timeouts from P95 response times
   - Plan for 20% headroom above peak load

2. **Resource Allocation**
   - CPU: Based on throughput requirements
   - Memory: Peak usage + 50% buffer
   - Connections: Max observed + 30% buffer

3. **Monitoring Setup**
   - Alert on error rate > 5%
   - Alert on P95 response time > threshold
   - Alert on resource usage > 80%

4. **Scaling Strategy**
   - Horizontal scaling for throughput
   - Vertical scaling for Korean text processing
   - Load balancing for mixed workloads