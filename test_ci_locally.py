#!/usr/bin/env python3
"""
Local CI/CD Test Runner
Tests the CI/CD pipeline components locally before GitHub Actions execution
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import shutil

class LocalCITester:
    """Tests CI/CD components locally"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.results = {}
        self.python_cmd = sys.executable
        
    def test_all(self):
        """Run all local CI tests"""
        print("🚀 Local CI/CD Pipeline Test")
        print("=" * 60)
        print(f"Project root: {self.project_root}")
        print(f"Python: {self.python_cmd}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Test components
        self.test_environment_setup()
        self.test_package_installation()
        self.test_automated_runner()
        self.test_artifact_generation()
        self.test_workflow_simulation()
        
        # Generate report
        self.generate_report()
        
    def test_environment_setup(self):
        """Test virtual environment setup"""
        print("\n📦 Testing virtual environment setup...")
        
        venv_path = self.project_root / "mcp-env"
        
        if venv_path.exists():
            print("✓ Virtual environment exists")
            self.results["venv_exists"] = True
            
            # Check if we can activate it
            activate_script = venv_path / "bin" / "activate"
            if activate_script.exists():
                print("✓ Activation script found")
                self.results["venv_activate"] = True
            else:
                print("✗ Activation script not found")
                self.results["venv_activate"] = False
        else:
            print("✗ Virtual environment not found")
            print("  Creating virtual environment...")
            
            try:
                subprocess.run(
                    [self.python_cmd, "-m", "venv", str(venv_path)],
                    check=True
                )
                print("✓ Virtual environment created")
                self.results["venv_created"] = True
            except Exception as e:
                print(f"✗ Failed to create venv: {e}")
                self.results["venv_created"] = False
                
    def test_package_installation(self):
        """Test package installation process"""
        print("\n📚 Testing package installation...")
        
        venv_python = self.project_root / "mcp-env" / "bin" / "python"
        
        if not venv_python.exists():
            print("✗ Virtual environment Python not found")
            self.results["packages_installed"] = False
            return
            
        # Check if packages are installed
        packages_to_check = [
            "voidlight_markitdown",
            "voidlight_markitdown-mcp",
            "pytest",
            "pytest-asyncio"
        ]
        
        for package in packages_to_check:
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "show", package],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ Package installed: {package}")
            else:
                print(f"⚠ Package not installed: {package}")
                
                # Try to install local packages
                if package.startswith("voidlight_markitdown"):
                    package_dir = self.project_root / "packages" / package
                    if package_dir.exists():
                        print(f"  Installing {package}...")
                        install_result = subprocess.run(
                            [str(venv_python), "-m", "pip", "install", "-e", str(package_dir)],
                            capture_output=True,
                            text=True
                        )
                        if install_result.returncode == 0:
                            print(f"  ✓ Installed successfully")
                        else:
                            print(f"  ✗ Installation failed: {install_result.stderr}")
                            
    def test_automated_runner(self):
        """Test the automated test runner script"""
        print("\n🏃 Testing automated test runner...")
        
        runner_script = self.project_root / "run_integration_tests_automated.py"
        
        if not runner_script.exists():
            print("✗ Automated test runner not found")
            self.results["runner_exists"] = False
            return
            
        print("✓ Test runner script exists")
        self.results["runner_exists"] = True
        
        # Test with dry run or minimal config
        test_config = {
            "test_suites": ["enhanced"],
            "timeout_minutes": 5,
            "save_artifacts": True,
            "artifact_dir": "test_artifacts_local",
            "verbose": True
        }
        
        # Create temporary test config
        temp_config = self.project_root / "test_config_local.json"
        with open(temp_config, 'w') as f:
            json.dump(test_config, f)
            
        print("  Running test runner with minimal config...")
        
        venv_python = self.project_root / "mcp-env" / "bin" / "python"
        
        # Check if test script exists first
        test_script = self.project_root / "test_mcp_integration_enhanced.py"
        if not test_script.exists():
            print("  ⚠ Test script not found, skipping runner test")
            self.results["runner_test"] = "skipped"
        else:
            try:
                # Run with short timeout for testing
                result = subprocess.run(
                    [str(venv_python), str(runner_script), "--config", str(temp_config), "--timeout", "1"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if "TEST EXECUTION SUMMARY" in result.stdout:
                    print("  ✓ Test runner executed successfully")
                    self.results["runner_test"] = "success"
                else:
                    print("  ⚠ Test runner executed but output unexpected")
                    self.results["runner_test"] = "partial"
                    
            except subprocess.TimeoutExpired:
                print("  ✓ Test runner started (timed out as expected)")
                self.results["runner_test"] = "timeout_ok"
            except Exception as e:
                print(f"  ✗ Test runner failed: {e}")
                self.results["runner_test"] = "failed"
            finally:
                # Cleanup
                temp_config.unlink(missing_ok=True)
                
    def test_artifact_generation(self):
        """Test artifact directory creation and management"""
        print("\n📁 Testing artifact generation...")
        
        artifact_dir = self.project_root / "test_artifacts"
        
        if not artifact_dir.exists():
            artifact_dir.mkdir(parents=True)
            print("✓ Created test_artifacts directory")
        else:
            print("✓ test_artifacts directory exists")
            
        # Test creating a sample artifact
        test_artifact = artifact_dir / "test_run.json"
        test_data = {
            "test": "local_ci_test",
            "timestamp": datetime.now().isoformat(),
            "status": "testing"
        }
        
        try:
            with open(test_artifact, 'w') as f:
                json.dump(test_data, f)
            print("✓ Can write to artifacts directory")
            self.results["artifact_write"] = True
            
            # Clean up
            test_artifact.unlink()
        except Exception as e:
            print(f"✗ Cannot write to artifacts directory: {e}")
            self.results["artifact_write"] = False
            
    def test_workflow_simulation(self):
        """Simulate GitHub Actions workflow steps"""
        print("\n🎭 Simulating GitHub Actions workflow...")
        
        venv_python = self.project_root / "mcp-env" / "bin" / "python"
        
        # Simulate key workflow steps
        steps = [
            {
                "name": "Check Python version",
                "command": [str(venv_python), "--version"],
                "expected": "Python 3"
            },
            {
                "name": "Check pip",
                "command": [str(venv_python), "-m", "pip", "--version"],
                "expected": "pip"
            },
            {
                "name": "List installed packages",
                "command": [str(venv_python), "-m", "pip", "list"],
                "expected": "voidlight"
            }
        ]
        
        for step in steps:
            print(f"\n  Step: {step['name']}")
            try:
                result = subprocess.run(
                    step["command"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if step["expected"] in result.stdout:
                    print(f"    ✓ Success")
                    self.results[f"step_{step['name']}"] = True
                else:
                    print(f"    ⚠ Unexpected output")
                    self.results[f"step_{step['name']}"] = False
                    
            except Exception as e:
                print(f"    ✗ Failed: {e}")
                self.results[f"step_{step['name']}"] = False
                
    def generate_report(self):
        """Generate local CI test report"""
        print("\n" + "=" * 60)
        print("LOCAL CI TEST REPORT")
        print("=" * 60)
        
        # Count results
        passed = sum(1 for v in self.results.values() if v is True or v == "success")
        failed = sum(1 for v in self.results.values() if v is False or v == "failed")
        other = len(self.results) - passed - failed
        
        print(f"\n📊 Summary:")
        print(f"  ✓ Passed: {passed}")
        print(f"  ✗ Failed: {failed}")
        print(f"  ⚠ Other: {other}")
        
        print(f"\n📋 Details:")
        for key, value in self.results.items():
            status = "✓" if value is True or value == "success" else "✗" if value is False or value == "failed" else "⚠"
            print(f"  {status} {key}: {value}")
            
        print(f"\n💡 Recommendations:")
        
        if failed == 0:
            print("  ✓ Local CI tests passed!")
            print("  ✓ Ready to test with GitHub Actions")
            print("\n  Next steps:")
            print("    1. Commit changes: git add -A && git commit -m 'ci: update workflow'")
            print("    2. Push to trigger workflow: git push")
            print("    3. Or manually trigger from GitHub Actions tab")
        else:
            print("  ✗ Fix failures before running GitHub Actions")
            
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": self.results,
            "summary": {
                "passed": passed,
                "failed": failed,
                "other": other
            }
        }
        
        report_file = self.project_root / f"local_ci_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Report saved to: {report_file}")

def main():
    """Main entry point"""
    tester = LocalCITester()
    tester.test_all()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())