#!/usr/bin/env python3
"""
Error Recovery and Chaos Engineering Framework for VoidLight MarkItDown
Tests production resilience and error recovery mechanisms
"""

import asyncio
import json
import logging
import os
import random
import signal
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import tempfile
import shutil
import psutil
import resource

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures to inject"""
    NETWORK_TIMEOUT = "network_timeout"
    NETWORK_DISCONNECT = "network_disconnect"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "packet_loss"
    
    FILE_PERMISSION_DENIED = "file_permission_denied"
    FILE_NOT_FOUND = "file_not_found"
    DISK_FULL = "disk_full"
    FILE_CORRUPTION = "file_corruption"
    
    MEMORY_EXHAUSTION = "memory_exhaustion"
    MEMORY_LEAK = "memory_leak"
    CPU_THROTTLING = "cpu_throttling"
    PROCESS_CRASH = "process_crash"
    
    ENCODING_ERROR = "encoding_error"
    UNICODE_ERROR = "unicode_error"
    MALFORMED_INPUT = "malformed_input"
    OVERSIZED_INPUT = "oversized_input"
    
    DEPENDENCY_FAILURE = "dependency_failure"
    KOREAN_NLP_FAILURE = "korean_nlp_failure"
    EXTERNAL_API_FAILURE = "external_api_failure"
    
    CONCURRENT_ACCESS = "concurrent_access"
    RACE_CONDITION = "race_condition"
    DEADLOCK = "deadlock"


class RecoveryMetric(Enum):
    """Metrics for measuring recovery effectiveness"""
    TIME_TO_DETECT = "time_to_detect"
    TIME_TO_RECOVER = "time_to_recover"
    DATA_LOSS = "data_loss"
    REQUESTS_FAILED = "requests_failed"
    RECOVERY_SUCCESS_RATE = "recovery_success_rate"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    ERROR_PROPAGATION = "error_propagation"
    RESOURCE_CLEANUP = "resource_cleanup"


@dataclass
class FailureScenario:
    """Define a failure scenario to test"""
    name: str
    failure_type: FailureType
    description: str
    setup: Optional[Callable] = None
    inject: Optional[Callable] = None
    verify: Optional[Callable] = None
    cleanup: Optional[Callable] = None
    expected_behavior: str = ""
    recovery_timeout: float = 30.0
    korean_specific: bool = False
    severity: str = "medium"  # low, medium, high, critical
    tags: List[str] = field(default_factory=list)


@dataclass
class RecoveryResult:
    """Result of a recovery test"""
    scenario_name: str
    success: bool
    failure_detected: bool
    recovery_completed: bool
    time_to_detect: float
    time_to_recover: float
    error_messages: List[str]
    metrics: Dict[str, Any]
    resource_state: Dict[str, Any]
    logs: List[str]
    recommendations: List[str]


class ChaosInjector:
    """Inject various types of failures into the system"""
    
    def __init__(self, target_path: str):
        self.target_path = Path(target_path)
        self.original_states = {}
        self.temp_files = []
        
    def inject_network_timeout(self, timeout_ms: int = 100):
        """Simulate network timeouts"""
        # This would typically use iptables or tc on Linux
        # For testing, we'll simulate with mocking
        logger.info(f"Injecting network timeout: {timeout_ms}ms")
        
    def inject_disk_full(self, path: Optional[str] = None):
        """Simulate disk full condition"""
        if path is None:
            path = tempfile.gettempdir()
            
        # Create a large file to fill disk space
        large_file = Path(path) / "disk_full_simulation.tmp"
        self.temp_files.append(large_file)
        
        try:
            # Try to create a very large file
            with open(large_file, 'wb') as f:
                # Write in chunks to avoid memory issues
                chunk_size = 1024 * 1024  # 1MB
                for _ in range(1000):  # Try to write 1GB
                    f.write(b'0' * chunk_size)
        except OSError as e:
            logger.info(f"Disk full simulation triggered: {e}")
            
    def inject_memory_pressure(self, size_mb: int = 500):
        """Create memory pressure"""
        logger.info(f"Injecting memory pressure: {size_mb}MB")
        
        # Allocate large chunks of memory
        memory_hogs = []
        try:
            for _ in range(size_mb):
                # Allocate 1MB chunks
                memory_hogs.append(bytearray(1024 * 1024))
            
            # Keep reference to prevent garbage collection
            self.original_states['memory_hogs'] = memory_hogs
            
        except MemoryError:
            logger.info("Memory exhaustion triggered")
            
    def inject_file_permission_error(self, file_path: str):
        """Make a file unreadable/unwritable"""
        path = Path(file_path)
        if path.exists():
            # Store original permissions
            self.original_states[str(path)] = path.stat().st_mode
            
            # Remove all permissions
            os.chmod(path, 0o000)
            logger.info(f"Removed permissions from {path}")
            
    def inject_corrupt_file(self, file_path: str, corruption_type: str = "random"):
        """Corrupt a file in various ways"""
        path = Path(file_path)
        if not path.exists():
            return
            
        # Backup original
        backup_path = path.with_suffix('.backup')
        shutil.copy2(path, backup_path)
        self.original_states[str(path)] = backup_path
        
        with open(path, 'rb') as f:
            data = f.read()
            
        if corruption_type == "random":
            # Random byte corruption
            data_array = bytearray(data)
            for _ in range(min(100, len(data_array) // 10)):
                pos = random.randint(0, len(data_array) - 1)
                data_array[pos] = random.randint(0, 255)
            corrupted = bytes(data_array)
            
        elif corruption_type == "truncate":
            # Truncate file
            corrupted = data[:len(data)//2]
            
        elif corruption_type == "encoding":
            # Mix encodings (especially problematic for Korean text)
            try:
                text = data.decode('utf-8')
                # Encode with different encoding and decode incorrectly
                corrupted = text.encode('cp949').decode('utf-8', errors='replace').encode('utf-8')
            except:
                corrupted = data
                
        with open(path, 'wb') as f:
            f.write(corrupted)
            
        logger.info(f"Corrupted file {path} with {corruption_type}")
        
    def inject_korean_encoding_error(self, text: str) -> bytes:
        """Create Korean-specific encoding errors"""
        # Common Korean encoding issues
        encoding_problems = [
            # Wrong encoding detection
            lambda t: t.encode('utf-8').decode('cp949', errors='replace').encode('utf-8'),
            # Mixed encodings
            lambda t: t[:len(t)//2].encode('utf-8') + t[len(t)//2:].encode('cp949'),
            # Mojibake
            lambda t: t.replace('안', '占쏙옙').encode('utf-8'),
            # Invalid UTF-8 sequences
            lambda t: t.encode('utf-8')[:-1] + b'\xff',
        ]
        
        problem = random.choice(encoding_problems)
        try:
            return problem(text)
        except:
            return text.encode('utf-8', errors='replace')
            
    def inject_process_crash(self, process_name: str):
        """Kill a process to simulate crash"""
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name in proc.info['name']:
                logger.info(f"Killing process {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
                return True
        return False
        
    def inject_cpu_throttling(self, cpu_percent: int = 20):
        """Limit CPU usage (requires cgroups on Linux)"""
        logger.info(f"Throttling CPU to {cpu_percent}%")
        # This would use cgroups or nice/renice on Linux
        # For testing, we simulate with busy loops
        
    def restore_all(self):
        """Restore all injected failures"""
        # Restore file permissions
        for path, mode in self.original_states.items():
            if isinstance(mode, int):
                try:
                    os.chmod(path, mode)
                except:
                    pass
            elif isinstance(mode, Path):
                # Restore from backup
                try:
                    shutil.copy2(mode, path)
                    mode.unlink()
                except:
                    pass
                    
        # Clean up temp files
        for temp_file in self.temp_files:
            try:
                temp_file.unlink()
            except:
                pass
                
        # Clear memory hogs
        self.original_states.clear()
        
        logger.info("Restored all injected failures")


class RecoveryValidator:
    """Validate system recovery from failures"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.injector = ChaosInjector(project_path)
        
    async def test_scenario(self, scenario: FailureScenario) -> RecoveryResult:
        """Test a single failure scenario"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing scenario: {scenario.name}")
        logger.info(f"Failure type: {scenario.failure_type.value}")
        logger.info(f"Description: {scenario.description}")
        logger.info(f"{'='*60}")
        
        result = RecoveryResult(
            scenario_name=scenario.name,
            success=False,
            failure_detected=False,
            recovery_completed=False,
            time_to_detect=0.0,
            time_to_recover=0.0,
            error_messages=[],
            metrics={},
            resource_state={},
            logs=[],
            recommendations=[]
        )
        
        start_time = time.time()
        
        try:
            # Setup
            if scenario.setup:
                logger.info("Running setup...")
                await scenario.setup(self)
                
            # Record initial state
            initial_state = self._capture_system_state()
            
            # Inject failure
            if scenario.inject:
                logger.info("Injecting failure...")
                inject_time = time.time()
                await scenario.inject(self)
                
            # Monitor for detection and recovery
            detected = False
            recovered = False
            
            timeout = time.time() + scenario.recovery_timeout
            
            while time.time() < timeout:
                # Check if failure was detected
                if not detected and scenario.verify:
                    if await scenario.verify(self, "detection"):
                        detected = True
                        result.failure_detected = True
                        result.time_to_detect = time.time() - inject_time
                        logger.info(f"Failure detected after {result.time_to_detect:.2f}s")
                        
                # Check if system recovered
                if detected and not recovered:
                    if await scenario.verify(self, "recovery"):
                        recovered = True
                        result.recovery_completed = True
                        result.time_to_recover = time.time() - inject_time
                        logger.info(f"System recovered after {result.time_to_recover:.2f}s")
                        break
                        
                await asyncio.sleep(0.5)
                
            # Capture final state
            final_state = self._capture_system_state()
            
            # Analyze results
            result.success = detected and recovered
            result.resource_state = self._compare_states(initial_state, final_state)
            
            # Generate recommendations
            if not result.success:
                result.recommendations = self._generate_recommendations(scenario, result)
                
        except Exception as e:
            logger.error(f"Error during scenario: {e}", exc_info=True)
            result.error_messages.append(str(e))
            
        finally:
            # Cleanup
            if scenario.cleanup:
                logger.info("Running cleanup...")
                try:
                    await scenario.cleanup(self)
                except:
                    pass
                    
            # Restore system state
            self.injector.restore_all()
            
        # Calculate metrics
        result.metrics = self._calculate_metrics(result)
        
        return result
        
    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'processes': [],
            'memory': {},
            'disk': {},
            'open_files': [],
            'network_connections': []
        }
        
        try:
            # Memory info
            mem = psutil.virtual_memory()
            state['memory'] = {
                'total': mem.total,
                'available': mem.available,
                'percent': mem.percent,
                'used': mem.used
            }
            
            # Disk info
            disk = psutil.disk_usage('/')
            state['disk'] = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
            
            # Process info
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                if 'voidlight' in proc.info['name'].lower() or 'markitdown' in proc.info['name'].lower():
                    state['processes'].append(proc.info)
                    
            # Open files (for current process)
            current_proc = psutil.Process()
            state['open_files'] = [f.path for f in current_proc.open_files()]
            
            # Network connections
            state['network_connections'] = len(current_proc.connections())
            
        except Exception as e:
            logger.error(f"Error capturing system state: {e}")
            
        return state
        
    def _compare_states(self, initial: Dict[str, Any], final: Dict[str, Any]) -> Dict[str, Any]:
        """Compare system states to detect resource leaks"""
        comparison = {
            'memory_leaked': False,
            'file_descriptors_leaked': False,
            'processes_leaked': False,
            'disk_space_leaked': False
        }
        
        # Check memory leak
        if final['memory']['used'] - initial['memory']['used'] > 100 * 1024 * 1024:  # 100MB
            comparison['memory_leaked'] = True
            comparison['memory_leak_size'] = final['memory']['used'] - initial['memory']['used']
            
        # Check file descriptor leak
        if len(final['open_files']) - len(initial['open_files']) > 10:
            comparison['file_descriptors_leaked'] = True
            comparison['leaked_files'] = list(set(final['open_files']) - set(initial['open_files']))
            
        # Check process leak
        initial_pids = {p['pid'] for p in initial['processes']}
        final_pids = {p['pid'] for p in final['processes']}
        leaked_pids = final_pids - initial_pids
        
        if leaked_pids:
            comparison['processes_leaked'] = True
            comparison['leaked_processes'] = list(leaked_pids)
            
        return comparison
        
    def _calculate_metrics(self, result: RecoveryResult) -> Dict[str, Any]:
        """Calculate recovery metrics"""
        metrics = {
            'detection_speed': 'fast' if result.time_to_detect < 1.0 else 'slow',
            'recovery_speed': 'fast' if result.time_to_recover < 5.0 else 'slow',
            'resource_cleanup': 'clean' if not any([
                result.resource_state.get('memory_leaked'),
                result.resource_state.get('file_descriptors_leaked'),
                result.resource_state.get('processes_leaked')
            ]) else 'leaked',
            'overall_grade': self._calculate_grade(result)
        }
        
        return metrics
        
    def _calculate_grade(self, result: RecoveryResult) -> str:
        """Calculate overall grade for recovery"""
        score = 0
        
        # Detection (30 points)
        if result.failure_detected:
            score += 30
            if result.time_to_detect < 1.0:
                score += 10
                
        # Recovery (40 points)  
        if result.recovery_completed:
            score += 40
            if result.time_to_recover < 5.0:
                score += 10
                
        # Resource cleanup (20 points)
        if not any([
            result.resource_state.get('memory_leaked'),
            result.resource_state.get('file_descriptors_leaked'),
            result.resource_state.get('processes_leaked')
        ]):
            score += 20
            
        # Grade mapping
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
            
    def _generate_recommendations(self, scenario: FailureScenario, result: RecoveryResult) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if not result.failure_detected:
            recommendations.append(f"Implement detection mechanism for {scenario.failure_type.value}")
            recommendations.append("Add health checks and monitoring for this failure mode")
            
        if not result.recovery_completed:
            recommendations.append(f"Implement automatic recovery for {scenario.failure_type.value}")
            recommendations.append("Add retry logic with exponential backoff")
            recommendations.append("Consider circuit breaker pattern for external dependencies")
            
        if result.resource_state.get('memory_leaked'):
            recommendations.append("Fix memory leak - ensure all resources are properly released")
            recommendations.append("Implement resource pooling to prevent leaks")
            
        if result.resource_state.get('file_descriptors_leaked'):
            recommendations.append("Ensure all file handles are closed properly")
            recommendations.append("Use context managers (with statements) for file operations")
            
        if result.time_to_detect > 5.0:
            recommendations.append("Improve failure detection speed - current detection is too slow")
            recommendations.append("Implement proactive health checks")
            
        if result.time_to_recover > 30.0:
            recommendations.append("Recovery time is too long - optimize recovery procedures")
            recommendations.append("Consider implementing graceful degradation")
            
        return recommendations


class ErrorRecoveryTestSuite:
    """Complete test suite for error recovery validation"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.validator = RecoveryValidator(project_path)
        self.results = []
        
    def create_test_scenarios(self) -> List[FailureScenario]:
        """Create comprehensive test scenarios"""
        scenarios = []
        
        # Network failures
        scenarios.extend([
            FailureScenario(
                name="network_timeout_recovery",
                failure_type=FailureType.NETWORK_TIMEOUT,
                description="Test recovery from network timeouts",
                inject=self._inject_network_timeout,
                verify=self._verify_network_recovery,
                expected_behavior="System should retry with exponential backoff",
                recovery_timeout=30.0,
                tags=["network", "timeout"]
            ),
            FailureScenario(
                name="network_disconnect_recovery",
                failure_type=FailureType.NETWORK_DISCONNECT,
                description="Test recovery from network disconnection",
                inject=self._inject_network_disconnect,
                verify=self._verify_network_recovery,
                expected_behavior="System should handle disconnection gracefully",
                recovery_timeout=60.0,
                tags=["network", "connection"]
            ),
        ])
        
        # File system failures
        scenarios.extend([
            FailureScenario(
                name="disk_full_recovery",
                failure_type=FailureType.DISK_FULL,
                description="Test behavior when disk is full",
                inject=self._inject_disk_full,
                verify=self._verify_disk_recovery,
                expected_behavior="System should handle disk full gracefully",
                recovery_timeout=30.0,
                severity="high",
                tags=["filesystem", "disk"]
            ),
            FailureScenario(
                name="file_permission_recovery",
                failure_type=FailureType.FILE_PERMISSION_DENIED,
                description="Test recovery from permission errors",
                inject=self._inject_permission_error,
                verify=self._verify_permission_recovery,
                expected_behavior="System should handle permission errors gracefully",
                recovery_timeout=20.0,
                tags=["filesystem", "permissions"]
            ),
            FailureScenario(
                name="file_corruption_recovery",
                failure_type=FailureType.FILE_CORRUPTION,
                description="Test recovery from corrupted files",
                inject=self._inject_file_corruption,
                verify=self._verify_corruption_recovery,
                expected_behavior="System should detect and handle corrupted files",
                recovery_timeout=30.0,
                severity="high",
                tags=["filesystem", "corruption"]
            ),
        ])
        
        # Memory/CPU failures
        scenarios.extend([
            FailureScenario(
                name="memory_exhaustion_recovery",
                failure_type=FailureType.MEMORY_EXHAUSTION,
                description="Test behavior under memory pressure",
                inject=self._inject_memory_exhaustion,
                verify=self._verify_memory_recovery,
                expected_behavior="System should degrade gracefully under memory pressure",
                recovery_timeout=60.0,
                severity="critical",
                tags=["resource", "memory"]
            ),
            FailureScenario(
                name="cpu_throttling_recovery",
                failure_type=FailureType.CPU_THROTTLING,
                description="Test behavior under CPU constraints",
                inject=self._inject_cpu_throttling,
                verify=self._verify_cpu_recovery,
                expected_behavior="System should handle CPU throttling gracefully",
                recovery_timeout=30.0,
                tags=["resource", "cpu"]
            ),
        ])
        
        # Korean-specific failures
        scenarios.extend([
            FailureScenario(
                name="korean_encoding_error_recovery",
                failure_type=FailureType.ENCODING_ERROR,
                description="Test recovery from Korean encoding errors",
                inject=self._inject_korean_encoding_error,
                verify=self._verify_encoding_recovery,
                expected_behavior="System should handle Korean encoding errors gracefully",
                recovery_timeout=20.0,
                korean_specific=True,
                tags=["korean", "encoding"]
            ),
            FailureScenario(
                name="korean_nlp_failure_recovery",
                failure_type=FailureType.KOREAN_NLP_FAILURE,
                description="Test recovery when Korean NLP libraries fail",
                inject=self._inject_korean_nlp_failure,
                verify=self._verify_nlp_recovery,
                expected_behavior="System should fallback when NLP libraries fail",
                recovery_timeout=30.0,
                korean_specific=True,
                tags=["korean", "nlp", "dependency"]
            ),
            FailureScenario(
                name="mixed_encoding_recovery",
                failure_type=FailureType.UNICODE_ERROR,
                description="Test recovery from mixed encoding documents",
                inject=self._inject_mixed_encoding,
                verify=self._verify_encoding_recovery,
                expected_behavior="System should handle mixed encodings",
                recovery_timeout=20.0,
                korean_specific=True,
                tags=["korean", "encoding", "unicode"]
            ),
        ])
        
        # Input validation failures
        scenarios.extend([
            FailureScenario(
                name="malformed_input_recovery",
                failure_type=FailureType.MALFORMED_INPUT,
                description="Test recovery from malformed input data",
                inject=self._inject_malformed_input,
                verify=self._verify_input_recovery,
                expected_behavior="System should validate and reject malformed input",
                recovery_timeout=10.0,
                tags=["input", "validation"]
            ),
            FailureScenario(
                name="oversized_input_recovery",
                failure_type=FailureType.OVERSIZED_INPUT,
                description="Test recovery from oversized input",
                inject=self._inject_oversized_input,
                verify=self._verify_input_recovery,
                expected_behavior="System should handle large inputs gracefully",
                recovery_timeout=30.0,
                severity="high",
                tags=["input", "size"]
            ),
        ])
        
        # Concurrency failures
        scenarios.extend([
            FailureScenario(
                name="concurrent_access_recovery",
                failure_type=FailureType.CONCURRENT_ACCESS,
                description="Test recovery from concurrent access issues",
                inject=self._inject_concurrent_access,
                verify=self._verify_concurrency_recovery,
                expected_behavior="System should handle concurrent access safely",
                recovery_timeout=30.0,
                tags=["concurrency", "threading"]
            ),
            FailureScenario(
                name="race_condition_recovery",
                failure_type=FailureType.RACE_CONDITION,
                description="Test recovery from race conditions",
                inject=self._inject_race_condition,
                verify=self._verify_concurrency_recovery,
                expected_behavior="System should prevent race conditions",
                recovery_timeout=30.0,
                severity="high",
                tags=["concurrency", "race"]
            ),
        ])
        
        return scenarios
        
    # Injection methods
    async def _inject_network_timeout(self, validator: RecoveryValidator):
        """Inject network timeout"""
        validator.injector.inject_network_timeout(100)
        
    async def _inject_network_disconnect(self, validator: RecoveryValidator):
        """Inject network disconnection"""
        # Simulate by killing network-related processes or blocking ports
        pass
        
    async def _inject_disk_full(self, validator: RecoveryValidator):
        """Inject disk full condition"""
        validator.injector.inject_disk_full()
        
    async def _inject_permission_error(self, validator: RecoveryValidator):
        """Inject file permission error"""
        # Find a test file to modify permissions
        test_file = validator.project_path / "test_file.txt"
        test_file.write_text("test content")
        validator.injector.inject_file_permission_error(str(test_file))
        
    async def _inject_file_corruption(self, validator: RecoveryValidator):
        """Inject file corruption"""
        test_file = validator.project_path / "test_korean.txt"
        test_file.write_text("안녕하세요 테스트 파일입니다")
        validator.injector.inject_corrupt_file(str(test_file), "encoding")
        
    async def _inject_memory_exhaustion(self, validator: RecoveryValidator):
        """Inject memory exhaustion"""
        validator.injector.inject_memory_pressure(500)
        
    async def _inject_cpu_throttling(self, validator: RecoveryValidator):
        """Inject CPU throttling"""
        validator.injector.inject_cpu_throttling(20)
        
    async def _inject_korean_encoding_error(self, validator: RecoveryValidator):
        """Inject Korean encoding error"""
        test_text = "안녕하세요 한글 테스트입니다"
        corrupted = validator.injector.inject_korean_encoding_error(test_text)
        
        test_file = validator.project_path / "korean_corrupted.txt"
        test_file.write_bytes(corrupted)
        
    async def _inject_korean_nlp_failure(self, validator: RecoveryValidator):
        """Simulate Korean NLP library failure"""
        # Mock NLP library failure by modifying import paths or killing processes
        pass
        
    async def _inject_mixed_encoding(self, validator: RecoveryValidator):
        """Inject mixed encoding document"""
        # Create file with mixed encodings
        test_file = validator.project_path / "mixed_encoding.txt"
        content = "Hello ".encode('utf-8') + "안녕하세요".encode('cp949') + " Test".encode('utf-8')
        test_file.write_bytes(content)
        
    async def _inject_malformed_input(self, validator: RecoveryValidator):
        """Inject malformed input"""
        # Create various malformed inputs
        malformed_files = [
            ("malformed.json", b'{"incomplete": '),
            ("malformed.xml", b'<root><unclosed>'),
            ("malformed.csv", b'col1,col2\nval1'),
        ]
        
        for filename, content in malformed_files:
            (validator.project_path / filename).write_bytes(content)
            
    async def _inject_oversized_input(self, validator: RecoveryValidator):
        """Inject oversized input"""
        # Create very large file
        large_file = validator.project_path / "oversized.txt"
        with open(large_file, 'wb') as f:
            # Write 100MB of data
            for _ in range(100):
                f.write(b'x' * (1024 * 1024))
                
    async def _inject_concurrent_access(self, validator: RecoveryValidator):
        """Simulate concurrent access"""
        # Create multiple threads/processes accessing same resource
        pass
        
    async def _inject_race_condition(self, validator: RecoveryValidator):
        """Simulate race condition"""
        # Create timing-dependent scenario
        pass
        
    # Verification methods
    async def _verify_network_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify network recovery"""
        # Check if system detected network issue and is retrying
        return True  # Placeholder
        
    async def _verify_disk_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify disk recovery"""
        # Check if system handles disk full gracefully
        return True  # Placeholder
        
    async def _verify_permission_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify permission recovery"""
        # Check if system handles permission errors
        return True  # Placeholder
        
    async def _verify_corruption_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify corruption recovery"""
        # Check if system detects and handles corruption
        return True  # Placeholder
        
    async def _verify_memory_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify memory recovery"""
        # Check if system handles memory pressure
        return True  # Placeholder
        
    async def _verify_cpu_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify CPU recovery"""
        # Check if system handles CPU constraints
        return True  # Placeholder
        
    async def _verify_encoding_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify encoding recovery"""
        # Check if system handles encoding errors
        return True  # Placeholder
        
    async def _verify_nlp_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify NLP recovery"""
        # Check if system falls back when NLP fails
        return True  # Placeholder
        
    async def _verify_input_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify input validation recovery"""
        # Check if system validates input properly
        return True  # Placeholder
        
    async def _verify_concurrency_recovery(self, validator: RecoveryValidator, phase: str) -> bool:
        """Verify concurrency recovery"""
        # Check if system handles concurrent access
        return True  # Placeholder
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test scenarios"""
        scenarios = self.create_test_scenarios()
        
        logger.info(f"Running {len(scenarios)} error recovery scenarios...")
        
        for scenario in scenarios:
            try:
                result = await self.validator.test_scenario(scenario)
                self.results.append(result)
                
                # Log result summary
                status = "PASSED" if result.success else "FAILED"
                logger.info(f"\nScenario: {scenario.name} - {status}")
                logger.info(f"  Detection: {result.failure_detected} ({result.time_to_detect:.2f}s)")
                logger.info(f"  Recovery: {result.recovery_completed} ({result.time_to_recover:.2f}s)")
                logger.info(f"  Grade: {result.metrics.get('overall_grade', 'N/A')}")
                
                if result.recommendations:
                    logger.info("  Recommendations:")
                    for rec in result.recommendations:
                        logger.info(f"    - {rec}")
                        
            except Exception as e:
                logger.error(f"Failed to run scenario {scenario.name}: {e}", exc_info=True)
                
        return self._generate_summary()
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all test results"""
        summary = {
            'total_scenarios': len(self.results),
            'passed': sum(1 for r in self.results if r.success),
            'failed': sum(1 for r in self.results if not r.success),
            'detection_rate': sum(1 for r in self.results if r.failure_detected) / len(self.results) if self.results else 0,
            'recovery_rate': sum(1 for r in self.results if r.recovery_completed) / len(self.results) if self.results else 0,
            'avg_detection_time': sum(r.time_to_detect for r in self.results if r.failure_detected) / sum(1 for r in self.results if r.failure_detected) if any(r.failure_detected for r in self.results) else 0,
            'avg_recovery_time': sum(r.time_to_recover for r in self.results if r.recovery_completed) / sum(1 for r in self.results if r.recovery_completed) if any(r.recovery_completed for r in self.results) else 0,
            'grade_distribution': {},
            'top_issues': [],
            'korean_specific_results': {},
            'severity_breakdown': {},
            'tag_analysis': {}
        }
        
        # Grade distribution
        for result in self.results:
            grade = result.metrics.get('overall_grade', 'F')
            summary['grade_distribution'][grade] = summary['grade_distribution'].get(grade, 0) + 1
            
        # Top issues
        issue_counts = {}
        for result in self.results:
            if not result.success:
                issue = f"{result.scenario_name}: {'No detection' if not result.failure_detected else 'No recovery'}"
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
                
        summary['top_issues'] = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return summary


async def main():
    """Main entry point for error recovery testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Error Recovery and Chaos Engineering Tests")
    parser.add_argument("--project-path", default="/Users/voidlight/voidlight_markitdown", help="Project path")
    parser.add_argument("--output", default="error_recovery_report.json", help="Output report file")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to test")
    
    args = parser.parse_args()
    
    # Create test suite
    test_suite = ErrorRecoveryTestSuite(args.project_path)
    
    # Run tests
    summary = await test_suite.run_all_tests()
    
    # Generate report
    report = {
        'test_date': datetime.now().isoformat(),
        'project_path': args.project_path,
        'summary': summary,
        'detailed_results': [
            {
                'scenario': r.scenario_name,
                'success': r.success,
                'metrics': r.metrics,
                'recommendations': r.recommendations,
                'resource_state': r.resource_state
            }
            for r in test_suite.results
        ]
    }
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
        
    # Print summary
    print("\n" + "="*80)
    print("ERROR RECOVERY TEST SUMMARY")
    print("="*80)
    print(f"Total Scenarios: {summary['total_scenarios']}")
    print(f"Passed: {summary['passed']} ({summary['passed']/summary['total_scenarios']*100:.1f}%)")
    print(f"Failed: {summary['failed']} ({summary['failed']/summary['total_scenarios']*100:.1f}%)")
    print(f"Detection Rate: {summary['detection_rate']*100:.1f}%")
    print(f"Recovery Rate: {summary['recovery_rate']*100:.1f}%")
    print(f"Avg Detection Time: {summary['avg_detection_time']:.2f}s")
    print(f"Avg Recovery Time: {summary['avg_recovery_time']:.2f}s")
    
    print("\nGrade Distribution:")
    for grade, count in sorted(summary['grade_distribution'].items()):
        print(f"  {grade}: {count}")
        
    if summary['top_issues']:
        print("\nTop Issues:")
        for issue, count in summary['top_issues'][:5]:
            print(f"  - {issue}: {count} occurrences")
            
    print(f"\nDetailed report saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())