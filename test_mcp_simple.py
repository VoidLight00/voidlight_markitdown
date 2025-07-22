#!/usr/bin/env python3
"""Simple test to debug MCP server communication"""

import subprocess
import json
import sys

MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"

# Start server
process = subprocess.Popen(
    [MCP_SERVER_BIN],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=0  # Unbuffered
)

# Send initialize request
init_request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "debug-client",
            "version": "1.0.0"
        }
    },
    "id": 1
}

print("Sending:", json.dumps(init_request))
process.stdin.write(json.dumps(init_request) + '\n')
process.stdin.flush()

# Read response
print("\nReading stdout...")
for i in range(5):  # Read up to 5 lines
    line = process.stdout.readline()
    if line:
        print(f"Line {i+1}: {repr(line)}")
        try:
            parsed = json.loads(line.strip())
            print(f"Parsed JSON: {json.dumps(parsed, indent=2)}")
            break
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
    else:
        print(f"Line {i+1}: (empty)")
        break

# Check stderr
print("\nChecking stderr...")
import select
ready = select.select([process.stderr], [], [], 0.1)
if ready[0]:
    stderr_lines = process.stderr.read()
    print("Stderr:", stderr_lines)

# Cleanup
process.terminate()
process.wait()