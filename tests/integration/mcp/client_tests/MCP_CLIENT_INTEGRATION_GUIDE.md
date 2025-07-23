# MCP Client Integration Guide for VoidLight MarkItDown

This guide provides comprehensive instructions for integrating the voidlight_markitdown MCP server with various MCP clients.

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Claude Desktop Integration](#claude-desktop-integration)
4. [VSCode Integration](#vscode-integration)
5. [Custom Client Integration](#custom-client-integration)
6. [Testing Your Integration](#testing-your-integration)
7. [Best Practices](#best-practices)
8. [API Reference](#api-reference)

## Overview

VoidLight MarkItDown MCP server provides two tools:
- `convert_to_markdown`: Convert any supported format to markdown
- `convert_korean_document`: Convert with enhanced Korean text support

The server supports both STDIO and HTTP/SSE transport modes.

## Installation

### Prerequisites
```bash
# Python 3.9+ required
python --version

# Install the MCP server
cd packages/voidlight_markitdown-mcp
pip install -e .

# Verify installation
python -m voidlight_markitdown_mcp --help
```

### Quick Test
```bash
# Test STDIO mode
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m voidlight_markitdown_mcp

# Test HTTP mode
python -m voidlight_markitdown_mcp --http --port 3001
# In another terminal:
curl http://localhost:3001/mcp -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

## Claude Desktop Integration

### 1. Locate Configuration File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### 2. Add Server Configuration

```json
{
  "mcpServers": {
    "voidlight-markitdown": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "voidlight_markitdown_mcp"],
      "env": {
        "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
        "VOIDLIGHT_LOG_LEVEL": "INFO",
        "VOIDLIGHT_LOG_FILE": "~/voidlight_mcp.log"
      }
    }
  }
}
```

### 3. Virtual Environment Setup

If using a virtual environment:

```json
{
  "mcpServers": {
    "voidlight-markitdown": {
      "type": "stdio",
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "voidlight_markitdown_mcp"],
      "env": {
        "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After editing the configuration:
1. Quit Claude Desktop completely
2. Start Claude Desktop
3. Look for "voidlight-markitdown" in the MCP servers list

### 5. Usage in Claude

Once connected, you can use commands like:
- "Convert https://example.com to markdown"
- "Convert this Korean document to markdown with normalization"

## VSCode Integration

### 1. Install MCP Extension

```bash
# Install the MCP extension (when available)
code --install-extension <mcp-extension-id>
```

### 2. Configure in Settings

**User Settings (global):**
```json
{
  "mcp.servers": {
    "voidlight-markitdown": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "voidlight_markitdown_mcp"],
      "env": {
        "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true"
      }
    }
  }
}
```

**Workspace Settings (project-specific):**
```json
// .vscode/settings.json
{
  "mcp.servers": {
    "voidlight-markitdown": {
      "type": "stdio",
      "command": "${workspaceFolder}/venv/bin/python",
      "args": ["-m", "voidlight_markitdown_mcp"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/packages"
      }
    }
  }
}
```

### 3. Using in VSCode

- Open Command Palette (`Cmd/Ctrl + Shift + P`)
- Type "MCP: Connect to Server"
- Select "voidlight-markitdown"
- Use MCP tools through the extension UI

## Custom Client Integration

### Python Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def convert_document():
    # Configure server connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "voidlight_markitdown_mcp"],
        env={
            "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
            "VOIDLIGHT_LOG_LEVEL": "INFO"
        }
    )
    
    # Connect and use
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Convert a document
            result = await session.call_tool(
                "convert_to_markdown",
                {"uri": "https://example.com"}
            )
            print(f"Converted content: {result.content}")
            
            # Convert Korean document
            korean_result = await session.call_tool(
                "convert_korean_document",
                {
                    "uri": "file:///path/to/korean.docx",
                    "normalize_korean": True
                }
            )
            print(f"Korean content: {korean_result.content}")

# Run the client
asyncio.run(convert_document())
```

### Node.js Client Example

```javascript
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

async function convertDocument() {
    // Create transport
    const transport = new StdioClientTransport({
        command: 'python',
        args: ['-m', 'voidlight_markitdown_mcp'],
        env: {
            ...process.env,
            VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS: 'true'
        }
    });

    // Create client
    const client = new Client({
        name: 'my-client',
        version: '1.0.0'
    }, {
        capabilities: {}
    });

    try {
        // Connect
        await client.connect(transport);

        // List tools
        const tools = await client.listTools();
        console.log('Available tools:', tools.tools.map(t => t.name));

        // Convert document
        const result = await client.callTool({
            name: 'convert_to_markdown',
            arguments: {
                uri: 'https://example.com'
            }
        });
        console.log('Converted:', result.content);

    } finally {
        await client.close();
    }
}

convertDocument().catch(console.error);
```

### HTTP/SSE Client Example

```python
import httpx
import json

async def convert_via_http():
    # Start server in HTTP mode first:
    # python -m voidlight_markitdown_mcp --http --port 3001
    
    async with httpx.AsyncClient() as client:
        # Call MCP method
        response = await client.post(
            "http://localhost:3001/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "convert_to_markdown",
                    "arguments": {
                        "uri": "https://example.com"
                    }
                },
                "id": 1
            }
        )
        
        result = response.json()
        print(f"Result: {result}")
```

## Testing Your Integration

### 1. Basic Connectivity Test

```python
# test_connection.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_connection():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "voidlight_markitdown_mcp"],
        env={"VOIDLIGHT_LOG_LEVEL": "DEBUG"}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connection successful!")
                
                # Test tool listing
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools")
                
                # Test simple conversion
                result = await session.call_tool(
                    "convert_to_markdown",
                    {"uri": "data:text/plain,Hello World"}
                )
                print("✅ Tool invocation successful!")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

asyncio.run(test_connection())
```

### 2. Run Comprehensive Tests

```bash
# Run all test suites
cd mcp_client_tests
python run_all_tests.py

# Run specific tests
python clients/python_test_client.py
python clients/protocol_compliance_validator.py
python clients/performance_test_client.py
```

## Best Practices

### 1. Error Handling

```python
async def robust_conversion(uri: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "convert_to_markdown",
                        {"uri": uri}
                    )
                    return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### 2. Connection Pooling

```python
class MCPConnectionPool:
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.connections = asyncio.Queue(maxsize=pool_size)
        
    async def get_connection(self):
        # Implementation for connection pooling
        pass
```

### 3. Caching Results

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_result(uri: str):
    # Cache conversion results for repeated URIs
    uri_hash = hashlib.md5(uri.encode()).hexdigest()
    # Implementation details...
```

### 4. Logging and Monitoring

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_client.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('mcp_client')

# Log all operations
logger.info(f"Converting URI: {uri}")
logger.debug(f"Server response: {result}")
```

## API Reference

### Tools

#### convert_to_markdown

Convert a resource to markdown format.

**Parameters:**
- `uri` (string, required): The URI to convert (http:, https:, file:, data:)

**Returns:**
- `content` (string): The converted markdown content

**Example:**
```json
{
  "name": "convert_to_markdown",
  "arguments": {
    "uri": "https://example.com/document.pdf"
  }
}
```

#### convert_korean_document

Convert Korean documents with enhanced text processing.

**Parameters:**
- `uri` (string, required): The URI to convert
- `normalize_korean` (boolean, optional): Whether to normalize Korean text (default: true)

**Returns:**
- `content` (string): The converted markdown content with Korean text properly handled

**Example:**
```json
{
  "name": "convert_korean_document",
  "arguments": {
    "uri": "file:///path/to/korean_document.docx",
    "normalize_korean": true
  }
}
```

### Environment Variables

- `VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS`: Enable/disable plugins ("true"/"false")
- `VOIDLIGHT_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `VOIDLIGHT_LOG_FILE`: Path to log file
- `PYTHONIOENCODING`: Set to "utf-8" for proper Unicode handling

### Transport Modes

#### STDIO Mode
- Default mode
- Best for local integrations
- Lower latency
- Single client connection

#### HTTP/SSE Mode
- Enable with `--http` flag
- Supports multiple concurrent clients
- Better for remote connections
- Supports streaming responses

### URI Formats

Supported URI schemes:
- `http://` and `https://` - Web resources
- `file://` - Local files
- `data:` - Inline data (base64 or plain text)

Examples:
```
https://example.com/document.pdf
file:///Users/me/document.docx
data:text/plain;base64,SGVsbG8gV29ybGQ=
data:text/plain;charset=utf-8,한글 텍스트
```

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed troubleshooting steps.

## Contributing

To contribute to the MCP server:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

- GitHub Issues: [voidlight/voidlight_markitdown](https://github.com/voidlight/voidlight_markitdown)
- Documentation: This guide and associated files
- Tests: Run `python mcp_client_tests/run_all_tests.py` to verify your setup