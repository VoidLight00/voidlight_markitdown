#!/usr/bin/env python3
"""
Fixed SSE test for VoidLight MarkItDown MCP Server
Properly handles SSE session management
"""

import json
import asyncio
import aiohttp
import sys
import time
from aiohttp_sse_client import client as sse_client

# Configuration
MCP_SERVER_BIN = "/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp"
TEST_KOREAN_DOC = "/Users/voidlight/voidlight_markitdown/test_korean_document.txt"
TEST_PORT = 3003

async def test_sse_with_session():
    """Test SSE with proper session handling"""
    print("\n=== Testing SSE with Session Management ===")
    
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
            # Step 1: Connect to SSE endpoint
            sse_url = f"http://localhost:{TEST_PORT}/sse"
            print(f"Connecting to SSE endpoint: {sse_url}")
            
            # Create SSE connection
            headers = {'Accept': 'text/event-stream'}
            
            # Use a separate task to handle SSE events
            sse_task = None
            session_id = None
            
            async def handle_sse_events():
                nonlocal session_id
                async with sse_client.EventSource(
                    sse_url,
                    headers=headers,
                    session=session
                ) as event_source:
                    async for event in event_source:
                        print(f"SSE Event: {event}")
                        # Extract session ID if provided
                        if event.type == 'session':
                            session_id = event.data
                            print(f"Got session ID: {session_id}")
            
            # Start SSE handler in background
            sse_task = asyncio.create_task(handle_sse_events())
            
            # Give SSE connection time to establish
            await asyncio.sleep(1)
            
            # Step 2: Send initialization message
            init_msg = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
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
            
            # Include session ID in headers if we have one
            post_headers = {'Content-Type': 'application/json'}
            if session_id:
                post_headers['Mcp-Session-Id'] = session_id
            
            messages_url = f"http://localhost:{TEST_PORT}/messages/"
            print(f"Sending init to: {messages_url}")
            
            async with session.post(
                messages_url, 
                json=init_msg,
                headers=post_headers
            ) as response:
                print(f"Init response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print(f"Init result: {json.dumps(result, indent=2)}")
                    
                    # Step 3: Send initialized notification
                    initialized_msg = {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized"
                    }
                    
                    async with session.post(
                        messages_url,
                        json=initialized_msg,
                        headers=post_headers
                    ) as notify_response:
                        print(f"Initialized notification status: {notify_response.status}")
                    
                    # Step 4: List tools
                    list_tools_msg = {
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "id": 2
                    }
                    
                    async with session.post(
                        messages_url,
                        json=list_tools_msg,
                        headers=post_headers
                    ) as tools_response:
                        if tools_response.status == 200:
                            tools_result = await tools_response.json()
                            print(f"Available tools: {json.dumps(tools_result, indent=2)}")
                            
                            # Step 5: Call Korean document conversion
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
                            
                            async with session.post(
                                messages_url,
                                json=call_tool_msg,
                                headers=post_headers
                            ) as call_response:
                                if call_response.status == 200:
                                    call_result = await call_response.json()
                                    print(f"Conversion result: {json.dumps(call_result, indent=2)[:500]}...")
                                    print("✓ SSE communication successful")
                                    return True
                                else:
                                    print(f"✗ Tool call failed with status {call_response.status}")
                                    body = await call_response.text()
                                    print(f"Error body: {body}")
                        else:
                            print(f"✗ List tools failed with status {tools_response.status}")
                            body = await tools_response.text()
                            print(f"Error body: {body}")
                else:
                    print(f"✗ Init failed with status {response.status}")
                    body = await response.text()
                    print(f"Error body: {body}")
                    return False
            
            # Cancel SSE task
            if sse_task:
                sse_task.cancel()
                try:
                    await sse_task
                except asyncio.CancelledError:
                    pass
                    
    finally:
        process.terminate()
        await process.wait()
    
    return False

async def test_streamable_http():
    """Test the newer Streamable HTTP endpoint"""
    print("\n=== Testing Streamable HTTP ===")
    
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
            # The MCP endpoint handles everything
            mcp_url = f"http://localhost:{TEST_PORT}/mcp"
            
            # Send initialization
            init_msg = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
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
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            async with session.post(mcp_url, json=init_msg, headers=headers) as response:
                print(f"Init response status: {response.status}")
                session_id = response.headers.get('Mcp-Session-Id')
                if session_id:
                    print(f"Got session ID: {session_id}")
                    headers['Mcp-Session-Id'] = session_id
                
                if response.status == 200:
                    result = await response.json()
                    print(f"Init result: {json.dumps(result, indent=2)}")
                    
                    # List tools
                    list_tools_msg = {
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "id": 2
                    }
                    
                    async with session.post(mcp_url, json=list_tools_msg, headers=headers) as tools_response:
                        if tools_response.status == 200:
                            tools_result = await tools_response.json()
                            print(f"Available tools: {json.dumps(tools_result, indent=2)}")
                            
                            # Call tool
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
                            
                            async with session.post(mcp_url, json=call_tool_msg, headers=headers) as call_response:
                                if call_response.status == 200:
                                    call_result = await call_response.json()
                                    print(f"Conversion result: {json.dumps(call_result, indent=2)[:500]}...")
                                    print("✓ Streamable HTTP communication successful")
                                    return True
                                else:
                                    print(f"✗ Tool call failed with status {call_response.status}")
                        else:
                            print(f"✗ List tools failed with status {tools_response.status}")
                else:
                    print(f"✗ Init failed with status {response.status}")
                    body = await response.text()
                    print(f"Error body: {body}")
                    
    finally:
        process.terminate()
        await process.wait()
    
    return False

async def main():
    """Run HTTP/SSE tests"""
    print("VoidLight MarkItDown MCP HTTP/SSE Test (Fixed)")
    print("=" * 50)
    
    results = []
    
    # Test 1: SSE with proper session handling
    # Note: This requires aiohttp-sse-client, skip if not available
    try:
        import aiohttp_sse_client
        results.append(("SSE with Session", await test_sse_with_session()))
    except ImportError:
        print("Skipping SSE test - aiohttp-sse-client not installed")
        print("Install with: pip install aiohttp-sse-client")
    
    # Test 2: Streamable HTTP
    results.append(("Streamable HTTP", await test_streamable_http()))
    
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