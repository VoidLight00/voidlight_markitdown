#!/usr/bin/env python3
"""Generate release notes for a specific version."""

import sys
import subprocess
from pathlib import Path
import re
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.maintenance.generate_changelog import ChangelogGenerator

class ReleaseNotesGenerator(ChangelogGenerator):
    """Generate release notes for a specific version."""
    
    def __init__(self, project_root: Path = None):
        super().__init__(project_root or Path.cwd())
    
    def generate_release_notes(self, version: str) -> str:
        """Generate release notes for a specific version."""
        # Get commits since last tag
        last_tag = self.get_last_version_tag()
        commits = self.get_commits_since_tag(last_tag)
        
        if not commits:
            return "No changes in this release."
        
        # Group commits by type
        grouped = self.group_commits_by_type(commits)
        
        # Build release notes
        lines = [f"# Release v{version}\n"]
        
        # Add summary
        total_commits = len(commits)
        lines.append(f"This release includes {total_commits} commits")
        
        # Count by type
        type_counts = []
        if "Added" in grouped:
            type_counts.append(f"{len(grouped['Added'])} new features")
        if "Fixed" in grouped:
            type_counts.append(f"{len(grouped['Fixed'])} bug fixes")
        if "Performance" in grouped:
            type_counts.append(f"{len(grouped['Performance'])} performance improvements")
        
        if type_counts:
            lines.append(f"with {', '.join(type_counts)}.")
        else:
            lines.append(".")
        
        lines.append("")
        
        # Check for Korean language improvements
        korean_commits = []
        for commit_list in grouped.values():
            for commit in commit_list:
                if any(k in commit['description'].lower() for k in ['korean', '한국', 'hangul', '한글']):
                    korean_commits.append(commit)
        
        if korean_commits:
            lines.append("## 🇰🇷 Korean Language Enhancements\n")
            lines.append(f"This release includes {len(korean_commits)} improvements to Korean language support:")
            for commit in korean_commits[:3]:  # Show top 3
                lines.append(f"- {commit['description']}")
            if len(korean_commits) > 3:
                lines.append(f"- ...and {len(korean_commits) - 3} more")
            lines.append("")
        
        # Add highlights section
        if grouped:
            lines.append("## Highlights\n")
            
            # Features
            if "Added" in grouped:
                lines.append("### ✨ New Features\n")
                for commit in grouped["Added"][:5]:  # Top 5 features
                    lines.append(self.format_commit_line(commit))
                if len(grouped["Added"]) > 5:
                    lines.append(f"- ...and {len(grouped['Added']) - 5} more features")
                lines.append("")
            
            # Bug fixes
            if "Fixed" in grouped:
                lines.append("### 🐛 Bug Fixes\n")
                for commit in grouped["Fixed"][:5]:  # Top 5 fixes
                    lines.append(self.format_commit_line(commit))
                if len(grouped["Fixed"]) > 5:
                    lines.append(f"- ...and {len(grouped['Fixed']) - 5} more fixes")
                lines.append("")
            
            # Performance
            if "Performance" in grouped:
                lines.append("### ⚡ Performance Improvements\n")
                for commit in grouped["Performance"]:
                    lines.append(self.format_commit_line(commit))
                lines.append("")
        
        # Add installation section
        lines.extend([
            "## Installation\n",
            "### PyPI\n",
            "```bash",
            "pip install voidlight-markitdown",
            "```\n",
            "### Upgrade\n",
            "```bash",
            "pip install --upgrade voidlight-markitdown",
            "```\n",
            "### Docker\n",
            "```bash",
            f"docker pull voidlight/voidlight-markitdown:{version}",
            "```\n",
            "### MCP Server\n",
            "```bash",
            "pip install voidlight-markitdown[mcp]",
            "```\n"
        ])
        
        # Add breaking changes warning if any
        breaking_changes = self.find_breaking_changes(commits)
        if breaking_changes:
            lines.extend([
                "## ⚠️ Breaking Changes\n",
                "This release contains breaking changes. Please review the following before upgrading:\n"
            ])
            for change in breaking_changes:
                lines.append(f"- {change}")
            lines.append("")
        
        # Add migration guide if needed
        if breaking_changes:
            lines.extend([
                "## Migration Guide\n",
                "To migrate from the previous version:\n",
                "1. Update your imports if using the library programmatically",
                "2. Review changed APIs in the documentation",
                "3. Test your integration thoroughly\n",
                "For detailed migration instructions, see the documentation.\n"
            ])
        
        # Add contributors section
        contributors = self.get_contributors_since_tag(last_tag)
        if contributors:
            lines.extend([
                "## Contributors\n",
                f"Thanks to the {len(contributors)} contributors who made this release possible:\n"
            ])
            for contributor in sorted(contributors):
                lines.append(f"- @{contributor}")
            lines.append("")
        
        # Add full changelog link
        lines.extend([
            "## Full Changelog\n",
            f"For a complete list of changes, see the [CHANGELOG](https://github.com/voidlight/voidlight_markitdown/blob/v{version}/CHANGELOG.md).\n"
        ])
        
        return "\n".join(lines)
    
    def find_breaking_changes(self, commits: List[Dict]) -> List[str]:
        """Find breaking changes in commits."""
        breaking = []
        
        for commit in commits:
            subject = commit.get("subject", "")
            body = commit.get("body", "")
            
            if "BREAKING CHANGE" in subject or "BREAKING CHANGE" in body:
                breaking.append(commit["description"])
            elif commit.get("type") == "feat" and "!" in subject:
                breaking.append(commit["description"])
        
        return breaking
    
    def get_contributors_since_tag(self, tag: str) -> List[str]:
        """Get unique contributors since last tag."""
        cmd = ["git", "log", "--format=%an"]
        if tag:
            cmd.append(f"{tag}..HEAD")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        
        if result.returncode != 0:
            return []
        
        contributors = set()
        for line in result.stdout.strip().split("\n"):
            if line and line != "VoidLight":  # Exclude bot/default
                contributors.add(line)
        
        return list(contributors)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate release notes")
    parser.add_argument(
        "version",
        help="Version to generate release notes for"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    generator = ReleaseNotesGenerator()
    notes = generator.generate_release_notes(args.version)
    
    # Format output
    if args.format == "html":
        try:
            import markdown
            notes = markdown.markdown(notes)
        except ImportError:
            print("Warning: markdown package not installed, outputting raw markdown", file=sys.stderr)
    elif args.format == "json":
        import json
        notes = json.dumps({
            "version": args.version,
            "content": notes,
            "format": "markdown"
        }, indent=2)
    
    # Output
    if args.output:
        args.output.write_text(notes)
        print(f"Release notes written to: {args.output}")
    else:
        print(notes)

if __name__ == "__main__":
    main()