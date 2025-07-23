# VoidLight MarkItDown Logging System

This document describes the comprehensive logging system implemented in VoidLight MarkItDown, providing debugging, monitoring, and performance tracking capabilities.

## Features

- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Flexible Output**: Console and/or file logging with rotation
- **Structured Logging**: JSON format for machine-readable logs
- **Performance Metrics**: Automatic timing and resource tracking
- **Configuration Options**: Environment variables, config files, or programmatic
- **Component-Specific Logging**: Separate loggers for different modules
- **Production-Ready**: Log rotation, size limits, and backup management

## Quick Start

### Basic Usage

```python
from voidlight_markitdown import VoidLightMarkItDown

# Logging is automatically configured with sensible defaults
converter = VoidLightMarkItDown()
result = converter.convert("file.pdf")
```

### Setting Log Level

```bash
# Via environment variable
export VOIDLIGHT_LOG_LEVEL=DEBUG

# Via CLI tool
python -m voidlight_markitdown.cli_logging --level DEBUG
```

### Enabling File Logging

```bash
# Via environment variable
export VOIDLIGHT_LOG_FILE=/var/log/voidlight.log

# Via CLI tool
python -m voidlight_markitdown.cli_logging --file /var/log/voidlight.log
```

## Configuration Methods

### 1. Environment Variables

- `VOIDLIGHT_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `VOIDLIGHT_LOG_FILE`: Path to log file
- `VOIDLIGHT_LOG_STRUCTURED`: Enable JSON structured logging (true/false)
- `VOIDLIGHT_LOG_CONSOLE`: Enable console output (true/false)
- `VOIDLIGHT_LOG_DETAILED`: Use detailed format with file/line info (true/false)
- `VOIDLIGHT_LOG_CONFIG`: Path to configuration file

### 2. Configuration Files

#### YAML Configuration (logging.yaml)

```yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: voidlight_markitdown.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  voidlight_markitdown:
    level: INFO
    handlers: [console, file]
```

#### JSON Configuration (logging.json)

```json
{
  "version": 1,
  "formatters": {
    "default": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "default"
    }
  },
  "loggers": {
    "voidlight_markitdown": {
      "level": "INFO",
      "handlers": ["console"]
    }
  }
}
```

### 3. Programmatic Configuration

```python
from voidlight_markitdown._logging import setup_logging

# Configure logging programmatically
setup_logging(
    level="DEBUG",
    log_file="/var/log/voidlight.log",
    structured=True,
    console=True,
    detailed=True,
    max_bytes=10*1024*1024,  # 10MB
    backup_count=5
)
```

## Logger Hierarchy

The logging system uses a hierarchical structure:

- `voidlight_markitdown` - Root logger for the library
  - `voidlight_markitdown.converters` - Converter-specific logging
    - `voidlight_markitdown.converters.pdf` - PDF converter logs
    - `voidlight_markitdown.converters.docx` - DOCX converter logs
    - etc.
  - `voidlight_markitdown.korean` - Korean text processing logs
  - `voidlight_markitdown.performance` - Performance metrics
  - `voidlight_markitdown.mcp` - MCP server logs

## Performance Logging

The system automatically tracks performance metrics:

```python
# Performance metrics are logged automatically
converter.convert("large_file.pdf")
# Logs: "Completed convert_pdf in 2.341s"
```

### Performance Log Format

```
2024-01-20 10:30:45 - voidlight_markitdown.performance.converter.pdf - PERF - Completed convert_pdf in 2.341s
```

### Accessing Performance Logs

```python
from voidlight_markitdown._logging import get_performance_logger

perf_logger = get_performance_logger("custom_operation")
with log_performance(perf_logger, "process_batch", batch_size=100):
    # Your code here
    pass
```

## Structured Logging

Enable JSON structured logging for machine-readable logs:

```python
setup_logging(structured=True)
```

### Structured Log Format

```json
{
  "timestamp": "2024-01-20T10:30:45.123456",
  "level": "INFO",
  "logger": "voidlight_markitdown",
  "message": "Successfully converted with PdfConverter",
  "module": "_voidlight_markitdown",
  "function": "convert",
  "line": 645,
  "converter": "PdfConverter",
  "result_size": 12345,
  "duration_seconds": 2.341
}
```

## Log Rotation

File logs are automatically rotated:

- Default max size: 10MB per file
- Default backup count: 5 files
- Files are named: `logfile.log`, `logfile.log.1`, `logfile.log.2`, etc.

## Debugging Tips

### 1. Enable Debug Logging

```bash
export VOIDLIGHT_LOG_LEVEL=DEBUG
export VOIDLIGHT_LOG_DETAILED=true
```

### 2. Trace Converter Selection

Debug logs show which converters are tried:

```
DEBUG - Attempting conversion with PdfConverter
DEBUG - PdfConverter.accepts() returned True
INFO - Successfully converted with PdfConverter
```

### 3. Monitor Korean Processing

```bash
export VOIDLIGHT_LOG_LEVEL=DEBUG
# Watch Korean text normalization and processing
```

### 4. Track Performance Issues

```bash
# Check performance log for slow operations
grep "PERF" voidlight_markitdown_performance.log | grep -E "in [0-9]+\."
```

## MCP Server Logging

The MCP server has additional logging:

```bash
# Start MCP server with debug logging
VOIDLIGHT_LOG_LEVEL=DEBUG python -m voidlight_markitdown_mcp --http
```

MCP server logs include:
- Request/response tracking
- Conversion metrics
- Error details with stack traces

## Production Deployment

### Recommended Settings

```bash
# Production environment variables
export VOIDLIGHT_LOG_LEVEL=INFO
export VOIDLIGHT_LOG_FILE=/var/log/voidlight/markitdown.log
export VOIDLIGHT_LOG_STRUCTURED=true
export VOIDLIGHT_LOG_CONSOLE=false
```

### Log Aggregation

Structured logs can be easily ingested by log aggregation systems:

- Elasticsearch/Logstash
- Splunk
- CloudWatch Logs
- Datadog

### Monitoring Integration

Use performance logs for monitoring:

```python
# Extract metrics from logs
import json

with open('voidlight_markitdown.log') as f:
    for line in f:
        if '"duration_seconds"' in line:
            data = json.loads(line)
            print(f"Operation: {data['message']}, Duration: {data['duration_seconds']}s")
```

## Troubleshooting

### No Logs Appearing

1. Check log level: `echo $VOIDLIGHT_LOG_LEVEL`
2. Verify file permissions for log file
3. Ensure console logging is enabled

### Too Many Logs

1. Increase log level: `export VOIDLIGHT_LOG_LEVEL=WARNING`
2. Disable detailed format: `export VOIDLIGHT_LOG_DETAILED=false`
3. Filter specific loggers in config file

### Performance Impact

- Structured logging has minimal overhead
- File I/O is buffered
- Consider async handlers for high-throughput scenarios

## Examples

See `examples/logging_demo.py` for comprehensive examples:

```bash
python examples/logging_demo.py
```

This demonstrates:
- Basic logging configuration
- Debug logging with Korean text
- Performance tracking
- Structured logging
- Error logging

## CLI Tool

Use the CLI tool for quick configuration:

```bash
# Show current configuration
python -m voidlight_markitdown.cli_logging --show-config

# Set up debug logging to file
python -m voidlight_markitdown.cli_logging --level DEBUG --file debug.log --detailed

# Export as environment variables
python -m voidlight_markitdown.cli_logging --export-env --level INFO --structured
```