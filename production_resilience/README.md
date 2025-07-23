# Production Resilience Testing Suite

This directory contains comprehensive production resilience testing for VoidLight MarkItDown, ensuring the system can handle real-world failures and recover gracefully.

## 🚀 Quick Start

Run all resilience tests:
```bash
python run_all_resilience_tests.py
```

## 📁 Test Components

### 1. Chaos Engineering Suite (`chaos_engineering_suite.py`)
Tests system behavior under extreme conditions:
- Memory exhaustion scenarios
- Corrupted input handling
- Concurrent failure recovery
- Korean encoding errors
- Resource cleanup validation

### 2. Error Injection Framework (`error_injection_framework.py`)
Systematically injects errors to test resilience:
- Network failures and latency
- File system errors
- Memory pressure
- CPU throttling
- Random exceptions
- Encoding errors

### 3. Recovery Validation Tests (`recovery_validation_tests.py`)
Validates automatic recovery mechanisms:
- Connection pool recovery
- Memory leak prevention
- File handle cleanup
- Korean NLP failover
- Concurrent operation recovery
- Graceful degradation

## 📊 Test Reports

All test results are saved in the `reports/` directory:
- `chaos_engineering_report_*.json` - Chaos test results
- `resilience_validation_*.json` - Error injection results
- `recovery_validation_*.json` - Recovery mechanism results
- `production_resilience_report_*.json` - Consolidated report

## 🔧 Key Features Tested

### Korean Language Support
- Encoding detection and recovery
- NLP library failover
- Mixed script handling
- Mojibake prevention
- Character normalization under stress

### Performance & Scalability
- Large file handling
- Concurrent operations
- Memory management
- Resource cleanup
- Connection pooling

### Error Recovery
- Automatic retry with backoff
- Circuit breaker patterns
- Graceful degradation
- Failover mechanisms
- Resource leak prevention

## 📋 Production Readiness Criteria

The system is considered production-ready when:
- Overall test success rate ≥ 80%
- Resilience score ≥ 0.7
- Recovery success rate ≥ 0.8
- Mean time to recovery < 10 seconds
- No significant memory leaks
- Korean text processing remains functional under stress

## 🛠️ Configuration

### Environment Variables
```bash
# Optional: Adjust test intensity
export CHAOS_TEST_INTENSITY=medium  # low, medium, high
export ERROR_INJECTION_RATE=0.3     # 0.0 to 1.0
export MAX_TEST_DURATION=300        # seconds
```

### Test Customization
Edit test parameters in each test file:
- Memory allocation sizes
- Error injection rates
- Timeout values
- Concurrent operation counts

## 🚨 Important Notes

1. **Resource Usage**: These tests can consume significant system resources. Run on a dedicated test environment.

2. **Time Requirements**: Full test suite takes 15-30 minutes depending on system performance.

3. **Cleanup**: Tests automatically clean up temporary files, but verify `/tmp` if tests are interrupted.

4. **Java Dependency**: Some Korean NLP tests work better with Java installed for KoNLPy.

## 📈 Interpreting Results

### Success Indicators
- ✅ High recovery success rate (>80%)
- ✅ Fast mean time to recovery (<5s)
- ✅ Graceful handling of edge cases
- ✅ Korean text preserved under stress
- ✅ No resource leaks detected

### Warning Signs
- ⚠️ Recovery success rate 60-80%
- ⚠️ Some Korean NLP failures
- ⚠️ Minor resource leaks
- ⚠️ Occasional timeout errors

### Failure Indicators
- ❌ Recovery success rate <60%
- ❌ System crashes during tests
- ❌ Significant memory leaks
- ❌ Korean text corruption
- ❌ Persistent resource exhaustion

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd /Users/voidlight/voidlight_markitdown
   export PYTHONPATH=$PWD:$PYTHONPATH
   ```

2. **Permission Errors**
   ```bash
   # Some tests need to create temporary files
   chmod 755 production_resilience/*.py
   ```

3. **Memory Errors**
   ```bash
   # Increase system limits if needed
   ulimit -m unlimited
   ulimit -v unlimited
   ```

## 📚 Additional Resources

- [Incident Response Playbook](./incident_response_playbook.md)
- [Production Readiness Checklist](./production_readiness_checklist.md)
- [Main Project README](../README.md)
- [Korean NLP Setup Guide](../packages/voidlight_markitdown/docs/korean_nlp_setup.md)

## 🤝 Contributing

To add new resilience tests:
1. Create a new test class following existing patterns
2. Include Korean-specific test cases
3. Add results to the consolidated report
4. Update this README with test descriptions
5. Ensure cleanup of all resources

---

**Note**: These tests are designed to stress the system to its limits. Always run in a controlled environment and never in production.