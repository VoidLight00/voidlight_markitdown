# Integration Tests

Tests for multi-component interactions and external API integrations.

## Structure

- `mcp/` - MCP protocol and client tests
- `api/` - External API integrations (YouTube, Wikipedia)
- `audio_test_suite/` - Audio processing integration tests

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific integration tests
pytest tests/integration/mcp/
pytest tests/integration/api/

# Run with specific markers
pytest tests/integration/ -m "mcp"
pytest tests/integration/ -m "korean"
```

## Test Guidelines

- Tests may use external services (with mocking preferred)
- Execution time < 10 seconds per test
- Test component interactions, not individual units
- Handle network failures gracefully

## Environment Setup

Some integration tests require environment variables:
```bash
export MCP_SERVER_URL=http://localhost:3000
export YOUTUBE_API_KEY=your_key_here
```

## Example Integration Test

```python
@pytest.mark.integration
async def test_mcp_client_server_communication():
    """Test that MCP client can communicate with server."""
    async with create_mcp_client() as client:
        response = await client.list_tools()
        assert len(response.tools) > 0
```