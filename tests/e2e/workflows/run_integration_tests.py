#!/usr/bin/env python3
"""
Automated Integration Test Runner for VoidLight MarkItDown MCP Server
Supports CI/CD pipelines and generates detailed test reports
"""

import sys
import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import argparse
import logging
from typing import Dict, List, Optional

# Setup paths
PROJECT_ROOT = Path(__file__).parent
MCP_ENV_PATH = PROJECT_ROOT / "mcp-env"
TEST_RESULTS_DIR = PROJECT_ROOT / "test-results"
TEST_LOGS_DIR = PROJECT_ROOT / "test-logs"

# Ensure directories exist
TEST_RESULTS_DIR.mkdir(exist_ok=True)
TEST_LOGS_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('integration-test-runner')

class TestRunner:
    """Automated test runner with reporting"""
    
    def __init__(self, verbose: bool = False, junit_output: bool = False):
        self.verbose = verbose
        self.junit_output = junit_output
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def setup_environment(self) -> bool:
        """Setup test environment"""
        logger.info("Setting up test environment...")
        
        # Check if virtual environment exists
        if not MCP_ENV_PATH.exists():
            logger.error(f"Virtual environment not found at {MCP_ENV_PATH}")
            return False
        
        # Check if MCP server is installed
        mcp_server_bin = MCP_ENV_PATH / "bin" / "voidlight-markitdown-mcp"
        if not mcp_server_bin.exists():
            logger.error(f"MCP server binary not found at {mcp_server_bin}")
            return False
        
        # Check Python version
        python_bin = MCP_ENV_PATH / "bin" / "python"
        result = subprocess.run(
            [str(python_bin), "--version"],
            capture_output=True,
            text=True
        )
        logger.info(f"Python version: {result.stdout.strip()}")
        
        return True
    
    def run_test_file(self, test_file: str) -> Dict:
        """Run a single test file and collect results"""
        logger.info(f"Running test: {test_file}")
        
        test_start_time = time.time()
        log_file = TEST_LOGS_DIR / f"{Path(test_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Run the test
        cmd = [str(MCP_ENV_PATH / "bin" / "python"), test_file]
        
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Stream output
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    output_lines.append(line.rstrip())
                    log.write(line)
                    if self.verbose:
                        print(line.rstrip())
            
            process.wait()
        
        test_duration = time.time() - test_start_time
        
        # Parse results from output
        passed_tests = 0
        failed_tests = 0
        test_details = []
        
        for line in output_lines:
            if "✓ PASSED" in line or "✓" in line:
                passed_tests += 1
                test_details.append({"status": "passed", "message": line})
            elif "✗ FAILED" in line or "✗" in line:
                failed_tests += 1
                test_details.append({"status": "failed", "message": line})
        
        result = {
            "test_file": test_file,
            "exit_code": process.returncode,
            "duration": test_duration,
            "passed": passed_tests,
            "failed": failed_tests,
            "total": passed_tests + failed_tests,
            "log_file": str(log_file),
            "details": test_details,
            "success": process.returncode == 0
        }
        
        self.test_results.append(result)
        return result
    
    def run_all_tests(self, test_files: List[str]) -> bool:
        """Run all test files"""
        self.start_time = datetime.now()
        all_passed = True
        
        logger.info(f"Running {len(test_files)} test files...")
        
        for test_file in test_files:
            if os.path.exists(test_file):
                result = self.run_test_file(test_file)
                if result['exit_code'] != 0:
                    all_passed = False
            else:
                logger.error(f"Test file not found: {test_file}")
                all_passed = False
        
        self.end_time = datetime.now()
        return all_passed
    
    def generate_json_report(self) -> str:
        """Generate JSON test report"""
        report = {
            "test_run": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
                "environment": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "mcp_env_path": str(MCP_ENV_PATH)
                }
            },
            "summary": {
                "total_files": len(self.test_results),
                "passed_files": sum(1 for r in self.test_results if r['success']),
                "failed_files": sum(1 for r in self.test_results if not r['success']),
                "total_tests": sum(r['total'] for r in self.test_results),
                "passed_tests": sum(r['passed'] for r in self.test_results),
                "failed_tests": sum(r['failed'] for r in self.test_results)
            },
            "test_files": self.test_results
        }
        
        report_file = TEST_RESULTS_DIR / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)
    
    def generate_junit_xml(self) -> str:
        """Generate JUnit XML report for CI systems"""
        if not self.junit_output:
            return None
        
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_content.append('<testsuites>')
        
        for test_result in self.test_results:
            xml_content.append(f'  <testsuite name="{Path(test_result["test_file"]).stem}" '
                             f'tests="{test_result["total"]}" '
                             f'failures="{test_result["failed"]}" '
                             f'time="{test_result["duration"]:.3f}">')
            
            for detail in test_result['details']:
                test_name = detail['message'].split(':')[0].strip() if ':' in detail['message'] else detail['message']
                xml_content.append(f'    <testcase name="{test_name}" time="0">')
                
                if detail['status'] == 'failed':
                    xml_content.append(f'      <failure message="{detail["message"]}" />')
                
                xml_content.append('    </testcase>')
            
            xml_content.append('  </testsuite>')
        
        xml_content.append('</testsuites>')
        
        junit_file = TEST_RESULTS_DIR / f"junit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        with open(junit_file, 'w') as f:
            f.write('\n'.join(xml_content))
        
        return str(junit_file)
    
    def print_summary(self):
        """Print test summary to console"""
        print("\n" + "="*70)
        print("INTEGRATION TEST SUMMARY")
        print("="*70)
        
        total_files = len(self.test_results)
        passed_files = sum(1 for r in self.test_results if r['success'])
        failed_files = total_files - passed_files
        
        total_tests = sum(r['total'] for r in self.test_results)
        passed_tests = sum(r['passed'] for r in self.test_results)
        failed_tests = sum(r['failed'] for r in self.test_results)
        
        print(f"\nTest Files: {passed_files}/{total_files} passed")
        print(f"Individual Tests: {passed_tests}/{total_tests} passed")
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"Total Duration: {duration:.2f} seconds")
        
        print("\nTest File Results:")
        for result in self.test_results:
            status = "PASSED" if result['success'] else "FAILED"
            print(f"  {Path(result['test_file']).name}: {status} "
                  f"({result['passed']}/{result['total']} tests passed, "
                  f"{result['duration']:.2f}s)")
        
        if failed_files > 0:
            print(f"\n❌ {failed_files} test file(s) failed")
            print("Check the log files for details:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['log_file']}")
        else:
            print("\n✅ All tests passed!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run integration tests for VoidLight MarkItDown MCP Server"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose test output"
    )
    parser.add_argument(
        "--junit",
        action="store_true",
        help="Generate JUnit XML report for CI systems"
    )
    parser.add_argument(
        "--test-files",
        nargs="+",
        help="Specific test files to run (default: all test_mcp*.py files)"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(verbose=args.verbose, junit_output=args.junit)
    
    # Setup environment
    if not runner.setup_environment():
        logger.error("Failed to setup test environment")
        sys.exit(1)
    
    # Determine test files
    if args.test_files:
        test_files = args.test_files
    else:
        # Find all MCP integration test files
        test_files = [
            str(PROJECT_ROOT / "test_mcp_integration_comprehensive.py"),
            str(PROJECT_ROOT / "test_mcp_server.py"),
            str(PROJECT_ROOT / "test_mcp_protocol.py"),
        ]
        # Filter existing files
        test_files = [f for f in test_files if os.path.exists(f)]
    
    if not test_files:
        logger.error("No test files found")
        sys.exit(1)
    
    # Run tests
    all_passed = runner.run_all_tests(test_files)
    
    # Generate reports
    json_report = runner.generate_json_report()
    logger.info(f"JSON report saved to: {json_report}")
    
    if args.junit:
        junit_report = runner.generate_junit_xml()
        if junit_report:
            logger.info(f"JUnit XML report saved to: {junit_report}")
    
    # Print summary
    runner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()