#!/usr/bin/env python3
"""Test script to verify VoidLight MarkItDown's architecture alignment with original MarkItDown."""

import sys
import io
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "voidlight_markitdown" / "src"))

from voidlight_markitdown import VoidLightMarkItDown
from voidlight_markitdown._stream_info import StreamInfo
from voidlight_markitdown._base_converter import DocumentConverter, DocumentConverterResult

def test_plain_text_conversion():
    """Test that plain text conversion works with stream-based architecture."""
    print("Testing plain text conversion with stream-based architecture...")
    
    # Create a VoidLightMarkItDown instance
    vmd = VoidLightMarkItDown(enable_builtins=True)
    
    # Test content
    test_content = "This is a test document.\n\nIt contains multiple lines."
    
    # Test 1: Convert from string (file path)
    with open("/tmp/test.txt", "w") as f:
        f.write(test_content)
    
    result1 = vmd.convert("/tmp/test.txt")
    print(f"✓ File path conversion: {len(result1.markdown)} chars")
    
    # Test 2: Convert from stream
    stream = io.BytesIO(test_content.encode('utf-8'))
    result2 = vmd.convert(stream, stream_info=StreamInfo(extension=".txt"))
    print(f"✓ Stream conversion: {len(result2.markdown)} chars")
    
    # Test 3: Verify both produce same result
    assert result1.markdown == result2.markdown, "File and stream conversions should produce same result"
    print("✓ File and stream conversions produce identical results")
    
    # Test 4: Check that converter uses accepts() and convert() methods
    from voidlight_markitdown.converters import PlainTextConverter
    converter = PlainTextConverter()
    
    # Reset stream
    stream.seek(0)
    
    # Test accepts method
    accepts = converter.accepts(stream, StreamInfo(extension=".txt"))
    assert accepts == True, "PlainTextConverter should accept .txt files"
    print("✓ PlainTextConverter.accepts() works correctly")
    
    # Reset stream position (important!)
    stream.seek(0)
    
    # Test convert method
    result3 = converter.convert(stream, StreamInfo(extension=".txt"))
    assert isinstance(result3, DocumentConverterResult), "Should return DocumentConverterResult"
    assert result3.markdown == test_content, "Direct converter should produce same content"
    print("✓ PlainTextConverter.convert() works correctly")
    
    print("\n✅ All tests passed! Architecture is properly aligned with stream-based design.")

def test_stream_info_compatibility():
    """Test that StreamInfo is compatible with original."""
    print("\nTesting StreamInfo compatibility...")
    
    # Test keyword-only arguments
    info = StreamInfo(
        mimetype="text/plain",
        extension=".txt",
        charset="utf-8",
        filename="test.txt",
        local_path="/tmp/test.txt",
        url=None
    )
    
    # Test copy_and_update
    info2 = info.copy_and_update(mimetype="text/html", extension=".html")
    assert info2.mimetype == "text/html"
    assert info2.extension == ".html"
    assert info2.charset == "utf-8"  # Should be preserved
    
    print("✓ StreamInfo is fully compatible")

if __name__ == "__main__":
    try:
        test_plain_text_conversion()
        test_stream_info_compatibility()
        print("\n🎉 Success! VoidLight MarkItDown is now fully aligned with the original's stream-based architecture.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)