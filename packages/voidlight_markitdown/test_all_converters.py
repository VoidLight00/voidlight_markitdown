#!/usr/bin/env python3
"""
Comprehensive test suite for all VoidLight MarkItDown converters.
Tests each converter with appropriate test files and Korean text processing.
"""

import os
import sys
import json
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add the package to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voidlight_markitdown import VoidLightMarkItDown, DocumentConverterResult


@dataclass
class TestResult:
    """Result of a single test."""
    converter_name: str
    test_file: str
    status: str  # "success", "failed", "skipped"
    error: Optional[str] = None
    markdown_preview: Optional[str] = None
    korean_content_found: bool = False


class ConverterTester:
    """Tests all converters with appropriate test files."""
    
    def __init__(self, test_files_dir: Path):
        self.test_files_dir = test_files_dir
        self.results: List[TestResult] = []
        
        # Map converters to appropriate test files
        self.converter_test_map = {
            "PlainTextConverter": ["test.json"],
            "HtmlConverter": ["test_blog.html", "test_wikipedia.html", "test_serp.html"],
            "RssConverter": ["test_rss.xml"],
            "WikipediaConverter": ["test_wikipedia.html"],
            "YouTubeConverter": [],  # No local test file for YouTube
            "BingSerpConverter": ["test_serp.html"],
            "DocxConverter": ["test.docx", "equations.docx", "test_with_comment.docx"],
            "XlsxConverter": ["test.xlsx"],
            "XlsConverter": ["test.xls"],
            "PptxConverter": ["test.pptx"],
            "AudioConverter": ["test.mp3", "test.m4a", "test.wav"],
            "ImageConverter": ["test.jpg", "test_llm.jpg"],
            "IpynbConverter": ["test_notebook.ipynb"],
            "PdfConverter": ["test.pdf"],
            "OutlookMsgConverter": ["test_outlook_msg.msg"],
            "EpubConverter": ["test.epub"],
            "ZipConverter": ["test_files.zip"],
            "CsvConverter": ["test_mskanji.csv"],
        }
        
        # Korean test content
        self.korean_test_content = {
            "한글": "Korean alphabet",
            "안녕하세요": "Hello",
            "감사합니다": "Thank you",
            "테스트": "Test"
        }
    
    def test_converter(self, converter_name: str, test_file: str, korean_mode: bool = False) -> TestResult:
        """Test a single converter with a specific file."""
        file_path = self.test_files_dir / test_file
        
        if not file_path.exists():
            return TestResult(
                converter_name=converter_name,
                test_file=test_file,
                status="skipped",
                error=f"Test file not found: {file_path}"
            )
        
        try:
            # Create MarkItDown instance
            md = VoidLightMarkItDown(
                enable_builtins=True,
                korean_mode=korean_mode,
                normalize_korean=True
            )
            
            # Convert the file
            result = md.convert(str(file_path))
            
            # Check for Korean content
            korean_found = any(
                korean in result.markdown 
                for korean in self.korean_test_content.keys()
            )
            
            # Get preview (first 500 chars)
            preview = result.markdown[:500] + "..." if len(result.markdown) > 500 else result.markdown
            
            return TestResult(
                converter_name=converter_name,
                test_file=test_file,
                status="success",
                markdown_preview=preview,
                korean_content_found=korean_found
            )
            
        except Exception as e:
            return TestResult(
                converter_name=converter_name,
                test_file=test_file,
                status="failed",
                error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            )
    
    def run_all_tests(self) -> None:
        """Run tests for all converters."""
        print("=" * 80)
        print("VoidLight MarkItDown Converter Test Suite")
        print("=" * 80)
        print()
        
        for converter_name, test_files in self.converter_test_map.items():
            print(f"\nTesting {converter_name}:")
            print("-" * 40)
            
            if not test_files:
                result = TestResult(
                    converter_name=converter_name,
                    test_file="N/A",
                    status="skipped",
                    error="No test files available for this converter"
                )
                self.results.append(result)
                print(f"  ⚠️  SKIPPED: {result.error}")
                continue
            
            for test_file in test_files:
                # Test without Korean mode
                print(f"  Testing with {test_file}...")
                result = self.test_converter(converter_name, test_file, korean_mode=False)
                self.results.append(result)
                
                if result.status == "success":
                    print(f"    ✅ SUCCESS")
                    if result.markdown_preview:
                        print(f"    Preview: {result.markdown_preview[:100]}...")
                elif result.status == "failed":
                    print(f"    ❌ FAILED: {result.error.split(chr(10))[0]}")
                else:
                    print(f"    ⚠️  SKIPPED: {result.error}")
                
                # Test with Korean mode for text-based files
                if test_file.endswith(('.html', '.docx', '.pdf', '.txt', '.csv')):
                    print(f"  Testing with {test_file} (Korean mode)...")
                    result_korean = self.test_converter(converter_name, test_file, korean_mode=True)
                    self.results.append(result_korean)
                    
                    if result_korean.status == "success":
                        print(f"    ✅ SUCCESS (Korean mode)")
                        if result_korean.korean_content_found:
                            print(f"    🇰🇷 Korean content detected!")
    
    def generate_report(self) -> str:
        """Generate a summary report of all test results."""
        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r.status == "success")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        
        report = f"""
# VoidLight MarkItDown Test Report

## Summary
- Total tests: {total_tests}
- ✅ Successful: {successful}
- ❌ Failed: {failed}
- ⚠️  Skipped: {skipped}
- Success rate: {(successful/total_tests*100):.1f}%

## Converter Status

"""
        
        # Group results by converter
        converter_results: Dict[str, List[TestResult]] = {}
        for result in self.results:
            if result.converter_name not in converter_results:
                converter_results[result.converter_name] = []
            converter_results[result.converter_name].append(result)
        
        for converter_name, results in converter_results.items():
            report += f"### {converter_name}\n"
            
            all_success = all(r.status == "success" for r in results)
            any_failed = any(r.status == "failed" for r in results)
            
            if all_success:
                report += "Status: ✅ **WORKING**\n\n"
            elif any_failed:
                report += "Status: ❌ **FAILING**\n\n"
            else:
                report += "Status: ⚠️  **SKIPPED**\n\n"
            
            for result in results:
                korean_tag = " (Korean mode)" if "Korean mode" in str(result) else ""
                if result.status == "success":
                    report += f"- ✅ {result.test_file}{korean_tag}\n"
                elif result.status == "failed":
                    report += f"- ❌ {result.test_file}{korean_tag}: {result.error.split(chr(10))[0]}\n"
                else:
                    report += f"- ⚠️  {result.test_file}{korean_tag}: {result.error}\n"
            
            report += "\n"
        
        # Add detailed failure information
        failures = [r for r in self.results if r.status == "failed"]
        if failures:
            report += "## Detailed Failure Information\n\n"
            for result in failures:
                report += f"### {result.converter_name} - {result.test_file}\n"
                report += "```\n"
                report += result.error
                report += "```\n\n"
        
        return report
    
    def save_results(self, output_file: str = "test_results.json") -> None:
        """Save test results to a JSON file."""
        results_data = []
        for result in self.results:
            results_data.append({
                "converter_name": result.converter_name,
                "test_file": result.test_file,
                "status": result.status,
                "error": result.error,
                "markdown_preview": result.markdown_preview,
                "korean_content_found": result.korean_content_found
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nTest results saved to: {output_file}")


def test_individual_converters():
    """Test individual converter functionality."""
    print("\n" + "=" * 80)
    print("Testing Individual Converter Features")
    print("=" * 80)
    
    # Test Korean text processing
    print("\n1. Testing Korean Text Processing:")
    print("-" * 40)
    
    md_korean = VoidLightMarkItDown(korean_mode=True, normalize_korean=True)
    
    # Create a test HTML file with Korean content
    korean_html = """
    <html>
    <body>
        <h1>한글 테스트 문서</h1>
        <p>안녕하세요! 이것은 한국어 처리 테스트입니다.</p>
        <p>감사합니다.</p>
    </body>
    </html>
    """
    
    test_korean_file = Path("test_korean.html")
    test_korean_file.write_text(korean_html, encoding='utf-8')
    
    try:
        result = md_korean.convert(str(test_korean_file))
        print("✅ Korean text processing successful!")
        print(f"Output:\n{result.markdown}")
    except Exception as e:
        print(f"❌ Korean text processing failed: {e}")
    finally:
        test_korean_file.unlink(missing_ok=True)
    
    # Test URL conversion
    print("\n2. Testing URL Conversion (with mock):")
    print("-" * 40)
    
    md = VoidLightMarkItDown()
    try:
        # We'll test with a data URI instead of a real URL
        data_uri = "data:text/html,<h1>Hello World</h1><p>This is a test.</p>"
        result = md.convert(data_uri)
        print("✅ URL conversion successful!")
        print(f"Output:\n{result.markdown}")
    except Exception as e:
        print(f"❌ URL conversion failed: {e}")


def main():
    """Main test execution function."""
    # Get test files directory
    test_files_dir = Path(__file__).parent / "tests" / "test_files"
    
    if not test_files_dir.exists():
        print(f"Error: Test files directory not found: {test_files_dir}")
        sys.exit(1)
    
    # Create tester instance
    tester = ConverterTester(test_files_dir)
    
    # Run all converter tests
    tester.run_all_tests()
    
    # Test individual features
    test_individual_converters()
    
    # Generate and save report
    report = tester.generate_report()
    report_file = Path("converter_test_report.md")
    report_file.write_text(report, encoding='utf-8')
    print(f"\n📄 Test report saved to: {report_file}")
    
    # Save JSON results
    tester.save_results("converter_test_results.json")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(tester.results)
    successful = sum(1 for r in tester.results if r.status == "success")
    failed = sum(1 for r in tester.results if r.status == "failed")
    
    print(f"Total tests run: {total}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {(successful/total*100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()