"""
Manual Wikipedia Testing Script

Quick testing tool for Wikipedia URLs with detailed output.
"""

import sys
import time
from urllib.request import urlopen, Request
from urllib.parse import quote

from voidlight_markitdown import VoidLightMarkItDown, StreamInfo


def test_wikipedia_url(url: str, save_output: bool = False):
    """Test a single Wikipedia URL with detailed output"""
    
    print(f"\n{'='*60}")
    print(f"Testing Wikipedia URL: {url}")
    print('='*60)
    
    md = VoidLightMarkItDown()
    
    try:
        # Fetch content
        print("\n1. Fetching content...")
        start_time = time.time()
        
        headers = {
            'User-Agent': 'VoidlightMarkitdown/1.0 (Manual Testing)',
            'Accept': 'text/html,application/xhtml+xml',
        }
        # Properly encode URL if it contains non-ASCII characters
        if any(ord(c) > 127 for c in url):
            # Split URL and encode only the path part
            parts = url.split('/', 3)
            if len(parts) >= 4:
                encoded_path = quote(parts[3].encode('utf-8'))
                url_encoded = '/'.join(parts[:3]) + '/' + encoded_path
            else:
                url_encoded = url
        else:
            url_encoded = url
        
        req = Request(url_encoded, headers=headers)
        
        with urlopen(req, timeout=30) as response:
            content = response.read()
            content_size = len(content)
        
        fetch_time = time.time() - start_time
        print(f"   ✓ Fetched {content_size:,} bytes in {fetch_time:.2f}s")
        
        # Convert to markdown
        print("\n2. Converting to Markdown...")
        convert_start = time.time()
        # Convert bytes to stream
        import io
        content_stream = io.BytesIO(content)
        stream_info = StreamInfo(url=url)
        result = md.convert_stream(content_stream, stream_info=stream_info)
        convert_time = time.time() - convert_start
        
        print(f"   ✓ Converted in {convert_time:.2f}s")
        print(f"   ✓ Title: {result.title}")
        print(f"   ✓ Markdown size: {len(result.markdown):,} characters")
        
        # Analyze content
        print("\n3. Content Analysis:")
        lines = result.markdown.split('\n')
        headers = [line for line in lines if line.strip().startswith('#')]
        
        print(f"   - Total lines: {len(lines)}")
        print(f"   - Headers: {len(headers)}")
        print(f"   - Tables: {'Yes' if '|---|' in result.markdown else 'No'}")
        print(f"   - Links: {result.markdown.count('](')} found")
        print(f"   - Lists: {'Yes' if any(line.strip().startswith(('- ', '* ', '1.')) for line in lines) else 'No'}")
        
        # Language detection
        has_korean = any('\uac00' <= char <= '\ud7af' for char in result.markdown)
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in result.markdown)
        has_arabic = any('\u0600' <= char <= '\u06ff' for char in result.markdown)
        has_hebrew = any('\u0590' <= char <= '\u05ff' for char in result.markdown)
        
        print("\n4. Language Detection:")
        if has_korean:
            print("   ✓ Korean (Hangul) detected")
        if has_chinese:
            print("   ✓ Chinese/Hanja characters detected")
        if has_arabic:
            print("   ✓ Arabic script detected")
        if has_hebrew:
            print("   ✓ Hebrew script detected")
        
        # Show preview
        print("\n5. Content Preview (first 500 chars):")
        print("-" * 40)
        preview = result.markdown[:500]
        if len(result.markdown) > 500:
            preview += "..."
        print(preview)
        print("-" * 40)
        
        # Show section structure
        if headers:
            print("\n6. Section Structure:")
            for i, header in enumerate(headers[:10]):  # Show first 10 headers
                level = header.count('#')
                indent = '  ' * (level - 1)
                title = header.strip('#').strip()
                print(f"{indent}{'└─' if level > 1 else ''} {title}")
            if len(headers) > 10:
                print(f"   ... and {len(headers) - 10} more sections")
        
        # Performance summary
        print("\n7. Performance Summary:")
        total_time = fetch_time + convert_time
        print(f"   - Total time: {total_time:.2f}s")
        print(f"   - Fetch time: {fetch_time:.2f}s ({fetch_time/total_time*100:.1f}%)")
        print(f"   - Convert time: {convert_time:.2f}s ({convert_time/total_time*100:.1f}%)")
        print(f"   - Compression ratio: {len(result.markdown)/content_size:.2f}")
        print(f"   - Speed: {content_size/total_time/1024:.1f} KB/s")
        
        # Save output if requested
        if save_output:
            output_file = url.split('/')[-1] + '.md'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.markdown)
            print(f"\n✓ Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        return False


def interactive_mode():
    """Interactive testing mode"""
    
    print("\n🌐 Wikipedia URL Testing Tool")
    print("=" * 50)
    print("Enter Wikipedia URLs to test (or 'quit' to exit)")
    print("Add '-s' flag to save output (e.g., 'url -s')")
    print("\nExample URLs:")
    print("- https://en.wikipedia.org/wiki/Python_(programming_language)")
    print("- https://ko.wikipedia.org/wiki/파이썬")
    print("- https://ja.wikipedia.org/wiki/Python")
    
    while True:
        try:
            user_input = input("\nEnter URL: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Check for save flag
            save_output = False
            if ' -s' in user_input:
                user_input = user_input.replace(' -s', '').strip()
                save_output = True
            
            # Validate URL
            if not user_input.startswith('http'):
                print("❌ Please enter a valid URL starting with http:// or https://")
                continue
            
            if 'wikipedia.org' not in user_input:
                print("⚠️  Warning: This doesn't appear to be a Wikipedia URL")
                confirm = input("Continue anyway? (y/n): ")
                if confirm.lower() != 'y':
                    continue
            
            # Test the URL
            test_wikipedia_url(user_input, save_output)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def batch_test(urls: list):
    """Test multiple URLs in batch"""
    
    print(f"\n📦 Batch Testing {len(urls)} URLs")
    print("=" * 50)
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Testing: {url}")
        success = test_wikipedia_url(url)
        results.append((url, success))
        
        if i < len(urls):
            print("\nWaiting 2 seconds before next request...")
            time.sleep(2)
    
    # Summary
    print("\n" + "="*50)
    print("BATCH TEST SUMMARY")
    print("="*50)
    
    successful = sum(1 for _, success in results if success)
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    if any(not success for _, success in results):
        print("\nFailed URLs:")
        for url, success in results:
            if not success:
                print(f"  - {url}")


def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--batch':
            # Batch mode with predefined URLs
            test_urls = [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://ko.wikipedia.org/wiki/인공지능",
                "https://ja.wikipedia.org/wiki/人工知能",
                "https://zh.wikipedia.org/wiki/人工智能",
                "https://en.wikipedia.org/wiki/Python_(programming_language)",
            ]
            batch_test(test_urls)
        else:
            # Single URL from command line
            url = sys.argv[1]
            save_output = '-s' in sys.argv
            test_wikipedia_url(url, save_output)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()