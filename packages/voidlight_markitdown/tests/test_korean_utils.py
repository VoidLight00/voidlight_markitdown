import pytest
from voidlight_markitdown._korean_utils import KoreanTextProcessor


class TestKoreanTextProcessor:
    """Test suite for KoreanTextProcessor."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.processor = KoreanTextProcessor()
    
    def test_is_korean_char(self):
        """Test Korean character detection."""
        # Test Hangul characters
        assert KoreanTextProcessor.is_korean_char('가')
        assert KoreanTextProcessor.is_korean_char('힣')
        assert KoreanTextProcessor.is_korean_char('ㄱ')
        assert KoreanTextProcessor.is_korean_char('ㅏ')
        
        # Test non-Korean characters
        assert not KoreanTextProcessor.is_korean_char('A')
        assert not KoreanTextProcessor.is_korean_char('1')
        assert not KoreanTextProcessor.is_korean_char('中')
        assert not KoreanTextProcessor.is_korean_char(' ')
    
    def test_is_hanja_char(self):
        """Test Hanja (Chinese character) detection."""
        # Test Hanja characters
        assert KoreanTextProcessor.is_hanja_char('中')
        assert KoreanTextProcessor.is_hanja_char('國')
        assert KoreanTextProcessor.is_hanja_char('愛')
        
        # Test non-Hanja characters
        assert not KoreanTextProcessor.is_hanja_char('가')
        assert not KoreanTextProcessor.is_hanja_char('A')
        assert not KoreanTextProcessor.is_hanja_char('1')
    
    def test_detect_korean_ratio(self):
        """Test Korean text ratio detection."""
        # Pure Korean text
        assert KoreanTextProcessor.detect_korean_ratio('안녕하세요') == 1.0
        
        # Mixed text
        ratio = KoreanTextProcessor.detect_korean_ratio('Hello 안녕')
        assert 0.3 < ratio < 0.4  # 2 Korean chars out of 7 total
        
        # No Korean
        assert KoreanTextProcessor.detect_korean_ratio('Hello World') == 0.0
        
        # Empty text
        assert KoreanTextProcessor.detect_korean_ratio('') == 0.0
    
    def test_normalize_korean_text(self):
        """Test Korean text normalization."""
        # Test whitespace normalization
        text = "안녕  하세요\n\n\n여러분"
        normalized = self.processor.normalize_korean_text(text)
        assert "  " not in normalized
        assert "\n\n\n" not in normalized
        
        # Test zero-width character removal
        text = "안녕\u200b하세요"  # Zero-width space
        normalized = self.processor.normalize_korean_text(text)
        assert '\u200b' not in normalized
        
        # Test mojibake patterns
        text = "안녕하세요 占쏙옙"
        normalized = self.processor.normalize_korean_text(text)
        assert '占쏙옙' not in normalized
        assert '?' in normalized
    
    def test_fix_korean_line_breaks(self):
        """Test Korean line break fixing."""
        # Test inappropriate line break removal
        text = "안녕하\n세요"
        fixed = self.processor.fix_korean_line_breaks(text)
        assert fixed == "안녕하 세요"
        
        # Test preserving line breaks after punctuation
        text = "안녕하세요.\n반갑습니다"
        fixed = self.processor.fix_korean_line_breaks(text)
        assert fixed == "안녕하세요.\n반갑습니다"
        
        # Test excessive line break removal
        text = "안녕\n\n\n\n하세요"
        fixed = self.processor.fix_korean_line_breaks(text)
        assert "\n\n\n" not in fixed
    
    def test_smart_decode(self):
        """Test smart decoding with Korean encodings."""
        # Test UTF-8
        text = "안녕하세요"
        encoded = text.encode('utf-8')
        decoded = KoreanTextProcessor.smart_decode(encoded)
        assert decoded == text
        
        # Test EUC-KR
        text = "한글 테스트"
        encoded = text.encode('euc-kr')
        decoded = KoreanTextProcessor.smart_decode(encoded)
        assert decoded == text
        
        # Test CP949
        text = "확장 완성형 한글"
        encoded = text.encode('cp949')
        decoded = KoreanTextProcessor.smart_decode(encoded)
        assert decoded == text
    
    def test_tokenize(self):
        """Test Korean tokenization."""
        text = "안녕하세요. 오늘 날씨가 좋네요."
        tokens = self.processor.tokenize(text)
        
        # Should return list of (token, pos) tuples
        assert isinstance(tokens, list)
        if tokens:  # Only test if tokenizer is available
            assert all(isinstance(t, tuple) and len(t) == 2 for t in tokens)
            assert any('안녕' in t[0] for t in tokens)
    
    def test_extract_nouns(self):
        """Test noun extraction."""
        text = "오늘 날씨가 정말 좋습니다. 공원에서 산책하고 싶어요."
        nouns = self.processor.extract_nouns(text)
        
        # Should return list of nouns
        assert isinstance(nouns, list)
        if nouns:  # Only test if tokenizer is available
            # Common nouns that should be extracted
            expected_nouns = ['오늘', '날씨', '공원', '산책']
            assert any(noun in nouns for noun in expected_nouns)
    
    def test_extract_korean_metadata(self):
        """Test Korean metadata extraction."""
        text = "안녕하세요. 오늘은 좋은 날입니다. Hello, world! 中國"
        metadata = self.processor.extract_korean_metadata(text)
        
        # Check metadata structure
        assert 'korean_ratio' in metadata
        assert 'has_korean' in metadata
        assert 'has_hanja' in metadata
        assert 'has_mixed_script' in metadata
        assert 'char_count' in metadata
        assert 'word_count' in metadata
        assert 'sentence_count' in metadata
        
        # Check metadata values
        assert metadata['has_korean'] is True
        assert metadata['has_hanja'] is True
        assert metadata['has_mixed_script'] is True
        assert metadata['sentence_count'] >= 2
        assert 0 < metadata['korean_ratio'] < 1
    
    def test_segment_sentences(self):
        """Test Korean sentence segmentation."""
        text = "안녕하세요. 반갑습니다! 오늘 날씨는 어떤가요? 좋은 하루 되세요."
        sentences = self.processor.segment_sentences(text)
        
        assert isinstance(sentences, list)
        assert len(sentences) >= 3
        assert any('안녕하세요' in s for s in sentences)
        assert any('반갑습니다' in s for s in sentences)
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "인공지능 기술이 빠르게 발전하고 있습니다. 인공지능은 우리 생활을 크게 변화시키고 있습니다."
        keywords = self.processor.extract_keywords(text, num_keywords=5)
        
        assert isinstance(keywords, list)
        if keywords:
            # Should return (keyword, score) tuples
            assert all(isinstance(k, tuple) and len(k) == 2 for k in keywords)
            # '인공지능' should be a top keyword due to frequency
            top_keywords = [k[0] for k in keywords]
            if self.processor.kiwi or self.processor.okt:
                assert '인공지능' in top_keywords
    
    def test_preprocess_korean_document(self):
        """Test complete Korean document preprocessing."""
        text = """안녕하세요.  

        오늘은   정말 
좋은 날씨입니다.

        여러분 모두 행복한 하루 되세요！"""
        
        processed = self.processor.preprocess_korean_document(text)
        
        # Check that preprocessing was applied
        assert "  " not in processed  # No double spaces
        assert "\n\n\n" not in processed  # No excessive line breaks
        assert processed.count('\n') < text.count('\n')  # Reduced line breaks


if __name__ == '__main__':
    pytest.main([__file__, '-v'])