#!/usr/bin/env python3
"""Capture MCP protocol messages to understand the correct format"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters, stdio_client

MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"

class ProtocolCapture:
    def __init__(self, stream):
        self.stream = stream
        self.messages = []
    
    async def read(self, n: int = -1):
        data = await self.stream.read(n)
        if data:
            try:
                # Try to parse as JSON-RPC
                lines = data.decode('utf-8').strip().split('\n')
                for line in lines:
                    if line.startswith('{'):
                        msg = json.loads(line)
                        print(f"<<< Server: {json.dumps(msg, indent=2)}")
                        self.messages.append(('server', msg))
            except:
                pass
        return data
    
    def __getattr__(self, name):
        return getattr(self.stream, name)

class WriteCapture:
    def __init__(self, stream):
        self.stream = stream
        self.messages = []
    
    async def write(self, data):
        if data:
            try:
                # Try to parse as JSON-RPC
                lines = data.decode('utf-8').strip().split('\n')
                for line in lines:
                    if line.startswith('{'):
                        msg = json.loads(line)
                        print(f">>> Client: {json.dumps(msg, indent=2)}")
                        self.messages.append(('client', msg))
            except:
                pass
        return await self.stream.write(data)
    
    def __getattr__(self, name):
        return getattr(self.stream, name)

async def capture_protocol():
    server_params = StdioServerParameters(
        command=MCP_SERVER_BIN
    )
    
    async with stdio_client(server_params) as (read, write):
        # Wrap streams to capture messages
        read_capture = ProtocolCapture(read)
        write_capture = WriteCapture(write)
        
        async with ClientSession(read_capture, write_capture) as session:
            print("=== Initialize ===")
            await session.initialize()
            
            print("\n=== List Tools ===")
            tools = await session.list_tools()
            
            print("\n=== Call Tool ===")
            if tools.tools:
                result = await session.call_tool(
                    "convert_to_markdown",
                    arguments={"uri": "data:text/plain,Hello%20World"}
                )

if __name__ == "__main__":
    asyncio.run(capture_protocol())