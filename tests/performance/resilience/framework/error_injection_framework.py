#!/usr/bin/env python3
"""
Error Injection Framework for VoidLight MarkItDown
Systematic error injection for resilience testing
"""

import os
import sys
import json
import time
import random
import signal
import threading
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Callable

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class ErrorInjector:
    """Framework for injecting various types of errors"""
    
    def __init__(self):
        self.active_injections = {}
        self.injection_history = []
        
    @contextmanager
    def inject_network_failure(self, failure_rate: float = 0.5, latency_ms: int = 5000):
        """Inject network failures and latency"""
        print(f"💉 Injecting network issues (failure_rate={failure_rate}, latency={latency_ms}ms)")
        
        # Store original socket functions
        import socket
        original_getaddrinfo = socket.getaddrinfo
        original_create_connection = socket.create_connection
        
        def failing_getaddrinfo(*args, **kwargs):
            if random.random() < failure_rate:
                raise socket.gaierror("Injected DNS failure")
            time.sleep(latency_ms / 1000.0)  # Add latency
            return original_getaddrinfo(*args, **kwargs)
        
        def failing_create_connection(*args, **kwargs):
            if random.random() < failure_rate:
                raise socket.timeout("Injected connection timeout")
            return original_create_connection(*args, **kwargs)
        
        # Monkey patch
        socket.getaddrinfo = failing_getaddrinfo
        socket.create_connection = failing_create_connection
        
        injection_id = f"network_{time.time()}"
        self.active_injections[injection_id] = "network_failure"
        
        try:
            yield
        finally:
            # Restore original functions
            socket.getaddrinfo = original_getaddrinfo
            socket.create_connection = original_create_connection
            del self.active_injections[injection_id]
            print("✅ Network injection removed")
    
    @contextmanager
    def inject_file_system_errors(self, error_rate: float = 0.3):
        """Inject file system errors"""
        print(f"💉 Injecting file system errors (error_rate={error_rate})")
        
        import builtins
        original_open = builtins.open
        
        def failing_open(file, mode='r', *args, **kwargs):
            if random.random() < error_rate:
                errors = [
                    PermissionError("Injected permission denied"),
                    FileNotFoundError("Injected file not found"),
                    OSError("Injected disk full"),
                    IOError("Injected I/O error")
                ]
                raise random.choice(errors)
            return original_open(file, mode, *args, **kwargs)
        
        builtins.open = failing_open
        injection_id = f"filesystem_{time.time()}"
        self.active_injections[injection_id] = "filesystem_errors"
        
        try:
            yield
        finally:
            builtins.open = original_open
            del self.active_injections[injection_id]
            print("✅ File system injection removed")
    
    @contextmanager
    def inject_memory_pressure(self, mb_to_allocate: int = 500):
        """Inject memory pressure by allocating memory"""
        print(f"💉 Injecting memory pressure ({mb_to_allocate}MB)")
        
        # Allocate memory
        memory_hog = []
        try:
            for _ in range(mb_to_allocate):
                # Allocate 1MB chunks
                memory_hog.append(b'x' * (1024 * 1024))
            
            injection_id = f"memory_{time.time()}"
            self.active_injections[injection_id] = "memory_pressure"
            
            yield
        finally:
            # Release memory
            memory_hog.clear()
            del self.active_injections[injection_id]
            print("✅ Memory pressure removed")
    
    @contextmanager
    def inject_cpu_throttling(self, load_factor: float = 0.8):
        """Inject CPU load to simulate throttling"""
        print(f"💉 Injecting CPU throttling (load={load_factor:.0%})")
        
        stop_flag = threading.Event()
        
        def cpu_burner():
            while not stop_flag.is_set():
                # Burn CPU cycles
                start = time.time()
                while time.time() - start < 0.1 * load_factor:
                    _ = sum(i * i for i in range(1000))
                time.sleep(0.1 * (1 - load_factor))
        
        # Start CPU burning threads
        threads = []
        for _ in range(os.cpu_count() or 4):
            t = threading.Thread(target=cpu_burner)
            t.daemon = True
            t.start()
            threads.append(t)
        
        injection_id = f"cpu_{time.time()}"
        self.active_injections[injection_id] = "cpu_throttling"
        
        try:
            yield
        finally:
            stop_flag.set()
            for t in threads:
                t.join(timeout=1)
            del self.active_injections[injection_id]
            print("✅ CPU throttling removed")
    
    @contextmanager
    def inject_random_exceptions(self, exception_rate: float = 0.2):
        """Inject random exceptions in function calls"""
        print(f"💉 Injecting random exceptions (rate={exception_rate})")
        
        def exception_wrapper(func):
            def wrapper(*args, **kwargs):
                if random.random() < exception_rate:
                    exceptions = [
                        ValueError("Injected value error"),
                        TypeError("Injected type error"),
                        RuntimeError("Injected runtime error"),
                        KeyError("Injected key error")
                    ]
                    raise random.choice(exceptions)
                return func(*args, **kwargs)
            return wrapper
        
        # Store for cleanup
        wrapped_functions = []
        
        # Wrap common functions
        import json
        import os
        
        original_json_loads = json.loads
        original_os_path_exists = os.path.exists
        
        json.loads = exception_wrapper(json.loads)
        os.path.exists = exception_wrapper(os.path.exists)
        
        injection_id = f"exceptions_{time.time()}"
        self.active_injections[injection_id] = "random_exceptions"
        
        try:
            yield
        finally:
            # Restore original functions
            json.loads = original_json_loads
            os.path.exists = original_os_path_exists
            del self.active_injections[injection_id]
            print("✅ Exception injection removed")
    
    @contextmanager
    def inject_encoding_errors(self):
        """Inject encoding-related errors"""
        print("💉 Injecting encoding errors")
        
        import codecs
        original_open = codecs.open
        
        def failing_codec_open(filename, mode='r', encoding=None, *args, **kwargs):
            # Randomly change encoding
            if encoding and random.random() < 0.3:
                wrong_encodings = ['ascii', 'latin-1', 'cp437']
                encoding = random.choice(wrong_encodings)
            return original_open(filename, mode, encoding, *args, **kwargs)
        
        codecs.open = failing_codec_open
        injection_id = f"encoding_{time.time()}"
        self.active_injections[injection_id] = "encoding_errors"
        
        try:
            yield
        finally:
            codecs.open = original_open
            del self.active_injections[injection_id]
            print("✅ Encoding injection removed")
    
    def get_active_injections(self) -> Dict[str, str]:
        """Get currently active injections"""
        return self.active_injections.copy()
    
    def clear_all_injections(self):
        """Emergency clear of all injections"""
        print("🚨 Clearing all active injections")
        self.active_injections.clear()


class ResilienceValidator:
    """Validates system resilience under various error conditions"""
    
    def __init__(self):
        self.injector = ErrorInjector()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": {},
            "metrics": {
                "total_scenarios": 0,
                "resilient": 0,
                "degraded": 0,
                "failed": 0
            }
        }
    
    def test_network_resilience(self):
        """Test resilience to network failures"""
        from packages.voidlight_markitdown.src.voidlight_markitdown import VoidLightMarkItDown
        
        print("\n🧪 Testing network resilience...")
        scenario = "network_failures"
        
        with self.injector.inject_network_failure(failure_rate=0.7, latency_ms=3000):
            converter = VoidLightMarkItDown()
            
            # Test Wikipedia converter (network dependent)
            test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
            
            start_time = time.time()
            attempts = 0
            success = False
            
            for attempt in range(3):  # Test retry logic
                attempts += 1
                try:
                    result = converter.convert(test_url)
                    if result and result.markdown:
                        success = True
                        break
                except Exception as e:
                    print(f"  Attempt {attempt + 1} failed: {type(e).__name__}")
                    time.sleep(2)  # Wait before retry
            
            duration = time.time() - start_time
            
            self.results["scenarios"][scenario] = {
                "status": "resilient" if success else "failed",
                "attempts": attempts,
                "duration": duration,
                "details": "System retried and recovered" if success else "Failed after retries"
            }
    
    def test_filesystem_resilience(self):
        """Test resilience to file system errors"""
        from packages.voidlight_markitdown.src.voidlight_markitdown import VoidLightMarkItDown
        
        print("\n🧪 Testing file system resilience...")
        scenario = "filesystem_errors"
        
        # Create test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content 한국어 내용")
            test_file = f.name
        
        successes = 0
        total_attempts = 10
        
        with self.injector.inject_file_system_errors(error_rate=0.5):
            converter = VoidLightMarkItDown(korean_mode=True)
            
            for i in range(total_attempts):
                try:
                    result = converter.convert(test_file)
                    if result and result.markdown:
                        successes += 1
                except Exception:
                    pass  # Count failures
        
        # Cleanup
        os.unlink(test_file)
        
        success_rate = successes / total_attempts
        self.results["scenarios"][scenario] = {
            "status": "resilient" if success_rate >= 0.3 else "failed",
            "success_rate": success_rate,
            "details": f"{successes}/{total_attempts} operations succeeded"
        }
    
    def test_memory_resilience(self):
        """Test resilience under memory pressure"""
        from packages.voidlight_markitdown.src.voidlight_markitdown import VoidLightMarkItDown
        
        print("\n🧪 Testing memory pressure resilience...")
        scenario = "memory_pressure"
        
        import tempfile
        # Create a moderately large file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("한국어 테스트 문서\n" * 100000)  # ~2MB
            test_file = f.name
        
        with self.injector.inject_memory_pressure(mb_to_allocate=300):
            converter = VoidLightMarkItDown(korean_mode=True)
            
            try:
                start_time = time.time()
                result = converter.convert(test_file)
                duration = time.time() - start_time
                
                if result and result.markdown:
                    status = "resilient"
                    details = f"Completed in {duration:.2f}s under memory pressure"
                else:
                    status = "degraded"
                    details = "Completed but with empty result"
            except Exception as e:
                status = "failed"
                details = f"Failed with {type(e).__name__}"
        
        # Cleanup
        os.unlink(test_file)
        
        self.results["scenarios"][scenario] = {
            "status": status,
            "details": details
        }
    
    def test_concurrent_resilience(self):
        """Test resilience under concurrent load with errors"""
        from packages.voidlight_markitdown.src.voidlight_markitdown import VoidLightMarkItDown
        
        print("\n🧪 Testing concurrent operations resilience...")
        scenario = "concurrent_errors"
        
        from concurrent.futures import ThreadPoolExecutor
        import tempfile
        
        def process_file(index):
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(f"Document {index} 한국어 내용 {index}")
                    file_path = f.name
                
                converter = VoidLightMarkItDown(korean_mode=True)
                result = converter.convert(file_path)
                
                # Cleanup
                os.unlink(file_path)
                
                return result is not None and result.markdown
            except Exception:
                return False
        
        # Test with random exceptions
        with self.injector.inject_random_exceptions(exception_rate=0.3):
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(process_file, i) for i in range(20)]
                results = [f.result() for f in futures]
        
        success_rate = sum(results) / len(results)
        
        self.results["scenarios"][scenario] = {
            "status": "resilient" if success_rate >= 0.5 else "failed",
            "success_rate": success_rate,
            "details": f"{sum(results)}/{len(results)} concurrent operations succeeded"
        }
    
    def test_encoding_resilience(self):
        """Test resilience to encoding errors"""
        from packages.voidlight_markitdown.src.voidlight_markitdown import VoidLightMarkItDown
        
        print("\n🧪 Testing encoding error resilience...")
        scenario = "encoding_errors"
        
        import tempfile
        test_cases = [
            ("UTF-8 Korean", "한글 테스트 문서입니다.", 'utf-8'),
            ("CP949 Korean", "윈도우 한글 인코딩", 'cp949'),
            ("EUC-KR Korean", "EUC-KR 한국어", 'euc-kr'),
            ("Mixed content", "English and 한글 mixed", 'utf-8')
        ]
        
        successes = 0
        
        with self.injector.inject_encoding_errors():
            converter = VoidLightMarkItDown(korean_mode=True)
            
            for description, content, encoding in test_cases:
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', 
                                                   delete=False, encoding=encoding) as f:
                        f.write(content)
                        file_path = f.name
                    
                    result = converter.convert(file_path)
                    
                    # Check if Korean preserved
                    if result and any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 
                                    for c in (result.markdown or '')):
                        successes += 1
                        print(f"  ✅ {description}: Korean preserved")
                    else:
                        print(f"  ⚠️ {description}: Korean lost")
                    
                    # Cleanup
                    os.unlink(file_path)
                    
                except Exception as e:
                    print(f"  ❌ {description}: {type(e).__name__}")
        
        success_rate = successes / len(test_cases)
        
        self.results["scenarios"][scenario] = {
            "status": "resilient" if success_rate >= 0.5 else "failed",
            "success_rate": success_rate,
            "details": f"{successes}/{len(test_cases)} encoding scenarios handled"
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate resilience validation report"""
        # Calculate metrics
        for scenario_data in self.results["scenarios"].values():
            self.results["metrics"]["total_scenarios"] += 1
            status = scenario_data["status"]
            if status == "resilient":
                self.results["metrics"]["resilient"] += 1
            elif status == "degraded":
                self.results["metrics"]["degraded"] += 1
            else:
                self.results["metrics"]["failed"] += 1
        
        # Calculate overall resilience score
        total = self.results["metrics"]["total_scenarios"]
        if total > 0:
            resilience_score = (
                self.results["metrics"]["resilient"] * 1.0 +
                self.results["metrics"]["degraded"] * 0.5
            ) / total
        else:
            resilience_score = 0
        
        # Generate recommendations
        recommendations = []
        
        if self.results["scenarios"].get("network_failures", {}).get("status") != "resilient":
            recommendations.append("Implement circuit breaker pattern for network operations")
            recommendations.append("Add configurable retry policies with exponential backoff")
        
        if self.results["scenarios"].get("filesystem_errors", {}).get("success_rate", 0) < 0.5:
            recommendations.append("Add file operation retry logic")
            recommendations.append("Implement temporary file fallback mechanism")
        
        if self.results["scenarios"].get("memory_pressure", {}).get("status") == "failed":
            recommendations.append("Implement streaming for large file processing")
            recommendations.append("Add memory usage monitoring and limits")
        
        if self.results["scenarios"].get("encoding_errors", {}).get("success_rate", 0) < 0.75:
            recommendations.append("Enhance encoding detection with chardet")
            recommendations.append("Add encoding fallback chain for Korean text")
        
        return {
            "summary": {
                "timestamp": self.results["timestamp"],
                "resilience_score": resilience_score,
                "total_scenarios": total,
                "breakdown": {
                    "resilient": self.results["metrics"]["resilient"],
                    "degraded": self.results["metrics"]["degraded"],
                    "failed": self.results["metrics"]["failed"]
                }
            },
            "scenarios": self.results["scenarios"],
            "recommendations": recommendations,
            "production_readiness": resilience_score >= 0.7
        }
    
    def run_all_tests(self):
        """Run all resilience tests"""
        print("🛡️ Starting Production Resilience Validation")
        print("=" * 60)
        
        self.test_network_resilience()
        self.test_filesystem_resilience()
        self.test_memory_resilience()
        self.test_concurrent_resilience()
        self.test_encoding_resilience()
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        os.makedirs("reports", exist_ok=True)
        report_path = f"reports/resilience_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Resilience Validation Summary")
        print("=" * 60)
        print(f"Resilience Score: {report['summary']['resilience_score']:.1%}")
        print(f"Total Scenarios: {report['summary']['total_scenarios']}")
        print(f"  - Resilient: {report['summary']['breakdown']['resilient']}")
        print(f"  - Degraded: {report['summary']['breakdown']['degraded']}")
        print(f"  - Failed: {report['summary']['breakdown']['failed']}")
        print(f"\nProduction Ready: {'✅ YES' if report['production_readiness'] else '❌ NO'}")
        
        if report['recommendations']:
            print("\n🔧 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        return report


if __name__ == "__main__":
    validator = ResilienceValidator()
    validator.run_all_tests()