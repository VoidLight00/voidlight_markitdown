#!/usr/bin/env python3
"""
MCP Performance Test Client
Tests server performance, resource usage, and scalability
"""

import asyncio
import json
import logging
import os
import psutil
import statistics
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
import matplotlib.pyplot as plt
import numpy as np
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance measurement result"""
    test_name: str
    metric_type: str  # 'latency', 'throughput', 'memory', 'cpu'
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'test_name': self.test_name,
            'metric_type': self.metric_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp
        }


@dataclass
class PerformanceTestResult:
    """Complete performance test result"""
    test_name: str
    duration: float
    metrics: List[PerformanceMetric]
    success_rate: float
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'test_name': self.test_name,
            'duration': self.duration,
            'metrics': [m.to_dict() for m in self.metrics],
            'success_rate': self.success_rate,
            'errors': self.errors
        }


class PerformanceTestClient:
    """Comprehensive performance testing for MCP server"""
    
    def __init__(self, report_dir: Path):
        self.report_dir = report_dir
        self.metrics_dir = report_dir / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.test_results: List[PerformanceTestResult] = []
    
    async def _measure_server_resources(self, pid: int) -> Dict[str, float]:
        """Measure server process resource usage"""
        try:
            process = psutil.Process(pid)
            
            # CPU usage (percentage)
            cpu_percent = process.cpu_percent(interval=0.1)
            
            # Memory usage (MB)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Open file descriptors
            num_fds = len(process.open_files())
            
            # Thread count
            num_threads = process.num_threads()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'file_descriptors': num_fds,
                'threads': num_threads
            }
        except:
            return {}
    
    async def test_latency_profile(self) -> PerformanceTestResult:
        """Test request latency under various conditions"""
        test_name = "Latency Profile Test"
        logger.info(f"Running {test_name}...")
        
        metrics = []
        errors = []
        latencies = []
        
        try:
            # Start server
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "voidlight_markitdown_mcp"],
                env={
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "WARNING"  # Reduce logging overhead
                }
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Test different payload sizes
                    test_cases = [
                        ("Small", "https://httpbin.org/html"),  # ~3KB
                        ("Medium", "https://www.example.com"),   # ~1KB
                        ("Text", "data:text/plain;base64,SGVsbG8gV29ybGQ="),  # Direct data
                    ]
                    
                    for case_name, uri in test_cases:
                        case_latencies = []
                        
                        # Warm-up
                        await session.call_tool("convert_to_markdown", {"uri": uri})
                        
                        # Measure latency (10 requests)
                        for i in range(10):
                            start_time = time.time()
                            try:
                                await session.call_tool("convert_to_markdown", {"uri": uri})
                                latency = (time.time() - start_time) * 1000  # ms
                                case_latencies.append(latency)
                                latencies.append(latency)
                            except Exception as e:
                                errors.append(f"{case_name} request {i}: {str(e)}")
                        
                        if case_latencies:
                            # Calculate statistics
                            metrics.append(PerformanceMetric(
                                test_name=f"{test_name} - {case_name}",
                                metric_type="latency",
                                value=statistics.mean(case_latencies),
                                unit="ms"
                            ))
                            
                            metrics.append(PerformanceMetric(
                                test_name=f"{test_name} - {case_name} P95",
                                metric_type="latency",
                                value=np.percentile(case_latencies, 95),
                                unit="ms"
                            ))
            
            success_rate = (len(latencies) / (len(test_cases) * 10)) * 100 if test_cases else 0
            
            return PerformanceTestResult(
                test_name=test_name,
                duration=sum(latencies) / 1000 if latencies else 0,
                metrics=metrics,
                success_rate=success_rate,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                duration=0,
                metrics=metrics,
                success_rate=0,
                errors=[str(e)]
            )
    
    async def test_throughput(self) -> PerformanceTestResult:
        """Test maximum throughput (requests per second)"""
        test_name = "Throughput Test"
        logger.info(f"Running {test_name}...")
        
        metrics = []
        errors = []
        
        try:
            # Start server
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "voidlight_markitdown_mcp"],
                env={
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "WARNING"
                }
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Test URI (small payload for throughput testing)
                    test_uri = "data:text/plain;base64,VGhyb3VnaHB1dCB0ZXN0"
                    
                    # Warm-up
                    await session.call_tool("convert_to_markdown", {"uri": test_uri})
                    
                    # Measure throughput for different concurrency levels
                    concurrency_levels = [1, 5, 10, 20]
                    
                    for concurrency in concurrency_levels:
                        logger.info(f"  Testing concurrency level: {concurrency}")
                        
                        async def make_request():
                            try:
                                await session.call_tool("convert_to_markdown", {"uri": test_uri})
                                return True
                            except:
                                return False
                        
                        # Run for 10 seconds
                        start_time = time.time()
                        request_count = 0
                        success_count = 0
                        
                        while time.time() - start_time < 10:
                            # Create concurrent requests
                            tasks = [make_request() for _ in range(concurrency)]
                            results = await asyncio.gather(*tasks)
                            
                            request_count += len(results)
                            success_count += sum(1 for r in results if r)
                        
                        duration = time.time() - start_time
                        rps = request_count / duration
                        success_rate = (success_count / request_count * 100) if request_count > 0 else 0
                        
                        metrics.append(PerformanceMetric(
                            test_name=f"{test_name} - Concurrency {concurrency}",
                            metric_type="throughput",
                            value=rps,
                            unit="requests/second"
                        ))
                        
                        logger.info(f"    RPS: {rps:.2f}, Success rate: {success_rate:.1f}%")
            
            return PerformanceTestResult(
                test_name=test_name,
                duration=40,  # Total test duration
                metrics=metrics,
                success_rate=100,  # Overall test success
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                duration=0,
                metrics=metrics,
                success_rate=0,
                errors=[str(e)]
            )
    
    async def test_resource_usage(self) -> PerformanceTestResult:
        """Test server resource usage under load"""
        test_name = "Resource Usage Test"
        logger.info(f"Running {test_name}...")
        
        metrics = []
        errors = []
        
        try:
            # Start server as subprocess to monitor
            server_process = subprocess.Popen(
                ["python", "-m", "voidlight_markitdown_mcp"],
                env={
                    **os.environ,
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "WARNING"
                }
            )
            
            # Wait for startup
            await asyncio.sleep(2)
            
            # Connect client
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "voidlight_markitdown_mcp"],
                env={
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "WARNING"
                }
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Monitor resources during different load levels
                    resource_samples = []
                    
                    # Idle state
                    logger.info("  Measuring idle resources...")
                    for _ in range(5):
                        resources = await self._measure_server_resources(server_process.pid)
                        if resources:
                            resource_samples.append(('idle', resources))
                        await asyncio.sleep(1)
                    
                    # Light load
                    logger.info("  Measuring light load resources...")
                    light_load_task = asyncio.create_task(self._generate_load(session, 1, 10))
                    for _ in range(10):
                        resources = await self._measure_server_resources(server_process.pid)
                        if resources:
                            resource_samples.append(('light', resources))
                        await asyncio.sleep(1)
                    await light_load_task
                    
                    # Heavy load
                    logger.info("  Measuring heavy load resources...")
                    heavy_load_task = asyncio.create_task(self._generate_load(session, 10, 10))
                    for _ in range(10):
                        resources = await self._measure_server_resources(server_process.pid)
                        if resources:
                            resource_samples.append(('heavy', resources))
                        await asyncio.sleep(1)
                    await heavy_load_task
                    
                    # Process samples
                    for load_type in ['idle', 'light', 'heavy']:
                        samples = [s[1] for s in resource_samples if s[0] == load_type]
                        if samples:
                            metrics.append(PerformanceMetric(
                                test_name=f"{test_name} - {load_type.title()} CPU",
                                metric_type="cpu",
                                value=statistics.mean(s['cpu_percent'] for s in samples),
                                unit="percent"
                            ))
                            
                            metrics.append(PerformanceMetric(
                                test_name=f"{test_name} - {load_type.title()} Memory",
                                metric_type="memory",
                                value=statistics.mean(s['memory_mb'] for s in samples),
                                unit="MB"
                            ))
            
            # Clean up
            server_process.terminate()
            server_process.wait()
            
            return PerformanceTestResult(
                test_name=test_name,
                duration=25,
                metrics=metrics,
                success_rate=100,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            if 'server_process' in locals():
                server_process.terminate()
            return PerformanceTestResult(
                test_name=test_name,
                duration=0,
                metrics=metrics,
                success_rate=0,
                errors=[str(e)]
            )
    
    async def _generate_load(self, session: ClientSession, concurrency: int, duration: int):
        """Generate load on the server"""
        test_uri = "data:text/plain;base64,TG9hZCB0ZXN0IGRhdGE="
        
        async def make_request():
            try:
                await session.call_tool("convert_to_markdown", {"uri": test_uri})
            except:
                pass
        
        end_time = time.time() + duration
        while time.time() < end_time:
            tasks = [make_request() for _ in range(concurrency)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.1)
    
    async def test_memory_leak(self) -> PerformanceTestResult:
        """Test for memory leaks during extended operation"""
        test_name = "Memory Leak Test"
        logger.info(f"Running {test_name}...")
        
        metrics = []
        errors = []
        
        try:
            # Start server as subprocess
            server_process = subprocess.Popen(
                ["python", "-m", "voidlight_markitdown_mcp"],
                env={
                    **os.environ,
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "WARNING"
                }
            )
            
            await asyncio.sleep(2)
            
            # Connect client
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "voidlight_markitdown_mcp"],
                env={
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "WARNING"
                }
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    memory_samples = []
                    
                    # Run for 60 seconds, making continuous requests
                    logger.info("  Running memory leak test for 60 seconds...")
                    start_time = time.time()
                    request_count = 0
                    
                    while time.time() - start_time < 60:
                        # Make request
                        try:
                            await session.call_tool(
                                "convert_to_markdown",
                                {"uri": "https://httpbin.org/uuid"}
                            )
                            request_count += 1
                        except:
                            pass
                        
                        # Sample memory every 5 seconds
                        if int(time.time() - start_time) % 5 == 0:
                            resources = await self._measure_server_resources(server_process.pid)
                            if resources:
                                memory_samples.append(resources['memory_mb'])
                        
                        await asyncio.sleep(0.1)
                    
                    # Analyze memory trend
                    if len(memory_samples) > 2:
                        # Calculate linear regression
                        x = np.arange(len(memory_samples))
                        slope, intercept = np.polyfit(x, memory_samples, 1)
                        
                        # Memory growth rate (MB per minute)
                        growth_rate = slope * 12  # 12 samples per minute
                        
                        metrics.append(PerformanceMetric(
                            test_name=f"{test_name} - Initial Memory",
                            metric_type="memory",
                            value=memory_samples[0],
                            unit="MB"
                        ))
                        
                        metrics.append(PerformanceMetric(
                            test_name=f"{test_name} - Final Memory",
                            metric_type="memory",
                            value=memory_samples[-1],
                            unit="MB"
                        ))
                        
                        metrics.append(PerformanceMetric(
                            test_name=f"{test_name} - Memory Growth Rate",
                            metric_type="memory",
                            value=growth_rate,
                            unit="MB/minute"
                        ))
                        
                        # Check if there's a significant leak
                        if growth_rate > 1.0:  # More than 1MB/minute growth
                            errors.append(f"Potential memory leak detected: {growth_rate:.2f} MB/minute")
            
            # Clean up
            server_process.terminate()
            server_process.wait()
            
            return PerformanceTestResult(
                test_name=test_name,
                duration=60,
                metrics=metrics,
                success_rate=100 if not errors else 90,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            if 'server_process' in locals():
                server_process.terminate()
            return PerformanceTestResult(
                test_name=test_name,
                duration=0,
                metrics=metrics,
                success_rate=0,
                errors=[str(e)]
            )
    
    async def test_korean_performance(self) -> PerformanceTestResult:
        """Test performance with Korean text processing"""
        test_name = "Korean Text Performance Test"
        logger.info(f"Running {test_name}...")
        
        metrics = []
        errors = []
        
        try:
            # Create Korean test files of different sizes
            test_files = []
            test_dir = self.report_dir.parent / "test_files"
            test_dir.mkdir(exist_ok=True)
            
            # Small Korean file (1KB)
            small_file = test_dir / "korean_small.txt"
            small_content = "안녕하세요! " * 50
            small_file.write_text(small_content, encoding='utf-8')
            test_files.append(("Small", small_file))
            
            # Medium Korean file (10KB)
            medium_file = test_dir / "korean_medium.txt"
            medium_content = """
# 한국어 문서 테스트

이것은 중간 크기의 한국어 문서입니다.

## 섹션 1
한국어 텍스트 처리 성능을 테스트하기 위한 문서입니다.
다양한 한글 문자와 특수 기호를 포함합니다: !@#$%^&*()

### 하위 섹션
- 첫 번째 항목
- 두 번째 항목
- 세 번째 항목

""" * 20
            medium_file.write_text(medium_content, encoding='utf-8')
            test_files.append(("Medium", medium_file))
            
            # Start server
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "voidlight_markitdown_mcp"],
                env={
                    "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                    "VOIDLIGHT_LOG_LEVEL": "WARNING"
                }
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    for size_name, test_file in test_files:
                        file_uri = f"file://{test_file.absolute()}"
                        processing_times = []
                        
                        # Warm-up
                        await session.call_tool("convert_korean_document", {
                            "uri": file_uri,
                            "normalize_korean": True
                        })
                        
                        # Measure performance (10 iterations)
                        for _ in range(10):
                            start_time = time.time()
                            try:
                                result = await session.call_tool("convert_korean_document", {
                                    "uri": file_uri,
                                    "normalize_korean": True
                                })
                                processing_time = (time.time() - start_time) * 1000  # ms
                                processing_times.append(processing_time)
                            except Exception as e:
                                errors.append(f"{size_name} Korean processing: {str(e)}")
                        
                        if processing_times:
                            metrics.append(PerformanceMetric(
                                test_name=f"{test_name} - {size_name} Average",
                                metric_type="latency",
                                value=statistics.mean(processing_times),
                                unit="ms"
                            ))
                            
                            metrics.append(PerformanceMetric(
                                test_name=f"{test_name} - {size_name} P95",
                                metric_type="latency",
                                value=np.percentile(processing_times, 95),
                                unit="ms"
                            ))
            
            return PerformanceTestResult(
                test_name=test_name,
                duration=sum(sum(pt for pt in processing_times) for _, processing_times in locals().items() if isinstance(processing_times, list)) / 1000,
                metrics=metrics,
                success_rate=100 - (len(errors) * 10),
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                duration=0,
                metrics=metrics,
                success_rate=0,
                errors=[str(e)]
            )
    
    def _generate_performance_charts(self, results: List[PerformanceTestResult]):
        """Generate performance visualization charts"""
        logger.info("Generating performance charts...")
        
        # Latency distribution chart
        latency_metrics = []
        for result in results:
            for metric in result.metrics:
                if metric.metric_type == "latency" and "P95" not in metric.test_name:
                    latency_metrics.append(metric)
        
        if latency_metrics:
            plt.figure(figsize=(10, 6))
            names = [m.test_name.split(" - ")[-1] for m in latency_metrics]
            values = [m.value for m in latency_metrics]
            
            plt.bar(names, values)
            plt.xlabel('Test Case')
            plt.ylabel('Latency (ms)')
            plt.title('Average Request Latency by Test Case')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = self.metrics_dir / "latency_distribution.png"
            plt.savefig(chart_path)
            plt.close()
            logger.info(f"  Saved latency chart to {chart_path}")
        
        # Throughput chart
        throughput_metrics = []
        for result in results:
            for metric in result.metrics:
                if metric.metric_type == "throughput":
                    throughput_metrics.append(metric)
        
        if throughput_metrics:
            plt.figure(figsize=(10, 6))
            concurrency = [int(m.test_name.split("Concurrency ")[-1]) for m in throughput_metrics]
            rps = [m.value for m in throughput_metrics]
            
            plt.plot(concurrency, rps, marker='o')
            plt.xlabel('Concurrency Level')
            plt.ylabel('Requests per Second')
            plt.title('Throughput vs Concurrency')
            plt.grid(True)
            plt.tight_layout()
            
            chart_path = self.metrics_dir / "throughput_curve.png"
            plt.savefig(chart_path)
            plt.close()
            logger.info(f"  Saved throughput chart to {chart_path}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        logger.info("Starting comprehensive MCP performance tests...\n")
        
        test_suites = [
            ("Latency Tests", self.test_latency_profile),
            ("Throughput Tests", self.test_throughput),
            ("Resource Usage Tests", self.test_resource_usage),
            ("Memory Leak Tests", self.test_memory_leak),
            ("Korean Performance Tests", self.test_korean_performance)
        ]
        
        all_results = []
        
        for suite_name, test_func in test_suites:
            logger.info(f"\nRunning {suite_name}...")
            try:
                result = await test_func()
                all_results.append(result)
                self.test_results.append(result)
                
                # Log summary
                logger.info(f"  Completed: {result.success_rate:.1f}% success rate")
                if result.errors:
                    logger.warning(f"  Errors: {len(result.errors)}")
                
            except Exception as e:
                logger.error(f"{suite_name} failed: {e}")
        
        # Generate charts
        self._generate_performance_charts(all_results)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(all_results),
                'total_duration': sum(r.duration for r in all_results),
                'average_success_rate': statistics.mean(r.success_rate for r in all_results) if all_results else 0
            },
            'test_results': [r.to_dict() for r in all_results],
            'performance_summary': self._generate_performance_summary(all_results)
        }
        
        # Save report
        report_file = self.report_dir / f"performance_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\nPerformance report saved to: {report_file}")
        
        return report
    
    def _generate_performance_summary(self, results: List[PerformanceTestResult]) -> Dict[str, Any]:
        """Generate performance summary statistics"""
        summary = {
            'latency': {},
            'throughput': {},
            'resource_usage': {},
            'recommendations': []
        }
        
        # Analyze latency
        latency_values = []
        for result in results:
            for metric in result.metrics:
                if metric.metric_type == "latency" and "Average" in metric.test_name:
                    latency_values.append(metric.value)
        
        if latency_values:
            summary['latency'] = {
                'average_ms': statistics.mean(latency_values),
                'min_ms': min(latency_values),
                'max_ms': max(latency_values)
            }
            
            if summary['latency']['average_ms'] > 100:
                summary['recommendations'].append(
                    "Average latency is high (>100ms). Consider optimizing conversion logic."
                )
        
        # Analyze throughput
        throughput_values = []
        for result in results:
            for metric in result.metrics:
                if metric.metric_type == "throughput":
                    throughput_values.append(metric.value)
        
        if throughput_values:
            summary['throughput'] = {
                'max_rps': max(throughput_values),
                'scalability_factor': max(throughput_values) / min(throughput_values) if min(throughput_values) > 0 else 0
            }
            
            if summary['throughput']['max_rps'] < 50:
                summary['recommendations'].append(
                    "Maximum throughput is low (<50 RPS). Consider async processing or caching."
                )
        
        # Analyze resource usage
        memory_values = []
        cpu_values = []
        for result in results:
            for metric in result.metrics:
                if metric.metric_type == "memory":
                    memory_values.append(metric.value)
                elif metric.metric_type == "cpu":
                    cpu_values.append(metric.value)
        
        if memory_values:
            summary['resource_usage']['memory_mb'] = {
                'average': statistics.mean(memory_values),
                'max': max(memory_values)
            }
        
        if cpu_values:
            summary['resource_usage']['cpu_percent'] = {
                'average': statistics.mean(cpu_values),
                'max': max(cpu_values)
            }
            
            if summary['resource_usage']['cpu_percent']['max'] > 80:
                summary['recommendations'].append(
                    "High CPU usage detected (>80%). Consider optimizing CPU-intensive operations."
                )
        
        return summary


async def main():
    """Main performance test runner"""
    report_dir = Path("/Users/voidlight/voidlight_markitdown/mcp_client_tests/reports")
    report_dir.mkdir(exist_ok=True)
    
    client = PerformanceTestClient(report_dir)
    report = await client.run_all_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("MCP PERFORMANCE TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Total Duration: {report['summary']['total_duration']:.2f}s")
    print(f"Average Success Rate: {report['summary']['average_success_rate']:.1f}%")
    
    perf_summary = report['performance_summary']
    if perf_summary.get('latency'):
        print(f"\nLatency: {perf_summary['latency']['average_ms']:.2f}ms average")
    if perf_summary.get('throughput'):
        print(f"Max Throughput: {perf_summary['throughput']['max_rps']:.2f} RPS")
    
    if perf_summary.get('recommendations'):
        print("\nRecommendations:")
        for rec in perf_summary['recommendations']:
            print(f"  - {rec}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())