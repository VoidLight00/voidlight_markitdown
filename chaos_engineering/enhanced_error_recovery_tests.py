#!/usr/bin/env python3
"""
Enhanced Production Error Recovery Tests for VoidLight MarkItDown
Comprehensive validation of fault tolerance and error recovery systems
"""

import asyncio
import concurrent.futures
import io
import json
import logging
import os
import random
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import multiprocessing
import psutil
import requests
from unittest.mock import Mock, patch

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
setup_logging(level="DEBUG", log_file="enhanced_error_recovery_test.log")
logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors to test"""
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    MEMORY = "memory"
    CPU = "cpu"
    ENCODING = "encoding"
    DEPENDENCY = "dependency"
    CONCURRENCY = "concurrency"
    KOREAN_SPECIFIC = "korean_specific"


@dataclass
class ErrorRecoveryMetrics:
    """Metrics for error recovery effectiveness"""
    error_type: str
    detection_time: float = 0.0
    recovery_time: float = 0.0
    data_integrity: float = 1.0  # 0-1 scale
    resource_cleanup: bool = True
    graceful_degradation: bool = False
    error_propagation_contained: bool = True
    retry_count: int = 0
    fallback_used: bool = False
    partial_success: bool = False
    error_message_quality: float = 0.0  # 0-1 scale
    
    @property
    def recovery_score(self) -> float:
        """Calculate overall recovery score"""
        score = 0.0
        
        # Fast detection (max 10 points)
        if self.detection_time < 0.1:
            score += 10
        elif self.detection_time < 1.0:
            score += 5
        elif self.detection_time < 5.0:
            score += 2
            
        # Fast recovery (max 10 points)
        if self.recovery_time < 1.0:
            score += 10
        elif self.recovery_time < 5.0:
            score += 5
        elif self.recovery_time < 30.0:
            score += 2
            
        # Data integrity (max 20 points)
        score += self.data_integrity * 20
        
        # Resource cleanup (max 10 points)
        if self.resource_cleanup:
            score += 10
            
        # Graceful degradation (max 10 points)
        if self.graceful_degradation:
            score += 10
            
        # Error containment (max 10 points)
        if self.error_propagation_contained:
            score += 10
            
        # Appropriate retry behavior (max 10 points)
        if 1 <= self.retry_count <= 3:
            score += 10
        elif self.retry_count == 0 and not self.fallback_used:
            score += 0
        elif self.retry_count > 5:
            score -= 5
            
        # Fallback usage (max 10 points)
        if self.fallback_used and self.partial_success:
            score += 10
            
        # Error message quality (max 10 points)
        score += self.error_message_quality * 10
        
        return score / 100.0  # Normalize to 0-1


class NetworkErrorSimulator:
    """Simulate various network errors"""
    
    @staticmethod
    def simulate_timeout(delay: float = 60.0):
        """Simulate network timeout"""
        def delayed_response(*args, **kwargs):
            time.sleep(delay)
            raise requests.Timeout("Simulated timeout")
        return delayed_response
    
    @staticmethod
    def simulate_connection_error():
        """Simulate connection error"""
        def connection_error(*args, **kwargs):
            raise requests.ConnectionError("Simulated connection error")
        return connection_error
    
    @staticmethod
    def simulate_dns_failure():
        """Simulate DNS resolution failure"""
        def dns_failure(*args, **kwargs):
            raise socket.gaierror("Simulated DNS failure")
        return dns_failure
    
    @staticmethod
    def simulate_partial_response(content_ratio: float = 0.5):
        """Simulate partial response"""
        def partial_response(*args, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"Partial content" * int(100 * content_ratio)
            response.headers = {'content-type': 'text/html'}
            response.raise_for_status = Mock()
            return response
        return partial_response
    
    @staticmethod
    def simulate_slow_network(delay_per_chunk: float = 0.5):
        """Simulate slow network with delays"""
        class SlowResponse:
            def __init__(self):
                self.status_code = 200
                self.headers = {'content-type': 'text/html'}
                self.content = b"Slow network test content" * 100
                
            def iter_content(self, chunk_size=1024):
                for i in range(0, len(self.content), chunk_size):
                    time.sleep(delay_per_chunk)
                    yield self.content[i:i+chunk_size]
                    
            def raise_for_status(self):
                pass
                
        def slow_response(*args, **kwargs):
            return SlowResponse()
        return slow_response


class FileSystemErrorSimulator:
    """Simulate file system errors"""
    
    @staticmethod
    @contextmanager
    def simulate_permission_denied(file_path: Path):
        """Temporarily make file unreadable"""
        original_mode = file_path.stat().st_mode
        try:
            os.chmod(file_path, 0o000)
            yield
        finally:
            os.chmod(file_path, original_mode)
    
    @staticmethod
    @contextmanager
    def simulate_disk_full():
        """Simulate disk full error"""
        original_write = os.write
        
        def failing_write(fd, data):
            raise OSError(28, "No space left on device")
            
        try:
            os.write = failing_write
            yield
        finally:
            os.write = original_write
    
    @staticmethod
    def create_corrupted_file(file_path: Path, corruption_type: str = "truncated"):
        """Create various types of corrupted files"""
        if corruption_type == "truncated":
            # Create truncated PDF
            content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog"
        elif corruption_type == "invalid_magic":
            # Invalid file signature
            content = b"\xFF\xFE\xFF\xFE" + b"Invalid file content"
        elif corruption_type == "mixed_encoding":
            # Mixed encoding content
            content = "Hello ".encode('utf-8') + "안녕하세요".encode('cp949') + " World".encode('utf-8')
        elif corruption_type == "binary_garbage":
            # Random binary data
            content = os.urandom(1024)
        else:
            content = b"Corrupted content"
            
        file_path.write_bytes(content)


class MemoryErrorSimulator:
    """Simulate memory-related errors"""
    
    def __init__(self):
        self.memory_hogs = []
    
    def simulate_memory_pressure(self, target_mb: int = 500):
        """Consume specified amount of memory"""
        try:
            # Allocate memory in chunks
            chunk_size = 10 * 1024 * 1024  # 10MB chunks
            chunks_needed = target_mb // 10
            
            for _ in range(chunks_needed):
                self.memory_hogs.append(bytearray(chunk_size))
                
        except MemoryError:
            logger.info("Memory allocation failed - system under pressure")
    
    def simulate_memory_leak(self, leak_rate_mb_per_sec: float = 10):
        """Simulate gradual memory leak"""
        def leak_memory():
            while True:
                try:
                    self.memory_hogs.append(bytearray(int(leak_rate_mb_per_sec * 1024 * 1024)))
                    time.sleep(1)
                except MemoryError:
                    break
                    
        thread = threading.Thread(target=leak_memory, daemon=True)
        thread.start()
        return thread
    
    def cleanup(self):
        """Release allocated memory"""
        self.memory_hogs.clear()


class KoreanErrorSimulator:
    """Simulate Korean-specific errors"""
    
    @staticmethod
    def create_mojibake_text() -> bytes:
        """Create mojibake (garbled text)"""
        korean_text = "안녕하세요. 한글 테스트입니다."
        # Encode as UTF-8, decode as CP949, re-encode
        try:
            mojibake = korean_text.encode('utf-8').decode('cp949', errors='replace')
            return mojibake.encode('utf-8')
        except:
            return b"????? ???? ??????"
    
    @staticmethod
    def create_mixed_encoding_document() -> bytes:
        """Create document with mixed encodings"""
        parts = [
            "English Header\n".encode('ascii'),
            "한글 제목\n".encode('utf-8'),
            "中文内容\n".encode('gbk', errors='ignore'),
            "일본어 コンテンツ\n".encode('shift_jis', errors='ignore'),
            "More Korean 더 많은 한글".encode('cp949')
        ]
        return b''.join(parts)
    
    @staticmethod
    def create_invalid_unicode() -> bytes:
        """Create text with invalid Unicode sequences"""
        valid_korean = "정상적인 한글 텍스트"
        invalid_sequences = [
            b'\xed\xa0\x80',  # Invalid UTF-8 sequence
            b'\xf0\x90\x80',  # Incomplete 4-byte sequence
            b'\xff\xfe',      # BOM in wrong place
        ]
        
        content = valid_korean.encode('utf-8')
        for seq in invalid_sequences:
            pos = random.randint(0, len(content))
            content = content[:pos] + seq + content[pos:]
            
        return content


class EnhancedErrorRecoveryTester:
    """Comprehensive error recovery testing framework"""
    
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="enhanced_recovery_test_"))
        self.converter = VoidLightMarkItDown(korean_mode=True)
        self.results = []
        self.network_simulator = NetworkErrorSimulator()
        self.fs_simulator = FileSystemErrorSimulator()
        self.memory_simulator = MemoryErrorSimulator()
        self.korean_simulator = KoreanErrorSimulator()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        self.memory_simulator.cleanup()
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    async def test_network_timeout_recovery(self) -> ErrorRecoveryMetrics:
        """Test recovery from network timeouts"""
        logger.info("Testing network timeout recovery...")
        
        metrics = ErrorRecoveryMetrics(error_type="network_timeout")
        start_time = time.time()
        
        # Mock the requests session with timeout
        with patch.object(
            self.converter._requests_session, 
            'get', 
            side_effect=self.network_simulator.simulate_timeout(2.0)
        ):
            try:
                # Attempt to convert a URL
                detection_start = time.time()
                result = self.converter.convert_url("https://example.com/test.html")
                
            except Exception as e:
                metrics.detection_time = time.time() - detection_start
                
                # Check error message quality
                error_msg = str(e)
                if "timeout" in error_msg.lower():
                    metrics.error_message_quality = 0.8
                if "retry" in error_msg.lower() or "attempted" in error_msg.lower():
                    metrics.error_message_quality = 1.0
                    
                # Check if error is properly typed
                metrics.error_propagation_contained = isinstance(e, (FileConversionException, requests.Timeout))
                
        metrics.recovery_time = time.time() - start_time
        
        # Test with retry mechanism
        retry_count = 0
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                with patch.object(
                    self.converter._requests_session, 
                    'get', 
                    side_effect=self.network_simulator.simulate_timeout(0.5) if attempt < 2 
                    else self.network_simulator.simulate_partial_response()
                ):
                    result = self.converter.convert_url("https://example.com/test.html")
                    metrics.partial_success = True
                    break
            except:
                retry_count += 1
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                
        metrics.retry_count = retry_count
        
        return metrics
    
    async def test_file_permission_recovery(self) -> ErrorRecoveryMetrics:
        """Test recovery from file permission errors"""
        logger.info("Testing file permission recovery...")
        
        metrics = ErrorRecoveryMetrics(error_type="file_permission_denied")
        
        # Create test file
        test_file = self.test_dir / "permission_test.txt"
        test_file.write_text("Test content for permission testing")
        
        start_time = time.time()
        
        with self.fs_simulator.simulate_permission_denied(test_file):
            try:
                detection_start = time.time()
                result = self.converter.convert_local(str(test_file))
            except Exception as e:
                metrics.detection_time = time.time() - detection_start
                
                # Check error handling
                error_msg = str(e)
                if "permission" in error_msg.lower() or "access" in error_msg.lower():
                    metrics.error_message_quality = 1.0
                elif "read" in error_msg.lower():
                    metrics.error_message_quality = 0.7
                else:
                    metrics.error_message_quality = 0.3
                    
                metrics.error_propagation_contained = isinstance(e, (FileConversionException, PermissionError, OSError))
                
        # Verify file is accessible again
        try:
            content = test_file.read_text()
            metrics.resource_cleanup = True
        except:
            metrics.resource_cleanup = False
            
        metrics.recovery_time = time.time() - start_time
        
        return metrics
    
    async def test_memory_exhaustion_recovery(self) -> ErrorRecoveryMetrics:
        """Test recovery from memory exhaustion"""
        logger.info("Testing memory exhaustion recovery...")
        
        metrics = ErrorRecoveryMetrics(error_type="memory_exhaustion")
        
        # Create large test file
        large_file = self.test_dir / "large_file.txt"
        large_content = "Large content line\n" * 1000000  # ~19MB
        large_file.write_text(large_content)
        
        # Monitor initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Simulate memory pressure
        self.memory_simulator.simulate_memory_pressure(target_mb=100)
        
        start_time = time.time()
        
        try:
            detection_start = time.time()
            result = self.converter.convert_local(str(large_file))
            
            # Check if conversion succeeded despite memory pressure
            if result and result.markdown:
                metrics.graceful_degradation = True
                metrics.partial_success = True
                
        except MemoryError as e:
            metrics.detection_time = time.time() - detection_start
            metrics.error_propagation_contained = True
            metrics.error_message_quality = 1.0
            
        except Exception as e:
            metrics.detection_time = time.time() - detection_start
            
            if "memory" in str(e).lower():
                metrics.error_message_quality = 0.8
            else:
                metrics.error_message_quality = 0.3
                
        finally:
            # Cleanup memory
            self.memory_simulator.cleanup()
            
            # Check memory was released
            time.sleep(0.5)  # Allow GC to run
            final_memory = process.memory_info().rss
            
            # Memory should return close to initial (within 50MB)
            if final_memory - initial_memory < 50 * 1024 * 1024:
                metrics.resource_cleanup = True
            else:
                metrics.resource_cleanup = False
                
        metrics.recovery_time = time.time() - start_time
        
        return metrics
    
    async def test_korean_encoding_recovery(self) -> ErrorRecoveryMetrics:
        """Test recovery from Korean encoding errors"""
        logger.info("Testing Korean encoding recovery...")
        
        metrics = ErrorRecoveryMetrics(error_type="korean_encoding_error")
        
        # Create files with various encoding issues
        test_cases = [
            ("mojibake.txt", self.korean_simulator.create_mojibake_text()),
            ("mixed_encoding.txt", self.korean_simulator.create_mixed_encoding_document()),
            ("invalid_unicode.txt", self.korean_simulator.create_invalid_unicode()),
        ]
        
        total_tests = len(test_cases)
        successful_recoveries = 0
        
        for filename, content in test_cases:
            test_file = self.test_dir / filename
            test_file.write_bytes(content)
            
            start_time = time.time()
            
            try:
                result = self.converter.convert_local(str(test_file))
                
                if result and result.markdown:
                    # Check if output is readable
                    if "�" not in result.markdown and "?" * 3 not in result.markdown:
                        successful_recoveries += 1
                        metrics.partial_success = True
                    else:
                        # Partial recovery - some garbled text
                        successful_recoveries += 0.5
                        metrics.graceful_degradation = True
                        
            except Exception as e:
                # Should handle encoding errors gracefully
                if isinstance(e, UnicodeDecodeError):
                    metrics.error_propagation_contained = False
                else:
                    metrics.error_propagation_contained = True
                    
        metrics.data_integrity = successful_recoveries / total_tests
        metrics.recovery_time = time.time() - start_time
        
        # Korean processor should provide fallbacks
        if hasattr(self.converter, '_korean_processor') and self.converter._korean_processor:
            metrics.fallback_used = True
            
        return metrics
    
    async def test_concurrent_access_recovery(self) -> ErrorRecoveryMetrics:
        """Test recovery from concurrent access issues"""
        logger.info("Testing concurrent access recovery...")
        
        metrics = ErrorRecoveryMetrics(error_type="concurrent_access")
        
        # Create shared test file
        shared_file = self.test_dir / "shared_file.txt"
        shared_file.write_text("Shared content for concurrent access testing")
        
        errors_caught = []
        results = []
        
        def concurrent_convert(thread_id: int):
            """Function to run in threads"""
            try:
                # Each thread tries to convert the same file
                result = self.converter.convert_local(str(shared_file))
                results.append((thread_id, result))
            except Exception as e:
                errors_caught.append((thread_id, e))
                
        start_time = time.time()
        
        # Run multiple threads
        threads = []
        num_threads = 10
        
        for i in range(num_threads):
            thread = threading.Thread(target=concurrent_convert, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)
            
        metrics.recovery_time = time.time() - start_time
        
        # Analyze results
        if len(results) == num_threads:
            # All threads succeeded
            metrics.data_integrity = 1.0
            metrics.error_propagation_contained = True
        elif len(results) > 0:
            # Some threads succeeded
            metrics.data_integrity = len(results) / num_threads
            metrics.graceful_degradation = True
            
        # Check for thread safety issues
        if not errors_caught:
            metrics.resource_cleanup = True
        else:
            # Analyze error types
            for _, error in errors_caught:
                if "thread" in str(error).lower() or "lock" in str(error).lower():
                    metrics.error_message_quality = 1.0
                    break
                    
        return metrics
    
    async def test_dependency_failure_recovery(self) -> ErrorRecoveryMetrics:
        """Test recovery from dependency failures"""
        logger.info("Testing dependency failure recovery...")
        
        metrics = ErrorRecoveryMetrics(error_type="dependency_failure")
        
        # Create a file that requires optional dependencies
        docx_file = self.test_dir / "test.docx"
        
        # Create minimal DOCX structure
        import zipfile
        with zipfile.ZipFile(docx_file, 'w') as zf:
            zf.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types></Types>')
            zf.writestr('word/document.xml', '<?xml version="1.0"?><document><body><p>Test</p></body></document>')
            
        # Mock missing dependency
        with patch('importlib.import_module', side_effect=ImportError("python-docx not installed")):
            start_time = time.time()
            
            try:
                result = self.converter.convert_local(str(docx_file))
                
            except MissingDependencyException as e:
                metrics.detection_time = time.time() - start_time
                metrics.error_propagation_contained = True
                
                # Check error message quality
                error_msg = str(e)
                if "install" in error_msg and ("python-docx" in error_msg or "docx" in error_msg):
                    metrics.error_message_quality = 1.0
                elif "dependency" in error_msg:
                    metrics.error_message_quality = 0.7
                else:
                    metrics.error_message_quality = 0.3
                    
            except Exception as e:
                metrics.detection_time = time.time() - start_time
                metrics.error_propagation_contained = False
                
        metrics.recovery_time = time.time() - start_time
        
        return metrics
    
    async def test_circuit_breaker_behavior(self) -> ErrorRecoveryMetrics:
        """Test circuit breaker pattern implementation"""
        logger.info("Testing circuit breaker behavior...")
        
        metrics = ErrorRecoveryMetrics(error_type="circuit_breaker")
        
        # Simulate repeated failures
        failure_count = 0
        success_after_failures = False
        
        with patch.object(
            self.converter._requests_session,
            'get',
            side_effect=[
                requests.ConnectionError("Failed"),
                requests.ConnectionError("Failed"),
                requests.ConnectionError("Failed"),
                requests.ConnectionError("Failed"),
                requests.ConnectionError("Failed"),
                # After 5 failures, circuit should open
                Mock(status_code=200, content=b"Success", headers={'content-type': 'text/html'})
            ]
        ):
            start_time = time.time()
            
            for attempt in range(10):
                try:
                    result = self.converter.convert_url("https://example.com/test.html")
                    success_after_failures = True
                    break
                except:
                    failure_count += 1
                    
                # Small delay between attempts
                time.sleep(0.1)
                
        metrics.recovery_time = time.time() - start_time
        
        # Check if circuit breaker behavior is present
        if failure_count >= 5 and not success_after_failures:
            # Circuit opened after threshold
            metrics.fallback_used = True
            metrics.graceful_degradation = True
        elif success_after_failures and failure_count < 10:
            # Circuit allowed retry after cooldown
            metrics.partial_success = True
            
        metrics.retry_count = failure_count
        
        return metrics
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all error recovery tests"""
        logger.info("Starting enhanced error recovery test suite...")
        
        test_methods = [
            self.test_network_timeout_recovery,
            self.test_file_permission_recovery,
            self.test_memory_exhaustion_recovery,
            self.test_korean_encoding_recovery,
            self.test_concurrent_access_recovery,
            self.test_dependency_failure_recovery,
            self.test_circuit_breaker_behavior,
        ]
        
        results = []
        
        for test_method in test_methods:
            logger.info(f"\nRunning {test_method.__name__}...")
            
            try:
                metrics = await test_method()
                results.append({
                    'test_name': test_method.__name__,
                    'metrics': metrics,
                    'score': metrics.recovery_score,
                    'passed': metrics.recovery_score >= 0.7
                })
                
                logger.info(f"Test completed - Score: {metrics.recovery_score:.2f}")
                
            except Exception as e:
                logger.error(f"Test failed with unexpected error: {e}", exc_info=True)
                results.append({
                    'test_name': test_method.__name__,
                    'error': str(e),
                    'score': 0.0,
                    'passed': False
                })
                
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('passed', False))
        average_score = sum(r.get('score', 0) for r in results) / total_tests if total_tests > 0 else 0
        
        # Categorize results
        by_category = {}
        for result in results:
            if 'metrics' in result:
                category = result['metrics'].error_type.split('_')[0]
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(result)
                
        return {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'average_score': average_score,
            'results': results,
            'by_category': by_category,
            'recommendations': self._generate_recommendations(results)
        }
    
    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze patterns
        low_score_tests = [r for r in results if r.get('score', 0) < 0.7]
        
        for test in low_score_tests:
            if 'metrics' not in test:
                continue
                
            metrics = test['metrics']
            test_name = test['test_name']
            
            if metrics.detection_time > 5.0:
                recommendations.append(f"Improve error detection speed in {test_name}")
                
            if metrics.recovery_time > 30.0:
                recommendations.append(f"Implement faster recovery mechanisms for {metrics.error_type}")
                
            if not metrics.resource_cleanup:
                recommendations.append(f"Ensure proper resource cleanup in {metrics.error_type} scenarios")
                
            if not metrics.graceful_degradation and metrics.data_integrity < 0.5:
                recommendations.append(f"Implement graceful degradation for {metrics.error_type}")
                
            if metrics.retry_count == 0 and not metrics.fallback_used:
                recommendations.append(f"Add retry logic for {metrics.error_type}")
                
            if metrics.retry_count > 5:
                recommendations.append(f"Implement exponential backoff for {metrics.error_type}")
                
            if metrics.error_message_quality < 0.5:
                recommendations.append(f"Improve error messages for {metrics.error_type}")
                
        # Remove duplicates and sort by priority
        recommendations = list(set(recommendations))
        
        return recommendations


async def main():
    """Main test execution"""
    with EnhancedErrorRecoveryTester() as tester:
        results = await tester.run_all_tests()
        
        # Generate report
        report_path = Path("enhanced_error_recovery_report.json")
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        # Print summary
        print("\n" + "="*60)
        print("Enhanced Error Recovery Test Results")
        print("="*60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Average Score: {results['average_score']:.2%}")
        print("\nRecommendations:")
        for rec in results['recommendations']:
            print(f"  - {rec}")
            
        print(f"\nDetailed report saved to: {report_path}")
        
        return results


if __name__ == "__main__":
    asyncio.run(main())