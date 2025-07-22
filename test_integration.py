#!/usr/bin/env python3
"""Integration test for VoidLight MarkItDown."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/voidlight_markitdown/src'))

try:
    from voidlight_markitdown import VoidLightMarkItDown
    from voidlight_markitdown._korean_utils import KoreanTextProcessor
    print("✓ Successfully imported VoidLightMarkItDown")
    print("✓ Successfully imported KoreanTextProcessor")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 1: Basic initialization
try:
    converter = VoidLightMarkItDown()
    print("✓ Basic initialization successful")
except Exception as e:
    print(f"✗ Basic initialization failed: {e}")

# Test 2: Korean mode initialization
try:
    korean_converter = VoidLightMarkItDown(korean_mode=True)
    print("✓ Korean mode initialization successful")
except Exception as e:
    print(f"✗ Korean mode initialization failed: {e}")

# Test 3: Korean text processor
try:
    processor = KoreanTextProcessor()
    
    # Test character detection
    assert processor.is_korean_char('가') == True
    assert processor.is_korean_char('A') == False
    print("✓ Korean character detection working")
    
    # Test text ratio
    ratio = processor.detect_korean_ratio('Hello 안녕')
    assert 0 < ratio < 1
    print("✓ Korean text ratio detection working")
    
    # Test encoding
    text = "안녕하세요"
    encoded = text.encode('utf-8')
    decoded = processor.smart_decode(encoded)
    assert decoded == text
    print("✓ Korean encoding/decoding working")
    
except Exception as e:
    print(f"✗ Korean text processor test failed: {e}")

# Test 4: Convert plain text
try:
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World\n안녕하세요")
        temp_path = f.name
    
    result = converter.convert(temp_path)
    assert "Hello World" in result.markdown
    assert "안녕하세요" in result.markdown
    os.unlink(temp_path)
    print("✓ Plain text conversion working")
    
except Exception as e:
    import traceback
    print(f"✗ Plain text conversion failed: {e}")
    traceback.print_exc()
    if 'temp_path' in locals():
        os.unlink(temp_path)

# Test 5: Convert data URI
try:
    data_uri = "data:text/plain;charset=utf-8,Hello%20World"
    result = converter.convert_uri(data_uri)
    assert "Hello World" in result.markdown
    print("✓ Data URI conversion working")
except Exception as e:
    import traceback
    print(f"✗ Data URI conversion failed: {e}")
    traceback.print_exc()

# Test 6: Check available converters
try:
    assert len(converter._converters) > 0
    print(f"✓ {len(converter._converters)} converters registered")
    
    # List converter types
    converter_types = set()
    for reg in converter._converters:
        converter_types.add(type(reg.converter).__name__)
    print(f"  Available converters: {', '.join(sorted(converter_types))}")
    
except Exception as e:
    print(f"✗ Converter check failed: {e}")

print("\n=== Integration test complete ===")
print(f"VoidLight MarkItDown is {'ready' if all else 'not fully ready'} for use.")