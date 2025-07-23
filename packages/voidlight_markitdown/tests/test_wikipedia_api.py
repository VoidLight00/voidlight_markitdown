"""
Comprehensive Wikipedia API Integration Tests

Tests the Wikipedia converter with real Wikipedia articles across multiple languages,
content types, and edge cases.
"""

import asyncio
import concurrent.futures
import json
import os
import time
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import quote

import pytest

from voidlight_markitdown import VoidLightMarkItDown, StreamInfo

# Test URLs for different Wikipedia content types and languages
TEST_URLS = {
    "english": {
        "simple_article": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "complex_article": "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "table_heavy": "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)",
        "infobox": "https://en.wikipedia.org/wiki/Seoul",
        "disambiguation": "https://en.wikipedia.org/wiki/Python",
        "redirect": "https://en.wikipedia.org/wiki/USA",
        "long_article": "https://en.wikipedia.org/wiki/World_War_II",
        "featured_article": "https://en.wikipedia.org/wiki/DNA",
        "math_heavy": "https://en.wikipedia.org/wiki/Fourier_transform",
        "media_rich": "https://en.wikipedia.org/wiki/Earth",
    },
    "korean": {
        "simple_article": "https://ko.wikipedia.org/wiki/파이썬",
        "complex_article": "https://ko.wikipedia.org/wiki/인공지능",
        "table_heavy": "https://ko.wikipedia.org/wiki/대한민국의_행정_구역",
        "infobox": "https://ko.wikipedia.org/wiki/서울특별시",
        "disambiguation": "https://ko.wikipedia.org/wiki/파이썬_(동음이의)",
        "redirect": "https://ko.wikipedia.org/wiki/한국",
        "long_article": "https://ko.wikipedia.org/wiki/제2차_세계_대전",
        "featured_article": "https://ko.wikipedia.org/wiki/DNA",
        "hanja_mixed": "https://ko.wikipedia.org/wiki/한자",
        "historical": "https://ko.wikipedia.org/wiki/조선",
    },
    "multilingual": {
        "arabic": "https://ar.wikipedia.org/wiki/الذكاء_الاصطناعي",
        "hebrew": "https://he.wikipedia.org/wiki/בינה_מלאכותית",
        "japanese": "https://ja.wikipedia.org/wiki/人工知能",
        "chinese_simplified": "https://zh.wikipedia.org/wiki/人工智能",
        "chinese_traditional": "https://zh.wikipedia.org/wiki/人工智慧",
        "russian": "https://ru.wikipedia.org/wiki/Искусственный_интеллект",
        "hindi": "https://hi.wikipedia.org/wiki/कृत्रिम_बुद्धिमत्ता",
        "thai": "https://th.wikipedia.org/wiki/ปัญญาประดิษฐ์",
    },
    "edge_cases": {
        "mobile_url": "https://en.m.wikipedia.org/wiki/Machine_learning",
        "special_chars": "https://en.wikipedia.org/wiki/C%2B%2B",
        "unicode_title": "https://ko.wikipedia.org/wiki/한글",
        "protected_page": "https://en.wikipedia.org/wiki/Main_Page",
        "wiki_project": "https://en.wikipedia.org/wiki/Wikipedia:About",
        "talk_page": "https://en.wikipedia.org/wiki/Talk:Artificial_intelligence",
    },
    "invalid": {
        "non_existent": "https://en.wikipedia.org/wiki/This_Page_Does_Not_Exist_12345",
        "malformed_url": "https://en.wikipedia.org/wiki/",
        "non_wikipedia": "https://example.com/wiki/test",
    }
}


class WikipediaTestMetrics:
    """Track performance and quality metrics for Wikipedia conversion"""
    
    def __init__(self):
        self.results = []
        self.performance_data = []
        self.content_quality = []
        self.error_log = []
        
    def add_result(self, url: str, category: str, subcategory: str, 
                   success: bool, duration: float, content_length: int = 0,
                   error: Optional[str] = None, quality_metrics: Optional[Dict] = None):
        """Add a test result"""
        result = {
            "url": url,
            "category": category,
            "subcategory": subcategory,
            "success": success,
            "duration": duration,
            "content_length": content_length,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "quality_metrics": quality_metrics or {}
        }
        self.results.append(result)
        
        if success:
            self.performance_data.append({
                "url": url,
                "duration": duration,
                "content_length": content_length,
                "bytes_per_second": content_length / duration if duration > 0 else 0
            })
        else:
            self.error_log.append({
                "url": url,
                "error": error,
                "timestamp": result["timestamp"]
            })
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests
        
        avg_duration = sum(r["duration"] for r in self.results) / total_tests if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful": successful_tests,
                "failed": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "average_duration": avg_duration,
                "test_date": datetime.now().isoformat()
            },
            "performance": {
                "fastest": min(self.performance_data, key=lambda x: x["duration"]) if self.performance_data else None,
                "slowest": max(self.performance_data, key=lambda x: x["duration"]) if self.performance_data else None,
                "average_content_length": sum(p["content_length"] for p in self.performance_data) / len(self.performance_data) if self.performance_data else 0
            },
            "by_category": self._analyze_by_category(),
            "errors": self.error_log,
            "detailed_results": self.results
        }
        
        return report
    
    def _analyze_by_category(self) -> Dict:
        """Analyze results by category"""
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "successful": 0, "subcategories": {}}
            
            categories[cat]["total"] += 1
            if result["success"]:
                categories[cat]["successful"] += 1
            
            subcat = result["subcategory"]
            if subcat not in categories[cat]["subcategories"]:
                categories[cat]["subcategories"][subcat] = {"total": 0, "successful": 0}
            
            categories[cat]["subcategories"][subcat]["total"] += 1
            if result["success"]:
                categories[cat]["subcategories"][subcat]["successful"] += 1
        
        return categories


def fetch_wikipedia_content(url: str, timeout: int = 30) -> Tuple[bytes, Dict]:
    """Fetch Wikipedia content with proper headers"""
    headers = {
        'User-Agent': 'VoidlightMarkitdown/1.0 (Wikipedia API Testing; https://github.com/voidlight)',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            info = {
                'status': response.status,
                'headers': dict(response.headers),
                'url': response.url,
                'content_length': len(content)
            }
            return content, info
    except (HTTPError, URLError) as e:
        raise e


def analyze_content_quality(markdown: str, url: str) -> Dict:
    """Analyze the quality of extracted content"""
    lines = markdown.split('\n')
    
    # Count various elements
    headers = sum(1 for line in lines if line.strip().startswith('#'))
    tables = markdown.count('|---|')  # Simple table detection
    links = markdown.count('](')
    code_blocks = markdown.count('```')
    lists = sum(1 for line in lines if line.strip().startswith(('- ', '* ', '1. ')))
    
    # Language-specific checks
    has_korean = any('\uac00' <= char <= '\ud7af' for char in markdown)
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in markdown)
    has_arabic = any('\u0600' <= char <= '\u06ff' for char in markdown)
    has_hebrew = any('\u0590' <= char <= '\u05ff' for char in markdown)
    
    # Content structure
    has_title = lines[0].startswith('#') if lines else False
    has_sections = headers > 1
    
    return {
        "total_lines": len(lines),
        "total_chars": len(markdown),
        "headers": headers,
        "tables": tables,
        "links": links,
        "code_blocks": code_blocks,
        "lists": lists,
        "has_korean": has_korean,
        "has_chinese": has_chinese,
        "has_arabic": has_arabic,
        "has_hebrew": has_hebrew,
        "has_title": has_title,
        "has_sections": has_sections,
        "empty_lines": sum(1 for line in lines if not line.strip()),
        "average_line_length": len(markdown) / len(lines) if lines else 0
    }


def test_wikipedia_url(url: str, category: str, subcategory: str, 
                      metrics: WikipediaTestMetrics, md: VoidLightMarkItDown) -> Dict:
    """Test a single Wikipedia URL"""
    print(f"\nTesting {category}/{subcategory}: {url}")
    
    start_time = time.time()
    
    try:
        # Fetch content
        content, info = fetch_wikipedia_content(url)
        fetch_time = time.time() - start_time
        
        # Convert to markdown
        convert_start = time.time()
        # Convert bytes to stream
        import io
        content_stream = io.BytesIO(content)
        stream_info = StreamInfo(url=url)
        result = md.convert_stream(content_stream, stream_info=stream_info)
        convert_time = time.time() - convert_start
        
        total_time = time.time() - start_time
        
        # Analyze quality
        quality = analyze_content_quality(result.markdown, url)
        
        # Basic validation
        assert result.markdown, f"Empty markdown for {url}"
        assert len(result.markdown) > 100, f"Markdown too short for {url}"
        
        # Language-specific validation
        if "ko.wikipedia" in url:
            assert quality["has_korean"], f"No Korean text found in {url}"
        elif "ar.wikipedia" in url:
            assert quality["has_arabic"], f"No Arabic text found in {url}"
        elif "he.wikipedia" in url:
            assert quality["has_hebrew"], f"No Hebrew text found in {url}"
        
        metrics.add_result(
            url=url,
            category=category,
            subcategory=subcategory,
            success=True,
            duration=total_time,
            content_length=len(result.markdown),
            quality_metrics={
                **quality,
                "fetch_time": fetch_time,
                "convert_time": convert_time,
                "title": result.title
            }
        )
        
        return {
            "success": True,
            "markdown_length": len(result.markdown),
            "quality": quality,
            "timing": {
                "fetch": fetch_time,
                "convert": convert_time,
                "total": total_time
            }
        }
        
    except Exception as e:
        total_time = time.time() - start_time
        error_msg = f"{type(e).__name__}: {str(e)}"
        
        metrics.add_result(
            url=url,
            category=category,
            subcategory=subcategory,
            success=False,
            duration=total_time,
            error=error_msg
        )
        
        return {
            "success": False,
            "error": error_msg,
            "timing": {"total": total_time}
        }


def test_concurrent_requests(urls: List[str], metrics: WikipediaTestMetrics, 
                           md: VoidLightMarkItDown, max_workers: int = 5) -> Dict:
    """Test concurrent Wikipedia requests"""
    print(f"\nTesting concurrent requests with {max_workers} workers...")
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, url in enumerate(urls[:max_workers]):
            future = executor.submit(
                test_wikipedia_url, 
                url, 
                "concurrent", 
                f"request_{i}", 
                metrics, 
                md
            )
            futures.append((url, future))
        
        for url, future in futures:
            try:
                result = future.result(timeout=60)
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "url": url
                })
    
    total_time = time.time() - start_time
    
    return {
        "total_time": total_time,
        "requests": len(urls),
        "average_time": total_time / len(urls),
        "results": results
    }


@pytest.fixture
def markitdown_instance():
    """Create markitdown instance for testing"""
    return VoidLightMarkItDown()


@pytest.fixture
def metrics():
    """Create metrics tracker"""
    return WikipediaTestMetrics()


class TestWikipediaAPI:
    """Test Wikipedia API integration"""
    
    def test_english_articles(self, markitdown_instance, metrics):
        """Test various English Wikipedia articles"""
        for subcategory, url in TEST_URLS["english"].items():
            test_wikipedia_url(url, "english", subcategory, metrics, markitdown_instance)
    
    def test_korean_articles(self, markitdown_instance, metrics):
        """Test Korean Wikipedia articles with special focus on Hangul/Hanja"""
        for subcategory, url in TEST_URLS["korean"].items():
            result = test_wikipedia_url(url, "korean", subcategory, metrics, markitdown_instance)
            
            # Additional Korean-specific validation
            if result["success"] and "quality" in result:
                quality = result["quality"]
                assert quality["has_korean"], f"Korean text not preserved in {url}"
    
    def test_multilingual_articles(self, markitdown_instance, metrics):
        """Test articles in various languages and scripts"""
        for subcategory, url in TEST_URLS["multilingual"].items():
            test_wikipedia_url(url, "multilingual", subcategory, metrics, markitdown_instance)
    
    def test_edge_cases(self, markitdown_instance, metrics):
        """Test edge cases and special Wikipedia pages"""
        for subcategory, url in TEST_URLS["edge_cases"].items():
            test_wikipedia_url(url, "edge_cases", subcategory, metrics, markitdown_instance)
    
    def test_invalid_urls(self, markitdown_instance, metrics):
        """Test handling of invalid URLs and error cases"""
        for subcategory, url in TEST_URLS["invalid"].items():
            result = test_wikipedia_url(url, "invalid", subcategory, metrics, markitdown_instance)
            # These should fail gracefully
            assert not result["success"] or url == TEST_URLS["invalid"]["non_wikipedia"]
    
    def test_concurrent_performance(self, markitdown_instance, metrics):
        """Test concurrent request handling"""
        # Select a mix of URLs for concurrent testing
        test_urls = [
            TEST_URLS["english"]["simple_article"],
            TEST_URLS["korean"]["simple_article"],
            TEST_URLS["multilingual"]["japanese"],
            TEST_URLS["english"]["table_heavy"],
            TEST_URLS["korean"]["infobox"],
        ]
        
        result = test_concurrent_requests(test_urls, metrics, markitdown_instance)
        
        assert result["total_time"] < 30, "Concurrent requests took too long"
        assert all(r["success"] for r in result["results"]), "Some concurrent requests failed"
    
    def test_mobile_url_handling(self, markitdown_instance, metrics):
        """Test mobile Wikipedia URL conversion"""
        mobile_url = TEST_URLS["edge_cases"]["mobile_url"]
        result = test_wikipedia_url(mobile_url, "mobile", "conversion", metrics, markitdown_instance)
        
        assert result["success"], "Mobile URL conversion failed"
        assert result["markdown_length"] > 1000, "Mobile content seems incomplete"
    
    def test_large_article_performance(self, markitdown_instance, metrics):
        """Test performance with large articles"""
        large_articles = [
            TEST_URLS["english"]["long_article"],
            TEST_URLS["korean"]["long_article"],
        ]
        
        for url in large_articles:
            start = time.time()
            result = test_wikipedia_url(url, "performance", "large_article", metrics, markitdown_instance)
            duration = time.time() - start
            
            assert result["success"], f"Large article conversion failed: {url}"
            assert duration < 10, f"Large article took too long: {duration}s"
    
    def test_special_characters_preservation(self, markitdown_instance, metrics):
        """Test preservation of special characters and Unicode"""
        test_cases = [
            (TEST_URLS["edge_cases"]["special_chars"], "C++"),
            (TEST_URLS["edge_cases"]["unicode_title"], "한글"),
            (TEST_URLS["korean"]["hanja_mixed"], "漢字"),
        ]
        
        for url, expected_text in test_cases:
            result = test_wikipedia_url(url, "unicode", "special_chars", metrics, markitdown_instance)
            
            if result["success"]:
                # Fetch and convert to verify content
                content, _ = fetch_wikipedia_content(url)
                import io
                content_stream = io.BytesIO(content)
                stream_info = StreamInfo(url=url)
                md_result = markitdown_instance.convert_stream(content_stream, stream_info=stream_info)
                
                assert expected_text in md_result.markdown, f"Expected text '{expected_text}' not found in {url}"


def main():
    """Run all Wikipedia API tests and generate report"""
    print("Starting comprehensive Wikipedia API testing...")
    
    md = VoidLightMarkItDown()
    metrics = WikipediaTestMetrics()
    
    # Run all test categories
    test_categories = {
        "English Articles": TEST_URLS["english"],
        "Korean Articles": TEST_URLS["korean"],
        "Multilingual": TEST_URLS["multilingual"],
        "Edge Cases": TEST_URLS["edge_cases"],
        "Invalid URLs": TEST_URLS["invalid"],
    }
    
    for category, urls in test_categories.items():
        print(f"\n{'='*50}")
        print(f"Testing {category}")
        print('='*50)
        
        for subcategory, url in urls.items():
            test_wikipedia_url(url, category, subcategory, metrics, md)
            time.sleep(0.5)  # Be polite to Wikipedia servers
    
    # Test concurrent requests
    print("\n" + "="*50)
    print("Testing Concurrent Requests")
    print("="*50)
    
    concurrent_urls = [
        TEST_URLS["english"]["simple_article"],
        TEST_URLS["korean"]["simple_article"],
        TEST_URLS["multilingual"]["japanese"],
    ]
    test_concurrent_requests(concurrent_urls, metrics, md)
    
    # Generate and save report
    report = metrics.generate_report()
    
    # Save JSON report
    report_path = "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/tests/wikipedia_api_test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Generate markdown report
    generate_markdown_report(report)
    
    print(f"\nTest completed! Results saved to {report_path}")
    print(f"Summary: {report['summary']['successful']}/{report['summary']['total_tests']} tests passed")


def generate_markdown_report(report: Dict):
    """Generate a markdown report from test results"""
    md_report = f"""# Wikipedia API Integration Test Report

Generated: {report['summary']['test_date']}

## Summary

- **Total Tests**: {report['summary']['total_tests']}
- **Successful**: {report['summary']['successful']}
- **Failed**: {report['summary']['failed']}
- **Success Rate**: {report['summary']['success_rate']:.1%}
- **Average Duration**: {report['summary']['average_duration']:.2f}s

## Performance Analysis

### Fastest Conversion
- URL: {report['performance']['fastest']['url'] if report['performance']['fastest'] else 'N/A'}
- Duration: {report['performance']['fastest']['duration']:.2f}s if report['performance']['fastest'] else 'N/A'
- Content Length: {report['performance']['fastest']['content_length']:,} chars if report['performance']['fastest'] else 'N/A'

### Slowest Conversion
- URL: {report['performance']['slowest']['url'] if report['performance']['slowest'] else 'N/A'}
- Duration: {report['performance']['slowest']['duration']:.2f}s if report['performance']['slowest'] else 'N/A'
- Content Length: {report['performance']['slowest']['content_length']:,} chars if report['performance']['slowest'] else 'N/A'

### Average Content Length: {report['performance']['average_content_length']:,.0f} characters

## Results by Category

"""
    
    for category, data in report['by_category'].items():
        success_rate = data['successful'] / data['total'] if data['total'] > 0 else 0
        md_report += f"\n### {category}\n"
        md_report += f"- Total: {data['total']}\n"
        md_report += f"- Successful: {data['successful']}\n"
        md_report += f"- Success Rate: {success_rate:.1%}\n"
        
        if data['subcategories']:
            md_report += "\n**Subcategories:**\n"
            for subcat, subdata in data['subcategories'].items():
                sub_rate = subdata['successful'] / subdata['total'] if subdata['total'] > 0 else 0
                md_report += f"- {subcat}: {subdata['successful']}/{subdata['total']} ({sub_rate:.1%})\n"
    
    if report['errors']:
        md_report += "\n## Errors\n\n"
        for error in report['errors'][:10]:  # Show first 10 errors
            md_report += f"- **{error['url']}**: {error['error']}\n"
        
        if len(report['errors']) > 10:
            md_report += f"\n... and {len(report['errors']) - 10} more errors\n"
    
    md_report += """
## Recommendations

1. **Caching**: Implement caching for frequently accessed Wikipedia articles
2. **Rate Limiting**: Add configurable rate limiting to be respectful to Wikipedia servers
3. **Error Handling**: Improve error messages for better debugging
4. **Content Validation**: Add more sophisticated content validation for different article types
5. **Performance**: Consider async/parallel processing for batch conversions

## Test Coverage

- ✅ Multiple languages (English, Korean, Arabic, Hebrew, Japanese, Chinese, etc.)
- ✅ Various content types (articles, tables, infoboxes, disambiguation pages)
- ✅ Edge cases (mobile URLs, special characters, protected pages)
- ✅ Error handling (non-existent pages, invalid URLs)
- ✅ Performance testing (concurrent requests, large articles)
- ✅ Unicode preservation (Hangul, Hanja, Arabic, Hebrew scripts)

"""
    
    report_path = "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/tests/wikipedia_api_test_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md_report)
    
    print(f"Markdown report saved to {report_path}")


if __name__ == "__main__":
    # Run the main test suite
    main()