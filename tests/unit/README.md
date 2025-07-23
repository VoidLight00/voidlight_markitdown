# Unit Tests

Fast, isolated tests for individual components of VoidLight MarkItDown.

## Structure

- `korean/` - Korean language processing utilities
- `converters/` - Document converter logic
- `utils/` - General utility functions and CLI tests

## Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific category
pytest tests/unit/korean/
pytest tests/unit/converters/

# Run with coverage
pytest tests/unit/ --cov=voidlight_markitdown
```

## Test Guidelines

- Each test should run in < 1 second
- No external dependencies (mocked if needed)
- Focus on single component/function
- Use descriptive test names: `test_<component>_<scenario>_<expected_result>`

## Example Unit Test

```python
def test_korean_char_detection_valid_hangul():
    """Test that valid Hangul characters are correctly identified."""
    assert KoreanTextProcessor.is_korean_char('가')
    assert KoreanTextProcessor.is_korean_char('힣')
```