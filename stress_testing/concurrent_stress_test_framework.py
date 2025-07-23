#!/usr/bin/env python3
"""
Comprehensive Concurrent Stress Testing Framework for VoidLight MarkItDown MCP Server
Designed to test concurrent access patterns, resource management, and failure modes.
"""

import asyncio
import json
import time
import os
import sys
import subprocess
import signal
import psutil
import threading
import queue
import random
import tempfile
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path
import aiohttp
import websockets
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np

# Test Configuration
MCP_ENV_PATH = "/Users/voidlight/voidlight_markitdown/mcp-env"
MCP_SERVER_BIN = f"{MCP_ENV_PATH}/bin/voidlight-markitdown-mcp"
BASE_PORT = 3001
MAX_PORTS = 10  # For testing multiple server instances

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stress_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LoadPattern(Enum):
    """Different load patterns for testing"""
    GRADUAL_RAMP = "gradual_ramp"
    SPIKE = "spike"
    SUSTAINED = "sustained"
    WAVE = "wave"
    STRESS_TO_FAILURE = "stress_to_failure"
    RANDOM = "random"


class ClientType(Enum):
    """Types of clients for testing"""
    STDIO = "stdio"
    HTTP_SSE = "http_sse"
    WEBSOCKET = "websocket"
    MIXED = "mixed"


@dataclass
class TestMetrics:
    """Metrics collected during testing"""
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    response_times: List[float] = field(default_factory=list)
    error_types: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Resource metrics
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    open_files: List[int] = field(default_factory=list)
    active_connections: List[int] = field(default_factory=list)
    
    # Percentile calculations
    def get_percentiles(self) -> Dict[str, float]:
        """Calculate response time percentiles"""
        if not self.response_times:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        sorted_times = sorted(self.response_times)
        return {
            "p50": np.percentile(sorted_times, 50),
            "p95": np.percentile(sorted_times, 95),
            "p99": np.percentile(sorted_times, 99),
            "mean": statistics.mean(sorted_times),
            "stdev": statistics.stdev(sorted_times) if len(sorted_times) > 1 else 0
        }
    
    def get_throughput(self, duration_seconds: float) -> float:
        """Calculate requests per second"""
        return self.request_count / duration_seconds if duration_seconds > 0 else 0
    
    def get_error_rate(self) -> float:
        """Calculate error rate percentage"""
        return (self.error_count / self.request_count * 100) if self.request_count > 0 else 0


@dataclass
class TestScenario:
    """Configuration for a test scenario"""
    name: str
    load_pattern: LoadPattern
    client_type: ClientType
    initial_clients: int
    max_clients: int
    duration_seconds: int
    ramp_up_seconds: int = 30
    request_delay_ms: int = 100
    payload_size: str = "small"  # small, medium, large, extreme
    korean_ratio: float = 0.5  # Ratio of Korean text requests
    error_injection_rate: float = 0.05  # 5% error injection
    connection_timeout: int = 30
    request_timeout: int = 60


class ResourceMonitor:
    """Monitor system resources during testing"""
    
    def __init__(self, pid: Optional[int] = None):
        self.pid = pid
        self.process = psutil.Process(pid) if pid else None
        self.monitoring = False
        self.metrics_queue = queue.Queue()
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = {
                    "timestamp": time.time(),
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "open_files": len(psutil.Process().open_files()) if self.process else 0,
                }
                
                if self.process and self.process.is_running():
                    metrics.update({
                        "process_cpu": self.process.cpu_percent(),
                        "process_memory": self.process.memory_info().rss / 1024 / 1024,  # MB
                        "process_threads": self.process.num_threads(),
                        "process_connections": len(self.process.connections()),
                    })
                
                self.metrics_queue.put(metrics)
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
            
            time.sleep(1)  # Monitor every second
    
    def get_metrics(self) -> List[Dict]:
        """Get all collected metrics"""
        metrics = []
        while not self.metrics_queue.empty():
            metrics.append(self.metrics_queue.get())
        return metrics


class MCPServerManager:
    """Manage MCP server lifecycle for testing"""
    
    def __init__(self, port: int = BASE_PORT):
        self.port = port
        self.process = None
        self.pid = None
        
    def start_server(self, mode: str = "http") -> bool:
        """Start MCP server in specified mode"""
        try:
            env = os.environ.copy()
            env["VOIDLIGHT_LOG_LEVEL"] = "INFO"
            env["VOIDLIGHT_LOG_FILE"] = f"mcp_server_{self.port}.log"
            
            cmd = [MCP_SERVER_BIN]
            if mode == "http":
                cmd.extend(["--http", "--port", str(self.port)])
            
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if sys.platform != "win32" else None
            )
            
            self.pid = self.process.pid
            time.sleep(2)  # Give server time to start
            
            # Verify server is running
            if mode == "http":
                try:
                    response = requests.get(f"http://localhost:{self.port}/health", timeout=5)
                    return response.status_code == 200
                except:
                    # Server might not have health endpoint, check process
                    return self.process.poll() is None
            
            return self.process.poll() is None
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop MCP server"""
        if self.process:
            try:
                if sys.platform == "win32":
                    self.process.terminate()
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            finally:
                self.process = None
                self.pid = None


class StressTestClient:
    """Base class for stress test clients"""
    
    def __init__(self, client_id: int, scenario: TestScenario):
        self.client_id = client_id
        self.scenario = scenario
        self.metrics = TestMetrics()
        self.running = False
        self.session = None
        
    async def connect(self):
        """Establish connection to server"""
        raise NotImplementedError
        
    async def disconnect(self):
        """Close connection to server"""
        raise NotImplementedError
        
    async def send_request(self, payload: Dict[str, Any]) -> Tuple[bool, float, Optional[str]]:
        """Send request and return (success, response_time, error_message)"""
        raise NotImplementedError
        
    async def run(self):
        """Run client test loop"""
        self.running = True
        
        try:
            await self.connect()
            
            while self.running:
                # Generate request payload
                payload = self._generate_payload()
                
                # Add error injection
                if random.random() < self.scenario.error_injection_rate:
                    payload = self._inject_error(payload)
                
                # Send request and measure response time
                start_time = time.time()
                success, response_time, error = await self.send_request(payload)
                
                # Update metrics
                self.metrics.request_count += 1
                if success:
                    self.metrics.success_count += 1
                    self.metrics.response_times.append(response_time)
                else:
                    self.metrics.error_count += 1
                    error_type = error or "Unknown"
                    self.metrics.error_types[error_type] = self.metrics.error_types.get(error_type, 0) + 1
                
                # Request delay
                await asyncio.sleep(self.scenario.request_delay_ms / 1000.0)
                
        except Exception as e:
            logger.error(f"Client {self.client_id} error: {e}")
        finally:
            await self.disconnect()
    
    def stop(self):
        """Stop client"""
        self.running = False
    
    def _generate_payload(self) -> Dict[str, Any]:
        """Generate test payload based on scenario"""
        use_korean = random.random() < self.scenario.korean_ratio
        
        # Payload size templates
        payloads = {
            "small": self._generate_small_payload,
            "medium": self._generate_medium_payload,
            "large": self._generate_large_payload,
            "extreme": self._generate_extreme_payload
        }
        
        return payloads[self.scenario.payload_size](use_korean)
    
    def _generate_small_payload(self, use_korean: bool) -> Dict[str, Any]:
        """Generate small payload"""
        if use_korean:
            text = "안녕하세요. 작은 테스트 문서입니다."
        else:
            text = "Hello. This is a small test document."
        
        return {
            "method": "convert_to_markdown",
            "params": {
                "uri": f"data:text/plain;base64,{self._encode_base64(text)}"
            }
        }
    
    def _generate_medium_payload(self, use_korean: bool) -> Dict[str, Any]:
        """Generate medium payload"""
        if use_korean:
            text = """# 한국어 문서 테스트
            
이것은 중간 크기의 한국어 테스트 문서입니다.

## 주요 내용
- 첫 번째 항목
- 두 번째 항목
- 세 번째 항목

### 세부 설명
한국어 처리 성능을 테스트하기 위한 문서입니다.
여러 줄의 텍스트와 다양한 한글 조합을 포함합니다.
""" * 10
        else:
            text = """# Test Document

This is a medium-sized test document.

## Main Content
- First item
- Second item  
- Third item

### Details
This document tests the server's ability to handle medium payloads.
Multiple lines of text with various formatting.
""" * 10
        
        return {
            "method": "convert_korean_document" if use_korean else "convert_to_markdown",
            "params": {
                "uri": f"data:text/plain;base64,{self._encode_base64(text)}",
                "normalize_korean": True
            }
        }
    
    def _generate_large_payload(self, use_korean: bool) -> Dict[str, Any]:
        """Generate large payload"""
        # Create temporary file with large content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            if use_korean:
                content = "대용량 한국어 텍스트 파일 테스트\n" * 10000
            else:
                content = "Large text file test\n" * 10000
            f.write(content)
            file_path = f.name
        
        return {
            "method": "convert_to_markdown",
            "params": {
                "uri": f"file://{file_path}"
            }
        }
    
    def _generate_extreme_payload(self, use_korean: bool) -> Dict[str, Any]:
        """Generate extreme payload for stress testing"""
        # 10MB+ payload
        if use_korean:
            text = "극한 스트레스 테스트용 대용량 한국어 텍스트 " * 100000
        else:
            text = "Extreme stress test with very large payload " * 100000
        
        return {
            "method": "convert_to_markdown",
            "params": {
                "uri": f"data:text/plain;base64,{self._encode_base64(text)}"
            }
        }
    
    def _inject_error(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Inject various errors into payload"""
        error_types = [
            lambda p: {"method": "invalid_method", "params": p.get("params", {})},
            lambda p: {"method": p.get("method"), "params": {"uri": "invalid://uri"}},
            lambda p: {"method": p.get("method"), "params": {}},  # Missing params
            lambda p: {"method": p.get("method"), "params": {"uri": "file:///nonexistent/file.txt"}},
            lambda p: None,  # Null payload
            lambda p: {"method": p.get("method"), "params": {"uri": "data:text/plain;base64,invalid_base64"}},
        ]
        
        error_func = random.choice(error_types)
        return error_func(payload)
    
    def _encode_base64(self, text: str) -> str:
        """Encode text to base64"""
        import base64
        return base64.b64encode(text.encode('utf-8')).decode('ascii')


class HTTPSSEClient(StressTestClient):
    """HTTP/SSE client for stress testing"""
    
    def __init__(self, client_id: int, scenario: TestScenario, port: int = BASE_PORT):
        super().__init__(client_id, scenario)
        self.port = port
        self.base_url = f"http://localhost:{port}"
        
    async def connect(self):
        """Create HTTP session"""
        timeout = aiohttp.ClientTimeout(
            total=self.scenario.connection_timeout,
            connect=5,
            sock_read=self.scenario.request_timeout
        )
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            
    async def send_request(self, payload: Dict[str, Any]) -> Tuple[bool, float, Optional[str]]:
        """Send HTTP request to MCP server"""
        if not self.session:
            return False, 0, "No session"
            
        try:
            start_time = time.time()
            
            # Prepare MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": f"{self.client_id}-{int(time.time()*1000)}",
                "method": payload.get("method", "convert_to_markdown"),
                "params": payload.get("params", {})
            }
            
            # Send request
            async with self.session.post(
                f"{self.base_url}/mcp/v1/invoke",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    if "error" in result:
                        return False, response_time, result["error"].get("message", "Unknown error")
                    return True, response_time, None
                else:
                    return False, response_time, f"HTTP {response.status}"
                    
        except asyncio.TimeoutError:
            return False, self.scenario.request_timeout, "Timeout"
        except Exception as e:
            return False, time.time() - start_time, str(e)


class STDIOClient(StressTestClient):
    """STDIO client for stress testing"""
    
    def __init__(self, client_id: int, scenario: TestScenario):
        super().__init__(client_id, scenario)
        self.process = None
        self.reader = None
        self.writer = None
        
    async def connect(self):
        """Start MCP server process in STDIO mode"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                MCP_SERVER_BIN,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.reader = self.process.stdout
            self.writer = self.process.stdin
            
            # Send initialization
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {}
                }
            }
            
            self.writer.write((json.dumps(init_request) + "\n").encode())
            await self.writer.drain()
            
            # Read initialization response
            response = await asyncio.wait_for(self.reader.readline(), timeout=5)
            
        except Exception as e:
            logger.error(f"STDIO client {self.client_id} connection error: {e}")
            raise
            
    async def disconnect(self):
        """Stop STDIO process"""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except:
                self.process.kill()
                
    async def send_request(self, payload: Dict[str, Any]) -> Tuple[bool, float, Optional[str]]:
        """Send request via STDIO"""
        if not self.writer:
            return False, 0, "No connection"
            
        try:
            start_time = time.time()
            
            # Prepare request
            request = {
                "jsonrpc": "2.0",
                "id": f"{self.client_id}-{int(time.time()*1000)}",
                "method": f"tools/{payload.get('method', 'convert_to_markdown')}",
                "params": payload.get("params", {})
            }
            
            # Send request
            self.writer.write((json.dumps(request) + "\n").encode())
            await self.writer.drain()
            
            # Read response
            response_line = await asyncio.wait_for(
                self.reader.readline(),
                timeout=self.scenario.request_timeout
            )
            
            response_time = time.time() - start_time
            
            if response_line:
                response = json.loads(response_line.decode())
                if "error" in response:
                    return False, response_time, response["error"].get("message", "Unknown error")
                return True, response_time, None
            else:
                return False, response_time, "Empty response"
                
        except asyncio.TimeoutError:
            return False, self.scenario.request_timeout, "Timeout"
        except Exception as e:
            return False, time.time() - start_time, str(e)


class LoadGenerator:
    """Generate load based on patterns"""
    
    def __init__(self, scenario: TestScenario):
        self.scenario = scenario
        self.active_clients: List[StressTestClient] = []
        self.metrics = TestMetrics()
        self.start_time = None
        self.stop_event = asyncio.Event()
        
    async def generate_load(self):
        """Generate load based on scenario pattern"""
        self.start_time = time.time()
        
        generators = {
            LoadPattern.GRADUAL_RAMP: self._gradual_ramp,
            LoadPattern.SPIKE: self._spike_load,
            LoadPattern.SUSTAINED: self._sustained_load,
            LoadPattern.WAVE: self._wave_load,
            LoadPattern.STRESS_TO_FAILURE: self._stress_to_failure,
            LoadPattern.RANDOM: self._random_load
        }
        
        generator = generators.get(self.scenario.load_pattern, self._gradual_ramp)
        await generator()
        
    async def _gradual_ramp(self):
        """Gradually increase load"""
        clients_per_step = max(1, (self.scenario.max_clients - self.scenario.initial_clients) // 10)
        step_duration = self.scenario.ramp_up_seconds / 10
        
        current_clients = self.scenario.initial_clients
        
        # Start initial clients
        await self._add_clients(current_clients)
        
        # Ramp up
        for _ in range(10):
            if self.stop_event.is_set():
                break
                
            await asyncio.sleep(step_duration)
            await self._add_clients(clients_per_step)
            current_clients += clients_per_step
            
            logger.info(f"Ramped up to {len(self.active_clients)} clients")
            
        # Sustain max load
        remaining_time = self.scenario.duration_seconds - self.scenario.ramp_up_seconds
        await asyncio.sleep(remaining_time)
        
    async def _spike_load(self):
        """Sudden spike in load"""
        # Start with minimal load
        await self._add_clients(5)
        await asyncio.sleep(10)
        
        # Sudden spike
        logger.info(f"Spiking load to {self.scenario.max_clients} clients")
        await self._add_clients(self.scenario.max_clients - 5)
        
        # Maintain spike
        await asyncio.sleep(self.scenario.duration_seconds - 10)
        
    async def _sustained_load(self):
        """Maintain constant load"""
        await self._add_clients(self.scenario.max_clients)
        await asyncio.sleep(self.scenario.duration_seconds)
        
    async def _wave_load(self):
        """Wave pattern - periodic increase/decrease"""
        wave_period = 60  # 60 second waves
        waves = self.scenario.duration_seconds // wave_period
        
        for wave in range(waves):
            if self.stop_event.is_set():
                break
                
            # Increase load
            target = self.scenario.max_clients if wave % 2 == 0 else self.scenario.initial_clients
            await self._adjust_clients(target)
            await asyncio.sleep(wave_period)
            
    async def _stress_to_failure(self):
        """Keep adding load until failure"""
        current_clients = self.scenario.initial_clients
        error_threshold = 0.5  # 50% error rate
        
        while not self.stop_event.is_set():
            await self._add_clients(10)
            current_clients += 10
            
            await asyncio.sleep(5)  # Let metrics stabilize
            
            # Check error rate
            error_rate = self.get_current_error_rate()
            logger.info(f"Clients: {current_clients}, Error rate: {error_rate:.2%}")
            
            if error_rate > error_threshold:
                logger.warning(f"Failure threshold reached at {current_clients} clients")
                break
                
            if current_clients > 1000:  # Safety limit
                logger.warning("Safety limit reached")
                break
                
    async def _random_load(self):
        """Random load pattern"""
        while not self.stop_event.is_set():
            target = random.randint(self.scenario.initial_clients, self.scenario.max_clients)
            await self._adjust_clients(target)
            await asyncio.sleep(random.randint(5, 30))
            
    async def _add_clients(self, count: int):
        """Add new clients"""
        tasks = []
        
        for i in range(count):
            client_id = len(self.active_clients) + i
            
            # Create appropriate client type
            if self.scenario.client_type == ClientType.STDIO:
                client = STDIOClient(client_id, self.scenario)
            elif self.scenario.client_type == ClientType.HTTP_SSE:
                client = HTTPSSEClient(client_id, self.scenario)
            elif self.scenario.client_type == ClientType.MIXED:
                # Randomly choose client type
                if random.random() < 0.5:
                    client = STDIOClient(client_id, self.scenario)
                else:
                    client = HTTPSSEClient(client_id, self.scenario)
            else:
                client = HTTPSSEClient(client_id, self.scenario)
                
            self.active_clients.append(client)
            tasks.append(asyncio.create_task(client.run()))
            
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _adjust_clients(self, target: int):
        """Adjust number of active clients to target"""
        current = len(self.active_clients)
        
        if target > current:
            await self._add_clients(target - current)
        elif target < current:
            # Stop excess clients
            for i in range(current - target):
                client = self.active_clients.pop()
                client.stop()
                
    def get_current_error_rate(self) -> float:
        """Get current error rate from all clients"""
        total_requests = sum(c.metrics.request_count for c in self.active_clients)
        total_errors = sum(c.metrics.error_count for c in self.active_clients)
        
        return total_errors / total_requests if total_requests > 0 else 0
        
    def aggregate_metrics(self) -> TestMetrics:
        """Aggregate metrics from all clients"""
        aggregated = TestMetrics()
        
        for client in self.active_clients:
            aggregated.request_count += client.metrics.request_count
            aggregated.success_count += client.metrics.success_count
            aggregated.error_count += client.metrics.error_count
            aggregated.response_times.extend(client.metrics.response_times)
            
            # Merge error types
            for error_type, count in client.metrics.error_types.items():
                aggregated.error_types[error_type] = aggregated.error_types.get(error_type, 0) + count
                
        return aggregated
        
    async def stop(self):
        """Stop all clients"""
        self.stop_event.set()
        
        for client in self.active_clients:
            client.stop()
            
        # Wait for clients to finish
        await asyncio.sleep(2)


class StressTestRunner:
    """Main stress test runner"""
    
    def __init__(self):
        self.scenarios: List[TestScenario] = []
        self.results: Dict[str, Any] = {}
        self.server_manager = MCPServerManager()
        self.resource_monitor = None
        
    def add_scenario(self, scenario: TestScenario):
        """Add test scenario"""
        self.scenarios.append(scenario)
        
    async def run_all_scenarios(self):
        """Run all test scenarios"""
        logger.info(f"Starting stress test with {len(self.scenarios)} scenarios")
        
        for scenario in self.scenarios:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running scenario: {scenario.name}")
            logger.info(f"{'='*60}")
            
            try:
                result = await self.run_scenario(scenario)
                self.results[scenario.name] = result
            except Exception as e:
                logger.error(f"Scenario {scenario.name} failed: {e}")
                self.results[scenario.name] = {"error": str(e)}
                
        # Generate final report
        self.generate_report()
        
    async def run_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """Run single test scenario"""
        # Start server if needed
        if scenario.client_type in [ClientType.HTTP_SSE, ClientType.MIXED]:
            if not self.server_manager.start_server("http"):
                raise RuntimeError("Failed to start HTTP server")
                
            # Start resource monitoring
            self.resource_monitor = ResourceMonitor(self.server_manager.pid)
            self.resource_monitor.start_monitoring()
            
        # Create load generator
        generator = LoadGenerator(scenario)
        
        # Run load test
        start_time = time.time()
        
        try:
            # Run in background
            load_task = asyncio.create_task(generator.generate_load())
            
            # Wait for duration
            await asyncio.sleep(scenario.duration_seconds)
            
            # Stop load
            await generator.stop()
            await load_task
            
        finally:
            duration = time.time() - start_time
            
            # Collect metrics
            metrics = generator.aggregate_metrics()
            
            # Stop resource monitoring
            if self.resource_monitor:
                self.resource_monitor.stop_monitoring()
                resource_metrics = self.resource_monitor.get_metrics()
            else:
                resource_metrics = []
                
            # Stop server
            if scenario.client_type in [ClientType.HTTP_SSE, ClientType.MIXED]:
                self.server_manager.stop_server()
                
        # Prepare results
        return {
            "scenario": asdict(scenario),
            "duration": duration,
            "metrics": {
                "total_requests": metrics.request_count,
                "successful_requests": metrics.success_count,
                "failed_requests": metrics.error_count,
                "error_rate": metrics.get_error_rate(),
                "throughput": metrics.get_throughput(duration),
                "response_times": metrics.get_percentiles(),
                "error_types": metrics.error_types,
            },
            "resource_usage": self._analyze_resource_metrics(resource_metrics),
            "timestamp": datetime.now().isoformat()
        }
        
    def _analyze_resource_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Analyze resource usage metrics"""
        if not metrics:
            return {}
            
        cpu_usage = [m.get("process_cpu", 0) for m in metrics if "process_cpu" in m]
        memory_usage = [m.get("process_memory", 0) for m in metrics if "process_memory" in m]
        connections = [m.get("process_connections", 0) for m in metrics if "process_connections" in m]
        
        return {
            "cpu": {
                "mean": statistics.mean(cpu_usage) if cpu_usage else 0,
                "max": max(cpu_usage) if cpu_usage else 0,
                "p95": np.percentile(cpu_usage, 95) if cpu_usage else 0,
            },
            "memory_mb": {
                "mean": statistics.mean(memory_usage) if memory_usage else 0,
                "max": max(memory_usage) if memory_usage else 0,
                "p95": np.percentile(memory_usage, 95) if memory_usage else 0,
            },
            "connections": {
                "mean": statistics.mean(connections) if connections else 0,
                "max": max(connections) if connections else 0,
            }
        }
        
    def generate_report(self):
        """Generate comprehensive test report"""
        report_path = Path("stress_test_report.json")
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
            
        logger.info(f"Test report saved to {report_path}")
        
        # Print summary
        print("\n" + "="*80)
        print("STRESS TEST SUMMARY")
        print("="*80)
        
        for scenario_name, result in self.results.items():
            if "error" in result:
                print(f"\n{scenario_name}: FAILED - {result['error']}")
                continue
                
            metrics = result.get("metrics", {})
            response_times = metrics.get("response_times", {})
            resource_usage = result.get("resource_usage", {})
            
            print(f"\n{scenario_name}:")
            print(f"  Total Requests: {metrics.get('total_requests', 0):,}")
            print(f"  Success Rate: {100 - metrics.get('error_rate', 0):.2f}%")
            print(f"  Throughput: {metrics.get('throughput', 0):.2f} req/s")
            print(f"  Response Times:")
            print(f"    - P50: {response_times.get('p50', 0):.3f}s")
            print(f"    - P95: {response_times.get('p95', 0):.3f}s")
            print(f"    - P99: {response_times.get('p99', 0):.3f}s")
            
            if resource_usage:
                print(f"  Resource Usage:")
                print(f"    - CPU: {resource_usage.get('cpu', {}).get('mean', 0):.1f}% (max: {resource_usage.get('cpu', {}).get('max', 0):.1f}%)")
                print(f"    - Memory: {resource_usage.get('memory_mb', {}).get('mean', 0):.1f}MB (max: {resource_usage.get('memory_mb', {}).get('max', 0):.1f}MB)")
                print(f"    - Connections: {resource_usage.get('connections', {}).get('max', 0)}")


def create_standard_scenarios() -> List[TestScenario]:
    """Create standard test scenarios"""
    scenarios = []
    
    # 1. Gradual ramp-up test
    scenarios.append(TestScenario(
        name="gradual_ramp_http",
        load_pattern=LoadPattern.GRADUAL_RAMP,
        client_type=ClientType.HTTP_SSE,
        initial_clients=1,
        max_clients=100,
        duration_seconds=300,
        ramp_up_seconds=120,
        request_delay_ms=100,
        payload_size="medium",
        korean_ratio=0.5
    ))
    
    # 2. Spike test
    scenarios.append(TestScenario(
        name="spike_test_mixed",
        load_pattern=LoadPattern.SPIKE,
        client_type=ClientType.MIXED,
        initial_clients=5,
        max_clients=200,
        duration_seconds=120,
        request_delay_ms=50,
        payload_size="small",
        korean_ratio=0.7
    ))
    
    # 3. Sustained load test
    scenarios.append(TestScenario(
        name="sustained_load_stdio",
        load_pattern=LoadPattern.SUSTAINED,
        client_type=ClientType.STDIO,
        initial_clients=50,
        max_clients=50,
        duration_seconds=600,
        request_delay_ms=200,
        payload_size="medium",
        korean_ratio=0.3
    ))
    
    # 4. Wave pattern test
    scenarios.append(TestScenario(
        name="wave_pattern_http",
        load_pattern=LoadPattern.WAVE,
        client_type=ClientType.HTTP_SSE,
        initial_clients=10,
        max_clients=80,
        duration_seconds=480,
        request_delay_ms=100,
        payload_size="medium",
        korean_ratio=0.5
    ))
    
    # 5. Stress to failure
    scenarios.append(TestScenario(
        name="stress_to_failure",
        load_pattern=LoadPattern.STRESS_TO_FAILURE,
        client_type=ClientType.HTTP_SSE,
        initial_clients=10,
        max_clients=1000,  # Will stop when failure threshold reached
        duration_seconds=1200,
        request_delay_ms=10,
        payload_size="large",
        korean_ratio=0.6,
        error_injection_rate=0.1
    ))
    
    # 6. Korean text heavy load
    scenarios.append(TestScenario(
        name="korean_text_stress",
        load_pattern=LoadPattern.SUSTAINED,
        client_type=ClientType.HTTP_SSE,
        initial_clients=30,
        max_clients=30,
        duration_seconds=300,
        request_delay_ms=50,
        payload_size="large",
        korean_ratio=1.0,  # 100% Korean text
        error_injection_rate=0.02
    ))
    
    # 7. Rapid connection test
    scenarios.append(TestScenario(
        name="rapid_connections",
        load_pattern=LoadPattern.RANDOM,
        client_type=ClientType.MIXED,
        initial_clients=5,
        max_clients=50,
        duration_seconds=180,
        request_delay_ms=10,
        payload_size="small",
        korean_ratio=0.4,
        connection_timeout=5,
        request_timeout=10
    ))
    
    # 8. Extreme payload test
    scenarios.append(TestScenario(
        name="extreme_payload",
        load_pattern=LoadPattern.SUSTAINED,
        client_type=ClientType.HTTP_SSE,
        initial_clients=5,
        max_clients=5,
        duration_seconds=120,
        request_delay_ms=5000,  # 5 seconds between requests
        payload_size="extreme",
        korean_ratio=0.5,
        error_injection_rate=0
    ))
    
    return scenarios


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Concurrent Stress Test Framework for VoidLight MarkItDown MCP Server")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to run")
    parser.add_argument("--quick", action="store_true", help="Run quick test (reduced duration)")
    parser.add_argument("--extreme", action="store_true", help="Include extreme stress tests")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = StressTestRunner()
    
    # Get scenarios
    all_scenarios = create_standard_scenarios()
    
    # Filter scenarios if specified
    if args.scenarios:
        all_scenarios = [s for s in all_scenarios if s.name in args.scenarios]
        
    # Adjust for quick test
    if args.quick:
        for scenario in all_scenarios:
            scenario.duration_seconds = min(60, scenario.duration_seconds)
            scenario.max_clients = min(20, scenario.max_clients)
            
    # Remove extreme tests unless requested
    if not args.extreme:
        all_scenarios = [s for s in all_scenarios if "extreme" not in s.name and "failure" not in s.name]
        
    # Add scenarios to runner
    for scenario in all_scenarios:
        runner.add_scenario(scenario)
        
    # Run tests
    await runner.run_all_scenarios()


if __name__ == "__main__":
    asyncio.run(main())