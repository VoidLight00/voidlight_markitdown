#!/usr/bin/env python3
"""
Production monitoring and alerting configuration for VoidLight MarkItDown
Provides health checks, metrics collection, and alert rules
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import threading
import queue
from collections import deque, defaultdict


class MetricType(Enum):
    """Types of metrics to collect"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Single metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    metric_name: str
    condition: str  # e.g., "> 90", "< 10", "== 0"
    severity: AlertSeverity
    duration: timedelta
    message_template: str
    labels: Dict[str, str] = field(default_factory=dict)
    cooldown: timedelta = timedelta(minutes=5)


@dataclass
class Alert:
    """Active alert instance"""
    rule: AlertRule
    triggered_at: datetime
    metric_value: float
    message: str
    resolved_at: Optional[datetime] = None


class MetricsCollector:
    """Collects and stores metrics"""
    
    def __init__(self, retention_period: timedelta = timedelta(hours=24)):
        self.retention_period = retention_period
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.lock = threading.Lock()
        
    def record_metric(self, metric: Metric):
        """Record a metric value"""
        with self.lock:
            key = self._metric_key(metric.name, metric.labels)
            
            if metric.metric_type == MetricType.COUNTER:
                self.counters[key] += metric.value
                metric.value = self.counters[key]
                
            self.metrics[key].append((metric.timestamp, metric.value))
            self._cleanup_old_metrics()
            
    def get_metric_values(self, name: str, labels: Optional[Dict[str, str]] = None,
                         time_range: Optional[timedelta] = None) -> List[Tuple[datetime, float]]:
        """Get metric values within time range"""
        with self.lock:
            key = self._metric_key(name, labels or {})
            values = list(self.metrics.get(key, []))
            
            if time_range:
                cutoff = datetime.now() - time_range
                values = [(ts, val) for ts, val in values if ts >= cutoff]
                
            return values
            
    def get_current_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get most recent metric value"""
        values = self.get_metric_values(name, labels, timedelta(minutes=1))
        return values[-1][1] if values else None
        
    def _metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """Generate unique key for metric"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
        
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff = datetime.now() - self.retention_period
        
        for key in list(self.metrics.keys()):
            # Remove old values
            while self.metrics[key] and self.metrics[key][0][0] < cutoff:
                self.metrics[key].popleft()
                
            # Remove empty metric series
            if not self.metrics[key]:
                del self.metrics[key]


class AlertManager:
    """Manages alert rules and active alerts"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.lock = threading.Lock()
        
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        with self.lock:
            self.rules.append(rule)
            
    def check_alerts(self) -> List[Alert]:
        """Check all alert rules and return new alerts"""
        new_alerts = []
        
        with self.lock:
            for rule in self.rules:
                alert_key = f"{rule.name}:{rule.metric_name}"
                
                # Check if alert is in cooldown
                if alert_key in self.active_alerts:
                    alert = self.active_alerts[alert_key]
                    if alert.resolved_at and (datetime.now() - alert.resolved_at) < rule.cooldown:
                        continue
                        
                # Get metric values for duration
                values = self.metrics_collector.get_metric_values(
                    rule.metric_name, rule.labels, rule.duration
                )
                
                if not values:
                    continue
                    
                # Check if condition is met for entire duration
                condition_met = True
                latest_value = values[-1][1]
                
                for _, value in values:
                    if not self._evaluate_condition(value, rule.condition):
                        condition_met = False
                        break
                        
                # Handle alert state changes
                if condition_met and alert_key not in self.active_alerts:
                    # New alert
                    alert = Alert(
                        rule=rule,
                        triggered_at=datetime.now(),
                        metric_value=latest_value,
                        message=rule.message_template.format(
                            metric_name=rule.metric_name,
                            value=latest_value,
                            threshold=rule.condition
                        )
                    )
                    self.active_alerts[alert_key] = alert
                    new_alerts.append(alert)
                    self.alert_history.append(alert)
                    
                elif not condition_met and alert_key in self.active_alerts:
                    # Alert resolved
                    alert = self.active_alerts[alert_key]
                    alert.resolved_at = datetime.now()
                    del self.active_alerts[alert_key]
                    
        return new_alerts
        
    def _evaluate_condition(self, value: float, condition: str) -> bool:
        """Evaluate alert condition"""
        try:
            # Parse condition (e.g., "> 90", "< 10", "== 0")
            parts = condition.split()
            if len(parts) != 2:
                return False
                
            operator, threshold = parts[0], float(parts[1])
            
            if operator == '>':
                return value > threshold
            elif operator == '>=':
                return value >= threshold
            elif operator == '<':
                return value < threshold
            elif operator == '<=':
                return value <= threshold
            elif operator == '==':
                return value == threshold
            elif operator == '!=':
                return value != threshold
            else:
                return False
                
        except:
            return False


class HealthChecker:
    """Health check implementation"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.checks = []
        
    def add_check(self, name: str, check_func, timeout: float = 5.0):
        """Add a health check"""
        self.checks.append({
            'name': name,
            'func': check_func,
            'timeout': timeout
        })
        
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        for check in self.checks:
            try:
                # Run check with timeout
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(check['func'])
                    result = future.result(timeout=check['timeout'])
                    
                results['checks'][check['name']] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'details': result
                }
                
                if not result:
                    results['status'] = 'unhealthy'
                    
            except Exception as e:
                results['checks'][check['name']] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                results['status'] = 'unhealthy'
                
        return results
        
    # Built-in health checks
    def check_file_system(self) -> bool:
        """Check file system health"""
        try:
            # Check if we can write to temp
            test_file = Path("/tmp/health_check_test.txt")
            test_file.write_text("test")
            test_file.unlink()
            return True
        except:
            return False
            
    def check_memory(self) -> bool:
        """Check memory availability"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            # Alert if less than 10% memory available
            return mem.percent < 90
        except:
            return True  # Assume OK if can't check
            
    def check_disk_space(self) -> bool:
        """Check disk space"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            # Alert if less than 10% disk space
            return disk.percent < 90
        except:
            return True  # Assume OK if can't check
            
    def check_korean_nlp(self) -> bool:
        """Check Korean NLP functionality"""
        try:
            from packages.voidlight_markitdown.src.voidlight_markitdown._korean_utils import KoreanTextProcessor
            processor = KoreanTextProcessor()
            result = processor.detect_korean_ratio("안녕하세요")
            return result > 0.5
        except:
            return False


def create_production_monitoring_config() -> Dict[str, Any]:
    """Create production monitoring configuration"""
    
    config = {
        "metrics": {
            "collection_interval": 10,  # seconds
            "retention_period": 86400,  # 24 hours in seconds
            "export_interval": 60,  # Export metrics every minute
        },
        
        "health_checks": {
            "interval": 30,  # seconds
            "timeout": 10,  # seconds per check
            "endpoint": "/health",
            "checks": [
                "file_system",
                "memory",
                "disk_space",
                "korean_nlp",
                "converter_availability"
            ]
        },
        
        "alert_rules": [
            # Performance alerts
            {
                "name": "high_response_time",
                "metric": "http_request_duration_seconds",
                "condition": "> 5",
                "severity": "warning",
                "duration": 300,  # 5 minutes
                "message": "Response time > 5 seconds for 5 minutes"
            },
            {
                "name": "very_high_response_time",
                "metric": "http_request_duration_seconds",
                "condition": "> 10",
                "severity": "critical",
                "duration": 60,  # 1 minute
                "message": "Response time > 10 seconds"
            },
            
            # Error rate alerts
            {
                "name": "high_error_rate",
                "metric": "error_rate_percent",
                "condition": "> 5",
                "severity": "warning",
                "duration": 300,
                "message": "Error rate > 5% for 5 minutes"
            },
            {
                "name": "critical_error_rate",
                "metric": "error_rate_percent",
                "condition": "> 20",
                "severity": "critical",
                "duration": 60,
                "message": "Error rate > 20%"
            },
            
            # Resource alerts
            {
                "name": "high_memory_usage",
                "metric": "memory_usage_percent",
                "condition": "> 80",
                "severity": "warning",
                "duration": 300,
                "message": "Memory usage > 80% for 5 minutes"
            },
            {
                "name": "critical_memory_usage",
                "metric": "memory_usage_percent",
                "condition": "> 95",
                "severity": "critical",
                "duration": 60,
                "message": "Memory usage > 95%"
            },
            {
                "name": "high_disk_usage",
                "metric": "disk_usage_percent",
                "condition": "> 85",
                "severity": "warning",
                "duration": 300,
                "message": "Disk usage > 85%"
            },
            
            # Korean processing alerts
            {
                "name": "korean_nlp_failure",
                "metric": "korean_nlp_available",
                "condition": "== 0",
                "severity": "error",
                "duration": 60,
                "message": "Korean NLP unavailable"
            },
            {
                "name": "high_korean_encoding_errors",
                "metric": "korean_encoding_error_rate",
                "condition": "> 10",
                "severity": "warning",
                "duration": 300,
                "message": "Korean encoding error rate > 10%"
            },
            
            # Concurrent request alerts
            {
                "name": "high_concurrent_requests",
                "metric": "concurrent_requests",
                "condition": "> 100",
                "severity": "warning",
                "duration": 300,
                "message": "Concurrent requests > 100 for 5 minutes"
            },
            
            # File descriptor alerts
            {
                "name": "high_fd_usage",
                "metric": "open_file_descriptors",
                "condition": "> 900",
                "severity": "warning",
                "duration": 60,
                "message": "Open file descriptors > 900"
            }
        ],
        
        "metrics_to_collect": [
            # Request metrics
            {
                "name": "http_requests_total",
                "type": "counter",
                "labels": ["method", "endpoint", "status"]
            },
            {
                "name": "http_request_duration_seconds",
                "type": "histogram",
                "labels": ["method", "endpoint"],
                "buckets": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            },
            
            # Conversion metrics
            {
                "name": "conversions_total",
                "type": "counter",
                "labels": ["format", "status", "korean_mode"]
            },
            {
                "name": "conversion_duration_seconds",
                "type": "histogram",
                "labels": ["format"],
                "buckets": [0.1, 0.5, 1.0, 5.0, 10.0, 30.0]
            },
            {
                "name": "conversion_size_bytes",
                "type": "histogram",
                "labels": ["format"],
                "buckets": [1024, 10240, 102400, 1048576, 10485760, 104857600]
            },
            
            # Error metrics
            {
                "name": "errors_total",
                "type": "counter",
                "labels": ["type", "converter", "severity"]
            },
            {
                "name": "error_rate_percent",
                "type": "gauge",
                "calculation": "rate(errors_total) / rate(http_requests_total) * 100"
            },
            
            # Resource metrics
            {
                "name": "memory_usage_bytes",
                "type": "gauge"
            },
            {
                "name": "memory_usage_percent",
                "type": "gauge"
            },
            {
                "name": "cpu_usage_percent",
                "type": "gauge"
            },
            {
                "name": "disk_usage_percent",
                "type": "gauge"
            },
            {
                "name": "open_file_descriptors",
                "type": "gauge"
            },
            {
                "name": "concurrent_requests",
                "type": "gauge"
            },
            
            # Korean processing metrics
            {
                "name": "korean_documents_processed",
                "type": "counter",
                "labels": ["nlp_library", "status"]
            },
            {
                "name": "korean_encoding_errors",
                "type": "counter",
                "labels": ["encoding_from", "encoding_to"]
            },
            {
                "name": "korean_nlp_available",
                "type": "gauge",
                "values": [0, 1]  # Binary
            },
            {
                "name": "korean_processing_duration_seconds",
                "type": "histogram",
                "labels": ["operation"],
                "buckets": [0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
            }
        ],
        
        "logging": {
            "level": "INFO",
            "format": "json",
            "outputs": [
                {
                    "type": "file",
                    "path": "/var/log/voidlight_markitdown/app.log",
                    "max_size_mb": 100,
                    "max_files": 10
                },
                {
                    "type": "stdout",
                    "format": "text"  # Human readable for console
                }
            ],
            "slow_query_threshold_seconds": 5.0,
            "log_slow_queries": True
        },
        
        "tracing": {
            "enabled": True,
            "sample_rate": 0.1,  # 10% of requests
            "exporters": [
                {
                    "type": "jaeger",
                    "endpoint": "http://localhost:14268/api/traces"
                }
            ]
        },
        
        "dashboards": {
            "grafana": {
                "enabled": True,
                "dashboards": [
                    "overview",
                    "performance",
                    "errors",
                    "korean_processing",
                    "resources"
                ]
            }
        }
    }
    
    return config


def create_production_runbook() -> Dict[str, Any]:
    """Create production runbook for common issues"""
    
    runbook = {
        "alerts": {
            "high_response_time": {
                "description": "Application response time is above threshold",
                "possible_causes": [
                    "High load/traffic",
                    "Slow converters (PDF, large files)",
                    "Memory pressure causing GC",
                    "Network issues",
                    "Korean NLP processing bottleneck"
                ],
                "investigation_steps": [
                    "Check current traffic levels",
                    "Identify slow endpoints in metrics",
                    "Check memory and CPU usage",
                    "Review recent deployments",
                    "Check converter-specific metrics"
                ],
                "remediation": [
                    "Scale horizontally if load-related",
                    "Optimize slow converters",
                    "Increase memory if GC-related",
                    "Enable caching for repeated conversions",
                    "Disable non-essential features (e.g., Korean NLP) temporarily"
                ]
            },
            
            "high_error_rate": {
                "description": "Error rate is above acceptable threshold",
                "possible_causes": [
                    "Bad deployment",
                    "External service failures",
                    "Malformed input surge",
                    "Encoding issues with Korean text",
                    "Resource exhaustion"
                ],
                "investigation_steps": [
                    "Check error logs for patterns",
                    "Identify error types and frequencies",
                    "Check external service health",
                    "Review recent changes",
                    "Analyze input patterns"
                ],
                "remediation": [
                    "Rollback if deployment-related",
                    "Implement circuit breakers for external services",
                    "Add input validation",
                    "Fix encoding detection for Korean text",
                    "Scale resources if needed"
                ]
            },
            
            "korean_nlp_failure": {
                "description": "Korean NLP processing is unavailable",
                "possible_causes": [
                    "Missing Java dependencies (for KoNLPy)",
                    "Corrupted model files",
                    "Memory issues",
                    "Library version conflicts"
                ],
                "investigation_steps": [
                    "Check Java installation and JAVA_HOME",
                    "Verify NLP library installations",
                    "Check available memory",
                    "Review dependency versions"
                ],
                "remediation": [
                    "Reinstall Java dependencies",
                    "Reinstall NLP libraries",
                    "Restart application",
                    "Use fallback text processing",
                    "Disable Korean mode temporarily"
                ]
            },
            
            "memory_leak": {
                "description": "Memory usage continuously increasing",
                "possible_causes": [
                    "File handles not being closed",
                    "Large objects retained in memory",
                    "Korean NLP models not garbage collected",
                    "Circular references in converters"
                ],
                "investigation_steps": [
                    "Generate heap dump",
                    "Check file descriptor count",
                    "Monitor GC activity",
                    "Profile memory allocations"
                ],
                "remediation": [
                    "Fix resource leaks in code",
                    "Implement proper cleanup in converters",
                    "Add periodic GC triggers",
                    "Restart application as temporary fix"
                ]
            }
        },
        
        "maintenance_procedures": {
            "deployment": {
                "pre_deployment": [
                    "Run error recovery test suite",
                    "Verify Korean text processing",
                    "Check resource requirements",
                    "Prepare rollback plan"
                ],
                "deployment": [
                    "Deploy to canary instance first",
                    "Monitor error rates and performance",
                    "Run smoke tests",
                    "Gradually increase traffic"
                ],
                "post_deployment": [
                    "Monitor metrics for 30 minutes",
                    "Check all alert conditions",
                    "Verify Korean processing functionality",
                    "Document any issues"
                ]
            },
            
            "scaling": {
                "horizontal_scaling": [
                    "Add new instances behind load balancer",
                    "Ensure shared storage for temp files",
                    "Distribute Korean NLP load",
                    "Update monitoring to include new instances"
                ],
                "vertical_scaling": [
                    "Increase memory for NLP models",
                    "Adjust JVM heap size if using Java-based NLP",
                    "Update resource alerts thresholds",
                    "Test with production-like load"
                ]
            }
        },
        
        "emergency_procedures": {
            "service_degradation": [
                "Enable circuit breakers",
                "Disable non-essential features",
                "Increase cache TTL",
                "Reduce concurrent request limits",
                "Switch to basic text extraction only"
            ],
            
            "data_corruption": [
                "Stop writes immediately",
                "Identify corruption scope",
                "Restore from backups if needed",
                "Validate data integrity",
                "Re-process affected conversions"
            ]
        }
    }
    
    return runbook


def generate_monitoring_setup_script() -> str:
    """Generate script to set up monitoring"""
    
    script = """#!/bin/bash
# VoidLight MarkItDown - Production Monitoring Setup Script

set -e

echo "Setting up monitoring for VoidLight MarkItDown..."

# Create directories
mkdir -p /var/log/voidlight_markitdown
mkdir -p /etc/voidlight_markitdown/monitoring

# Install monitoring dependencies
pip install prometheus-client psutil

# Create Prometheus configuration
cat > /etc/prometheus/voidlight_markitdown.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'voidlight_markitdown'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
EOF

# Create Grafana dashboards
mkdir -p /var/lib/grafana/dashboards

# Create systemd service for metrics exporter
cat > /etc/systemd/system/voidlight-metrics.service << EOF
[Unit]
Description=VoidLight MarkItDown Metrics Exporter
After=network.target

[Service]
Type=simple
User=voidlight
ExecStart=/usr/local/bin/voidlight-metrics-exporter
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create alert rules for Alertmanager
cat > /etc/alertmanager/voidlight_rules.yml << EOF
groups:
  - name: voidlight_markitdown
    interval: 30s
    rules:
      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High response time detected
          
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected
EOF

# Enable and start services
systemctl daemon-reload
systemctl enable voidlight-metrics.service
systemctl start voidlight-metrics.service

# Setup log rotation
cat > /etc/logrotate.d/voidlight_markitdown << EOF
/var/log/voidlight_markitdown/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 voidlight voidlight
    sharedscripts
    postrotate
        systemctl reload voidlight-markitdown
    endscript
}
EOF

echo "Monitoring setup complete!"
echo "Access points:"
echo "  - Metrics: http://localhost:9090/metrics"
echo "  - Health: http://localhost:8080/health"
echo "  - Grafana: http://localhost:3000"
"""
    
    return script


# Example monitoring integration
class MonitoringMiddleware:
    """Middleware to collect metrics from VoidLight MarkItDown"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.active_requests = 0
        self.lock = threading.Lock()
        
    def process_request(self, request_info: Dict[str, Any]):
        """Process incoming request"""
        with self.lock:
            self.active_requests += 1
            
        # Record metric
        self.metrics.record_metric(Metric(
            name="concurrent_requests",
            value=self.active_requests,
            timestamp=datetime.now(),
            metric_type=MetricType.GAUGE
        ))
        
        # Record request
        self.metrics.record_metric(Metric(
            name="http_requests_total",
            value=1,
            timestamp=datetime.now(),
            labels={
                "method": request_info.get("method", "unknown"),
                "endpoint": request_info.get("endpoint", "unknown")
            },
            metric_type=MetricType.COUNTER
        ))
        
    def process_response(self, response_info: Dict[str, Any]):
        """Process outgoing response"""
        with self.lock:
            self.active_requests -= 1
            
        # Record response time
        if "duration" in response_info:
            self.metrics.record_metric(Metric(
                name="http_request_duration_seconds",
                value=response_info["duration"],
                timestamp=datetime.now(),
                labels={
                    "method": response_info.get("method", "unknown"),
                    "endpoint": response_info.get("endpoint", "unknown")
                },
                metric_type=MetricType.HISTOGRAM
            ))
            
        # Record errors
        if response_info.get("status", 200) >= 400:
            self.metrics.record_metric(Metric(
                name="errors_total",
                value=1,
                timestamp=datetime.now(),
                labels={
                    "type": "http_error",
                    "severity": "error" if response_info.get("status", 500) >= 500 else "warning"
                },
                metric_type=MetricType.COUNTER
            ))


def main():
    """Generate monitoring configuration files"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate monitoring configuration")
    parser.add_argument("--output-dir", default="monitoring", help="Output directory")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Generate configurations
    config = create_production_monitoring_config()
    with open(output_dir / "monitoring_config.json", 'w') as f:
        json.dump(config, f, indent=2)
        
    runbook = create_production_runbook()
    with open(output_dir / "runbook.json", 'w') as f:
        json.dump(runbook, f, indent=2)
        
    setup_script = generate_monitoring_setup_script()
    script_path = output_dir / "setup_monitoring.sh"
    with open(script_path, 'w') as f:
        f.write(setup_script)
    script_path.chmod(0o755)
    
    print(f"Monitoring configuration generated in {output_dir}")
    print("Files created:")
    print(f"  - monitoring_config.json")
    print(f"  - runbook.json")
    print(f"  - setup_monitoring.sh")


if __name__ == "__main__":
    main()