#!/usr/bin/env python3
"""Profile application performance."""

import sys
from pathlib import Path
import time
import tempfile
import cProfile
import pstats
from io import StringIO

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from voidlight_markitdown import VoidLightMarkItDown

def profile_conversions():
    """Profile various document conversions."""
    converter = VoidLightMarkItDown(korean_mode=True)
    
    # Create test files
    test_files = []
    
    # Text file
    text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    text_file.write("This is a test document.\n한국어 텍스트 테스트입니다.")
    text_file.close()
    test_files.append(text_file.name)
    
    # HTML file
    html_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    html_file.write("""
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>Test Document</h1>
        <p>This is a test paragraph.</p>
        <p>한국어 단락입니다.</p>
    </body>
    </html>
    """)
    html_file.close()
    test_files.append(html_file.name)
    
    # Profile conversions
    print("Profiling document conversions...")
    
    for test_file in test_files:
        print(f"\nProfiling: {Path(test_file).suffix}")
        start_time = time.time()
        
        # Run conversion
        result = converter.convert(test_file)
        
        end_time = time.time()
        print(f"Conversion time: {end_time - start_time:.3f}s")
        print(f"Result length: {len(result.text_content)} characters")
    
    # Cleanup
    for test_file in test_files:
        Path(test_file).unlink()

def profile_korean_processing():
    """Profile Korean text processing."""
    from voidlight_markitdown.korean import KoreanTextProcessor
    
    processor = KoreanTextProcessor()
    
    test_texts = [
        "안녕하세요. 반갑습니다.",
        "한국어 텍스트 처리 성능을 테스트합니다.",
        "다양한 한글 문장을 처리하여 성능을 측정합니다." * 10,
        "English and 한국어 mixed text processing test." * 5,
    ]
    
    print("\nProfiling Korean text processing...")
    
    for i, text in enumerate(test_texts):
        print(f"\nTest {i+1} (length: {len(text)} chars)")
        
        # Profile normalization
        start = time.time()
        normalized = processor.normalize_text(text)
        print(f"Normalization: {(time.time() - start) * 1000:.2f}ms")
        
        # Profile tokenization
        if processor.mecab_available:
            start = time.time()
            tokens = processor.tokenize(text)
            print(f"Tokenization: {(time.time() - start) * 1000:.2f}ms")
            print(f"Token count: {len(tokens)}")

def profile_batch_conversions():
    """Profile batch document conversions."""
    converter = VoidLightMarkItDown(korean_mode=True)
    
    # Create multiple test files
    num_files = 50
    test_files = []
    
    for i in range(num_files):
        text_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.txt', 
            delete=False
        )
        text_file.write(f"Test document {i}\n한국어 문서 {i}")
        text_file.close()
        test_files.append(text_file.name)
    
    print(f"\nProfiling batch conversion of {num_files} files...")
    
    start_time = time.time()
    results = []
    
    for test_file in test_files:
        result = converter.convert(test_file)
        results.append(result)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"Total time: {total_time:.3f}s")
    print(f"Average time per file: {total_time / num_files:.3f}s")
    print(f"Files per second: {num_files / total_time:.2f}")
    
    # Cleanup
    for test_file in test_files:
        Path(test_file).unlink()

def generate_profile_report(stats: pstats.Stats) -> str:
    """Generate profile report."""
    s = StringIO()
    ps = pstats.Stats(stats, stream=s)
    
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    
    # Print header
    s.write("\n" + "="*80 + "\n")
    s.write("Performance Profile Report\n")
    s.write("="*80 + "\n\n")
    
    # Top 20 functions by cumulative time
    s.write("Top 20 functions by cumulative time:\n")
    s.write("-"*80 + "\n")
    ps.print_stats(20)
    
    # Top 10 functions by total time
    s.write("\n\nTop 10 functions by total time:\n")
    s.write("-"*80 + "\n")
    ps.sort_stats('time')
    ps.print_stats(10)
    
    # Callers
    s.write("\n\nTop callers:\n")
    s.write("-"*80 + "\n")
    ps.print_callers(10)
    
    return s.getvalue()

def main():
    """Main profiling entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Profile voidlight_markitdown performance")
    parser.add_argument(
        "--mode",
        choices=["conversions", "korean", "batch", "all"],
        default="all",
        help="Profiling mode"
    )
    parser.add_argument(
        "--output",
        help="Output file for profile stats"
    )
    
    args = parser.parse_args()
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Run profiling
    profiler.enable()
    
    if args.mode in ["conversions", "all"]:
        profile_conversions()
    
    if args.mode in ["korean", "all"]:
        profile_korean_processing()
    
    if args.mode in ["batch", "all"]:
        profile_batch_conversions()
    
    profiler.disable()
    
    # Generate report
    stats = pstats.Stats(profiler)
    report = generate_profile_report(stats)
    
    # Output results
    if args.output:
        # Save detailed stats
        stats.dump_stats(args.output)
        
        # Save readable report
        report_path = Path(args.output).with_suffix('.txt')
        report_path.write_text(report)
        
        print(f"\nProfile stats saved to: {args.output}")
        print(f"Readable report saved to: {report_path}")
    else:
        print(report)

if __name__ == "__main__":
    main()