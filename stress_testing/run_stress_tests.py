#!/usr/bin/env python3
"""
Main script to run comprehensive stress tests for VoidLight MarkItDown MCP Server
Coordinates all testing components and generates final reports
"""

import asyncio
import json
import sys
import os
import time
import subprocess
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import argparse

# Add stress_testing directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import testing components
from concurrent_stress_test_framework import (
    StressTestRunner, TestScenario, LoadPattern, ClientType, 
    create_standard_scenarios, MCPServerManager
)
from monitoring_dashboard import MetricsCollector, MonitoringDashboard
from client_simulators import ClientPool, ClientConfig, RequestPattern
from performance_analyzer import PerformanceAnalyzer, visualize_performance_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stress_test_run.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class StressTestOrchestrator:
    """Orchestrate the complete stress testing process"""
    
    def __init__(self, test_config: Dict[str, Any]):
        self.config = test_config
        self.results_dir = Path(self.config.get("results_dir", "stress_test_results"))
        self.results_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_results_file = self.results_dir / f"stress_test_results_{self.timestamp}.json"
        self.analysis_report_file = self.results_dir / f"performance_analysis_{self.timestamp}.json"
        
        self.server_manager = None
        self.dashboard_process = None
        self.metrics_collector = MetricsCollector()
        
    def prepare_environment(self):
        """Prepare test environment"""
        logger.info("Preparing test environment")
        
        # Check MCP server binary
        mcp_binary = self.config.get("mcp_binary", "/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp")
        if not Path(mcp_binary).exists():
            raise FileNotFoundError(f"MCP server binary not found: {mcp_binary}")
            
        # Create required directories
        for dir_name in ["logs", "plots", "reports"]:
            (self.results_dir / dir_name).mkdir(exist_ok=True)
            
        # Kill any existing MCP servers
        self._cleanup_servers()
        
    def _cleanup_servers(self):
        """Kill any existing MCP server processes"""
        try:
            # Find and kill MCP server processes
            result = subprocess.run(
                ["pgrep", "-f", "voidlight-markitdown-mcp"],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        logger.info(f"Killed existing MCP server process: {pid}")
                    except:
                        pass
                        
                time.sleep(2)  # Wait for processes to terminate
        except:
            pass
            
    def start_monitoring_dashboard(self):
        """Start the monitoring dashboard in background"""
        if self.config.get("enable_dashboard", True):
            logger.info("Starting monitoring dashboard")
            
            dashboard_script = Path(__file__).parent / "monitoring_dashboard.py"
            self.dashboard_process = subprocess.Popen(
                [sys.executable, str(dashboard_script), "--port", "8050"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(3)  # Give dashboard time to start
            logger.info("Monitoring dashboard available at http://localhost:8050")
            
    def stop_monitoring_dashboard(self):
        """Stop the monitoring dashboard"""
        if self.dashboard_process:
            logger.info("Stopping monitoring dashboard")
            self.dashboard_process.terminate()
            self.dashboard_process.wait(timeout=5)
            
    async def run_test_suite(self):
        """Run the complete test suite"""
        logger.info("Starting stress test suite")
        
        # Get test scenarios
        scenarios = self._get_test_scenarios()
        
        # Create test runner
        runner = StressTestRunner()
        
        # Add scenarios
        for scenario in scenarios:
            runner.add_scenario(scenario)
            
        # Hook up metrics collector
        original_run_scenario = runner.run_scenario
        
        async def run_scenario_with_metrics(scenario):
            # Update dashboard with current scenario
            self.metrics_collector.current_scenario = scenario.name
            self.metrics_collector.test_start_time = datetime.now()
            
            # Run scenario
            result = await original_run_scenario(scenario)
            
            # Update metrics collector with results
            if "metrics" in result:
                metrics = result["metrics"]
                self.metrics_collector.add_metrics({
                    "throughput": metrics.get("throughput", 0),
                    "response_times": metrics.get("response_times", {}),
                    "error_rate": metrics.get("error_rate", 0),
                    "active_clients": scenario.max_clients,
                    "resources": result.get("resource_usage", {}).get("cpu", {}),
                    "error_types": metrics.get("error_types", {})
                })
                
            return result
            
        runner.run_scenario = run_scenario_with_metrics
        
        # Run all scenarios
        await runner.run_all_scenarios()
        
        # Save results
        with open(self.test_results_file, 'w') as f:
            json.dump(runner.results, f, indent=2, default=str)
            
        logger.info(f"Test results saved to {self.test_results_file}")
        
        return runner.results
        
    def _get_test_scenarios(self) -> List[TestScenario]:
        """Get test scenarios based on configuration"""
        test_profile = self.config.get("test_profile", "standard")
        
        if test_profile == "quick":
            # Quick test scenarios (reduced duration and clients)
            scenarios = [
                TestScenario(
                    name="quick_http_test",
                    load_pattern=LoadPattern.GRADUAL_RAMP,
                    client_type=ClientType.HTTP_SSE,
                    initial_clients=1,
                    max_clients=20,
                    duration_seconds=60,
                    ramp_up_seconds=20,
                    request_delay_ms=100,
                    payload_size="small",
                    korean_ratio=0.5
                ),
                TestScenario(
                    name="quick_stdio_test",
                    load_pattern=LoadPattern.SUSTAINED,
                    client_type=ClientType.STDIO,
                    initial_clients=10,
                    max_clients=10,
                    duration_seconds=60,
                    request_delay_ms=200,
                    payload_size="medium",
                    korean_ratio=0.7
                ),
                TestScenario(
                    name="quick_mixed_test",
                    load_pattern=LoadPattern.SPIKE,
                    client_type=ClientType.MIXED,
                    initial_clients=5,
                    max_clients=30,
                    duration_seconds=60,
                    request_delay_ms=150,
                    payload_size="small",
                    korean_ratio=0.5
                )
            ]
        elif test_profile == "comprehensive":
            # Full comprehensive test
            scenarios = create_standard_scenarios()
        elif test_profile == "korean_focus":
            # Korean text focused testing
            scenarios = [
                TestScenario(
                    name="korean_basic_load",
                    load_pattern=LoadPattern.SUSTAINED,
                    client_type=ClientType.HTTP_SSE,
                    initial_clients=20,
                    max_clients=20,
                    duration_seconds=300,
                    request_delay_ms=100,
                    payload_size="medium",
                    korean_ratio=1.0
                ),
                TestScenario(
                    name="korean_high_volume",
                    load_pattern=LoadPattern.GRADUAL_RAMP,
                    client_type=ClientType.HTTP_SSE,
                    initial_clients=10,
                    max_clients=100,
                    duration_seconds=300,
                    request_delay_ms=50,
                    payload_size="large",
                    korean_ratio=1.0
                ),
                TestScenario(
                    name="korean_mixed_encoding",
                    load_pattern=LoadPattern.WAVE,
                    client_type=ClientType.MIXED,
                    initial_clients=15,
                    max_clients=50,
                    duration_seconds=240,
                    request_delay_ms=100,
                    payload_size="medium",
                    korean_ratio=0.8,
                    error_injection_rate=0.1
                )
            ]
        elif test_profile == "stress_only":
            # Stress to failure testing
            scenarios = [
                TestScenario(
                    name="stress_to_failure_http",
                    load_pattern=LoadPattern.STRESS_TO_FAILURE,
                    client_type=ClientType.HTTP_SSE,
                    initial_clients=10,
                    max_clients=1000,
                    duration_seconds=600,
                    request_delay_ms=10,
                    payload_size="medium",
                    korean_ratio=0.5,
                    error_injection_rate=0.05
                ),
                TestScenario(
                    name="extreme_payload_stress",
                    load_pattern=LoadPattern.SUSTAINED,
                    client_type=ClientType.HTTP_SSE,
                    initial_clients=10,
                    max_clients=10,
                    duration_seconds=180,
                    request_delay_ms=1000,
                    payload_size="extreme",
                    korean_ratio=0.5,
                    error_injection_rate=0
                )
            ]
        else:
            # Custom scenarios from config
            scenarios = []
            for scenario_config in self.config.get("custom_scenarios", []):
                scenarios.append(TestScenario(**scenario_config))
                
        # Apply global overrides if specified
        if "scenario_overrides" in self.config:
            overrides = self.config["scenario_overrides"]
            for scenario in scenarios:
                for key, value in overrides.items():
                    if hasattr(scenario, key):
                        setattr(scenario, key, value)
                        
        return scenarios
        
    def analyze_results(self, test_results: Dict[str, Any]):
        """Analyze test results and generate reports"""
        logger.info("Analyzing test results")
        
        # Create analyzer
        analyzer = PerformanceAnalyzer(self.test_results_file)
        analyzer.load_test_results()
        
        # Analyze all scenarios
        analyzer.analyze_all_scenarios()
        
        # Generate reports
        print("\n" + "="*80)
        print("STRESS TEST ANALYSIS")
        print("="*80)
        
        analyzer.generate_comparison_report()
        analyzer.generate_optimization_recommendations()
        
        # Save analysis report
        analyzer.save_analysis_report(self.analysis_report_file)
        
        # Generate visualizations
        if self.config.get("generate_plots", True):
            plot_dir = self.results_dir / "plots"
            visualize_performance_data(str(self.test_results_file), str(plot_dir))
            
    def generate_final_report(self):
        """Generate final comprehensive report"""
        logger.info("Generating final report")
        
        report_file = self.results_dir / f"final_report_{self.timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# VoidLight MarkItDown MCP Server - Stress Test Report\n\n")
            f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Test Profile:** {self.config.get('test_profile', 'standard')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            
            # Load test results
            with open(self.test_results_file, 'r') as rf:
                test_results = json.load(rf)
                
            # Calculate summary metrics
            total_scenarios = len(test_results)
            failed_scenarios = sum(1 for r in test_results.values() if "error" in r)
            
            f.write(f"- **Total Scenarios Tested:** {total_scenarios}\n")
            f.write(f"- **Successful Scenarios:** {total_scenarios - failed_scenarios}\n")
            f.write(f"- **Failed Scenarios:** {failed_scenarios}\n\n")
            
            # Key findings
            f.write("### Key Findings\n\n")
            
            # Find best and worst performers
            best_throughput = 0
            worst_error_rate = 0
            best_scenario = ""
            worst_scenario = ""
            
            for scenario_name, result in test_results.items():
                if "error" not in result:
                    metrics = result.get("metrics", {})
                    throughput = metrics.get("throughput", 0)
                    error_rate = metrics.get("error_rate", 0)
                    
                    if throughput > best_throughput:
                        best_throughput = throughput
                        best_scenario = scenario_name
                        
                    if error_rate > worst_error_rate:
                        worst_error_rate = error_rate
                        worst_scenario = scenario_name
                        
            f.write(f"- **Best Throughput:** {best_throughput:.2f} req/s ({best_scenario})\n")
            f.write(f"- **Highest Error Rate:** {worst_error_rate:.2f}% ({worst_scenario})\n\n")
            
            # Detailed results
            f.write("## Detailed Results\n\n")
            
            for scenario_name, result in test_results.items():
                f.write(f"### {scenario_name}\n\n")
                
                if "error" in result:
                    f.write(f"**Status:** FAILED - {result['error']}\n\n")
                else:
                    metrics = result.get("metrics", {})
                    f.write(f"**Status:** SUCCESS\n\n")
                    f.write("**Metrics:**\n")
                    f.write(f"- Total Requests: {metrics.get('total_requests', 0):,}\n")
                    f.write(f"- Throughput: {metrics.get('throughput', 0):.2f} req/s\n")
                    f.write(f"- Error Rate: {metrics.get('error_rate', 0):.2f}%\n")
                    
                    response_times = metrics.get("response_times", {})
                    f.write(f"- Response Times:\n")
                    f.write(f"  - P50: {response_times.get('p50', 0)*1000:.0f}ms\n")
                    f.write(f"  - P95: {response_times.get('p95', 0)*1000:.0f}ms\n")
                    f.write(f"  - P99: {response_times.get('p99', 0)*1000:.0f}ms\n\n")
                    
            # Load analysis report if available
            if self.analysis_report_file.exists():
                with open(self.analysis_report_file, 'r') as af:
                    analysis = json.load(af)
                    
                f.write("## Performance Analysis\n\n")
                f.write(f"**Total Bottlenecks Identified:** {analysis.get('total_bottlenecks', 0)}\n\n")
                
                # Recommendations summary
                if "recommendations" in analysis:
                    f.write("### Top Recommendations\n\n")
                    for i, rec in enumerate(analysis["recommendations"][:10], 1):
                        f.write(f"{i}. {rec}\n")
                        
            f.write("\n## Test Configuration\n\n")
            f.write("```json\n")
            f.write(json.dumps(self.config, indent=2))
            f.write("\n```\n")
            
        logger.info(f"Final report saved to {report_file}")
        print(f"\nFinal report available at: {report_file}")
        
    async def run_complete_test(self):
        """Run the complete stress test process"""
        try:
            # Prepare environment
            self.prepare_environment()
            
            # Start monitoring dashboard
            self.start_monitoring_dashboard()
            
            # Run test suite
            test_results = await self.run_test_suite()
            
            # Analyze results
            self.analyze_results(test_results)
            
            # Generate final report
            self.generate_final_report()
            
            logger.info("Stress testing completed successfully")
            
        except Exception as e:
            logger.error(f"Stress testing failed: {e}", exc_info=True)
            raise
            
        finally:
            # Cleanup
            self.stop_monitoring_dashboard()
            self._cleanup_servers()


def load_test_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load test configuration"""
    default_config = {
        "test_profile": "quick",  # quick, comprehensive, korean_focus, stress_only, custom
        "results_dir": "stress_test_results",
        "mcp_binary": "/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp",
        "enable_dashboard": True,
        "generate_plots": True,
        "scenario_overrides": {},
        "custom_scenarios": []
    }
    
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            custom_config = json.load(f)
            default_config.update(custom_config)
            
    return default_config


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive stress tests for VoidLight MarkItDown MCP Server"
    )
    
    parser.add_argument(
        "--profile", 
        choices=["quick", "comprehensive", "korean_focus", "stress_only", "custom"],
        default="quick",
        help="Test profile to run"
    )
    parser.add_argument(
        "--config",
        help="Path to custom configuration file"
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Disable monitoring dashboard"
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable plot generation"
    )
    parser.add_argument(
        "--results-dir",
        default="stress_test_results",
        help="Directory for test results"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_test_config(args.config)
    
    # Apply command line overrides
    config["test_profile"] = args.profile
    config["enable_dashboard"] = not args.no_dashboard
    config["generate_plots"] = not args.no_plots
    config["results_dir"] = args.results_dir
    
    # Create and run orchestrator
    orchestrator = StressTestOrchestrator(config)
    await orchestrator.run_complete_test()
    
    print("\n" + "="*80)
    print("STRESS TESTING COMPLETE")
    print("="*80)
    print(f"Results directory: {orchestrator.results_dir}")
    print(f"Test results: {orchestrator.test_results_file}")
    print(f"Analysis report: {orchestrator.analysis_report_file}")
    
    if config["enable_dashboard"]:
        print("\nMonitoring dashboard was available at: http://localhost:8050")
        
    if config["generate_plots"]:
        print(f"Performance plots: {orchestrator.results_dir}/plots/")


if __name__ == "__main__":
    asyncio.run(main())