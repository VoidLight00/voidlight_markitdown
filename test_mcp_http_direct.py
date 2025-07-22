#!/usr/bin/env python3
"""
Direct HTTP test for VoidLight MarkItDown MCP Server
Tests the Streamable HTTP endpoint directly
"""

import json
import asyncio
import aiohttp
import sys
import time

# Configuration
MCP_SERVER_BIN = "/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp"
TEST_KOREAN_DOC = "/Users/voidlight/voidlight_markitdown/test_korean_document.txt"
TEST_PORT = 3004

async def test_streamable_http_direct():
    """Test Streamable HTTP with direct JSON-RPC calls"""
    print("\n=== Testing Streamable HTTP Direct ===")
    
    # Start server
    process = await asyncio.create_subprocess_exec(
        MCP_SERVER_BIN, "--http", "--port", str(TEST_PORT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        print("Waiting for server to start...")
        await asyncio.sleep(3)
        
        async with aiohttp.ClientSession() as session:
            # Test different endpoints
            base_url = f"http://localhost:{TEST_PORT}"
            
            # First, check if server is running
            try:
                async with session.get(base_url) as response:
                    print(f"Server status check: {response.status}")
            except Exception as e:
                print(f"Server check error: {e}")
            
            # Test the /mcp endpoint
            mcp_url = f"{base_url}/mcp"
            
            # Initialize request
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
            
            print(f"\nSending initialize request to: {mcp_url}")
            print(f"Request: {json.dumps(init_request, indent=2)}")
            
            try:
                async with session.post(mcp_url, json=init_request, headers=headers) as response:
                    print(f"Response status: {response.status}")
                    print(f"Response headers: {dict(response.headers)}")
                    
                    # Get session ID if provided
                    session_id = response.headers.get('Mcp-Session-Id')
                    if session_id:
                        print(f"Session ID: {session_id}")
                        headers['Mcp-Session-Id'] = session_id
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"Initialize result: {json.dumps(result, indent=2)}")
                        
                        # Now list tools
                        list_request = {
                            "jsonrpc": "2.0",
                            "method": "tools/list",
                            "params": {},
                            "id": 2
                        }
                        
                        print(f"\nSending tools/list request")
                        async with session.post(mcp_url, json=list_request, headers=headers) as tools_response:
                            print(f"Tools response status: {tools_response.status}")
                            
                            if tools_response.status == 200:
                                tools_result = await tools_response.json()
                                print(f"Tools result: {json.dumps(tools_result, indent=2)}")
                                
                                # Call Korean document conversion
                                call_request = {
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
                                
                                print(f"\nSending tools/call request")
                                async with session.post(mcp_url, json=call_request, headers=headers) as call_response:
                                    print(f"Call response status: {call_response.status}")
                                    
                                    if call_response.status == 200:
                                        call_result = await call_response.json()
                                        print(f"Call result: {json.dumps(call_result, indent=2)[:500]}...")
                                        print("\n✓ HTTP test successful!")
                                        return True
                                    else:
                                        error_text = await call_response.text()
                                        print(f"Call error: {error_text}")
                            else:
                                error_text = await tools_response.text()
                                print(f"Tools list error: {error_text}")
                    else:
                        error_text = await response.text()
                        print(f"Initialize error: {error_text}")
                        
            except aiohttp.ClientError as e:
                print(f"HTTP request error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
                import traceback
                traceback.print_exc()
                
    finally:
        print("\nShutting down server...")
        process.terminate()
        await process.wait()
    
    return False

async def main():
    """Run the test"""
    print("VoidLight MarkItDown MCP HTTP Direct Test")
    print("=" * 50)
    
    success = await test_streamable_http_direct()
    
    if success:
        print(f"\n✓ Test PASSED")
        return 0
    else:
        print(f"\n✗ Test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))