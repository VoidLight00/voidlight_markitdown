#!/usr/bin/env python3
"""Test VoidLight MarkItDown library usage."""

from voidlight_markitdown import VoidLightMarkItDown

# Create converter with Korean mode
converter = VoidLightMarkItDown(korean_mode=True)

print("=== Testing VoidLight MarkItDown Library ===\n")

# Test 1: Convert text file
print("1. Converting Korean text file:")
result = converter.convert("test_korean_document.txt")
print(f"   Length: {len(result.markdown)} characters")
print(f"   Preview: {result.markdown[:100]}...")

# Test 2: Convert HTML file
print("\n2. Converting Korean HTML file:")
result = converter.convert("test_korean.html")
print(f"   Length: {len(result.markdown)} characters")
print(f"   Preview: {result.markdown[:100]}...")

# Test 3: Convert from string
print("\n3. Converting from data URI:")
data_uri = "data:text/plain;charset=utf-8,안녕하세요! VoidLight MarkItDown 테스트입니다."
result = converter.convert_uri(data_uri)
print(f"   Result: {result.markdown}")

# Test 4: Check registered converters
print("\n4. Registered converters:")
print(f"   Total: {len(converter._converters)}")
converter_names = [type(reg.converter).__name__ for reg in converter._converters]
print(f"   Types: {', '.join(sorted(set(converter_names)))}")

print("\n=== Test Complete ===")