#!/usr/bin/env python3
"""
Performance Analyzer and Bottleneck Detection Tool
Analyzes stress test results and identifies performance bottlenecks
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import psutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    throughput: List[float] = field(default_factory=list)
    response_times_p50: List[float] = field(default_factory=list)
    response_times_p95: List[float] = field(default_factory=list)
    response_times_p99: List[float] = field(default_factory=list)
    error_rates: List[float] = field(default_factory=list)
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    connection_count: List[int] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)


@dataclass
class Bottleneck:
    """Identified performance bottleneck"""
    type: str  # cpu, memory, io, network, application
    severity: str  # low, medium, high, critical
    description: str
    metrics: Dict[str, Any]
    recommendations: List[str]
    impact_score: float  # 0-100


class PerformanceAnalyzer:
    """Analyze performance data and identify bottlenecks"""
    
    def __init__(self, test_results_path: str):
        self.test_results_path = Path(test_results_path)
        self.test_data: Dict[str, Any] = {}
        self.bottlenecks: List[Bottleneck] = []
        self.metrics = PerformanceMetrics()
        
    def load_test_results(self):
        """Load test results from file"""
        if not self.test_results_path.exists():
            raise FileNotFoundError(f"Test results not found: {self.test_results_path}")
            
        with open(self.test_results_path, 'r') as f:
            self.test_data = json.load(f)
            
        logger.info(f"Loaded test results with {len(self.test_data)} scenarios")
        
    def analyze_all_scenarios(self):
        """Analyze all test scenarios"""
        for scenario_name, scenario_data in self.test_data.items():
            if "error" in scenario_data:
                logger.warning(f"Skipping failed scenario: {scenario_name}")
                continue
                
            logger.info(f"\nAnalyzing scenario: {scenario_name}")
            self.analyze_scenario(scenario_name, scenario_data)
            
    def analyze_scenario(self, scenario_name: str, scenario_data: Dict[str, Any]):
        """Analyze a single scenario"""
        # Extract metrics
        metrics = scenario_data.get("metrics", {})
        resource_usage = scenario_data.get("resource_usage", {})
        scenario_config = scenario_data.get("scenario", {})
        
        # Clear previous bottlenecks
        self.bottlenecks.clear()
        
        # Analyze different aspects
        self._analyze_throughput(metrics, scenario_config)
        self._analyze_response_times(metrics)
        self._analyze_error_rates(metrics)
        self._analyze_resource_usage(resource_usage)
        self._analyze_scalability(metrics, resource_usage, scenario_config)
        self._detect_anomalies(metrics, resource_usage)
        
        # Generate report for this scenario
        self._generate_scenario_report(scenario_name, scenario_data)
        
    def _analyze_throughput(self, metrics: Dict[str, Any], scenario_config: Dict[str, Any]):
        """Analyze throughput metrics"""
        throughput = metrics.get("throughput", 0)
        total_requests = metrics.get("total_requests", 0)
        max_clients = scenario_config.get("max_clients", 0)
        
        # Expected throughput based on client count and request delay
        request_delay_ms = scenario_config.get("request_delay_ms", 100)
        expected_throughput = (max_clients * 1000) / request_delay_ms
        
        # Check if throughput is significantly lower than expected
        throughput_ratio = throughput / expected_throughput if expected_throughput > 0 else 0
        
        if throughput_ratio < 0.5:
            self.bottlenecks.append(Bottleneck(
                type="application",
                severity="high" if throughput_ratio < 0.3 else "medium",
                description=f"Throughput is {(1-throughput_ratio)*100:.1f}% below expected",
                metrics={
                    "actual_throughput": throughput,
                    "expected_throughput": expected_throughput,
                    "throughput_ratio": throughput_ratio
                },
                recommendations=[
                    "Check for synchronization bottlenecks",
                    "Analyze request processing pipeline",
                    "Consider implementing request batching",
                    "Review connection pooling configuration"
                ],
                impact_score=80 * (1 - throughput_ratio)
            ))
            
    def _analyze_response_times(self, metrics: Dict[str, Any]):
        """Analyze response time metrics"""
        response_times = metrics.get("response_times", {})
        p50 = response_times.get("p50", 0)
        p95 = response_times.get("p95", 0)
        p99 = response_times.get("p99", 0)
        
        # Check for high response times
        if p95 > 1.0:  # More than 1 second
            severity = "critical" if p95 > 5.0 else "high" if p95 > 2.0 else "medium"
            
            self.bottlenecks.append(Bottleneck(
                type="application",
                severity=severity,
                description=f"High P95 response time: {p95:.2f}s",
                metrics={
                    "p50": p50,
                    "p95": p95,
                    "p99": p99,
                    "p95_to_p50_ratio": p95/p50 if p50 > 0 else 0
                },
                recommendations=[
                    "Profile slow request paths",
                    "Implement caching for frequent operations",
                    "Optimize Korean text processing",
                    "Consider async processing for heavy operations"
                ],
                impact_score=min(100, p95 * 20)
            ))
            
        # Check for high variance (p99 much higher than p95)
        if p99 > 0 and p95 > 0:
            variance_ratio = p99 / p95
            if variance_ratio > 3:
                self.bottlenecks.append(Bottleneck(
                    type="application",
                    severity="medium",
                    description=f"High response time variance (P99/P95 = {variance_ratio:.1f})",
                    metrics={
                        "variance_ratio": variance_ratio,
                        "p95": p95,
                        "p99": p99
                    },
                    recommendations=[
                        "Investigate outlier requests",
                        "Check for garbage collection pauses",
                        "Review timeout configurations",
                        "Analyze request queue behavior"
                    ],
                    impact_score=30 * min(variance_ratio / 3, 3)
                ))
                
    def _analyze_error_rates(self, metrics: Dict[str, Any]):
        """Analyze error rates and types"""
        error_rate = metrics.get("error_rate", 0)
        error_types = metrics.get("error_types", {})
        
        if error_rate > 5:  # More than 5% errors
            severity = "critical" if error_rate > 20 else "high" if error_rate > 10 else "medium"
            
            # Identify dominant error types
            dominant_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:3]
            
            recommendations = []
            
            # Specific recommendations based on error types
            for error_type, count in dominant_errors:
                if "timeout" in error_type.lower():
                    recommendations.extend([
                        "Increase timeout values",
                        "Optimize slow operations",
                        "Implement request prioritization"
                    ])
                elif "connection" in error_type.lower():
                    recommendations.extend([
                        "Increase connection pool size",
                        "Implement connection retry logic",
                        "Check network configuration"
                    ])
                elif "memory" in error_type.lower():
                    recommendations.extend([
                        "Increase memory allocation",
                        "Implement memory usage limits",
                        "Optimize data structures"
                    ])
                    
            self.bottlenecks.append(Bottleneck(
                type="reliability",
                severity=severity,
                description=f"High error rate: {error_rate:.1f}%",
                metrics={
                    "error_rate": error_rate,
                    "error_types": dict(dominant_errors),
                    "total_errors": metrics.get("failed_requests", 0)
                },
                recommendations=list(set(recommendations)),  # Remove duplicates
                impact_score=error_rate * 2
            ))
            
    def _analyze_resource_usage(self, resource_usage: Dict[str, Any]):
        """Analyze system resource usage"""
        if not resource_usage:
            return
            
        # CPU analysis
        cpu_data = resource_usage.get("cpu", {})
        cpu_mean = cpu_data.get("mean", 0)
        cpu_max = cpu_data.get("max", 0)
        
        if cpu_mean > 70:
            self.bottlenecks.append(Bottleneck(
                type="cpu",
                severity="high" if cpu_mean > 85 else "medium",
                description=f"High CPU usage: {cpu_mean:.1f}% average, {cpu_max:.1f}% peak",
                metrics={
                    "cpu_mean": cpu_mean,
                    "cpu_max": cpu_max,
                    "cpu_p95": cpu_data.get("p95", 0)
                },
                recommendations=[
                    "Profile CPU-intensive operations",
                    "Implement CPU-bound operation caching",
                    "Consider horizontal scaling",
                    "Optimize Korean NLP processing"
                ],
                impact_score=cpu_mean
            ))
            
        # Memory analysis
        memory_data = resource_usage.get("memory_mb", {})
        memory_mean = memory_data.get("mean", 0)
        memory_max = memory_data.get("max", 0)
        
        # Check for memory growth (potential leak)
        if memory_max > memory_mean * 1.5:
            self.bottlenecks.append(Bottleneck(
                type="memory",
                severity="high",
                description=f"Potential memory leak: {memory_mean:.1f}MB average, {memory_max:.1f}MB peak",
                metrics={
                    "memory_mean": memory_mean,
                    "memory_max": memory_max,
                    "growth_ratio": memory_max / memory_mean if memory_mean > 0 else 0
                },
                recommendations=[
                    "Investigate memory allocation patterns",
                    "Check for resource cleanup issues",
                    "Implement memory profiling",
                    "Review object lifecycle management"
                ],
                impact_score=50 * (memory_max / memory_mean - 1) if memory_mean > 0 else 0
            ))
            
        # Connection analysis
        connections = resource_usage.get("connections", {})
        conn_max = connections.get("max", 0)
        
        if conn_max > 500:
            self.bottlenecks.append(Bottleneck(
                type="network",
                severity="medium",
                description=f"High connection count: {conn_max} connections",
                metrics={
                    "connections_max": conn_max,
                    "connections_mean": connections.get("mean", 0)
                },
                recommendations=[
                    "Implement connection pooling",
                    "Review keep-alive settings",
                    "Consider connection limits",
                    "Optimize connection lifecycle"
                ],
                impact_score=min(100, conn_max / 10)
            ))
            
    def _analyze_scalability(self, metrics: Dict[str, Any], resource_usage: Dict[str, Any], 
                           scenario_config: Dict[str, Any]):
        """Analyze scalability characteristics"""
        max_clients = scenario_config.get("max_clients", 0)
        throughput = metrics.get("throughput", 0)
        cpu_mean = resource_usage.get("cpu", {}).get("mean", 0)
        
        if max_clients > 0 and throughput > 0 and cpu_mean > 0:
            # Calculate efficiency metrics
            throughput_per_client = throughput / max_clients
            cpu_per_throughput = cpu_mean / throughput
            
            # Check for poor scalability
            if cpu_per_throughput > 0.1:  # More than 0.1% CPU per request/second
                self.bottlenecks.append(Bottleneck(
                    type="scalability",
                    severity="medium",
                    description=f"Poor scalability: {cpu_per_throughput:.3f}% CPU per req/s",
                    metrics={
                        "throughput_per_client": throughput_per_client,
                        "cpu_per_throughput": cpu_per_throughput,
                        "max_sustainable_throughput": 100 / cpu_per_throughput
                    },
                    recommendations=[
                        "Implement request batching",
                        "Use async processing where possible",
                        "Consider microservice architecture",
                        "Optimize critical path operations"
                    ],
                    impact_score=min(100, cpu_per_throughput * 100)
                ))
                
    def _detect_anomalies(self, metrics: Dict[str, Any], resource_usage: Dict[str, Any]):
        """Detect anomalies in metrics"""
        # This would ideally use time-series data, but we'll check for obvious issues
        
        # Check for suspicious patterns
        error_types = metrics.get("error_types", {})
        
        # Look for specific error patterns
        if "JSON decode error" in error_types or "Invalid response format" in error_types:
            self.bottlenecks.append(Bottleneck(
                type="application",
                severity="high",
                description="Protocol/serialization errors detected",
                metrics={
                    "serialization_errors": sum(count for error, count in error_types.items() 
                                               if "json" in error.lower() or "decode" in error.lower())
                },
                recommendations=[
                    "Review protocol implementation",
                    "Add response validation",
                    "Implement proper error handling",
                    "Check for encoding issues with Korean text"
                ],
                impact_score=60
            ))
            
    def _generate_scenario_report(self, scenario_name: str, scenario_data: Dict[str, Any]):
        """Generate detailed report for a scenario"""
        print(f"\n{'='*80}")
        print(f"PERFORMANCE ANALYSIS: {scenario_name}")
        print(f"{'='*80}")
        
        # Summary metrics
        metrics = scenario_data.get("metrics", {})
        print(f"\nSummary Metrics:")
        print(f"  Total Requests: {metrics.get('total_requests', 0):,}")
        print(f"  Throughput: {metrics.get('throughput', 0):.2f} req/s")
        print(f"  Error Rate: {metrics.get('error_rate', 0):.2f}%")
        
        response_times = metrics.get("response_times", {})
        print(f"  Response Times:")
        print(f"    P50: {response_times.get('p50', 0)*1000:.0f}ms")
        print(f"    P95: {response_times.get('p95', 0)*1000:.0f}ms")
        print(f"    P99: {response_times.get('p99', 0)*1000:.0f}ms")
        
        # Bottlenecks
        if self.bottlenecks:
            print(f"\nIdentified Bottlenecks ({len(self.bottlenecks)}):")
            
            # Sort by impact score
            sorted_bottlenecks = sorted(self.bottlenecks, key=lambda b: b.impact_score, reverse=True)
            
            for i, bottleneck in enumerate(sorted_bottlenecks, 1):
                print(f"\n{i}. {bottleneck.type.upper()} - {bottleneck.severity.upper()}")
                print(f"   Description: {bottleneck.description}")
                print(f"   Impact Score: {bottleneck.impact_score:.1f}/100")
                print(f"   Key Metrics:")
                for key, value in bottleneck.metrics.items():
                    if isinstance(value, float):
                        print(f"     - {key}: {value:.2f}")
                    else:
                        print(f"     - {key}: {value}")
                print(f"   Recommendations:")
                for rec in bottleneck.recommendations[:3]:  # Top 3 recommendations
                    print(f"     • {rec}")
        else:
            print("\nNo significant bottlenecks detected.")
            
    def generate_comparison_report(self):
        """Generate comparison report across all scenarios"""
        print(f"\n{'='*80}")
        print("CROSS-SCENARIO COMPARISON")
        print(f"{'='*80}")
        
        # Collect metrics for comparison
        comparison_data = []
        
        for scenario_name, scenario_data in self.test_data.items():
            if "error" in scenario_data:
                continue
                
            metrics = scenario_data.get("metrics", {})
            resource_usage = scenario_data.get("resource_usage", {})
            
            comparison_data.append({
                "scenario": scenario_name,
                "throughput": metrics.get("throughput", 0),
                "error_rate": metrics.get("error_rate", 0),
                "p95_response": metrics.get("response_times", {}).get("p95", 0),
                "cpu_mean": resource_usage.get("cpu", {}).get("mean", 0),
                "memory_max": resource_usage.get("memory_mb", {}).get("max", 0)
            })
            
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            
            # Find best and worst performers
            print("\nBest Performers:")
            print(f"  Highest Throughput: {df.loc[df['throughput'].idxmax(), 'scenario']} "
                  f"({df['throughput'].max():.2f} req/s)")
            print(f"  Lowest Error Rate: {df.loc[df['error_rate'].idxmin(), 'scenario']} "
                  f"({df['error_rate'].min():.2f}%)")
            print(f"  Fastest P95: {df.loc[df['p95_response'].idxmin(), 'scenario']} "
                  f"({df['p95_response'].min()*1000:.0f}ms)")
            
            print("\nWorst Performers:")
            print(f"  Lowest Throughput: {df.loc[df['throughput'].idxmin(), 'scenario']} "
                  f"({df['throughput'].min():.2f} req/s)")
            print(f"  Highest Error Rate: {df.loc[df['error_rate'].idxmax(), 'scenario']} "
                  f"({df['error_rate'].max():.2f}%)")
            print(f"  Slowest P95: {df.loc[df['p95_response'].idxmax(), 'scenario']} "
                  f"({df['p95_response'].max()*1000:.0f}ms)")
            
    def generate_optimization_recommendations(self):
        """Generate overall optimization recommendations"""
        print(f"\n{'='*80}")
        print("OPTIMIZATION RECOMMENDATIONS")
        print(f"{'='*80}")
        
        # Collect all bottlenecks across scenarios
        all_bottlenecks = []
        
        for scenario_name, scenario_data in self.test_data.items():
            if "error" not in scenario_data:
                self.analyze_scenario(scenario_name, scenario_data)
                all_bottlenecks.extend(self.bottlenecks)
                
        # Group by type and severity
        bottleneck_summary = {}
        for bottleneck in all_bottlenecks:
            key = (bottleneck.type, bottleneck.severity)
            if key not in bottleneck_summary:
                bottleneck_summary[key] = {
                    "count": 0,
                    "total_impact": 0,
                    "recommendations": set()
                }
            bottleneck_summary[key]["count"] += 1
            bottleneck_summary[key]["total_impact"] += bottleneck.impact_score
            bottleneck_summary[key]["recommendations"].update(bottleneck.recommendations)
            
        # Generate prioritized recommendations
        priorities = []
        for (btype, severity), data in bottleneck_summary.items():
            avg_impact = data["total_impact"] / data["count"]
            priority_score = avg_impact * (4 if severity == "critical" else 3 if severity == "high" else 2 if severity == "medium" else 1)
            priorities.append({
                "type": btype,
                "severity": severity,
                "occurrences": data["count"],
                "avg_impact": avg_impact,
                "priority_score": priority_score,
                "recommendations": list(data["recommendations"])[:5]  # Top 5
            })
            
        # Sort by priority
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        print("\nTop Priority Optimizations:")
        for i, priority in enumerate(priorities[:5], 1):
            print(f"\n{i}. {priority['type'].upper()} Issues ({priority['severity'].upper()})")
            print(f"   Occurrences: {priority['occurrences']}")
            print(f"   Average Impact: {priority['avg_impact']:.1f}/100")
            print(f"   Key Recommendations:")
            for rec in priority['recommendations'][:3]:
                print(f"     • {rec}")
                
        # Specific optimization strategies
        print("\n\nDetailed Optimization Strategy:")
        
        print("\n1. IMMEDIATE ACTIONS (Quick Wins):")
        print("   • Increase connection pool sizes")
        print("   • Adjust timeout values based on P95 response times")
        print("   • Enable connection keep-alive")
        print("   • Implement basic request caching")
        
        print("\n2. SHORT-TERM OPTIMIZATIONS (1-2 weeks):")
        print("   • Profile and optimize Korean text processing")
        print("   • Implement request batching for high-volume scenarios")
        print("   • Add circuit breakers for failing operations")
        print("   • Optimize memory allocation patterns")
        
        print("\n3. LONG-TERM IMPROVEMENTS (1-3 months):")
        print("   • Redesign architecture for horizontal scaling")
        print("   • Implement async processing for heavy operations")
        print("   • Add comprehensive monitoring and alerting")
        print("   • Consider microservice decomposition for bottleneck components")
        
    def save_analysis_report(self, output_path: str):
        """Save complete analysis report"""
        report_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "test_results_file": str(self.test_results_path),
            "scenarios_analyzed": len(self.test_data),
            "total_bottlenecks": sum(len(self.bottlenecks) for _ in self.test_data.values()),
            "bottleneck_summary": {},
            "recommendations": []
        }
        
        # Analyze all scenarios
        for scenario_name, scenario_data in self.test_data.items():
            if "error" not in scenario_data:
                self.analyze_scenario(scenario_name, scenario_data)
                report_data["bottleneck_summary"][scenario_name] = [
                    {
                        "type": b.type,
                        "severity": b.severity,
                        "description": b.description,
                        "impact_score": b.impact_score,
                        "recommendations": b.recommendations
                    }
                    for b in self.bottlenecks
                ]
                
        # Save report
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        logger.info(f"Analysis report saved to {output_path}")


def visualize_performance_data(test_results_path: str, output_dir: str = "performance_plots"):
    """Create visualizations of performance data"""
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Load test results
    with open(test_results_path, 'r') as f:
        test_data = json.load(f)
        
    # Prepare data for visualization
    scenarios = []
    throughputs = []
    error_rates = []
    p95_responses = []
    cpu_usage = []
    
    for scenario_name, scenario_data in test_data.items():
        if "error" not in scenario_data:
            metrics = scenario_data.get("metrics", {})
            resources = scenario_data.get("resource_usage", {})
            
            scenarios.append(scenario_name)
            throughputs.append(metrics.get("throughput", 0))
            error_rates.append(metrics.get("error_rate", 0))
            p95_responses.append(metrics.get("response_times", {}).get("p95", 0) * 1000)  # Convert to ms
            cpu_usage.append(resources.get("cpu", {}).get("mean", 0))
            
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("Performance Test Results Overview", fontsize=16)
    
    # Throughput comparison
    ax1 = axes[0, 0]
    ax1.bar(range(len(scenarios)), throughputs, color='blue', alpha=0.7)
    ax1.set_xlabel("Scenario")
    ax1.set_ylabel("Throughput (req/s)")
    ax1.set_title("Throughput by Scenario")
    ax1.set_xticks(range(len(scenarios)))
    ax1.set_xticklabels(scenarios, rotation=45, ha='right')
    
    # Error rates
    ax2 = axes[0, 1]
    ax2.bar(range(len(scenarios)), error_rates, color='red', alpha=0.7)
    ax2.set_xlabel("Scenario")
    ax2.set_ylabel("Error Rate (%)")
    ax2.set_title("Error Rates by Scenario")
    ax2.set_xticks(range(len(scenarios)))
    ax2.set_xticklabels(scenarios, rotation=45, ha='right')
    
    # Response times
    ax3 = axes[1, 0]
    ax3.bar(range(len(scenarios)), p95_responses, color='green', alpha=0.7)
    ax3.set_xlabel("Scenario")
    ax3.set_ylabel("P95 Response Time (ms)")
    ax3.set_title("P95 Response Times by Scenario")
    ax3.set_xticks(range(len(scenarios)))
    ax3.set_xticklabels(scenarios, rotation=45, ha='right')
    
    # CPU usage
    ax4 = axes[1, 1]
    ax4.bar(range(len(scenarios)), cpu_usage, color='orange', alpha=0.7)
    ax4.set_xlabel("Scenario")
    ax4.set_ylabel("Average CPU Usage (%)")
    ax4.set_title("CPU Usage by Scenario")
    ax4.set_xticks(range(len(scenarios)))
    ax4.set_xticklabels(scenarios, rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_dir / "performance_overview.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create correlation heatmap
    if len(scenarios) > 1:
        plt.figure(figsize=(10, 8))
        
        # Create correlation matrix
        data = pd.DataFrame({
            "Throughput": throughputs,
            "Error Rate": error_rates,
            "P95 Response": p95_responses,
            "CPU Usage": cpu_usage
        })
        
        correlation = data.corr()
        
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title("Performance Metrics Correlation")
        plt.tight_layout()
        plt.savefig(output_dir / "metrics_correlation.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    logger.info(f"Visualizations saved to {output_dir}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Analyzer for Stress Test Results")
    parser.add_argument("results_file", help="Path to stress test results JSON file")
    parser.add_argument("--output", default="performance_analysis.json", 
                       help="Output file for analysis report")
    parser.add_argument("--visualize", action="store_true", 
                       help="Generate performance visualizations")
    parser.add_argument("--plot-dir", default="performance_plots",
                       help="Directory for visualization outputs")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = PerformanceAnalyzer(args.results_file)
    
    # Load and analyze data
    analyzer.load_test_results()
    analyzer.analyze_all_scenarios()
    
    # Generate reports
    analyzer.generate_comparison_report()
    analyzer.generate_optimization_recommendations()
    
    # Save analysis
    analyzer.save_analysis_report(args.output)
    
    # Generate visualizations if requested
    if args.visualize:
        visualize_performance_data(args.results_file, args.plot_dir)


if __name__ == "__main__":
    main()