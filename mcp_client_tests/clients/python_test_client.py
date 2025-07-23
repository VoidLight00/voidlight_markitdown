#!/usr/bin/env python3
"""
Python MCP Test Client for voidlight_markitdown
Tests STDIO and HTTP/SSE connections with comprehensive protocol validation
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_client_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a single test"""
    test_name: str
    passed: bool
    duration: float
    details: Dict[str, Any]
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'test_name': self.test_name,
            'passed': self.passed,
            'duration': self.duration,
            'details': self.details,
            'error': self.error,
            'timestamp': datetime.now().isoformat()
        }


class MCPTestClient:
    """Comprehensive MCP test client for voidlight_markitdown"""
    
    def __init__(self, report_dir: Path):
        self.report_dir = report_dir
        self.test_results: List[TestResult] = []
        self.session: Optional[ClientSession] = None
        
    async def test_stdio_connection(self) -> TestResult:
        """Test STDIO mode connection"""
        start_time = time.time()
        test_name = "STDIO Connection Test"
        
        try:
            logger.info("Testing STDIO connection...")
            
            # Start the server
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "voidlight_markitdown_mcp"],
                env={
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "DEBUG"
                }
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    
                    # Initialize connection
                    await session.initialize()
                    
                    # Get server info
                    server_info = {
                        'name': session.server_info.name if hasattr(session, 'server_info') else 'Unknown',
                        'version': session.server_info.version if hasattr(session, 'server_info') else 'Unknown'
                    }
                    
                    # List available tools
                    tools_result = await session.list_tools()
                    tools = [tool.model_dump() for tool in tools_result.tools]
                    
                    duration = time.time() - start_time
                    
                    return TestResult(
                        test_name=test_name,
                        passed=True,
                        duration=duration,
                        details={
                            'server_info': server_info,
                            'tools_count': len(tools),
                            'tools': tools,
                            'connection_type': 'stdio'
                        }
                    )
                    
        except Exception as e:
            logger.error(f"STDIO connection test failed: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration=time.time() - start_time,
                details={'connection_type': 'stdio'},
                error=str(e)
            )
    
    async def test_http_sse_connection(self) -> TestResult:
        """Test HTTP/SSE mode connection"""
        start_time = time.time()
        test_name = "HTTP/SSE Connection Test"
        
        try:
            logger.info("Testing HTTP/SSE connection...")
            
            # Start the HTTP server in a subprocess
            server_process = subprocess.Popen(
                ["python", "-m", "voidlight_markitdown_mcp", "--http", "--port", "3001"],
                env={
                    **dict(os.environ),
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "DEBUG"
                }
            )
            
            # Wait for server to start
            await asyncio.sleep(2)
            
            try:
                # Test HTTP endpoint
                async with httpx.AsyncClient() as client:
                    # Test server health
                    response = await client.get("http://localhost:3001/")
                    health_status = response.status_code
                    
                    # Test MCP endpoint
                    mcp_response = await client.post(
                        "http://localhost:3001/mcp",
                        json={
                            "jsonrpc": "2.0",
                            "method": "tools/list",
                            "id": 1
                        }
                    )
                    
                    mcp_data = mcp_response.json() if mcp_response.status_code == 200 else {}
                    
                    duration = time.time() - start_time
                    
                    return TestResult(
                        test_name=test_name,
                        passed=health_status < 500,
                        duration=duration,
                        details={
                            'health_status': health_status,
                            'mcp_response_status': mcp_response.status_code,
                            'mcp_data': mcp_data,
                            'connection_type': 'http_sse'
                        }
                    )
                    
            finally:
                # Clean up server process
                server_process.terminate()
                server_process.wait()
                
        except Exception as e:
            logger.error(f"HTTP/SSE connection test failed: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration=time.time() - start_time,
                details={'connection_type': 'http_sse'},
                error=str(e)
            )
    
    async def test_tool_invocation(self, tool_name: str, params: Dict[str, Any]) -> TestResult:
        """Test specific tool invocation"""
        start_time = time.time()
        test_name = f"Tool Invocation: {tool_name}"
        
        try:
            logger.info(f"Testing tool invocation: {tool_name}")
            
            if not self.session:
                # Create a new session for this test
                server_params = StdioServerParameters(
                    command="python",
                    args=["-m", "voidlight_markitdown_mcp"],
                    env={
                        "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                        "VOIDLIGHT_LOG_LEVEL": "DEBUG"
                    }
                )
                
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        # Call the tool
                        result = await session.call_tool(tool_name, params)
                        
                        duration = time.time() - start_time
                        
                        return TestResult(
                            test_name=test_name,
                            passed=True,
                            duration=duration,
                            details={
                                'tool_name': tool_name,
                                'params': params,
                                'result': result.model_dump() if hasattr(result, 'model_dump') else str(result)
                            }
                        )
            else:
                # Use existing session
                result = await self.session.call_tool(tool_name, params)
                
                duration = time.time() - start_time
                
                return TestResult(
                    test_name=test_name,
                    passed=True,
                    duration=duration,
                    details={
                        'tool_name': tool_name,
                        'params': params,
                        'result': result.model_dump() if hasattr(result, 'model_dump') else str(result)
                    }
                )
                
        except Exception as e:
            logger.error(f"Tool invocation test failed: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration=time.time() - start_time,
                details={
                    'tool_name': tool_name,
                    'params': params
                },
                error=str(e)
            )
    
    async def test_korean_text_processing(self) -> TestResult:
        """Test Korean text processing capabilities"""
        start_time = time.time()
        test_name = "Korean Text Processing"
        
        try:
            logger.info("Testing Korean text processing...")
            
            # Create test file with Korean content
            test_file = self.report_dir.parent / "test_files" / "korean_test.txt"
            test_file.parent.mkdir(exist_ok=True)
            
            korean_text = """안녕하세요! 한국어 문서 테스트입니다.
            
# 제목 1
이것은 **굵은 글씨**이고 이것은 *기울임 글씨*입니다.

## 제목 2
- 첫 번째 항목
- 두 번째 항목
- 세 번째 항목

### 코드 예제
```python
def 인사하기(이름):
    return f"안녕하세요, {이름}님!"
```

[링크 텍스트](https://example.com)
"""
            
            test_file.write_text(korean_text, encoding='utf-8')
            
            # Test conversion
            file_uri = f"file://{test_file.absolute()}"
            
            result = await self.test_tool_invocation(
                "convert_korean_document",
                {
                    "uri": file_uri,
                    "normalize_korean": True
                }
            )
            
            # Additional validation for Korean content
            if result.passed and result.details.get('result'):
                converted_text = result.details['result']
                korean_preserved = all(char in converted_text for char in ['안녕하세요', '한국어', '제목'])
                
                result.details['korean_validation'] = {
                    'korean_preserved': korean_preserved,
                    'original_length': len(korean_text),
                    'converted_length': len(converted_text) if isinstance(converted_text, str) else 0
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Korean text processing test failed: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def test_concurrent_requests(self, num_requests: int = 5) -> TestResult:
        """Test concurrent request handling"""
        start_time = time.time()
        test_name = f"Concurrent Requests ({num_requests})"
        
        try:
            logger.info(f"Testing {num_requests} concurrent requests...")
            
            # Create test URIs
            test_uris = [
                "https://example.com",
                "https://www.python.org",
                "https://github.com",
                "https://docs.python.org",
                "https://pypi.org"
            ][:num_requests]
            
            # Create concurrent tasks
            tasks = []
            for i, uri in enumerate(test_uris):
                task = self.test_tool_invocation(
                    "convert_to_markdown",
                    {"uri": uri}
                )
                tasks.append(task)
            
            # Execute concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successful = sum(1 for r in results if isinstance(r, TestResult) and r.passed)
            failed = sum(1 for r in results if isinstance(r, TestResult) and not r.passed)
            errors = sum(1 for r in results if isinstance(r, Exception))
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name=test_name,
                passed=successful == num_requests,
                duration=duration,
                details={
                    'total_requests': num_requests,
                    'successful': successful,
                    'failed': failed,
                    'errors': errors,
                    'avg_time_per_request': duration / num_requests
                }
            )
            
        except Exception as e:
            logger.error(f"Concurrent requests test failed: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration=time.time() - start_time,
                details={'num_requests': num_requests},
                error=str(e)
            )
    
    async def test_error_handling(self) -> TestResult:
        """Test error handling and recovery"""
        start_time = time.time()
        test_name = "Error Handling"
        
        try:
            logger.info("Testing error handling...")
            
            error_cases = []
            
            # Test 1: Invalid URI
            result1 = await self.test_tool_invocation(
                "convert_to_markdown",
                {"uri": "invalid://not-a-real-uri"}
            )
            error_cases.append({
                'case': 'Invalid URI',
                'handled_gracefully': not result1.passed and result1.error is not None
            })
            
            # Test 2: Missing required parameter
            try:
                result2 = await self.test_tool_invocation(
                    "convert_to_markdown",
                    {}  # Missing 'uri' parameter
                )
                error_cases.append({
                    'case': 'Missing Parameter',
                    'handled_gracefully': not result2.passed
                })
            except:
                error_cases.append({
                    'case': 'Missing Parameter',
                    'handled_gracefully': True
                })
            
            # Test 3: Invalid tool name
            result3 = await self.test_tool_invocation(
                "non_existent_tool",
                {"param": "value"}
            )
            error_cases.append({
                'case': 'Invalid Tool Name',
                'handled_gracefully': not result3.passed
            })
            
            # All error cases should be handled gracefully
            all_handled = all(case['handled_gracefully'] for case in error_cases)
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name=test_name,
                passed=all_handled,
                duration=duration,
                details={
                    'error_cases': error_cases,
                    'total_cases': len(error_cases),
                    'handled_gracefully': sum(1 for case in error_cases if case['handled_gracefully'])
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        logger.info("Starting comprehensive MCP client tests...")
        
        # Test suites
        test_suites = [
            ("Connection Tests", [
                self.test_stdio_connection(),
                self.test_http_sse_connection()
            ]),
            ("Tool Tests", [
                self.test_tool_invocation(
                    "convert_to_markdown",
                    {"uri": "https://example.com"}
                ),
                self.test_korean_text_processing()
            ]),
            ("Stress Tests", [
                self.test_concurrent_requests(5),
                self.test_error_handling()
            ])
        ]
        
        all_results = []
        suite_summaries = []
        
        for suite_name, tests in test_suites:
            logger.info(f"\nRunning {suite_name}...")
            suite_results = []
            
            for test in tests:
                result = await test
                suite_results.append(result)
                all_results.append(result)
                self.test_results.append(result)
                
                # Log result
                status = "PASSED" if result.passed else "FAILED"
                logger.info(f"  {result.test_name}: {status} ({result.duration:.2f}s)")
                if result.error:
                    logger.error(f"    Error: {result.error}")
            
            # Suite summary
            passed = sum(1 for r in suite_results if r.passed)
            total = len(suite_results)
            suite_summaries.append({
                'suite': suite_name,
                'passed': passed,
                'total': total,
                'success_rate': (passed / total * 100) if total > 0 else 0
            })
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(all_results),
                'passed': sum(1 for r in all_results if r.passed),
                'failed': sum(1 for r in all_results if not r.passed),
                'total_duration': sum(r.duration for r in all_results),
                'success_rate': (sum(1 for r in all_results if r.passed) / len(all_results) * 100) if all_results else 0
            },
            'suite_summaries': suite_summaries,
            'test_results': [r.to_dict() for r in all_results]
        }
        
        # Save report
        report_file = self.report_dir / f"python_client_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.write_text(json.dumps(report, indent=2))
        logger.info(f"\nTest report saved to: {report_file}")
        
        return report


async def main():
    """Main test runner"""
    report_dir = Path("/Users/voidlight/voidlight_markitdown/mcp_client_tests/reports")
    report_dir.mkdir(exist_ok=True)
    
    client = MCPTestClient(report_dir)
    report = await client.run_all_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("MCP CLIENT TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Total Duration: {report['summary']['total_duration']:.2f}s")
    print("="*60)


if __name__ == "__main__":
    import os
    asyncio.run(main())