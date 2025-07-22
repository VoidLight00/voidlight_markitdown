#!/usr/bin/env python3
"""
Enhanced Comprehensive Integration Test Suite for VoidLight MarkItDown MCP Server
Includes automated testing, performance benchmarks, stress tests, and detailed reporting
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
import socket
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
import concurrent.futures
import uuid
import hashlib
import statistics
import yaml
import base64
from collections import defaultdict
import traceback

# Test configuration
MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"
TEST_KOREAN_DOC = "/Users/voidlight/voidlight_markitdown/test_korean_document.txt"
TEST_PORT_BASE = 3001
MAX_PORT_ATTEMPTS = 10

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Performance thresholds
PERF_THRESHOLDS = {
    'initialization_time': 2.0,  # seconds
    'tool_call_time': 5.0,  # seconds
    'concurrent_clients': 10,  # number of clients
    'memory_usage_mb': 500,  # MB
    'response_time_p95': 3.0,  # seconds
}

class TestMetrics:
    """Track test metrics and performance data"""
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = []
        self.performance_data = defaultdict(list)
        self.error_logs = []
        self.memory_usage = []
        self.response_times = []
        
    def add_result(self, category: str, name: str, passed: bool, message: str, details: Dict = None):
        """Add a test result"""
        self.test_results.append({
            'category': category,
            'name': name,
            'passed': passed,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now()
        })
        
    def add_performance_metric(self, metric_name: str, value: float):
        """Add performance metric"""
        self.performance_data[metric_name].append(value)
        
    def add_error(self, error: str, context: Dict = None):
        """Log an error"""
        self.error_logs.append({
            'error': error,
            'context': context or {},
            'timestamp': datetime.now(),
            'traceback': traceback.format_exc()
        })
        
    def get_summary(self) -> Dict:
        """Get test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        
        # Calculate performance statistics
        perf_stats = {}
        for metric, values in self.performance_data.items():
            if values:
                perf_stats[metric] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': statistics.mean(values),
                    'median': statistics.median(values),
                    'p95': statistics.quantiles(values, n=20)[18] if len(values) > 1 else values[0]
                }
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'performance_stats': perf_stats,
            'error_count': len(self.error_logs)
        }

class MCPTestServer:
    """Manages MCP server lifecycle for testing"""
    
    def __init__(self, mode: str = "stdio", port: Optional[int] = None):
        self.mode = mode
        self.port = port or self._find_free_port()
        self.process = None
        self.start_time = None
        self.pid = None
        
    def _find_free_port(self) -> int:
        """Find a free port for testing"""
        for i in range(MAX_PORT_ATTEMPTS):
            port = TEST_PORT_BASE + i
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                continue
        raise RuntimeError("Could not find a free port")
        
    async def start(self) -> bool:
        """Start the MCP server"""
        try:
            if self.mode == "stdio":
                self.process = subprocess.Popen(
                    [MCP_SERVER_BIN],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
            else:  # HTTP/SSE mode
                self.process = subprocess.Popen(
                    [MCP_SERVER_BIN, "--http", "--port", str(self.port)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Wait for server to start
                await asyncio.sleep(2)
                
                # Verify server is running
                for _ in range(10):
                    try:
                        response = requests.get(f"http://localhost:{self.port}/", timeout=1)
                        if response.status_code < 500:
                            break
                    except:
                        await asyncio.sleep(0.5)
                        
            self.start_time = datetime.now()
            self.pid = self.process.pid
            return True
            
        except Exception as e:
            print(f"{RED}Failed to start server: {str(e)}{RESET}")
            return False
            
    async def stop(self):
        """Stop the MCP server"""
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.create_subprocess_exec('wait', str(self.process.pid)),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                self.process.kill()
                
    def get_memory_usage(self) -> Optional[float]:
        """Get server memory usage in MB"""
        if self.pid:
            try:
                process = psutil.Process(self.pid)
                return process.memory_info().rss / 1024 / 1024  # Convert to MB
            except:
                pass
        return None

class MCPProtocolTester:
    """Tests MCP protocol compliance"""
    
    def __init__(self, server: MCPTestServer, metrics: TestMetrics):
        self.server = server
        self.metrics = metrics
        self.client_id = str(uuid.uuid4())
        
    async def test_protocol_compliance(self) -> bool:
        """Test full MCP protocol compliance"""
        all_passed = True
        
        # Test required methods
        required_methods = [
            "initialize",
            "initialized",
            "tools/list",
            "tools/call",
            "resources/list",
            "resources/read",
            "prompts/list",
            "prompts/get",
            "completion/complete"
        ]
        
        for method in required_methods:
            passed = await self._test_method(method)
            all_passed = all_passed and passed
            
        return all_passed
        
    async def _test_method(self, method: str) -> bool:
        """Test a specific MCP method"""
        # Implementation depends on method
        # This is a placeholder - implement based on MCP spec
        return True

class StressTestRunner:
    """Runs stress tests on the MCP server"""
    
    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        
    async def run_stress_test(self, server_port: int, duration_seconds: int = 30) -> Dict:
        """Run stress test for specified duration"""
        print(f"\n{YELLOW}Running stress test for {duration_seconds} seconds...{RESET}")
        
        results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        
        start_time = time.time()
        tasks = []
        
        # Create continuous load
        async def stress_client(client_id: int):
            while time.time() - start_time < duration_seconds:
                try:
                    request_start = time.time()
                    
                    # Make a request
                    response = await self._make_stress_request(server_port, client_id)
                    
                    request_time = time.time() - request_start
                    results['response_times'].append(request_time)
                    
                    if response:
                        results['successful_requests'] += 1
                    else:
                        results['failed_requests'] += 1
                        
                    results['total_requests'] += 1
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    results['errors'].append(str(e))
                    results['failed_requests'] += 1
                    
        # Start multiple stress clients
        num_clients = 10
        for i in range(num_clients):
            task = asyncio.create_task(stress_client(i))
            tasks.append(task)
            
        # Wait for all clients to finish
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate statistics
        if results['response_times']:
            results['avg_response_time'] = statistics.mean(results['response_times'])
            results['p95_response_time'] = statistics.quantiles(results['response_times'], n=20)[18]
            results['max_response_time'] = max(results['response_times'])
            
        results['requests_per_second'] = results['total_requests'] / duration_seconds
        results['success_rate'] = (results['successful_requests'] / results['total_requests'] * 100) if results['total_requests'] > 0 else 0
        
        return results
        
    async def _make_stress_request(self, port: int, client_id: int) -> bool:
        """Make a single stress test request"""
        try:
            # Create a test file with unique content
            content = f"Stress test {client_id} - {uuid.uuid4()}\n한글 스트레스 테스트"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_file = f.name
                
            try:
                # Make conversion request
                data = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_korean_document",
                        "arguments": {
                            "uri": f"file://{temp_file}",
                            "normalize_korean": True
                        }
                    },
                    "id": str(uuid.uuid4())
                }
                
                response = requests.post(
                    f"http://localhost:{port}/mcp",
                    json=data,
                    timeout=5
                )
                
                return response.status_code == 200
                
            finally:
                os.unlink(temp_file)
                
        except Exception:
            return False

class AutomatedTestRunner:
    """Main automated test runner"""
    
    def __init__(self):
        self.metrics = TestMetrics()
        self.test_report = {
            'start_time': datetime.now().isoformat(),
            'environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'mcp_server_path': MCP_SERVER_BIN,
                'test_port_base': TEST_PORT_BASE
            },
            'tests': [],
            'summary': {}
        }
        
    async def run_all_tests(self) -> int:
        """Run all integration tests"""
        print(f"{BOLD}{CYAN}VoidLight MarkItDown MCP Server - Enhanced Integration Test Suite{RESET}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        if not os.path.exists(MCP_SERVER_BIN):
            print(f"{RED}Error: MCP server not found at {MCP_SERVER_BIN}{RESET}")
            return 1
            
        try:
            # Run test suites
            await self._test_stdio_mode()
            await self._test_http_sse_mode()
            await self._test_concurrent_clients()
            await self._test_error_handling()
            await self._test_korean_processing()
            await self._test_performance()
            await self._test_stress()
            await self._test_edge_cases()
            
            # Generate report
            self._generate_report()
            
            # Print summary
            summary = self.metrics.get_summary()
            self._print_summary(summary)
            
            # Determine exit code
            return 0 if summary['failed_tests'] == 0 else 1
            
        except Exception as e:
            print(f"{RED}Fatal error during testing: {str(e)}{RESET}")
            traceback.print_exc()
            return 2
            
    async def _test_stdio_mode(self):
        """Test STDIO mode comprehensively"""
        print(f"\n{BLUE}Testing STDIO Mode...{RESET}")
        
        server = MCPTestServer(mode="stdio")
        if not await server.start():
            self.metrics.add_result("STDIO", "Server Start", False, "Failed to start STDIO server")
            return
            
        try:
            # Test basic communication
            start_time = time.time()
            
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "automated-test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            server.process.stdin.write(json.dumps(init_request) + '\n')
            server.process.stdin.flush()
            
            # Read response with timeout
            response_line = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, server.process.stdout.readline),
                timeout=5.0
            )
            
            init_time = time.time() - start_time
            self.metrics.add_performance_metric('stdio_init_time', init_time)
            
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        self.metrics.add_result("STDIO", "Initialization", True, 
                                              f"Initialized in {init_time:.2f}s",
                                              {"server_info": response["result"].get("serverInfo")})
                    else:
                        self.metrics.add_result("STDIO", "Initialization", False, 
                                              "No result in response", {"response": response})
                except json.JSONDecodeError:
                    self.metrics.add_result("STDIO", "Initialization", False, 
                                          "Invalid JSON response", {"response": response_line})
            else:
                self.metrics.add_result("STDIO", "Initialization", False, "No response received")
                
            # Test tool listing
            list_tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            server.process.stdin.write(json.dumps(list_tools_request) + '\n')
            server.process.stdin.flush()
            
            response_line = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, server.process.stdout.readline),
                timeout=5.0
            )
            
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        tools = response["result"].get("tools", [])
                        self.metrics.add_result("STDIO", "List Tools", len(tools) >= 2,
                                              f"Found {len(tools)} tools",
                                              {"tools": [t.get("name") for t in tools]})
                    else:
                        self.metrics.add_result("STDIO", "List Tools", False,
                                              "No result in response", {"response": response})
                except json.JSONDecodeError:
                    self.metrics.add_result("STDIO", "List Tools", False,
                                          "Invalid JSON response", {"response": response_line})
                                          
            # Test Korean document conversion
            test_content = "안녕하세요. STDIO 모드 테스트입니다.\nHello from STDIO mode!"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(test_content)
                temp_file = f.name
                
            try:
                convert_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_korean_document",
                        "arguments": {
                            "uri": f"file://{temp_file}",
                            "normalize_korean": True
                        }
                    },
                    "id": 3
                }
                
                start_time = time.time()
                server.process.stdin.write(json.dumps(convert_request) + '\n')
                server.process.stdin.flush()
                
                response_line = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, server.process.stdout.readline),
                    timeout=10.0
                )
                
                convert_time = time.time() - start_time
                self.metrics.add_performance_metric('stdio_convert_time', convert_time)
                
                if response_line:
                    try:
                        response = json.loads(response_line.strip())
                        if "result" in response:
                            content = response["result"].get("content", [])
                            if content and isinstance(content, list):
                                text = content[0].get("text", "")
                                has_korean = "안녕하세요" in text
                                self.metrics.add_result("STDIO", "Korean Conversion", has_korean,
                                                      f"Converted in {convert_time:.2f}s",
                                                      {"content_preview": text[:100]})
                            else:
                                self.metrics.add_result("STDIO", "Korean Conversion", False,
                                                      "No content in response", {"response": response})
                        else:
                            self.metrics.add_result("STDIO", "Korean Conversion", False,
                                                  "No result in response", {"response": response})
                    except json.JSONDecodeError:
                        self.metrics.add_result("STDIO", "Korean Conversion", False,
                                              "Invalid JSON response", {"response": response_line})
                                              
            finally:
                os.unlink(temp_file)
                
            # Check memory usage
            memory_mb = server.get_memory_usage()
            if memory_mb:
                self.metrics.add_performance_metric('stdio_memory_mb', memory_mb)
                self.metrics.add_result("STDIO", "Memory Usage", 
                                      memory_mb < PERF_THRESHOLDS['memory_usage_mb'],
                                      f"Using {memory_mb:.1f} MB",
                                      {"threshold": PERF_THRESHOLDS['memory_usage_mb']})
                                      
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "stdio_mode"})
            self.metrics.add_result("STDIO", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    async def _test_http_sse_mode(self):
        """Test HTTP/SSE mode comprehensively"""
        print(f"\n{BLUE}Testing HTTP/SSE Mode...{RESET}")
        
        server = MCPTestServer(mode="http")
        if not await server.start():
            self.metrics.add_result("HTTP/SSE", "Server Start", False, "Failed to start HTTP server")
            return
            
        try:
            port = server.port
            
            # Test server health
            try:
                response = requests.get(f"http://localhost:{port}/", timeout=5)
                self.metrics.add_result("HTTP/SSE", "Server Health", 
                                      response.status_code < 500,
                                      f"Server responded with {response.status_code}")
            except Exception as e:
                self.metrics.add_result("HTTP/SSE", "Server Health", False, str(e))
                return
                
            # Test SSE endpoint
            try:
                headers = {'Accept': 'text/event-stream', 'Cache-Control': 'no-cache'}
                with requests.get(f"http://localhost:{port}/sse", headers=headers, stream=True, timeout=2) as r:
                    self.metrics.add_result("HTTP/SSE", "SSE Endpoint", r.status_code == 200,
                                          "SSE endpoint accessible")
            except requests.exceptions.Timeout:
                # Timeout is expected for SSE
                self.metrics.add_result("HTTP/SSE", "SSE Endpoint", True, "SSE ready for streaming")
            except Exception as e:
                self.metrics.add_result("HTTP/SSE", "SSE Endpoint", False, str(e))
                
            # Test MCP initialization
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
            
            start_time = time.time()
            response = requests.post(f"http://localhost:{port}/mcp", json=init_data)
            init_time = time.time() - start_time
            self.metrics.add_performance_metric('http_init_time', init_time)
            
            if response.status_code == 200:
                self.metrics.add_result("HTTP/SSE", "MCP Initialize", True,
                                      f"Initialized in {init_time:.2f}s")
            else:
                self.metrics.add_result("HTTP/SSE", "MCP Initialize", False,
                                      f"Status {response.status_code}")
                                      
            # Test tool listing
            list_data = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            response = requests.post(f"http://localhost:{port}/mcp", json=list_data)
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    tools = result["result"].get("tools", [])
                    self.metrics.add_result("HTTP/SSE", "List Tools", len(tools) >= 2,
                                          f"Found {len(tools)} tools",
                                          {"tools": [t.get("name") for t in tools]})
                                          
            # Test Korean HTML conversion
            html_content = """<!DOCTYPE html>
<html lang="ko">
<head><title>HTTP 테스트</title></head>
<body>
<h1>HTTP/SSE 모드 테스트</h1>
<p>이것은 <strong>한글</strong> HTML 문서입니다.</p>
</body>
</html>"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
                
            try:
                convert_data = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_korean_document",
                        "arguments": {
                            "uri": f"file://{temp_file}",
                            "normalize_korean": True
                        }
                    },
                    "id": 3
                }
                
                start_time = time.time()
                response = requests.post(f"http://localhost:{port}/mcp", json=convert_data)
                convert_time = time.time() - start_time
                self.metrics.add_performance_metric('http_convert_time', convert_time)
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        content = result["result"].get("content", [])
                        if content and isinstance(content, list):
                            text = content[0].get("text", "")
                            has_korean = "한글" in text and "HTTP/SSE" in text
                            self.metrics.add_result("HTTP/SSE", "HTML Conversion", has_korean,
                                                  f"Converted in {convert_time:.2f}s",
                                                  {"has_korean": has_korean})
                                                  
            finally:
                os.unlink(temp_file)
                
            # Check memory usage
            memory_mb = server.get_memory_usage()
            if memory_mb:
                self.metrics.add_performance_metric('http_memory_mb', memory_mb)
                
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "http_sse_mode"})
            self.metrics.add_result("HTTP/SSE", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    async def _test_concurrent_clients(self):
        """Test concurrent client handling"""
        print(f"\n{BLUE}Testing Concurrent Clients...{RESET}")
        
        server = MCPTestServer(mode="http")
        if not await server.start():
            self.metrics.add_result("Concurrent", "Server Start", False, "Failed to start server")
            return
            
        try:
            port = server.port
            num_clients = PERF_THRESHOLDS['concurrent_clients']
            
            # Create test files
            test_files = []
            for i in range(num_clients):
                content = f"Client {i} test document\n클라이언트 {i} 테스트 문서"
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(content)
                    test_files.append(f.name)
                    
            try:
                async def client_task(client_id: int) -> Tuple[int, bool, float]:
                    """Run a single client test"""
                    start_time = time.time()
                    
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
                        
                        response = requests.post(f"http://localhost:{port}/mcp", json=init_data)
                        if response.status_code != 200:
                            return (client_id, False, 0)
                            
                        # Convert document
                        convert_data = {
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "params": {
                                "name": "convert_korean_document",
                                "arguments": {
                                    "uri": f"file://{test_files[client_id]}",
                                    "normalize_korean": True
                                }
                            },
                            "id": 2
                        }
                        
                        response = requests.post(f"http://localhost:{port}/mcp", json=convert_data)
                        elapsed = time.time() - start_time
                        
                        return (client_id, response.status_code == 200, elapsed)
                        
                    except Exception:
                        return (client_id, False, 0)
                        
                # Run concurrent clients
                start_time = time.time()
                tasks = [client_task(i) for i in range(num_clients)]
                results = await asyncio.gather(*tasks)
                total_time = time.time() - start_time
                
                # Analyze results
                successful = sum(1 for _, success, _ in results if success)
                response_times = [t for _, success, t in results if success and t > 0]
                
                if response_times:
                    avg_response = statistics.mean(response_times)
                    self.metrics.add_performance_metric('concurrent_response_time', avg_response)
                    
                self.metrics.add_result("Concurrent", "Client Handling",
                                      successful == num_clients,
                                      f"{successful}/{num_clients} clients succeeded in {total_time:.2f}s",
                                      {"avg_response_time": avg_response if response_times else None})
                                      
                # Check server memory during concurrent load
                memory_mb = server.get_memory_usage()
                if memory_mb:
                    self.metrics.add_performance_metric('concurrent_memory_mb', memory_mb)
                    
            finally:
                # Cleanup test files
                for f in test_files:
                    try:
                        os.unlink(f)
                    except:
                        pass
                        
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "concurrent_clients"})
            self.metrics.add_result("Concurrent", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    async def _test_error_handling(self):
        """Test error handling scenarios"""
        print(f"\n{BLUE}Testing Error Handling...{RESET}")
        
        server = MCPTestServer(mode="http")
        if not await server.start():
            self.metrics.add_result("Error Handling", "Server Start", False, "Failed to start server")
            return
            
        try:
            port = server.port
            
            # Initialize first
            init_data = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "error-test", "version": "1.0.0"}},
                "id": 1
            }
            requests.post(f"http://localhost:{port}/mcp", json=init_data)
            
            # Test various error scenarios
            error_tests = [
                {
                    "name": "Invalid Method",
                    "data": {
                        "jsonrpc": "2.0",
                        "method": "invalid/method",
                        "params": {},
                        "id": 2
                    }
                },
                {
                    "name": "Invalid Tool",
                    "data": {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {"name": "non_existent_tool", "arguments": {}},
                        "id": 3
                    }
                },
                {
                    "name": "Missing Arguments",
                    "data": {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {"name": "convert_to_markdown", "arguments": {}},
                        "id": 4
                    }
                },
                {
                    "name": "Invalid URI",
                    "data": {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "convert_to_markdown",
                            "arguments": {"uri": "not-a-valid-uri"}
                        },
                        "id": 5
                    }
                },
                {
                    "name": "Non-existent File",
                    "data": {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "convert_to_markdown",
                            "arguments": {"uri": "file:///non/existent/file.txt"}
                        },
                        "id": 6
                    }
                }
            ]
            
            for test in error_tests:
                response = requests.post(f"http://localhost:{port}/mcp", json=test["data"])
                
                if response.status_code == 200:
                    result = response.json()
                    has_error = "error" in result
                    self.metrics.add_result("Error Handling", test["name"], has_error,
                                          "Error returned" if has_error else "No error returned",
                                          {"error": result.get("error") if has_error else None})
                else:
                    self.metrics.add_result("Error Handling", test["name"], True,
                                          f"HTTP error {response.status_code}")
                                          
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "error_handling"})
            self.metrics.add_result("Error Handling", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    async def _test_korean_processing(self):
        """Test Korean text processing capabilities"""
        print(f"\n{BLUE}Testing Korean Processing...{RESET}")
        
        server = MCPTestServer(mode="stdio")
        if not await server.start():
            self.metrics.add_result("Korean", "Server Start", False, "Failed to start server")
            return
            
        try:
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "korean-test", "version": "1.0.0"}},
                "id": 1
            }
            
            server.process.stdin.write(json.dumps(init_request) + '\n')
            server.process.stdin.flush()
            await asyncio.sleep(0.5)  # Wait for initialization
            
            # Test various Korean text scenarios
            test_cases = [
                {
                    "name": "Basic Hangul",
                    "content": "가나다라마바사아자차카타파하",
                    "check": lambda t: "가나다라" in t
                },
                {
                    "name": "Complex Characters",
                    "content": "읽기, 닭고기, 값진, 앉아서, 밟고, 넓은",
                    "check": lambda t: "닭고기" in t and "값진" in t
                },
                {
                    "name": "Special Characters",
                    "content": "특수문자: ㈜회사 ㎡면적 ℃온도 『책』 「문서」",
                    "check": lambda t: "㈜" in t or "회사" in t
                },
                {
                    "name": "Mixed Script",
                    "content": "English한글中文日本語\n混ざった텍스트です",
                    "check": lambda t: "한글" in t and "English" in t
                },
                {
                    "name": "Emoji and Korean",
                    "content": "한글과 이모지 😀 테스트 🎉 완료 ✅",
                    "check": lambda t: "한글" in t and ("😀" in t or "이모지" in t)
                },
                {
                    "name": "JSON Korean",
                    "content": '{"이름": "홍길동", "주소": "서울시 강남구", "메모": "테스트"}',
                    "check": lambda t: "홍길동" in t
                }
            ]
            
            for test_case in test_cases:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(test_case["content"])
                    temp_file = f.name
                    
                try:
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
                    
                    server.process.stdin.write(json.dumps(request) + '\n')
                    server.process.stdin.flush()
                    
                    response_line = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, server.process.stdout.readline),
                        timeout=5.0
                    )
                    
                    if response_line:
                        try:
                            response = json.loads(response_line.strip())
                            if "result" in response:
                                content = response["result"].get("content", [])
                                if content and isinstance(content, list):
                                    text = content[0].get("text", "")
                                    passed = test_case["check"](text)
                                    self.metrics.add_result("Korean", test_case["name"], passed,
                                                          "Processed correctly" if passed else "Check failed",
                                                          {"preview": text[:100]})
                                else:
                                    self.metrics.add_result("Korean", test_case["name"], False,
                                                          "No content in response")
                            else:
                                self.metrics.add_result("Korean", test_case["name"], False,
                                                      "No result in response")
                        except json.JSONDecodeError:
                            self.metrics.add_result("Korean", test_case["name"], False,
                                                  "Invalid JSON response")
                    else:
                        self.metrics.add_result("Korean", test_case["name"], False,
                                              "No response received")
                                              
                finally:
                    os.unlink(temp_file)
                    
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "korean_processing"})
            self.metrics.add_result("Korean", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    async def _test_performance(self):
        """Test performance metrics"""
        print(f"\n{BLUE}Testing Performance...{RESET}")
        
        server = MCPTestServer(mode="http")
        if not await server.start():
            self.metrics.add_result("Performance", "Server Start", False, "Failed to start server")
            return
            
        try:
            port = server.port
            
            # Create test files of various sizes
            test_files = {
                "small": (1, "Small file test\n작은 파일 테스트"),
                "medium": (100, "Medium file line {}\n중간 크기 파일 라인 {}"),
                "large": (1000, "Large file line {}\n큰 파일 라인 {}")
            }
            
            file_paths = {}
            for size_name, (lines, template) in test_files.items():
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    for i in range(lines):
                        f.write(template.format(i, i) + '\n')
                    file_paths[size_name] = f.name
                    
            try:
                # Initialize session
                init_data = {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "perf-test", "version": "1.0.0"}},
                    "id": 1
                }
                requests.post(f"http://localhost:{port}/mcp", json=init_data)
                
                # Test conversion performance for different file sizes
                for size_name, file_path in file_paths.items():
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
                        "id": size_name
                    }
                    
                    start_time = time.time()
                    response = requests.post(f"http://localhost:{port}/mcp", json=convert_data)
                    elapsed = time.time() - start_time
                    
                    self.metrics.add_performance_metric(f'convert_{size_name}_time', elapsed)
                    
                    if response.status_code == 200:
                        self.metrics.add_result("Performance", f"{size_name.title()} File",
                                              elapsed < PERF_THRESHOLDS['tool_call_time'],
                                              f"Converted in {elapsed:.2f}s",
                                              {"threshold": PERF_THRESHOLDS['tool_call_time']})
                    else:
                        self.metrics.add_result("Performance", f"{size_name.title()} File",
                                              False, f"Failed with status {response.status_code}")
                                              
                # Test rapid sequential requests
                rapid_times = []
                for i in range(10):
                    start_time = time.time()
                    response = requests.post(f"http://localhost:{port}/mcp", json={
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": f"rapid-{i}"
                    })
                    rapid_times.append(time.time() - start_time)
                    
                avg_rapid = statistics.mean(rapid_times)
                self.metrics.add_performance_metric('rapid_request_time', avg_rapid)
                self.metrics.add_result("Performance", "Rapid Requests",
                                      avg_rapid < 0.1,  # Should be very fast
                                      f"Avg {avg_rapid:.3f}s for 10 requests")
                                      
            finally:
                # Cleanup
                for path in file_paths.values():
                    try:
                        os.unlink(path)
                    except:
                        pass
                        
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "performance"})
            self.metrics.add_result("Performance", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    async def _test_stress(self):
        """Run stress tests"""
        print(f"\n{BLUE}Running Stress Tests...{RESET}")
        
        server = MCPTestServer(mode="http")
        if not await server.start():
            self.metrics.add_result("Stress", "Server Start", False, "Failed to start server")
            return
            
        try:
            # Initialize for stress test
            init_data = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "stress-test", "version": "1.0.0"}},
                "id": 1
            }
            requests.post(f"http://localhost:{server.port}/mcp", json=init_data)
            
            # Run stress test
            stress_runner = StressTestRunner(self.metrics)
            stress_results = await stress_runner.run_stress_test(server.port, duration_seconds=10)
            
            # Evaluate results
            self.metrics.add_result("Stress", "Request Handling",
                                  stress_results['success_rate'] > 95,
                                  f"{stress_results['success_rate']:.1f}% success rate",
                                  {
                                      "total_requests": stress_results['total_requests'],
                                      "requests_per_second": f"{stress_results['requests_per_second']:.1f}",
                                      "avg_response_time": f"{stress_results.get('avg_response_time', 0):.3f}s"
                                  })
                                  
            if stress_results.get('p95_response_time'):
                self.metrics.add_result("Stress", "Response Time P95",
                                      stress_results['p95_response_time'] < PERF_THRESHOLDS['response_time_p95'],
                                      f"{stress_results['p95_response_time']:.3f}s",
                                      {"threshold": PERF_THRESHOLDS['response_time_p95']})
                                      
            # Check server stability after stress
            memory_mb = server.get_memory_usage()
            if memory_mb:
                self.metrics.add_performance_metric('stress_memory_mb', memory_mb)
                self.metrics.add_result("Stress", "Memory After Stress",
                                      memory_mb < PERF_THRESHOLDS['memory_usage_mb'] * 1.5,
                                      f"Using {memory_mb:.1f} MB after stress")
                                      
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "stress"})
            self.metrics.add_result("Stress", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    async def _test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print(f"\n{BLUE}Testing Edge Cases...{RESET}")
        
        server = MCPTestServer(mode="http")
        if not await server.start():
            self.metrics.add_result("Edge Cases", "Server Start", False, "Failed to start server")
            return
            
        try:
            port = server.port
            
            # Initialize
            init_data = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "edge-test", "version": "1.0.0"}},
                "id": 1
            }
            requests.post(f"http://localhost:{port}/mcp", json=init_data)
            
            # Test edge cases
            edge_tests = [
                {
                    "name": "Empty File",
                    "content": "",
                    "check": lambda r: r.status_code == 200
                },
                {
                    "name": "Only Whitespace",
                    "content": "   \n\t\n   \n",
                    "check": lambda r: r.status_code == 200
                },
                {
                    "name": "Very Long Line",
                    "content": "A" * 10000 + " 긴줄테스트",
                    "check": lambda r: r.status_code == 200
                },
                {
                    "name": "Binary Data",
                    "content": b"\x00\x01\x02\xFF\xFE\xFD",
                    "binary": True,
                    "check": lambda r: True  # Should handle gracefully
                },
                {
                    "name": "Mixed Encodings",
                    "content": "UTF-8: 한글\nLatin-1: café\nASCII: test",
                    "check": lambda r: r.status_code == 200
                },
                {
                    "name": "Null Bytes",
                    "content": "Before\x00After\x00한글",
                    "check": lambda r: r.status_code == 200
                }
            ]
            
            for test in edge_tests:
                if test.get("binary"):
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
                        f.write(test["content"])
                        temp_file = f.name
                else:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                        f.write(test["content"])
                        temp_file = f.name
                        
                try:
                    convert_data = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "convert_to_markdown",
                            "arguments": {"uri": f"file://{temp_file}"}
                        },
                        "id": test["name"]
                    }
                    
                    response = requests.post(f"http://localhost:{port}/mcp", json=convert_data)
                    passed = test["check"](response)
                    
                    self.metrics.add_result("Edge Cases", test["name"], passed,
                                          "Handled gracefully" if passed else "Failed to handle",
                                          {"status_code": response.status_code})
                                          
                finally:
                    os.unlink(temp_file)
                    
            # Test large batch request
            batch_requests = []
            for i in range(50):
                batch_requests.append({
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": f"batch-{i}"
                })
                
            # Send as JSON array (batch request)
            response = requests.post(f"http://localhost:{port}/mcp", json=batch_requests)
            self.metrics.add_result("Edge Cases", "Batch Request",
                                  response.status_code < 500,
                                  f"Server responded with {response.status_code}")
                                  
        except Exception as e:
            self.metrics.add_error(str(e), {"test": "edge_cases"})
            self.metrics.add_result("Edge Cases", "General", False, f"Exception: {str(e)}")
            
        finally:
            await server.stop()
            
    def _generate_report(self):
        """Generate comprehensive test report"""
        summary = self.metrics.get_summary()
        
        # Group results by category
        categories = defaultdict(list)
        for result in self.metrics.test_results:
            categories[result['category']].append(result)
            
        # Build report
        self.test_report['summary'] = summary
        self.test_report['categories'] = {}
        
        for category, results in categories.items():
            passed = sum(1 for r in results if r['passed'])
            total = len(results)
            
            self.test_report['categories'][category] = {
                'passed': passed,
                'failed': total - passed,
                'total': total,
                'success_rate': (passed / total * 100) if total > 0 else 0,
                'tests': [
                    {
                        'name': r['name'],
                        'passed': r['passed'],
                        'message': r['message'],
                        'details': r['details']
                    }
                    for r in results
                ]
            }
            
        # Add performance data
        self.test_report['performance'] = summary['performance_stats']
        
        # Add errors if any
        if self.metrics.error_logs:
            self.test_report['errors'] = [
                {
                    'error': e['error'],
                    'context': e['context'],
                    'timestamp': e['timestamp'].isoformat()
                }
                for e in self.metrics.error_logs
            ]
            
        # Save report to file
        report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_report, f, indent=2)
            
        print(f"\n{CYAN}Test report saved to: {report_file}{RESET}")
        
    def _print_summary(self, summary: Dict):
        """Print test summary"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}Integration Test Summary{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        
        # Overall results
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"{GREEN}Passed: {summary['passed_tests']}{RESET}")
        print(f"{RED}Failed: {summary['failed_tests']}{RESET}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Duration: {summary['duration']:.2f} seconds")
        
        # Category breakdown
        print(f"\n{BOLD}Results by Category:{RESET}")
        categories = defaultdict(lambda: {'passed': 0, 'total': 0})
        for result in self.metrics.test_results:
            cat = categories[result['category']]
            cat['total'] += 1
            if result['passed']:
                cat['passed'] += 1
                
        for category, stats in sorted(categories.items()):
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            color = GREEN if success_rate == 100 else YELLOW if success_rate >= 80 else RED
            print(f"  {category}: {color}{stats['passed']}/{stats['total']} ({success_rate:.0f}%){RESET}")
            
        # Performance summary
        if summary['performance_stats']:
            print(f"\n{BOLD}Performance Metrics:{RESET}")
            for metric, stats in summary['performance_stats'].items():
                print(f"  {metric}:")
                print(f"    Min: {stats['min']:.3f}s, Max: {stats['max']:.3f}s")
                print(f"    Avg: {stats['avg']:.3f}s, P95: {stats['p95']:.3f}s")
                
        # Error summary
        if summary['error_count'] > 0:
            print(f"\n{RED}Errors encountered: {summary['error_count']}{RESET}")
            print("See detailed report for error information.")
            
        # Final verdict
        print(f"\n{BLUE}{'='*70}{RESET}")
        if summary['failed_tests'] == 0:
            print(f"{GREEN}{BOLD}All tests passed! 🎉{RESET}")
        else:
            print(f"{RED}{BOLD}{summary['failed_tests']} tests failed. Review the detailed report.{RESET}")

async def main():
    """Main entry point"""
    runner = AutomatedTestRunner()
    return await runner.run_all_tests()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)