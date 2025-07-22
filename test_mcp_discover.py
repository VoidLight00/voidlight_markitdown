#!/usr/bin/env python3
"""Discover MCP protocol methods"""

import asyncio
from mcp import ClientSession, StdioServerParameters, stdio_client

MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"

async def discover_methods():
    server_params = StdioServerParameters(
        command=MCP_SERVER_BIN
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            print("Initializing session...")
            await session.initialize()
            print("✓ Session initialized")
            
            # List available tools
            print("\nListing tools...")
            tools = await session.list_tools()
            print(f"✓ Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
                if hasattr(tool, 'inputSchema'):
                    print(f"    Input schema: {tool.inputSchema}")
            
            # Test a tool call
            if tools.tools:
                print("\nTesting tool call...")
                test_tool = tools.tools[0]
                print(f"Calling tool: {test_tool.name}")
                
                # Create test arguments based on the tool
                if test_tool.name == "convert_to_markdown":
                    args = {"uri": "data:text/plain,Hello%20World"}
                elif test_tool.name == "convert_korean_document":
                    args = {"uri": "data:text/plain,Hello%20World", "normalize_korean": True}
                else:
                    args = {}
                
                try:
                    result = await session.call_tool(test_tool.name, arguments=args)
                    print(f"✓ Tool call successful")
                    print(f"  Result type: {type(result)}")
                    print(f"  Result: {str(result)[:200]}...")
                except Exception as e:
                    print(f"✗ Tool call failed: {e}")

if __name__ == "__main__":
    asyncio.run(discover_methods())