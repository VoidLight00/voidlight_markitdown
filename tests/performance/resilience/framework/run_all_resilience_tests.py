#!/usr/bin/env python3
"""
Run all production resilience tests for VoidLight MarkItDown
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import test suites
from chaos_engineering_suite import ChaosEngineeringTests
from error_injection_framework import ResilienceValidator
from recovery_validation_tests import RecoveryValidator


def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "=" * 70)
    print(f"🔥 {text}")
    print("=" * 70)


def main():
    """Run all resilience tests and generate comprehensive report"""
    print_banner("VoidLight MarkItDown - Production Resilience Testing")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    results = {
        "test_time": datetime.now().isoformat(),
        "test_suites": {},
        "overall_results": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "production_ready": False
        }
    }
    
    # 1. Run Chaos Engineering Tests
    print_banner("Running Chaos Engineering Tests")
    try:
        chaos_tester = ChaosEngineeringTests()
        chaos_tester.run_all_tests()
        
        # Read the generated report
        latest_chaos_report = max(
            Path("reports").glob("chaos_engineering_report_*.json"),
            key=os.path.getctime
        )
        with open(latest_chaos_report, 'r') as f:
            chaos_results = json.load(f)
        
        results["test_suites"]["chaos_engineering"] = chaos_results
        results["overall_results"]["total_tests"] += chaos_results["summary"]["total_scenarios"]
        results["overall_results"]["passed"] += chaos_results["summary"]["passed"]
        results["overall_results"]["failed"] += chaos_results["summary"]["failed"]
        
    except Exception as e:
        print(f"❌ Chaos Engineering Tests failed: {e}")
        results["test_suites"]["chaos_engineering"] = {"error": str(e)}
    
    # 2. Run Error Injection Tests
    print_banner("Running Error Injection & Resilience Tests")
    try:
        resilience_validator = ResilienceValidator()
        resilience_report = resilience_validator.run_all_tests()
        
        results["test_suites"]["error_injection"] = resilience_report
        results["overall_results"]["total_tests"] += resilience_report["summary"]["total_scenarios"]
        results["overall_results"]["passed"] += resilience_report["summary"]["breakdown"]["resilient"]
        results["overall_results"]["failed"] += resilience_report["summary"]["breakdown"]["failed"]
        
    except Exception as e:
        print(f"❌ Error Injection Tests failed: {e}")
        results["test_suites"]["error_injection"] = {"error": str(e)}
    
    # 3. Run Recovery Validation Tests
    print_banner("Running Recovery Mechanism Tests")
    try:
        recovery_validator = RecoveryValidator()
        recovery_report = recovery_validator.run_all_tests()
        
        results["test_suites"]["recovery_validation"] = recovery_report
        
        # Count recovery tests
        recovery_passed = sum(
            1 for test in recovery_report["recovery_tests"].values()
            if test.get("recovered", False)
        )
        recovery_failed = len(recovery_report["recovery_tests"]) - recovery_passed
        
        results["overall_results"]["total_tests"] += len(recovery_report["recovery_tests"])
        results["overall_results"]["passed"] += recovery_passed
        results["overall_results"]["failed"] += recovery_failed
        
    except Exception as e:
        print(f"❌ Recovery Validation Tests failed: {e}")
        results["test_suites"]["recovery_validation"] = {"error": str(e)}
    
    # Calculate overall production readiness
    if results["overall_results"]["total_tests"] > 0:
        success_rate = results["overall_results"]["passed"] / results["overall_results"]["total_tests"]
        results["overall_results"]["success_rate"] = success_rate
        
        # Production ready if:
        # - Success rate >= 80%
        # - Resilience score >= 0.7
        # - Recovery success rate >= 0.8
        production_criteria = [
            success_rate >= 0.8,
            results["test_suites"].get("error_injection", {}).get("summary", {}).get("resilience_score", 0) >= 0.7,
            results["test_suites"].get("recovery_validation", {}).get("summary", {}).get("production_ready", False)
        ]
        
        results["overall_results"]["production_ready"] = all(production_criteria)
    
    # Generate consolidated recommendations
    all_recommendations = set()
    
    for suite_name, suite_data in results["test_suites"].items():
        if isinstance(suite_data, dict) and "recommendations" in suite_data:
            all_recommendations.update(suite_data["recommendations"])
    
    results["consolidated_recommendations"] = list(all_recommendations)
    
    # Save comprehensive report
    report_path = f"reports/production_resilience_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print final summary
    print_banner("Production Resilience Testing Complete")
    print(f"\n📊 Overall Results:")
    print(f"  Total Tests: {results['overall_results']['total_tests']}")
    print(f"  Passed: {results['overall_results']['passed']}")
    print(f"  Failed: {results['overall_results']['failed']}")
    print(f"  Success Rate: {results['overall_results'].get('success_rate', 0):.1%}")
    print(f"\n🚀 Production Ready: {'✅ YES' if results['overall_results']['production_ready'] else '❌ NO'}")
    
    if results["consolidated_recommendations"]:
        print("\n🔧 Top Recommendations:")
        for i, rec in enumerate(results["consolidated_recommendations"][:5], 1):
            print(f"  {i}. {rec}")
    
    print(f"\n📄 Full report saved to: {report_path}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code based on production readiness
    return 0 if results["overall_results"]["production_ready"] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)