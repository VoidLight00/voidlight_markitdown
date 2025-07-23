#!/usr/bin/env python3
"""
Comprehensive Test Execution Script for voidlight_markitdown
Executes all test files and generates detailed reports
"""

import subprocess
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Define all test files by category
TEST_CATEGORIES = {
    'unit_tests': [
        'packages/voidlight_markitdown/tests/test_voidlight_markitdown.py',
        'packages/voidlight_markitdown/tests/test_module_misc.py', 
        'packages/voidlight_markitdown/tests/test_module_vectors.py',
        'packages/voidlight_markitdown/tests/_test_vectors.py',
    ],
    'cli_tests': [
        'packages/voidlight_markitdown/tests/test_cli_misc.py',
        'packages/voidlight_markitdown/tests/test_cli_vectors.py',
    ],
    'korean_nlp_tests': [
        'packages/voidlight_markitdown/tests/test_korean_nlp_features.py',
        'packages/voidlight_markitdown/tests/test_korean_utils.py',
        'packages/voidlight_markitdown/test_korean_nlp_simple.py',
        'test_korean_nlp.py',
        'test_korean_features.py',
        'test_korean_features_final.py',
    ],
    'converter_tests': [
        'packages/voidlight_markitdown/test_all_converters.py',
        'test_converters.py',
        'test_more_converters.py',
        'test_remaining_converters.py',
        'test_remaining_converters_final.py',
    ],
    'integration_tests': [
        'test_integration.py',
        'test_quick_integration.py',
        'run_integration_tests.py',
        'run_integration_tests_automated.py',
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
    'misc_tests': [
        'test_architecture_alignment.py',
        'test_library_usage.py',
        'test_logging_system.py',
        'packages/voidlight_markitdown/test_install.py',
        'packages/voidlight_markitdown/test_summary.py',
    ]
}

def run_pytest_file(test_file):
    """Run a pytest file and return results"""
    print(f"\n{'='*70}")
    print(f"Running: {test_file}")
    print(f"{'='*70}")
    
    result = {
        'file': test_file,
        'start_time': datetime.now().isoformat(),
    }
    
    try:
        cmd = [
            sys.executable, '-m', 'pytest',
            test_file,
            '-v', '--tb=short',
            '--json-report', '--json-report-file=test_report.json'
        ]
        
        start = time.time()
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        duration = time.time() - start
        
        result['duration'] = duration
        result['returncode'] = proc.returncode
        result['stdout'] = proc.stdout
        result['stderr'] = proc.stderr
        
        # Try to parse pytest json report
        try:
            with open('test_report.json', 'r') as f:
                pytest_report = json.load(f)
                result['summary'] = pytest_report.get('summary', {})
                result['tests'] = len(pytest_report.get('tests', []))
            os.remove('test_report.json')
        except:
            # Fallback to parsing stdout
            if 'passed' in proc.stdout or 'failed' in proc.stdout:
                summary = {'passed': 0, 'failed': 0, 'skipped': 0}
                if 'passed' in proc.stdout:
                    try:
                        summary['passed'] = int(proc.stdout.split('passed')[0].strip().split()[-1])
                    except: pass
                if 'failed' in proc.stdout:
                    try:
                        summary['failed'] = int(proc.stdout.split('failed')[0].strip().split()[-1])
                    except: pass
                if 'skipped' in proc.stdout:
                    try:
                        summary['skipped'] = int(proc.stdout.split('skipped')[0].strip().split()[-1])
                    except: pass
                result['summary'] = summary
        
        result['status'] = 'passed' if proc.returncode == 0 else 'failed'
        
    except subprocess.TimeoutExpired:
        result['status'] = 'timeout'
        result['error'] = 'Test timed out after 120 seconds'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        
    return result

def run_python_script(test_file):
    """Run a regular Python script test file"""
    print(f"\n{'='*70}")
    print(f"Running Python script: {test_file}")
    print(f"{'='*70}")
    
    result = {
        'file': test_file,
        'start_time': datetime.now().isoformat(),
    }
    
    try:
        cmd = [sys.executable, test_file]
        
        start = time.time()
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        duration = time.time() - start
        
        result['duration'] = duration
        result['returncode'] = proc.returncode
        result['stdout'] = proc.stdout
        result['stderr'] = proc.stderr
        result['status'] = 'passed' if proc.returncode == 0 else 'failed'
        
        # Try to parse output for pass/fail counts
        summary = {'passed': 0, 'failed': 0, 'skipped': 0}
        if '✓' in proc.stdout:
            summary['passed'] = proc.stdout.count('✓')
        if '✗' in proc.stdout or 'FAILED' in proc.stdout:
            summary['failed'] = proc.stdout.count('✗') + proc.stdout.count('FAILED')
        result['summary'] = summary
        
    except subprocess.TimeoutExpired:
        result['status'] = 'timeout'
        result['error'] = 'Script timed out after 120 seconds'
    except Exception as e:
        result['status'] = 'error' 
        result['error'] = str(e)
        
    return result

def is_pytest_file(file_path):
    """Check if file uses pytest"""
    if not Path(file_path).exists():
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
        return 'import pytest' in content or 'from pytest' in content or 'def test_' in content

def main():
    print(f"Starting comprehensive test execution at {datetime.now()}")
    print(f"Working directory: {os.getcwd()}")
    
    # Activate virtual environment
    activate_cmd = 'source mcp-env/bin/activate'
    
    all_results = []
    category_summaries = {}
    
    for category, test_files in TEST_CATEGORIES.items():
        print(f"\n{'#'*70}")
        print(f"# Category: {category.upper()}")
        print(f"{'#'*70}")
        
        category_results = []
        
        for test_file in test_files:
            if not Path(test_file).exists():
                print(f"⚠️  Test file not found: {test_file}")
                continue
                
            # Determine test type and run
            if is_pytest_file(test_file):
                result = run_pytest_file(test_file)
            else:
                result = run_python_script(test_file)
                
            result['category'] = category
            category_results.append(result)
            all_results.append(result)
            
            # Print quick summary
            if result['status'] == 'passed':
                print(f"✅ PASSED: {test_file}")
            elif result['status'] == 'failed':
                print(f"❌ FAILED: {test_file}")
            elif result['status'] == 'timeout':
                print(f"⏱️  TIMEOUT: {test_file}")
            else:
                print(f"⚠️  ERROR: {test_file}")
                
        # Category summary
        category_summaries[category] = {
            'total': len(category_results),
            'passed': len([r for r in category_results if r['status'] == 'passed']),
            'failed': len([r for r in category_results if r['status'] == 'failed']),
            'timeout': len([r for r in category_results if r['status'] == 'timeout']),
            'error': len([r for r in category_results if r['status'] == 'error']),
        }
    
    # Generate final report
    report = {
        'execution_date': datetime.now().isoformat(),
        'python_version': sys.version,
        'total_files': len(all_results),
        'category_summaries': category_summaries,
        'results': all_results,
        'overall_summary': {
            'total': len(all_results),
            'passed': len([r for r in all_results if r['status'] == 'passed']),
            'failed': len([r for r in all_results if r['status'] == 'failed']),
            'timeout': len([r for r in all_results if r['status'] == 'timeout']),
            'error': len([r for r in all_results if r['status'] == 'error']),
        }
    }
    
    # Save detailed report
    with open('comprehensive_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    # Print summary
    print(f"\n{'='*70}")
    print("COMPREHENSIVE TEST EXECUTION SUMMARY")
    print(f"{'='*70}")
    print(f"Total test files executed: {report['overall_summary']['total']}")
    print(f"✅ Passed: {report['overall_summary']['passed']}")
    print(f"❌ Failed: {report['overall_summary']['failed']}")
    print(f"⏱️  Timeout: {report['overall_summary']['timeout']}")
    print(f"⚠️  Error: {report['overall_summary']['error']}")
    
    print(f"\nDetailed report saved to: comprehensive_test_report.json")
    
    # Exit with appropriate code
    if report['overall_summary']['failed'] > 0 or report['overall_summary']['error'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()