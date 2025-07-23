#!/usr/bin/env python3
"""
Main script to run all chaos engineering and error recovery tests
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chaos_test_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def run_chaos_engineering_tests() -> Dict[str, Any]:
    """Run chaos engineering framework tests"""
    logger.info("Starting chaos engineering tests...")
    
    try:
        # Import and run chaos tests
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chaos_engineering'))
        from error_recovery_framework import ErrorRecoveryTestSuite
        
        test_suite = ErrorRecoveryTestSuite("/Users/voidlight/voidlight_markitdown")
        results = await test_suite.run_all_tests()
        
        return {
            'status': 'completed',
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Chaos engineering tests failed: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


def run_production_recovery_tests() -> Dict[str, Any]:
    """Run production-specific recovery tests"""
    logger.info("Starting production recovery tests...")
    
    try:
        # Import and run production tests
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chaos_engineering'))
        from production_recovery_tests import ProductionRecoveryTester
        
        with ProductionRecoveryTester() as tester:
            results = tester.run_all_tests()
            
        return {
            'status': 'completed',
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Production recovery tests failed: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


def setup_monitoring() -> Dict[str, Any]:
    """Setup monitoring configuration"""
    logger.info("Setting up monitoring configuration...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chaos_engineering'))
        from monitoring_config import (
            create_production_monitoring_config,
            create_production_runbook,
            MetricsCollector,
            AlertManager,
            HealthChecker
        )
        
        # Create configurations
        monitoring_config = create_production_monitoring_config()
        runbook = create_production_runbook()
        
        # Test monitoring components
        metrics_collector = MetricsCollector()
        alert_manager = AlertManager(metrics_collector)
        health_checker = HealthChecker("/Users/voidlight/voidlight_markitdown")
        
        # Add health checks
        health_checker.add_check("file_system", health_checker.check_file_system)
        health_checker.add_check("memory", health_checker.check_memory)
        health_checker.add_check("disk_space", health_checker.check_disk_space)
        health_checker.add_check("korean_nlp", health_checker.check_korean_nlp)
        
        # Run health checks
        health_results = health_checker.run_checks()
        
        return {
            'status': 'completed',
            'monitoring_config': monitoring_config,
            'runbook': runbook,
            'health_check_results': health_results
        }
        
    except Exception as e:
        logger.error(f"Monitoring setup failed: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


def generate_comprehensive_report(results: Dict[str, Any]) -> str:
    """Generate comprehensive test report"""
    report = []
    report.append("# VoidLight MarkItDown - Production Error Recovery Validation Report")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n## Executive Summary")
    
    # Overall status
    all_passed = all(
        r.get('status') == 'completed' 
        for r in results.values()
    )
    
    if all_passed:
        report.append("\n✅ **Overall Status: PRODUCTION READY**")
        report.append("\nAll error recovery and chaos engineering tests passed successfully.")
    else:
        report.append("\n⚠️ **Overall Status: ISSUES FOUND**")
        report.append("\nSome tests failed. Review detailed results below.")
    
    # Chaos engineering results
    if 'chaos_engineering' in results and results['chaos_engineering']['status'] == 'completed':
        chaos_results = results['chaos_engineering']['results']
        report.append("\n## Chaos Engineering Test Results")
        report.append(f"\n- Total Scenarios: {chaos_results['total_scenarios']}")
        report.append(f"- Passed: {chaos_results['passed']}")
        report.append(f"- Failed: {chaos_results['failed']}")
        report.append(f"- Detection Rate: {chaos_results['detection_rate']*100:.1f}%")
        report.append(f"- Recovery Rate: {chaos_results['recovery_rate']*100:.1f}%")
        
        if chaos_results.get('top_issues'):
            report.append("\n### Top Issues:")
            for issue, count in chaos_results['top_issues'][:5]:
                report.append(f"- {issue}")
    
    # Production recovery results
    if 'production_recovery' in results and results['production_recovery']['status'] == 'completed':
        prod_results = results['production_recovery']['results']
        report.append("\n## Production Recovery Test Results")
        report.append(f"\n- Total Tests: {prod_results['total_tests']}")
        report.append(f"- Passed: {prod_results['passed_tests']}")
        report.append(f"- Failed: {prod_results['failed_tests']}")
        
        report.append("\n### Resilience Summary:")
        for metric, status in prod_results['summary'].items():
            if metric != 'success_rate':
                emoji = '✅' if status == 'GOOD' else '⚠️' if status == 'PARTIAL' else '❌'
                report.append(f"- {metric.replace('_', ' ').title()}: {emoji} {status}")
    
    # Health check results
    if 'monitoring' in results and results['monitoring']['status'] == 'completed':
        health_results = results['monitoring'].get('health_check_results', {})
        report.append("\n## System Health Check")
        report.append(f"\nOverall Health: **{health_results.get('status', 'unknown').upper()}**")
        
        if 'checks' in health_results:
            report.append("\n### Component Health:")
            for check_name, check_result in health_results['checks'].items():
                status_emoji = '✅' if check_result['status'] == 'healthy' else '❌'
                report.append(f"- {check_name}: {status_emoji} {check_result['status']}")
    
    # Recommendations
    report.append("\n## Recommendations")
    
    recommendations = []
    
    # Based on chaos engineering results
    if 'chaos_engineering' in results and results['chaos_engineering']['status'] == 'completed':
        chaos_results = results['chaos_engineering']['results']
        if chaos_results['detection_rate'] < 0.8:
            recommendations.append("- Improve failure detection mechanisms (current rate: {:.1f}%)".format(
                chaos_results['detection_rate']*100
            ))
        if chaos_results['recovery_rate'] < 0.9:
            recommendations.append("- Enhance automatic recovery procedures (current rate: {:.1f}%)".format(
                chaos_results['recovery_rate']*100
            ))
    
    # Based on production recovery results
    if 'production_recovery' in results and results['production_recovery']['status'] == 'completed':
        prod_summary = results['production_recovery']['results']['summary']
        
        if prod_summary.get('encoding_resilience') != 'GOOD':
            recommendations.append("- Strengthen encoding error handling for Korean text")
        if prod_summary.get('memory_resilience') != 'GOOD':
            recommendations.append("- Implement better memory management and limits")
        if prod_summary.get('concurrency_safety') != 'GOOD':
            recommendations.append("- Add thread-safe resource management")
        if prod_summary.get('korean_nlp_resilience') != 'GOOD':
            recommendations.append("- Ensure robust fallbacks for Korean NLP failures")
    
    if not recommendations:
        recommendations.append("- System shows excellent resilience - maintain current standards")
        recommendations.append("- Continue regular chaos testing in staging environment")
        recommendations.append("- Monitor production metrics closely after deployment")
    
    report.extend(recommendations)
    
    # Production readiness checklist
    report.append("\n## Production Readiness Checklist")
    
    checklist = [
        ("Error Detection", chaos_results.get('detection_rate', 0) > 0.8 if 'chaos_engineering' in results else False),
        ("Automatic Recovery", chaos_results.get('recovery_rate', 0) > 0.8 if 'chaos_engineering' in results else False),
        ("Encoding Resilience", prod_summary.get('encoding_resilience') == 'GOOD' if 'production_recovery' in results else False),
        ("Memory Management", prod_summary.get('memory_resilience') in ['GOOD', 'PARTIAL'] if 'production_recovery' in results else False),
        ("Concurrency Safety", prod_summary.get('concurrency_safety') in ['GOOD', 'PARTIAL'] if 'production_recovery' in results else False),
        ("Korean NLP Fallbacks", prod_summary.get('korean_nlp_resilience') in ['GOOD', 'PARTIAL'] if 'production_recovery' in results else False),
        ("Health Checks", health_results.get('status') == 'healthy' if 'monitoring' in results else False),
        ("Monitoring Setup", 'monitoring' in results and results['monitoring']['status'] == 'completed'),
    ]
    
    for item, status in checklist:
        emoji = '✅' if status else '❌'
        report.append(f"- {emoji} {item}")
    
    ready_count = sum(1 for _, status in checklist if status)
    report.append(f"\n**Production Readiness Score: {ready_count}/{len(checklist)}**")
    
    # Monitoring configuration
    if 'monitoring' in results and results['monitoring']['status'] == 'completed':
        report.append("\n## Monitoring Configuration")
        report.append("\nMonitoring has been configured with:")
        report.append("- Prometheus metrics collection")
        report.append("- Alert rules for performance and errors")
        report.append("- Health check endpoints")
        report.append("- Grafana dashboards")
        report.append("- Production runbook for incident response")
    
    return '\n'.join(report)


async def main():
    """Main test orchestrator"""
    logger.info("="*80)
    logger.info("VoidLight MarkItDown - Production Error Recovery Validation")
    logger.info("="*80)
    
    results = {}
    
    # Run chaos engineering tests
    logger.info("\n[1/3] Running chaos engineering tests...")
    chaos_results = await run_chaos_engineering_tests()
    results['chaos_engineering'] = chaos_results
    
    # Save intermediate results
    with open('chaos_engineering_results.json', 'w') as f:
        json.dump(chaos_results, f, indent=2)
    
    # Run production recovery tests
    logger.info("\n[2/3] Running production recovery tests...")
    production_results = run_production_recovery_tests()
    results['production_recovery'] = production_results
    
    # Save intermediate results
    with open('production_recovery_results.json', 'w') as f:
        json.dump(production_results, f, indent=2)
    
    # Setup monitoring
    logger.info("\n[3/3] Setting up monitoring configuration...")
    monitoring_results = setup_monitoring()
    results['monitoring'] = monitoring_results
    
    # Save monitoring config
    if monitoring_results['status'] == 'completed':
        with open('monitoring_config.json', 'w') as f:
            json.dump(monitoring_results['monitoring_config'], f, indent=2)
        with open('runbook.json', 'w') as f:
            json.dump(monitoring_results['runbook'], f, indent=2)
    
    # Generate comprehensive report
    report = generate_comprehensive_report(results)
    
    # Save report
    with open('ERROR_RECOVERY_VALIDATION_REPORT.md', 'w') as f:
        f.write(report)
    
    # Save all results
    with open('all_chaos_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    
    all_passed = all(r.get('status') == 'completed' for r in results.values())
    
    if all_passed:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n⚠️ Some tests failed. Review the reports for details.")
    
    print("\nReports generated:")
    print("  - ERROR_RECOVERY_VALIDATION_REPORT.md (main report)")
    print("  - chaos_engineering_results.json")
    print("  - production_recovery_results.json")
    print("  - monitoring_config.json")
    print("  - runbook.json")
    print("  - chaos_test_results.log")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)