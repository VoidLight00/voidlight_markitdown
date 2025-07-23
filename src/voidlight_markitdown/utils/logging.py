"""
Logging configuration and utilities for VoidLight MarkItDown.

This module provides:
- Centralized logging configuration
- Performance metrics logging
- Structured logging support
- Log level management
- File and console logging handlers
"""

import logging
import logging.config
import logging.handlers
import json
import time
import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime
from contextlib import contextmanager
import functools


# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"

# Performance log format
PERFORMANCE_FORMAT = "%(asctime)s - %(name)s - PERF - %(message)s"


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter for machine-readable logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "pathname", "process", "processName", "relativeCreated",
                          "thread", "threadName", "exc_info", "exc_text", "stack_info"]:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


class PerformanceLogger:
    """Context manager for performance logging."""
    
    def __init__(self, logger: logging.Logger, operation: str, **extra):
        self.logger = logger
        self.operation = operation
        self.extra = extra
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting {self.operation}", extra=self.extra)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        extra = {**self.extra, "duration_seconds": duration}
        
        if exc_type:
            self.logger.error(
                f"Failed {self.operation} after {duration:.3f}s: {exc_val}",
                extra=extra,
                exc_info=True
            )
        else:
            self.logger.info(
                f"Completed {self.operation} in {duration:.3f}s",
                extra=extra
            )


def get_log_level(level: Union[str, int, None] = None) -> int:
    """Get log level from string, int, or environment variable."""
    if level is None:
        level = os.getenv("VOIDLIGHT_LOG_LEVEL", "INFO")
    
    if isinstance(level, str):
        return getattr(logging, level.upper(), logging.INFO)
    elif isinstance(level, int):
        return level
    else:
        return logging.INFO


# Keep track of whether logging has been configured
_logging_configured = False


def setup_logging(
    level: Union[str, int, None] = None,
    log_file: Optional[Union[str, Path]] = None,
    structured: bool = False,
    console: bool = True,
    detailed: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    config_file: Optional[Union[str, Path]] = None,
) -> None:
    """
    Setup logging configuration for VoidLight MarkItDown.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        structured: Use structured JSON logging
        console: Enable console logging
        detailed: Use detailed format with file/line info
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        config_file: Path to logging configuration file (overrides other settings)
    """
    global _logging_configured
    
    # Skip if already configured (unless explicitly reconfiguring)
    if _logging_configured and config_file is None:
        return
    
    # If config file is provided, use it
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            if config_path.suffix == ".json":
                with open(config_path) as f:
                    config = json.load(f)
                logging.config.dictConfig(config)
            else:
                logging.config.fileConfig(config_path)
            return
    
    # Build configuration dictionary
    handlers = {}
    handler_list = []
    
    # Console handler
    if console:
        console_handler = {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        }
        
        if structured:
            console_handler["formatter"] = "structured"
        elif detailed:
            console_handler["formatter"] = "detailed"
        else:
            console_handler["formatter"] = "default"
        
        handlers["console"] = console_handler
        handler_list.append("console")
    
    # File handler
    if log_file:
        file_handler = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": str(log_file),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
            "encoding": "utf-8",
        }
        
        if structured:
            file_handler["formatter"] = "structured"
        elif detailed:
            file_handler["formatter"] = "detailed"
        else:
            file_handler["formatter"] = "default"
        
        handlers["file"] = file_handler
        handler_list.append("file")
    
    # Formatters
    formatters = {
        "default": {
            "format": DEFAULT_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": DETAILED_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "performance": {
            "format": PERFORMANCE_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "structured": {
            "()": StructuredFormatter
        }
    }
    
    # Build config
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": {
            "voidlight_markitdown": {
                "level": get_log_level(level),
                "handlers": handler_list,
                "propagate": False
            },
            "voidlight_markitdown.performance": {
                "level": "INFO",
                "handlers": handler_list,
                "propagate": False
            }
        },
        "root": {
            "level": get_log_level(level),
            "handlers": handler_list
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(config)
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    # Ensure logging is configured with defaults if not already done
    if not _logging_configured:
        setup_logging()
    return logging.getLogger(name)


def get_performance_logger(name: str) -> logging.Logger:
    """Get a performance logger instance."""
    # Ensure logging is configured with defaults if not already done
    if not _logging_configured:
        setup_logging()
    return logging.getLogger(f"voidlight_markitdown.performance.{name}")


@contextmanager
def log_performance(logger: logging.Logger, operation: str, **extra):
    """
    Context manager for logging performance metrics.
    
    Usage:
        with log_performance(logger, "convert_pdf", file_size=1024):
            # Do work here
            pass
    """
    with PerformanceLogger(logger, operation, **extra):
        yield


def log_converter_metrics(converter_name: str):
    """
    Decorator for logging converter performance metrics.
    
    Usage:
        @log_converter_metrics("pdf")
        def convert(self, file_stream, stream_info, **kwargs):
            # Converter implementation
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, file_stream: Any, stream_info: Any, **kwargs):
            logger = get_performance_logger(f"converter.{converter_name}")
            
            # Get file size if possible
            extra = {"converter": converter_name}
            try:
                current_pos = file_stream.tell()
                file_stream.seek(0, 2)  # Seek to end
                extra["file_size_bytes"] = file_stream.tell()
                file_stream.seek(current_pos)  # Restore position
            except:
                pass
            
            # Add stream info
            if stream_info:
                if stream_info.mimetype:
                    extra["mimetype"] = stream_info.mimetype
                if stream_info.extension:
                    extra["extension"] = stream_info.extension
                if stream_info.filename:
                    extra["filename"] = stream_info.filename
            
            with log_performance(logger, f"convert_{converter_name}", **extra):
                result = func(self, file_stream, stream_info, **kwargs)
                
                # Log result metrics
                if result and hasattr(result, "markdown"):
                    logger.info(
                        f"Conversion result size: {len(result.markdown)} characters",
                        extra={**extra, "result_size": len(result.markdown)}
                    )
                
                return result
        
        return wrapper
    return decorator


class LoggingMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            # Ensure logging is configured
            if not _logging_configured:
                setup_logging()
            self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        return self._logger
    
    def log_debug(self, message: str, **extra):
        """Log debug message."""
        self.logger.debug(message, extra=extra)
    
    def log_info(self, message: str, **extra):
        """Log info message."""
        self.logger.info(message, extra=extra)
    
    def log_warning(self, message: str, **extra):
        """Log warning message."""
        self.logger.warning(message, extra=extra)
    
    def log_error(self, message: str, exc_info: bool = False, **extra):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def log_critical(self, message: str, exc_info: bool = False, **extra):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info, extra=extra)


# Don't initialize logging automatically to avoid circular imports
# Users should call setup_logging() explicitly or it will be initialized
# on first use with default settings


# Alias for backward compatibility
def set_log_level(level: Union[str, int]):
    """Set the log level for all voidlight_markitdown loggers."""
    log_level = get_log_level(level)
    logging.getLogger("voidlight_markitdown").setLevel(log_level)
    logging.getLogger("voidlight_markitdown.performance").setLevel(log_level)