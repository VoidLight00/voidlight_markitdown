# VoidLight MarkItDown - Production Deployment Guide

## Overview

This guide covers the production deployment of VoidLight MarkItDown with comprehensive error recovery, monitoring, and resilience features. The system has been thoroughly tested for production readiness with chaos engineering and error recovery validation.

## Pre-Deployment Checklist

### 1. Error Recovery Validation
- [ ] Run chaos engineering tests: `python run_chaos_tests.py`
- [ ] Verify all recovery mechanisms pass (>80% recovery rate)
- [ ] Check Korean text processing resilience
- [ ] Validate resource cleanup (no memory/FD leaks)

### 2. System Requirements
- Python 3.8+ with virtual environment
- Java 8+ (for Korean NLP - KoNLPy)
- Minimum 2GB RAM (4GB recommended for Korean NLP)
- 10GB disk space for logs and temporary files
- Network access for external conversions

### 3. Dependencies Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt

# Install Korean NLP dependencies (optional but recommended)
pip install kiwipiepy konlpy soynlp hanspell jamo hanja

# Install monitoring dependencies
pip install prometheus-client psutil
```

## Production Configuration

### 1. Environment Variables
```bash
# Core settings
export VOIDLIGHT_LOG_LEVEL=INFO
export VOIDLIGHT_LOG_FILE=/var/log/voidlight_markitdown/app.log
export VOIDLIGHT_KOREAN_MODE=true
export VOIDLIGHT_MAX_WORKERS=4

# Resource limits
export VOIDLIGHT_MAX_MEMORY_MB=3072
export VOIDLIGHT_MAX_FILE_SIZE_MB=100
export VOIDLIGHT_REQUEST_TIMEOUT_SECONDS=30
export VOIDLIGHT_MAX_CONCURRENT_REQUESTS=100

# Korean NLP settings
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
export KONLPY_DATA_PATH=/opt/voidlight/konlpy_data

# Monitoring
export METRICS_PORT=9090
export HEALTH_CHECK_PORT=8080
```

### 2. Logging Configuration
Create `/etc/voidlight_markitdown/logging.yaml`:
```yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    class: voidlight_markitdown._logging.StructuredFormatter

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: json
    filename: /var/log/voidlight_markitdown/app.log
    maxBytes: 104857600  # 100MB
    backupCount: 10
    encoding: utf-8
  
  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: json
    filename: /var/log/voidlight_markitdown/error.log
    maxBytes: 52428800  # 50MB
    backupCount: 5

root:
  level: INFO
  handlers: [console, file, error_file]

loggers:
  voidlight_markitdown:
    level: INFO
    handlers: [file]
    propagate: false
  
  voidlight_markitdown.performance:
    level: INFO
    handlers: [file]
    propagate: false
```

### 3. Resource Limits
Create `/etc/systemd/system/voidlight-markitdown.service`:
```ini
[Unit]
Description=VoidLight MarkItDown Service
After=network.target

[Service]
Type=simple
User=voidlight
Group=voidlight
WorkingDirectory=/opt/voidlight_markitdown

# Resource limits
LimitNOFILE=65536
LimitNPROC=32768
MemoryLimit=4G
CPUQuota=200%

# Environment
Environment="PYTHONPATH=/opt/voidlight_markitdown"
EnvironmentFile=/etc/voidlight_markitdown/environment

# Restart policy
Restart=always
RestartSec=10
StartLimitBurst=3
StartLimitInterval=60s

# Health check
ExecStartPre=/opt/voidlight_markitdown/venv/bin/python -m voidlight_markitdown.health_check
ExecStart=/opt/voidlight_markitdown/venv/bin/python -m voidlight_markitdown.server

# Graceful shutdown
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

## Error Recovery Features

### 1. Automatic Retry with Backoff
The system implements exponential backoff for transient failures:
- Network timeouts: 3 retries with 1s, 2s, 4s delays
- File system errors: 2 retries with 500ms delay
- External API failures: Circuit breaker after 5 failures

### 2. Resource Management
- **Memory Protection**: Automatic garbage collection triggers
- **File Descriptor Limits**: Pooled connections with automatic cleanup
- **CPU Throttling**: Request rate limiting under high load

### 3. Korean Text Processing Resilience
- **Encoding Detection**: Multi-stage encoding detection with fallbacks
- **NLP Failures**: Graceful degradation to basic text processing
- **Mixed Encodings**: Automatic normalization and correction

### 4. Input Validation
```python
# Implemented validation checks:
- File size limits (configurable, default 100MB)
- Format validation before processing
- Malformed input rejection with detailed errors
- Binary content detection and handling
```

## Monitoring Setup

### 1. Prometheus Metrics
```bash
# Install and configure Prometheus
./chaos_engineering/setup_monitoring.sh

# Key metrics exposed:
- voidlight_http_requests_total
- voidlight_conversion_duration_seconds
- voidlight_error_rate_percent
- voidlight_memory_usage_bytes
- voidlight_korean_documents_processed
- voidlight_concurrent_requests
```

### 2. Health Check Endpoints
```
GET /health
{
  "status": "healthy",
  "timestamp": "2024-01-22T10:30:00Z",
  "checks": {
    "file_system": {"status": "healthy"},
    "memory": {"status": "healthy", "usage_percent": 45.2},
    "disk_space": {"status": "healthy", "free_gb": 25.3},
    "korean_nlp": {"status": "healthy", "available": true}
  }
}

GET /ready
Returns 200 if service is ready to accept requests
```

### 3. Alert Rules
Key alerts configured:
- **High Response Time**: >5s for 5 minutes (warning), >10s (critical)
- **Error Rate**: >5% for 5 minutes (warning), >20% (critical)
- **Memory Usage**: >80% (warning), >95% (critical)
- **Korean NLP Failure**: Unavailable for 1 minute (error)

### 4. Grafana Dashboards
Import dashboards from `/monitoring/grafana/`:
- `overview.json`: Service overview and SLIs
- `performance.json`: Detailed performance metrics
- `errors.json`: Error analysis and patterns
- `korean_processing.json`: Korean-specific metrics
- `resources.json`: Resource utilization

## Deployment Steps

### 1. Initial Deployment
```bash
# 1. Clone repository
git clone https://github.com/your-org/voidlight_markitdown.git
cd voidlight_markitdown

# 2. Run pre-deployment tests
python run_chaos_tests.py
# Verify all tests pass

# 3. Setup environment
./scripts/setup_production.sh

# 4. Deploy application
sudo systemctl start voidlight-markitdown
sudo systemctl enable voidlight-markitdown

# 5. Verify health
curl http://localhost:8080/health
```

### 2. Rolling Update
```bash
# 1. Deploy to canary instance
./scripts/deploy_canary.sh

# 2. Run smoke tests
python tests/smoke_tests.py --target=canary

# 3. Monitor metrics (5-10 minutes)
# Check error rates, response times

# 4. Gradual rollout
./scripts/rolling_update.sh --percentage=25
# Wait and monitor
./scripts/rolling_update.sh --percentage=50
# Wait and monitor
./scripts/rolling_update.sh --percentage=100

# 5. Verify all instances healthy
./scripts/check_fleet_health.sh
```

### 3. Rollback Procedure
```bash
# Automatic rollback on high error rate
# Manual rollback:
./scripts/rollback.sh --version=previous

# Or using systemd:
sudo systemctl stop voidlight-markitdown
cd /opt/voidlight_markitdown
git checkout <previous-version>
sudo systemctl start voidlight-markitdown
```

## Performance Tuning

### 1. Korean NLP Optimization
```python
# In production config:
KOREAN_NLP_CONFIG = {
    'kiwi_num_workers': 4,  # Parallel processing
    'cache_size': 1000,     # LRU cache for repeated text
    'batch_size': 50,       # Batch processing
    'timeout': 5.0          # Fallback on timeout
}
```

### 2. Memory Optimization
- Use streaming for large files (>10MB)
- Implement request pooling
- Configure garbage collection:
  ```python
  import gc
  gc.set_threshold(700, 10, 10)  # More aggressive GC
  ```

### 3. Caching Strategy
- Enable HTTP caching headers
- Implement Redis for conversion cache
- Cache Korean NLP results

## Troubleshooting

### Common Issues and Solutions

1. **High Memory Usage**
   - Check for memory leaks: `python scripts/check_memory_leaks.py`
   - Reduce worker count or request limits
   - Enable memory profiling

2. **Korean NLP Failures**
   - Verify Java installation: `java -version`
   - Check KoNLPy data: `python -m konlpy.data`
   - Fall back to Kiwi if KoNLPy fails

3. **Slow Response Times**
   - Check converter-specific metrics
   - Enable request tracing
   - Review slow query logs

4. **Encoding Errors**
   - Check input file encoding
   - Review encoding detection logs
   - Use manual encoding override if needed

### Emergency Procedures

1. **Service Degradation Mode**
   ```bash
   # Disable non-essential features
   export VOIDLIGHT_DEGRADED_MODE=true
   export VOIDLIGHT_DISABLE_KOREAN_NLP=true
   export VOIDLIGHT_BASIC_CONVERSION_ONLY=true
   sudo systemctl restart voidlight-markitdown
   ```

2. **Emergency Scaling**
   ```bash
   # Horizontal scaling
   ./scripts/emergency_scale.sh --instances=10
   
   # Vertical scaling (requires restart)
   export VOIDLIGHT_MAX_WORKERS=8
   export VOIDLIGHT_MAX_MEMORY_MB=8192
   sudo systemctl restart voidlight-markitdown
   ```

## Maintenance

### Regular Tasks
- **Daily**: Check error logs and metrics
- **Weekly**: Review performance trends
- **Monthly**: Update dependencies, run full test suite
- **Quarterly**: Chaos engineering tests in staging

### Backup and Recovery
```bash
# Backup configuration
/opt/voidlight_markitdown/scripts/backup_config.sh

# Backup logs (before rotation)
/opt/voidlight_markitdown/scripts/backup_logs.sh

# Disaster recovery test
/opt/voidlight_markitdown/scripts/dr_test.sh
```

## Security Considerations

1. **Input Sanitization**: All inputs validated and sanitized
2. **File Upload Limits**: Enforced at multiple levels
3. **Resource Limits**: Prevent DoS attacks
4. **Secure Dependencies**: Regular vulnerability scanning
5. **Korean Text Security**: Special handling for Unicode attacks

## Support and Documentation

- **Runbook**: See `runbook.json` for detailed procedures
- **Monitoring**: Access Grafana at http://monitoring.internal:3000
- **Logs**: Centralized in `/var/log/voidlight_markitdown/`
- **Metrics**: Prometheus at http://monitoring.internal:9090

## Appendix: Validated Error Recovery Scenarios

The following scenarios have been tested and validated:

### Network Failures
- ✅ Network timeouts with retry
- ✅ Connection failures with circuit breaker
- ✅ DNS resolution failures

### File System Errors
- ✅ Permission denied with graceful error
- ✅ Disk full with early detection
- ✅ File corruption with validation

### Resource Exhaustion
- ✅ Memory pressure with GC optimization
- ✅ CPU throttling with request limiting
- ✅ File descriptor exhaustion with pooling

### Korean-Specific
- ✅ Encoding detection failures with fallback
- ✅ NLP library crashes with degradation
- ✅ Mixed encoding documents with normalization

### Input Validation
- ✅ Malformed files with detailed errors
- ✅ Oversized inputs with streaming
- ✅ Binary files with type detection

### Concurrency
- ✅ Thread safety with proper locking
- ✅ Race condition prevention
- ✅ Deadlock detection and recovery

All scenarios achieved >80% recovery rate in testing.