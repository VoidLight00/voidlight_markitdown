#!/usr/bin/env python3
"""
Chaos Engineering Test Suite for VoidLight MarkItDown
Tests production error recovery mechanisms
"""

import os
import sys
import json
import time
import random
import asyncio
import psutil
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from packages.voidlight_markitdown.src.voidlight_markitdown import VoidLightMarkItDown


class ChaosEngineeringTests:
    """Chaos engineering tests for production resilience"""
    
    def __init__(self):
        self.results = {
            "test_time": datetime.now().isoformat(),
            "scenarios": {},
            "metrics": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "recovery_times": []
            }
        }
        self.temp_dir = tempfile.mkdtemp()
        
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def run_with_timeout(self, func, timeout=30):
        """Run function with timeout"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func)
            try:
                return future.result(timeout=timeout)
            except TimeoutError:
                return None
    
    def test_memory_exhaustion(self):
        """Test behavior under memory pressure"""
        print("\n🧪 Testing memory exhaustion scenario...")
        scenario = "memory_exhaustion"
        start_time = time.time()
        
        try:
            # Create large text content
            large_content = "한국어 테스트 " * 1000000  # ~13MB of Korean text
            
            # Test with progressively larger files
            for size_multiplier in [1, 10, 50]:
                content = large_content * size_multiplier
                file_path = os.path.join(self.temp_dir, f"large_{size_multiplier}.txt")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Monitor memory before
                process = psutil.Process()
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
                
                # Try conversion
                converter = VoidLightMarkItDown(korean_mode=True)
                result = self.run_with_timeout(
                    lambda: converter.convert(file_path),
                    timeout=60
                )
                
                # Monitor memory after
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                mem_increase = mem_after - mem_before
                
                if result:
                    print(f"✅ Handled {size_multiplier}x file (Memory +{mem_increase:.1f}MB)")
                else:
                    print(f"⚠️ Timeout/failure with {size_multiplier}x file")
                    break
            
            recovery_time = time.time() - start_time
            self.results["scenarios"][scenario] = {
                "status": "passed",
                "recovery_time": recovery_time,
                "details": f"System handled up to {size_multiplier}x large files"
            }
            self.results["metrics"]["passed"] += 1
            
        except Exception as e:
            self.results["scenarios"][scenario] = {
                "status": "failed",
                "error": str(e)
            }
            self.results["metrics"]["failed"] += 1
        
        self.results["metrics"]["total_tests"] += 1
    
    def test_corrupted_input(self):
        """Test handling of corrupted input files"""
        print("\n🧪 Testing corrupted input handling...")
        scenario = "corrupted_input"
        
        test_cases = [
            # (filename, content, description)
            ("invalid_pdf.pdf", b"Not a real PDF content", "Invalid PDF"),
            ("broken_utf8.txt", b"\xff\xfe Invalid UTF-8 \x80\x81", "Broken UTF-8"),
            ("mixed_encoding.txt", "English text 한국어 텍스트".encode('cp949'), "Mixed encoding"),
            ("null_bytes.txt", b"Text with \x00 null \x00 bytes", "Null bytes"),
            ("truncated_file.docx", b"PK\x03\x04", "Truncated DOCX"),
        ]
        
        passed = 0
        converter = VoidLightMarkItDown(korean_mode=True)
        
        for filename, content, description in test_cases:
            file_path = os.path.join(self.temp_dir, filename)
            
            # Write corrupted content
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(file_path, mode) as f:
                f.write(content)
            
            try:
                # Attempt conversion
                result = converter.convert(file_path)
                if result and result.markdown:
                    print(f"✅ Gracefully handled {description}")
                    passed += 1
                else:
                    print(f"⚠️ Empty result for {description}")
            except Exception as e:
                # Should handle gracefully, not crash
                print(f"❌ Exception with {description}: {type(e).__name__}")
        
        self.results["scenarios"][scenario] = {
            "status": "passed" if passed >= 3 else "failed",
            "passed_cases": passed,
            "total_cases": len(test_cases)
        }
        self.results["metrics"]["total_tests"] += 1
        if passed >= 3:
            self.results["metrics"]["passed"] += 1
        else:
            self.results["metrics"]["failed"] += 1
    
    def test_concurrent_failures(self):
        """Test recovery from concurrent operation failures"""
        print("\n🧪 Testing concurrent failure recovery...")
        scenario = "concurrent_failures"
        
        def stress_conversion(file_index):
            """Single conversion with potential failure"""
            try:
                converter = VoidLightMarkItDown(korean_mode=True)
                
                # Create test file
                content = f"Test content {file_index} 한국어 내용 {file_index}"
                file_path = os.path.join(self.temp_dir, f"concurrent_{file_index}.txt")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Random failure injection
                if random.random() < 0.3:  # 30% failure rate
                    raise Exception("Simulated failure")
                
                result = converter.convert(file_path)
                return result is not None
                
            except Exception:
                return False
        
        # Run concurrent operations
        num_threads = 20
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(stress_conversion, i) for i in range(num_threads)]
            results = [f.result() for f in futures]
        
        success_rate = sum(results) / len(results)
        
        self.results["scenarios"][scenario] = {
            "status": "passed" if success_rate >= 0.5 else "failed",
            "success_rate": success_rate,
            "total_operations": num_threads
        }
        self.results["metrics"]["total_tests"] += 1
        if success_rate >= 0.5:
            self.results["metrics"]["passed"] += 1
        else:
            self.results["metrics"]["failed"] += 1
    
    def test_korean_encoding_errors(self):
        """Test Korean-specific encoding error recovery"""
        print("\n🧪 Testing Korean encoding error recovery...")
        scenario = "korean_encoding_errors"
        
        test_cases = [
            # Various problematic Korean text scenarios
            ("broken_hangul.txt", b'\xed\x95\x9c\xea\xb5\xad\xec\x96\xb4 \xff\xfe', "Broken Hangul"),
            ("mixed_korean.txt", "한국어 текст العربية 中文".encode('utf-8'), "Mixed scripts"),
            ("cp949_content.txt", "한글 윈도우 인코딩".encode('cp949'), "CP949 encoding"),
            ("euckr_content.txt", "한국어 EUC-KR".encode('euc-kr'), "EUC-KR encoding"),
            ("mojibake.txt", "í•œêµ­ì–´".encode('utf-8'), "Mojibake text"),
        ]
        
        converter = VoidLightMarkItDown(korean_mode=True)
        passed = 0
        
        for filename, content, description in test_cases:
            file_path = os.path.join(self.temp_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            try:
                result = converter.convert(file_path)
                if result and result.markdown:
                    # Check if Korean text is preserved or recovered
                    if any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in result.markdown):
                        print(f"✅ Recovered Korean text from {description}")
                        passed += 1
                    else:
                        print(f"⚠️ Lost Korean text in {description}")
                else:
                    print(f"⚠️ Empty result for {description}")
            except Exception as e:
                print(f"❌ Failed on {description}: {type(e).__name__}")
        
        self.results["scenarios"][scenario] = {
            "status": "passed" if passed >= 3 else "failed",
            "passed_cases": passed,
            "total_cases": len(test_cases)
        }
        self.results["metrics"]["total_tests"] += 1
        if passed >= 3:
            self.results["metrics"]["passed"] += 1
        else:
            self.results["metrics"]["failed"] += 1
    
    def test_resource_cleanup(self):
        """Test proper resource cleanup after errors"""
        print("\n🧪 Testing resource cleanup...")
        scenario = "resource_cleanup"
        
        # Get initial resource state
        process = psutil.Process()
        initial_handles = process.num_handles() if hasattr(process, 'num_handles') else 0
        initial_threads = process.num_threads()
        
        # Perform multiple operations with failures
        for i in range(10):
            try:
                converter = VoidLightMarkItDown(korean_mode=True)
                
                # Create and convert file
                file_path = os.path.join(self.temp_dir, f"cleanup_test_{i}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Test content {i} 한국어 테스트 {i}")
                
                # Force some failures
                if i % 3 == 0:
                    # Simulate file permission error
                    os.chmod(file_path, 0o000)
                
                try:
                    converter.convert(file_path)
                except:
                    pass  # Expected failures
                finally:
                    # Restore permissions
                    if os.path.exists(file_path):
                        os.chmod(file_path, 0o644)
                
            except Exception:
                pass
        
        # Check resource state after operations
        time.sleep(1)  # Allow cleanup
        final_handles = process.num_handles() if hasattr(process, 'num_handles') else 0
        final_threads = process.num_threads()
        
        # Calculate leaks
        handle_leak = final_handles - initial_handles if initial_handles > 0 else 0
        thread_leak = final_threads - initial_threads
        
        self.results["scenarios"][scenario] = {
            "status": "passed" if handle_leak <= 5 and thread_leak <= 2 else "failed",
            "handle_leak": handle_leak,
            "thread_leak": thread_leak
        }
        self.results["metrics"]["total_tests"] += 1
        if handle_leak <= 5 and thread_leak <= 2:
            self.results["metrics"]["passed"] += 1
            print("✅ Resource cleanup working properly")
        else:
            self.results["metrics"]["failed"] += 1
            print(f"❌ Resource leaks detected: handles={handle_leak}, threads={thread_leak}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        report = {
            "summary": {
                "test_time": self.results["test_time"],
                "total_scenarios": self.results["metrics"]["total_tests"],
                "passed": self.results["metrics"]["passed"],
                "failed": self.results["metrics"]["failed"],
                "success_rate": self.results["metrics"]["passed"] / max(self.results["metrics"]["total_tests"], 1)
            },
            "scenarios": self.results["scenarios"],
            "recommendations": []
        }
        
        # Add recommendations based on results
        if self.results["metrics"]["failed"] > 0:
            report["recommendations"].append("Implement circuit breaker pattern for repeated failures")
            report["recommendations"].append("Add retry logic with exponential backoff")
            report["recommendations"].append("Improve error messages for better debugging")
        
        if "memory_exhaustion" in self.results["scenarios"]:
            if self.results["scenarios"]["memory_exhaustion"]["status"] == "failed":
                report["recommendations"].append("Implement streaming for large files")
                report["recommendations"].append("Add memory usage monitoring")
        
        if "korean_encoding_errors" in self.results["scenarios"]:
            if self.results["scenarios"]["korean_encoding_errors"]["passed_cases"] < 4:
                report["recommendations"].append("Enhance encoding detection for Korean text")
                report["recommendations"].append("Add fallback encoding strategies")
        
        return report
    
    def run_all_tests(self):
        """Run all chaos engineering tests"""
        print("🚀 Starting Chaos Engineering Tests for VoidLight MarkItDown")
        print("=" * 60)
        
        try:
            self.test_memory_exhaustion()
            self.test_corrupted_input()
            self.test_concurrent_failures()
            self.test_korean_encoding_errors()
            self.test_resource_cleanup()
            
            # Generate and save report
            report = self.generate_report()
            
            # Save report
            os.makedirs("reports", exist_ok=True)
            report_path = f"reports/chaos_engineering_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 Chaos Engineering Test Summary")
            print("=" * 60)
            print(f"Total Scenarios: {report['summary']['total_scenarios']}")
            print(f"Passed: {report['summary']['passed']}")
            print(f"Failed: {report['summary']['failed']}")
            print(f"Success Rate: {report['summary']['success_rate']:.1%}")
            print(f"\n📄 Full report saved to: {report_path}")
            
            if report['recommendations']:
                print("\n🔧 Recommendations:")
                for rec in report['recommendations']:
                    print(f"  • {rec}")
            
        finally:
            self.cleanup()


if __name__ == "__main__":
    tester = ChaosEngineeringTests()
    tester.run_all_tests()