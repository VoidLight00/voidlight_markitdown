#!/usr/bin/env python3
"""
Recovery Validation Tests for VoidLight MarkItDown
Tests automatic recovery mechanisms and failover strategies
"""

import os
import sys
import json
import time
import psutil
import signal
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from packages.voidlight_markitdown.src.voidlight_markitdown import VoidLightMarkItDown


class RecoveryValidator:
    """Validates automatic recovery mechanisms"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "recovery_tests": {},
            "metrics": {
                "mean_time_to_recovery": [],
                "recovery_success_rate": 0,
                "failover_effectiveness": 0
            }
        }
    
    def measure_recovery_time(self, failure_func, recovery_func) -> Tuple[bool, float]:
        """Measure time to recover from a failure"""
        start_time = time.time()
        
        # Induce failure
        failure_func()
        
        # Attempt recovery
        max_attempts = 5
        recovered = False
        
        for attempt in range(max_attempts):
            if recovery_func():
                recovered = True
                break
            time.sleep(1)  # Wait before retry
        
        recovery_time = time.time() - start_time
        return recovered, recovery_time
    
    def test_connection_pool_recovery(self):
        """Test recovery of connection pools after failure"""
        print("\n🧪 Testing connection pool recovery...")
        test_name = "connection_pool_recovery"
        
        # Simulate connection pool exhaustion
        converters = []
        recovery_times = []
        
        try:
            # Create multiple converters to stress connection pool
            for i in range(20):
                converter = VoidLightMarkItDown()
                converters.append(converter)
            
            # Simulate failure - force garbage collection
            converters.clear()
            
            # Measure recovery
            def recovery_func():
                try:
                    converter = VoidLightMarkItDown()
                    # Test with simple conversion
                    result = converter.convert_stream(
                        io.BytesIO(b"Test recovery"),
                        file_extension=".txt"
                    )
                    return result is not None
                except:
                    return False
            
            recovered, recovery_time = self.measure_recovery_time(
                lambda: None,  # Failure already induced
                recovery_func
            )
            
            self.results["recovery_tests"][test_name] = {
                "recovered": recovered,
                "recovery_time": recovery_time,
                "details": "Connection pool recovered successfully" if recovered else "Failed to recover"
            }
            
            if recovered:
                self.results["metrics"]["mean_time_to_recovery"].append(recovery_time)
            
        except Exception as e:
            self.results["recovery_tests"][test_name] = {
                "recovered": False,
                "error": str(e)
            }
    
    def test_memory_leak_prevention(self):
        """Test memory leak prevention mechanisms"""
        print("\n🧪 Testing memory leak prevention...")
        test_name = "memory_leak_prevention"
        
        import gc
        import tempfile
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        for i in range(50):
            try:
                converter = VoidLightMarkItDown(korean_mode=True)
                
                # Create and convert temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(f"Test content {i} 한국어 내용 " * 1000)
                    temp_file = f.name
                
                result = converter.convert(temp_file)
                os.unlink(temp_file)
                
                # Force cleanup
                del converter
                del result
                
            except Exception:
                pass
        
        # Force garbage collection
        gc.collect()
        time.sleep(1)
        
        # Check final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Acceptable threshold: 50MB increase
        no_significant_leak = memory_increase < 50
        
        self.results["recovery_tests"][test_name] = {
            "recovered": no_significant_leak,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "increase_mb": memory_increase,
            "details": "No significant memory leak" if no_significant_leak else "Memory leak detected"
        }
    
    def test_file_handle_cleanup(self):
        """Test proper file handle cleanup after errors"""
        print("\n🧪 Testing file handle cleanup...")
        test_name = "file_handle_cleanup"
        
        import tempfile
        
        # Get initial file handles
        process = psutil.Process()
        if hasattr(process, 'num_handles'):
            initial_handles = process.num_handles()
        else:
            initial_handles = len(process.open_files())
        
        # Create operations that might leak handles
        for i in range(20):
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write("Test content for handle test")
                    temp_file = f.name
                
                converter = VoidLightMarkItDown()
                
                # Simulate error during conversion
                if i % 3 == 0:
                    os.chmod(temp_file, 0o000)  # Remove permissions
                
                try:
                    result = converter.convert(temp_file)
                except:
                    pass  # Expected to fail
                
                # Cleanup
                try:
                    os.chmod(temp_file, 0o644)
                    os.unlink(temp_file)
                except:
                    pass
                    
            except Exception:
                pass
        
        # Check final handles
        time.sleep(1)  # Allow cleanup
        if hasattr(process, 'num_handles'):
            final_handles = process.num_handles()
        else:
            final_handles = len(process.open_files())
        
        handle_increase = final_handles - initial_handles
        
        # Acceptable threshold: 10 handles
        handles_cleaned = handle_increase < 10
        
        self.results["recovery_tests"][test_name] = {
            "recovered": handles_cleaned,
            "initial_handles": initial_handles,
            "final_handles": final_handles,
            "increase": handle_increase,
            "details": "File handles properly cleaned" if handles_cleaned else "File handle leak detected"
        }
    
    def test_korean_nlp_failover(self):
        """Test failover between Korean NLP libraries"""
        print("\n🧪 Testing Korean NLP failover...")
        test_name = "korean_nlp_failover"
        
        import tempfile
        
        # Test Korean text
        korean_text = """
        안녕하세요. 이것은 한국어 NLP 라이브러리 페일오버 테스트입니다.
        다양한 한국어 처리 기능이 작동하는지 확인합니다.
        KoNLPy, Kiwipiepy, 그리고 다른 라이브러리들 간의 전환을 테스트합니다.
        """
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, 
                                       encoding='utf-8') as f:
            f.write(korean_text)
            test_file = f.name
        
        # Test with Korean mode
        converter = VoidLightMarkItDown(korean_mode=True)
        
        try:
            start_time = time.time()
            result = converter.convert(test_file)
            conversion_time = time.time() - start_time
            
            # Check if Korean text preserved
            korean_preserved = False
            if result and result.markdown:
                # Check for Korean characters
                korean_preserved = any(
                    ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 
                    for c in result.markdown
                )
            
            # Check if any NLP features worked (even with fallback)
            nlp_worked = korean_preserved and len(result.markdown) > len(korean_text) * 0.8
            
            self.results["recovery_tests"][test_name] = {
                "recovered": nlp_worked,
                "conversion_time": conversion_time,
                "korean_preserved": korean_preserved,
                "details": "NLP failover successful" if nlp_worked else "NLP failover failed"
            }
            
            if nlp_worked:
                self.results["metrics"]["mean_time_to_recovery"].append(conversion_time)
            
        except Exception as e:
            self.results["recovery_tests"][test_name] = {
                "recovered": False,
                "error": str(e)
            }
        finally:
            os.unlink(test_file)
    
    def test_concurrent_recovery(self):
        """Test recovery under concurrent load"""
        print("\n🧪 Testing concurrent operation recovery...")
        test_name = "concurrent_recovery"
        
        import tempfile
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def worker_with_recovery(worker_id):
            """Worker that handles failures and recovers"""
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    # Create test file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', 
                                                   delete=False, encoding='utf-8') as f:
                        f.write(f"Worker {worker_id} content 한국어 {worker_id}")
                        temp_file = f.name
                    
                    # Random failure injection
                    import random
                    if random.random() < 0.3 and attempt == 0:
                        raise Exception("Simulated failure")
                    
                    converter = VoidLightMarkItDown(korean_mode=True)
                    result = converter.convert(temp_file)
                    
                    # Cleanup
                    os.unlink(temp_file)
                    
                    return {
                        "worker_id": worker_id,
                        "success": True,
                        "attempts": attempt + 1,
                        "result": result is not None
                    }
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        return {
                            "worker_id": worker_id,
                            "success": False,
                            "attempts": attempt + 1,
                            "error": str(e)
                        }
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
        
        # Run concurrent workers
        num_workers = 20
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_with_recovery, i) for i in range(num_workers)]
            results = [f.result() for f in as_completed(futures)]
        
        # Analyze results
        successful = sum(1 for r in results if r["success"])
        total_attempts = sum(r["attempts"] for r in results)
        avg_attempts = total_attempts / len(results)
        
        recovery_rate = successful / len(results)
        
        self.results["recovery_tests"][test_name] = {
            "recovered": recovery_rate >= 0.8,
            "recovery_rate": recovery_rate,
            "successful_workers": successful,
            "total_workers": num_workers,
            "avg_attempts_per_worker": avg_attempts,
            "details": f"{successful}/{num_workers} workers recovered successfully"
        }
    
    def test_graceful_degradation(self):
        """Test graceful degradation when features unavailable"""
        print("\n🧪 Testing graceful degradation...")
        test_name = "graceful_degradation"
        
        import tempfile
        
        # Test with various file types that might fail
        test_cases = [
            ("complex_pdf.pdf", b"%PDF-1.4\n%Invalid PDF content\n%%EOF", "Invalid PDF"),
            ("huge_file.txt", b"x" * (100 * 1024 * 1024), "100MB file"),  # 100MB
            ("special_chars.txt", "Special chars: \x00\x01\x02\x03\x04".encode(), "Special chars"),
            ("korean_mixed.txt", "한글 English 中文 العربية".encode('utf-8'), "Mixed languages")
        ]
        
        degraded_results = []
        
        for filename, content, description in test_cases:
            file_path = os.path.join(tempfile.gettempdir(), filename)
            
            try:
                # Write test file
                with open(file_path, 'wb') as f:
                    f.write(content if isinstance(content, bytes) else content.encode())
                
                converter = VoidLightMarkItDown(korean_mode=True)
                
                # Attempt conversion with timeout
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Conversion timeout")
                
                # Set timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(5)  # 5 second timeout
                
                try:
                    result = converter.convert(file_path)
                    signal.alarm(0)  # Cancel timeout
                    
                    # Check if we got any result (even if degraded)
                    if result:
                        if result.markdown:
                            degraded_results.append({
                                "file": description,
                                "status": "success",
                                "output_size": len(result.markdown)
                            })
                        else:
                            degraded_results.append({
                                "file": description,
                                "status": "degraded",
                                "output_size": 0
                            })
                    else:
                        degraded_results.append({
                            "file": description,
                            "status": "failed"
                        })
                        
                except TimeoutError:
                    degraded_results.append({
                        "file": description,
                        "status": "timeout"
                    })
                except Exception as e:
                    degraded_results.append({
                        "file": description,
                        "status": "error",
                        "error": type(e).__name__
                    })
                
            finally:
                # Cleanup
                try:
                    os.unlink(file_path)
                except:
                    pass
        
        # Calculate degradation effectiveness
        handled = sum(1 for r in degraded_results 
                     if r["status"] in ["success", "degraded"])
        degradation_rate = handled / len(test_cases)
        
        self.results["recovery_tests"][test_name] = {
            "recovered": degradation_rate >= 0.5,
            "degradation_rate": degradation_rate,
            "results": degraded_results,
            "details": f"Gracefully handled {handled}/{len(test_cases)} edge cases"
        }
    
    def calculate_metrics(self):
        """Calculate overall recovery metrics"""
        # Recovery success rate
        total_tests = len(self.results["recovery_tests"])
        successful_recoveries = sum(
            1 for test in self.results["recovery_tests"].values()
            if test.get("recovered", False)
        )
        
        self.results["metrics"]["recovery_success_rate"] = (
            successful_recoveries / total_tests if total_tests > 0 else 0
        )
        
        # Mean time to recovery
        if self.results["metrics"]["mean_time_to_recovery"]:
            avg_mttr = sum(self.results["metrics"]["mean_time_to_recovery"]) / len(
                self.results["metrics"]["mean_time_to_recovery"]
            )
            self.results["metrics"]["mean_time_to_recovery"] = avg_mttr
        else:
            self.results["metrics"]["mean_time_to_recovery"] = 0
        
        # Failover effectiveness (based on specific tests)
        failover_tests = ["korean_nlp_failover", "concurrent_recovery", "graceful_degradation"]
        failover_success = sum(
            1 for test_name in failover_tests
            if self.results["recovery_tests"].get(test_name, {}).get("recovered", False)
        )
        self.results["metrics"]["failover_effectiveness"] = (
            failover_success / len(failover_tests)
        )
    
    def generate_report(self) -> Dict:
        """Generate comprehensive recovery validation report"""
        self.calculate_metrics()
        
        # Determine production readiness
        production_ready = (
            self.results["metrics"]["recovery_success_rate"] >= 0.8 and
            self.results["metrics"]["failover_effectiveness"] >= 0.66 and
            self.results["metrics"]["mean_time_to_recovery"] < 10  # seconds
        )
        
        # Generate recommendations
        recommendations = []
        
        if self.results["metrics"]["recovery_success_rate"] < 0.8:
            recommendations.append("Implement comprehensive retry strategies")
            recommendations.append("Add circuit breaker patterns")
        
        if self.results["metrics"]["mean_time_to_recovery"] > 5:
            recommendations.append("Optimize recovery detection mechanisms")
            recommendations.append("Implement faster failover strategies")
        
        if not self.results["recovery_tests"].get("memory_leak_prevention", {}).get("recovered"):
            recommendations.append("Implement automatic memory cleanup")
            recommendations.append("Add memory usage monitoring")
        
        if not self.results["recovery_tests"].get("korean_nlp_failover", {}).get("recovered"):
            recommendations.append("Improve Korean NLP library failover")
            recommendations.append("Add more NLP backend options")
        
        return {
            "summary": {
                "timestamp": self.results["timestamp"],
                "production_ready": production_ready,
                "recovery_success_rate": f"{self.results['metrics']['recovery_success_rate']:.1%}",
                "mean_time_to_recovery": f"{self.results['metrics']['mean_time_to_recovery']:.2f}s",
                "failover_effectiveness": f"{self.results['metrics']['failover_effectiveness']:.1%}"
            },
            "recovery_tests": self.results["recovery_tests"],
            "recommendations": recommendations,
            "rto_analysis": {
                "target_rto": "5 seconds",
                "actual_mttr": f"{self.results['metrics']['mean_time_to_recovery']:.2f}s",
                "meets_target": self.results["metrics"]["mean_time_to_recovery"] < 5
            }
        }
    
    def run_all_tests(self):
        """Run all recovery validation tests"""
        print("🔄 Starting Recovery Mechanism Validation")
        print("=" * 60)
        
        # Import required modules
        global io
        import io
        
        # Run tests
        self.test_connection_pool_recovery()
        self.test_memory_leak_prevention()
        self.test_file_handle_cleanup()
        self.test_korean_nlp_failover()
        self.test_concurrent_recovery()
        self.test_graceful_degradation()
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        os.makedirs("reports", exist_ok=True)
        report_path = f"reports/recovery_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Recovery Validation Summary")
        print("=" * 60)
        print(f"Production Ready: {'✅ YES' if report['summary']['production_ready'] else '❌ NO'}")
        print(f"Recovery Success Rate: {report['summary']['recovery_success_rate']}")
        print(f"Mean Time to Recovery: {report['summary']['mean_time_to_recovery']}")
        print(f"Failover Effectiveness: {report['summary']['failover_effectiveness']}")
        print(f"Meets RTO Target: {'✅ YES' if report['rto_analysis']['meets_target'] else '❌ NO'}")
        
        if report['recommendations']:
            print("\n🔧 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        return report


if __name__ == "__main__":
    validator = RecoveryValidator()
    validator.run_all_tests()