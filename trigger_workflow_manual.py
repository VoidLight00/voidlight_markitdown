#!/usr/bin/env python3
"""
Manual Workflow Trigger Helper
Provides instructions and validation for manually triggering the GitHub Actions workflow
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class WorkflowTriggerHelper:
    """Helps with manual workflow triggering"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.workflow_file = self.project_root / ".github/workflows/integration-tests.yml"
        
    def check_prerequisites(self):
        """Check if everything is ready for workflow trigger"""
        print("🔍 Checking prerequisites for workflow trigger...")
        
        checks = {
            "workflow_exists": self.workflow_file.exists(),
            "git_repo": (self.project_root / ".git").exists(),
            "workflow_has_manual_trigger": self.check_manual_trigger(),
            "test_config_exists": (self.project_root / "test_config.json").exists(),
            "docker_files_exist": self.check_docker_files(),
            "test_scripts_exist": self.check_test_scripts()
        }
        
        all_good = all(checks.values())
        
        print("\n📋 Prerequisites:")
        for check, status in checks.items():
            icon = "✓" if status else "✗"
            print(f"  {icon} {check.replace('_', ' ').title()}: {status}")
            
        return all_good
        
    def check_manual_trigger(self):
        """Check if workflow has manual trigger"""
        if not self.workflow_file.exists():
            return False
            
        with open(self.workflow_file, 'r') as f:
            content = f.read()
            
        return "workflow_dispatch:" in content
        
    def check_docker_files(self):
        """Check if Docker files exist"""
        files = ["Dockerfile.test", "docker-compose.test.yml"]
        return all((self.project_root / f).exists() for f in files)
        
    def check_test_scripts(self):
        """Check if test scripts exist"""
        scripts = ["run_integration_tests_automated.py"]
        return all((self.project_root / s).exists() for s in scripts)
        
    def get_git_status(self):
        """Get current git status"""
        print("\n📊 Git Status:")
        
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            current_branch = branch_result.stdout.strip()
            print(f"  Current branch: {current_branch}")
            
            # Get uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if status_result.stdout:
                print("  ⚠ Uncommitted changes detected:")
                changes = status_result.stdout.strip().split('\n')[:5]
                for change in changes:
                    print(f"    {change}")
                if len(status_result.stdout.strip().split('\n')) > 5:
                    remaining = len(status_result.stdout.strip().split('\n')) - 5
                    print(f"    ... and {remaining} more")
            else:
                print("  ✓ No uncommitted changes")
                
            # Get remote info
            remote_result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if remote_result.stdout:
                print("  Remote configured:")
                for line in remote_result.stdout.strip().split('\n')[:2]:
                    print(f"    {line}")
            else:
                print("  ✗ No git remote configured")
                
            return current_branch, bool(remote_result.stdout)
            
        except Exception as e:
            print(f"  ✗ Error checking git status: {e}")
            return None, False
            
    def show_trigger_instructions(self, branch="main", has_remote=True):
        """Show instructions for triggering the workflow"""
        print("\n📚 How to Trigger the Workflow:")
        
        print("\n🔧 Option 1: GitHub Web Interface (Recommended)")
        print("  1. Go to your repository on GitHub")
        print("  2. Click on the 'Actions' tab")
        print("  3. Select 'MCP Integration Tests' workflow from the left sidebar")
        print("  4. Click 'Run workflow' button")
        print("  5. Select branch and optionally specify test suites")
        print("  6. Click 'Run workflow' to start")
        
        print("\n🖥️ Option 2: GitHub CLI")
        print("  Install GitHub CLI if not already installed:")
        print("    brew install gh")
        print("  Authenticate:")
        print("    gh auth login")
        print("  Trigger workflow:")
        print("    gh workflow run integration-tests.yml")
        print("  With custom inputs:")
        print("    gh workflow run integration-tests.yml -f test_suites='enhanced comprehensive'")
        
        print("\n🚀 Option 3: Push to Trigger")
        if branch in ["main", "develop"]:
            print(f"  Current branch '{branch}' will trigger on push")
            print("  Commands:")
            print("    git add -A")
            print("    git commit -m 'ci: trigger integration tests'")
            print("    git push origin " + branch)
        else:
            print(f"  Current branch '{branch}' won't trigger automatically")
            print("  Switch to main or develop branch, or create a PR to main")
            
        print("\n📱 Option 4: API Trigger")
        print("  Using curl (replace YOUR_TOKEN and OWNER/REPO):")
        print("  curl -X POST \\")
        print("    -H 'Accept: application/vnd.github.v3+json' \\")
        print("    -H 'Authorization: token YOUR_TOKEN' \\")
        print("    https://api.github.com/repos/OWNER/REPO/actions/workflows/integration-tests.yml/dispatches \\")
        print("    -d '{\"ref\":\"main\",\"inputs\":{\"test_suites\":\"enhanced comprehensive\"}}'")
        
    def create_trigger_commit(self):
        """Create a trigger commit if user wants"""
        print("\n🎯 Create Trigger Commit?")
        print("  This will create an empty commit to trigger the workflow")
        
        response = input("  Create trigger commit? (y/n): ")
        
        if response.lower() == 'y':
            try:
                # Create empty commit
                result = subprocess.run(
                    ["git", "commit", "--allow-empty", "-m", "ci: trigger integration tests"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    print("  ✓ Trigger commit created")
                    print("  Now run: git push origin <branch>")
                else:
                    print(f"  ✗ Failed to create commit: {result.stderr}")
                    
            except Exception as e:
                print(f"  ✗ Error creating commit: {e}")
                
    def show_monitoring_tips(self):
        """Show tips for monitoring the workflow"""
        print("\n👀 Monitoring the Workflow:")
        print("  1. GitHub Actions tab shows real-time logs")
        print("  2. Workflow will run tests for Python 3.9, 3.10, and 3.11")
        print("  3. Artifacts will be uploaded after each job")
        print("  4. Check the 'Summary' section for test results")
        print("  5. Download artifacts for detailed logs")
        
        print("\n⏱️ Expected Duration:")
        print("  - Integration tests: ~5-10 minutes per Python version")
        print("  - Performance tests: ~5 minutes")
        print("  - Total: ~15-20 minutes")
        
        print("\n🔍 Troubleshooting:")
        print("  - Check workflow logs for errors")
        print("  - Ensure all secrets are configured (if any)")
        print("  - Verify branch protection rules allow Actions")
        print("  - Check GitHub Actions usage limits")
        
    def generate_workflow_status_badge(self):
        """Generate workflow status badge markdown"""
        print("\n🏷️ Workflow Status Badge:")
        print("  Add this to your README.md:")
        print("  [![MCP Integration Tests](https://github.com/OWNER/REPO/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/integration-tests.yml)")
        
    def run(self):
        """Main execution"""
        print("🚀 GitHub Actions Workflow Trigger Helper")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Not all prerequisites are met!")
            print("   Fix the issues above before triggering the workflow.")
            return 1
            
        # Get git status
        branch, has_remote = self.get_git_status()
        
        if not has_remote:
            print("\n❌ No git remote configured!")
            print("   Add a remote: git remote add origin <repository-url>")
            return 1
            
        # Show instructions
        self.show_trigger_instructions(branch, has_remote)
        
        # Offer to create trigger commit
        self.create_trigger_commit()
        
        # Show monitoring tips
        self.show_monitoring_tips()
        
        # Show badge info
        self.generate_workflow_status_badge()
        
        print("\n✅ Ready to trigger workflow!")
        print("   Choose one of the options above to start your CI/CD pipeline.")
        
        return 0

def main():
    """Main entry point"""
    helper = WorkflowTriggerHelper()
    return helper.run()

if __name__ == "__main__":
    sys.exit(main())