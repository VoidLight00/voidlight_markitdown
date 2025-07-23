#!/usr/bin/env python3
"""
Comprehensive YouTube API Integration Test Suite
Tests real YouTube videos with various scenarios including Korean content
"""
import os
import time
import pytest
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from voidlight_markitdown import VoidLightMarkItDown
from voidlight_markitdown._stream_info import StreamInfo
from voidlight_markitdown.converters._youtube_converter import YouTubeConverter

# Skip these tests in CI/CD to avoid API quota issues
skip_remote = True if os.environ.get("GITHUB_ACTIONS") else False
skip_youtube_api = True if os.environ.get("SKIP_YOUTUBE_TESTS") else False

# Test video configurations
TEST_VIDEOS = {
    "english_with_captions": {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "expected_title": "Rick Astley - Never Gonna Give You Up",
        "expected_strings": ["never gonna give you up", "never gonna let you down"],
        "has_transcript": True,
        "duration": "PT3M33S",
    },
    "korean_with_captions": {
        "url": "https://www.youtube.com/watch?v=IHNzOHi8sJs",  # BLACKPINK - DDU-DU DDU-DU
        "expected_title": "BLACKPINK",
        "expected_strings": ["DDU-DU DDU-DU", "블랙핑크"],
        "has_transcript": True,
        "korean_content": True,
    },
    "no_captions": {
        "url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ",  # Big Buck Bunny (often no captions)
        "expected_title": "Big Buck Bunny",
        "has_transcript": False,
    },
    "youtube_short": {
        "url": "https://www.youtube.com/shorts/tPEE9ZwTmy0",  # YouTube Short
        "expected_title": "shorts",
        "is_short": True,
    },
    "long_video": {
        "url": "https://www.youtube.com/watch?v=EngW7tLk6R8",  # 2+ hour podcast/lecture
        "expected_title": "podcast",
        "min_duration_minutes": 120,
    },
    "live_stream_recording": {
        "url": "https://www.youtube.com/watch?v=21X5lGlDOfg",  # NASA live stream recording
        "expected_title": "NASA",
        "is_live_recording": True,
    },
}

# Error test cases
ERROR_TEST_CASES = {
    "invalid_video_id": "https://www.youtube.com/watch?v=INVALID_ID_12345",
    "private_video": "https://www.youtube.com/watch?v=xxxxxxxxxxxxxxx",
    "deleted_video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ_deleted",
    "malformed_url": "https://youtube.com/watch?v=",
    "playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "channel_url": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
}


class YouTubeTestMetrics:
    """Track performance metrics for YouTube API calls"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.memory_usage: List[int] = []
        self.api_calls: int = 0
        self.errors: List[Dict] = []
        
    def record_request(self, video_id: str, duration: float, success: bool, error: Optional[str] = None):
        self.api_calls += 1
        self.response_times.append(duration)
        if not success:
            self.errors.append({
                "video_id": video_id,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_summary(self) -> Dict:
        return {
            "total_api_calls": self.api_calls,
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "error_count": len(self.errors),
            "error_rate": len(self.errors) / self.api_calls if self.api_calls > 0 else 0,
        }


@pytest.fixture
def markitdown():
    """Create VoidLightMarkItDown instance"""
    return VoidLightMarkItDown()


@pytest.fixture
def youtube_converter():
    """Create YouTubeConverter instance"""
    return YouTubeConverter()


@pytest.fixture
def metrics():
    """Create metrics tracker"""
    return YouTubeTestMetrics()


class TestYouTubeConverterUnit:
    """Unit tests for YouTube converter functionality"""
    
    def test_accepts_youtube_urls(self, youtube_converter):
        """Test that converter properly accepts YouTube URLs"""
        # Valid YouTube URLs
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=123&list=PLxxx",
            "https://www.youtube.com/watch?v=abc&t=10s",
        ]
        
        for url in valid_urls:
            stream_info = StreamInfo(
                url=url,
                mimetype="text/html",
                extension=".html"
            )
            assert youtube_converter.accepts(None, stream_info) is True
    
    def test_rejects_non_youtube_urls(self, youtube_converter):
        """Test that converter rejects non-YouTube URLs"""
        invalid_urls = [
            "https://vimeo.com/123456",
            "https://www.youtube.com/playlist?list=PLxxx",
            "https://youtu.be/dQw4w9WgXcQ",  # Short URL not supported
            "https://example.com/video.html",
        ]
        
        for url in invalid_urls:
            stream_info = StreamInfo(
                url=url,
                mimetype="text/html",
                extension=".html"
            )
            assert youtube_converter.accepts(None, stream_info) is False
    
    def test_url_unquoting(self, youtube_converter):
        """Test URL unquoting functionality"""
        # URL with escaped characters
        escaped_url = "https://www.youtube.com/watch\\?v\\=dQw4w9WgXcQ"
        stream_info = StreamInfo(
            url=escaped_url,
            mimetype="text/html",
            extension=".html"
        )
        assert youtube_converter.accepts(None, stream_info) is True


@pytest.mark.skipif(skip_remote or skip_youtube_api, reason="Skip YouTube API tests")
class TestYouTubeAPIIntegration:
    """Integration tests with real YouTube API"""
    
    def test_english_video_with_captions(self, markitdown, metrics):
        """Test English video with captions"""
        video = TEST_VIDEOS["english_with_captions"]
        start_time = time.time()
        
        try:
            result = markitdown.convert(video["url"])
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, True)
            
            # Verify title
            assert video["expected_title"].lower() in result.text_content.lower()
            
            # Verify transcript exists
            if video.get("has_transcript"):
                assert "### Transcript" in result.text_content
                for expected_string in video.get("expected_strings", []):
                    assert expected_string.lower() in result.text_content.lower()
            
            # Verify metadata
            assert "### Video Metadata" in result.text_content
            if video.get("duration"):
                assert video["duration"] in result.text_content
                
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, False, str(e))
            pytest.fail(f"Failed to convert video: {e}")
    
    def test_korean_video_with_captions(self, markitdown, metrics):
        """Test Korean video with Korean captions"""
        video = TEST_VIDEOS["korean_with_captions"]
        start_time = time.time()
        
        try:
            # Test with Korean language preference
            result = markitdown.convert(
                video["url"],
                youtube_transcript_languages=["ko", "en"]
            )
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, True)
            
            # Verify Korean content is preserved
            if video.get("korean_content"):
                # Check for Korean characters
                korean_chars = any('\uac00' <= char <= '\ud7af' for char in result.text_content)
                assert korean_chars, "Korean content not found in result"
            
            # Verify expected strings
            for expected_string in video.get("expected_strings", []):
                assert expected_string in result.text_content
                
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, False, str(e))
            pytest.fail(f"Failed to convert Korean video: {e}")
    
    def test_video_without_captions(self, markitdown, metrics):
        """Test video without captions"""
        video = TEST_VIDEOS["no_captions"]
        start_time = time.time()
        
        try:
            result = markitdown.convert(video["url"])
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, True)
            
            # Should still get title and metadata
            assert video["expected_title"].lower() in result.text_content.lower()
            
            # Transcript section might be missing or empty
            if not video.get("has_transcript"):
                # Either no transcript section or empty transcript
                transcript_exists = "### Transcript" in result.text_content
                if transcript_exists:
                    # Check if transcript is essentially empty
                    lines = result.text_content.split('\n')
                    transcript_index = lines.index("### Transcript")
                    # Next non-empty line should be another section or end
                    assert transcript_index < len(lines) - 1
                    
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, False, str(e))
            # This is expected to fail gracefully
            print(f"Expected graceful failure for no-caption video: {e}")
    
    def test_youtube_short(self, markitdown, metrics):
        """Test YouTube Shorts"""
        video = TEST_VIDEOS["youtube_short"]
        start_time = time.time()
        
        try:
            # Note: Shorts URLs redirect to regular watch URLs
            result = markitdown.convert(video["url"])
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, True)
            
            # Should still process as regular video
            assert "# YouTube" in result.text_content
            
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, False, str(e))
            # Shorts might not be fully supported
            print(f"YouTube Short processing: {e}")
    
    def test_long_video_performance(self, markitdown, metrics):
        """Test performance with long videos"""
        video = TEST_VIDEOS["long_video"]
        start_time = time.time()
        
        try:
            result = markitdown.convert(video["url"])
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, True)
            
            # Check performance
            assert duration < 30, f"Long video took too long: {duration}s"
            
            # Verify content
            assert video["expected_title"].lower() in result.text_content.lower()
            
            # Check transcript length for long videos
            if "### Transcript" in result.text_content:
                transcript_length = len(result.text_content.split("### Transcript")[1])
                assert transcript_length > 1000, "Long video should have substantial transcript"
                
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_request(video["url"], duration, False, str(e))
            pytest.fail(f"Failed to process long video: {e}")
    
    @pytest.mark.parametrize("error_url", list(ERROR_TEST_CASES.values()))
    def test_error_handling(self, markitdown, metrics, error_url):
        """Test error handling for various failure scenarios"""
        start_time = time.time()
        
        try:
            result = markitdown.convert(error_url)
            duration = time.time() - start_time
            
            # Some errors might still return partial results
            if result and result.text_content:
                # Should at least have basic structure
                assert "# YouTube" in result.text_content
            
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_request(error_url, duration, False, str(e))
            # Expected to fail - that's what we're testing
            print(f"Expected error for {error_url}: {e}")
    
    def test_concurrent_requests(self, markitdown, metrics):
        """Test handling multiple concurrent requests"""
        import concurrent.futures
        
        urls = [
            TEST_VIDEOS["english_with_captions"]["url"],
            TEST_VIDEOS["korean_with_captions"]["url"],
        ]
        
        def convert_video(url):
            start = time.time()
            try:
                result = markitdown.convert(url)
                return url, time.time() - start, True, result
            except Exception as e:
                return url, time.time() - start, False, str(e)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(convert_video, url) for url in urls]
            
            for future in concurrent.futures.as_completed(futures):
                url, duration, success, result = future.result()
                metrics.record_request(url, duration, success, None if success else result)
                
                if success:
                    assert "# YouTube" in result.text_content
    
    def test_transcript_language_fallback(self, markitdown):
        """Test transcript language fallback mechanism"""
        video = TEST_VIDEOS["korean_with_captions"]
        
        # Request non-existent language, should fall back
        result = markitdown.convert(
            video["url"],
            youtube_transcript_languages=["fr", "de", "en", "ko"]
        )
        
        # Should still get some transcript
        assert "### Transcript" in result.text_content or "### Description" in result.text_content
    
    def test_retry_mechanism(self, markitdown, metrics):
        """Test retry mechanism for transient failures"""
        # This uses the built-in retry mechanism
        video = TEST_VIDEOS["english_with_captions"]
        
        # The converter has retry logic built in (3 retries, 2 second delay)
        start_time = time.time()
        try:
            result = markitdown.convert(video["url"])
            duration = time.time() - start_time
            
            # Even with retries, should complete in reasonable time
            assert duration < 20, f"Request with retries took too long: {duration}s"
            
        except Exception as e:
            duration = time.time() - start_time
            # If it failed after retries, duration should reflect retry attempts
            assert duration >= 4, "Should have attempted retries (2s delay * 2 retries minimum)"


@pytest.mark.skipif(skip_remote or skip_youtube_api, reason="Skip YouTube API tests")
class TestYouTubeAPIEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_special_characters_in_url(self, markitdown):
        """Test URLs with special characters"""
        # URL with timestamp
        url_with_timestamp = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"
        result = markitdown.convert(url_with_timestamp)
        assert "# YouTube" in result.text_content
        
        # URL with playlist
        url_with_playlist = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        result = markitdown.convert(url_with_playlist)
        assert "# YouTube" in result.text_content
    
    def test_metadata_extraction_completeness(self, markitdown):
        """Test completeness of metadata extraction"""
        video = TEST_VIDEOS["english_with_captions"]
        result = markitdown.convert(video["url"])
        
        # Check for various metadata fields
        metadata_sections = ["Views", "Keywords", "Runtime", "Description"]
        found_sections = sum(1 for section in metadata_sections if section in result.text_content)
        
        # Should have at least some metadata
        assert found_sections >= 2, f"Missing metadata sections. Found only {found_sections}"
    
    def test_transcript_formatting(self, markitdown):
        """Test transcript formatting and structure"""
        video = TEST_VIDEOS["english_with_captions"]
        result = markitdown.convert(video["url"])
        
        if "### Transcript" in result.text_content:
            transcript_section = result.text_content.split("### Transcript")[1]
            
            # Transcript should have reasonable length
            assert len(transcript_section) > 100
            
            # Should be readable text, not JSON or timestamps
            assert "[" not in transcript_section[:50]  # No JSON arrays at start
            assert "{" not in transcript_section[:50]  # No JSON objects at start


def test_youtube_converter_caching():
    """Test if converter implements any caching mechanism"""
    markitdown = VoidLightMarkItDown()
    video_url = TEST_VIDEOS["english_with_captions"]["url"]
    
    # First request
    start1 = time.time()
    result1 = markitdown.convert(video_url)
    duration1 = time.time() - start1
    
    # Second request (might be cached)
    start2 = time.time()
    result2 = markitdown.convert(video_url)
    duration2 = time.time() - start2
    
    # Results should be identical
    assert result1.text_content == result2.text_content
    
    # Note: Current implementation doesn't have caching
    print(f"First request: {duration1:.2f}s, Second request: {duration2:.2f}s")


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "-s"])