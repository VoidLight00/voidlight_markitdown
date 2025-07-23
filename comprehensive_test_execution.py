#!/usr/bin/env python3
"""
Comprehensive Test Execution Framework for voidlight_markitdown
Executes all tests systematically and generates detailed reports.
"""

import subprocess
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime
import psutil
import traceback

class TestExecutor:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        self.test_categories = {
            'unit_tests': [],
            'integration_tests': [],
            'converter_tests': [],
            'korean_nlp_tests': [],
            'mcp_tests': [],
            'cli_tests': []
        }
        
    def categorize_tests(self):
        """Categorize all test files by type"""
        test_files = {
            'unit_tests': [
                'packages/voidlight_markitdown/tests/test_voidlight_markitdown.py',
                'packages/voidlight_markitdown/tests/test_module_misc.py',
                'packages/voidlight_markitdown/tests/test_module_vectors.py',
            ],
            'integration_tests': [
                'test_integration.py',
                'test_quick_integration.py',
                'run_integration_tests.py',
                'run_integration_tests_automated.py',
            ],
            'converter_tests': [
                'test_converters.py',
                'test_more_converters.py',
                'test_remaining_converters.py',
                'test_remaining_converters_final.py',
                'packages/voidlight_markitdown/test_all_converters.py',
            ],
            'korean_nlp_tests': [
                'test_korean_nlp.py',
                'test_korean_features.py',
                'test_korean_features_final.py',
                'packages/voidlight_markitdown/test_korean_nlp_simple.py',
                'packages/voidlight_markitdown/tests/test_korean_nlp_features.py',
                'packages/voidlight_markitdown/tests/test_korean_utils.py',
            ],
            'mcp_tests': [
                'test_mcp_server.py',
                'test_mcp_client_simple.py',
                'test_mcp_discover.py',
                'test_mcp_edge_cases.py',
                'test_mcp_http_direct.py',
                'test_mcp_integration_comprehensive.py',
                'test_mcp_integration_enhanced.py',
                'test_mcp_protocol.py',
                'test_mcp_protocol_capture.py',
                'test_mcp_raw_protocol.py',
                'test_mcp_simple.py',
                'test_mcp_sse_fixed.py',
            ],
            'cli_tests': [
                'packages/voidlight_markitdown/tests/test_cli_misc.py',
                'packages/voidlight_markitdown/tests/test_cli_vectors.py',
            ],
            'misc_tests': [
                'test_architecture_alignment.py',
                'test_library_usage.py',
                'test_logging_system.py',
                'packages/voidlight_markitdown/test_install.py',
            ]
        }
        
        # Verify which files exist
        for category, files in test_files.items():
            for file in files:
                if Path(file).exists():
                    self.test_categories[category].append(file)
                    
    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
        
    def run_single_test(self, test_file, category):
        """Run a single test file and capture results"""
        print(f"\n{'='*80}")
        print(f"Running: {test_file} (Category: {category})")
        print(f"{'='*80}")
        
        result = {
            'file': test_file,
            'category': category,
            'start_time': datetime.now().isoformat(),
            'memory_before': self.get_memory_usage()
        }
        
        try:
            # Activate virtual environment and run test
            cmd = [
                sys.executable,
                '-m', 'pytest',
                test_file,
                '-v',
                '--tb=short',
                '--no-header',
                '-q'
            ]
            
            start = time.time()
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test
            )
            duration = time.time() - start
            
            result.update({
                'status': 'passed' if proc.returncode == 0 else 'failed',
                'duration': duration,
                'returncode': proc.returncode,
                'stdout': proc.stdout,
                'stderr': proc.stderr,
                'memory_after': self.get_memory_usage(),
                'memory_delta': self.get_memory_usage() - result['memory_before']
            })
            
            # Parse pytest output for more details
            if 'passed' in proc.stdout:
                passed = int(proc.stdout.split('passed')[0].strip().split()[-1])
                result['passed_count'] = passed
            if 'failed' in proc.stdout:
                failed = int(proc.stdout.split('failed')[0].strip().split()[-1])
                result['failed_count'] = failed
            if 'skipped' in proc.stdout:
                skipped = int(proc.stdout.split('skipped')[0].strip().split()[-1])
                result['skipped_count'] = skipped
                
        except subprocess.TimeoutExpired:
            result.update({
                'status': 'timeout',
                'error': 'Test execution timed out after 5 minutes'
            })
        except Exception as e:
            result.update({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            
        self.results.append(result)
        return result
        
    def run_test_batch(self, category):
        """Run all tests in a category"""
        tests = self.test_categories.get(category, [])
        if not tests:
            print(f"\nNo tests found for category: {category}")
            return
            
        print(f"\n{'#'*80}")
        print(f"# Running {category.upper()} ({len(tests)} test files)")
        print(f"{'#'*80}")
        
        category_results = []
        for test_file in tests:
            result = self.run_single_test(test_file, category)
            category_results.append(result)
            
            # Quick summary after each test
            if result['status'] == 'passed':
                print(f"✅ PASSED: {test_file}")
            elif result['status'] == 'failed':
                print(f"❌ FAILED: {test_file}")
            elif result['status'] == 'timeout':
                print(f"⏱️  TIMEOUT: {test_file}")
            else:
                print(f"⚠️  ERROR: {test_file}")
                
        return category_results
        
    def generate_report(self):
        """Generate comprehensive test report"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'execution_date': self.start_time.isoformat(),
            'total_duration': total_duration,
            'python_version': sys.version,
            'platform': sys.platform,
            'results': self.results,
            'summary': {
                'total_files': len(self.results),
                'passed': len([r for r in self.results if r['status'] == 'passed']),
                'failed': len([r for r in self.results if r['status'] == 'failed']),
                'timeout': len([r for r in self.results if r['status'] == 'timeout']),
                'error': len([r for r in self.results if r['status'] == 'error']),
            }
        }
        
        # Category summaries
        category_summary = {}
        for category in self.test_categories:
            category_results = [r for r in self.results if r['category'] == category]
            if category_results:
                category_summary[category] = {
                    'total': len(category_results),
                    'passed': len([r for r in category_results if r['status'] == 'passed']),
                    'failed': len([r for r in category_results if r['status'] == 'failed']),
                }
                
        report['category_summary'] = category_summary
        
        # Save detailed report
        with open('comprehensive_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate human-readable summary
        self.print_summary(report)
        
    def print_summary(self, report):
        """Print human-readable test summary"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Execution Date: {report['execution_date']}")
        print(f"Total Duration: {report['total_duration']:.2f} seconds")
        print(f"Python Version: {sys.version.split()[0]}")
        print(f"\nOVERALL RESULTS:")
        print(f"  Total Test Files: {report['summary']['total_files']}")
        print(f"  ✅ Passed: {report['summary']['passed']}")
        print(f"  ❌ Failed: {report['summary']['failed']}")
        print(f"  ⏱️  Timeout: {report['summary']['timeout']}")
        print(f"  ⚠️  Error: {report['summary']['error']}")
        
        print(f"\nCATEGORY BREAKDOWN:")
        for category, stats in report['category_summary'].items():
            print(f"\n{category.upper()}:")
            print(f"  Total: {stats['total']}")
            print(f"  Passed: {stats['passed']}")
            print(f"  Failed: {stats['failed']}")
            
        # Print failed tests details
        failed_tests = [r for r in self.results if r['status'] == 'failed']
        if failed_tests:
            print(f"\n{'='*80}")
            print("FAILED TESTS DETAILS:")
            print(f"{'='*80}")
            for test in failed_tests:
                print(f"\n❌ {test['file']}:")
                if 'stderr' in test and test['stderr']:
                    print(f"Error Output:\n{test['stderr'][:500]}...")
                    
    def execute_all_tests(self):
        """Main execution method"""
        print("Starting Comprehensive Test Execution...")
        print(f"Working Directory: {os.getcwd()}")
        
        # Categorize tests
        self.categorize_tests()
        
        # Run tests by category in order of importance
        test_order = [
            'unit_tests',
            'integration_tests', 
            'converter_tests',
            'korean_nlp_tests',
            'cli_tests',
            'mcp_tests',
            'misc_tests'
        ]
        
        for category in test_order:
            self.run_test_batch(category)
            
        # Generate final report
        self.generate_report()
        
        return self.results

if __name__ == '__main__':
    executor = TestExecutor()
    executor.execute_all_tests()