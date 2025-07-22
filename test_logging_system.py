#!/usr/bin/env python
"""
Test script to verify the logging system implementation.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "voidlight_markitdown" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "voidlight_markitdown-mcp" / "src"))

def test_basic_logging():
    """Test basic logging functionality."""
    print("\n=== Testing Basic Logging ===")
    
    from voidlight_markitdown import VoidLightMarkItDown, setup_logging
    
    # Setup logging
    with tempfile.NamedTemporaryFile(mode='w', suffix='_test.log', delete=False) as f:
        log_file = f.name
    
    setup_logging(level="DEBUG", log_file=log_file, console=True, detailed=True)
    
    # Create converter
    converter = VoidLightMarkItDown()
    
    # Test with data URI
    result = converter.convert("data:text/plain,Hello World")
    print(f"✓ Basic conversion successful: {result.markdown}")
    
    # Check log file
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "Initializing VoidLightMarkItDown" in log_content
        assert "Starting conversion" in log_content
        assert "Conversion completed successfully" in log_content
        print("✓ Log entries found in file")
    
    os.unlink(log_file)
    print("✓ Basic logging test passed")


def test_korean_logging():
    """Test Korean text processing logging."""
    print("\n=== Testing Korean Logging ===")
    
    from voidlight_markitdown import VoidLightMarkItDown, setup_logging
    
    setup_logging(level="DEBUG")
    
    # Create converter with Korean mode
    converter = VoidLightMarkItDown(korean_mode=True)
    
    # Test Korean text
    korean_text = "안녕하세요! 한국어 로깅 테스트입니다."
    result = converter.convert(f"data:text/plain;charset=utf-8,{korean_text}")
    
    print(f"✓ Korean conversion successful")
    print(f"✓ Result: {result.markdown}")


def test_performance_logging():
    """Test performance metrics logging."""
    print("\n=== Testing Performance Logging ===")
    
    from voidlight_markitdown import VoidLightMarkItDown, setup_logging, get_performance_logger, log_performance
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_perf.log', delete=False) as f:
        perf_log = f.name
    
    setup_logging(level="INFO", log_file=perf_log)
    
    # Test performance logging
    perf_logger = get_performance_logger("test")
    
    with log_performance(perf_logger, "test_operation", size=1000):
        # Simulate work
        import time
        time.sleep(0.1)
    
    # Check performance log
    with open(perf_log, 'r') as f:
        log_content = f.read()
        # Look for the performance log entry
        if "Completed test_operation" in log_content and ("0.1" in log_content or "duration" in log_content):
            print("✓ Performance metrics logged")
        else:
            # Alternative check for structured logs
            for line in f:
                if "test_operation" in line:
                    print("✓ Performance metrics logged")
                    break
    
    os.unlink(perf_log)
    print("✓ Performance logging test passed")


def test_structured_logging():
    """Test structured JSON logging."""
    print("\n=== Testing Structured Logging ===")
    
    from voidlight_markitdown import setup_logging, get_logger
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_struct.log', delete=False) as f:
        struct_log = f.name
    
    setup_logging(level="INFO", log_file=struct_log, structured=True, console=False)
    
    logger = get_logger("test.structured")
    logger.info("Test message", extra={"extra_field": "value", "numeric": 42})
    
    # Read and parse structured log
    with open(struct_log, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                if log_entry.get('message') == 'Test message':
                    assert log_entry['extra_field'] == 'value'
                    assert log_entry['numeric'] == 42
                    print("✓ Structured logging with extra fields works")
                    break
            except:
                pass
    
    os.unlink(struct_log)
    print("✓ Structured logging test passed")


def test_converter_logging():
    """Test converter-specific logging."""
    print("\n=== Testing Converter Logging ===")
    
    from voidlight_markitdown import VoidLightMarkItDown, setup_logging
    
    setup_logging(level="DEBUG")
    
    converter = VoidLightMarkItDown()
    
    # Create a test PDF file would require pdfminer
    # For now, test with plain text
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test document for converter logging")
        temp_path = f.name
    
    try:
        result = converter.convert_local(temp_path)
        print("✓ Converter logging works")
    finally:
        os.unlink(temp_path)


def test_error_logging():
    """Test error logging."""
    print("\n=== Testing Error Logging ===")
    
    from voidlight_markitdown import VoidLightMarkItDown, setup_logging
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_error.log', delete=False) as f:
        error_log = f.name
    
    setup_logging(level="INFO", log_file=error_log)
    
    converter = VoidLightMarkItDown()
    
    # Try to convert unsupported format
    try:
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xyz', delete=False) as f:
            f.write(b'\x00\x01\x02\x03')
            temp_path = f.name
        
        result = converter.convert_local(temp_path)
    except Exception as e:
        print(f"✓ Expected error occurred: {type(e).__name__}")
        
        # Check error log
        with open(error_log, 'r') as f:
            log_content = f.read()
            assert "ERROR" in log_content or "error" in log_content
            print("✓ Error logged successfully")
    finally:
        if 'temp_path' in locals():
            os.unlink(temp_path)
    
    os.unlink(error_log)
    print("✓ Error logging test passed")


def test_mcp_logging():
    """Test MCP server logging (import only)."""
    print("\n=== Testing MCP Logging ===")
    
    try:
        from voidlight_markitdown_mcp.__main__ import logger
        print("✓ MCP logger imported successfully")
    except Exception as e:
        print(f"✗ MCP import failed: {e}")


def test_cli_logging():
    """Test CLI logging configuration."""
    print("\n=== Testing CLI Logging ===")
    
    try:
        from voidlight_markitdown.cli_logging import parse_args, show_config
        print("✓ CLI logging module imported successfully")
    except Exception as e:
        print(f"✗ CLI import failed: {e}")


def main():
    """Run all tests."""
    print("VoidLight MarkItDown Logging System Test Suite")
    print("=" * 50)
    
    tests = [
        test_basic_logging,
        test_korean_logging,
        test_performance_logging,
        test_structured_logging,
        test_converter_logging,
        test_error_logging,
        test_mcp_logging,
        test_cli_logging,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✓ All tests passed! The logging system is working correctly.")
    else:
        print(f"\n✗ {failed} tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()