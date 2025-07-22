import pytest
import os
import tempfile
from pathlib import Path
from voidlight_markitdown import VoidLightMarkItDown, DocumentConverterResult


class TestVoidLightMarkItDown:
    """Test suite for VoidLightMarkItDown main functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.converter = VoidLightMarkItDown()
        self.korean_converter = VoidLightMarkItDown(korean_mode=True)
    
    def test_initialization(self):
        """Test VoidLightMarkItDown initialization."""
        # Test default initialization
        converter = VoidLightMarkItDown()
        assert converter._korean_mode is False
        assert converter._normalize_korean is True
        assert converter._korean_processor is None
        
        # Test Korean mode initialization
        korean_converter = VoidLightMarkItDown(korean_mode=True, normalize_korean=False)
        assert korean_converter._korean_mode is True
        assert korean_converter._normalize_korean is False
        assert korean_converter._korean_processor is not None
    
    def test_convert_plain_text(self):
        """Test plain text conversion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, World!\n안녕하세요!")
            temp_path = f.name
        
        try:
            # Test standard conversion
            result = self.converter.convert(temp_path)
            assert isinstance(result, DocumentConverterResult)
            assert "Hello, World!" in result.text_content
            assert "안녕하세요!" in result.text_content
            
            # Test Korean mode conversion
            result = self.korean_converter.convert(temp_path)
            assert isinstance(result, DocumentConverterResult)
            assert "안녕하세요!" in result.text_content
        finally:
            os.unlink(temp_path)
    
    def test_convert_korean_encoding(self):
        """Test conversion of Korean text with different encodings."""
        test_text = "한글 인코딩 테스트입니다."
        
        # Test EUC-KR encoding
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            f.write(test_text.encode('euc-kr'))
            temp_path = f.name
        
        try:
            result = self.korean_converter.convert(temp_path)
            assert isinstance(result, DocumentConverterResult)
            # The text should be properly decoded
            assert "한글" in result.text_content
            assert "인코딩" in result.text_content
            assert "테스트" in result.text_content
        finally:
            os.unlink(temp_path)
        
        # Test CP949 encoding
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            f.write(test_text.encode('cp949'))
            temp_path = f.name
        
        try:
            result = self.korean_converter.convert(temp_path)
            assert isinstance(result, DocumentConverterResult)
            assert "한글" in result.text_content
        finally:
            os.unlink(temp_path)
    
    def test_convert_html_korean(self):
        """Test HTML conversion with Korean content."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>한국어 테스트</title>
        </head>
        <body>
            <h1>안녕하세요</h1>
            <p>이것은 한국어 HTML 문서입니다.</p>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            result = self.korean_converter.convert(temp_path)
            assert isinstance(result, DocumentConverterResult)
            assert "안녕하세요" in result.text_content
            assert "한국어 HTML 문서" in result.text_content
        finally:
            os.unlink(temp_path)
    
    def test_convert_csv_korean(self):
        """Test CSV conversion with Korean content."""
        csv_content = """이름,나이,직업
김철수,30,개발자
이영희,25,디자이너
박민수,35,관리자"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            result = self.korean_converter.convert(temp_path)
            assert isinstance(result, DocumentConverterResult)
            assert "김철수" in result.text_content
            assert "개발자" in result.text_content
            assert "디자이너" in result.text_content
        finally:
            os.unlink(temp_path)
    
    def test_convert_uri(self):
        """Test URI conversion."""
        # Test data URI
        data_uri = "data:text/plain;charset=utf-8,안녕하세요%20World!"
        result = self.converter.convert_uri(data_uri)
        assert isinstance(result, DocumentConverterResult)
        assert "안녕하세요" in result.text_content
        assert "World!" in result.text_content
        
        # Test file URI
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("File URI test")
            temp_path = f.name
        
        try:
            file_uri = f"file://{temp_path}"
            result = self.converter.convert_uri(file_uri)
            assert isinstance(result, DocumentConverterResult)
            assert "File URI test" in result.text_content
        finally:
            os.unlink(temp_path)
    
    def test_korean_text_normalization(self):
        """Test Korean text normalization in conversion."""
        # Create text with normalization issues
        text_with_issues = """안녕하세요...  

        저는   김철수입니다.
        
        
        
        오늘날씨가좋네요ㅋㅋㅋㅋㅋㅋㅋㅋ"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text_with_issues)
            temp_path = f.name
        
        try:
            # Test with normalization enabled (default)
            result = self.korean_converter.convert(temp_path)
            content = result.text_content
            
            # Check normalization effects
            assert "  " not in content  # No double spaces
            assert "\n\n\n" not in content  # No excessive line breaks
            
            # Test with normalization disabled
            converter_no_norm = VoidLightMarkItDown(korean_mode=True, normalize_korean=False)
            result_no_norm = converter_no_norm.convert(temp_path)
            
            # Without normalization, issues might remain
            # (but basic line break normalization still happens in _convert)
            assert len(result_no_norm.text_content) >= len(result.text_content)
        finally:
            os.unlink(temp_path)
    
    def test_converter_registration(self):
        """Test converter registration and priority."""
        # Create a simple test converter
        from voidlight_markitdown._base_converter import DocumentConverter, DocumentConverterResult
        
        class TestConverter(DocumentConverter):
            def accepts(self, file_stream, stream_info, **kwargs):
                return stream_info.extension == '.test'
            
            def convert(self, file_stream, stream_info, **kwargs):
                return DocumentConverterResult(text_content="Test converter output")
        
        # Register the converter
        converter = VoidLightMarkItDown()
        test_converter = TestConverter()
        converter.register_converter(test_converter, priority=5.0)
        
        # Verify it's registered
        assert any(reg.converter == test_converter for reg in converter._converters)
        
        # Find the registration and check priority
        for reg in converter._converters:
            if reg.converter == test_converter:
                assert reg.priority == 5.0
                break
    
    def test_error_handling(self):
        """Test error handling in conversion."""
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            self.converter.convert("/non/existent/file.txt")
        
        # Test with invalid URI
        with pytest.raises(ValueError):
            self.converter.convert_uri("invalid://uri")
        
        # Test with empty data URI
        with pytest.raises(ValueError):
            self.converter.convert_uri("data:")
    
    def test_stream_conversion(self):
        """Test stream conversion."""
        import io
        
        # Create a byte stream
        text = "Stream conversion test\n스트림 변환 테스트"
        stream = io.BytesIO(text.encode('utf-8'))
        
        # Test conversion
        result = self.converter.convert_stream(stream)
        assert isinstance(result, DocumentConverterResult)
        assert "Stream conversion test" in result.text_content
        assert "스트림 변환 테스트" in result.text_content
        
        # Test Korean mode
        stream.seek(0)
        result = self.korean_converter.convert_stream(stream)
        assert isinstance(result, DocumentConverterResult)
        assert "스트림 변환 테스트" in result.text_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])