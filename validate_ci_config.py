#!/usr/bin/env python3
"""
CI/CD Configuration Validator for VoidLight MarkItDown
Validates GitHub Actions workflow, Docker files, and test configurations
"""

import json
import os
import sys
from pathlib import Path
import subprocess
from datetime import datetime

class CICDValidator:
    """Validates CI/CD configuration and environment"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        self.warnings = []
        self.info = []
        
    def validate_all(self):
        """Run all validation checks"""
        print("CI/CD Configuration Validator")
        print("=" * 60)
        
        # Check directory structure
        self.validate_directory_structure()
        
        # Check workflow file
        self.validate_github_workflow()
        
        # Check Docker configuration
        self.validate_docker_config()
        
        # Check test configuration
        self.validate_test_config()
        
        # Check test scripts
        self.validate_test_scripts()
        
        # Check dependencies
        self.validate_dependencies()
        
        # Check environment
        self.validate_environment()
        
        # Generate report
        self.generate_report()
        
    def validate_directory_structure(self):
        """Validate required directories exist"""
        print("\n📁 Validating directory structure...")
        
        required_dirs = [
            ".github/workflows",
            "packages/voidlight_markitdown",
            "packages/voidlight_markitdown-mcp",
            "test_artifacts"
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.info.append(f"✓ Directory exists: {dir_path}")
            else:
                if dir_path == "test_artifacts":
                    # Create test_artifacts directory if missing
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.warnings.append(f"Created missing directory: {dir_path}")
                else:
                    self.issues.append(f"✗ Missing directory: {dir_path}")
                    
    def validate_github_workflow(self):
        """Validate GitHub Actions workflow file"""
        print("\n🔧 Validating GitHub Actions workflow...")
        
        workflow_file = self.project_root / ".github/workflows/integration-tests.yml"
        
        if not workflow_file.exists():
            self.issues.append("✗ Workflow file not found: .github/workflows/integration-tests.yml")
            return
            
        # Check basic structure
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            # Check for required elements
            required_elements = [
                "name:",
                "on:",
                "jobs:",
                "integration-tests:",
                "performance-tests:",
                "workflow_dispatch:",
                "matrix:",
                "python-version:"
            ]
            
            for element in required_elements:
                if element in content:
                    self.info.append(f"✓ Workflow contains: {element}")
                else:
                    self.issues.append(f"✗ Workflow missing: {element}")
                    
            # Check for modern action versions
            if "actions/checkout@v4" in content:
                self.info.append("✓ Using latest checkout action")
            else:
                self.warnings.append("⚠ Not using latest checkout action version")
                
            # Check for manual trigger
            if "workflow_dispatch:" in content:
                self.info.append("✓ Manual trigger configured")
            else:
                self.issues.append("✗ No manual trigger (workflow_dispatch)")
                
        except Exception as e:
            self.issues.append(f"✗ Error reading workflow file: {str(e)}")
            
    def validate_docker_config(self):
        """Validate Docker configuration files"""
        print("\n🐳 Validating Docker configuration...")
        
        docker_files = [
            ("Dockerfile.test", [
                "FROM python:",
                "WORKDIR /app",
                "mcp-env",
                "voidlight_markitdown",
                "CMD"
            ]),
            ("docker-compose.test.yml", [
                "version:",
                "services:",
                "mcp-integration-tests:",
                "volumes:",
                "environment:"
            ])
        ]
        
        for filename, required_elements in docker_files:
            file_path = self.project_root / filename
            
            if not file_path.exists():
                self.issues.append(f"✗ Docker file not found: {filename}")
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                for element in required_elements:
                    if element in content:
                        self.info.append(f"✓ {filename} contains: {element}")
                    else:
                        self.warnings.append(f"⚠ {filename} might be missing: {element}")
                        
            except Exception as e:
                self.issues.append(f"✗ Error reading {filename}: {str(e)}")
                
    def validate_test_config(self):
        """Validate test configuration file"""
        print("\n⚙️ Validating test configuration...")
        
        config_file = self.project_root / "test_config.json"
        
        if not config_file.exists():
            self.issues.append("✗ Test configuration not found: test_config.json")
            return
            
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Check required fields
            required_fields = [
                "test_suites",
                "timeout_minutes",
                "artifact_dir"
            ]
            
            for field in required_fields:
                if field in config:
                    self.info.append(f"✓ Config contains: {field} = {config[field]}")
                else:
                    self.issues.append(f"✗ Config missing: {field}")
                    
            # Validate test suites
            if "test_suites" in config:
                for suite in config["test_suites"]:
                    self.info.append(f"✓ Test suite configured: {suite}")
                    
        except json.JSONDecodeError as e:
            self.issues.append(f"✗ Invalid JSON in test_config.json: {str(e)}")
        except Exception as e:
            self.issues.append(f"✗ Error reading test config: {str(e)}")
            
    def validate_test_scripts(self):
        """Validate test scripts exist"""
        print("\n🧪 Validating test scripts...")
        
        test_scripts = [
            "run_integration_tests_automated.py",
            "test_mcp_integration_enhanced.py",
            "test_mcp_integration_comprehensive.py"
        ]
        
        for script in test_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                self.info.append(f"✓ Test script exists: {script}")
                
                # Check if executable
                if os.access(script_path, os.X_OK):
                    self.info.append(f"✓ {script} is executable")
                else:
                    self.warnings.append(f"⚠ {script} is not executable")
            else:
                self.warnings.append(f"⚠ Test script not found: {script}")
                
    def validate_dependencies(self):
        """Check for required dependencies"""
        print("\n📦 Validating dependencies...")
        
        # Check Python packages
        packages = [
            ("packages/voidlight_markitdown", "setup.py"),
            ("packages/voidlight_markitdown-mcp", "setup.py")
        ]
        
        for package_dir, setup_file in packages:
            setup_path = self.project_root / package_dir / setup_file
            if setup_path.exists():
                self.info.append(f"✓ Package setup found: {package_dir}")
            else:
                self.issues.append(f"✗ Missing setup.py in {package_dir}")
                
    def validate_environment(self):
        """Validate environment setup"""
        print("\n🌍 Validating environment...")
        
        # Check for virtual environment
        venv_path = self.project_root / "mcp-env"
        if venv_path.exists():
            self.info.append("✓ Virtual environment exists: mcp-env")
        else:
            self.warnings.append("⚠ Virtual environment not found: mcp-env")
            
        # Check for required environment variables in workflow
        env_vars = [
            "VOIDLIGHT_LOG_LEVEL",
            "TEST_MODE"
        ]
        
        workflow_file = self.project_root / ".github/workflows/integration-tests.yml"
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            for var in env_vars:
                if var in content:
                    self.info.append(f"✓ Environment variable configured: {var}")
                else:
                    self.warnings.append(f"⚠ Environment variable not found in workflow: {var}")
                    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  ✓ Passed: {len(self.info)}")
        print(f"  ⚠ Warnings: {len(self.warnings)}")
        print(f"  ✗ Issues: {len(self.issues)}")
        
        # Details
        if self.issues:
            print(f"\n❌ Critical Issues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  {issue}")
                
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
                
        print(f"\n✅ Passed Checks ({len(self.info)}):")
        for i, info in enumerate(self.info[:10]):  # Show first 10
            print(f"  {info}")
        if len(self.info) > 10:
            print(f"  ... and {len(self.info) - 10} more")
            
        # Recommendations
        print("\n📋 Recommendations:")
        
        if not self.issues:
            print("  ✓ CI/CD configuration appears to be valid!")
            print("  ✓ Ready for manual workflow trigger")
        else:
            print("  ✗ Fix critical issues before running CI/CD")
            
        if self.warnings:
            print("  ⚠ Review warnings for potential improvements")
            
        print("\n💡 Next Steps:")
        print("  1. Fix any critical issues")
        print("  2. Review and address warnings")
        print("  3. Create a test commit to trigger workflow")
        print("  4. Or manually trigger workflow from GitHub Actions tab")
        
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": len(self.info),
                "warnings": len(self.warnings),
                "issues": len(self.issues)
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "info": self.info,
            "ready_for_ci": len(self.issues) == 0
        }
        
        report_file = self.project_root / f"ci_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Full report saved to: {report_file}")
        
        return len(self.issues) == 0

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.absolute()
    
    validator = CICDValidator(project_root)
    success = validator.validate_all()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())