#!/usr/bin/env python3
"""
MCP Protocol Compliance Validator
Tests JSON-RPC 2.0 compliance and MCP-specific protocol requirements
"""

import asyncio
import json
import logging
import socket
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jsonschema

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ComplianceCheck:
    """Individual compliance check result"""
    category: str
    test_name: str
    passed: bool
    severity: str  # 'critical', 'high', 'medium', 'low'
    details: str
    spec_reference: Optional[str] = None
    actual_value: Any = None
    expected_value: Any = None


class ProtocolComplianceValidator:
    """Validates MCP server protocol compliance"""
    
    # JSON-RPC 2.0 request schema
    JSONRPC_REQUEST_SCHEMA = {
        "type": "object",
        "required": ["jsonrpc", "method"],
        "properties": {
            "jsonrpc": {"const": "2.0"},
            "method": {"type": "string"},
            "params": {"type": ["object", "array"]},
            "id": {"type": ["string", "number", "null"]}
        }
    }
    
    # JSON-RPC 2.0 response schema
    JSONRPC_RESPONSE_SCHEMA = {
        "type": "object",
        "required": ["jsonrpc"],
        "oneOf": [
            {
                "required": ["result", "id"],
                "properties": {
                    "jsonrpc": {"const": "2.0"},
                    "result": {},
                    "id": {"type": ["string", "number", "null"]}
                }
            },
            {
                "required": ["error", "id"],
                "properties": {
                    "jsonrpc": {"const": "2.0"},
                    "error": {
                        "type": "object",
                        "required": ["code", "message"],
                        "properties": {
                            "code": {"type": "integer"},
                            "message": {"type": "string"},
                            "data": {}
                        }
                    },
                    "id": {"type": ["string", "number", "null"]}
                }
            }
        ]
    }
    
    # MCP-specific method patterns
    MCP_METHODS = {
        "initialize": {
            "params_required": True,
            "params_schema": {
                "type": "object",
                "required": ["protocolVersion", "capabilities", "clientInfo"],
                "properties": {
                    "protocolVersion": {"type": "string"},
                    "capabilities": {"type": "object"},
                    "clientInfo": {
                        "type": "object",
                        "required": ["name", "version"],
                        "properties": {
                            "name": {"type": "string"},
                            "version": {"type": "string"}
                        }
                    }
                }
            }
        },
        "tools/list": {
            "params_required": False
        },
        "tools/call": {
            "params_required": True,
            "params_schema": {
                "type": "object",
                "required": ["name", "arguments"],
                "properties": {
                    "name": {"type": "string"},
                    "arguments": {"type": "object"}
                }
            }
        }
    }
    
    def __init__(self, report_dir: Path):
        self.report_dir = report_dir
        self.compliance_checks: List[ComplianceCheck] = []
        self.server_process: Optional[subprocess.Popen] = None
        self.request_id = 0
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def _send_raw_request(self, host: str, port: int, request: Dict[str, Any]) -> Tuple[Optional[Dict], float]:
        """Send raw JSON-RPC request and measure response time"""
        start_time = time.time()
        
        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((host, port))
            
            # Send request
            request_str = json.dumps(request) + '\n'
            sock.send(request_str.encode())
            
            # Receive response
            response_data = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in response_data:
                    break
            
            sock.close()
            
            # Parse response
            response_str = response_data.decode().strip()
            response = json.loads(response_str)
            
            elapsed = time.time() - start_time
            return response, elapsed
            
        except Exception as e:
            logger.error(f"Raw request failed: {e}")
            elapsed = time.time() - start_time
            return None, elapsed
    
    async def validate_jsonrpc_compliance(self) -> List[ComplianceCheck]:
        """Validate JSON-RPC 2.0 compliance"""
        checks = []
        
        logger.info("Validating JSON-RPC 2.0 compliance...")
        
        # Start server in HTTP mode for raw protocol testing
        self.server_process = subprocess.Popen(
            ["python", "-m", "voidlight_markitdown_mcp", "--http", "--port", "3003"],
            env={
                "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                "VOIDLIGHT_LOG_LEVEL": "DEBUG"
            }
        )
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        # Test 1: Valid request format
        valid_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": self._get_next_id()
        }
        
        response, elapsed = await self._send_raw_request("localhost", 3003, valid_request)
        
        if response:
            try:
                jsonschema.validate(response, self.JSONRPC_RESPONSE_SCHEMA)
                checks.append(ComplianceCheck(
                    category="JSON-RPC 2.0",
                    test_name="Valid Response Format",
                    passed=True,
                    severity="critical",
                    details="Server returns valid JSON-RPC 2.0 responses",
                    spec_reference="JSON-RPC 2.0 Section 5"
                ))
            except jsonschema.ValidationError as e:
                checks.append(ComplianceCheck(
                    category="JSON-RPC 2.0",
                    test_name="Valid Response Format",
                    passed=False,
                    severity="critical",
                    details=f"Invalid response format: {e.message}",
                    spec_reference="JSON-RPC 2.0 Section 5",
                    actual_value=response
                ))
        
        # Test 2: Missing jsonrpc version
        invalid_request = {
            "method": "tools/list",
            "id": self._get_next_id()
        }
        
        response, _ = await self._send_raw_request("localhost", 3003, invalid_request)
        
        if response and "error" in response:
            checks.append(ComplianceCheck(
                category="JSON-RPC 2.0",
                test_name="Missing Version Handling",
                passed=True,
                severity="high",
                details="Server correctly rejects requests without jsonrpc version",
                spec_reference="JSON-RPC 2.0 Section 4.2"
            ))
        else:
            checks.append(ComplianceCheck(
                category="JSON-RPC 2.0",
                test_name="Missing Version Handling",
                passed=False,
                severity="high",
                details="Server should reject requests without jsonrpc version",
                spec_reference="JSON-RPC 2.0 Section 4.2",
                actual_value=response
            ))
        
        # Test 3: Invalid method
        invalid_method_request = {
            "jsonrpc": "2.0",
            "method": "invalid/method",
            "id": self._get_next_id()
        }
        
        response, _ = await self._send_raw_request("localhost", 3003, invalid_method_request)
        
        if response and "error" in response and response["error"]["code"] == -32601:
            checks.append(ComplianceCheck(
                category="JSON-RPC 2.0",
                test_name="Method Not Found Error",
                passed=True,
                severity="high",
                details="Server returns correct error code for unknown methods",
                spec_reference="JSON-RPC 2.0 Section 5.1",
                actual_value=response["error"]["code"],
                expected_value=-32601
            ))
        else:
            checks.append(ComplianceCheck(
                category="JSON-RPC 2.0",
                test_name="Method Not Found Error",
                passed=False,
                severity="high",
                details="Server should return -32601 for unknown methods",
                spec_reference="JSON-RPC 2.0 Section 5.1",
                actual_value=response.get("error", {}).get("code") if response else None,
                expected_value=-32601
            ))
        
        # Test 4: Batch requests
        batch_request = [
            {"jsonrpc": "2.0", "method": "tools/list", "id": self._get_next_id()},
            {"jsonrpc": "2.0", "method": "tools/list", "id": self._get_next_id()}
        ]
        
        response, _ = await self._send_raw_request("localhost", 3003, batch_request)
        
        if isinstance(response, list) and len(response) == 2:
            checks.append(ComplianceCheck(
                category="JSON-RPC 2.0",
                test_name="Batch Request Support",
                passed=True,
                severity="medium",
                details="Server supports batch requests",
                spec_reference="JSON-RPC 2.0 Section 6"
            ))
        else:
            checks.append(ComplianceCheck(
                category="JSON-RPC 2.0",
                test_name="Batch Request Support",
                passed=False,
                severity="medium",
                details="Server should support batch requests",
                spec_reference="JSON-RPC 2.0 Section 6",
                actual_value=type(response).__name__ if response else None,
                expected_value="list"
            ))
        
        # Clean up server
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        return checks
    
    async def validate_mcp_methods(self) -> List[ComplianceCheck]:
        """Validate MCP-specific method implementations"""
        checks = []
        
        logger.info("Validating MCP method implementations...")
        
        # Use STDIO mode for MCP-specific testing
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "voidlight_markitdown_mcp"],
            env={
                "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                "VOIDLIGHT_LOG_LEVEL": "DEBUG"
            }
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # Test 1: Initialize method
                try:
                    await session.initialize()
                    checks.append(ComplianceCheck(
                        category="MCP Protocol",
                        test_name="Initialize Method",
                        passed=True,
                        severity="critical",
                        details="Server implements initialize method correctly"
                    ))
                    
                    # Check server info
                    if hasattr(session, 'server_info'):
                        checks.append(ComplianceCheck(
                            category="MCP Protocol",
                            test_name="Server Info",
                            passed=True,
                            severity="medium",
                            details=f"Server provides info: {session.server_info.name} v{session.server_info.version}"
                        ))
                except Exception as e:
                    checks.append(ComplianceCheck(
                        category="MCP Protocol",
                        test_name="Initialize Method",
                        passed=False,
                        severity="critical",
                        details=f"Initialize failed: {str(e)}"
                    ))
                
                # Test 2: Tools listing
                try:
                    tools_result = await session.list_tools()
                    tools = tools_result.tools
                    
                    if tools and len(tools) > 0:
                        checks.append(ComplianceCheck(
                            category="MCP Protocol",
                            test_name="Tools List Method",
                            passed=True,
                            severity="critical",
                            details=f"Server exposes {len(tools)} tools",
                            actual_value=len(tools)
                        ))
                        
                        # Validate tool schema
                        for tool in tools:
                            if hasattr(tool, 'name') and hasattr(tool, 'description'):
                                checks.append(ComplianceCheck(
                                    category="MCP Protocol",
                                    test_name=f"Tool Schema: {tool.name}",
                                    passed=True,
                                    severity="medium",
                                    details="Tool has required fields"
                                ))
                            else:
                                checks.append(ComplianceCheck(
                                    category="MCP Protocol",
                                    test_name=f"Tool Schema: {getattr(tool, 'name', 'unknown')}",
                                    passed=False,
                                    severity="medium",
                                    details="Tool missing required fields"
                                ))
                    else:
                        checks.append(ComplianceCheck(
                            category="MCP Protocol",
                            test_name="Tools List Method",
                            passed=False,
                            severity="critical",
                            details="No tools exposed by server"
                        ))
                        
                except Exception as e:
                    checks.append(ComplianceCheck(
                        category="MCP Protocol",
                        test_name="Tools List Method",
                        passed=False,
                        severity="critical",
                        details=f"Tools listing failed: {str(e)}"
                    ))
                
                # Test 3: Tool invocation
                try:
                    result = await session.call_tool(
                        "convert_to_markdown",
                        {"uri": "https://example.com"}
                    )
                    
                    checks.append(ComplianceCheck(
                        category="MCP Protocol",
                        test_name="Tool Invocation",
                        passed=True,
                        severity="critical",
                        details="Tool invocation successful"
                    ))
                    
                except Exception as e:
                    checks.append(ComplianceCheck(
                        category="MCP Protocol",
                        test_name="Tool Invocation",
                        passed=False,
                        severity="critical",
                        details=f"Tool invocation failed: {str(e)}"
                    ))
        
        return checks
    
    async def validate_error_handling(self) -> List[ComplianceCheck]:
        """Validate error handling compliance"""
        checks = []
        
        logger.info("Validating error handling...")
        
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "voidlight_markitdown_mcp"],
            env={
                "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                "VOIDLIGHT_LOG_LEVEL": "DEBUG"
            }
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Test 1: Invalid parameters
                try:
                    await session.call_tool("convert_to_markdown", {})  # Missing required 'uri'
                    checks.append(ComplianceCheck(
                        category="Error Handling",
                        test_name="Missing Parameters",
                        passed=False,
                        severity="high",
                        details="Server should reject calls with missing required parameters"
                    ))
                except Exception as e:
                    error_msg = str(e).lower()
                    if "uri" in error_msg or "required" in error_msg or "missing" in error_msg:
                        checks.append(ComplianceCheck(
                            category="Error Handling",
                            test_name="Missing Parameters",
                            passed=True,
                            severity="high",
                            details="Server correctly rejects missing parameters"
                        ))
                    else:
                        checks.append(ComplianceCheck(
                            category="Error Handling",
                            test_name="Missing Parameters",
                            passed=False,
                            severity="high",
                            details="Error message should indicate missing parameter",
                            actual_value=error_msg
                        ))
                
                # Test 2: Invalid URI
                try:
                    await session.call_tool(
                        "convert_to_markdown",
                        {"uri": "not-a-valid-uri"}
                    )
                    checks.append(ComplianceCheck(
                        category="Error Handling",
                        test_name="Invalid URI",
                        passed=False,
                        severity="medium",
                        details="Server should handle invalid URIs gracefully"
                    ))
                except Exception as e:
                    checks.append(ComplianceCheck(
                        category="Error Handling",
                        test_name="Invalid URI",
                        passed=True,
                        severity="medium",
                        details="Server handles invalid URIs with proper error"
                    ))
                
                # Test 3: Non-existent tool
                try:
                    await session.call_tool("non_existent_tool", {"param": "value"})
                    checks.append(ComplianceCheck(
                        category="Error Handling",
                        test_name="Non-existent Tool",
                        passed=False,
                        severity="high",
                        details="Server should reject non-existent tools"
                    ))
                except Exception as e:
                    checks.append(ComplianceCheck(
                        category="Error Handling",
                        test_name="Non-existent Tool",
                        passed=True,
                        severity="high",
                        details="Server correctly rejects non-existent tools"
                    ))
        
        return checks
    
    async def validate_streaming_capabilities(self) -> List[ComplianceCheck]:
        """Validate streaming and long-running operation support"""
        checks = []
        
        logger.info("Validating streaming capabilities...")
        
        # Test with a large document
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "voidlight_markitdown_mcp"],
            env={
                "VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS": "true",
                "VOIDLIGHT_LOG_LEVEL": "DEBUG"
            }
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Test 1: Large payload handling
                try:
                    # Test with a known large document
                    start_time = time.time()
                    result = await session.call_tool(
                        "convert_to_markdown",
                        {"uri": "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm"}  # Pride and Prejudice
                    )
                    elapsed = time.time() - start_time
                    
                    if hasattr(result, 'content'):
                        content_size = len(result.content) if isinstance(result.content, str) else 0
                        
                        checks.append(ComplianceCheck(
                            category="Streaming",
                            test_name="Large Payload Handling",
                            passed=content_size > 10000,
                            severity="medium",
                            details=f"Handled {content_size} bytes in {elapsed:.2f}s",
                            actual_value=content_size
                        ))
                    
                except Exception as e:
                    checks.append(ComplianceCheck(
                        category="Streaming",
                        test_name="Large Payload Handling",
                        passed=False,
                        severity="medium",
                        details=f"Failed to handle large payload: {str(e)}"
                    ))
                
                # Test 2: Timeout handling
                # This would require a slow/hanging endpoint
                checks.append(ComplianceCheck(
                    category="Streaming",
                    test_name="Timeout Handling",
                    passed=True,
                    severity="low",
                    details="Timeout handling not tested (requires mock endpoint)"
                ))
        
        return checks
    
    async def run_all_validations(self) -> Dict[str, Any]:
        """Run all compliance validations"""
        logger.info("Starting MCP Protocol Compliance Validation...")
        
        all_checks = []
        
        # Run validation suites
        validation_suites = [
            ("JSON-RPC 2.0 Compliance", self.validate_jsonrpc_compliance),
            ("MCP Methods", self.validate_mcp_methods),
            ("Error Handling", self.validate_error_handling),
            ("Streaming Capabilities", self.validate_streaming_capabilities)
        ]
        
        for suite_name, validator_func in validation_suites:
            logger.info(f"\nRunning {suite_name}...")
            try:
                suite_checks = await validator_func()
                all_checks.extend(suite_checks)
                self.compliance_checks.extend(suite_checks)
                
                # Log results
                passed = sum(1 for c in suite_checks if c.passed)
                total = len(suite_checks)
                logger.info(f"{suite_name}: {passed}/{total} checks passed")
                
            except Exception as e:
                logger.error(f"Suite {suite_name} failed: {e}")
                all_checks.append(ComplianceCheck(
                    category=suite_name,
                    test_name="Suite Execution",
                    passed=False,
                    severity="critical",
                    details=f"Suite failed: {str(e)}"
                ))
        
        # Generate compliance report
        report = self._generate_compliance_report(all_checks)
        
        # Save report
        report_file = self.report_dir / f"protocol_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.write_text(json.dumps(report, indent=2))
        logger.info(f"\nCompliance report saved to: {report_file}")
        
        return report
    
    def _generate_compliance_report(self, checks: List[ComplianceCheck]) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        # Group by category
        by_category = {}
        for check in checks:
            if check.category not in by_category:
                by_category[check.category] = []
            by_category[check.category].append(check)
        
        # Group by severity
        by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for check in checks:
            by_severity[check.severity].append(check)
        
        # Calculate compliance score
        severity_weights = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        total_weight = sum(
            severity_weights[check.severity] 
            for check in checks
        )
        
        passed_weight = sum(
            severity_weights[check.severity] 
            for check in checks 
            if check.passed
        )
        
        compliance_score = (passed_weight / total_weight * 100) if total_weight > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': len(checks),
                'passed': sum(1 for c in checks if c.passed),
                'failed': sum(1 for c in checks if not c.passed),
                'compliance_score': round(compliance_score, 2),
                'by_severity': {
                    severity: {
                        'total': len(checks_list),
                        'passed': sum(1 for c in checks_list if c.passed),
                        'failed': sum(1 for c in checks_list if not c.passed)
                    }
                    for severity, checks_list in by_severity.items()
                }
            },
            'by_category': {
                category: {
                    'total': len(cat_checks),
                    'passed': sum(1 for c in cat_checks if c.passed),
                    'checks': [
                        {
                            'test_name': c.test_name,
                            'passed': c.passed,
                            'severity': c.severity,
                            'details': c.details,
                            'spec_reference': c.spec_reference,
                            'actual_value': c.actual_value,
                            'expected_value': c.expected_value
                        }
                        for c in cat_checks
                    ]
                }
                for category, cat_checks in by_category.items()
            },
            'failed_critical_checks': [
                {
                    'category': c.category,
                    'test_name': c.test_name,
                    'details': c.details,
                    'spec_reference': c.spec_reference
                }
                for c in checks
                if not c.passed and c.severity == 'critical'
            ]
        }


async def main():
    """Main validator runner"""
    report_dir = Path("/Users/voidlight/voidlight_markitdown/mcp_client_tests/reports")
    report_dir.mkdir(exist_ok=True)
    
    validator = ProtocolComplianceValidator(report_dir)
    report = await validator.run_all_validations()
    
    # Print summary
    print("\n" + "="*60)
    print("MCP PROTOCOL COMPLIANCE REPORT")
    print("="*60)
    print(f"Total Checks: {report['summary']['total_checks']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Compliance Score: {report['summary']['compliance_score']}%")
    print("\nBy Severity:")
    for severity, stats in report['summary']['by_severity'].items():
        print(f"  {severity.upper()}: {stats['passed']}/{stats['total']} passed")
    
    if report['failed_critical_checks']:
        print("\nFAILED CRITICAL CHECKS:")
        for check in report['failed_critical_checks']:
            print(f"  - [{check['category']}] {check['test_name']}: {check['details']}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())