# VoidLight MarkItDown - Incident Response Playbook

## 🚨 Emergency Contacts

- **Primary On-Call**: [Your Name/Team]
- **Escalation**: [Manager/Senior Engineer]
- **Infrastructure**: [DevOps Team]
- **Security**: [Security Team]

## 📋 Incident Severity Levels

### SEV-1 (Critical)
- Complete service outage
- Data corruption or loss
- Security breach
- Korean text processing completely broken

### SEV-2 (High)
- Partial service degradation
- Memory leaks in production
- High error rates (>10%)
- Major converter failures

### SEV-3 (Medium)
- Performance degradation
- Intermittent failures
- Non-critical converter issues
- Minor Korean NLP failures

### SEV-4 (Low)
- Cosmetic issues
- Non-urgent bugs
- Documentation errors

## 🔥 Common Incident Scenarios

### 1. High Memory Usage

**Symptoms:**
- Server using >80% memory
- OOM kills
- Slow response times

**Immediate Actions:**
1. Check current memory usage:
   ```bash
   ps aux | grep voidlight
   free -h
   ```

2. Identify memory-heavy operations:
   ```bash
   # Check for large file conversions
   tail -n 1000 /var/log/voidlight/app.log | grep -E "(large|memory|size)"
   ```

3. Emergency mitigation:
   ```bash
   # Restart service
   systemctl restart voidlight-markitdown
   
   # If critical, enable memory limits
   systemctl edit voidlight-markitdown
   # Add: MemoryMax=4G
   ```

**Root Cause Analysis:**
- Check for large file processing
- Review recent deployments
- Analyze memory profiling data

### 2. Korean Text Processing Failures

**Symptoms:**
- Mojibake (깨진 글자)
- Empty results for Korean documents
- Encoding errors in logs

**Immediate Actions:**
1. Verify locale settings:
   ```bash
   locale | grep -E "(LANG|LC_)"
   echo $LANG
   ```

2. Check Korean NLP libraries:
   ```bash
   python3 -c "import konlpy; print('KoNLPy OK')"
   python3 -c "import kiwipiepy; print('Kiwi OK')"
   ```

3. Test basic Korean processing:
   ```python
   from voidlight_markitdown import VoidLightMarkItDown
   converter = VoidLightMarkItDown(korean_mode=True)
   result = converter.convert_stream(io.BytesIO("테스트".encode('utf-8')))
   print(result.markdown)
   ```

**Root Cause Analysis:**
- Check Java installation for KoNLPy
- Verify font packages installed
- Review encoding configuration

### 3. Converter Failures

**Symptoms:**
- Specific file types failing
- "Converter not found" errors
- Timeout errors

**Immediate Actions:**
1. Identify failing converter:
   ```bash
   tail -n 100 /var/log/voidlight/app.log | grep -i "converter"
   ```

2. Check dependencies:
   ```bash
   # For PDF
   python3 -c "import pdfplumber; print('PDF OK')"
   
   # For DOCX
   python3 -c "import docx; print('DOCX OK')"
   ```

3. Test specific converter:
   ```python
   # Test in isolation
   from voidlight_markitdown.converters import PdfConverter
   converter = PdfConverter()
   # Test with sample file
   ```

### 4. Performance Degradation

**Symptoms:**
- Response times >5s
- CPU usage >80%
- Request timeouts

**Immediate Actions:**
1. Check system resources:
   ```bash
   top -n 1
   iostat -x 1
   netstat -an | grep ESTABLISHED | wc -l
   ```

2. Identify slow operations:
   ```bash
   # Find slow requests
   grep "duration" /var/log/voidlight/app.log | awk '$NF > 5000' | tail -20
   ```

3. Enable emergency rate limiting:
   ```nginx
   # In nginx config
   limit_req_zone $binary_remote_addr zone=emergency:10m rate=10r/s;
   limit_req zone=emergency burst=20;
   ```

### 5. Connection Pool Exhaustion

**Symptoms:**
- "Connection pool exhausted" errors
- Hanging requests
- Resource warnings

**Immediate Actions:**
1. Check connection usage:
   ```bash
   netstat -an | grep :8080 | wc -l
   lsof -p $(pgrep voidlight) | grep -c TCP
   ```

2. Increase pool size temporarily:
   ```python
   # In config
   CONNECTION_POOL_SIZE = 100  # Increase from default
   CONNECTION_TIMEOUT = 30     # Increase timeout
   ```

3. Clear stuck connections:
   ```bash
   # Restart with connection cleanup
   systemctl stop voidlight-markitdown
   sleep 5
   systemctl start voidlight-markitdown
   ```

## 🛠️ Diagnostic Commands

### Health Check
```bash
curl -f http://localhost:8080/health || echo "Health check failed"
```

### Log Analysis
```bash
# Error rate
tail -n 10000 /var/log/voidlight/app.log | grep -c ERROR

# Response times
tail -n 1000 /var/log/voidlight/app.log | grep duration | \
  awk '{print $NF}' | sort -n | tail -20

# Korean processing errors
tail -n 1000 /var/log/voidlight/app.log | grep -i "korean\|encoding\|unicode"
```

### Resource Monitoring
```bash
# Memory usage over time
while true; do
  date
  ps aux | grep voidlight | grep -v grep
  sleep 60
done

# File descriptor usage
lsof -p $(pgrep voidlight) | wc -l
```

## 📊 Monitoring Queries

### Prometheus/Grafana
```promql
# Error rate
rate(voidlight_errors_total[5m])

# Response time P95
histogram_quantile(0.95, rate(voidlight_request_duration_seconds_bucket[5m]))

# Memory usage
process_resident_memory_bytes{job="voidlight"}

# Korean processing failures
rate(voidlight_korean_processing_errors_total[5m])
```

### CloudWatch (AWS)
```
# High memory usage alarm
MetricName: MemoryUtilization
Threshold: 80
Period: 300

# Error rate alarm
MetricName: ErrorRate
Threshold: 0.05
Period: 300
```

## 🔄 Recovery Procedures

### 1. Service Restart
```bash
# Graceful restart
systemctl reload voidlight-markitdown

# Full restart
systemctl restart voidlight-markitdown

# Emergency restart with cleanup
systemctl stop voidlight-markitdown
rm -f /tmp/voidlight-*.lock
rm -rf /tmp/voidlight-cache/*
systemctl start voidlight-markitdown
```

### 2. Rollback Procedure
```bash
# Check current version
voidlight-markitdown --version

# Rollback to previous version
cd /opt/voidlight-markitdown
git log --oneline -5
git checkout <previous-commit>
pip install -e .
systemctl restart voidlight-markitdown
```

### 3. Emergency Configuration
```python
# /etc/voidlight/emergency.conf
DISABLE_KOREAN_NLP = True  # Disable if causing issues
MAX_FILE_SIZE = 10485760   # 10MB limit
TIMEOUT_SECONDS = 30       # Reduce timeout
CACHE_DISABLED = True      # Disable caching
```

## 📝 Post-Incident Actions

1. **Document Timeline**
   - When did the incident start?
   - What were the symptoms?
   - What actions were taken?
   - When was it resolved?

2. **Root Cause Analysis**
   - What caused the incident?
   - Why wasn't it caught earlier?
   - What can prevent recurrence?

3. **Action Items**
   - Code fixes needed
   - Monitoring improvements
   - Documentation updates
   - Process improvements

4. **Metrics to Track**
   - MTTR (Mean Time To Recovery)
   - Incident frequency
   - Customer impact
   - SLA compliance

## 🚀 Preventive Measures

### Daily Checks
- Monitor error rates
- Check memory usage trends
- Verify Korean processing success rate
- Review slow query logs

### Weekly Tasks
- Analyze performance metrics
- Review dependency updates
- Check security advisories
- Update documentation

### Monthly Tasks
- Disaster recovery drill
- Dependency audit
- Performance baseline update
- Incident review meeting

## 📞 Escalation Matrix

| Time | Action | Contact |
|------|--------|---------|
| 0 min | Initial response | On-call engineer |
| 15 min | No progress | Team lead |
| 30 min | Major outage | Engineering manager |
| 60 min | Data loss risk | CTO/VP Engineering |

## 🔗 Related Documents

- [Production Deployment Guide](./production_deployment_guide.md)
- [Monitoring Setup Guide](./monitoring_setup_guide.md)
- [Error Recovery Patterns](./error_recovery_patterns.md)
- [Korean Text Processing Guide](../packages/voidlight_markitdown/docs/korean_nlp_setup.md)