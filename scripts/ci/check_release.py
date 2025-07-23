#!/usr/bin/env python3
"""
Release readiness checker for voidlight-markitdown
Validates that the project is ready for release
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ReleaseChecker:
    """Validates release readiness"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checks_passed = True
        self.errors = []
        self.warnings = []
        
    def check_git_status(self) -> bool:
        """Check if working directory is clean"""
        print("\n📋 Checking Git status...")
        
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            self.errors.append("Working directory has uncommitted changes")
            return False
            
        # Check if on main/master branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )
        
        branch = result.stdout.strip()
        if branch not in ["main", "master"]:
            self.warnings.append(f"Not on main branch (current: {branch})")
            
        print("✅ Git status clean")
        return True
        
    def check_version(self) -> bool:
        """Verify version consistency"""
        print("\n🏷️  Checking version consistency...")
        
        # Read version from __about__.py
        about_file = self.project_root / "src/voidlight_markitdown/__about__.py"
        namespace = {}
        exec(open(about_file).read(), namespace)
        version = namespace["__version__"]
        
        # Check if version tag exists
        result = subprocess.run(
            ["git", "tag", "-l", f"v{version}"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            self.errors.append(f"Version {version} already tagged")
            return False
            
        print(f"✅ Version {version} ready for release")
        return True
        
    def check_changelog(self) -> bool:
        """Check if CHANGELOG is updated"""
        print("\n📝 Checking CHANGELOG...")
        
        changelog_file = self.project_root / "CHANGELOG.md"
        if not changelog_file.exists():
            self.warnings.append("CHANGELOG.md not found")
            return True
            
        with open(changelog_file) as f:
            content = f.read()
            
        if "## [Unreleased]" not in content:
            self.warnings.append("CHANGELOG.md missing [Unreleased] section")
            
        print("✅ CHANGELOG checked")
        return True
        
    def check_tests(self) -> bool:
        """Run test suite"""
        print("\n🧪 Running tests...")
        
        result = subprocess.run(
            ["pytest", "tests", "-v", "--tb=short"],
            capture_output=True
        )
        
        if result.returncode != 0:
            self.errors.append("Tests failed")
            return False
            
        print("✅ All tests passed")
        return True
        
    def check_code_quality(self) -> bool:
        """Check code quality"""
        print("\n🔍 Checking code quality...")
        
        checks = [
            ("black", ["black", "--check", "src", "tests"]),
            ("isort", ["isort", "--check-only", "src", "tests"]),
            ("flake8", ["flake8", "src"]),
            ("mypy", ["mypy", "src"]),
        ]
        
        all_passed = True
        for name, cmd in checks:
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                self.warnings.append(f"{name} check failed")
                all_passed = False
            else:
                print(f"  ✅ {name} passed")
                
        return all_passed
        
    def check_documentation(self) -> bool:
        """Check documentation"""
        print("\n📚 Checking documentation...")
        
        required_docs = [
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "docs/index.md",
        ]
        
        missing_docs = []
        for doc in required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                missing_docs.append(doc)
                
        if missing_docs:
            self.warnings.append(f"Missing documentation: {', '.join(missing_docs)}")
            
        print("✅ Documentation checked")
        return True
        
    def check_dependencies(self) -> bool:
        """Check dependency security"""
        print("\n🔒 Checking dependencies...")
        
        # Check with safety
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True
        )
        
        if result.returncode != 0:
            try:
                issues = json.loads(result.stdout)
                self.warnings.append(f"Found {len(issues)} security issues in dependencies")
            except:
                self.warnings.append("Dependency security check failed")
                
        print("✅ Dependencies checked")
        return True
        
    def check_package_build(self) -> bool:
        """Test package build"""
        print("\n📦 Testing package build...")
        
        # Clean dist directory
        dist_dir = self.project_root / "dist"
        if dist_dir.exists():
            import shutil
            shutil.rmtree(dist_dir)
            
        # Build package
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            capture_output=True
        )
        
        if result.returncode != 0:
            self.errors.append("Package build failed")
            return False
            
        # Check with twine
        result = subprocess.run(
            ["twine", "check", "dist/*"],
            capture_output=True
        )
        
        if result.returncode != 0:
            self.errors.append("Package validation failed")
            return False
            
        print("✅ Package build successful")
        return True
        
    def generate_report(self) -> Dict:
        """Generate release readiness report"""
        return {
            "ready_for_release": self.checks_passed and not self.errors,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks": {
                "git_clean": len(self.errors) == 0,
                "tests_passing": "Tests failed" not in self.errors,
                "package_builds": "Package build failed" not in self.errors,
            }
        }
        
    def run_checks(self) -> bool:
        """Run all release checks"""
        print("🚀 Running release readiness checks...")
        
        checks = [
            self.check_git_status,
            self.check_version,
            self.check_changelog,
            self.check_tests,
            self.check_code_quality,
            self.check_documentation,
            self.check_dependencies,
            self.check_package_build,
        ]
        
        for check in checks:
            try:
                if not check():
                    self.checks_passed = False
            except Exception as e:
                self.errors.append(f"{check.__name__} failed: {str(e)}")
                self.checks_passed = False
                
        # Generate report
        report = self.generate_report()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 RELEASE READINESS SUMMARY")
        print("="*60)
        
        if report["ready_for_release"]:
            print("✅ Project is ready for release!")
        else:
            print("❌ Project is NOT ready for release")
            
        if self.errors:
            print("\n❌ Errors (must fix):")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.warnings:
            print("\n⚠️  Warnings (should fix):")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        # Save report
        report_file = self.project_root / "build-reports/release-readiness.json"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Full report saved to: {report_file}")
        
        return report["ready_for_release"]


def main():
    """Main entry point"""
    checker = ReleaseChecker(project_root)
    
    if checker.run_checks():
        print("\n✅ All checks passed! Ready to release.")
        sys.exit(0)
    else:
        print("\n❌ Release checks failed. Please fix issues before releasing.")
        sys.exit(1)


if __name__ == "__main__":
    main()