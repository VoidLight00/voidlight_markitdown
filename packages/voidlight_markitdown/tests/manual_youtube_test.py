#!/usr/bin/env python3
"""
Manual YouTube Testing Tool
Allows testing specific YouTube videos and inspecting the output
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidlight_markitdown import VoidLightMarkItDown


class YouTubeTestTool:
    """Interactive YouTube testing tool"""
    
    def __init__(self):
        self.markitdown = VoidLightMarkItDown()
        self.test_history = []
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        parsed = urlparse(url)
        if parsed.hostname in ['www.youtube.com', 'youtube.com']:
            if parsed.path == '/watch':
                params = parse_qs(parsed.query)
                return params.get('v', [None])[0]
        elif parsed.hostname == 'youtu.be':
            return parsed.path[1:]
        return None
    
    def test_video(self, url: str, languages: list = None, save_output: bool = False):
        """Test a single YouTube video"""
        print(f"\n{'='*60}")
        print(f"Testing YouTube Video")
        print(f"URL: {url}")
        
        video_id = self.extract_video_id(url)
        if video_id:
            print(f"Video ID: {video_id}")
        
        if languages:
            print(f"Preferred Languages: {', '.join(languages)}")
        
        print(f"{'='*60}\n")
        
        # Start timing
        start_time = time.time()
        
        try:
            # Convert with optional language preferences
            kwargs = {}
            if languages:
                kwargs['youtube_transcript_languages'] = languages
            
            result = self.markitdown.convert(url, **kwargs)
            duration = time.time() - start_time
            
            # Analyze results
            content = result.text_content
            
            print(f"✓ Conversion successful in {duration:.2f} seconds")
            print(f"\nContent Analysis:")
            print(f"- Total length: {len(content)} characters")
            print(f"- Title found: {'Yes' if result.title else 'No'}")
            print(f"- Has transcript: {'Yes' if '### Transcript' in content else 'No'}")
            print(f"- Has description: {'Yes' if '### Description' in content else 'No'}")
            print(f"- Has metadata: {'Yes' if '### Video Metadata' in content else 'No'}")
            
            # Check for Korean content
            has_korean = any('\uac00' <= char <= '\ud7af' for char in content)
            if has_korean:
                print(f"- Contains Korean text: Yes")
            
            # Extract sections
            sections = self._extract_sections(content)
            print(f"\nSections found:")
            for section, length in sections.items():
                print(f"- {section}: {length} characters")
            
            # Show preview
            print(f"\n{'='*60}")
            print("CONTENT PREVIEW (first 1000 characters):")
            print(f"{'='*60}")
            print(content[:1000])
            if len(content) > 1000:
                print(f"\n... (truncated, {len(content) - 1000} more characters)")
            
            # Save output if requested
            if save_output:
                filename = f"youtube_test_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"\n✓ Output saved to: {filename}")
            
            # Record test
            self.test_history.append({
                "url": url,
                "video_id": video_id,
                "success": True,
                "duration": duration,
                "content_length": len(content),
                "has_transcript": '### Transcript' in content,
                "has_korean": has_korean,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"✗ Conversion failed after {duration:.2f} seconds")
            print(f"Error: {e}")
            
            # Show detailed error for debugging
            import traceback
            print(f"\nDetailed error:")
            traceback.print_exc()
            
            # Record failed test
            self.test_history.append({
                "url": url,
                "video_id": video_id,
                "success": False,
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def _extract_sections(self, content: str) -> dict:
        """Extract sections from markdown content"""
        sections = {}
        lines = content.split('\n')
        
        current_section = "Header"
        section_start = 0
        
        for i, line in enumerate(lines):
            if line.startswith('###'):
                if current_section != "Header":
                    sections[current_section] = sum(len(l) for l in lines[section_start:i])
                current_section = line.strip('# ').strip()
                section_start = i
        
        # Add last section
        if current_section != "Header":
            sections[current_section] = sum(len(l) for l in lines[section_start:])
        
        return sections
    
    def test_multiple_videos(self, urls: list, languages: list = None):
        """Test multiple videos in sequence"""
        print(f"\nTesting {len(urls)} videos...")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Testing video...")
            self.test_video(url, languages)
            
            # Rate limiting
            if i < len(urls):
                print(f"\nWaiting 3 seconds before next request...")
                time.sleep(3)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        if not self.test_history:
            print("\nNo tests run yet.")
            return
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        total = len(self.test_history)
        successful = sum(1 for t in self.test_history if t['success'])
        failed = total - successful
        
        print(f"\nTotal tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {successful/total*100:.1f}%")
        
        # Successful test stats
        successful_tests = [t for t in self.test_history if t['success']]
        if successful_tests:
            avg_duration = sum(t['duration'] for t in successful_tests) / len(successful_tests)
            avg_content = sum(t['content_length'] for t in successful_tests) / len(successful_tests)
            with_transcript = sum(1 for t in successful_tests if t['has_transcript'])
            with_korean = sum(1 for t in successful_tests if t.get('has_korean', False))
            
            print(f"\nSuccessful test statistics:")
            print(f"- Average duration: {avg_duration:.2f} seconds")
            print(f"- Average content length: {avg_content:.0f} characters")
            print(f"- With transcript: {with_transcript}/{len(successful_tests)} ({with_transcript/len(successful_tests)*100:.1f}%)")
            print(f"- With Korean content: {with_korean}/{len(successful_tests)} ({with_korean/len(successful_tests)*100:.1f}%)")
        
        # Failed test summary
        if failed > 0:
            print(f"\nFailed tests:")
            for test in self.test_history:
                if not test['success']:
                    print(f"- {test['url']}: {test.get('error', 'Unknown error')}")
    
    def save_test_report(self, filename: str = "youtube_test_report.json"):
        """Save test report to file"""
        report = {
            "test_date": datetime.now().isoformat(),
            "total_tests": len(self.test_history),
            "tests": self.test_history,
            "summary": {
                "successful": sum(1 for t in self.test_history if t['success']),
                "failed": sum(1 for t in self.test_history if not t['success']),
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nTest report saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Test YouTube video conversion")
    parser.add_argument("urls", nargs='+', help="YouTube video URL(s) to test")
    parser.add_argument("-l", "--languages", nargs='+', help="Preferred transcript languages (e.g., ko en)")
    parser.add_argument("-s", "--save", action="store_true", help="Save output to file")
    parser.add_argument("-r", "--report", action="store_true", help="Save test report")
    
    args = parser.parse_args()
    
    # Create test tool
    tool = YouTubeTestTool()
    
    # Test videos
    if len(args.urls) == 1:
        tool.test_video(args.urls[0], args.languages, args.save)
    else:
        tool.test_multiple_videos(args.urls, args.languages)
    
    # Save report if requested
    if args.report:
        tool.save_test_report()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show example usage
        print("YouTube Video Testing Tool")
        print("\nExample usage:")
        print("  python manual_youtube_test.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("  python manual_youtube_test.py https://www.youtube.com/watch?v=IHNzOHi8sJs -l ko en")
        print("  python manual_youtube_test.py URL1 URL2 URL3 -r")
        print("\nTest videos:")
        print("  English: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("  Korean: https://www.youtube.com/watch?v=IHNzOHi8sJs")
        print("  No captions: https://www.youtube.com/watch?v=aqz-KE-bpKQ")
    else:
        main()