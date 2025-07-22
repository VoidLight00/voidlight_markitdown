#!/usr/bin/env python3
"""
Quick integration test to verify the enhanced test suite works
"""

import asyncio
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def quick_test():
    """Run a quick test of the enhanced integration suite"""
    print("Running quick integration test...")
    
    # Import the enhanced test module
    from test_mcp_integration_enhanced import MCPTestServer, TestMetrics
    
    # Create metrics tracker
    metrics = TestMetrics()
    
    # Test STDIO mode
    print("\nTesting STDIO mode startup...")
    stdio_server = MCPTestServer(mode="stdio")
    
    if await stdio_server.start():
        print("✓ STDIO server started successfully")
        metrics.add_result("Quick Test", "STDIO Start", True, "Server started")
        
        # Check if process is running
        if stdio_server.process and stdio_server.process.poll() is None:
            print("✓ STDIO server process is running")
            metrics.add_result("Quick Test", "STDIO Process", True, "Process active")
        else:
            print("✗ STDIO server process not running")
            metrics.add_result("Quick Test", "STDIO Process", False, "Process not active")
            
        await stdio_server.stop()
        print("✓ STDIO server stopped")
    else:
        print("✗ Failed to start STDIO server")
        metrics.add_result("Quick Test", "STDIO Start", False, "Failed to start")
        
    # Test HTTP mode
    print("\nTesting HTTP mode startup...")
    http_server = MCPTestServer(mode="http")
    
    if await http_server.start():
        print(f"✓ HTTP server started on port {http_server.port}")
        metrics.add_result("Quick Test", "HTTP Start", True, f"Server started on port {http_server.port}")
        
        # Test server is accessible
        import requests
        try:
            response = requests.get(f"http://localhost:{http_server.port}/", timeout=5)
            print(f"✓ HTTP server responding with status {response.status_code}")
            metrics.add_result("Quick Test", "HTTP Health", True, f"Status {response.status_code}")
        except Exception as e:
            print(f"✗ HTTP server not responding: {e}")
            metrics.add_result("Quick Test", "HTTP Health", False, str(e))
            
        await http_server.stop()
        print("✓ HTTP server stopped")
    else:
        print("✗ Failed to start HTTP server")
        metrics.add_result("Quick Test", "HTTP Start", False, "Failed to start")
        
    # Print summary
    summary = metrics.get_summary()
    print(f"\nQuick Test Summary:")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    return summary['failed_tests'] == 0

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)