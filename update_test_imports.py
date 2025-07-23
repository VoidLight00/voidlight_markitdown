#!/usr/bin/env python3
"""
Update imports in test files after reorganization.
This script ensures all test files use proper absolute imports.
"""

import os
import re
from pathlib import Path


def update_imports_in_file(file_path: Path) -> bool:
    """Update imports in a single test file."""
    updated = False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update relative imports to absolute imports
        # Pattern: from ..something import Something
        content = re.sub(
            r'from \.\.([\w\.]+) import',
            r'from voidlight_markitdown\1 import',
            content
        )
        
        # Pattern: from . import something
        content = re.sub(
            r'from \. import',
            r'from voidlight_markitdown import',
            content
        )
        
        # Update sys.path manipulations for new structure
        if 'sys.path' in content:
            # Remove old sys.path manipulations
            content = re.sub(
                r'sys\.path\.insert\(0, .*\n',
                '',
                content
            )
            
            # Add new imports after the import statements
            import_section_end = 0
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith(('import', 'from')):
                    import_section_end = i
                    break
            
            # The conftest.py handles path setup now
            
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            updated = True
            print(f"Updated: {file_path}")
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return updated


def main():
    """Update imports in all test files."""
    test_root = Path(__file__).parent
    test_files = list(test_root.rglob("test_*.py"))
    test_files.extend(test_root.rglob("*_test.py"))
    
    updated_count = 0
    for test_file in test_files:
        if update_imports_in_file(test_file):
            updated_count += 1
    
    print(f"\nTotal files updated: {updated_count}/{len(test_files)}")


if __name__ == "__main__":
    main()