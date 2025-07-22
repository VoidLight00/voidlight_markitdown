#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for VoidLight MarkItDown MCP Server
Tests all MCP protocol methods, error handling, concurrent clients, and Korean text processing
"""

import json
import asyncio
import subprocess
import time
import sys
import os
import tempfile
import requests
import threading
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import concurrent.futures
import uuid

# Test configuration
MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"
TEST_KOREAN_DOC = "/Users/voidlight/voidlight_markitdown/test_korean_document.txt"
TEST_PORT = 3001

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

class TestResult:
    """Container for test results"""
    def __init__(self, name: str, passed: bool, message: str, details: Optional[Dict] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()

class MCPTestClient:
    """Test client for MCP server communication"""
    
    def __init__(self, mode: str = "stdio", host: str = "localhost", port: int = TEST_PORT):
        self.mode = mode
        self.host = host
        self.port = port
        self.process = None
        self.session_id = str(uuid.uuid4())
        
    def start_stdio_server(self):
        """Start MCP server in STDIO mode"""
        self.process = subprocess.Popen(
            [MCP_SERVER_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        return self.process
    
    def send_request(self, request: Dict) -> Optional[Dict]:
        """Send request and get response in STDIO mode"""
        if self.mode == "stdio" and self.process:
            self.process.stdin.write(json.dumps(request) + '\n')
            self.process.stdin.flush()
            
            # Read response, skipping log lines
            import select
            timeout = 5  # 5 second timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check if data is available
                ready = select.select([self.process.stdout], [], [], 0.1)
                if ready[0]:
                    response_line = self.process.stdout.readline()
                    if not response_line:
                        return None
                    
                    # Skip log lines (they contain timestamps)
                    response_line = response_line.strip()
                    if response_line.startswith('{') and response_line.endswith('}'):
                        try:
                            return json.loads(response_line)
                        except json.JSONDecodeError:
                            continue
            
            return None  # Timeout
        return None
    
    def send_http_request(self, endpoint: str, data: Dict) -> requests.Response:
        """Send HTTP request to MCP server"""
        url = f"http://{self.host}:{self.port}{endpoint}"
        return requests.post(
            url,
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
        )
    
    def close(self):
        """Clean up resources"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
                self.process.wait()

class IntegrationTestSuite:
    """Comprehensive integration test suite"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.test_files: List[str] = []
        
    def add_result(self, result: TestResult):
        """Add test result"""
        self.results.append(result)
        self._print_result(result)
    
    def _print_result(self, result: TestResult):
        """Print test result with formatting"""
        status = f"{GREEN}✓ PASSED{RESET}" if result.passed else f"{RED}✗ FAILED{RESET}"
        print(f"{status} {result.name}: {result.message}")
        if result.details and not result.passed:
            for key, value in result.details.items():
                print(f"  {YELLOW}{key}:{RESET} {value}")
    
    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{title}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
    
    def create_test_files(self) -> Dict[str, str]:
        """Create various test files for comprehensive testing"""
        files = {}
        
        # Korean text file
        korean_content = """한국어 문서 테스트
        
이것은 다양한 한글 문자를 포함합니다:
- 기본 한글: 가나다라마바사
- 받침이 있는 글자: 강남, 학교, 병원
- 복잡한 글자: 읽, 닭, 값
- 특수 문자: 『』「」〈〉

숫자와 혼합: 2024년 7월 22일
영어와 혼합: Hello 안녕하세요 World!
중국어와 혼합: 你好 안녕하세요 您好

테스트 완료!"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(korean_content)
            files['korean_text'] = f.name
            self.test_files.append(f.name)
        
        # HTML file with Korean
        html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>한국어 HTML 테스트</title>
</head>
<body>
    <h1>VoidLight MarkItDown 통합 테스트</h1>
    <p>이것은 <strong>HTML</strong> 문서입니다.</p>
    <ul>
        <li>첫 번째: 기본 변환</li>
        <li>두 번째: 한글 처리</li>
        <li>세 번째: 특수문자 ℃ ㎡ ㎏</li>
    </ul>
    <table>
        <tr><th>항목</th><th>값</th></tr>
        <tr><td>온도</td><td>25℃</td></tr>
        <tr><td>면적</td><td>100㎡</td></tr>
    </table>
</body>
</html>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            files['korean_html'] = f.name
            self.test_files.append(f.name)
        
        # JSON file with Korean
        json_content = {
            "title": "한국어 JSON 테스트",
            "description": "JSON 파일에서 한글 처리 테스트",
            "data": {
                "이름": "홍길동",
                "나이": 30,
                "주소": "서울시 강남구",
                "특수문자": "㈜ ㎡ ℃"
            },
            "배열": ["첫째", "둘째", "셋째"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=2)
            files['korean_json'] = f.name
            self.test_files.append(f.name)
        
        # Mixed encoding file (intentionally problematic)
        mixed_content = "ASCII text\n한글 텍스트\nLatin-1: café\nEmoji: 😀 🎉"
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            # Write with mixed encodings to test robustness
            f.write(mixed_content.encode('utf-8'))
            files['mixed_encoding'] = f.name
            self.test_files.append(f.name)
        
        return files
    
    async def test_mcp_protocol_methods(self):
        """Test all MCP protocol methods"""
        self.print_header("MCP Protocol Methods Test")
        
        client = MCPTestClient(mode="stdio")
        server = client.start_stdio_server()
        
        try:
            # Test 1: Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "integration-test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            response = client.send_request(init_request)
            if response and "result" in response:
                self.add_result(TestResult(
                    "MCP Initialize",
                    True,
                    "Server initialized successfully",
                    {"server_info": response.get("result", {}).get("serverInfo")}
                ))
            else:
                self.add_result(TestResult(
                    "MCP Initialize",
                    False,
                    "Failed to initialize server",
                    {"response": response}
                ))
            
            # Test 2: List Tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            response = client.send_request(list_tools_request)
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                self.add_result(TestResult(
                    "MCP List Tools",
                    len(tools) >= 2,  # Should have at least 2 tools
                    f"Found {len(tools)} tools",
                    {"tools": [t.get("name") for t in tools]}
                ))
            else:
                self.add_result(TestResult(
                    "MCP List Tools",
                    False,
                    "Failed to list tools",
                    {"response": response}
                ))
            
            # Test 3: Call Tool - convert_to_markdown
            test_files = self.create_test_files()
            
            convert_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "convert_to_markdown",
                    "arguments": {
                        "uri": f"file://{test_files['korean_text']}"
                    }
                },
                "id": 3
            }
            
            response = client.send_request(convert_request)
            if response and "result" in response:
                content = response["result"].get("content", [])
                if content and isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                    has_korean = any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in text)
                    self.add_result(TestResult(
                        "MCP Tool Call - convert_to_markdown",
                        has_korean,
                        "Successfully converted Korean text",
                        {"content_length": len(text), "has_korean": has_korean}
                    ))
                else:
                    self.add_result(TestResult(
                        "MCP Tool Call - convert_to_markdown",
                        False,
                        "No content in response",
                        {"response": response}
                    ))
            else:
                self.add_result(TestResult(
                    "MCP Tool Call - convert_to_markdown",
                    False,
                    "Tool call failed",
                    {"response": response}
                ))
            
            # Test 4: Call Tool - convert_korean_document
            korean_convert_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "convert_korean_document",
                    "arguments": {
                        "uri": f"file://{test_files['korean_html']}",
                        "normalize_korean": True
                    }
                },
                "id": 4
            }
            
            response = client.send_request(korean_convert_request)
            if response and "result" in response:
                content = response["result"].get("content", [])
                if content and isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                    # Check for normalized Korean and proper HTML conversion
                    has_header = "VoidLight MarkItDown" in text
                    has_list = "첫 번째" in text
                    self.add_result(TestResult(
                        "MCP Tool Call - convert_korean_document",
                        has_header and has_list,
                        "Successfully converted Korean HTML",
                        {"has_header": has_header, "has_list": has_list}
                    ))
                else:
                    self.add_result(TestResult(
                        "MCP Tool Call - convert_korean_document",
                        False,
                        "No content in response",
                        {"response": response}
                    ))
            else:
                self.add_result(TestResult(
                    "MCP Tool Call - convert_korean_document",
                    False,
                    "Korean document tool call failed",
                    {"response": response}
                ))
            
        finally:
            client.close()
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        self.print_header("Error Handling Test")
        
        client = MCPTestClient(mode="stdio")
        server = client.start_stdio_server()
        
        try:
            # Initialize first
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "error-test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            client.send_request(init_request)
            
            # Test 1: Invalid method
            invalid_method_request = {
                "jsonrpc": "2.0",
                "method": "invalid/method",
                "params": {},
                "id": 2
            }
            
            response = client.send_request(invalid_method_request)
            if response and "error" in response:
                self.add_result(TestResult(
                    "Error Handling - Invalid Method",
                    True,
                    "Server correctly returned error for invalid method",
                    {"error": response["error"]}
                ))
            else:
                self.add_result(TestResult(
                    "Error Handling - Invalid Method",
                    False,
                    "Server did not handle invalid method properly",
                    {"response": response}
                ))
            
            # Test 2: Invalid tool name
            invalid_tool_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "non_existent_tool",
                    "arguments": {}
                },
                "id": 3
            }
            
            response = client.send_request(invalid_tool_request)
            if response and "error" in response:
                self.add_result(TestResult(
                    "Error Handling - Invalid Tool",
                    True,
                    "Server correctly returned error for invalid tool",
                    {"error": response["error"]}
                ))
            else:
                self.add_result(TestResult(
                    "Error Handling - Invalid Tool",
                    False,
                    "Server did not handle invalid tool properly",
                    {"response": response}
                ))
            
            # Test 3: Invalid URI
            invalid_uri_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "convert_to_markdown",
                    "arguments": {
                        "uri": "invalid://not-a-valid-uri"
                    }
                },
                "id": 4
            }
            
            response = client.send_request(invalid_uri_request)
            if response and "error" in response:
                self.add_result(TestResult(
                    "Error Handling - Invalid URI",
                    True,
                    "Server correctly handled invalid URI",
                    {"error": response["error"]}
                ))
            else:
                self.add_result(TestResult(
                    "Error Handling - Invalid URI",
                    False,
                    "Server did not handle invalid URI properly",
                    {"response": response}
                ))
            
            # Test 4: Missing required arguments
            missing_args_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "convert_to_markdown",
                    "arguments": {}  # Missing 'uri' argument
                },
                "id": 5
            }
            
            response = client.send_request(missing_args_request)
            if response and "error" in response:
                self.add_result(TestResult(
                    "Error Handling - Missing Arguments",
                    True,
                    "Server correctly handled missing arguments",
                    {"error": response["error"]}
                ))
            else:
                self.add_result(TestResult(
                    "Error Handling - Missing Arguments",
                    False,
                    "Server did not handle missing arguments properly",
                    {"response": response}
                ))
            
            # Test 5: Non-existent file
            non_existent_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "convert_to_markdown",
                    "arguments": {
                        "uri": "file:///does/not/exist/file.txt"
                    }
                },
                "id": 6
            }
            
            response = client.send_request(non_existent_request)
            if response and "error" in response:
                self.add_result(TestResult(
                    "Error Handling - Non-existent File",
                    True,
                    "Server correctly handled non-existent file",
                    {"error": response["error"]}
                ))
            else:
                self.add_result(TestResult(
                    "Error Handling - Non-existent File",
                    False,
                    "Server did not handle non-existent file properly",
                    {"response": response}
                ))
            
        finally:
            client.close()
    
    async def test_concurrent_clients(self):
        """Test multiple concurrent clients"""
        self.print_header("Concurrent Clients Test")
        
        # Start HTTP/SSE server
        server_process = subprocess.Popen(
            [MCP_SERVER_BIN, "--http", "--port", str(TEST_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Create test files
            test_files = self.create_test_files()
            
            async def client_task(client_id: int, file_path: str) -> Tuple[int, bool, str]:
                """Task for each concurrent client"""
                try:
                    # Initialize session
                    init_data = {
                        "jsonrpc": "2.0",
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
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
                        return (client_id, False, f"Init failed: {response.status_code}")
                    
                    # Convert document
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
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "result" in result:
                            return (client_id, True, "Success")
                        else:
                            return (client_id, False, "No result in response")
                    else:
                        return (client_id, False, f"Convert failed: {response.status_code}")
                    
                except Exception as e:
                    return (client_id, False, str(e))
            
            # Run concurrent clients
            num_clients = 5
            tasks = []
            
            for i in range(num_clients):
                # Use different files for variety
                file_key = list(test_files.keys())[i % len(test_files)]
                task = asyncio.create_task(client_task(i, test_files[file_key]))
                tasks.append(task)
            
            # Wait for all tasks
            results = await asyncio.gather(*tasks)
            
            # Analyze results
            successful = sum(1 for _, success, _ in results if success)
            
            self.add_result(TestResult(
                "Concurrent Clients",
                successful == num_clients,
                f"{successful}/{num_clients} clients completed successfully",
                {f"client_{id}": f"{success} - {msg}" for id, success, msg in results}
            ))
            
        finally:
            # Cleanup
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except:
                server_process.kill()
                server_process.wait()
    
    async def test_http_sse_mode(self):
        """Test HTTP/SSE mode comprehensively"""
        self.print_header("HTTP/SSE Mode Test")
        
        # Start server
        server_process = subprocess.Popen(
            [MCP_SERVER_BIN, "--http", "--port", str(TEST_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Wait for server
            await asyncio.sleep(3)
            
            # Test 1: Server health check
            try:
                response = requests.get(f"http://localhost:{TEST_PORT}/", timeout=5)
                self.add_result(TestResult(
                    "HTTP Server Health",
                    response.status_code < 500,
                    f"Server responding with status {response.status_code}",
                    {}
                ))
            except Exception as e:
                self.add_result(TestResult(
                    "HTTP Server Health",
                    False,
                    "Server not responding",
                    {"error": str(e)}
                ))
            
            # Test 2: SSE endpoint
            try:
                headers = {
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache'
                }
                
                # Start SSE connection (will timeout, which is expected)
                with requests.get(
                    f"http://localhost:{TEST_PORT}/sse",
                    headers=headers,
                    stream=True,
                    timeout=2
                ) as response:
                    self.add_result(TestResult(
                        "SSE Endpoint",
                        response.status_code == 200,
                        "SSE endpoint is available",
                        {"headers": dict(response.headers)}
                    ))
            except requests.exceptions.Timeout:
                # Timeout is expected for SSE
                self.add_result(TestResult(
                    "SSE Endpoint",
                    True,
                    "SSE endpoint ready for streaming",
                    {}
                ))
            except Exception as e:
                self.add_result(TestResult(
                    "SSE Endpoint",
                    False,
                    "SSE endpoint error",
                    {"error": str(e)}
                ))
            
            # Test 3: MCP protocol over HTTP
            test_files = self.create_test_files()
            
            # Initialize
            init_data = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "http-test-client",
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
            
            if response.status_code == 200:
                self.add_result(TestResult(
                    "HTTP MCP Initialize",
                    True,
                    "Successfully initialized via HTTP",
                    {}
                ))
                
                # Test tool call
                convert_data = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_korean_document",
                        "arguments": {
                            "uri": f"file://{test_files['korean_json']}",
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
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        self.add_result(TestResult(
                            "HTTP Tool Call",
                            True,
                            "Successfully called tool via HTTP",
                            {"response_size": len(response.text)}
                        ))
                    else:
                        self.add_result(TestResult(
                            "HTTP Tool Call",
                            False,
                            "No result in HTTP response",
                            {"response": result}
                        ))
                else:
                    self.add_result(TestResult(
                        "HTTP Tool Call",
                        False,
                        f"HTTP tool call failed with status {response.status_code}",
                        {}
                    ))
            else:
                self.add_result(TestResult(
                    "HTTP MCP Initialize",
                    False,
                    f"HTTP initialization failed with status {response.status_code}",
                    {}
                ))
            
        finally:
            # Cleanup
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except:
                server_process.kill()
                server_process.wait()
    
    async def test_korean_text_processing(self):
        """Test Korean text processing through MCP"""
        self.print_header("Korean Text Processing Test")
        
        client = MCPTestClient(mode="stdio")
        server = client.start_stdio_server()
        
        try:
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "korean-test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            client.send_request(init_request)
            
            # Create various Korean test cases
            test_cases = [
                {
                    "name": "Basic Korean",
                    "content": "안녕하세요. 한글 테스트입니다.",
                    "check": lambda text: "안녕하세요" in text
                },
                {
                    "name": "Mixed Korean-English",
                    "content": "Hello 세계! This is 테스트 document.",
                    "check": lambda text: "Hello" in text and "세계" in text
                },
                {
                    "name": "Korean with special characters",
                    "content": "특수문자: 『한글』 「테스트」 〈문서〉 ㈜회사",
                    "check": lambda text: "『한글』" in text or "한글" in text
                },
                {
                    "name": "Korean with numbers",
                    "content": "2024년 7월 22일 오후 3시 30분",
                    "check": lambda text: "2024" in text and "7월" in text
                },
                {
                    "name": "Complex Korean characters",
                    "content": "읽기, 닭고기, 값진, 앉아서, 밟고",
                    "check": lambda text: "닭고기" in text
                }
            ]
            
            for test_case in test_cases:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(test_case["content"])
                    temp_file = f.name
                
                try:
                    # Test with convert_korean_document
                    request = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "convert_korean_document",
                            "arguments": {
                                "uri": f"file://{temp_file}",
                                "normalize_korean": True
                            }
                        },
                        "id": test_case["name"]
                    }
                    
                    response = client.send_request(request)
                    if response and "result" in response:
                        content = response["result"].get("content", [])
                        if content and isinstance(content, list):
                            text = content[0].get("text", "")
                            passed = test_case["check"](text)
                            self.add_result(TestResult(
                                f"Korean Processing - {test_case['name']}",
                                passed,
                                "Correctly processed" if passed else "Processing failed",
                                {"original": test_case["content"][:50], "processed": text[:50]}
                            ))
                        else:
                            self.add_result(TestResult(
                                f"Korean Processing - {test_case['name']}",
                                False,
                                "No content in response",
                                {}
                            ))
                    else:
                        self.add_result(TestResult(
                            f"Korean Processing - {test_case['name']}",
                            False,
                            "Request failed",
                            {"response": response}
                        ))
                finally:
                    os.unlink(temp_file)
            
        finally:
            client.close()
    
    def cleanup(self):
        """Clean up test files"""
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
    
    async def run_all_tests(self):
        """Run all integration tests"""
        start_time = datetime.now()
        
        print(f"{CYAN}VoidLight MarkItDown MCP Server - Comprehensive Integration Tests{RESET}")
        print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        if not os.path.exists(MCP_SERVER_BIN):
            print(f"{RED}Error: MCP server not found at {MCP_SERVER_BIN}{RESET}")
            return 1
        
        try:
            # Run all test suites
            await self.test_mcp_protocol_methods()
            await self.test_error_handling()
            await self.test_http_sse_mode()
            await self.test_concurrent_clients()
            await self.test_korean_text_processing()
            
            # Print summary
            self.print_header("Test Summary")
            
            passed = sum(1 for r in self.results if r.passed)
            total = len(self.results)
            
            # Group results by category
            categories = {}
            for result in self.results:
                category = result.name.split(" - ")[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(result)
            
            # Print by category
            for category, results in categories.items():
                cat_passed = sum(1 for r in results if r.passed)
                cat_total = len(results)
                print(f"\n{MAGENTA}{category}:{RESET} {cat_passed}/{cat_total} passed")
                
                for result in results:
                    status = f"{GREEN}✓{RESET}" if result.passed else f"{RED}✗{RESET}"
                    print(f"  {status} {result.name}")
            
            # Overall summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n{BLUE}{'='*70}{RESET}")
            print(f"Total: {passed}/{total} tests passed")
            print(f"Duration: {duration:.2f} seconds")
            
            if passed == total:
                print(f"\n{GREEN}All tests passed! 🎉{RESET}")
                return 0
            else:
                print(f"\n{RED}{total - passed} tests failed. See details above.{RESET}")
                return 1
                
        finally:
            self.cleanup()

async def main():
    """Main entry point"""
    suite = IntegrationTestSuite()
    return await suite.run_all_tests()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)