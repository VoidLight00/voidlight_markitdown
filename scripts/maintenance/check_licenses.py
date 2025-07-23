#!/usr/bin/env python3
"""
License compliance checker for voidlight-markitdown
Validates that all dependencies have compatible licenses
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class LicenseChecker:
    """Check dependency licenses for compatibility"""
    
    # List of approved licenses (compatible with MIT)
    APPROVED_LICENSES = {
        "MIT",
        "MIT License",
        "BSD",
        "BSD License",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "Apache",
        "Apache 2.0",
        "Apache Software License",
        "Apache License 2.0",
        "ISC",
        "ISC License",
        "Python Software Foundation License",
        "PSF",
        "Unlicense",
        "CC0",
        "CC-BY",
        "CC-BY-SA",
        "Public Domain",
        "WTFPL",
    }
    
    # Licenses that need review
    REVIEW_LICENSES = {
        "GPL",
        "GPLv2",
        "GPLv3",
        "LGPL",
        "LGPLv2",
        "LGPLv3",
        "AGPL",
        "AGPLv3",
    }
    
    # Known package license overrides (for packages with incorrect metadata)
    LICENSE_OVERRIDES = {
        # Add any known overrides here
        # "package-name": "Actual License",
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        self.warnings = []
        
    def get_installed_packages(self) -> List[Dict]:
        """Get list of installed packages with licenses"""
        # Run pip-licenses command
        result = subprocess.run(
            ["pip-licenses", "--format=json", "--with-urls", "--with-description"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError("Failed to get package licenses")
            
        return json.loads(result.stdout)
        
    def normalize_license(self, license_str: str) -> str:
        """Normalize license string for comparison"""
        if not license_str:
            return "UNKNOWN"
            
        # Clean up the string
        license_str = license_str.strip()
        
        # Common normalizations
        replacements = {
            "MIT license": "MIT",
            "BSD license": "BSD",
            "Apache License, Version 2.0": "Apache 2.0",
            "3-Clause BSD License": "BSD-3-Clause",
            "2-Clause BSD License": "BSD-2-Clause",
        }
        
        for old, new in replacements.items():
            if old.lower() in license_str.lower():
                return new
                
        return license_str
        
    def check_license_compatibility(self, package: Dict) -> str:
        """Check if a package license is compatible"""
        package_name = package.get("Name", "Unknown")
        license_str = package.get("License", "")
        
        # Check for override
        if package_name in self.LICENSE_OVERRIDES:
            license_str = self.LICENSE_OVERRIDES[package_name]
            
        # Normalize license
        normalized = self.normalize_license(license_str)
        
        # Check if approved
        if any(approved.lower() in normalized.lower() for approved in self.APPROVED_LICENSES):
            return "approved"
            
        # Check if needs review
        if any(review.lower() in normalized.lower() for review in self.REVIEW_LICENSES):
            return "review"
            
        # Check if unknown
        if normalized == "UNKNOWN" or not normalized:
            return "unknown"
            
        # Otherwise, it's unapproved
        return "unapproved"
        
    def generate_license_report(self) -> Dict:
        """Generate comprehensive license report"""
        packages = self.get_installed_packages()
        
        report = {
            "total_packages": len(packages),
            "approved": [],
            "review_needed": [],
            "unknown": [],
            "unapproved": [],
            "summary": {},
        }
        
        # Analyze each package
        for package in packages:
            status = self.check_license_compatibility(package)
            package_info = {
                "name": package.get("Name"),
                "version": package.get("Version"),
                "license": package.get("License", "UNKNOWN"),
                "url": package.get("URL", ""),
            }
            
            if status == "approved":
                report["approved"].append(package_info)
            elif status == "review":
                report["review_needed"].append(package_info)
                self.warnings.append(f"{package_info['name']}: {package_info['license']} (needs review)")
            elif status == "unknown":
                report["unknown"].append(package_info)
                self.warnings.append(f"{package_info['name']}: Unknown license")
            else:
                report["unapproved"].append(package_info)
                self.issues.append(f"{package_info['name']}: {package_info['license']} (not approved)")
                
        # Generate summary
        report["summary"] = {
            "approved": len(report["approved"]),
            "review_needed": len(report["review_needed"]),
            "unknown": len(report["unknown"]),
            "unapproved": len(report["unapproved"]),
        }
        
        return report
        
    def generate_notice_file(self, report: Dict):
        """Generate NOTICE file for attribution"""
        notice_path = self.project_root / "NOTICE"
        
        content = ["THIRD-PARTY SOFTWARE NOTICES AND INFORMATION"]
        content.append("=" * 50)
        content.append("")
        content.append("This project uses the following third-party packages:")
        content.append("")
        
        # Group by license
        by_license = {}
        for package in report["approved"]:
            license_name = package["license"]
            if license_name not in by_license:
                by_license[license_name] = []
            by_license[license_name].append(package)
            
        # Add each license group
        for license_name, packages in sorted(by_license.items()):
            content.append(f"\n## {license_name}")
            content.append("")
            
            for package in sorted(packages, key=lambda x: x["name"]):
                content.append(f"- {package['name']} ({package['version']})")
                if package.get("url"):
                    content.append(f"  {package['url']}")
                    
        # Add attribution
        content.append("")
        content.append("-" * 50)
        content.append("For full license texts, please see the individual packages.")
        
        with open(notice_path, "w") as f:
            f.write("\n".join(content))
            
        print(f"✅ Generated {notice_path}")
        
    def run_check(self) -> bool:
        """Run license compliance check"""
        print("🔍 Checking license compliance...")
        
        try:
            report = self.generate_license_report()
            
            # Save detailed report
            report_path = self.project_root / "build-reports/license-report.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
                
            print(f"\n📊 License Report Summary:")
            print(f"  Total packages: {report['summary']['approved'] + report['summary']['review_needed'] + report['summary']['unknown'] + report['summary']['unapproved']}")
            print(f"  ✅ Approved: {report['summary']['approved']}")
            print(f"  ⚠️  Review needed: {report['summary']['review_needed']}")
            print(f"  ❓ Unknown: {report['summary']['unknown']}")
            print(f"  ❌ Unapproved: {report['summary']['unapproved']}")
            
            # Print issues
            if self.issues:
                print("\n❌ License Issues (must resolve):")
                for issue in self.issues:
                    print(f"  - {issue}")
                    
            if self.warnings:
                print("\n⚠️  License Warnings (should review):")
                for warning in self.warnings:
                    print(f"  - {warning}")
                    
            # Generate NOTICE file
            self.generate_notice_file(report)
            
            print(f"\n📄 Detailed report saved to: {report_path}")
            
            # Return success if no blocking issues
            return len(self.issues) == 0
            
        except Exception as e:
            print(f"❌ License check failed: {e}")
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check dependency licenses")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")
    parser.add_argument("--update-notice", action="store_true", help="Update NOTICE file")
    
    args = parser.parse_args()
    
    checker = LicenseChecker(project_root)
    
    if checker.run_check():
        if args.strict and checker.warnings:
            print("\n❌ Strict mode: failing due to warnings")
            sys.exit(1)
        else:
            print("\n✅ License check passed!")
            sys.exit(0)
    else:
        print("\n❌ License check failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()