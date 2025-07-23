# MCP Client Test Suite

Comprehensive testing framework for the VoidLight MarkItDown MCP server with real MCP clients.

## Overview

This test suite validates the voidlight_markitdown MCP server with:
- Multiple MCP client implementations (Python, Node.js)
- Protocol compliance validation
- Performance benchmarking
- Korean language support testing
- Integration scenarios

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run all tests
python run_all_tests.py

# View results
cat reports/test_summary_*.json
```

## Test Components

### 1. Python Test Client (`clients/python_test_client.py`)
- STDIO and HTTP/SSE connection tests
- Tool invocation tests
- Korean text processing validation
- Concurrent request handling
- Error recovery testing

### 2. Node.js Test Client (`clients/nodejs_test_client.js`)
- Cross-language compatibility testing
- MCP SDK integration validation
- Protocol compliance from JavaScript

### 3. Protocol Compliance Validator (`clients/protocol_compliance_validator.py`)
- JSON-RPC 2.0 compliance checking
- MCP method implementation validation
- Error handling compliance
- Streaming capability testing

### 4. Performance Test Client (`clients/performance_test_client.py`)
- Latency profiling
- Throughput testing
- Resource usage monitoring
- Memory leak detection
- Korean text performance benchmarking

## Configuration

### Claude Desktop Configuration

Location: `configs/claude_desktop_config.json`

```json
{
  "mcpServers": {
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

Copy to:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### VSCode Configuration

Location: `configs/vscode_mcp_config.json`

Add to VSCode settings:
- User settings: `Cmd+,` → Search "mcp"
- Workspace: `.vscode/settings.json`

### Custom Client Configuration

Location: `configs/custom_client_config.yaml`

Flexible configuration for custom MCP client implementations.

## Running Individual Tests

### Python Tests Only
```bash
python clients/python_test_client.py
```

### Protocol Compliance Only
```bash
python clients/protocol_compliance_validator.py
```

### Performance Tests Only
```bash
python clients/performance_test_client.py
```

### Node.js Tests Only
```bash
node clients/nodejs_test_client.js
```

## Test Reports

Reports are saved in the `reports/` directory:

- `test_summary_*.json` - Overall test summary
- `python_client_test_report_*.json` - Python client results
- `nodejs_client_test_report_*.json` - Node.js client results
- `protocol_compliance_report_*.json` - Protocol validation results
- `performance_test_report_*.json` - Performance metrics
- `metrics/` - Performance visualization charts

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.

## Integration Guide

See [MCP_CLIENT_INTEGRATION_GUIDE.md](./MCP_CLIENT_INTEGRATION_GUIDE.md) for detailed integration instructions.

## Test Coverage

### Connection Types
- ✅ STDIO mode
- ✅ HTTP/SSE mode
- ✅ Multiple concurrent clients
- ✅ Reconnection handling

### Protocol Features
- ✅ JSON-RPC 2.0 compliance
- ✅ MCP method implementations
- ✅ Error handling
- ✅ Request/response correlation
- ✅ Batch requests

### Tool Testing
- ✅ convert_to_markdown
- ✅ convert_korean_document
- ✅ Parameter validation
- ✅ Large payload handling
- ✅ Various URI schemes

### Korean Language
- ✅ UTF-8 encoding
- ✅ Text normalization
- ✅ Character preservation
- ✅ Mixed language documents

### Performance
- ✅ Latency measurements
- ✅ Throughput testing
- ✅ Memory usage tracking
- ✅ CPU utilization
- ✅ Scalability testing

## CI/CD Integration

### GitHub Actions Example

```yaml
name: MCP Client Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - uses: actions/setup-node@v3
        with:
          node-version: '16'
      
      - name: Install dependencies
        run: |
          pip install -r mcp_client_tests/requirements.txt
          cd mcp_client_tests && npm install
      
      - name: Run MCP tests
        run: |
          cd mcp_client_tests
          python run_all_tests.py
      
      - name: Upload test reports
        uses: actions/upload-artifact@v3
        with:
          name: mcp-test-reports
          path: mcp_client_tests/reports/
```

## Development

### Adding New Tests

1. Create test in appropriate client file
2. Follow existing test patterns
3. Add to test suite in `run_all_tests.py`
4. Update documentation

### Test Best Practices

- Use descriptive test names
- Include both positive and negative cases
- Test edge cases and error conditions
- Measure and report performance metrics
- Clean up resources after tests

## Requirements

- Python 3.9+
- Node.js 16+ (for Node.js tests)
- voidlight_markitdown_mcp installed
- See `requirements.txt` for Python packages
- See `package.json` for Node.js packages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Same as voidlight_markitdown project.