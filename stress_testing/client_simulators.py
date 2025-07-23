#!/usr/bin/env python3
"""
Specialized Client Simulators for Different Load Patterns
Includes STDIO, HTTP/SSE, and mixed protocol clients with various behaviors
"""

import asyncio
import json
import time
import os
import sys
import subprocess
import random
import tempfile
import base64
import aiohttp
import websockets
from typing import Dict, List, Optional, Tuple, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import hashlib
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Korean text samples for testing
KOREAN_SAMPLES = [
    "안녕하세요. 이것은 한국어 테스트 문서입니다.",
    "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
    "한글은 세종대왕이 창제한 문자입니다.",
    "대한민국의 수도는 서울입니다.",
    "김치는 한국의 전통 발효 음식입니다.",
    "한국어 자연어 처리는 복잡한 작업입니다.",
    "조선시대는 1392년부터 1910년까지 지속되었습니다.",
    "한강은 서울을 가로지르는 주요 강입니다.",
    "태극기는 대한민국의 국기입니다.",
    "한국의 전통 음악을 국악이라고 합니다."
]

# Mixed language samples
MIXED_SAMPLES = [
    "Hello 안녕하세요 World 세계",
    "Python 파이썬 Programming 프로그래밍",
    "Machine Learning 기계 학습 AI 인공지능",
    "Server 서버 Client 클라이언트 Connection 연결"
]


class RequestPattern(Enum):
    """Different request patterns for testing"""
    STEADY = "steady"          # Constant rate
    BURST = "burst"           # Sudden bursts
    RANDOM = "random"         # Random intervals
    INCREASING = "increasing"  # Gradually increasing rate
    OSCILLATING = "oscillating"  # Wave-like pattern


@dataclass
class ClientConfig:
    """Configuration for client simulator"""
    client_id: int
    server_url: str = "http://localhost:3001"
    request_pattern: RequestPattern = RequestPattern.STEADY
    base_delay_ms: int = 100
    korean_ratio: float = 0.5
    error_injection_rate: float = 0.05
    timeout_seconds: int = 30
    max_retries: int = 3
    persistent_connection: bool = True
    log_responses: bool = False


class BaseClient:
    """Base class for all client simulators"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
        self.running = False
        self.session_start = None
        
    async def start(self):
        """Start the client"""
        self.running = True
        self.session_start = time.time()
        logger.info(f"Client {self.config.client_id} starting")
        
    async def stop(self):
        """Stop the client"""
        self.running = False
        duration = time.time() - self.session_start if self.session_start else 0
        logger.info(f"Client {self.config.client_id} stopped - Requests: {self.request_count}, "
                   f"Errors: {self.error_count}, Duration: {duration:.2f}s")
        
    async def generate_request(self) -> Dict[str, Any]:
        """Generate a request payload"""
        use_korean = random.random() < self.config.korean_ratio
        
        # Inject errors based on configuration
        if random.random() < self.config.error_injection_rate:
            return self._generate_error_request()
            
        # Generate normal request
        content_type = random.choice(["text", "html", "markdown", "mixed"])
        
        if content_type == "text":
            return self._generate_text_request(use_korean)
        elif content_type == "html":
            return self._generate_html_request(use_korean)
        elif content_type == "markdown":
            return self._generate_markdown_request(use_korean)
        else:
            return self._generate_mixed_content_request(use_korean)
            
    def _generate_text_request(self, use_korean: bool) -> Dict[str, Any]:
        """Generate plain text request"""
        if use_korean:
            text = random.choice(KOREAN_SAMPLES) * random.randint(1, 10)
        else:
            text = f"This is test document {self.request_count} from client {self.config.client_id}. " * random.randint(1, 10)
            
        encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')
        
        return {
            "method": "convert_korean_document" if use_korean else "convert_to_markdown",
            "params": {
                "uri": f"data:text/plain;base64,{encoded}",
                "normalize_korean": True if use_korean else None
            }
        }
        
    def _generate_html_request(self, use_korean: bool) -> Dict[str, Any]:
        """Generate HTML request"""
        if use_korean:
            html = f"""
            <html>
            <head><title>한국어 테스트 문서</title></head>
            <body>
                <h1>테스트 제목 {self.request_count}</h1>
                <p>{random.choice(KOREAN_SAMPLES)}</p>
                <ul>
                    <li>첫 번째 항목</li>
                    <li>두 번째 항목</li>
                </ul>
            </body>
            </html>
            """
        else:
            html = f"""
            <html>
            <head><title>Test Document</title></head>
            <body>
                <h1>Test Title {self.request_count}</h1>
                <p>This is a test paragraph from client {self.config.client_id}.</p>
                <ul>
                    <li>First item</li>
                    <li>Second item</li>
                </ul>
            </body>
            </html>
            """
            
        encoded = base64.b64encode(html.encode('utf-8')).decode('ascii')
        
        return {
            "method": "convert_to_markdown",
            "params": {
                "uri": f"data:text/html;base64,{encoded}"
            }
        }
        
    def _generate_markdown_request(self, use_korean: bool) -> Dict[str, Any]:
        """Generate Markdown request"""
        if use_korean:
            markdown = f"""
# 한국어 마크다운 문서

## 소개
{random.choice(KOREAN_SAMPLES)}

### 목록
- 항목 1
- 항목 2
- 항목 3

**굵은 텍스트** 와 *기울임 텍스트*
            """
        else:
            markdown = f"""
# Markdown Document

## Introduction
This is test document {self.request_count} from client {self.config.client_id}.

### List
- Item 1
- Item 2
- Item 3

**Bold text** and *italic text*
            """
            
        encoded = base64.b64encode(markdown.encode('utf-8')).decode('ascii')
        
        return {
            "method": "convert_to_markdown",
            "params": {
                "uri": f"data:text/markdown;base64,{encoded}"
            }
        }
        
    def _generate_mixed_content_request(self, use_korean: bool) -> Dict[str, Any]:
        """Generate mixed language content request"""
        content = random.choice(MIXED_SAMPLES) * random.randint(5, 20)
        encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
        
        return {
            "method": "convert_korean_document",
            "params": {
                "uri": f"data:text/plain;base64,{encoded}",
                "normalize_korean": True
            }
        }
        
    def _generate_error_request(self) -> Dict[str, Any]:
        """Generate various error-inducing requests"""
        error_types = [
            # Invalid method
            lambda: {
                "method": "invalid_method_name",
                "params": {"uri": "data:text/plain;base64,dGVzdA=="}
            },
            # Missing required parameter
            lambda: {
                "method": "convert_to_markdown",
                "params": {}
            },
            # Invalid URI scheme
            lambda: {
                "method": "convert_to_markdown",
                "params": {"uri": "invalid://scheme"}
            },
            # Malformed base64
            lambda: {
                "method": "convert_to_markdown",
                "params": {"uri": "data:text/plain;base64,!!!invalid!!!"}
            },
            # Non-existent file
            lambda: {
                "method": "convert_to_markdown",
                "params": {"uri": f"file:///non/existent/file_{random.randint(1000, 9999)}.txt"}
            },
            # Null parameters
            lambda: {
                "method": "convert_to_markdown",
                "params": None
            },
            # Empty request
            lambda: {},
            # Extremely large payload
            lambda: {
                "method": "convert_to_markdown",
                "params": {"uri": f"data:text/plain;base64,{base64.b64encode(b'X' * 10000000).decode('ascii')}"}
            }
        ]
        
        return random.choice(error_types)()
        
    async def calculate_delay(self) -> float:
        """Calculate delay based on request pattern"""
        base_delay = self.config.base_delay_ms / 1000.0
        
        if self.config.request_pattern == RequestPattern.STEADY:
            return base_delay
            
        elif self.config.request_pattern == RequestPattern.BURST:
            # Burst every 10 requests
            if self.request_count % 10 < 5:
                return base_delay / 10  # Fast during burst
            else:
                return base_delay * 5   # Slow between bursts
                
        elif self.config.request_pattern == RequestPattern.RANDOM:
            return random.uniform(0, base_delay * 3)
            
        elif self.config.request_pattern == RequestPattern.INCREASING:
            # Gradually decrease delay (increase rate)
            factor = max(0.1, 1.0 - (self.request_count / 1000))
            return base_delay * factor
            
        elif self.config.request_pattern == RequestPattern.OSCILLATING:
            # Sine wave pattern
            import math
            phase = self.request_count / 50  # Complete cycle every 50 requests
            factor = 0.5 + 0.5 * math.sin(2 * math.pi * phase)
            return base_delay * (0.5 + factor)
            
        return base_delay


class HTTPClient(BaseClient):
    """HTTP/SSE client simulator"""
    
    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def start(self):
        """Start HTTP client"""
        await super().start()
        
        # Create session
        timeout = aiohttp.ClientTimeout(
            total=self.config.timeout_seconds,
            connect=5,
            sock_read=self.config.timeout_seconds
        )
        
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            force_close=not self.config.persistent_connection
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )
        
    async def stop(self):
        """Stop HTTP client"""
        if self.session:
            await self.session.close()
        await super().stop()
        
    async def send_request(self, request: Dict[str, Any]) -> Tuple[bool, float, Optional[str]]:
        """Send HTTP request"""
        if not self.session:
            return False, 0, "No session"
            
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"{self.config.client_id}-{self.request_count}",
            "method": request.get("method"),
            "params": request.get("params")
        }
        
        start_time = time.time()
        
        for retry in range(self.config.max_retries):
            try:
                async with self.session.post(
                    f"{self.config.server_url}/mcp/v1/invoke",
                    json=mcp_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if self.config.log_responses:
                            logger.debug(f"Client {self.config.client_id} response: {result}")
                            
                        if "error" in result:
                            return False, response_time, result["error"].get("message", "Unknown error")
                            
                        return True, response_time, None
                    else:
                        error_msg = f"HTTP {response.status}"
                        if retry < self.config.max_retries - 1:
                            await asyncio.sleep(1)  # Wait before retry
                            continue
                        return False, response_time, error_msg
                        
            except asyncio.TimeoutError:
                return False, self.config.timeout_seconds, "Timeout"
            except aiohttp.ClientError as e:
                error_msg = str(e)
                if retry < self.config.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                return False, time.time() - start_time, error_msg
            except Exception as e:
                return False, time.time() - start_time, str(e)
                
        return False, time.time() - start_time, "Max retries exceeded"
        
    async def run(self):
        """Run client simulation"""
        while self.running:
            try:
                # Generate request
                request = await self.generate_request()
                
                # Send request
                success, response_time, error = await self.send_request(request)
                
                # Update stats
                self.request_count += 1
                self.total_response_time += response_time
                if not success:
                    self.error_count += 1
                    if error:
                        logger.warning(f"Client {self.config.client_id} error: {error}")
                        
                # Calculate and apply delay
                delay = await self.calculate_delay()
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Client {self.config.client_id} run error: {e}")
                self.error_count += 1
                await asyncio.sleep(1)


class STDIOClient(BaseClient):
    """STDIO client simulator"""
    
    def __init__(self, config: ClientConfig, mcp_binary: str):
        super().__init__(config)
        self.mcp_binary = mcp_binary
        self.process: Optional[asyncio.subprocess.Process] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.initialized = False
        
    async def start(self):
        """Start STDIO client"""
        await super().start()
        
        try:
            # Start MCP server process
            self.process = await asyncio.create_subprocess_exec(
                self.mcp_binary,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "VOIDLIGHT_LOG_LEVEL": "ERROR"}  # Reduce noise
            )
            
            self.reader = self.process.stdout
            self.writer = self.process.stdin
            
            # Initialize connection
            await self._initialize_connection()
            
        except Exception as e:
            logger.error(f"STDIO client {self.config.client_id} start error: {e}")
            raise
            
    async def stop(self):
        """Stop STDIO client"""
        if self.process:
            try:
                # Send shutdown
                if self.writer and not self.writer.is_closing():
                    shutdown_request = {
                        "jsonrpc": "2.0",
                        "id": "shutdown",
                        "method": "shutdown",
                        "params": {}
                    }
                    self.writer.write((json.dumps(shutdown_request) + "\n").encode())
                    await self.writer.drain()
                    
                # Terminate process
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except:
                if self.process:
                    self.process.kill()
                    
        await super().stop()
        
    async def _initialize_connection(self):
        """Initialize MCP connection"""
        init_request = {
            "jsonrpc": "2.0",
            "id": "init",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": f"stress-test-client-{self.config.client_id}",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialization
        self.writer.write((json.dumps(init_request) + "\n").encode())
        await self.writer.drain()
        
        # Read response
        response_line = await asyncio.wait_for(self.reader.readline(), timeout=5)
        if response_line:
            response = json.loads(response_line.decode())
            if "result" in response:
                self.initialized = True
                logger.info(f"STDIO client {self.config.client_id} initialized")
            else:
                raise RuntimeError(f"Initialization failed: {response}")
        else:
            raise RuntimeError("No initialization response")
            
    async def send_request(self, request: Dict[str, Any]) -> Tuple[bool, float, Optional[str]]:
        """Send STDIO request"""
        if not self.initialized or not self.writer:
            return False, 0, "Not initialized"
            
        # Prepare MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"{self.config.client_id}-{self.request_count}",
            "method": f"tools/{request.get('method', 'convert_to_markdown')}",
            "params": request.get("params", {})
        }
        
        start_time = time.time()
        
        try:
            # Send request
            self.writer.write((json.dumps(mcp_request) + "\n").encode())
            await self.writer.drain()
            
            # Read response
            response_line = await asyncio.wait_for(
                self.reader.readline(),
                timeout=self.config.timeout_seconds
            )
            
            response_time = time.time() - start_time
            
            if response_line:
                response = json.loads(response_line.decode())
                
                if self.config.log_responses:
                    logger.debug(f"STDIO client {self.config.client_id} response: {response}")
                    
                if "error" in response:
                    return False, response_time, response["error"].get("message", "Unknown error")
                elif "result" in response:
                    return True, response_time, None
                else:
                    return False, response_time, "Invalid response format"
            else:
                return False, response_time, "Empty response"
                
        except asyncio.TimeoutError:
            return False, self.config.timeout_seconds, "Timeout"
        except json.JSONDecodeError as e:
            return False, time.time() - start_time, f"JSON decode error: {e}"
        except Exception as e:
            return False, time.time() - start_time, str(e)
            
    async def run(self):
        """Run client simulation"""
        while self.running and self.initialized:
            try:
                # Generate request
                request = await self.generate_request()
                
                # Send request
                success, response_time, error = await self.send_request(request)
                
                # Update stats
                self.request_count += 1
                self.total_response_time += response_time
                if not success:
                    self.error_count += 1
                    if error:
                        logger.warning(f"STDIO client {self.config.client_id} error: {error}")
                        
                    # Check if connection is broken
                    if "broken pipe" in error.lower() or "eof" in error.lower():
                        logger.error(f"STDIO client {self.config.client_id} connection broken, restarting")
                        await self.stop()
                        await self.start()
                        
                # Calculate and apply delay
                delay = await self.calculate_delay()
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"STDIO client {self.config.client_id} run error: {e}")
                self.error_count += 1
                await asyncio.sleep(1)


class MixedProtocolClient(BaseClient):
    """Client that randomly switches between HTTP and STDIO"""
    
    def __init__(self, config: ClientConfig, mcp_binary: str):
        super().__init__(config)
        self.mcp_binary = mcp_binary
        self.http_client = HTTPClient(config)
        self.stdio_client = STDIOClient(config, mcp_binary)
        self.current_protocol = None
        
    async def start(self):
        """Start mixed client"""
        await super().start()
        # Start both clients
        await self.http_client.start()
        await self.stdio_client.start()
        
    async def stop(self):
        """Stop mixed client"""
        await self.http_client.stop()
        await self.stdio_client.stop()
        await super().stop()
        
    async def run(self):
        """Run client simulation with protocol switching"""
        switch_interval = 20  # Switch protocol every N requests
        
        while self.running:
            try:
                # Decide which protocol to use
                if self.request_count % switch_interval == 0:
                    self.current_protocol = random.choice(["http", "stdio"])
                    logger.info(f"Client {self.config.client_id} switching to {self.current_protocol}")
                    
                # Use appropriate client
                if self.current_protocol == "http":
                    client = self.http_client
                else:
                    client = self.stdio_client
                    
                # Generate and send request
                request = await self.generate_request()
                success, response_time, error = await client.send_request(request)
                
                # Update stats
                self.request_count += 1
                self.total_response_time += response_time
                if not success:
                    self.error_count += 1
                    
                # Calculate and apply delay
                delay = await self.calculate_delay()
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Mixed client {self.config.client_id} error: {e}")
                self.error_count += 1
                await asyncio.sleep(1)


class ClientPool:
    """Manage a pool of clients"""
    
    def __init__(self, mcp_binary: str = None):
        self.mcp_binary = mcp_binary or "/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp"
        self.clients: List[BaseClient] = []
        self.running = False
        
    def add_http_clients(self, count: int, config_template: ClientConfig):
        """Add HTTP clients to pool"""
        for i in range(count):
            config = ClientConfig(
                client_id=len(self.clients) + i,
                server_url=config_template.server_url,
                request_pattern=config_template.request_pattern,
                base_delay_ms=config_template.base_delay_ms,
                korean_ratio=config_template.korean_ratio,
                error_injection_rate=config_template.error_injection_rate,
                timeout_seconds=config_template.timeout_seconds,
                max_retries=config_template.max_retries,
                persistent_connection=config_template.persistent_connection,
                log_responses=config_template.log_responses
            )
            self.clients.append(HTTPClient(config))
            
    def add_stdio_clients(self, count: int, config_template: ClientConfig):
        """Add STDIO clients to pool"""
        for i in range(count):
            config = ClientConfig(
                client_id=len(self.clients) + i,
                server_url=config_template.server_url,
                request_pattern=config_template.request_pattern,
                base_delay_ms=config_template.base_delay_ms,
                korean_ratio=config_template.korean_ratio,
                error_injection_rate=config_template.error_injection_rate,
                timeout_seconds=config_template.timeout_seconds,
                max_retries=config_template.max_retries,
                persistent_connection=config_template.persistent_connection,
                log_responses=config_template.log_responses
            )
            self.clients.append(STDIOClient(config, self.mcp_binary))
            
    def add_mixed_clients(self, count: int, config_template: ClientConfig):
        """Add mixed protocol clients to pool"""
        for i in range(count):
            config = ClientConfig(
                client_id=len(self.clients) + i,
                server_url=config_template.server_url,
                request_pattern=config_template.request_pattern,
                base_delay_ms=config_template.base_delay_ms,
                korean_ratio=config_template.korean_ratio,
                error_injection_rate=config_template.error_injection_rate,
                timeout_seconds=config_template.timeout_seconds,
                max_retries=config_template.max_retries,
                persistent_connection=config_template.persistent_connection,
                log_responses=config_template.log_responses
            )
            self.clients.append(MixedProtocolClient(config, self.mcp_binary))
            
    async def start_all(self):
        """Start all clients"""
        self.running = True
        logger.info(f"Starting {len(self.clients)} clients")
        
        # Start clients in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(self.clients), batch_size):
            batch = self.clients[i:i + batch_size]
            await asyncio.gather(*[client.start() for client in batch])
            await asyncio.sleep(0.5)  # Brief pause between batches
            
    async def run_all(self, duration_seconds: int):
        """Run all clients for specified duration"""
        if not self.running:
            await self.start_all()
            
        # Run clients
        tasks = [asyncio.create_task(client.run()) for client in self.clients]
        
        # Wait for duration
        await asyncio.sleep(duration_seconds)
        
        # Stop all clients
        await self.stop_all()
        
        # Cancel remaining tasks
        for task in tasks:
            task.cancel()
            
    async def stop_all(self):
        """Stop all clients"""
        self.running = False
        logger.info("Stopping all clients")
        
        # Stop in batches
        batch_size = 10
        for i in range(0, len(self.clients), batch_size):
            batch = self.clients[i:i + batch_size]
            await asyncio.gather(*[client.stop() for client in batch], return_exceptions=True)
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics from all clients"""
        total_requests = sum(c.request_count for c in self.clients)
        total_errors = sum(c.error_count for c in self.clients)
        total_response_time = sum(c.total_response_time for c in self.clients)
        
        avg_response_time = total_response_time / total_requests if total_requests > 0 else 0
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_clients": len(self.clients),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "average_response_time": avg_response_time,
            "requests_per_client": total_requests / len(self.clients) if self.clients else 0,
            "errors_per_client": total_errors / len(self.clients) if self.clients else 0
        }


async def demo_client_simulators():
    """Demonstrate different client simulators"""
    
    # Create client pool
    pool = ClientPool()
    
    # Add different types of clients
    base_config = ClientConfig(
        client_id=0,
        request_pattern=RequestPattern.STEADY,
        base_delay_ms=100,
        korean_ratio=0.5,
        error_injection_rate=0.05
    )
    
    # Add 10 HTTP clients with steady pattern
    steady_config = ClientConfig(**base_config.__dict__)
    steady_config.request_pattern = RequestPattern.STEADY
    pool.add_http_clients(10, steady_config)
    
    # Add 5 STDIO clients with burst pattern
    burst_config = ClientConfig(**base_config.__dict__)
    burst_config.request_pattern = RequestPattern.BURST
    pool.add_stdio_clients(5, burst_config)
    
    # Add 5 mixed clients with random pattern
    random_config = ClientConfig(**base_config.__dict__)
    random_config.request_pattern = RequestPattern.RANDOM
    pool.add_mixed_clients(5, random_config)
    
    # Run for 60 seconds
    logger.info("Starting client simulation demo")
    await pool.run_all(60)
    
    # Print statistics
    stats = pool.get_statistics()
    print("\n" + "="*60)
    print("CLIENT SIMULATION RESULTS")
    print("="*60)
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Client simulators for stress testing")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--clients", type=int, default=10, help="Number of clients")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--pattern", choices=[p.value for p in RequestPattern], 
                       default=RequestPattern.STEADY.value, help="Request pattern")
    parser.add_argument("--protocol", choices=["http", "stdio", "mixed"], 
                       default="http", help="Protocol type")
    
    args = parser.parse_args()
    
    if args.demo:
        asyncio.run(demo_client_simulators())
    else:
        # Run custom configuration
        pool = ClientPool()
        
        config = ClientConfig(
            client_id=0,
            request_pattern=RequestPattern(args.pattern),
            base_delay_ms=100,
            korean_ratio=0.5,
            error_injection_rate=0.05
        )
        
        if args.protocol == "http":
            pool.add_http_clients(args.clients, config)
        elif args.protocol == "stdio":
            pool.add_stdio_clients(args.clients, config)
        else:
            pool.add_mixed_clients(args.clients, config)
            
        asyncio.run(pool.run_all(args.duration))
        
        # Print results
        stats = pool.get_statistics()
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        for key, value in stats.items():
            print(f"{key}: {value}")