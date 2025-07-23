# End-to-End Tests

Complete workflow tests that validate the entire system from input to output.

## Structure

- `workflows/` - Complete conversion workflows and system tests

## Running E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/

# Run specific workflow tests
pytest tests/e2e/workflows/

# Run with extended timeout
pytest tests/e2e/ --timeout=600
```

## Test Guidelines

- Test complete user workflows
- Use real files and services
- Validate final output quality
- May take longer to execute (up to several minutes)
- Should be run before releases

## Test Scenarios

1. **Document Conversion Flow**
   - Input various document formats
   - Process through converters
   - Validate markdown output

2. **MCP Server Integration**
   - Start MCP server
   - Process requests
   - Validate responses

3. **Multi-format Processing**
   - Batch processing
   - Error handling
   - Performance under load

## Example E2E Test

```python
@pytest.mark.e2e
def test_complete_pdf_conversion_workflow():
    """Test complete PDF to Markdown conversion workflow."""
    # Setup
    pdf_file = "sample.pdf"
    
    # Execute conversion
    result = convert_document(pdf_file)
    
    # Validate output
    assert result.success
    assert "# " in result.markdown  # Has headers
    assert len(result.markdown) > 100  # Meaningful content
```