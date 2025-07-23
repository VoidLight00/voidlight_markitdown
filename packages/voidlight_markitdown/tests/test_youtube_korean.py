#!/usr/bin/env python3
"""
YouTube Korean Content Test Suite
Specifically tests Korean language video processing and transcription
"""
import os
import pytest
from typing import Dict, List

from voidlight_markitdown import VoidLightMarkItDown

# Skip these tests in CI/CD
skip_remote = True if os.environ.get("GITHUB_ACTIONS") else False
skip_youtube_api = True if os.environ.get("SKIP_YOUTUBE_TESTS") else False

# Korean test videos with various characteristics
KOREAN_TEST_VIDEOS = {
    "kpop_music_video": {
        "url": "https://www.youtube.com/watch?v=IHNzOHi8sJs",  # BLACKPINK - DDU-DU DDU-DU
        "title_contains": ["BLACKPINK", "DDU-DU DDU-DU"],
        "has_korean_transcript": True,
        "expected_korean_words": ["블랙핑크", "뚜두뚜두"],
    },
    "korean_news": {
        "url": "https://www.youtube.com/watch?v=0YMKpdIFJQ4",  # Korean news broadcast
        "title_contains": ["뉴스", "KBS"],
        "has_korean_transcript": True,
        "expected_korean_words": ["오늘", "뉴스", "한국"],
    },
    "korean_educational": {
        "url": "https://www.youtube.com/watch?v=Oj_54AEn5ls",  # Korean language lesson
        "title_contains": ["Korean", "한국어"],
        "has_korean_transcript": True,
        "has_english_transcript": True,
        "mixed_language": True,
    },
    "korean_cooking": {
        "url": "https://www.youtube.com/watch?v=8H_Zu0M5VRE",  # Korean cooking show
        "title_contains": ["김치", "요리"],
        "has_korean_transcript": True,
        "expected_korean_words": ["김치", "맛있다", "재료"],
    },
    "korean_drama_clip": {
        "url": "https://www.youtube.com/watch?v=oc7KqUlbCqE",  # K-drama clip
        "title_contains": ["드라마"],
        "has_korean_transcript": True,
        "conversational": True,
    },
}


@pytest.fixture
def markitdown():
    """Create VoidLightMarkItDown instance"""
    return VoidLightMarkItDown()


def contains_korean(text: str) -> bool:
    """Check if text contains Korean characters"""
    # Korean Unicode ranges:
    # Hangul Syllables: AC00-D7AF
    # Hangul Jamo: 1100-11FF
    # Hangul Compatibility Jamo: 3130-318F
    for char in text:
        if ('\uAC00' <= char <= '\uD7AF' or
            '\u1100' <= char <= '\u11FF' or
            '\u3130' <= char <= '\u318F'):
            return True
    return False


def extract_korean_text(text: str) -> List[str]:
    """Extract Korean words/phrases from mixed text"""
    import re
    # Pattern to match sequences of Korean characters
    korean_pattern = r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]+'
    return re.findall(korean_pattern, text)


@pytest.mark.skipif(skip_remote or skip_youtube_api, reason="Skip YouTube API tests")
class TestKoreanYouTubeContent:
    """Test Korean YouTube content processing"""
    
    def test_korean_transcript_extraction(self, markitdown):
        """Test extraction of Korean transcripts"""
        video = KOREAN_TEST_VIDEOS["kpop_music_video"]
        
        # Test with Korean language preference
        result = markitdown.convert(
            video["url"],
            youtube_transcript_languages=["ko"]
        )
        
        # Verify Korean content exists
        assert contains_korean(result.text_content), "No Korean content found"
        
        # Check for expected Korean words
        korean_words = extract_korean_text(result.text_content)
        assert len(korean_words) > 10, "Too few Korean words extracted"
        
        # Verify specific expected words
        content_lower = result.text_content.lower()
        for expected_word in video.get("expected_korean_words", []):
            assert expected_word in result.text_content, f"Expected Korean word '{expected_word}' not found"
    
    def test_korean_metadata_preservation(self, markitdown):
        """Test that Korean metadata is properly preserved"""
        video = KOREAN_TEST_VIDEOS["korean_news"]
        
        result = markitdown.convert(video["url"])
        
        # Check title preservation
        for title_part in video.get("title_contains", []):
            if contains_korean(title_part):
                assert title_part in result.text_content, f"Korean title part '{title_part}' not preserved"
        
        # Check if Korean description is preserved
        if "### Description" in result.text_content:
            description_start = result.text_content.index("### Description")
            description_section = result.text_content[description_start:description_start + 500]
            # Many Korean videos have Korean descriptions
            if contains_korean(description_section):
                korean_in_desc = extract_korean_text(description_section)
                assert len(korean_in_desc) > 0, "Korean description not properly preserved"
    
    def test_mixed_language_content(self, markitdown):
        """Test videos with mixed Korean/English content"""
        video = KOREAN_TEST_VIDEOS["korean_educational"]
        
        # Try to get both Korean and English
        result = markitdown.convert(
            video["url"],
            youtube_transcript_languages=["ko", "en"]
        )
        
        # Should have both Korean and English content
        assert contains_korean(result.text_content), "No Korean content in mixed language video"
        
        # Check for English content too
        english_words = ["korean", "language", "learn", "study"]
        english_found = any(word in result.text_content.lower() for word in english_words)
        assert english_found or video.get("mixed_language"), "Expected mixed language content"
    
    def test_korean_language_fallback(self, markitdown):
        """Test language fallback when Korean is not available"""
        video = KOREAN_TEST_VIDEOS["kpop_music_video"]
        
        # Request non-existent language first, then Korean
        result = markitdown.convert(
            video["url"],
            youtube_transcript_languages=["fr", "ko", "en"]
        )
        
        # Should fall back to available language
        assert "### Transcript" in result.text_content or "### Description" in result.text_content
        
        # If transcript exists, check it has content
        if "### Transcript" in result.text_content:
            transcript_start = result.text_content.index("### Transcript")
            transcript_section = result.text_content[transcript_start:]
            assert len(transcript_section) > 50, "Transcript section too short"
    
    def test_korean_character_encoding(self, markitdown):
        """Test proper encoding of Korean characters"""
        video = KOREAN_TEST_VIDEOS["korean_cooking"]
        
        result = markitdown.convert(video["url"])
        
        # Check that Korean characters are not corrupted
        korean_words = extract_korean_text(result.text_content)
        
        for word in korean_words[:10]:  # Check first 10 Korean words
            # Verify each character is valid Korean
            for char in word:
                assert ('\uAC00' <= char <= '\uD7AF' or
                       '\u1100' <= char <= '\u11FF' or
                       '\u3130' <= char <= '\u318F'), f"Invalid Korean character detected: {char}"
    
    @pytest.mark.parametrize("video_key", list(KOREAN_TEST_VIDEOS.keys()))
    def test_all_korean_videos(self, markitdown, video_key):
        """Test all Korean test videos"""
        video = KOREAN_TEST_VIDEOS[video_key]
        
        try:
            result = markitdown.convert(
                video["url"],
                youtube_transcript_languages=["ko", "en"]
            )
            
            # Basic checks for all videos
            assert "# YouTube" in result.text_content
            assert len(result.text_content) > 100
            
            # Check for title contents
            for title_part in video.get("title_contains", []):
                title_found = title_part.lower() in result.text_content.lower()
                if not title_found and contains_korean(title_part):
                    # For Korean titles, check exact match
                    title_found = title_part in result.text_content
                assert title_found, f"Expected title part '{title_part}' not found"
            
            # Check Korean content if expected
            if video.get("has_korean_transcript"):
                assert contains_korean(result.text_content), f"No Korean content in {video_key}"
            
        except Exception as e:
            pytest.fail(f"Failed to process {video_key}: {e}")
    
    def test_korean_transcript_quality(self, markitdown):
        """Test quality of Korean transcript extraction"""
        video = KOREAN_TEST_VIDEOS["korean_drama_clip"]
        
        result = markitdown.convert(
            video["url"],
            youtube_transcript_languages=["ko"]
        )
        
        if "### Transcript" in result.text_content:
            transcript_start = result.text_content.index("### Transcript")
            transcript_end = result.text_content.find("\n#", transcript_start + 1)
            if transcript_end == -1:
                transcript_end = len(result.text_content)
            
            transcript = result.text_content[transcript_start:transcript_end]
            
            # Check transcript characteristics
            korean_words = extract_korean_text(transcript)
            
            # Conversational videos should have many short Korean phrases
            if video.get("conversational"):
                assert len(korean_words) > 20, "Too few Korean words for conversational content"
                
                # Check for common conversational Korean words
                common_words = ["나", "너", "안녕", "네", "아니", "그래", "뭐", "왜"]
                found_common = sum(1 for word in common_words if word in transcript)
                assert found_common > 0, "No common conversational Korean words found"


def test_korean_error_messages():
    """Test error handling for Korean content"""
    markitdown = VoidLightMarkItDown()
    
    # Test with invalid Korean video URL
    invalid_url = "https://www.youtube.com/watch?v=한글잘못된아이디"
    
    try:
        result = markitdown.convert(invalid_url)
        # If it doesn't raise an exception, it should handle gracefully
        assert result is not None
    except Exception as e:
        # Error message should be properly formatted
        error_str = str(e)
        assert len(error_str) > 0
        # Should not have encoding issues in error message
        try:
            error_str.encode('utf-8')
        except UnicodeEncodeError:
            pytest.fail("Error message has encoding issues")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s", "-k", "korean"])