# Production Readiness Checklist - VoidLight MarkItDown

## 🏗️ Infrastructure Requirements

### ✅ System Requirements
- [ ] **OS**: Ubuntu 20.04+ or compatible Linux distribution
- [ ] **Python**: 3.9, 3.10, or 3.11 installed
- [ ] **Memory**: Minimum 4GB RAM (8GB recommended)
- [ ] **Storage**: 10GB free space for logs and temp files
- [ ] **CPU**: 2+ cores (4+ recommended for concurrent operations)

### ✅ Korean Language Support
- [ ] **Locale**: `ko_KR.UTF-8` installed and configured
- [ ] **Fonts**: Korean fonts installed (Noto Sans CJK)
- [ ] **Java**: OpenJDK 11+ for KoNLPy (optional but recommended)
- [ ] **Environment**: `LANG=ko_KR.UTF-8` set

### ✅ Network Requirements
- [ ] **Ports**: 8080 (HTTP), 8081 (metrics), 8082 (health)
- [ ] **Firewall**: Configured for service ports
- [ ] **DNS**: Proper hostname resolution
- [ ] **SSL/TLS**: Certificates for HTTPS (production)

## 🔧 Application Configuration

### ✅ Core Configuration
- [ ] **Config Files**: `/etc/voidlight/config.yaml` created
- [ ] **Logging**: Configured with rotation (max 1GB/file)
- [ ] **Temp Directory**: Writable and with cleanup cron
- [ ] **File Limits**: `ulimit -n 65536` set

### ✅ Performance Tuning
```yaml
# config.yaml
max_workers: 10
connection_pool_size: 50
request_timeout: 30
max_file_size: 104857600  # 100MB
korean_mode: true
enable_caching: true
cache_ttl: 3600
```

### ✅ Security Configuration
- [ ] **User**: Non-root service user created
- [ ] **Permissions**: Restrictive file permissions (640/750)
- [ ] **Secrets**: Environment variables or secret manager
- [ ] **Input Validation**: File size and type limits enforced
- [ ] **Rate Limiting**: Configured at proxy level

## 📊 Monitoring & Alerting

### ✅ Metrics Collection
- [ ] **Prometheus**: Endpoint exposed at `/metrics`
- [ ] **Custom Metrics**:
  - `voidlight_requests_total`
  - `voidlight_request_duration_seconds`
  - `voidlight_errors_total`
  - `voidlight_korean_processing_total`
  - `voidlight_converter_usage{converter="..."}`

### ✅ Logging Configuration
- [ ] **Structured Logging**: JSON format enabled
- [ ] **Log Levels**: Appropriate for production (INFO)
- [ ] **Log Aggregation**: Fluentd/Logstash configured
- [ ] **Log Retention**: 30 days minimum

### ✅ Alerts Configuration
```yaml
alerts:
  - name: HighErrorRate
    threshold: 0.05  # 5% error rate
    duration: 5m
    severity: warning
  
  - name: HighMemoryUsage
    threshold: 80  # 80% memory
    duration: 10m
    severity: critical
  
  - name: KoreanProcessingFailures
    threshold: 0.10  # 10% failure rate
    duration: 5m
    severity: warning
```

### ✅ Health Checks
- [ ] **Endpoint**: `/health` returns 200 OK
- [ ] **Deep Check**: `/health/deep` validates dependencies
- [ ] **Readiness**: `/ready` for load balancer
- [ ] **Liveness**: `/alive` for container orchestration

## 🚀 Deployment Configuration

### ✅ Service Management
```ini
# /etc/systemd/system/voidlight-markitdown.service
[Unit]
Description=VoidLight MarkItDown MCP Server
After=network.target

[Service]
Type=simple
User=voidlight
Group=voidlight
WorkingDirectory=/opt/voidlight-markitdown
Environment="PYTHONPATH=/opt/voidlight-markitdown"
Environment="LANG=ko_KR.UTF-8"
ExecStart=/usr/bin/python3 -m voidlight_markitdown.server
Restart=always
RestartSec=10
MemoryMax=4G
TasksMax=1000

[Install]
WantedBy=multi-user.target
```

### ✅ Load Balancing
- [ ] **Reverse Proxy**: Nginx/HAProxy configured
- [ ] **Sticky Sessions**: Not required (stateless)
- [ ] **Connection Pooling**: Configured at proxy
- [ ] **Request Timeout**: 60s at proxy level

### ✅ Auto-Scaling (if applicable)
- [ ] **Metrics**: CPU > 70% or Memory > 80%
- [ ] **Min Instances**: 2
- [ ] **Max Instances**: 10
- [ ] **Cooldown**: 300 seconds

## 🔐 Security Checklist

### ✅ Application Security
- [ ] **Dependencies**: All updated, no known CVEs
- [ ] **Input Sanitization**: File uploads validated
- [ ] **Path Traversal**: Protected against directory traversal
- [ ] **Resource Limits**: Max file size, timeout configured
- [ ] **Error Messages**: No sensitive info exposed

### ✅ Infrastructure Security
- [ ] **Firewall**: Only required ports open
- [ ] **SSH**: Key-based auth only
- [ ] **Updates**: Automatic security updates enabled
- [ ] **Audit Logging**: System calls logged
- [ ] **SELinux/AppArmor**: Configured if required

## 📦 Dependency Management

### ✅ Python Dependencies
```bash
# Verify all dependencies
pip check

# Security scan
pip-audit

# License check
pip-licenses --format=markdown
```

### ✅ System Dependencies
- [ ] **libmagic**: For file type detection
- [ ] **tesseract**: For OCR (if using)
- [ ] **ffmpeg**: For audio conversion
- [ ] **Java Runtime**: For KoNLPy

## 🔄 Backup & Recovery

### ✅ Data Backup
- [ ] **Logs**: Backed up daily
- [ ] **Configuration**: Version controlled
- [ ] **Temp Files**: Cleanup policy defined
- [ ] **Cache**: Can be regenerated

### ✅ Disaster Recovery
- [ ] **RTO**: 15 minutes defined
- [ ] **RPO**: Not applicable (stateless)
- [ ] **Runbook**: Documented procedures
- [ ] **Backup Region**: Secondary deployment ready

## 🧪 Testing Requirements

### ✅ Pre-Production Testing
- [ ] **Load Testing**: 100 concurrent users passed
- [ ] **Stress Testing**: Breaking point identified
- [ ] **Soak Testing**: 24-hour test passed
- [ ] **Korean Content**: Extensive testing done
- [ ] **File Types**: All converters tested

### ✅ Smoke Tests
```bash
# Basic health check
curl http://localhost:8080/health

# Korean text processing
echo "안녕하세요" | curl -X POST http://localhost:8080/convert \
  -H "Content-Type: text/plain; charset=utf-8" -d @-

# File conversion
curl -X POST http://localhost:8080/convert \
  -F "file=@sample.pdf" \
  -H "Accept: text/markdown"
```

## 📋 Operational Procedures

### ✅ Deployment Process
1. [ ] **Pre-deployment**: Run test suite
2. [ ] **Backup**: Current version backed up
3. [ ] **Deploy**: Blue-green or rolling update
4. [ ] **Verify**: Health checks pass
5. [ ] **Monitor**: Watch metrics for 30 min
6. [ ] **Rollback**: Plan ready if needed

### ✅ Maintenance Windows
- [ ] **Schedule**: Defined and communicated
- [ ] **Duration**: Maximum 2 hours
- [ ] **Notification**: 48 hours advance notice
- [ ] **Rollback**: Tested procedure

## 📊 Performance Baselines

### ✅ Expected Metrics
| Metric | Target | Acceptable |
|--------|--------|------------|
| Response Time (P50) | <500ms | <1s |
| Response Time (P99) | <2s | <5s |
| Error Rate | <0.1% | <1% |
| Throughput | 100 RPS | 50 RPS |
| Memory Usage | <2GB | <4GB |
| CPU Usage | <50% | <80% |

### ✅ Korean Processing Metrics
| Operation | Target | Acceptable |
|-----------|--------|------------|
| Tokenization | <100ms | <500ms |
| NLP Analysis | <500ms | <2s |
| Encoding Detection | <50ms | <200ms |
| Character Normalization | <20ms | <100ms |

## 🚦 Go-Live Criteria

### Must Have (Blockers)
- [ ] All security vulnerabilities addressed
- [ ] Health checks passing
- [ ] Monitoring configured and tested
- [ ] Incident response plan ready
- [ ] Korean text processing verified
- [ ] Load testing passed

### Should Have
- [ ] Auto-scaling configured
- [ ] Advanced monitoring dashboards
- [ ] Automated deployment pipeline
- [ ] Performance profiling completed

### Nice to Have
- [ ] A/B testing capability
- [ ] Feature flags system
- [ ] Advanced analytics
- [ ] Multi-region deployment

## 🎯 Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Development Lead | | | |
| Operations Lead | | | |
| Security Lead | | | |
| Product Owner | | | |

## 📝 Notes

**Last Updated**: [Date]  
**Version**: 1.0  
**Next Review**: [Date + 3 months]

---

### Post-Deployment Checklist

After going live, verify within 24 hours:
- [ ] No memory leaks observed
- [ ] Error rates within acceptable range
- [ ] Korean processing working correctly
- [ ] All converters functional
- [ ] Logs properly collected
- [ ] Alerts firing correctly
- [ ] Performance meets baselines