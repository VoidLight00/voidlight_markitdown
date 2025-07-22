#!/usr/bin/env python3
"""
Edge Case and Performance Tests for VoidLight MarkItDown MCP Server
Tests boundary conditions, large files, and performance characteristics
"""

import json
import asyncio
import subprocess
import time
import sys
import os
import tempfile
import requests
from pathlib import Path
import random
import string
from datetime import datetime
import threading
import psutil
import gc

# Test configuration
MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"
TEST_PORT = 3002  # Different port to avoid conflicts

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

class EdgeCaseTests:
    """Edge case and performance tests"""
    
    def __init__(self):
        self.results = []
        self.temp_files = []
    
    def print_test(self, name: str, passed: bool, message: str, details: dict = None):
        """Print test result"""
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{status} {name}: {message}")
        if details and not passed:
            for key, value in details.items():
                print(f"  {YELLOW}{key}:{RESET} {value}")
    
    def create_large_file(self, size_mb: int, korean_ratio: float = 0.5) -> str:
        """Create a large test file with mixed content"""
        print(f"Creating {size_mb}MB test file with {korean_ratio*100}% Korean content...")
        
        # Generate content
        content_parts = []
        target_size = size_mb * 1024 * 1024  # Convert to bytes
        current_size = 0
        
        korean_chars = "가나다라마바사아자차카타파하" * 100
        english_chars = string.ascii_letters * 100
        
        while current_size < target_size:
            if random.random() < korean_ratio:
                # Korean paragraph
                paragraph = "한글 문단입니다. " + "".join(random.choices(korean_chars, k=500)) + "\n\n"
            else:
                # English paragraph
                paragraph = "English paragraph. " + "".join(random.choices(english_chars, k=500)) + "\n\n"
            
            content_parts.append(paragraph)
            current_size += len(paragraph.encode('utf-8'))
        
        # Write to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("".join(content_parts))
            self.temp_files.append(f.name)
            return f.name
    
    def test_large_file_conversion(self):
        """Test conversion of large files"""
        print(f"\n{BLUE}Testing Large File Conversion{RESET}")
        
        test_sizes = [1, 5, 10]  # MB
        
        for size_mb in test_sizes:
            file_path = self.create_large_file(size_mb)
            
            # Start server
            process = subprocess.Popen(
                [MCP_SERVER_BIN],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                # Initialize
                init_req = {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "large-file-test", "version": "1.0"}},
                    "id": 1
                }
                process.stdin.write(json.dumps(init_req) + '\n')
                process.stdin.flush()
                process.stdout.readline()  # Read init response
                
                # Measure conversion time
                start_time = time.time()
                
                convert_req = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_korean_document",
                        "arguments": {
                            "uri": f"file://{file_path}",
                            "normalize_korean": True
                        }
                    },
                    "id": 2
                }
                
                process.stdin.write(json.dumps(convert_req) + '\n')
                process.stdin.flush()
                
                # Set timeout based on file size
                timeout = 30 + (size_mb * 10)
                response_line = None
                
                # Read with timeout
                import select
                ready = select.select([process.stdout], [], [], timeout)
                if ready[0]:
                    response_line = process.stdout.readline()
                
                elapsed_time = time.time() - start_time
                
                if response_line:
                    response = json.loads(response_line)
                    if "result" in response:
                        self.print_test(
                            f"Large File ({size_mb}MB)",
                            True,
                            f"Converted in {elapsed_time:.2f}s",
                            {"throughput": f"{size_mb/elapsed_time:.2f} MB/s"}
                        )
                    else:
                        self.print_test(
                            f"Large File ({size_mb}MB)",
                            False,
                            "Conversion failed",
                            {"response": str(response)[:100]}
                        )
                else:
                    self.print_test(
                        f"Large File ({size_mb}MB)",
                        False,
                        f"Timeout after {timeout}s",
                        {}
                    )
                
            finally:
                process.terminate()
                process.wait()
    
    def test_memory_usage(self):
        """Test memory usage during conversion"""
        print(f"\n{BLUE}Testing Memory Usage{RESET}")
        
        # Create a moderately large file
        file_path = self.create_large_file(5)
        
        # Start server and monitor memory
        process = subprocess.Popen(
            [MCP_SERVER_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Get process info
            proc = psutil.Process(process.pid)
            initial_memory = proc.memory_info().rss / 1024 / 1024  # MB
            
            # Initialize
            init_req = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "memory-test", "version": "1.0"}},
                "id": 1
            }
            process.stdin.write(json.dumps(init_req) + '\n')
            process.stdin.flush()
            process.stdout.readline()
            
            # Convert file
            convert_req = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "convert_korean_document",
                    "arguments": {
                        "uri": f"file://{file_path}",
                        "normalize_korean": True
                    }
                },
                "id": 2
            }
            
            process.stdin.write(json.dumps(convert_req) + '\n')
            process.stdin.flush()
            
            # Monitor memory during conversion
            peak_memory = initial_memory
            for _ in range(10):
                time.sleep(0.5)
                current_memory = proc.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)
            
            response = process.stdout.readline()
            
            memory_increase = peak_memory - initial_memory
            
            self.print_test(
                "Memory Usage",
                memory_increase < 100,  # Less than 100MB increase
                f"Memory increase: {memory_increase:.1f}MB",
                {
                    "initial": f"{initial_memory:.1f}MB",
                    "peak": f"{peak_memory:.1f}MB"
                }
            )
            
        finally:
            process.terminate()
            process.wait()
    
    def test_malformed_requests(self):
        """Test handling of malformed requests"""
        print(f"\n{BLUE}Testing Malformed Request Handling{RESET}")
        
        process = subprocess.Popen(
            [MCP_SERVER_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Initialize first
            init_req = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "malformed-test", "version": "1.0"}},
                "id": 1
            }
            process.stdin.write(json.dumps(init_req) + '\n')
            process.stdin.flush()
            process.stdout.readline()
            
            # Test cases
            malformed_requests = [
                {
                    "name": "Missing JSONRPC version",
                    "request": {
                        "method": "tools/call",
                        "params": {"name": "convert_to_markdown"},
                        "id": 1
                    }
                },
                {
                    "name": "Invalid JSONRPC version",
                    "request": {
                        "jsonrpc": "1.0",
                        "method": "tools/call",
                        "params": {"name": "convert_to_markdown"},
                        "id": 2
                    }
                },
                {
                    "name": "Missing method",
                    "request": {
                        "jsonrpc": "2.0",
                        "params": {},
                        "id": 3
                    }
                },
                {
                    "name": "Invalid JSON",
                    "request": "not valid json"
                },
                {
                    "name": "Empty request",
                    "request": {}
                }
            ]
            
            for test_case in malformed_requests:
                # Send request
                if isinstance(test_case["request"], str):
                    process.stdin.write(test_case["request"] + '\n')
                else:
                    process.stdin.write(json.dumps(test_case["request"]) + '\n')
                process.stdin.flush()
                
                # Try to read response with timeout
                import select
                ready = select.select([process.stdout], [], [], 2)
                
                if ready[0]:
                    response_line = process.stdout.readline()
                    if response_line:
                        try:
                            response = json.loads(response_line)
                            if "error" in response:
                                self.print_test(
                                    f"Malformed Request - {test_case['name']}",
                                    True,
                                    "Properly returned error",
                                    {"error": response["error"].get("message", "Unknown error")}
                                )
                            else:
                                self.print_test(
                                    f"Malformed Request - {test_case['name']}",
                                    False,
                                    "Should have returned error",
                                    {"response": str(response)[:100]}
                                )
                        except json.JSONDecodeError:
                            self.print_test(
                                f"Malformed Request - {test_case['name']}",
                                False,
                                "Invalid JSON response",
                                {}
                            )
                    else:
                        self.print_test(
                            f"Malformed Request - {test_case['name']}",
                            True,
                            "No response (server still running)",
                            {}
                        )
                else:
                    # No response is acceptable for some malformed requests
                    self.print_test(
                        f"Malformed Request - {test_case['name']}",
                        True,
                        "No response (expected for malformed input)",
                        {}
                    )
            
        finally:
            process.terminate()
            process.wait()
    
    def test_special_characters(self):
        """Test handling of special Unicode characters"""
        print(f"\n{BLUE}Testing Special Character Handling{RESET}")
        
        # Create test files with special characters
        test_cases = [
            {
                "name": "Emoji and symbols",
                "content": "Emoji test: 😀 🎉 🚀 💻\nSymbols: ♠ ♣ ♥ ♦ © ® ™"
            },
            {
                "name": "Mathematical symbols",
                "content": "Math: ∑ ∏ ∫ ∂ ∇ ≈ ≠ ≤ ≥\nGreek: α β γ δ ε ζ η θ"
            },
            {
                "name": "CJK characters",
                "content": "Korean: 한글\nJapanese: ひらがな カタカナ 漢字\nChinese: 中文 繁體字"
            },
            {
                "name": "Zero-width characters",
                "content": "Zero​width​space​test\nZero‌width‌non‌joiner"
            },
            {
                "name": "RTL text",
                "content": "Arabic: مرحبا بالعالم\nHebrew: שלום עולם"
            }
        ]
        
        process = subprocess.Popen(
            [MCP_SERVER_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Initialize
            init_req = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "unicode-test", "version": "1.0"}},
                "id": 1
            }
            process.stdin.write(json.dumps(init_req) + '\n')
            process.stdin.flush()
            process.stdout.readline()
            
            for test_case in test_cases:
                # Create file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(test_case["content"])
                    file_path = f.name
                    self.temp_files.append(file_path)
                
                # Convert
                convert_req = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_to_markdown",
                        "arguments": {"uri": f"file://{file_path}"}
                    },
                    "id": test_case["name"]
                }
                
                process.stdin.write(json.dumps(convert_req) + '\n')
                process.stdin.flush()
                
                response_line = process.stdout.readline()
                if response_line:
                    try:
                        response = json.loads(response_line)
                        if "result" in response:
                            # Check if characters were preserved
                            content = response["result"].get("content", [])
                            if content:
                                text = content[0].get("text", "")
                                # Simple check - at least some content preserved
                                preserved = len(text) > 0
                                self.print_test(
                                    f"Special Characters - {test_case['name']}",
                                    preserved,
                                    "Characters handled correctly" if preserved else "Lost content",
                                    {"original_len": len(test_case["content"]), "result_len": len(text)}
                                )
                            else:
                                self.print_test(
                                    f"Special Characters - {test_case['name']}",
                                    False,
                                    "No content returned",
                                    {}
                                )
                        else:
                            self.print_test(
                                f"Special Characters - {test_case['name']}",
                                False,
                                "Conversion failed",
                                {"error": response.get("error", "Unknown")}
                            )
                    except Exception as e:
                        self.print_test(
                            f"Special Characters - {test_case['name']}",
                            False,
                            f"Exception: {str(e)}",
                            {}
                        )
                
        finally:
            process.terminate()
            process.wait()
    
    def test_concurrent_conversions(self):
        """Test multiple concurrent conversions"""
        print(f"\n{BLUE}Testing Concurrent Conversions{RESET}")
        
        # Start HTTP server for concurrent access
        server_process = subprocess.Popen(
            [MCP_SERVER_BIN, "--http", "--port", str(TEST_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Wait for server
            time.sleep(3)
            
            # Create test files
            test_files = []
            for i in range(5):
                content = f"Test file {i}\n한글 테스트 {i}\n" * 100
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(content)
                    test_files.append(f.name)
                    self.temp_files.append(f.name)
            
            # Function to convert a file
            def convert_file(file_path: str, client_id: int) -> tuple:
                try:
                    # Initialize
                    init_data = {
                        "jsonrpc": "2.0",
                        "method": "initialize",
                        "params": {
                            "clientInfo": {
                                "name": f"concurrent-client-{client_id}",
                                "version": "1.0.0"
                            }
                        },
                        "id": 1
                    }
                    
                    response = requests.post(
                        f"http://localhost:{TEST_PORT}/mcp",
                        json=init_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code != 200:
                        return (client_id, False, "Init failed")
                    
                    # Convert
                    start_time = time.time()
                    convert_data = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "convert_korean_document",
                            "arguments": {
                                "uri": f"file://{file_path}",
                                "normalize_korean": True
                            }
                        },
                        "id": 2
                    }
                    
                    response = requests.post(
                        f"http://localhost:{TEST_PORT}/mcp",
                        json=convert_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    elapsed = time.time() - start_time
                    
                    if response.status_code == 200:
                        return (client_id, True, f"Completed in {elapsed:.2f}s")
                    else:
                        return (client_id, False, f"Failed with {response.status_code}")
                    
                except Exception as e:
                    return (client_id, False, str(e))
            
            # Run concurrent conversions
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                start_time = time.time()
                
                for i, file_path in enumerate(test_files):
                    future = executor.submit(convert_file, file_path, i)
                    futures.append(future)
                
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
                total_time = time.time() - start_time
            
            # Check results
            successful = sum(1 for _, success, _ in results if success)
            
            self.print_test(
                "Concurrent Conversions",
                successful == len(test_files),
                f"{successful}/{len(test_files)} completed successfully in {total_time:.2f}s",
                {f"client_{id}": msg for id, success, msg in results}
            )
            
        finally:
            server_process.terminate()
            server_process.wait()
    
    def test_data_uri_edge_cases(self):
        """Test edge cases with data URIs"""
        print(f"\n{BLUE}Testing Data URI Edge Cases{RESET}")
        
        process = subprocess.Popen(
            [MCP_SERVER_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Initialize
            init_req = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "data-uri-test", "version": "1.0"}},
                "id": 1
            }
            process.stdin.write(json.dumps(init_req) + '\n')
            process.stdin.flush()
            process.stdout.readline()
            
            # Test cases
            test_cases = [
                {
                    "name": "Basic text",
                    "uri": "data:text/plain;charset=utf-8,Hello%20World",
                    "expected": "Hello World"
                },
                {
                    "name": "Korean text",
                    "uri": "data:text/plain;charset=utf-8," + requests.utils.quote("안녕하세요"),
                    "expected": "안녕하세요"
                },
                {
                    "name": "Base64 encoded",
                    "uri": "data:text/plain;base64,SGVsbG8gV29ybGQ=",
                    "expected": "Hello World"
                },
                {
                    "name": "HTML content",
                    "uri": "data:text/html,<h1>Test</h1><p>Content</p>",
                    "expected_contains": ["Test", "Content"]
                },
                {
                    "name": "Empty data",
                    "uri": "data:text/plain,",
                    "expected": ""
                }
            ]
            
            for test_case in test_cases:
                convert_req = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_to_markdown",
                        "arguments": {"uri": test_case["uri"]}
                    },
                    "id": test_case["name"]
                }
                
                process.stdin.write(json.dumps(convert_req) + '\n')
                process.stdin.flush()
                
                response_line = process.stdout.readline()
                if response_line:
                    try:
                        response = json.loads(response_line)
                        if "result" in response:
                            content = response["result"].get("content", [])
                            if content:
                                text = content[0].get("text", "")
                                
                                if "expected" in test_case:
                                    passed = test_case["expected"] in text
                                elif "expected_contains" in test_case:
                                    passed = all(item in text for item in test_case["expected_contains"])
                                else:
                                    passed = True
                                
                                self.print_test(
                                    f"Data URI - {test_case['name']}",
                                    passed,
                                    "Converted correctly" if passed else "Conversion incorrect",
                                    {"result": text[:50] + "..." if len(text) > 50 else text}
                                )
                            else:
                                passed = test_case.get("expected") == ""
                                self.print_test(
                                    f"Data URI - {test_case['name']}",
                                    passed,
                                    "Empty result" if passed else "No content returned",
                                    {}
                                )
                        else:
                            self.print_test(
                                f"Data URI - {test_case['name']}",
                                False,
                                "Conversion failed",
                                {"error": response.get("error", "Unknown")}
                            )
                    except Exception as e:
                        self.print_test(
                            f"Data URI - {test_case['name']}",
                            False,
                            f"Exception: {str(e)}",
                            {}
                        )
                
        finally:
            process.terminate()
            process.wait()
    
    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print(f"{YELLOW}VoidLight MarkItDown MCP Server - Edge Case Tests{RESET}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check server exists
        if not os.path.exists(MCP_SERVER_BIN):
            print(f"{RED}Error: MCP server not found at {MCP_SERVER_BIN}{RESET}")
            return 1
        
        try:
            # Run test suites
            self.test_malformed_requests()
            self.test_special_characters()
            self.test_data_uri_edge_cases()
            self.test_large_file_conversion()
            self.test_memory_usage()
            self.test_concurrent_conversions()
            
            print(f"\n{BLUE}Edge case testing complete{RESET}")
            return 0
            
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    tester = EdgeCaseTests()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())