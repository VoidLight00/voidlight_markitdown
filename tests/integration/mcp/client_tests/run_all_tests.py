#!/usr/bin/env python3
"""
MCP Client Test Suite Runner
Executes all MCP client tests and generates a comprehensive report
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_test_suite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TestSuiteRunner:
    """Orchestrates all MCP client tests"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.clients_dir = self.base_dir / "clients"
        self.reports_dir = self.base_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.test_results = {}
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        required_packages = {
            'mcp': 'mcp',
            'httpx': 'httpx',
            'aiohttp': 'aiohttp',
            'psutil': 'psutil',
            'matplotlib': 'matplotlib',
            'numpy': 'numpy',
            'aiofiles': 'aiofiles',
            'jsonschema': 'jsonschema'
        }
        
        missing = []
        for package, import_name in required_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                missing.append(package)
        
        if missing:
            logger.error(f"Missing dependencies: {', '.join(missing)}")
            logger.info("Install with: pip install " + ' '.join(missing))
            return False
        
        # Check if voidlight_markitdown_mcp is installed
        try:
            result = subprocess.run(
                ["python", "-m", "voidlight_markitdown_mcp", "--help"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error("voidlight_markitdown_mcp module not found")
                logger.info("Install with: pip install -e packages/voidlight_markitdown-mcp")
                return False
        except Exception as e:
            logger.error(f"Failed to check voidlight_markitdown_mcp: {e}")
            return False
        
        logger.info("All dependencies satisfied")
        return True
    
    async def run_python_tests(self) -> Dict[str, Any]:
        """Run Python client tests"""
        logger.info("\n" + "="*60)
        logger.info("Running Python MCP Client Tests")
        logger.info("="*60)
        
        try:
            # Import and run Python test client
            from clients.python_test_client import MCPTestClient
            
            client = MCPTestClient(self.reports_dir)
            report = await client.run_all_tests()
            
            self.test_results['python'] = {
                'status': 'completed',
                'report': report,
                'report_file': f"python_client_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Python tests failed: {e}")
            self.test_results['python'] = {
                'status': 'failed',
                'error': str(e)
            }
            return {'error': str(e)}
    
    async def run_nodejs_tests(self) -> Dict[str, Any]:
        """Run Node.js client tests"""
        logger.info("\n" + "="*60)
        logger.info("Running Node.js MCP Client Tests")
        logger.info("="*60)
        
        try:
            # Check if Node.js is available
            node_check = subprocess.run(["node", "--version"], capture_output=True)
            if node_check.returncode != 0:
                logger.warning("Node.js not found, skipping Node.js tests")
                self.test_results['nodejs'] = {
                    'status': 'skipped',
                    'reason': 'Node.js not available'
                }
                return {'status': 'skipped'}
            
            # Check for required npm packages
            npm_packages = ['@modelcontextprotocol/sdk', 'axios']
            missing_packages = []
            
            for package in npm_packages:
                check = subprocess.run(
                    ["npm", "list", package, "--depth=0"],
                    capture_output=True,
                    cwd=self.base_dir
                )
                if check.returncode != 0:
                    missing_packages.append(package)
            
            if missing_packages:
                logger.info(f"Installing missing npm packages: {', '.join(missing_packages)}")
                subprocess.run(
                    ["npm", "install"] + missing_packages,
                    cwd=self.base_dir
                )
            
            # Run Node.js tests
            result = subprocess.run(
                ["node", str(self.clients_dir / "nodejs_test_client.js")],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                # Parse the latest report file
                report_files = list(self.reports_dir.glob("nodejs_client_test_report_*.json"))
                if report_files:
                    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
                    with open(latest_report) as f:
                        report = json.load(f)
                    
                    self.test_results['nodejs'] = {
                        'status': 'completed',
                        'report': report,
                        'report_file': latest_report.name
                    }
                    
                    return report
                else:
                    self.test_results['nodejs'] = {
                        'status': 'completed',
                        'output': result.stdout
                    }
                    return {'output': result.stdout}
            else:
                logger.error(f"Node.js tests failed: {result.stderr}")
                self.test_results['nodejs'] = {
                    'status': 'failed',
                    'error': result.stderr
                }
                return {'error': result.stderr}
                
        except Exception as e:
            logger.error(f"Node.js tests failed: {e}")
            self.test_results['nodejs'] = {
                'status': 'failed',
                'error': str(e)
            }
            return {'error': str(e)}
    
    async def run_protocol_compliance_tests(self) -> Dict[str, Any]:
        """Run protocol compliance tests"""
        logger.info("\n" + "="*60)
        logger.info("Running Protocol Compliance Tests")
        logger.info("="*60)
        
        try:
            from clients.protocol_compliance_validator import ProtocolComplianceValidator
            
            validator = ProtocolComplianceValidator(self.reports_dir)
            report = await validator.run_all_validations()
            
            self.test_results['protocol_compliance'] = {
                'status': 'completed',
                'report': report,
                'report_file': f"protocol_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Protocol compliance tests failed: {e}")
            self.test_results['protocol_compliance'] = {
                'status': 'failed',
                'error': str(e)
            }
            return {'error': str(e)}
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        logger.info("\n" + "="*60)
        logger.info("Running Performance Tests")
        logger.info("="*60)
        
        try:
            from clients.performance_test_client import PerformanceTestClient
            
            client = PerformanceTestClient(self.reports_dir)
            report = await client.run_all_tests()
            
            self.test_results['performance'] = {
                'status': 'completed',
                'report': report,
                'report_file': f"performance_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Performance tests failed: {e}")
            self.test_results['performance'] = {
                'status': 'failed',
                'error': str(e)
            }
            return {'error': str(e)}
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        logger.info("\nGenerating summary report...")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'overall_status': 'passed',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'key_findings': [],
            'recommendations': []
        }
        
        # Process each test suite
        for suite_name, suite_result in self.test_results.items():
            suite_summary = {
                'status': suite_result['status']
            }
            
            if suite_result['status'] == 'completed' and 'report' in suite_result:
                report = suite_result['report']
                
                # Extract key metrics based on suite type
                if suite_name == 'python':
                    if 'summary' in report:
                        suite_summary['tests'] = report['summary']['total_tests']
                        suite_summary['passed'] = report['summary']['passed']
                        suite_summary['failed'] = report['summary']['failed']
                        suite_summary['success_rate'] = report['summary']['success_rate']
                        
                        summary['total_tests'] += report['summary']['total_tests']
                        summary['passed_tests'] += report['summary']['passed']
                        summary['failed_tests'] += report['summary']['failed']
                
                elif suite_name == 'protocol_compliance':
                    if 'summary' in report:
                        suite_summary['compliance_score'] = report['summary']['compliance_score']
                        suite_summary['critical_failures'] = len(report.get('failed_critical_checks', []))
                        
                        if report['summary']['compliance_score'] < 80:
                            summary['key_findings'].append(
                                f"Protocol compliance score is low: {report['summary']['compliance_score']}%"
                            )
                            summary['overall_status'] = 'failed'
                
                elif suite_name == 'performance':
                    if 'performance_summary' in report:
                        perf = report['performance_summary']
                        if 'latency' in perf:
                            suite_summary['average_latency_ms'] = perf['latency'].get('average_ms', 0)
                        if 'throughput' in perf:
                            suite_summary['max_throughput_rps'] = perf['throughput'].get('max_rps', 0)
                        
                        # Add recommendations
                        if 'recommendations' in perf:
                            summary['recommendations'].extend(perf['recommendations'])
            
            elif suite_result['status'] == 'failed':
                summary['overall_status'] = 'failed'
                summary['key_findings'].append(
                    f"{suite_name} test suite failed: {suite_result.get('error', 'Unknown error')}"
                )
            
            summary['test_suites'][suite_name] = suite_summary
        
        # Add overall recommendations
        if summary['failed_tests'] > 0:
            summary['recommendations'].insert(0, 
                f"Fix {summary['failed_tests']} failing tests before deployment"
            )
        
        # Save summary report
        summary_file = self.reports_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Summary report saved to: {summary_file}")
        
        return summary
    
    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("Starting MCP Client Test Suite")
        logger.info(f"Test directory: {self.base_dir}")
        logger.info(f"Reports will be saved to: {self.reports_dir}")
        
        # Check dependencies first
        if not self.check_dependencies():
            logger.error("Dependency check failed. Please install missing packages.")
            return
        
        # Run test suites
        test_suites = [
            ("Python Client Tests", self.run_python_tests),
            ("Node.js Client Tests", self.run_nodejs_tests),
            ("Protocol Compliance Tests", self.run_protocol_compliance_tests),
            ("Performance Tests", self.run_performance_tests)
        ]
        
        for suite_name, test_func in test_suites:
            try:
                await test_func()
            except Exception as e:
                logger.error(f"{suite_name} encountered an error: {e}")
        
        # Generate summary
        summary = self.generate_summary_report()
        
        # Print final summary
        print("\n" + "="*80)
        print("MCP CLIENT TEST SUITE SUMMARY")
        print("="*80)
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        
        if summary['key_findings']:
            print("\nKey Findings:")
            for finding in summary['key_findings']:
                print(f"  - {finding}")
        
        if summary['recommendations']:
            print("\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
        
        print("\nTest Suite Results:")
        for suite_name, suite_result in summary['test_suites'].items():
            status = suite_result['status'].upper()
            print(f"  {suite_name}: {status}")
            
            if suite_result['status'] == 'completed':
                if 'success_rate' in suite_result:
                    print(f"    Success Rate: {suite_result['success_rate']:.1f}%")
                if 'compliance_score' in suite_result:
                    print(f"    Compliance Score: {suite_result['compliance_score']:.1f}%")
                if 'average_latency_ms' in suite_result:
                    print(f"    Avg Latency: {suite_result['average_latency_ms']:.2f}ms")
        
        print("="*80)
        
        # Create README for test results
        self.create_test_readme(summary)
    
    def create_test_readme(self, summary: Dict[str, Any]):
        """Create a README file for the test results"""
        readme_content = f"""# MCP Client Test Results

Generated: {summary['timestamp']}

## Overall Status: {summary['overall_status'].upper()}

### Test Summary
- **Total Tests**: {summary['total_tests']}
- **Passed**: {summary['passed_tests']}
- **Failed**: {summary['failed_tests']}

### Test Suites

"""
        
        for suite_name, suite_result in summary['test_suites'].items():
            readme_content += f"#### {suite_name.replace('_', ' ').title()}\n"
            readme_content += f"- **Status**: {suite_result['status']}\n"
            
            if suite_result['status'] == 'completed':
                if 'success_rate' in suite_result:
                    readme_content += f"- **Success Rate**: {suite_result['success_rate']:.1f}%\n"
                if 'compliance_score' in suite_result:
                    readme_content += f"- **Compliance Score**: {suite_result['compliance_score']:.1f}%\n"
                if 'average_latency_ms' in suite_result:
                    readme_content += f"- **Average Latency**: {suite_result['average_latency_ms']:.2f}ms\n"
                if 'max_throughput_rps' in suite_result:
                    readme_content += f"- **Max Throughput**: {suite_result['max_throughput_rps']:.2f} RPS\n"
            
            readme_content += "\n"
        
        if summary['key_findings']:
            readme_content += "### Key Findings\n\n"
            for finding in summary['key_findings']:
                readme_content += f"- {finding}\n"
            readme_content += "\n"
        
        if summary['recommendations']:
            readme_content += "### Recommendations\n\n"
            for rec in summary['recommendations']:
                readme_content += f"- {rec}\n"
            readme_content += "\n"
        
        readme_content += """## Test Reports

Individual test reports are available in the `reports` directory:
- `python_client_test_report_*.json` - Python client test results
- `nodejs_client_test_report_*.json` - Node.js client test results
- `protocol_compliance_report_*.json` - Protocol compliance validation
- `performance_test_report_*.json` - Performance test results

## Running Tests

To run all tests:
```bash
python run_all_tests.py
```

To run individual test suites:
```bash
# Python tests
python clients/python_test_client.py

# Protocol compliance
python clients/protocol_compliance_validator.py

# Performance tests
python clients/performance_test_client.py

# Node.js tests (requires Node.js)
node clients/nodejs_test_client.js
```

## Requirements

- Python 3.9+
- Node.js 16+ (for Node.js tests)
- Required Python packages: mcp, httpx, aiohttp, psutil, matplotlib, numpy, aiofiles, jsonschema
- Required npm packages: @modelcontextprotocol/sdk, axios
"""
        
        readme_file = self.reports_dir / "README.md"
        readme_file.write_text(readme_content)
        logger.info(f"Test README created at: {readme_file}")


async def main():
    """Main entry point"""
    runner = TestSuiteRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())