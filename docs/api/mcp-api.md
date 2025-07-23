# MCP (Model Context Protocol) API Reference

Complete reference for the VoidLight MarkItDown MCP server implementation.

## Table of Contents

1. [Overview](#overview)
2. [Server Configuration](#server-configuration)
3. [Protocol Modes](#protocol-modes)
4. [Available Tools](#available-tools)
5. [Request/Response Format](#requestresponse-format)
6. [Error Handling](#error-handling)
7. [Client Integration](#client-integration)
8. [Examples](#examples)

## Overview

The VoidLight MarkItDown MCP server provides document conversion capabilities through the Model Context Protocol, enabling AI assistants and other tools to convert documents to markdown.

### Key Features

- **Multiple transport modes**: STDIO and HTTP/SSE
- **Streaming support**: Handle large files efficiently
- **Korean language support**: Advanced Korean text processing
- **Rich metadata**: Document information and statistics
- **Error recovery**: Robust error handling

## Server Configuration

### Starting the Server

```bash
# STDIO mode (default)
voidlight-markitdown-mcp

# HTTP mode
voidlight-markitdown-mcp --mode http --port 8080

# With custom configuration
voidlight-markitdown-mcp --config config.json
```

### Configuration File

```json
{
  "server": {
    "mode": "http",
    "host": "localhost",
    "port": 8080,
    "timeout": 300
  },
  "conversion": {
    "korean_mode": true,
    "ocr_enabled": true,
    "max_file_size": 104857600,
    "allowed_formats": [
      ".pdf", ".docx", ".xlsx", ".pptx",
      ".html", ".txt", ".md", ".epub"
    ]
  },
  "security": {
    "require_auth": false,
    "api_keys": [],
    "allowed_origins": ["*"]
  },
  "logging": {
    "level": "INFO",
    "file": "mcp-server.log"
  }
}
```

### Environment Variables

```bash
# Server configuration
export MCP_SERVER_MODE=http
export MCP_SERVER_PORT=8080
export MCP_SERVER_HOST=0.0.0.0

# Conversion settings
export MCP_KOREAN_MODE=true
export MCP_OCR_ENABLED=true
export MCP_MAX_FILE_SIZE=104857600

# Logging
export MCP_LOG_LEVEL=INFO
export MCP_LOG_FILE=mcp-server.log
```

## Protocol Modes

### STDIO Mode

Standard input/output mode for direct integration with tools like Claude Desktop.

```bash
# Start server
voidlight-markitdown-mcp

# Server reads from stdin and writes to stdout
# Perfect for subprocess integration
```

### HTTP/SSE Mode

HTTP mode with Server-Sent Events for web-based clients.

```bash
# Start HTTP server
voidlight-markitdown-mcp --mode http --port 8080

# Endpoints:
# POST /convert - Convert document
# GET /sse - SSE endpoint for streaming
# GET /health - Health check
# GET /tools - List available tools
```

## Available Tools

### convert_document

Main tool for document conversion.

```json
{
  "name": "convert_document",
  "description": "Convert a document to Markdown format",
  "inputSchema": {
    "type": "object",
    "properties": {
      "source": {
        "type": "string",
        "description": "File path or URL to convert"
      },
      "encoding": {
        "type": "string",
        "description": "Force specific encoding (optional)"
      },
      "korean_mode": {
        "type": "boolean",
        "description": "Enable Korean language processing"
      },
      "ocr_enabled": {
        "type": "boolean",
        "description": "Enable OCR for images/PDFs"
      },
      "include_metadata": {
        "type": "boolean",
        "description": "Include document metadata"
      },
      "stream": {
        "type": "boolean",
        "description": "Enable streaming mode"
      }
    },
    "required": ["source"]
  }
}
```

### convert_batch

Convert multiple documents at once.

```json
{
  "name": "convert_batch",
  "description": "Convert multiple documents to Markdown",
  "inputSchema": {
    "type": "object",
    "properties": {
      "sources": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of file paths or URLs"
      },
      "korean_mode": {
        "type": "boolean",
        "description": "Enable Korean mode for all documents"
      },
      "parallel": {
        "type": "boolean",
        "description": "Process in parallel"
      }
    },
    "required": ["sources"]
  }
}
```

### get_supported_formats

Get list of supported file formats.

```json
{
  "name": "get_supported_formats",
  "description": "Get list of supported file formats",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

### analyze_document

Analyze document without full conversion.

```json
{
  "name": "analyze_document",
  "description": "Analyze document structure and metadata",
  "inputSchema": {
    "type": "object",
    "properties": {
      "source": {
        "type": "string",
        "description": "File path or URL to analyze"
      },
      "deep_analysis": {
        "type": "boolean",
        "description": "Perform deep content analysis"
      }
    },
    "required": ["source"]
  }
}
```

## Request/Response Format

### STDIO Format

#### Request

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "convert_document",
    "arguments": {
      "source": "/path/to/document.pdf",
      "korean_mode": true
    }
  }
}
```

#### Response

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# Document Title\n\nConverted markdown content..."
      }
    ],
    "metadata": {
      "source_type": "pdf",
      "pages": 10,
      "conversion_time": 2.5,
      "word_count": 5000
    }
  }
}
```

### HTTP Format

#### Request

```http
POST /convert HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "source": "/path/to/document.pdf",
  "korean_mode": true,
  "include_metadata": true
}
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "markdown": "# Document Title\n\nConverted content...",
  "metadata": {
    "source_type": "pdf",
    "pages": 10,
    "title": "Document Title",
    "author": "Author Name",
    "conversion_time": 2.5
  }
}
```

### Streaming Response (SSE)

```http
GET /sse?source=/path/to/large.pdf HTTP/1.1
Host: localhost:8080
Accept: text/event-stream

HTTP/1.1 200 OK
Content-Type: text/event-stream

event: chunk
data: {"index": 0, "content": "# Document Title\n\n"}

event: chunk
data: {"index": 1, "content": "First paragraph..."}

event: complete
data: {"metadata": {"pages": 100, "conversion_time": 15.2}}
```

## Error Handling

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "error": {
    "code": -32001,
    "message": "Unsupported file format",
    "data": {
      "format": ".xyz",
      "supported_formats": [".pdf", ".docx", "..."]
    }
  }
}
```

### Error Codes

| Code | Name | Description |
|------|------|-------------|
| -32001 | UNSUPPORTED_FORMAT | File format not supported |
| -32002 | FILE_NOT_FOUND | Source file doesn't exist |
| -32003 | CONVERSION_ERROR | Conversion failed |
| -32004 | ENCODING_ERROR | Encoding detection/conversion failed |
| -32005 | OCR_ERROR | OCR processing failed |
| -32006 | TIMEOUT_ERROR | Conversion timed out |
| -32007 | FILE_SIZE_ERROR | File exceeds size limit |
| -32008 | KOREAN_PROCESSING_ERROR | Korean text processing failed |
| -32009 | NETWORK_ERROR | Failed to fetch URL |
| -32010 | PERMISSION_ERROR | No permission to access file |

### Error Handling Examples

```python
# Python client example
import requests

try:
    response = requests.post(
        "http://localhost:8080/convert",
        json={"source": "document.pdf"}
    )
    response.raise_for_status()
    result = response.json()
except requests.HTTPError as e:
    error_data = e.response.json()
    print(f"Error: {error_data['error']['message']}")
```

## Client Integration

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "voidlight-markitdown": {
      "command": "voidlight-markitdown-mcp",
      "args": [],
      "env": {
        "MCP_KOREAN_MODE": "true"
      }
    }
  }
}
```

### Python Client

```python
import subprocess
import json

class MCPClient:
    def __init__(self):
        self.process = subprocess.Popen(
            ["voidlight-markitdown-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    def convert_document(self, source, **options):
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {
                "name": "convert_document",
                "arguments": {
                    "source": source,
                    **options
                }
            }
        }
        
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        response = json.loads(self.process.stdout.readline())
        return response["result"]

# Usage
client = MCPClient()
result = client.convert_document(
    "/path/to/document.pdf",
    korean_mode=True
)
```

### JavaScript Client

```javascript
const { spawn } = require('child_process');

class MCPClient {
    constructor() {
        this.process = spawn('voidlight-markitdown-mcp');
        this.setupHandlers();
    }
    
    async convertDocument(source, options = {}) {
        const request = {
            jsonrpc: "2.0",
            id: Date.now().toString(),
            method: "tools/call",
            params: {
                name: "convert_document",
                arguments: { source, ...options }
            }
        };
        
        return this.sendRequest(request);
    }
    
    sendRequest(request) {
        return new Promise((resolve, reject) => {
            this.process.stdin.write(JSON.stringify(request) + '\n');
            
            this.process.stdout.once('data', (data) => {
                const response = JSON.parse(data.toString());
                if (response.error) {
                    reject(response.error);
                } else {
                    resolve(response.result);
                }
            });
        });
    }
}

// Usage
const client = new MCPClient();
const result = await client.convertDocument(
    '/path/to/document.pdf',
    { korean_mode: true }
);
```

### HTTP Client (curl)

```bash
# Basic conversion
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{"source": "/path/to/document.pdf"}'

# With options
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "source": "/path/to/korean.docx",
    "korean_mode": true,
    "include_metadata": true
  }'

# Streaming conversion
curl -N http://localhost:8080/sse?source=/path/to/large.pdf
```

## Examples

### Basic Document Conversion

```json
// Request
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "convert_document",
    "arguments": {
      "source": "report.pdf"
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# Annual Report 2024\n\n## Executive Summary\n\n..."
      }
    ]
  }
}
```

### Korean Document with Metadata

```json
// Request
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/call",
  "params": {
    "name": "convert_document",
    "arguments": {
      "source": "korean_document.docx",
      "korean_mode": true,
      "include_metadata": true
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "2",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# 한국어 문서\n\n## 소개\n\n..."
      }
    ],
    "metadata": {
      "title": "한국어 문서",
      "author": "홍길동",
      "pages": 5,
      "encoding": "utf-8",
      "korean_stats": {
        "hangul_ratio": 0.85,
        "mixed_script": true
      }
    }
  }
}
```

### Batch Conversion

```json
// Request
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "convert_batch",
    "arguments": {
      "sources": [
        "doc1.pdf",
        "doc2.docx",
        "doc3.pptx"
      ],
      "parallel": true
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "3",
  "result": {
    "conversions": [
      {
        "source": "doc1.pdf",
        "success": true,
        "markdown": "# Document 1\n\n..."
      },
      {
        "source": "doc2.docx",
        "success": true,
        "markdown": "# Document 2\n\n..."
      },
      {
        "source": "doc3.pptx",
        "success": false,
        "error": "File corrupted"
      }
    ],
    "statistics": {
      "total": 3,
      "successful": 2,
      "failed": 1,
      "total_time": 5.2
    }
  }
}
```

### Streaming Large File

```json
// Initial request
{
  "jsonrpc": "2.0",
  "id": "4",
  "method": "tools/call",
  "params": {
    "name": "convert_document",
    "arguments": {
      "source": "large_book.pdf",
      "stream": true
    }
  }
}

// Streaming responses
{
  "jsonrpc": "2.0",
  "id": "4",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# Chapter 1\n\n...",
        "chunk_index": 0
      }
    ]
  }
}

// ... more chunks ...

// Final chunk with metadata
{
  "jsonrpc": "2.0",
  "id": "4",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "... end of document.",
        "chunk_index": 42,
        "is_final": true
      }
    ],
    "metadata": {
      "total_chunks": 43,
      "pages": 500,
      "conversion_time": 45.3
    }
  }
}
```

## Advanced Features

### Custom Headers (HTTP)

```http
POST /convert HTTP/1.1
Host: localhost:8080
Content-Type: application/json
X-API-Key: your-api-key
X-Request-ID: unique-request-id

{
  "source": "document.pdf"
}
```

### Progress Tracking (SSE)

```javascript
const evtSource = new EventSource('/sse?source=large.pdf');

evtSource.addEventListener('progress', (e) => {
    const data = JSON.parse(e.data);
    console.log(`Progress: ${data.percentage}%`);
});

evtSource.addEventListener('chunk', (e) => {
    const data = JSON.parse(e.data);
    appendMarkdown(data.content);
});

evtSource.addEventListener('complete', (e) => {
    const data = JSON.parse(e.data);
    console.log('Conversion complete:', data.metadata);
    evtSource.close();
});
```

### Health Check

```bash
# Check server health
curl http://localhost:8080/health

# Response
{
  "status": "healthy",
  "version": "0.1.13",
  "uptime": 3600,
  "conversions_count": 150,
  "korean_mode": true
}
```

---

<div align="center">
  <p>For implementation examples, see the <a href="../guides/mcp-server.md">MCP Server Guide</a></p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>