#!/usr/bin/env python3
"""
Validate stress testing setup and dependencies
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_mcp_server():
    """Check MCP server binary"""
    print("\nChecking MCP server...")
    mcp_binary = Path("/Users/voidlight/voidlight_markitdown/mcp-env/bin/voidlight-markitdown-mcp")
    
    if mcp_binary.exists():
        print(f"✓ MCP server found: {mcp_binary}")
        
        # Try to run it with --help
        try:
            result = subprocess.run(
                [str(mcp_binary), "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ MCP server is executable")
                return True
            else:
                print("✗ MCP server failed to run")
                return False
        except Exception as e:
            print(f"✗ Error running MCP server: {e}")
            return False
    else:
        print(f"✗ MCP server not found at {mcp_binary}")
        return False

def check_dependencies():
    """Check required Python packages"""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        ("aiohttp", "HTTP client library"),
        ("websockets", "WebSocket support"),
        ("psutil", "System monitoring"),
        ("numpy", "Numerical operations"),
        ("pandas", "Data analysis"),
        ("plotly", "Visualization"),
        ("dash", "Dashboard framework"),
        ("matplotlib", "Plotting"),
        ("seaborn", "Statistical plots"),
        ("scipy", "Scientific computing")
    ]
    
    missing = []
    
    for package, description in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            print(f"✓ {package} - {description}")
        else:
            print(f"✗ {package} - {description} (MISSING)")
            missing.append(package)
            
    return len(missing) == 0, missing

def check_ports():
    """Check if required ports are available"""
    print("\nChecking port availability...")
    
    ports_to_check = [
        (3001, "MCP HTTP server"),
        (8050, "Monitoring dashboard")
    ]
    
    import socket
    
    all_available = True
    
    for port, description in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"⚠ Port {port} ({description}) is in use")
                all_available = False
            else:
                print(f"✓ Port {port} ({description}) is available")
        except Exception as e:
            print(f"✗ Error checking port {port}: {e}")
            all_available = False
            
    return all_available

def check_system_limits():
    """Check system resource limits"""
    print("\nChecking system limits...")
    
    try:
        import resource
        
        # Check file descriptor limit
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft < 1024:
            print(f"⚠ File descriptor limit is low: {soft} (recommended: 4096+)")
            print(f"  Run: ulimit -n 4096")
        else:
            print(f"✓ File descriptor limit: {soft}")
            
        # Check process limit
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_NPROC)
            if soft < 1024:
                print(f"⚠ Process limit is low: {soft}")
            else:
                print(f"✓ Process limit: {soft}")
        except:
            print("  Unable to check process limit")
            
        return True
    except Exception as e:
        print(f"✗ Error checking system limits: {e}")
        return False

def check_directories():
    """Check required directories"""
    print("\nChecking directories...")
    
    stress_test_dir = Path("/Users/voidlight/voidlight_markitdown/stress_testing")
    
    if stress_test_dir.exists():
        print(f"✓ Stress test directory exists")
        
        # Check for key files
        required_files = [
            "concurrent_stress_test_framework.py",
            "monitoring_dashboard.py",
            "client_simulators.py",
            "performance_analyzer.py",
            "run_stress_tests.py"
        ]
        
        all_found = True
        for file in required_files:
            if (stress_test_dir / file).exists():
                print(f"✓ {file}")
            else:
                print(f"✗ {file} (MISSING)")
                all_found = False
                
        return all_found
    else:
        print(f"✗ Stress test directory not found")
        return False

def main():
    """Run all validation checks"""
    print("="*60)
    print("VoidLight MarkItDown MCP Server - Stress Test Setup Validation")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("MCP Server", check_mcp_server()),
        ("Dependencies", check_dependencies()[0]),
        ("Ports", check_ports()),
        ("System Limits", check_system_limits()),
        ("Directories", check_directories())
    ]
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for check_name, passed in checks:
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {check_name}: {status}")
        if not passed:
            all_passed = False
            
    if all_passed:
        print("\n✓ All checks passed! Ready to run stress tests.")
        print("\nTo run a quick test:")
        print("  python run_stress_tests.py --profile quick")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        
        # Check if we need to install dependencies
        _, missing = check_dependencies()
        if missing:
            print("\nTo install missing dependencies:")
            print("  pip install -r requirements.txt")
            
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())