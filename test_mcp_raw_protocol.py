#!/usr/bin/env python3
"""Test raw MCP protocol messages"""

import subprocess
import json
import time

MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"

# Start server with stderr redirected to see logs
process = subprocess.Popen(
    [MCP_SERVER_BIN],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

def send_and_receive(request):
    print(f"\n>>> Sending: {json.dumps(request)}")
    process.stdin.write(json.dumps(request) + '\n')
    process.stdin.flush()
    
    # Read multiple lines to handle logs
    for i in range(10):
        line = process.stdout.readline()
        if line:
            line = line.strip()
            if line.startswith('{'):
                try:
                    response = json.loads(line)
                    print(f"<<< Response: {json.dumps(response, indent=2)}")
                    return response
                except json.JSONDecodeError:
                    print(f"<<< Non-JSON: {line}")
            else:
                print(f"<<< Log: {line}")
    return None

# Test sequence based on MCP specification
# 1. Initialize
init_response = send_and_receive({
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    },
    "id": 1
})

# 2. Send initialized notification (required by protocol)
send_and_receive({
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
    "params": {}
})

# 3. List tools - the correct method name according to MCP spec
tools_response = send_and_receive({
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
})

# 4. Call a tool
if tools_response and "result" in tools_response:
    call_response = send_and_receive({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "convert_to_markdown",
            "arguments": {
                "uri": "data:text/plain,Hello%20World"
            }
        },
        "id": 3
    })

# Check stderr for any errors
import select
ready = select.select([process.stderr], [], [], 0.1)
if ready[0]:
    stderr = process.stderr.read()
    if stderr:
        print(f"\n=== Server errors ===\n{stderr}")

# Cleanup
process.terminate()
process.wait()