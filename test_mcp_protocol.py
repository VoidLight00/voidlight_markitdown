#!/usr/bin/env python3
"""
Direct MCP protocol test for VoidLight MarkItDown server
"""

import json
import subprocess
import asyncio
import aiohttp
import sys
import time
from pathlib import Path

# Configuration
MCP_SERVER_BIN = "/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp"
TEST_KOREAN_DOC = "/Users/voidlight/voidlight_markitdown/test_korean_document.txt"
TEST_PORT = 3002

async def test_stdio_protocol():
    """Test STDIO protocol directly"""
    print("\n=== Testing STDIO Protocol ===")
    
    # Start server process
    process = await asyncio.create_subprocess_exec(
        MCP_SERVER_BIN,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Send initialization
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0.0",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        process.stdin.write((json.dumps(init_msg) + '\n').encode())
        await process.stdin.drain()
        
        # Read response
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode())
        print(f"Init response: {response}")
        
        if 'result' in response:
            print("✓ Initialization successful")
            
            # Send initialized notification
            initialized_msg = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write((json.dumps(initialized_msg) + '\n').encode())
            await process.stdin.drain()
            
            # List tools
            list_tools_msg = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 2
            }
            process.stdin.write((json.dumps(list_tools_msg) + '\n').encode())
            await process.stdin.drain()
            
            # Read tools response
            tools_line = await process.stdout.readline()
            tools_response = json.loads(tools_line.decode())
            print(f"\nAvailable tools: {json.dumps(tools_response, indent=2)}")
            
            # Call Korean document conversion tool
            if 'result' in tools_response:
                call_tool_msg = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "convert_korean_document",
                        "arguments": {
                            "uri": f"file://{TEST_KOREAN_DOC}",
                            "normalize_korean": True
                        }
                    },
                    "id": 3
                }
                process.stdin.write((json.dumps(call_tool_msg) + '\n').encode())
                await process.stdin.drain()
                
                # Read conversion result
                result_line = await process.stdout.readline()
                result = json.loads(result_line.decode())
                print(f"\nConversion result: {json.dumps(result, indent=2)[:500]}...")
                
                if 'result' in result:
                    print("✓ Korean document conversion successful")
                    return True
                else:
                    print("✗ Korean document conversion failed")
                    return False
        else:
            print("✗ Initialization failed")
            return False
            
    finally:
        process.terminate()
        await process.wait()

async def test_http_sse_protocol():
    """Test HTTP/SSE protocol"""
    print("\n=== Testing HTTP/SSE Protocol ===")
    
    # Start server
    process = await asyncio.create_subprocess_exec(
        MCP_SERVER_BIN, "--http", "--port", str(TEST_PORT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        await asyncio.sleep(2)
        
        async with aiohttp.ClientSession() as session:
            # Test SSE endpoint
            print("\nTesting SSE endpoint...")
            url = f"http://localhost:{TEST_PORT}/sse"
            
            # Create SSE connection
            async with session.get(url, headers={'Accept': 'text/event-stream'}) as response:
                if response.status == 200:
                    print("✓ SSE endpoint connected")
                    
                    # Send initialization via POST to messages endpoint
                    init_msg = {
                        "jsonrpc": "2.0",
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "1.0.0",
                            "capabilities": {
                                "tools": {}
                            },
                            "clientInfo": {
                                "name": "test-client",
                                "version": "1.0.0"
                            }
                        },
                        "id": 1
                    }
                    
                    messages_url = f"http://localhost:{TEST_PORT}/messages/"
                    async with session.post(messages_url, json=init_msg) as init_response:
                        if init_response.status == 200:
                            result = await init_response.json()
                            print(f"Init response: {result}")
                            print("✓ HTTP/SSE communication successful")
                            return True
                        else:
                            print(f"✗ Init failed with status {init_response.status}")
                            return False
                else:
                    print(f"✗ SSE connection failed with status {response.status}")
                    return False
                    
    finally:
        process.terminate()
        await process.wait()

async def test_direct_conversion():
    """Test direct conversion using the library"""
    print("\n=== Testing Direct Library Conversion ===")
    
    try:
        from voidlight_markitdown import VoidLightMarkItDown
        
        # Test 1: Basic conversion
        converter = VoidLightMarkItDown(enable_plugins=False)
        result = converter.convert_uri(f"file://{TEST_KOREAN_DOC}")
        print(f"Basic conversion preview: {result.markdown[:200]}...")
        print("✓ Basic conversion successful")
        
        # Test 2: Korean mode conversion
        korean_converter = VoidLightMarkItDown(
            korean_mode=True,
            normalize_korean=True,
            enable_plugins=False
        )
        korean_result = korean_converter.convert_uri(f"file://{TEST_KOREAN_DOC}")
        print(f"\nKorean mode conversion preview: {korean_result.markdown[:200]}...")
        print("✓ Korean mode conversion successful")
        
        # Compare results
        if korean_result.markdown != result.markdown:
            print("✓ Korean normalization is working (results differ)")
        else:
            print("⚠ Korean normalization might not be applied (results are identical)")
            
        return True
        
    except Exception as e:
        print(f"✗ Direct conversion failed: {str(e)}")
        return False

async def main():
    """Run all protocol tests"""
    print("VoidLight MarkItDown MCP Protocol Test")
    print("=" * 50)
    
    results = []
    
    # Test 1: STDIO Protocol
    results.append(("STDIO Protocol", await test_stdio_protocol()))
    
    # Test 2: HTTP/SSE Protocol
    results.append(("HTTP/SSE Protocol", await test_http_sse_protocol()))
    
    # Test 3: Direct Library
    results.append(("Direct Library", await test_direct_conversion()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))