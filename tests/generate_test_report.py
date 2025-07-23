#!/usr/bin/env python3
"""
Generate a comprehensive test report for VoidLight MarkItDown.
Analyzes test structure, coverage, and provides recommendations.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET


class TestReportGenerator:
    def __init__(self, test_root: Path):
        self.test_root = test_root
        self.project_root = test_root.parent
        
    def count_tests(self) -> Dict[str, int]:
        """Count tests by category."""
        counts = {
            'unit': 0,
            'integration': 0,
            'e2e': 0,
            'performance': 0,
            'total': 0
        }
        
        for category in ['unit', 'integration', 'e2e', 'performance']:
            category_path = self.test_root / category
            if category_path.exists():
                test_files = list(category_path.rglob('test_*.py'))
                test_files.extend(category_path.rglob('*_test.py'))
                
                for test_file in test_files:
                    with open(test_file, 'r') as f:
                        content = f.read()
                        # Count test functions
                        test_count = content.count('def test_')
                        counts[category] += test_count
                        counts['total'] += test_count
        
        return counts
    
    def analyze_coverage(self) -> Dict[str, any]:
        """Analyze test coverage if available."""
        coverage_file = self.project_root / '.coverage'
        if not coverage_file.exists():
            return {'available': False}
        
        try:
            # Run coverage report
            result = subprocess.run(
                ['python3', '-m', 'coverage', 'report', '--format=json'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return {
                    'available': True,
                    'total_coverage': coverage_data.get('totals', {}).get('percent_covered', 0),
                    'files': coverage_data.get('files', {})
                }
        except Exception as e:
            print(f"Error analyzing coverage: {e}")
        
        return {'available': False}
    
    def check_test_structure(self) -> List[Dict[str, str]]:
        """Check for test structure issues."""
        issues = []
        
        # Check for __init__.py files
        for root, dirs, files in os.walk(self.test_root):
            if '__init__.py' not in files and root != str(self.test_root):
                issues.append({
                    'type': 'missing_init',
                    'path': root,
                    'message': f"Missing __init__.py in {root}"
                })
        
        # Check for tests in wrong locations
        root_tests = list(self.project_root.glob('test_*.py'))
        if root_tests:
            issues.append({
                'type': 'misplaced_tests',
                'count': len(root_tests),
                'message': f"Found {len(root_tests)} test files in project root"
            })
        
        # Check for proper test naming
        for test_file in self.test_root.rglob('*.py'):
            if test_file.name not in ['__init__.py', 'conftest.py']:
                if not (test_file.name.startswith('test_') or test_file.name.endswith('_test.py')):
                    if 'test' in test_file.name.lower():
                        issues.append({
                            'type': 'naming_convention',
                            'path': str(test_file),
                            'message': f"Test file {test_file.name} doesn't follow naming convention"
                        })
        
        return issues
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("# VoidLight MarkItDown Test Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n## Test Statistics\n")
        
        # Test counts
        counts = self.count_tests()
        report.append("### Test Count by Category\n")
        report.append("| Category | Count | Percentage |")
        report.append("|----------|-------|------------|")
        
        for category in ['unit', 'integration', 'e2e', 'performance']:
            percentage = (counts[category] / counts['total'] * 100) if counts['total'] > 0 else 0
            report.append(f"| {category.capitalize()} | {counts[category]} | {percentage:.1f}% |")
        
        report.append(f"| **Total** | **{counts['total']}** | **100%** |")
        
        # Coverage analysis
        report.append("\n## Code Coverage\n")
        coverage = self.analyze_coverage()
        if coverage['available']:
            report.append(f"Overall Coverage: **{coverage['total_coverage']:.1f}%**\n")
        else:
            report.append("Coverage data not available. Run tests with `--cov` flag.\n")
        
        # Structure analysis
        report.append("\n## Test Structure Analysis\n")
        issues = self.check_test_structure()
        if issues:
            report.append(f"Found {len(issues)} structure issues:\n")
            for issue in issues:
                report.append(f"- {issue['message']}")
        else:
            report.append("✅ Test structure looks good!\n")
        
        # Recommendations
        report.append("\n## Recommendations\n")
        
        if counts['total'] < 50:
            report.append("- Consider adding more tests for better coverage")
        
        if counts['unit'] < counts['total'] * 0.5:
            report.append("- Unit tests should make up at least 50% of tests")
        
        if counts['performance'] < 5:
            report.append("- Add more performance tests to ensure system stability")
        
        if not coverage['available']:
            report.append("- Run tests with coverage to identify untested code")
        elif coverage['available'] and coverage['total_coverage'] < 80:
            report.append(f"- Improve code coverage (currently {coverage['total_coverage']:.1f}%)")
        
        # Test commands
        report.append("\n## Quick Test Commands\n")
        report.append("```bash")
        report.append("# Run all tests with coverage")
        report.append("pytest --cov=voidlight_markitdown")
        report.append("\n# Run specific test categories")
        report.append("pytest tests/unit/           # Fast unit tests")
        report.append("pytest tests/integration/    # Integration tests")
        report.append("pytest tests/e2e/           # End-to-end tests")
        report.append("pytest tests/performance/    # Performance tests")
        report.append("\n# Run tests by marker")
        report.append("pytest -m korean            # Korean language tests")
        report.append("pytest -m mcp              # MCP protocol tests")
        report.append("```")
        
        return '\n'.join(report)
    
    def save_report(self, output_path: Path):
        """Save report to file."""
        report = self.generate_report()
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"Report saved to: {output_path}")


def main():
    """Generate test report."""
    test_root = Path(__file__).parent
    generator = TestReportGenerator(test_root)
    
    # Generate and save report
    report_path = test_root / 'TEST_REPORT.md'
    generator.save_report(report_path)
    
    # Also print to console
    print(generator.generate_report())


if __name__ == "__main__":
    main()