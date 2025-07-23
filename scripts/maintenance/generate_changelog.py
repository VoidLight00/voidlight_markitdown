#!/usr/bin/env python3
"""
Changelog generator for voidlight-markitdown
Generates changelog entries from git commits
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ChangelogGenerator:
    """Generates changelog from git commits"""
    
    # Commit type mapping to changelog sections
    TYPE_MAPPING = {
        "feat": "Added",
        "fix": "Fixed",
        "docs": "Documentation",
        "style": "Changed",
        "refactor": "Changed",
        "perf": "Performance",
        "test": "Testing",
        "build": "Build",
        "ci": "CI/CD",
        "chore": "Maintenance",
        "revert": "Reverted",
    }
    
    # Types to include in changelog
    INCLUDED_TYPES = ["feat", "fix", "docs", "perf", "revert"]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.commits = []
        
    def get_last_version_tag(self) -> str:
        """Get the last version tag"""
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
        
    def get_commits_since_tag(self, tag: str = None) -> List[Dict]:
        """Get commits since last tag"""
        cmd = ["git", "log", "--pretty=format:%H|%s|%b|%an|%ae|%ad", "--date=short"]
        
        if tag:
            cmd.append(f"{tag}..HEAD")
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
                
            parts = line.split("|", 5)
            if len(parts) >= 6:
                commit = {
                    "hash": parts[0],
                    "subject": parts[1],
                    "body": parts[2],
                    "author_name": parts[3],
                    "author_email": parts[4],
                    "date": parts[5],
                }
                
                # Parse conventional commit
                parsed = self.parse_conventional_commit(commit["subject"])
                commit.update(parsed)
                
                commits.append(commit)
                
        return commits
        
    def parse_conventional_commit(self, subject: str) -> Dict:
        """Parse conventional commit format"""
        # Pattern for conventional commits
        pattern = r"^(\w+)(?:\(([^)]+)\))?: (.+)$"
        match = re.match(pattern, subject)
        
        if match:
            return {
                "type": match.group(1),
                "scope": match.group(2),
                "description": match.group(3),
            }
        else:
            # Try to guess type from keywords
            subject_lower = subject.lower()
            if "fix" in subject_lower:
                commit_type = "fix"
            elif "add" in subject_lower or "feat" in subject_lower:
                commit_type = "feat"
            elif "doc" in subject_lower:
                commit_type = "docs"
            else:
                commit_type = "other"
                
            return {
                "type": commit_type,
                "scope": None,
                "description": subject,
            }
            
    def group_commits_by_type(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Group commits by type"""
        grouped = {}
        
        for commit in commits:
            commit_type = commit.get("type", "other")
            
            # Only include specified types
            if commit_type in self.INCLUDED_TYPES:
                section = self.TYPE_MAPPING.get(commit_type, "Other")
                
                if section not in grouped:
                    grouped[section] = []
                    
                grouped[section].append(commit)
                
        return grouped
        
    def format_commit_line(self, commit: Dict) -> str:
        """Format a single commit line"""
        description = commit["description"]
        
        # Add scope if present
        if commit.get("scope"):
            description = f"**{commit['scope']}**: {description}"
            
        # Add commit hash reference
        short_hash = commit["hash"][:7]
        line = f"- {description} ([{short_hash}](https://github.com/voidlight/voidlight_markitdown/commit/{commit['hash']}))"
        
        # Add author if not default
        if commit["author_name"] != "VoidLight":
            line += f" by @{commit['author_name']}"
            
        return line
        
    def generate_changelog_section(self, version: str = "Unreleased") -> str:
        """Generate changelog section for current changes"""
        last_tag = self.get_last_version_tag()
        commits = self.get_commits_since_tag(last_tag)
        
        if not commits:
            return ""
            
        # Group commits
        grouped = self.group_commits_by_type(commits)
        
        if not grouped:
            return ""
            
        # Build changelog section
        lines = []
        
        # Add version header
        if version == "Unreleased":
            lines.append("## [Unreleased]")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
            lines.append(f"## [{version}] - {date_str}")
            
        lines.append("")
        
        # Add sections
        section_order = ["Added", "Fixed", "Changed", "Performance", "Documentation", "Reverted"]
        
        for section in section_order:
            if section in grouped:
                lines.append(f"### {section}")
                
                for commit in grouped[section]:
                    lines.append(self.format_commit_line(commit))
                    
                lines.append("")
                
        return "\n".join(lines)
        
    def update_changelog_file(self):
        """Update CHANGELOG.md file"""
        changelog_path = self.project_root / "CHANGELOG.md"
        
        # Generate new section
        new_section = self.generate_changelog_section()
        
        if not new_section:
            print("No changes to add to changelog")
            return
            
        # Read existing changelog
        if changelog_path.exists():
            with open(changelog_path, "r") as f:
                content = f.read()
                
            # Find where to insert new content
            if "## [Unreleased]" in content:
                # Replace existing unreleased section
                pattern = r"## \[Unreleased\].*?(?=## \[|$)"
                content = re.sub(pattern, new_section + "\n\n", content, flags=re.DOTALL)
            else:
                # Insert after header
                lines = content.split("\n")
                insert_index = 0
                
                # Find end of header
                for i, line in enumerate(lines):
                    if line.startswith("## "):
                        insert_index = i
                        break
                        
                lines.insert(insert_index, new_section)
                content = "\n".join(lines)
        else:
            # Create new changelog
            content = self.create_initial_changelog()
            content = content.replace("## [Unreleased]", new_section)
            
        # Write updated changelog
        with open(changelog_path, "w") as f:
            f.write(content)
            
        print(f"✅ Updated {changelog_path}")
        
    def create_initial_changelog(self) -> str:
        """Create initial CHANGELOG.md content"""
        return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""
        
    def generate_release_notes(self, version: str) -> str:
        """Generate release notes for a specific version"""
        section = self.generate_changelog_section(version)
        
        # Extract just the content without version header
        lines = section.split("\n")[2:]  # Skip version header and empty line
        
        return "\n".join(lines)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate changelog from commits")
    parser.add_argument("--update", action="store_true", help="Update CHANGELOG.md")
    parser.add_argument("--version", help="Generate for specific version")
    parser.add_argument("--release-notes", action="store_true", help="Generate release notes only")
    
    args = parser.parse_args()
    
    generator = ChangelogGenerator(project_root)
    
    if args.update:
        generator.update_changelog_file()
    elif args.release_notes:
        notes = generator.generate_release_notes(args.version or "Unreleased")
        print(notes)
    else:
        section = generator.generate_changelog_section(args.version or "Unreleased")
        print(section)


if __name__ == "__main__":
    main()