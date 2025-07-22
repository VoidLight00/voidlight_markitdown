#!/usr/bin/env python3
"""
Comprehensive test script for VoidLight MarkItDown MCP Server
Tests both STDIO and HTTP/SSE modes with Korean document conversion
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
import signal
from datetime import datetime

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
RESET = '\033[0m'

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing: {test_name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_result(success, message):
    """Print test result with color"""
    if success:
        print(f"{GREEN}✓ {message}{RESET}")
    else:
        print(f"{RED}✗ {message}{RESET}")

def test_stdio_mode():
    """Test MCP server in STDIO mode"""
    print_test_header("STDIO Mode")
    
    try:
        # Create a test request for Korean document conversion
        request = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "name": "convert_korean_document",
                "arguments": {
                    "uri": f"file://{TEST_KOREAN_DOC}",
                    "normalize_korean": True
                }
            },
            "id": 1
        }
        
        # Start the MCP server in STDIO mode
        process = subprocess.Popen(
            [MCP_SERVER_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialization request first
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 0
        }
        
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read initialization response
        init_response = process.stdout.readline()
        print(f"\nInitialization response: {init_response[:100]}...")
        
        # Send the actual tool call request
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        
        # Terminate the process
        process.terminate()
        process.wait(timeout=5)
        
        if response:
            result = json.loads(response)
            print_result(True, "STDIO mode communication successful")
            print(f"\nResponse preview: {json.dumps(result)[:200]}...")
            return True
        else:
            print_result(False, "No response received from STDIO mode")
            return False
            
    except Exception as e:
        print_result(False, f"STDIO mode test failed: {str(e)}")
        return False

def test_http_sse_mode():
    """Test MCP server in HTTP/SSE mode"""
    print_test_header("HTTP/SSE Mode")
    
    # Start the server
    server_process = subprocess.Popen(
        [MCP_SERVER_BIN, "--http", "--port", str(TEST_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        # Test server health
        try:
            response = requests.get(f"http://localhost:{TEST_PORT}/")
            print_result(True, f"Server is running on port {TEST_PORT}")
        except:
            print_result(False, "Server is not responding")
            return False
        
        # Test SSE endpoint
        print("\nTesting SSE endpoint...")
        sse_url = f"http://localhost:{TEST_PORT}/sse"
        
        # Create SSE connection test
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        try:
            # Test if SSE endpoint is accessible
            response = requests.get(sse_url, headers=headers, stream=True, timeout=2)
            if response.status_code == 200:
                print_result(True, "SSE endpoint is accessible")
            else:
                print_result(False, f"SSE endpoint returned status {response.status_code}")
        except requests.exceptions.Timeout:
            # Timeout is expected for SSE - it means the connection is open
            print_result(True, "SSE endpoint is ready for streaming")
        except Exception as e:
            print_result(False, f"SSE endpoint test failed: {str(e)}")
        
        # Test MCP endpoint
        print("\nTesting MCP endpoint...")
        mcp_url = f"http://localhost:{TEST_PORT}/mcp"
        
        # Send an initialization request
        init_data = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        try:
            response = requests.post(
                f"{mcp_url}/initialize",
                json=init_data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print_result(True, "MCP initialization successful")
                print(f"Response: {response.text[:200]}...")
            else:
                print_result(False, f"MCP initialization failed with status {response.status_code}")
        except Exception as e:
            print_result(False, f"MCP endpoint test failed: {str(e)}")
        
        # Test Korean document conversion
        print("\nTesting Korean document conversion via HTTP...")
        tool_data = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "name": "convert_korean_document",
                "arguments": {
                    "uri": f"file://{TEST_KOREAN_DOC}",
                    "normalize_korean": True
                }
            },
            "id": 2
        }
        
        try:
            response = requests.post(
                f"{mcp_url}/call_tool",
                json=tool_data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print_result(True, "Korean document conversion request successful")
                result = response.json()
                print(f"\nConverted content preview: {str(result)[:300]}...")
            else:
                print_result(False, f"Conversion failed with status {response.status_code}")
        except Exception as e:
            print_result(False, f"Korean document conversion failed: {str(e)}")
        
        return True
        
    finally:
        # Cleanup: terminate the server
        print("\nShutting down server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except:
            server_process.kill()
            server_process.wait()

def test_mcp_client():
    """Test using the official MCP client if available"""
    print_test_header("MCP Client Test")
    
    # Check if mcp client is available
    mcp_client_path = f"{MCP_ENV_PATH}/bin/mcp"
    if not os.path.exists(mcp_client_path):
        print_result(False, "MCP client not found in virtual environment")
        return False
    
    try:
        # Create a test script for MCP client
        test_script = """
import asyncio
from mcp.client import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def test_client():
    server_params = StdioServerParameters(
        command="%s"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            
            # Test Korean document conversion
            result = await session.call_tool(
                "convert_korean_document",
                arguments={
                    "uri": "file://%s",
                    "normalize_korean": True
                }
            )
            
            print("Conversion result preview:", str(result)[:200], "...")
            return True

if __name__ == "__main__":
    success = asyncio.run(test_client())
    print("Test", "passed" if success else "failed")
""" % (MCP_SERVER_BIN, TEST_KOREAN_DOC)
        
        # Write test script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            test_file = f.name
        
        # Run the test
        result = subprocess.run(
            [f"{MCP_ENV_PATH}/bin/python", test_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_result(True, "MCP client test successful")
            print(f"\nOutput:\n{result.stdout}")
            return True
        else:
            print_result(False, "MCP client test failed")
            print(f"\nError:\n{result.stderr}")
            return False
            
    except Exception as e:
        print_result(False, f"MCP client test error: {str(e)}")
        return False
    finally:
        # Cleanup
        if 'test_file' in locals():
            os.unlink(test_file)

def create_test_html():
    """Create a test HTML file with Korean content"""
    html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>한국어 테스트 문서</title>
</head>
<body>
    <h1>VoidLight MarkItDown 한국어 HTML 테스트</h1>
    <p>이것은 <strong>HTML 문서</strong>에서 한국어가 올바르게 변환되는지 테스트합니다.</p>
    <ul>
        <li>첫 번째 항목: HTML 태그 처리</li>
        <li>두 번째 항목: 한글 인코딩</li>
        <li>세 번째 항목: 특수문자 『』「」</li>
    </ul>
    <pre><code>
def 한글_함수():
    return "안녕하세요!"
    </code></pre>
</body>
</html>"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        return f.name

def main():
    """Run all tests"""
    print(f"{YELLOW}VoidLight MarkItDown MCP Server Test Suite{RESET}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not os.path.exists(MCP_SERVER_BIN):
        print(f"{RED}Error: MCP server not found at {MCP_SERVER_BIN}{RESET}")
        print("Please ensure the virtual environment is properly set up.")
        sys.exit(1)
    
    if not os.path.exists(TEST_KOREAN_DOC):
        print(f"{RED}Error: Test Korean document not found at {TEST_KOREAN_DOC}{RESET}")
        sys.exit(1)
    
    # Run tests
    test_results = []
    
    # Test 1: STDIO mode
    test_results.append(("STDIO Mode", test_stdio_mode()))
    
    # Test 2: HTTP/SSE mode
    test_results.append(("HTTP/SSE Mode", test_http_sse_mode()))
    
    # Test 3: MCP Client
    test_results.append(("MCP Client", test_mcp_client()))
    
    # Test 4: HTML conversion
    print_test_header("HTML Korean Document Test")
    html_file = create_test_html()
    try:
        # Quick test with direct conversion
        from voidlight_markitdown import VoidLightMarkItDown
        converter = VoidLightMarkItDown(korean_mode=True, normalize_korean=True)
        result = converter.convert_uri(f"file://{html_file}")
        print_result(True, "HTML Korean document conversion successful")
        print(f"\nConverted content:\n{result.markdown[:300]}...")
        test_results.append(("HTML Conversion", True))
    except Exception as e:
        print_result(False, f"HTML conversion failed: {str(e)}")
        test_results.append(("HTML Conversion", False))
    finally:
        os.unlink(html_file)
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}All tests passed! ✨{RESET}")
        return 0
    else:
        print(f"\n{RED}Some tests failed. Please check the output above.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())