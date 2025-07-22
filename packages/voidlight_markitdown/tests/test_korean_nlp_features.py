"""
Comprehensive tests for Korean NLP features with dependency checking.
"""

import pytest
import logging
from voidlight_markitdown._korean_utils import KoreanTextProcessor
from voidlight_markitdown._korean_nlp_init import get_korean_nlp_status


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


class TestKoreanNLPFeatures:
    """Test suite for advanced Korean NLP features."""
    
    @classmethod
    def setup_class(cls):
        """Setup for the test class."""
        cls.nlp_status = get_korean_nlp_status()
        cls.processor = KoreanTextProcessor()
        
        # Check which features are available
        cls.has_kiwi = cls.processor.kiwi is not None
        cls.has_okt = cls.processor.okt is not None
        cls.has_any_tokenizer = cls.has_kiwi or cls.has_okt
        
        # Print status for debugging
        print("\n" + "="*60)
        print("Korean NLP Test Environment Status")
        print("="*60)
        print(cls.nlp_status.get_status_report())
        print("="*60 + "\n")
    
    def test_nlp_initialization_status(self):
        """Test that NLP initialization provides proper status."""
        status = self.nlp_status.dependencies_status
        
        # Should have status for key components
        assert 'java' in status
        assert 'kiwipiepy' in status
        assert 'konlpy' in status
        
        # Java status should have required fields
        java_status = status['java']
        assert 'installed' in java_status
        assert 'version' in java_status
    
    def test_tokenization_with_normalization(self):
        """Test tokenization with text normalization."""
        # Text with spacing and encoding issues
        text = "안녕하세요.  오늘은   정말좋은날입니다."
        
        tokens = self.processor.tokenize(text, normalize=True)
        
        assert isinstance(tokens, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in tokens)
        
        if self.has_any_tokenizer:
            # Should have meaningful POS tags
            pos_tags = [pos for _, pos in tokens]
            assert any(pos not in ['UNK', 'NN'] for pos in pos_tags)
    
    def test_tokenization_fallback(self):
        """Test that tokenization has proper fallback."""
        text = "한글 테스트 문장입니다."
        tokens = self.processor.tokenize(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(t, tuple) and len(t) == 2 for t in tokens)
        
        # Even without NLP libraries, should provide basic POS tags
        token_text, pos = tokens[0]
        assert token_text == "한글"
        assert pos in ['NN', 'NNP', 'NNG', 'UNK']  # Basic POS guessing or Kiwi tags
    
    def test_spacing_correction(self):
        """Test Korean spacing correction."""
        # Text with incorrect spacing
        text = "안녕하세요오늘날씨가좋네요"
        
        corrected = self.processor.correct_spacing(text)
        
        if self.has_kiwi:
            # Kiwi should add proper spacing
            assert ' ' in corrected
            assert corrected != text
        else:
            # Without Kiwi, should return original
            assert corrected == text
    
    def test_morpheme_extraction(self):
        """Test morpheme extraction with detailed information."""
        text = "안녕하세요. 반갑습니다."
        
        morphemes = self.processor.get_morphemes(text)
        
        assert isinstance(morphemes, list)
        assert len(morphemes) > 0
        
        # Check morpheme structure
        for morpheme in morphemes:
            assert isinstance(morpheme, dict)
            assert 'surface' in morpheme
            assert 'pos' in morpheme
            assert 'lemma' in morpheme
            assert 'start' in morpheme
            assert 'end' in morpheme
        
        if self.has_kiwi:
            # Kiwi provides position information
            assert any(m['start'] >= 0 for m in morphemes)
    
    def test_sentence_segmentation_advanced(self):
        """Test advanced sentence segmentation."""
        # Complex text with quotes and various endings
        text = '''안녕하세요. "오늘 날씨가 좋네요!" 그가 말했다.
        내일은 비가 올까요? 모르겠습니다... 
        확인해 보세요.'''
        
        sentences = self.processor.segment_sentences(text)
        
        assert isinstance(sentences, list)
        assert len(sentences) >= 4
        
        # Check that quotes are handled properly
        assert any('"' in sent for sent in sentences)
        
        # Check various endings are preserved
        assert any(sent.endswith('.') for sent in sentences)
        assert any(sent.endswith('?') for sent in sentences)
        assert any(sent.endswith('...') for sent in sentences)
    
    def test_formality_analysis(self):
        """Test formality level analysis."""
        # Formal text
        formal_text = "안녕하십니까. 오늘 회의에 참석해 주셔서 감사합니다. 발표를 시작하겠습니다."
        formal_analysis = self.processor.analyze_formality(formal_text)
        
        assert formal_analysis['formality_level'] in ['formal', 'polite']
        assert formal_analysis['formal_endings'] > 0
        
        # Informal text  
        informal_text = "야, 오늘 뭐해? 같이 밥 먹자. 배고프다."
        informal_analysis = self.processor.analyze_formality(informal_text)
        
        assert informal_analysis['formality_level'] == 'informal'
        assert informal_analysis['informal_endings'] > 0
        
        # Mixed formality
        mixed_text = "안녕하세요. 오늘 날씨 좋네. 같이 가실래요?"
        mixed_analysis = self.processor.analyze_formality(mixed_text)
        
        assert mixed_analysis['formal_endings'] > 0
        assert mixed_analysis['informal_endings'] > 0
    
    def test_reading_difficulty_estimation(self):
        """Test reading difficulty estimation."""
        # Simple text
        simple_text = "안녕. 나는 학생이야. 학교에 가."
        simple_difficulty = self.processor.get_reading_difficulty(simple_text)
        
        assert simple_difficulty['level'] in ['beginner', 'intermediate']
        assert simple_difficulty['avg_sentence_length'] < 10
        
        # Complex text with Hanja
        complex_text = """韓國의 傳統文化는 오랜 歷史를 통해 발전해왔습니다. 
        특히 朝鮮時代의 儒敎的 價値觀은 현대 한국 사회에도 
        깊은 영향을 미치고 있으며, 이는 敎育制度와 社會構造에서 
        명확히 드러납니다."""
        
        complex_difficulty = self.processor.get_reading_difficulty(complex_text)
        
        assert complex_difficulty['level'] in ['intermediate', 'advanced']
        assert complex_difficulty['hanja_ratio'] > 0.1
        assert complex_difficulty['avg_sentence_length'] > 10
    
    def test_keyword_extraction_with_frequency(self):
        """Test keyword extraction with proper frequency analysis."""
        text = """인공지능 기술이 빠르게 발전하고 있습니다. 
        특히 자연어 처리 분야에서 인공지능의 발전이 두드러집니다.
        한국어 자연어 처리도 인공지능 덕분에 크게 향상되었습니다.
        앞으로 인공지능이 가져올 변화가 기대됩니다."""
        
        keywords = self.processor.extract_keywords(text, num_keywords=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        
        if keywords and self.has_any_tokenizer:
            # Check keyword structure
            assert all(isinstance(k, tuple) and len(k) == 2 for k in keywords)
            
            # '인공지능' should be top keyword due to frequency
            top_keywords = [k[0] for k in keywords[:3]]
            assert '인공지능' in top_keywords
            
            # Scores should be in descending order
            scores = [k[1] for k in keywords]
            assert scores == sorted(scores, reverse=True)
    
    def test_hanja_conversion(self):
        """Test Hanja to Hangul conversion."""
        text = "韓國語를 勉强합니다. 中國 文字도 있습니다."
        
        converted = self.processor.convert_hanja_to_hangul(text)
        
        # Check if conversion happened (depends on hanja module)
        from voidlight_markitdown._korean_utils import HANJA_AVAILABLE
        
        if HANJA_AVAILABLE:
            # Some Hanja should be converted
            assert converted != text
            # But Korean text should remain
            assert '합니다' in converted
        else:
            # Without hanja module, should return original
            assert converted == text
    
    def test_metadata_extraction_comprehensive(self):
        """Test comprehensive metadata extraction."""
        text = """안녕하세요! 오늘은 韓國語 수업입니다.
        Let's learn Korean together. 中文也可以。
        여러분 모두 열심히 공부하세요. 화이팅!"""
        
        metadata = self.processor.extract_korean_metadata(text)
        
        # Check all expected fields
        assert 'korean_ratio' in metadata
        assert 'has_korean' in metadata
        assert 'has_hanja' in metadata
        assert 'has_mixed_script' in metadata
        assert 'char_count' in metadata
        assert 'word_count' in metadata
        assert 'sentence_count' in metadata
        
        # Verify values
        assert metadata['has_korean'] is True
        assert metadata['has_hanja'] is True
        assert metadata['has_mixed_script'] is True
        assert 0 < metadata['korean_ratio'] < 1
        assert metadata['sentence_count'] >= 3
        
        if self.has_any_tokenizer:
            assert 'noun_count' in metadata
            assert metadata['noun_count'] > 0
            
            if 'top_nouns' in metadata:
                assert isinstance(metadata['top_nouns'], list)
    
    def test_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline."""
        # Messy text with various issues
        text = """안녕하세요...   

        오늘은  정말
좋은날씨네요！！！

中國語도   있고요
        
        占쏙옙 이상한 문자도 있어요"""
        
        processed = self.processor.preprocess_korean_document(text)
        
        # Check improvements
        assert '   ' not in processed  # No triple spaces
        assert '\n\n\n' not in processed  # No excessive newlines
        assert '占쏙옙' not in processed  # Mojibake fixed
        
        # Should preserve meaningful content
        assert '안녕하세요' in processed
        assert '좋은날씨네요' in processed or '좋은 날씨네요' in processed


class TestKoreanNLPErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.processor = KoreanTextProcessor()
    
    def test_empty_text_handling(self):
        """Test handling of empty or None text."""
        assert self.processor.tokenize('') == []
        assert self.processor.tokenize(None) == []
        assert self.processor.extract_nouns('') == []
        assert self.processor.segment_sentences('') == ['']
        assert self.processor.correct_spacing('') == ''
        assert self.processor.normalize_korean_text('') == ''
    
    def test_non_korean_text_handling(self):
        """Test handling of non-Korean text."""
        english_text = "Hello, this is English text."
        
        # Should handle gracefully
        tokens = self.processor.tokenize(english_text)
        assert len(tokens) > 0
        
        metadata = self.processor.extract_korean_metadata(english_text)
        assert metadata['has_korean'] is False
        assert metadata['korean_ratio'] == 0
    
    def test_mixed_script_edge_cases(self):
        """Test edge cases with mixed scripts."""
        # Numbers and Korean
        text1 = "2023년 12월 25일"
        tokens1 = self.processor.tokenize(text1)
        assert len(tokens1) > 0
        
        # Special characters
        text2 = "안녕하세요! @#$% ^&*()"
        tokens2 = self.processor.tokenize(text2)
        assert len(tokens2) > 0
        
        # Emoji and Korean
        text3 = "좋아요 👍 감사합니다 😊"
        tokens3 = self.processor.tokenize(text3)
        assert len(tokens3) > 0
    
    def test_long_text_handling(self):
        """Test handling of very long texts."""
        # Generate long text
        long_text = "안녕하세요. " * 1000
        
        # Should handle without crashing
        sentences = self.processor.segment_sentences(long_text)
        assert len(sentences) > 0
        
        # Metadata extraction should work
        metadata = self.processor.extract_korean_metadata(long_text)
        assert metadata['char_count'] > 5000
    
    def test_malformed_unicode_handling(self):
        """Test handling of malformed Unicode."""
        # Text with potential Unicode issues
        texts = [
            ("안\u200b녕하세요", "안녕하세요"),  # Zero-width space - should be removed
            ("안\ufeff녕하세요", "안녕하세요"),  # BOM - should be removed
            ("안\u00a0녕하세요", "안 녕하세요"),  # Non-breaking space - should be normalized to space
        ]
        
        for original, expected in texts:
            normalized = self.processor.normalize_korean_text(original)
            # Should handle problematic characters properly
            assert normalized == expected
            assert '안' in normalized and '녕하세요' in normalized


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])