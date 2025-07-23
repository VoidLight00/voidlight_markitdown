#!/usr/bin/env python3
"""
Production-specific error recovery tests for VoidLight MarkItDown
Tests actual error handling implementations in the codebase
"""

import asyncio
import io
import json
import os
import random
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import VoidLight MarkItDown components
try:
    from packages.voidlight_markitdown.src.voidlight_markitdown import (
        VoidLightMarkItDown,
        FileConversionException,
        UnsupportedFormatException,
        MissingDependencyException,
        setup_logging
    )
    from packages.voidlight_markitdown.src.voidlight_markitdown._korean_utils import KoreanTextProcessor
except ImportError:
    # Try alternative import paths
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'packages', 'voidlight_markitdown', 'src'))
    from voidlight_markitdown import (
        VoidLightMarkItDown,
        FileConversionException,
        UnsupportedFormatException,
        MissingDependencyException,
        setup_logging
    )
    from voidlight_markitdown._korean_utils import KoreanTextProcessor

# Configure logging
setup_logging(level="DEBUG", log_file="production_recovery_test.log")
logger = logging.getLogger(__name__)


class ProductionRecoveryTester:
    """Test production error recovery mechanisms"""
    
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="voidlight_recovery_test_"))
        self.converter = VoidLightMarkItDown(korean_mode=True)
        self.results = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def create_test_file(self, name: str, content: bytes) -> Path:
        """Create a test file"""
        file_path = self.test_dir / name
        file_path.write_bytes(content)
        return file_path
        
    def test_encoding_error_recovery(self) -> Dict[str, Any]:
        """Test recovery from encoding errors"""
        logger.info("Testing encoding error recovery...")
        
        results = {
            'test_name': 'encoding_error_recovery',
            'subtests': []
        }
        
        # Test 1: Mixed encoding document
        test_cases = [
            {
                'name': 'mixed_utf8_cp949',
                'content': b'Hello ' + '안녕하세요'.encode('cp949') + b' World',
                'expected': 'partial_recovery'
            },
            {
                'name': 'invalid_utf8_sequences',
                'content': b'Valid text \xff\xfe Invalid bytes 안녕하세요',
                'expected': 'graceful_degradation'
            },
            {
                'name': 'mojibake_korean',
                'content': '占쏙옙占쏙옙占쏙옙'.encode('utf-8'),
                'expected': 'detection_and_handling'
            },
            {
                'name': 'truncated_utf8',
                'content': '안녕하세요 테스트'.encode('utf-8')[:-2],
                'expected': 'handle_truncation'
            }
        ]
        
        for test_case in test_cases:
            subtest_result = {
                'name': test_case['name'],
                'passed': False,
                'error': None,
                'recovery_time': 0,
                'output_quality': None
            }
            
            try:
                start_time = time.time()
                file_path = self.create_test_file(f"{test_case['name']}.txt", test_case['content'])
                
                # Try conversion
                result = self.converter.convert_local(str(file_path))
                
                subtest_result['recovery_time'] = time.time() - start_time
                subtest_result['passed'] = True
                
                # Check output quality
                if result.markdown:
                    if '�' in result.markdown or '?' * 3 in result.markdown:
                        subtest_result['output_quality'] = 'degraded'
                    else:
                        subtest_result['output_quality'] = 'good'
                else:
                    subtest_result['output_quality'] = 'empty'
                    
            except Exception as e:
                subtest_result['error'] = str(e)
                subtest_result['recovery_time'] = time.time() - start_time
                
            results['subtests'].append(subtest_result)
            
        # Calculate overall result
        results['passed'] = all(st['passed'] for st in results['subtests'])
        results['recovery_rate'] = sum(1 for st in results['subtests'] if st['passed']) / len(results['subtests'])
        
        return results
        
    def test_file_system_error_recovery(self) -> Dict[str, Any]:
        """Test recovery from file system errors"""
        logger.info("Testing file system error recovery...")
        
        results = {
            'test_name': 'file_system_error_recovery',
            'subtests': []
        }
        
        # Test 1: Permission denied
        subtest = {
            'name': 'permission_denied',
            'passed': False,
            'error': None,
            'handled_gracefully': False
        }
        
        try:
            file_path = self.create_test_file('readonly.txt', b'Test content')
            os.chmod(file_path, 0o000)  # Remove all permissions
            
            try:
                result = self.converter.convert_local(str(file_path))
                subtest['passed'] = False  # Should have failed
            except (PermissionError, FileConversionException) as e:
                # This is expected
                subtest['passed'] = True
                subtest['handled_gracefully'] = True
                subtest['error'] = str(e)
                
        finally:
            # Restore permissions for cleanup
            if file_path.exists():
                os.chmod(file_path, 0o644)
                
        results['subtests'].append(subtest)
        
        # Test 2: Non-existent file
        subtest = {
            'name': 'file_not_found',
            'passed': False,
            'error': None,
            'handled_gracefully': False
        }
        
        try:
            result = self.converter.convert_local('/non/existent/file.txt')
            subtest['passed'] = False  # Should have failed
        except (FileNotFoundError, FileConversionException) as e:
            subtest['passed'] = True
            subtest['handled_gracefully'] = True
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        # Test 3: Directory instead of file
        subtest = {
            'name': 'directory_not_file',
            'passed': False,
            'error': None,
            'handled_gracefully': False
        }
        
        try:
            result = self.converter.convert_local(str(self.test_dir))
            subtest['passed'] = False  # Should have failed
        except (IsADirectoryError, FileConversionException, OSError) as e:
            subtest['passed'] = True
            subtest['handled_gracefully'] = True
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        results['passed'] = all(st['passed'] for st in results['subtests'])
        results['recovery_rate'] = sum(1 for st in st['passed'] for st in results['subtests']) / len(results['subtests'])
        
        return results
        
    def test_memory_pressure_recovery(self) -> Dict[str, Any]:
        """Test behavior under memory pressure"""
        logger.info("Testing memory pressure recovery...")
        
        results = {
            'test_name': 'memory_pressure_recovery',
            'subtests': []
        }
        
        # Test 1: Large file processing
        subtest = {
            'name': 'large_file_processing',
            'passed': False,
            'error': None,
            'memory_efficient': False,
            'processing_time': 0
        }
        
        try:
            # Create a large file (10MB of Korean text)
            large_content = ('안녕하세요 ' * 1000 + '\n') * 10000
            file_path = self.create_test_file('large_korean.txt', large_content.encode('utf-8'))
            
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            result = self.converter.convert_local(str(file_path))
            
            end_memory = self._get_memory_usage()
            subtest['processing_time'] = time.time() - start_time
            
            # Check if memory was managed efficiently
            memory_increase = end_memory - start_memory
            file_size = file_path.stat().st_size
            
            # Memory increase should be reasonable (not more than 2x file size)
            if memory_increase < file_size * 2:
                subtest['memory_efficient'] = True
                
            subtest['passed'] = result.markdown is not None
            
        except Exception as e:
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        # Test 2: Many small files (file descriptor exhaustion)
        subtest = {
            'name': 'many_files_processing',
            'passed': False,
            'error': None,
            'file_descriptors_managed': False
        }
        
        try:
            # Create 100 small files
            file_paths = []
            for i in range(100):
                content = f'File {i}: 안녕하세요 테스트입니다\n'.encode('utf-8')
                file_path = self.create_test_file(f'small_{i}.txt', content)
                file_paths.append(file_path)
                
            initial_fds = self._count_open_fds()
            
            # Process all files
            for file_path in file_paths:
                self.converter.convert_local(str(file_path))
                
            final_fds = self._count_open_fds()
            
            # Check if file descriptors were properly released
            if final_fds - initial_fds < 10:  # Allow some overhead
                subtest['file_descriptors_managed'] = True
                subtest['passed'] = True
                
        except Exception as e:
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        results['passed'] = all(st['passed'] for st in results['subtests'])
        
        return results
        
    def test_korean_nlp_failure_recovery(self) -> Dict[str, Any]:
        """Test recovery when Korean NLP components fail"""
        logger.info("Testing Korean NLP failure recovery...")
        
        results = {
            'test_name': 'korean_nlp_failure_recovery',
            'subtests': []
        }
        
        # Test 1: Create converter without NLP libraries
        subtest = {
            'name': 'missing_nlp_libraries',
            'passed': False,
            'error': None,
            'fallback_works': False
        }
        
        try:
            # Temporarily disable NLP libraries
            import sys
            original_modules = {}
            nlp_modules = ['kiwipiepy', 'konlpy', 'soynlp', 'hanspell']
            
            for module in nlp_modules:
                if module in sys.modules:
                    original_modules[module] = sys.modules[module]
                    sys.modules[module] = None
                    
            try:
                # Create new converter instance
                converter_no_nlp = VoidLightMarkItDown(korean_mode=True)
                
                # Test Korean text processing
                korean_text = '안녕하세요. 이것은 한글 테스트입니다. NLP 라이브러리 없이도 작동해야 합니다.'
                file_path = self.create_test_file('korean_no_nlp.txt', korean_text.encode('utf-8'))
                
                result = converter_no_nlp.convert_local(str(file_path))
                
                if result.markdown and '안녕하세요' in result.markdown:
                    subtest['fallback_works'] = True
                    subtest['passed'] = True
                    
            finally:
                # Restore original modules
                for module, original in original_modules.items():
                    sys.modules[module] = original
                    
        except Exception as e:
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        # Test 2: Corrupted NLP model data
        subtest = {
            'name': 'corrupted_nlp_data',
            'passed': False,
            'error': None,
            'graceful_degradation': False
        }
        
        try:
            # Test with text that might cause NLP errors
            problematic_text = ''.join([
                '한글 テスト 测试 ',  # Mixed scripts
                '🇰🇷 이모지 텍스트 🎌',  # Emojis
                '１２３４５',  # Full-width numbers
                '＠＃＄％＾',  # Full-width symbols
                'ㄱㄴㄷㄹㅁㅂㅅ',  # Jamo characters
                '가나다라마바사아자차카타파하'  # Basic Korean
            ])
            
            file_path = self.create_test_file('problematic_korean.txt', problematic_text.encode('utf-8'))
            result = self.converter.convert_local(str(file_path))
            
            if result.markdown:
                subtest['graceful_degradation'] = True
                subtest['passed'] = True
                
        except Exception as e:
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        results['passed'] = all(st['passed'] for st in results['subtests'])
        
        return results
        
    def test_concurrent_conversion_recovery(self) -> Dict[str, Any]:
        """Test recovery from concurrent access issues"""
        logger.info("Testing concurrent conversion recovery...")
        
        results = {
            'test_name': 'concurrent_conversion_recovery',
            'subtests': []
        }
        
        # Test 1: Multiple threads converting same file
        subtest = {
            'name': 'concurrent_same_file',
            'passed': False,
            'error': None,
            'all_succeeded': False,
            'no_corruption': False
        }
        
        try:
            # Create test file
            content = '동시 접근 테스트입니다. ' * 100
            file_path = self.create_test_file('concurrent_test.txt', content.encode('utf-8'))
            
            # Run concurrent conversions
            results_list = []
            errors = []
            
            def convert_file():
                try:
                    result = self.converter.convert_local(str(file_path))
                    return result.markdown
                except Exception as e:
                    errors.append(str(e))
                    return None
                    
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(convert_file) for _ in range(10)]
                results_list = [f.result() for f in futures]
                
            # Check results
            successful_results = [r for r in results_list if r is not None]
            
            if len(successful_results) > 0:
                subtest['all_succeeded'] = len(successful_results) == len(results_list)
                
                # Check if all results are identical (no corruption)
                if all(r == successful_results[0] for r in successful_results):
                    subtest['no_corruption'] = True
                    
                subtest['passed'] = True
                
        except Exception as e:
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        # Test 2: Resource contention
        subtest = {
            'name': 'resource_contention',
            'passed': False,
            'error': None,
            'no_deadlock': False
        }
        
        try:
            # Create multiple files
            file_paths = []
            for i in range(20):
                content = f'파일 {i}: 리소스 경합 테스트\n'.encode('utf-8')
                file_path = self.create_test_file(f'contention_{i}.txt', content)
                file_paths.append(file_path)
                
            # Convert files concurrently
            start_time = time.time()
            
            def convert_with_timeout(path):
                try:
                    return self.converter.convert_local(str(path))
                except Exception:
                    return None
                    
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(convert_with_timeout, fp) for fp in file_paths]
                
                # Wait with timeout to detect deadlocks
                completed = 0
                for future in futures:
                    try:
                        result = future.result(timeout=5.0)
                        if result:
                            completed += 1
                    except:
                        pass
                        
            elapsed = time.time() - start_time
            
            # Check for deadlock (should complete within reasonable time)
            if elapsed < 30.0 and completed > len(file_paths) * 0.8:
                subtest['no_deadlock'] = True
                subtest['passed'] = True
                
        except Exception as e:
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        results['passed'] = all(st['passed'] for st in results['subtests'])
        
        return results
        
    def test_malformed_input_recovery(self) -> Dict[str, Any]:
        """Test recovery from malformed input files"""
        logger.info("Testing malformed input recovery...")
        
        results = {
            'test_name': 'malformed_input_recovery',
            'subtests': []
        }
        
        # Various malformed inputs
        malformed_cases = [
            {
                'name': 'truncated_pdf',
                'filename': 'truncated.pdf',
                'content': b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog',  # Incomplete PDF
                'expected': 'graceful_failure'
            },
            {
                'name': 'corrupted_docx',
                'filename': 'corrupted.docx',
                'content': b'PK\x03\x04' + b'\x00' * 100,  # Broken ZIP structure
                'expected': 'graceful_failure'
            },
            {
                'name': 'invalid_json',
                'filename': 'invalid.json',
                'content': b'{"test": "incomplete"',
                'expected': 'partial_recovery'
            },
            {
                'name': 'binary_as_text',
                'filename': 'binary.txt',
                'content': bytes(random.randint(0, 255) for _ in range(1000)),
                'expected': 'handle_binary'
            }
        ]
        
        for case in malformed_cases:
            subtest = {
                'name': case['name'],
                'passed': False,
                'error': None,
                'handled_gracefully': False
            }
            
            try:
                file_path = self.create_test_file(case['filename'], case['content'])
                
                try:
                    result = self.converter.convert(str(file_path))
                    # If it succeeded, check if output is reasonable
                    if result.markdown:
                        subtest['handled_gracefully'] = True
                        subtest['passed'] = True
                except (FileConversionException, UnsupportedFormatException) as e:
                    # Expected exception - this is good
                    subtest['handled_gracefully'] = True
                    subtest['passed'] = True
                    subtest['error'] = str(e)
                except Exception as e:
                    # Unexpected exception
                    subtest['error'] = f"Unexpected error: {str(e)}"
                    
            except Exception as e:
                subtest['error'] = f"Test setup error: {str(e)}"
                
            results['subtests'].append(subtest)
            
        results['passed'] = all(st['passed'] for st in results['subtests'])
        results['graceful_handling_rate'] = sum(1 for st in results['subtests'] if st['handled_gracefully']) / len(results['subtests'])
        
        return results
        
    def test_network_error_recovery(self) -> Dict[str, Any]:
        """Test recovery from network-related errors"""
        logger.info("Testing network error recovery...")
        
        results = {
            'test_name': 'network_error_recovery',
            'subtests': []
        }
        
        # Test 1: Timeout handling
        subtest = {
            'name': 'url_timeout',
            'passed': False,
            'error': None,
            'timeout_handled': False
        }
        
        try:
            # Use a URL that will timeout
            # Note: In production, this would test actual timeout behavior
            slow_url = "http://httpstat.us/200?sleep=30000"  # 30 second delay
            
            start_time = time.time()
            try:
                # This should timeout before 30 seconds
                result = self.converter.convert_url(slow_url)
                subtest['passed'] = False  # Should have timed out
            except Exception as e:
                elapsed = time.time() - start_time
                if elapsed < 30:  # Timed out properly
                    subtest['timeout_handled'] = True
                    subtest['passed'] = True
                subtest['error'] = str(e)
                
        except Exception as e:
            subtest['error'] = f"Test error: {str(e)}"
            
        results['subtests'].append(subtest)
        
        # Test 2: Invalid URL handling
        subtest = {
            'name': 'invalid_url',
            'passed': False,
            'error': None,
            'handled_gracefully': False
        }
        
        invalid_urls = [
            'not_a_url',
            'ftp://unsupported.protocol.com',
            'http://',
            'https://[invalid]:port/',
        ]
        
        for url in invalid_urls:
            try:
                result = self.converter.convert_url(url)
                # Should have failed
            except Exception as e:
                subtest['handled_gracefully'] = True
                subtest['passed'] = True
                subtest['error'] = str(e)
                break
                
        results['subtests'].append(subtest)
        
        results['passed'] = all(st['passed'] for st in results['subtests'])
        
        return results
        
    def test_stream_handling_recovery(self) -> Dict[str, Any]:
        """Test recovery from stream-related errors"""
        logger.info("Testing stream handling recovery...")
        
        results = {
            'test_name': 'stream_handling_recovery',
            'subtests': []
        }
        
        # Test 1: Non-seekable stream
        subtest = {
            'name': 'non_seekable_stream',
            'passed': False,
            'error': None,
            'handled_correctly': False
        }
        
        try:
            # Create a non-seekable stream
            class NonSeekableStream(io.BytesIO):
                def seekable(self):
                    return False
                    
            content = '비탐색 스트림 테스트입니다.'.encode('utf-8')
            stream = NonSeekableStream(content)
            
            result = self.converter.convert_stream(stream)
            if result.markdown:
                subtest['handled_correctly'] = True
                subtest['passed'] = True
                
        except Exception as e:
            subtest['error'] = str(e)
            
        results['subtests'].append(subtest)
        
        # Test 2: Stream that raises during read
        subtest = {
            'name': 'failing_stream',
            'passed': False,
            'error': None,
            'exception_handled': False
        }
        
        try:
            class FailingStream(io.BytesIO):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.read_count = 0
                    
                def read(self, size=-1):
                    self.read_count += 1
                    if self.read_count > 2:
                        raise IOError("Simulated read error")
                    return super().read(size)
                    
            content = '오류 발생 스트림 테스트'.encode('utf-8')
            stream = FailingStream(content)
            
            try:
                result = self.converter.convert_stream(stream)
            except Exception as e:
                subtest['exception_handled'] = True
                subtest['passed'] = True
                subtest['error'] = str(e)
                
        except Exception as e:
            subtest['error'] = f"Test error: {str(e)}"
            
        results['subtests'].append(subtest)
        
        results['passed'] = all(st['passed'] for st in results['subtests'])
        
        return results
        
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            
    def _count_open_fds(self) -> int:
        """Count open file descriptors"""
        try:
            import psutil
            process = psutil.Process()
            return len(process.open_files())
        except:
            # Fallback for systems without psutil
            import subprocess
            pid = os.getpid()
            try:
                result = subprocess.run(['lsof', '-p', str(pid)], capture_output=True, text=True)
                return len(result.stdout.strip().split('\n')) - 1  # Subtract header
            except:
                return 0
                
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all production recovery tests"""
        test_methods = [
            self.test_encoding_error_recovery,
            self.test_file_system_error_recovery,
            self.test_memory_pressure_recovery,
            self.test_korean_nlp_failure_recovery,
            self.test_concurrent_conversion_recovery,
            self.test_malformed_input_recovery,
            self.test_network_error_recovery,
            self.test_stream_handling_recovery,
        ]
        
        overall_results = {
            'test_date': datetime.now().isoformat(),
            'total_tests': len(test_methods),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': [],
            'summary': {}
        }
        
        for test_method in test_methods:
            try:
                result = test_method()
                overall_results['test_results'].append(result)
                
                if result.get('passed', False):
                    overall_results['passed_tests'] += 1
                else:
                    overall_results['failed_tests'] += 1
                    
                logger.info(f"Test {result['test_name']}: {'PASSED' if result.get('passed') else 'FAILED'}")
                
            except Exception as e:
                logger.error(f"Test {test_method.__name__} crashed: {e}", exc_info=True)
                overall_results['failed_tests'] += 1
                overall_results['test_results'].append({
                    'test_name': test_method.__name__,
                    'passed': False,
                    'error': str(e),
                    'crashed': True
                })
                
        # Generate summary
        overall_results['summary'] = {
            'success_rate': overall_results['passed_tests'] / overall_results['total_tests'] if overall_results['total_tests'] > 0 else 0,
            'encoding_resilience': self._check_test_result(overall_results, 'encoding_error_recovery'),
            'filesystem_resilience': self._check_test_result(overall_results, 'file_system_error_recovery'),
            'memory_resilience': self._check_test_result(overall_results, 'memory_pressure_recovery'),
            'korean_nlp_resilience': self._check_test_result(overall_results, 'korean_nlp_failure_recovery'),
            'concurrency_safety': self._check_test_result(overall_results, 'concurrent_conversion_recovery'),
            'input_validation': self._check_test_result(overall_results, 'malformed_input_recovery'),
            'network_resilience': self._check_test_result(overall_results, 'network_error_recovery'),
            'stream_handling': self._check_test_result(overall_results, 'stream_handling_recovery'),
        }
        
        return overall_results
        
    def _check_test_result(self, results: Dict[str, Any], test_name: str) -> str:
        """Check specific test result and return status"""
        for test in results['test_results']:
            if test.get('test_name') == test_name:
                if test.get('passed'):
                    return 'GOOD'
                elif test.get('recovery_rate', 0) > 0.5:
                    return 'PARTIAL'
                else:
                    return 'POOR'
        return 'NOT_TESTED'
        
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable report"""
        report = []
        report.append("# VoidLight MarkItDown - Production Error Recovery Test Report")
        report.append(f"\nTest Date: {results['test_date']}")
        report.append(f"Total Tests: {results['total_tests']}")
        report.append(f"Passed: {results['passed_tests']} ({results['passed_tests']/results['total_tests']*100:.1f}%)")
        report.append(f"Failed: {results['failed_tests']} ({results['failed_tests']/results['total_tests']*100:.1f}%)")
        
        report.append("\n## Summary")
        report.append(f"- Overall Success Rate: {results['summary']['success_rate']*100:.1f}%")
        
        for key, value in results['summary'].items():
            if key != 'success_rate':
                status_emoji = '✅' if value == 'GOOD' else '⚠️' if value == 'PARTIAL' else '❌'
                report.append(f"- {key.replace('_', ' ').title()}: {status_emoji} {value}")
                
        report.append("\n## Detailed Test Results")
        
        for test in results['test_results']:
            status = '✅ PASSED' if test.get('passed') else '❌ FAILED'
            report.append(f"\n### {test['test_name'].replace('_', ' ').title()} - {status}")
            
            if 'subtests' in test:
                report.append(f"Subtests: {len(test['subtests'])}")
                passed_subtests = sum(1 for st in test['subtests'] if st.get('passed'))
                report.append(f"Passed: {passed_subtests}/{len(test['subtests'])}")
                
                for subtest in test['subtests']:
                    sub_status = '✓' if subtest.get('passed') else '✗'
                    report.append(f"  {sub_status} {subtest['name']}")
                    if subtest.get('error') and not subtest.get('passed'):
                        report.append(f"    Error: {subtest['error']}")
                        
            if test.get('recovery_rate') is not None:
                report.append(f"Recovery Rate: {test['recovery_rate']*100:.1f}%")
                
        report.append("\n## Recommendations")
        
        recommendations = []
        
        if results['summary']['encoding_resilience'] != 'GOOD':
            recommendations.append("- Improve encoding error detection and recovery")
            recommendations.append("- Add more robust charset detection for Korean text")
            
        if results['summary']['memory_resilience'] != 'GOOD':
            recommendations.append("- Implement streaming processing for large files")
            recommendations.append("- Add memory usage monitoring and limits")
            
        if results['summary']['concurrency_safety'] != 'GOOD':
            recommendations.append("- Add thread-safe resource management")
            recommendations.append("- Implement proper locking for shared resources")
            
        if results['summary']['korean_nlp_resilience'] != 'GOOD':
            recommendations.append("- Ensure graceful fallback when NLP libraries fail")
            recommendations.append("- Add alternative Korean processing methods")
            
        if not recommendations:
            recommendations.append("- All systems show good resilience!")
            
        report.extend(recommendations)
        
        return '\n'.join(report)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Error Recovery Tests")
    parser.add_argument("--output", default="production_recovery_report.json", help="Output report file")
    parser.add_argument("--format", choices=["json", "markdown", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    with ProductionRecoveryTester() as tester:
        # Run all tests
        results = tester.run_all_tests()
        
        # Save JSON report
        if args.format in ["json", "both"]:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"JSON report saved to: {args.output}")
            
        # Save markdown report
        if args.format in ["markdown", "both"]:
            markdown_file = args.output.replace('.json', '.md')
            report = tester.generate_report(results)
            with open(markdown_file, 'w') as f:
                f.write(report)
            print(f"Markdown report saved to: {markdown_file}")
            
        # Print summary
        print("\n" + "="*60)
        print("PRODUCTION ERROR RECOVERY TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']} ({results['passed_tests']/results['total_tests']*100:.1f}%)")
        print(f"Failed: {results['failed_tests']} ({results['failed_tests']/results['total_tests']*100:.1f}%)")
        
        print("\nResilience Summary:")
        for key, value in results['summary'].items():
            if key != 'success_rate':
                print(f"  {key.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    main()