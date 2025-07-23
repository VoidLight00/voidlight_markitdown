#!/usr/bin/env python3
"""
Release creation script for voidlight-markitdown
Automates the release process with validation
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ReleaseCreator:
    """Automates the release creation process"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.version = self.get_current_version()
        self.release_notes = []
        
    def get_current_version(self) -> str:
        """Get current version from __about__.py"""
        about_file = self.project_root / "src/voidlight_markitdown/__about__.py"
        namespace = {}
        exec(open(about_file).read(), namespace)
        return namespace["__version__"]
        
    def update_changelog(self) -> str:
        """Update CHANGELOG.md and extract release notes"""
        print("\n📝 Updating CHANGELOG...")
        
        changelog_file = self.project_root / "CHANGELOG.md"
        if not changelog_file.exists():
            print("⚠️  CHANGELOG.md not found, creating one...")
            self.create_initial_changelog()
            
        with open(changelog_file, "r") as f:
            content = f.read()
            
        # Extract unreleased changes
        unreleased_pattern = r"## \[Unreleased\](.*?)(?=## \[|$)"
        unreleased_match = re.search(unreleased_pattern, content, re.DOTALL)
        
        if unreleased_match:
            unreleased_content = unreleased_match.group(1).strip()
            self.release_notes = unreleased_content.split("\n")
        else:
            self.release_notes = ["- Initial release"]
            
        # Update changelog with new version
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_version_header = f"## [{self.version}] - {date_str}"
        
        # Replace [Unreleased] with version
        updated_content = content.replace(
            "## [Unreleased]",
            f"## [Unreleased]\n\n{new_version_header}"
        )
        
        with open(changelog_file, "w") as f:
            f.write(updated_content)
            
        print(f"✅ CHANGELOG updated for version {self.version}")
        return "\n".join(self.release_notes)
        
    def create_initial_changelog(self):
        """Create initial CHANGELOG.md"""
        changelog_content = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of voidlight-markitdown
- Document conversion with Korean language support
- MCP server integration
- Support for multiple file formats
"""
        
        changelog_file = self.project_root / "CHANGELOG.md"
        with open(changelog_file, "w") as f:
            f.write(changelog_content)
            
    def create_git_tag(self) -> bool:
        """Create git tag for release"""
        print(f"\n🏷️  Creating git tag v{self.version}...")
        
        # Create annotated tag
        tag_message = f"Release v{self.version}\n\n" + "\n".join(self.release_notes)
        
        result = subprocess.run(
            ["git", "tag", "-a", f"v{self.version}", "-m", tag_message],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to create tag: {result.stderr}")
            return False
            
        print(f"✅ Created tag v{self.version}")
        return True
        
    def build_packages(self) -> bool:
        """Build distribution packages"""
        print("\n📦 Building packages...")
        
        # Clean dist directory
        dist_dir = self.project_root / "dist"
        if dist_dir.exists():
            import shutil
            shutil.rmtree(dist_dir)
            
        # Build
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            capture_output=True
        )
        
        if result.returncode != 0:
            print("❌ Build failed")
            return False
            
        print("✅ Packages built successfully")
        return True
        
    def create_github_release(self) -> bool:
        """Create GitHub release"""
        print("\n🐙 Creating GitHub release...")
        
        # Check if gh CLI is available
        if subprocess.run(["which", "gh"], capture_output=True).returncode != 0:
            print("⚠️  GitHub CLI (gh) not found, skipping GitHub release")
            return True
            
        # Create release notes file
        release_notes_file = self.project_root / "build-reports/release-notes.md"
        release_notes_file.parent.mkdir(exist_ok=True)
        
        with open(release_notes_file, "w") as f:
            f.write(f"# Release v{self.version}\n\n")
            f.write("\n".join(self.release_notes))
            f.write("\n\n## Installation\n\n")
            f.write("```bash\npip install voidlight-markitdown\n```\n\n")
            f.write("## Docker\n\n")
            f.write(f"```bash\ndocker pull voidlight/markitdown:{self.version}\n```\n")
            
        # Create release
        result = subprocess.run([
            "gh", "release", "create",
            f"v{self.version}",
            "--title", f"v{self.version}",
            "--notes-file", str(release_notes_file),
            "dist/*"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  GitHub release creation failed: {result.stderr}")
            return False
            
        print("✅ GitHub release created")
        return True
        
    def update_docker_images(self) -> bool:
        """Build and tag Docker images"""
        print("\n🐳 Building Docker images...")
        
        # Build main image
        result = subprocess.run([
            "docker", "build",
            "-t", f"voidlight/markitdown:{self.version}",
            "-t", "voidlight/markitdown:latest",
            "--build-arg", f"VERSION={self.version}",
            "--build-arg", f"BUILD_DATE={datetime.now().isoformat()}",
            "--build-arg", f"VCS_REF={self.get_git_hash()}",
            "."
        ])
        
        if result.returncode != 0:
            print("❌ Docker build failed")
            return False
            
        # Build MCP image
        result = subprocess.run([
            "docker", "build",
            "-f", "Dockerfile.mcp",
            "-t", f"voidlight/markitdown-mcp:{self.version}",
            "-t", "voidlight/markitdown-mcp:latest",
            "--build-arg", f"VERSION={self.version}",
            "--build-arg", f"BUILD_DATE={datetime.now().isoformat()}",
            "--build-arg", f"VCS_REF={self.get_git_hash()}",
            "."
        ])
        
        if result.returncode != 0:
            print("❌ Docker MCP build failed")
            return False
            
        print("✅ Docker images built")
        return True
        
    def get_git_hash(self) -> str:
        """Get current git commit hash"""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
        
    def generate_release_report(self) -> Dict:
        """Generate comprehensive release report"""
        return {
            "version": self.version,
            "date": datetime.now().isoformat(),
            "git_tag": f"v{self.version}",
            "git_hash": self.get_git_hash(),
            "release_notes": self.release_notes,
            "artifacts": {
                "pypi": f"voidlight-markitdown=={self.version}",
                "docker": f"voidlight/markitdown:{self.version}",
                "docker_mcp": f"voidlight/markitdown-mcp:{self.version}",
            },
            "checksums": self.generate_checksums()
        }
        
    def generate_checksums(self) -> Dict:
        """Generate checksums for release artifacts"""
        import hashlib
        
        checksums = {}
        dist_dir = self.project_root / "dist"
        
        for file_path in dist_dir.glob("*"):
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    content = f.read()
                    checksums[file_path.name] = {
                        "sha256": hashlib.sha256(content).hexdigest(),
                        "size": len(content)
                    }
                    
        return checksums
        
    def create_release(self, skip_tests: bool = False, skip_publish: bool = False):
        """Execute the release process"""
        print(f"🚀 Creating release for voidlight-markitdown v{self.version}")
        
        # Run release checks first
        if not skip_tests:
            print("\n🔍 Running release checks...")
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "scripts/ci/check_release.py")
            ])
            
            if result.returncode != 0:
                print("❌ Release checks failed")
                sys.exit(1)
                
        # Update changelog
        self.update_changelog()
        
        # Commit changes
        print("\n📝 Committing release changes...")
        subprocess.run(["git", "add", "CHANGELOG.md"])
        subprocess.run([
            "git", "commit", "-m",
            f"chore: prepare release v{self.version}"
        ])
        
        # Create tag
        if not self.create_git_tag():
            sys.exit(1)
            
        # Build packages
        if not self.build_packages():
            sys.exit(1)
            
        # Build Docker images
        self.update_docker_images()
        
        # Create GitHub release
        self.create_github_release()
        
        # Generate release report
        report = self.generate_release_report()
        report_file = self.project_root / f"build-reports/release-{self.version}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Release report saved to: {report_file}")
        
        # Print next steps
        print("\n" + "="*60)
        print("✅ RELEASE CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nVersion: {self.version}")
        print(f"Tag: v{self.version}")
        print("\nNext steps:")
        print("1. Push changes: git push origin main --tags")
        print("2. Publish to PyPI: make publish")
        print("3. Push Docker images: make docker-push")
        print("4. Update documentation")
        print("5. Announce release")
        
        if not skip_publish:
            print("\n🔄 Auto-publishing is available. Run with --publish to auto-publish.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a new release")
    parser.add_argument("--skip-tests", action="store_true", help="Skip release checks")
    parser.add_argument("--publish", action="store_true", help="Auto-publish after creation")
    
    args = parser.parse_args()
    
    creator = ReleaseCreator(project_root)
    creator.create_release(skip_tests=args.skip_tests, skip_publish=not args.publish)


if __name__ == "__main__":
    main()