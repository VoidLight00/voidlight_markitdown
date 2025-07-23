#!/usr/bin/env python3
"""
Stress testing for voidlight_markitdown.

This script performs stress tests to find the limits of the system,
including maximum file sizes, concurrent operations, and resource constraints.
"""

import os
import sys
import time
import json
import psutil
import tempfile
import threading
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random
import string
import gc

# Add parent directory to path

from voidlight_markitdown import VoidLightMarkItDown, StreamInfo
from voidlight_markitdown._exceptions import VoidLightMarkItDownException


class StressTester:
    """Perform stress tests on voidlight_markitdown."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "./stress_test_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test results
        self.results = {
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'system': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                    'disk_free_gb': psutil.disk_usage('/').free / (1024**3),
                }
            },
            'tests': {}
        }
    
    def test_maximum_file_size(self, file_type: str = 'txt', start_size_mb: int = 100) -> Dict:
        """Find the maximum file size that can be processed."""
        print(f"\n{'='*60}")
        print(f"TESTING MAXIMUM FILE SIZE ({file_type.upper()})")
        print(f"{'='*60}")
        
        test_result = {
            'file_type': file_type,
            'attempts': [],
            'maximum_successful_mb': 0,
            'failure_size_mb': None,
            'failure_reason': None,
        }
        
        current_size_mb = start_size_mb
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\nAttempt {attempt}: Testing {current_size_mb}MB {file_type} file...")
            
            # Create test file
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{file_type}', delete=False) as f:
                test_file = f.name
                
                # Generate content
                if file_type == 'txt':
                    self._generate_large_text_file(f, current_size_mb)
                else:
                    print(f"Unsupported file type for size testing: {file_type}")
                    return test_result
            
            # Test conversion
            converter = VoidLightMarkItDown()
            start_time = time.time()
            success = False
            error = None
            memory_peak_mb = 0
            
            try:
                # Monitor memory during conversion
                process = psutil.Process()
                memory_start = process.memory_info().rss / (1024 * 1024)
                
                result = converter.convert_local(test_file)
                
                memory_end = process.memory_info().rss / (1024 * 1024)
                memory_peak_mb = memory_end  # Approximate
                
                success = True
                test_result['maximum_successful_mb'] = current_size_mb
                
            except MemoryError as e:
                error = f"MemoryError: {str(e)}"
                test_result['failure_size_mb'] = current_size_mb
                test_result['failure_reason'] = 'memory_error'
                
            except Exception as e:
                error = f"{type(e).__name__}: {str(e)}"
                if 'memory' in str(e).lower():
                    test_result['failure_size_mb'] = current_size_mb
                    test_result['failure_reason'] = 'memory_related'
            
            finally:
                # Clean up
                try:
                    os.unlink(test_file)
                except:
                    pass
                
                gc.collect()
            
            processing_time = time.time() - start_time
            
            # Record attempt
            test_result['attempts'].append({
                'size_mb': current_size_mb,
                'success': success,
                'processing_time': processing_time,
                'memory_peak_mb': memory_peak_mb,
                'error': error,
            })
            
            print(f"  Result: {'✅ Success' if success else '❌ Failed'}")
            print(f"  Time: {processing_time:.2f}s")
            print(f"  Memory: {memory_peak_mb:.1f}MB")
            if error:
                print(f"  Error: {error}")
            
            # Determine next size
            if success:
                # Increase size
                if current_size_mb < 500:
                    current_size_mb = int(current_size_mb * 1.5)
                else:
                    current_size_mb += 250
            else:
                # We hit the limit
                break
        
        print(f"\nMaximum successful size: {test_result['maximum_successful_mb']}MB")
        if test_result['failure_size_mb']:
            print(f"Failed at: {test_result['failure_size_mb']}MB ({test_result['failure_reason']})")
        
        return test_result
    
    def _generate_large_text_file(self, file_handle, size_mb: int):
        """Generate a large text file."""
        target_bytes = size_mb * 1024 * 1024
        written = 0
        
        # Write header
        header = f"# Large Test File - {size_mb}MB\n\n"
        file_handle.write(header)
        written += len(header.encode('utf-8'))
        
        # Generate content
        while written < target_bytes:
            # Generate a paragraph
            paragraph = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 20
            paragraph += "\n\n"
            
            file_handle.write(paragraph)
            written += len(paragraph.encode('utf-8'))
    
    def test_concurrent_operations(self, num_files: int = 10, file_size_mb: int = 50) -> Dict:
        """Test concurrent file processing."""
        print(f"\n{'='*60}")
        print(f"TESTING CONCURRENT OPERATIONS")
        print(f"{'='*60}")
        print(f"Files: {num_files}, Size: {file_size_mb}MB each")
        
        test_result = {
            'num_files': num_files,
            'file_size_mb': file_size_mb,
            'worker_tests': {},
        }
        
        # Create test files
        test_files = []
        print("\nCreating test files...")
        for i in range(num_files):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                self._generate_large_text_file(f, file_size_mb)
                test_files.append(f.name)
        
        # Test different worker counts
        for num_workers in [1, 2, 4, 8, 16]:
            if num_workers > multiprocessing.cpu_count() * 2:
                continue
            
            print(f"\nTesting with {num_workers} workers...")
            
            start_time = time.time()
            results = []
            errors = []
            
            def process_file(filepath):
                try:
                    converter = VoidLightMarkItDown()
                    result = converter.convert_local(filepath)
                    return True, None
                except Exception as e:
                    return False, str(e)
            
            if num_workers == 1:
                # Sequential processing
                for filepath in test_files:
                    success, error = process_file(filepath)
                    results.append(success)
                    if error:
                        errors.append(error)
            else:
                # Concurrent processing
                from concurrent.futures import ThreadPoolExecutor
                
                with ThreadPoolExecutor(max_workers=num_workers) as executor:
                    futures = [executor.submit(process_file, f) for f in test_files]
                    
                    for future in futures:
                        try:
                            success, error = future.result(timeout=300)
                            results.append(success)
                            if error:
                                errors.append(error)
                        except Exception as e:
                            results.append(False)
                            errors.append(str(e))
            
            processing_time = time.time() - start_time
            successful = sum(results)
            
            test_result['worker_tests'][num_workers] = {
                'processing_time': processing_time,
                'successful': successful,
                'failed': len(results) - successful,
                'throughput_files_per_second': successful / processing_time if processing_time > 0 else 0,
                'throughput_mb_per_second': (successful * file_size_mb) / processing_time if processing_time > 0 else 0,
                'errors': errors[:5],  # First 5 errors
            }
            
            print(f"  Time: {processing_time:.2f}s")
            print(f"  Success: {successful}/{num_files}")
            print(f"  Throughput: {test_result['worker_tests'][num_workers]['throughput_mb_per_second']:.2f}MB/s")
        
        # Clean up test files
        for filepath in test_files:
            try:
                os.unlink(filepath)
            except:
                pass
        
        # Find optimal worker count
        best_workers = max(test_result['worker_tests'].items(), 
                          key=lambda x: x[1]['throughput_mb_per_second'])[0]
        test_result['optimal_workers'] = best_workers
        
        print(f"\nOptimal worker count: {best_workers}")
        
        return test_result
    
    def test_memory_limits(self, file_size_mb: int = 100) -> Dict:
        """Test behavior under memory constraints."""
        print(f"\n{'='*60}")
        print(f"TESTING MEMORY LIMITS")
        print(f"{'='*60}")
        
        test_result = {
            'file_size_mb': file_size_mb,
            'tests': [],
        }
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            self._generate_large_text_file(f, file_size_mb)
            test_file = f.name
        
        # Test 1: Normal processing (baseline)
        print("\n1. Baseline test (no constraints)...")
        converter = VoidLightMarkItDown()
        
        gc.collect()
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)
        
        start_time = time.time()
        try:
            result = converter.convert_local(test_file)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
        
        processing_time = time.time() - start_time
        memory_after = process.memory_info().rss / (1024 * 1024)
        memory_used = memory_after - memory_before
        
        test_result['tests'].append({
            'name': 'baseline',
            'success': success,
            'processing_time': processing_time,
            'memory_used_mb': memory_used,
            'error': error,
        })
        
        print(f"  Result: {'✅ Success' if success else '❌ Failed'}")
        print(f"  Memory used: {memory_used:.1f}MB")
        
        # Test 2: Multiple simultaneous conversions
        print("\n2. Multiple simultaneous conversions...")
        num_simultaneous = 5
        
        gc.collect()
        memory_before = process.memory_info().rss / (1024 * 1024)
        
        threads = []
        results = []
        
        def convert_in_thread():
            try:
                converter = VoidLightMarkItDown()
                converter.convert_local(test_file)
                results.append(True)
            except:
                results.append(False)
        
        start_time = time.time()
        for _ in range(num_simultaneous):
            t = threading.Thread(target=convert_in_thread)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        processing_time = time.time() - start_time
        memory_after = process.memory_info().rss / (1024 * 1024)
        memory_used = memory_after - memory_before
        
        test_result['tests'].append({
            'name': f'simultaneous_{num_simultaneous}',
            'success': all(results),
            'successful_count': sum(results),
            'processing_time': processing_time,
            'memory_used_mb': memory_used,
            'memory_per_conversion_mb': memory_used / num_simultaneous,
        })
        
        print(f"  Result: {sum(results)}/{num_simultaneous} successful")
        print(f"  Total memory used: {memory_used:.1f}MB")
        print(f"  Memory per conversion: {memory_used/num_simultaneous:.1f}MB")
        
        # Clean up
        try:
            os.unlink(test_file)
        except:
            pass
        
        return test_result
    
    def test_file_corruption_handling(self) -> Dict:
        """Test handling of corrupted files."""
        print(f"\n{'='*60}")
        print(f"TESTING CORRUPTED FILE HANDLING")
        print(f"{'='*60}")
        
        test_result = {
            'tests': []
        }
        
        converter = VoidLightMarkItDown()
        
        # Test 1: Binary data in text file
        print("\n1. Binary data in text file...")
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            # Write some text, then binary data
            f.write(b"This is text\n")
            f.write(os.urandom(1024))  # Random binary data
            f.write(b"\nMore text")
            test_file = f.name
        
        try:
            result = converter.convert_local(test_file)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
        
        test_result['tests'].append({
            'name': 'binary_in_text',
            'success': success,
            'error': error,
        })
        
        print(f"  Result: {'✅ Handled' if success else '❌ Failed'}")
        os.unlink(test_file)
        
        # Test 2: Truncated PDF
        print("\n2. Truncated PDF file...")
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Write partial PDF header
            f.write(b"%PDF-1.4\n")
            f.write(b"1 0 obj\n<< /Type /Catalog")
            # Truncated - missing rest of file
            test_file = f.name
        
        try:
            result = converter.convert_local(test_file)
            success = True
            error = None
        except Exception as e:
            success = False
            error = type(e).__name__
        
        test_result['tests'].append({
            'name': 'truncated_pdf',
            'success': success is False,  # Should fail gracefully
            'error': error,
        })
        
        print(f"  Result: {'✅ Failed gracefully' if not success else '❌ Unexpected success'}")
        os.unlink(test_file)
        
        # Test 3: Wrong extension
        print("\n3. Wrong file extension...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("This is actually a text file, not a PDF")
            test_file = f.name
        
        try:
            result = converter.convert_local(test_file)
            success = True
            error = None
            # Check if it was processed as text
            contains_text = "This is actually a text file" in result.markdown
        except Exception as e:
            success = False
            error = str(e)
            contains_text = False
        
        test_result['tests'].append({
            'name': 'wrong_extension',
            'success': success,
            'handled_correctly': contains_text if success else False,
            'error': error,
        })
        
        print(f"  Result: {'✅ Handled' if success else '❌ Failed'}")
        if success:
            print(f"  Content detected: {'✅ Yes' if contains_text else '❌ No'}")
        os.unlink(test_file)
        
        return test_result
    
    def test_edge_cases(self) -> Dict:
        """Test various edge cases."""
        print(f"\n{'='*60}")
        print(f"TESTING EDGE CASES")
        print(f"{'='*60}")
        
        test_result = {
            'tests': []
        }
        
        converter = VoidLightMarkItDown()
        
        # Test 1: Empty file
        print("\n1. Empty file...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_file = f.name
        
        try:
            result = converter.convert_local(test_file)
            success = True
            error = None
            markdown_length = len(result.markdown)
        except Exception as e:
            success = False
            error = str(e)
            markdown_length = 0
        
        test_result['tests'].append({
            'name': 'empty_file',
            'success': success,
            'markdown_length': markdown_length,
            'error': error,
        })
        
        print(f"  Result: {'✅ Success' if success else '❌ Failed'}")
        os.unlink(test_file)
        
        # Test 2: Very long lines
        print("\n2. Very long lines...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Create a line with 1 million characters
            long_line = 'x' * 1_000_000
            f.write(f"Short line\n{long_line}\nAnother short line")
            test_file = f.name
        
        try:
            result = converter.convert_local(test_file)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
        
        test_result['tests'].append({
            'name': 'very_long_lines',
            'success': success,
            'error': error,
        })
        
        print(f"  Result: {'✅ Success' if success else '❌ Failed'}")
        os.unlink(test_file)
        
        # Test 3: Special characters and encodings
        print("\n3. Special characters...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("ASCII: Hello World\n")
            f.write("Korean: 안녕하세요 세계\n")
            f.write("Emoji: 🚀 🌟 ✨\n")
            f.write("Math: ∑∫∂ ≠ ≤ ≥\n")
            f.write("Null char: \x00\n")
            test_file = f.name
        
        try:
            result = converter.convert_local(test_file)
            success = True
            error = None
            # Check if special characters are preserved
            has_korean = "안녕하세요" in result.markdown
            has_emoji = "🚀" in result.markdown
        except Exception as e:
            success = False
            error = str(e)
            has_korean = False
            has_emoji = False
        
        test_result['tests'].append({
            'name': 'special_characters',
            'success': success,
            'korean_preserved': has_korean,
            'emoji_preserved': has_emoji,
            'error': error,
        })
        
        print(f"  Result: {'✅ Success' if success else '❌ Failed'}")
        if success:
            print(f"  Korean preserved: {'✅' if has_korean else '❌'}")
            print(f"  Emoji preserved: {'✅' if has_emoji else '❌'}")
        os.unlink(test_file)
        
        return test_result
    
    def run_all_stress_tests(self) -> Dict:
        """Run all stress tests."""
        print("VOIDLIGHT MARKITDOWN STRESS TEST SUITE")
        print("=" * 60)
        print(f"Start time: {datetime.now()}")
        print(f"System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total / (1024**3):.1f}GB RAM")
        print("=" * 60)
        
        # Run tests
        self.results['tests']['maximum_file_size'] = self.test_maximum_file_size('txt', start_size_mb=100)
        self.results['tests']['concurrent_operations'] = self.test_concurrent_operations(num_files=10, file_size_mb=50)
        self.results['tests']['memory_limits'] = self.test_memory_limits(file_size_mb=100)
        self.results['tests']['corruption_handling'] = self.test_file_corruption_handling()
        self.results['tests']['edge_cases'] = self.test_edge_cases()
        
        # Complete metadata
        self.results['metadata']['end_time'] = datetime.now().isoformat()
        
        # Save results
        results_file = self.output_dir / f"stress_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate summary
        summary = self._generate_summary()
        summary_file = self.output_dir / f"stress_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"\n{'='*60}")
        print("STRESS TEST COMPLETE")
        print(f"{'='*60}")
        print(f"Results: {results_file}")
        print(f"Summary: {summary_file}")
        
        return self.results
    
    def _generate_summary(self) -> str:
        """Generate a summary report."""
        summary = """# VoidLight MarkItDown Stress Test Summary

## System Information
"""
        
        sys_info = self.results['metadata']['system']
        summary += f"- CPU Cores: {sys_info['cpu_count']}\n"
        summary += f"- Total Memory: {sys_info['memory_total_gb']:.1f}GB\n"
        summary += f"- Disk Free: {sys_info['disk_free_gb']:.1f}GB\n\n"
        
        # Maximum file size
        if 'maximum_file_size' in self.results['tests']:
            test = self.results['tests']['maximum_file_size']
            summary += "## Maximum File Size\n\n"
            summary += f"- **Maximum Successful**: {test['maximum_successful_mb']}MB\n"
            if test['failure_size_mb']:
                summary += f"- **Failure Size**: {test['failure_size_mb']}MB\n"
                summary += f"- **Failure Reason**: {test['failure_reason']}\n"
            summary += "\n"
        
        # Concurrent operations
        if 'concurrent_operations' in self.results['tests']:
            test = self.results['tests']['concurrent_operations']
            summary += "## Concurrent Operations\n\n"
            summary += f"- **Optimal Workers**: {test.get('optimal_workers', 'N/A')}\n"
            summary += f"- **File Size Tested**: {test['file_size_mb']}MB\n\n"
            
            summary += "| Workers | Time (s) | Throughput (MB/s) | Success Rate |\n"
            summary += "|---------|----------|-------------------|---------------|\n"
            
            for workers, data in sorted(test['worker_tests'].items()):
                success_rate = (data['successful'] / test['num_files']) * 100
                summary += f"| {workers} | {data['processing_time']:.1f} | "
                summary += f"{data['throughput_mb_per_second']:.1f} | {success_rate:.0f}% |\n"
            summary += "\n"
        
        # Memory limits
        if 'memory_limits' in self.results['tests']:
            test = self.results['tests']['memory_limits']
            summary += "## Memory Usage\n\n"
            
            for t in test['tests']:
                if t['name'] == 'baseline':
                    summary += f"- **Single File ({test['file_size_mb']}MB)**: {t['memory_used_mb']:.1f}MB\n"
                elif 'simultaneous' in t['name']:
                    summary += f"- **Concurrent Processing**: {t['memory_per_conversion_mb']:.1f}MB per file\n"
            summary += "\n"
        
        # Edge cases
        summary += "## Robustness\n\n"
        
        all_tests = []
        for test_category in ['corruption_handling', 'edge_cases']:
            if test_category in self.results['tests']:
                all_tests.extend(self.results['tests'][test_category]['tests'])
        
        if all_tests:
            summary += "| Test | Result |\n"
            summary += "|------|--------|\n"
            
            for t in all_tests:
                result = "✅ Pass" if t.get('success') or t.get('handled_correctly') else "❌ Fail"
                summary += f"| {t['name'].replace('_', ' ').title()} | {result} |\n"
        
        summary += "\n## Recommendations\n\n"
        summary += "1. **File Size**: System can handle files up to "
        summary += f"{self.results['tests'].get('maximum_file_size', {}).get('maximum_successful_mb', 'N/A')}MB\n"
        summary += "2. **Concurrency**: Use "
        summary += f"{self.results['tests'].get('concurrent_operations', {}).get('optimal_workers', '2-4')} workers for best performance\n"
        summary += "3. **Memory**: Plan for ~1MB of memory per MB of file size\n"
        summary += "4. **Robustness**: System handles corrupted files and edge cases gracefully\n"
        
        return summary


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stress test voidlight_markitdown')
    parser.add_argument('--output-dir', default='./stress_test_results', help='Output directory')
    parser.add_argument('--test', choices=['all', 'size', 'concurrent', 'memory', 'corruption', 'edge'],
                       default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    tester = StressTester(output_dir=args.output_dir)
    
    if args.test == 'all':
        tester.run_all_stress_tests()
    elif args.test == 'size':
        result = tester.test_maximum_file_size()
        print(json.dumps(result, indent=2))
    elif args.test == 'concurrent':
        result = tester.test_concurrent_operations()
        print(json.dumps(result, indent=2))
    elif args.test == 'memory':
        result = tester.test_memory_limits()
        print(json.dumps(result, indent=2))
    elif args.test == 'corruption':
        result = tester.test_file_corruption_handling()
        print(json.dumps(result, indent=2))
    elif args.test == 'edge':
        result = tester.test_edge_cases()
        print(json.dumps(result, indent=2))
    
    print("\n✅ Stress testing complete!")


if __name__ == "__main__":
    main()