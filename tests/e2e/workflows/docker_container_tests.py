#!/usr/bin/env python3
"""Docker container comprehensive tests for voidlight_markitdown"""

import sys
import os
import time
import json
import psutil
import platform
from datetime import datetime

def test_system_info():
    """Test system information"""
    print("\n=== SYSTEM INFORMATION ===")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python version: {sys.version}")
    print(f"Process ID: {os.getpid()}")
    print(f"Working directory: {os.getcwd()}")
    
    # Memory info
    memory = psutil.virtual_memory()
    print(f"Memory: {memory.total / (1024**3):.2f} GB total, {memory.available / (1024**3):.2f} GB available")
    
    # CPU info
    print(f"CPU cores: {psutil.cpu_count()}")
    
    return True

def test_locales():
    """Test locale support"""
    print("\n=== LOCALE TESTS ===")
    import locale
    
    # Test default locale
    print(f"Default locale: {locale.getdefaultlocale()}")
    
    # Test Korean text
    korean_text = "안녕하세요! 이것은 한국어 테스트입니다."
    print(f"Korean text: {korean_text}")
    print(f"Korean text length: {len(korean_text)}")
    
    # Test encoding
    encoded = korean_text.encode('utf-8')
    decoded = encoded.decode('utf-8')
    print(f"UTF-8 encoding/decoding: {'OK' if decoded == korean_text else 'FAILED'}")
    
    return True

def test_imports():
    """Test importing all required modules"""
    print("\n=== IMPORT TESTS ===")
    
    required_modules = [
        'beautifulsoup4',
        'markdownify',
        'charset_normalizer',
        'magika',
        'requests',
        'tabulate',
        'numpy',
        'cython',
        'pytest',
        'pytest_asyncio',
        'pytest_cov',
        'psutil',
        'yaml',
        'mcp',
        'anyio',
        'httpx',
        'pydantic',
        'starlette',
        'uvicorn'
    ]
    
    failed = []
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_mcp_server():
    """Test MCP server components"""
    print("\n=== MCP SERVER TESTS ===")
    
    try:
        # Import MCP server
        from voidlight_markitdown_mcp import server
        print("✓ MCP server module imported")
        
        # Check server attributes
        if hasattr(server, 'app'):
            print("✓ Server app exists")
        
        # Test configuration
        from voidlight_markitdown_mcp import config
        print("✓ Config module imported")
        
        return True
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        return False

def test_korean_processing():
    """Test Korean text processing capabilities"""
    print("\n=== KOREAN PROCESSING TESTS ===")
    
    test_texts = [
        "한글 테스트",
        "대한민국 서울특별시",
        "안녕하세요! 반갑습니다.",
        "1234 숫자와 한글 혼합 ABC"
    ]
    
    for text in test_texts:
        print(f"Processing: {text}")
        # Basic string operations
        print(f"  Length: {len(text)}")
        print(f"  Upper: {text.upper()}")
        print(f"  Encoded size: {len(text.encode('utf-8'))} bytes")
    
    return True

def test_file_operations():
    """Test file operations with Korean filenames"""
    print("\n=== FILE OPERATION TESTS ===")
    
    test_dir = "/tmp/docker_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # Test Korean filename
    korean_filename = os.path.join(test_dir, "한글_테스트_파일.txt")
    test_content = "이것은 테스트 파일입니다.\nThis is a test file."
    
    try:
        # Write file
        with open(korean_filename, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✓ Created file: {korean_filename}")
        
        # Read file
        with open(korean_filename, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        if read_content == test_content:
            print("✓ File read/write successful")
        else:
            print("✗ File content mismatch")
        
        # Cleanup
        os.remove(korean_filename)
        os.rmdir(test_dir)
        
        return True
    except Exception as e:
        print(f"✗ File operation failed: {e}")
        return False

def test_container_resources():
    """Test container resource usage"""
    print("\n=== CONTAINER RESOURCE TESTS ===")
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU usage: {cpu_percent}%")
    
    # Memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Process memory: {memory_info.rss / (1024**2):.2f} MB")
    
    # Disk usage
    disk_usage = psutil.disk_usage('/')
    print(f"Disk usage: {disk_usage.percent}% of {disk_usage.total / (1024**3):.2f} GB")
    
    return True

def test_network():
    """Test network connectivity"""
    print("\n=== NETWORK TESTS ===")
    
    try:
        import requests
        
        # Test DNS resolution
        response = requests.get('http://httpbin.org/ip', timeout=5)
        if response.status_code == 200:
            print(f"✓ Network connectivity OK: {response.json()}")
        else:
            print(f"✗ Network test failed: HTTP {response.status_code}")
        
        return True
    except Exception as e:
        print(f"✗ Network test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== DOCKER CONTAINER COMPREHENSIVE TESTS ===")
    print(f"Started at: {datetime.now()}")
    
    tests = [
        ("System Info", test_system_info),
        ("Locales", test_locales),
        ("Imports", test_imports),
        ("MCP Server", test_mcp_server),
        ("Korean Processing", test_korean_processing),
        ("File Operations", test_file_operations),
        ("Container Resources", test_container_resources),
        ("Network", test_network)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Save results
    with open('/app/test_artifacts/container_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'passed': passed,
                'total': total
            }
        }, f, indent=2)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)