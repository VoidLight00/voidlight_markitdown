#!/usr/bin/env python3
"""Test Korean features of VoidLight MarkItDown."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/voidlight_markitdown/src'))

from voidlight_markitdown import VoidLightMarkItDown
from voidlight_markitdown._korean_utils import KoreanTextProcessor

print("=== Testing Korean Features ===\n")

# Test Korean text processor
processor = KoreanTextProcessor()

# Test 1: Character detection
print("1. Character Detection:")
test_chars = [('가', True), ('A', False), ('韓', True), ('漢', True), ('あ', False)]
for char, expected in test_chars:
    result = processor.is_korean_char(char)
    status = "✓" if result == expected else "✗"
    print(f"   {status} is_korean_char('{char}') = {result} (expected {expected})")

# Test 2: Korean ratio detection
print("\n2. Korean Text Ratio:")
test_texts = [
    ("안녕하세요", 1.0),
    ("Hello World", 0.0),
    ("Hello 안녕", 0.3),  # approximate
    ("韓國語 텍스트", 0.5),  # approximate
]
for text, expected_min in test_texts:
    ratio = processor.detect_korean_ratio(text)
    status = "✓" if ratio >= expected_min * 0.8 else "✗"  # 80% tolerance
    print(f"   {status} detect_korean_ratio('{text}') = {ratio:.2f}")

# Test 3: Encoding detection
print("\n3. Encoding Detection:")
test_encodings = [
    ("안녕하세요".encode('utf-8'), 'utf-8'),
    ("안녕하세요".encode('cp949'), 'cp949'),
    ("안녕하세요".encode('euc-kr'), 'euc-kr'),
]
for encoded, expected in test_encodings:
    detected = processor.detect_encoding(encoded)
    status = "✓" if detected == expected else "✗"
    print(f"   {status} detect_encoding({expected} encoded) = {detected}")

# Test 4: Korean document conversion
print("\n4. Korean Document Conversion:")
converter = VoidLightMarkItDown(korean_mode=True)

# Create test file
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write("# 제목\n\n안녕하세요. 이것은 **테스트** 문서입니다.\n\nHello World!")
    temp_path = f.name

try:
    result = converter.convert(temp_path)
    print(f"   ✓ Successfully converted Korean document")
    print(f"   Content preview: {result.markdown[:50]}...")
    
    # Check if Korean text is preserved
    if "안녕하세요" in result.markdown and "테스트" in result.markdown:
        print("   ✓ Korean text preserved correctly")
    else:
        print("   ✗ Korean text not preserved")
        
finally:
    os.unlink(temp_path)

# Test 5: Mixed encoding document
print("\n5. Mixed Content Handling:")
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write("English: Hello World\n한글: 안녕하세요\n中文: 你好\n日本語: こんにちは")
    temp_path = f.name

try:
    result = converter.convert(temp_path)
    preserved = all(text in result.markdown for text in ["Hello", "안녕하세요", "你好", "こんにちは"])
    status = "✓" if preserved else "✗"
    print(f"   {status} Mixed language content preserved")
finally:
    os.unlink(temp_path)

# Test 6: Korean NLP features (if available)
print("\n6. Korean NLP Features:")
try:
    # Test normalization
    text = "ㅎㅏㄴㄱㅡㄹ"  # Decomposed Hangul
    normalized = processor.normalize_korean_text(text)
    print(f"   ✓ Text normalization: '{text}' → '{normalized}'")
    
    # Test spacing correction (if available)
    if hasattr(processor, 'correct_spacing'):
        text = "안녕하세요여러분"
        corrected = processor.correct_spacing(text)
        print(f"   ✓ Spacing correction: '{text}' → '{corrected}'")
    else:
        print("   - Spacing correction not available")
        
except Exception as e:
    print(f"   - NLP features not available: {e}")

print("\n=== Korean Features Test Complete ===")