#!/usr/bin/env python
"""
Demonstration of VoidLight MarkItDown logging capabilities.

This script shows how to:
1. Configure logging programmatically
2. Use different log levels
3. Enable performance logging
4. Use structured logging
"""

import os
import tempfile
from pathlib import Path

# Add parent directory to path for development
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "voidlight_markitdown" / "src"))

from voidlight_markitdown import VoidLightMarkItDown
from voidlight_markitdown._logging import setup_logging, get_logger


def demo_basic_logging():
    """Demonstrate basic logging functionality."""
    print("\n=== Basic Logging Demo ===")
    
    # Setup logging with INFO level
    setup_logging(level="INFO", detailed=False)
    
    # Create converter and convert a simple text
    converter = VoidLightMarkItDown()
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello, this is a test document for logging demonstration.")
        temp_path = f.name
    
    try:
        # Convert the file
        result = converter.convert_local(temp_path)
        print(f"Conversion successful! Result length: {len(result.markdown)}")
    finally:
        os.unlink(temp_path)


def demo_debug_logging():
    """Demonstrate debug logging with detailed information."""
    print("\n=== Debug Logging Demo ===")
    
    # Setup logging with DEBUG level and detailed format
    setup_logging(level="DEBUG", detailed=True)
    
    # Create converter with Korean mode
    converter = VoidLightMarkItDown(korean_mode=True)
    
    # Convert a data URI
    data_uri = "data:text/plain;charset=utf-8,안녕하세요! 한국어 테스트입니다."
    result = converter.convert_uri(data_uri)
    print(f"Korean text conversion successful! Result: {result.markdown[:50]}...")


def demo_performance_logging():
    """Demonstrate performance logging."""
    print("\n=== Performance Logging Demo ===")
    
    # Setup logging for performance metrics
    with tempfile.NamedTemporaryFile(mode='w', suffix='_perf.log', delete=False) as f:
        perf_log = f.name
    
    setup_logging(
        level="INFO",
        log_file=perf_log,
        console=True
    )
    
    converter = VoidLightMarkItDown()
    
    # Create a larger test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document.\n" * 1000)
        temp_path = f.name
    
    try:
        # Convert with performance logging
        result = converter.convert_local(temp_path)
        print(f"Large file conversion complete!")
        
        # Show performance log
        print(f"\nPerformance metrics logged to: {perf_log}")
        with open(perf_log, 'r') as f:
            perf_lines = [line for line in f if 'PERF' in line or 'duration' in line]
            if perf_lines:
                print("Sample performance entries:")
                for line in perf_lines[-5:]:
                    print(f"  {line.strip()}")
    finally:
        os.unlink(temp_path)
        # Keep perf log for inspection


def demo_structured_logging():
    """Demonstrate structured JSON logging."""
    print("\n=== Structured Logging Demo ===")
    
    # Setup structured logging
    with tempfile.NamedTemporaryFile(mode='w', suffix='_structured.log', delete=False) as f:
        struct_log = f.name
    
    setup_logging(
        level="INFO",
        log_file=struct_log,
        structured=True,
        console=False  # Disable console to see clean output
    )
    
    # Get a logger
    logger = get_logger("demo")
    
    # Log some structured data
    logger.info(
        "Processing document",
        document_type="test",
        size_bytes=1024,
        encoding="utf-8",
        tags=["demo", "test", "structured"]
    )
    
    # Convert something to generate logs
    converter = VoidLightMarkItDown()
    result = converter.convert("data:text/plain,Structured logging test")
    
    print(f"Structured logs written to: {struct_log}")
    
    # Show sample structured log
    with open(struct_log, 'r') as f:
        import json
        print("\nSample structured log entries:")
        for line in f:
            try:
                log_entry = json.loads(line)
                print(f"  Level: {log_entry['level']}, "
                      f"Logger: {log_entry['logger']}, "
                      f"Message: {log_entry['message']}")
            except:
                pass


def demo_error_logging():
    """Demonstrate error logging."""
    print("\n=== Error Logging Demo ===")
    
    setup_logging(level="INFO")
    
    converter = VoidLightMarkItDown()
    
    # Try to convert an unsupported format
    try:
        # Create a fake binary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xyz', delete=False) as f:
            f.write(b'\x00\x01\x02\x03\x04\x05')
            temp_path = f.name
        
        result = converter.convert_local(temp_path)
    except Exception as e:
        print(f"Expected error occurred: {type(e).__name__}")
        print("Check the logs for detailed error information")
    finally:
        os.unlink(temp_path)


def main():
    """Run all demonstrations."""
    print("VoidLight MarkItDown Logging System Demonstration")
    print("=" * 50)
    
    demos = [
        demo_basic_logging,
        demo_debug_logging,
        demo_performance_logging,
        demo_structured_logging,
        demo_error_logging,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"Demo failed: {e}")
        print()  # Empty line between demos
    
    print("\n" + "=" * 50)
    print("Logging demonstration complete!")
    print("\nTo configure logging for your application:")
    print("1. Set environment variables:")
    print("   export VOIDLIGHT_LOG_LEVEL=DEBUG")
    print("   export VOIDLIGHT_LOG_FILE=/path/to/logfile.log")
    print("2. Or use the CLI tool:")
    print("   python -m voidlight_markitdown.cli_logging --help")
    print("3. Or configure programmatically:")
    print("   from voidlight_markitdown._logging import setup_logging")
    print("   setup_logging(level='DEBUG', log_file='app.log')")


if __name__ == "__main__":
    main()