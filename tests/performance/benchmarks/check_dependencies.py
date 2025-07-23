#!/usr/bin/env python3
"""
Check if all dependencies for performance testing are available.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def check_import(module_name: str, package_name: str = None) -> bool:
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - Install with: pip install {package_name}")
        return False

def check_command(command: str) -> bool:
    """Check if a command is available."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=False)
        print(f"✅ {command}")
        return True
    except FileNotFoundError:
        print(f"❌ {command} - Not found in PATH")
        return False

def main():
    """Check all dependencies."""
    print("Checking Performance Testing Dependencies")
    print("=" * 50)
    
    print("\nPython version:")
    print(f"  {sys.version}")
    
    print("\nCore dependencies:")
    core_deps = [
        ("psutil", None),
        ("matplotlib", None),
        ("numpy", None),
        ("reportlab", None),
        ("openpyxl", None),
        ("docx", "python-docx"),
        ("lorem", None),
        ("pandas", None),
        ("PIL", "Pillow"),
    ]
    
    core_ok = all(check_import(mod, pkg) for mod, pkg in core_deps)
    
    print("\nVoidLight MarkItDown dependencies:")
    markitdown_deps = [
        ("bs4", "beautifulsoup4"),
        ("markdownify", None),
        ("charset_normalizer", None),
        ("magika", None),
        ("requests", None),
        ("tabulate", None),
    ]
    
    markitdown_ok = all(check_import(mod, pkg) for mod, pkg in markitdown_deps)
    
    print("\nOptional tools:")
    optional_deps = [
        ("memory_profiler", None),
    ]
    
    for mod, pkg in optional_deps:
        check_import(mod, pkg)
    
    print("\nSystem commands:")
    commands = ["git", "python3", "pip"]
    
    for cmd in commands:
        check_command(cmd)
    
    print("\n" + "=" * 50)
    
    if core_ok and markitdown_ok:
        print("✅ All required dependencies are installed!")
        print("\nYou can run the performance tests with:")
        print("  python run_all_tests.py --quick")
        return 0
    else:
        print("❌ Some dependencies are missing.")
        print("\nInstall all dependencies with:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())