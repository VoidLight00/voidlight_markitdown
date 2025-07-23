# MCP Client Troubleshooting Guide

This guide helps diagnose and resolve common issues when connecting MCP clients to the voidlight_markitdown server.

## Table of Contents
- [Common Issues](#common-issues)
- [Client-Specific Issues](#client-specific-issues)
- [Debugging Tools](#debugging-tools)
- [Protocol Issues](#protocol-issues)
- [Performance Issues](#performance-issues)
- [Korean Text Issues](#korean-text-issues)

## Common Issues

### 1. Server Not Starting

**Symptoms:**
- Client cannot connect
- "Connection refused" errors
- No server process visible

**Solutions:**
```bash
# Check if the module is installed
python -m voidlight_markitdown_mcp --help

# If not installed, install it
cd packages/voidlight_markitdown-mcp
pip install -e .

# Check Python path
python -c "import voidlight_markitdown_mcp; print(voidlight_markitdown_mcp.__file__)"
```

### 2. Connection Timeouts

**Symptoms:**
- Client connects but times out during initialization
- Slow response times
- Intermittent failures

**Solutions:**
```bash
# Enable debug logging
export VOIDLIGHT_LOG_LEVEL=DEBUG
export VOIDLIGHT_LOG_FILE=./mcp_debug.log

# Run server with extended timeout
python -m voidlight_markitdown_mcp --timeout 30000
```

### 3. Tool Not Found Errors

**Symptoms:**
- "Method not found" errors
- Tools not listed
- Tool invocation fails

**Debug Steps:**
```python
# Test tool listing directly
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_tools():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "voidlight_markitdown_mcp"],
        env={"VOIDLIGHT_LOG_LEVEL": "DEBUG"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

asyncio.run(test_tools())
```

## Client-Specific Issues

### Claude Desktop App

**Configuration Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Common Issues:**

1. **Path Issues on Windows:**
```json
{
  "mcpServers": {
    "voidlight-markitdown": {
      "type": "stdio",
      "command": "C:\\Python39\\python.exe",
      "args": ["-m", "voidlight_markitdown_mcp"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\voidlight_markitdown\\packages"
      }
    }
  }
}
```

2. **Virtual Environment Issues:**
```json
{
  "mcpServers": {
    "voidlight-markitdown": {
      "type": "stdio",
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "voidlight_markitdown_mcp"]
    }
  }
}
```

### VSCode MCP Extension

**Common Issues:**

1. **Extension Not Finding Server:**
   - Check VSCode settings: `Cmd+,` → Search "mcp"
   - Ensure extension is installed: `code --install-extension <mcp-extension-id>`

2. **Workspace Settings:**
```json
// .vscode/settings.json
{
  "mcp.servers": {
    "voidlight-markitdown": {
      "type": "stdio",
      "command": "${workspaceFolder}/venv/bin/python",
      "args": ["-m", "voidlight_markitdown_mcp"]
    }
  }
}
```

### Custom MCP Clients

**Connection Examples:**

1. **Python Client Connection Issues:**
```python
# Debug connection with detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add connection retry logic
async def connect_with_retry(max_attempts=3):
    for attempt in range(max_attempts):
        try:
            # Your connection code here
            break
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

2. **Node.js Client Issues:**
```javascript
// Enable debug mode
process.env.DEBUG = 'mcp:*';

// Handle connection errors
client.on('error', (error) => {
  console.error('MCP Client Error:', error);
});
```

## Debugging Tools

### 1. Protocol Trace Capture

Create a debug wrapper script:

```python
#!/usr/bin/env python3
# debug_wrapper.py
import sys
import json
from datetime import datetime

log_file = open('mcp_protocol_trace.log', 'a')

def log_message(direction, data):
    log_file.write(f"{datetime.now().isoformat()} {direction}: {data}\n")
    log_file.flush()

# Wrap stdin/stdout for protocol tracing
# ... (implementation details)
```

### 2. Health Check Script

```bash
#!/bin/bash
# mcp_health_check.sh

echo "Checking MCP Server Health..."

# Check if server starts
timeout 5 python -m voidlight_markitdown_mcp --help
if [ $? -ne 0 ]; then
    echo "❌ Server module not accessible"
    exit 1
fi

# Test STDIO mode
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | \
    python -m voidlight_markitdown_mcp 2>/dev/null | \
    grep -q '"result"'

if [ $? -eq 0 ]; then
    echo "✅ STDIO mode working"
else
    echo "❌ STDIO mode failed"
fi

# Test HTTP mode
python -m voidlight_markitdown_mcp --http --port 3999 &
SERVER_PID=$!
sleep 2

curl -s http://localhost:3999/mcp \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' \
    | grep -q '"result"'

if [ $? -eq 0 ]; then
    echo "✅ HTTP mode working"
else
    echo "❌ HTTP mode failed"
fi

kill $SERVER_PID 2>/dev/null
```

## Protocol Issues

### JSON-RPC Errors

**Common Error Codes:**
- `-32700`: Parse error (invalid JSON)
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

**Debugging Invalid Requests:**
```python
# Validate JSON-RPC request format
def validate_request(request):
    required = ['jsonrpc', 'method']
    for field in required:
        if field not in request:
            return False, f"Missing field: {field}"
    
    if request['jsonrpc'] != '2.0':
        return False, "Invalid jsonrpc version"
    
    return True, None
```

### SSE Connection Issues

**Symptoms:**
- Connection drops after a few seconds
- "Event stream error" messages
- Partial responses

**Solutions:**
1. Check proxy/firewall settings
2. Increase client timeout
3. Enable keep-alive:
```python
# In HTTP mode startup
uvicorn.run(app, host="0.0.0.0", port=3001, 
            timeout_keep_alive=30,
            limit_max_requests=1000)
```

## Performance Issues

### Slow Conversions

**Diagnosis:**
```bash
# Profile server performance
python -m cProfile -o profile.stats -m voidlight_markitdown_mcp

# Analyze profile
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

**Common Causes:**
1. Plugin overhead - disable unnecessary plugins
2. Large file processing - implement streaming
3. Network latency - use local files for testing

### Memory Issues

**Monitor memory usage:**
```python
# Add to server startup
import tracemalloc
tracemalloc.start()

# Periodically log memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.2f} MB")
```

## Korean Text Issues

### Encoding Problems

**Symptoms:**
- Garbled Korean text
- "UnicodeDecodeError" exceptions
- Missing characters

**Solutions:**
```python
# Force UTF-8 encoding
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Set environment
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8
```

### Normalization Issues

**Test Korean normalization:**
```python
# Test script
test_text = "한글 테스트"
result = await client.call_tool("convert_korean_document", {
    "uri": f"data:text/plain;charset=utf-8,{test_text}",
    "normalize_korean": True
})
print(f"Original: {test_text}")
print(f"Converted: {result}")
```

## Getting Help

### Logs and Diagnostics

1. **Enable verbose logging:**
```bash
export VOIDLIGHT_LOG_LEVEL=DEBUG
export VOIDLIGHT_LOG_FILE=./detailed_debug.log
```

2. **Collect diagnostic information:**
```bash
# System info
python --version
pip show voidlight-markitdown-mcp
pip show mcp

# Test installation
python -c "import voidlight_markitdown_mcp; print('✅ Module imports successfully')"
```

3. **Create minimal reproduction:**
```python
# minimal_repro.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def minimal_test():
    # Your minimal failing case here
    pass

if __name__ == "__main__":
    asyncio.run(minimal_test())
```

### Reporting Issues

When reporting issues, include:
1. Full error message and stack trace
2. Client and server versions
3. Configuration files (sanitized)
4. Minimal reproduction script
5. Debug logs with `VOIDLIGHT_LOG_LEVEL=DEBUG`

### Community Resources

- GitHub Issues: [voidlight/voidlight_markitdown](https://github.com/voidlight/voidlight_markitdown/issues)
- MCP Documentation: [Model Context Protocol](https://modelcontextprotocol.io)
- Discord/Slack channels (if available)