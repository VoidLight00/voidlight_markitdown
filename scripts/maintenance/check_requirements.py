#!/usr/bin/env python3
"""Check and validate requirements files."""

import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pkg_resources


def parse_requirements(file_path: Path) -> Set[str]:
    """Parse requirements from a file."""
    requirements = set()
    
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Skip -r references
            if line.startswith("-r"):
                continue
            # Extract package name
            if "==" in line:
                pkg_name = line.split("==")[0].strip()
            elif ">=" in line:
                pkg_name = line.split(">=")[0].strip()
            elif ">" in line:
                pkg_name = line.split(">")[0].strip()
            elif "[" in line:
                pkg_name = line.split("[")[0].strip()
            else:
                pkg_name = line.strip()
                
            requirements.add(pkg_name.lower())
            
    return requirements


def check_duplicates(requirements_dir: Path) -> List[Tuple[str, List[str]]]:
    """Check for duplicate packages across requirement files."""
    file_packages: Dict[str, Set[str]] = {}
    
    for req_file in requirements_dir.glob("*.txt"):
        packages = parse_requirements(req_file)
        file_packages[req_file.name] = packages
        
    # Find duplicates
    duplicates = []
    files = list(file_packages.keys())
    
    for i, file1 in enumerate(files):
        for file2 in files[i+1:]:
            common = file_packages[file1] & file_packages[file2]
            
            # Exclude base.txt from duplicate checks as it's expected to be included
            if "base.txt" in [file1, file2]:
                continue
                
            if common:
                duplicates.append((f"{file1} & {file2}", sorted(list(common))))
                
    return duplicates


def check_conflicts(requirements_dir: Path) -> List[str]:
    """Check for potential version conflicts."""
    conflicts = []
    all_requirements = {}
    
    for req_file in requirements_dir.glob("*.txt"):
        with open(req_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-r"):
                    continue
                    
                # Parse package and version
                if "==" in line:
                    pkg_name, version = line.split("==", 1)
                    pkg_name = pkg_name.strip().lower()
                    
                    if pkg_name in all_requirements:
                        if all_requirements[pkg_name] != version.strip():
                            conflicts.append(
                                f"{pkg_name}: {all_requirements[pkg_name]} vs {version.strip()}"
                            )
                    else:
                        all_requirements[pkg_name] = version.strip()
                        
    return conflicts


def check_missing_base(requirements_dir: Path) -> List[Tuple[str, bool]]:
    """Check if non-base requirement files include base.txt."""
    results = []
    
    for req_file in requirements_dir.glob("*.txt"):
        if req_file.name == "base.txt":
            continue
            
        includes_base = False
        with open(req_file, "r") as f:
            for line in f:
                if line.strip() == "-r base.txt":
                    includes_base = True
                    break
                    
        results.append((req_file.name, includes_base))
        
    return results


def main():
    """Main function."""
    requirements_dir = Path(__file__).parent.parent.parent / "requirements"
    
    if not requirements_dir.exists():
        print(f"Error: Requirements directory not found: {requirements_dir}")
        sys.exit(1)
        
    print("Checking requirements files...\n")
    
    # Check for duplicates
    duplicates = check_duplicates(requirements_dir)
    if duplicates:
        print("⚠️  Found duplicate packages:")
        for files, packages in duplicates:
            print(f"  {files}:")
            for pkg in packages:
                print(f"    - {pkg}")
        print()
    else:
        print("✓ No duplicate packages found\n")
        
    # Check for conflicts
    conflicts = check_conflicts(requirements_dir)
    if conflicts:
        print("⚠️  Found version conflicts:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        print()
    else:
        print("✓ No version conflicts found\n")
        
    # Check base.txt inclusion
    base_inclusion = check_missing_base(requirements_dir)
    missing_base = [f for f, included in base_inclusion if not included]
    
    if missing_base:
        print("⚠️  Files not including base.txt:")
        for file in missing_base:
            print(f"  - {file}")
        print()
    else:
        print("✓ All requirement files properly include base.txt\n")
        
    # Return non-zero exit code if issues found
    if duplicates or conflicts or missing_base:
        sys.exit(1)
    else:
        print("All requirements checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()