#!/usr/bin/env python3
"""
Automated Integration Test Runner for VoidLight MarkItDown MCP Server
Can be used for CI/CD pipelines, scheduled testing, or manual execution
"""

import os
import sys
import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Configuration
PROJECT_ROOT = Path(__file__).parent.absolute()
MCP_ENV_PATH = PROJECT_ROOT / "mcp-env"
PYTHON_BIN = MCP_ENV_PATH / "bin" / "python"
TEST_SCRIPTS = {
    "comprehensive": "test_mcp_integration_comprehensive.py",
    "enhanced": "test_mcp_integration_enhanced.py",
    "simple": "test_mcp_server.py",
    "edge_cases": "test_mcp_edge_cases.py",
    "protocol": "test_mcp_protocol.py"
}

class IntegrationTestRunner:
    """Manages automated integration test execution"""
    
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self.results = {}
        self.start_time = datetime.now()
        
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "test_suites": ["enhanced"],
            "timeout_minutes": 30,
            "retry_failed": True,
            "max_retries": 2,
            "email_notifications": False,
            "slack_notifications": False,
            "save_artifacts": True,
            "artifact_dir": "test_artifacts",
            "verbose": True
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
        
    def run_test_suite(self, suite_name: str) -> dict:
        """Run a single test suite"""
        print(f"\n{'='*60}")
        print(f"Running test suite: {suite_name}")
        print(f"{'='*60}")
        
        if suite_name not in TEST_SCRIPTS:
            print(f"Error: Unknown test suite '{suite_name}'")
            return {"passed": False, "error": "Unknown test suite"}
            
        test_script = PROJECT_ROOT / TEST_SCRIPTS[suite_name]
        if not test_script.exists():
            print(f"Error: Test script not found: {test_script}")
            return {"passed": False, "error": "Test script not found"}
            
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(PROJECT_ROOT)
        env['VOIDLIGHT_LOG_LEVEL'] = 'INFO'
        
        # Create artifact directory for this run
        if self.config['save_artifacts']:
            artifact_dir = PROJECT_ROOT / self.config['artifact_dir'] / f"{suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            env['TEST_ARTIFACT_DIR'] = str(artifact_dir)
            
        # Run the test
        start_time = time.time()
        try:
            result = subprocess.run(
                [str(PYTHON_BIN), str(test_script)],
                capture_output=True,
                text=True,
                env=env,
                timeout=self.config['timeout_minutes'] * 60
            )
            
            duration = time.time() - start_time
            
            # Parse results
            test_result = {
                "passed": result.returncode == 0,
                "duration": duration,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Try to extract summary from output
            if "Test Summary" in result.stdout:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if "Total:" in line and "tests passed" in line:
                        test_result["summary"] = line.strip()
                        break
                        
            # Save output if configured
            if self.config['save_artifacts'] and 'artifact_dir' in locals():
                with open(artifact_dir / "stdout.txt", 'w') as f:
                    f.write(result.stdout)
                with open(artifact_dir / "stderr.txt", 'w') as f:
                    f.write(result.stderr)
                    
                # Look for generated reports
                for report_file in PROJECT_ROOT.glob("integration_test_report_*.json"):
                    if report_file.stat().st_mtime > start_time:
                        # This report was created during the test
                        import shutil
                        shutil.move(str(report_file), str(artifact_dir / report_file.name))
                        test_result["report_file"] = str(artifact_dir / report_file.name)
                        
            return test_result
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": f"Test timed out after {self.config['timeout_minutes']} minutes",
                "duration": self.config['timeout_minutes'] * 60
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
            
    def run_all_tests(self) -> bool:
        """Run all configured test suites"""
        print(f"VoidLight MarkItDown MCP Integration Tests")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Configuration: {json.dumps(self.config, indent=2)}")
        
        all_passed = True
        
        for suite_name in self.config['test_suites']:
            result = self.run_test_suite(suite_name)
            self.results[suite_name] = result
            
            # Handle retries if configured
            if not result['passed'] and self.config['retry_failed']:
                for retry in range(1, self.config['max_retries'] + 1):
                    print(f"\nRetrying {suite_name} (attempt {retry + 1}/{self.config['max_retries'] + 1})...")
                    time.sleep(5)  # Brief pause before retry
                    
                    retry_result = self.run_test_suite(suite_name)
                    if retry_result['passed']:
                        self.results[suite_name] = retry_result
                        self.results[suite_name]['retries'] = retry
                        break
                        
            all_passed = all_passed and self.results[suite_name]['passed']
            
        return all_passed
        
    def generate_summary(self) -> dict:
        """Generate test execution summary"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_duration_seconds": total_duration,
            "test_suites_run": len(self.results),
            "passed": sum(1 for r in self.results.values() if r['passed']),
            "failed": sum(1 for r in self.results.values() if not r['passed']),
            "results": self.results
        }
        
        return summary
        
    def save_summary(self, summary: dict):
        """Save test summary to file"""
        summary_file = PROJECT_ROOT / f"test_summary_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"\nTest summary saved to: {summary_file}")
        return summary_file
        
    def send_notifications(self, summary: dict):
        """Send test result notifications"""
        if self.config.get('email_notifications'):
            self._send_email_notification(summary)
            
        if self.config.get('slack_notifications'):
            self._send_slack_notification(summary)
            
    def _send_email_notification(self, summary: dict):
        """Send email notification with test results"""
        # This is a placeholder - implement based on your email configuration
        print("Email notifications not implemented")
        
    def _send_slack_notification(self, summary: dict):
        """Send Slack notification with test results"""
        # This is a placeholder - implement based on your Slack configuration
        print("Slack notifications not implemented")
        
    def print_summary(self, summary: dict):
        """Print test execution summary"""
        print("\n" + "="*60)
        print("TEST EXECUTION SUMMARY")
        print("="*60)
        
        print(f"Total Duration: {summary['total_duration_seconds']:.2f} seconds")
        print(f"Test Suites Run: {summary['test_suites_run']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        
        print("\nDetailed Results:")
        for suite_name, result in summary['results'].items():
            status = "PASSED" if result['passed'] else "FAILED"
            print(f"\n{suite_name}: {status}")
            if 'duration' in result:
                print(f"  Duration: {result['duration']:.2f}s")
            if 'summary' in result:
                print(f"  Summary: {result['summary']}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            if 'retries' in result:
                print(f"  Retries: {result['retries']}")
            if 'report_file' in result:
                print(f"  Report: {result['report_file']}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run VoidLight MarkItDown MCP integration tests")
    parser.add_argument(
        "--config",
        help="Path to configuration file (JSON)",
        default=None
    )
    parser.add_argument(
        "--suites",
        nargs="+",
        choices=list(TEST_SCRIPTS.keys()),
        help="Test suites to run",
        default=None
    )
    parser.add_argument(
        "--no-retry",
        action="store_true",
        help="Don't retry failed tests"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout in minutes for each test suite",
        default=30
    )
    parser.add_argument(
        "--artifacts-dir",
        help="Directory to save test artifacts",
        default="test_artifacts"
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = IntegrationTestRunner(args.config)
    
    # Override config with command line arguments
    if args.suites:
        runner.config['test_suites'] = args.suites
    if args.no_retry:
        runner.config['retry_failed'] = False
    if args.timeout:
        runner.config['timeout_minutes'] = args.timeout
    if args.artifacts_dir:
        runner.config['artifact_dir'] = args.artifacts_dir
        
    # Run tests
    all_passed = runner.run_all_tests()
    
    # Generate and save summary
    summary = runner.generate_summary()
    runner.save_summary(summary)
    runner.print_summary(summary)
    
    # Send notifications
    runner.send_notifications(summary)
    
    # Exit with appropriate code
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())