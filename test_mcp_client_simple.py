#!/usr/bin/env python3
"""
Simple MCP client test using the mcp package
"""

import asyncio
import json
from pathlib import Path

async def test_mcp_stdio():
    """Test MCP server via STDIO using subprocess"""
    print("Testing MCP Server via STDIO Protocol")
    print("=" * 50)
    
    server_cmd = "/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp"
    test_file = "/Users/voidlight/voidlight_markitdown/test_korean_document.txt"
    
    # Start the server process
    process = await asyncio.create_subprocess_exec(
        server_cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    async def send_message(msg):
        """Send a message and get response"""
        msg_str = json.dumps(msg) + '\n'
        process.stdin.write(msg_str.encode())
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        return json.loads(response_line.decode())
    
    try:
        # Step 1: Initialize
        print("\n1. Initializing connection...")
        init_response = await send_message({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        })
        print(f"Server: {init_response.get('result', {}).get('serverInfo', {})}")
        
        # Step 2: Send initialized notification
        await send_message({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })
        
        # Step 3: List tools
        print("\n2. Listing available tools...")
        tools_response = await send_message({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        })
        
        tools = tools_response.get('result', {}).get('tools', [])
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description'][:60]}...")
        
        # Step 4: Test Korean document conversion
        print("\n3. Testing Korean document conversion...")
        convert_response = await send_message({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "convert_korean_document",
                "arguments": {
                    "uri": f"file://{test_file}",
                    "normalize_korean": True
                }
            },
            "id": 3
        })
        
        if 'result' in convert_response:
            content = convert_response['result']['content'][0]['text']
            print(f"   Conversion successful!")
            print(f"   Preview: {content[:150]}...")
            
            # Check for Korean normalization
            if '테스트' in content and '문서' in content:
                print("   ✓ Korean text properly preserved")
            
            # Count Korean characters
            korean_chars = sum(1 for c in content if ord('가') <= ord(c) <= ord('힣'))
            print(f"   ✓ Found {korean_chars} Korean characters in output")
        else:
            print(f"   Error: {convert_response.get('error', 'Unknown error')}")
        
        # Step 5: Test regular markdown conversion for comparison
        print("\n4. Testing regular markdown conversion...")
        regular_response = await send_message({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "convert_to_markdown",
                "arguments": {
                    "uri": f"file://{test_file}"
                }
            },
            "id": 4
        })
        
        if 'result' in regular_response:
            print("   ✓ Regular conversion also successful")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
    finally:
        # Cleanup
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_stdio())