#!/usr/bin/env python3
"""
Generate a clean summary of the converter test results.
"""

import json
from pathlib import Path
from collections import defaultdict

def generate_summary():
    # Load test results
    with open('converter_test_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Group by converter
    converter_status = defaultdict(lambda: {'success': 0, 'failed': 0, 'skipped': 0, 'files': []})
    
    for result in results:
        converter = result['converter_name']
        status = result['status']
        file_name = result['test_file']
        
        # Count status
        converter_status[converter][status] += 1
        
        # Track files tested
        if file_name not in converter_status[converter]['files']:
            converter_status[converter]['files'].append(file_name)
    
    # Print summary table
    print("\n" + "=" * 80)
    print("VOIDLIGHT MARKITDOWN CONVERTER TEST SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Converter':<25} {'Status':<12} {'Success':<10} {'Failed':<10} {'Files Tested'}")
    print("-" * 80)
    
    # Sort converters by name
    for converter in sorted(converter_status.keys()):
        stats = converter_status[converter]
        total = stats['success'] + stats['failed'] + stats['skipped']
        
        # Determine overall status
        if stats['failed'] > 0:
            status = "❌ FAILING"
        elif stats['skipped'] == total:
            status = "⚠️  SKIPPED"
        else:
            status = "✅ WORKING"
        
        files = ', '.join(stats['files'])
        if len(files) > 30:
            files = files[:27] + "..."
        
        print(f"{converter:<25} {status:<12} {stats['success']:<10} {stats['failed']:<10} {files}")
    
    # Print issues that need fixing
    print("\n" + "=" * 80)
    print("ISSUES REQUIRING ATTENTION")
    print("=" * 80)
    print()
    
    missing_deps = set()
    other_errors = []
    
    for result in results:
        if result['status'] == 'failed' and result['error']:
            if 'MissingDependencyException' in result['error']:
                # Extract the dependency type
                if 'docx' in result['error']:
                    missing_deps.add('docx')
                elif 'xlsx' in result['error']:
                    missing_deps.add('xlsx')
                elif 'xls' in result['error']:
                    missing_deps.add('xls')
                elif 'pptx' in result['error']:
                    missing_deps.add('pptx')
                elif 'outlook' in result['error']:
                    missing_deps.add('outlook')
            elif 'TypeError' in result['error']:
                error_msg = result['error'].split(':')[1].split('\n')[0].strip()
                other_errors.append(f"{result['converter_name']}: {error_msg}")
    
    if missing_deps:
        print("1. Missing Dependencies:")
        print("   The following optional dependencies are not installed:")
        for dep in sorted(missing_deps):
            print(f"   - {dep}")
        print("\n   To install all dependencies, run:")
        print("   pip install voidlight-markitdown[all]")
    
    if other_errors:
        print("\n2. Code Errors:")
        for error in other_errors:
            print(f"   - {error}")
    
    # Korean processing summary
    print("\n" + "=" * 80)
    print("KOREAN PROCESSING TEST RESULTS")
    print("=" * 80)
    print()
    
    korean_tests = [r for r in results if 'Korean mode' in str(r)]
    if korean_tests:
        print(f"Total Korean mode tests: {len(korean_tests)}")
        korean_success = sum(1 for r in korean_tests if r['status'] == 'success')
        print(f"Successful: {korean_success}")
        
        # Check if any Korean content was detected
        korean_detected = sum(1 for r in results if r.get('korean_content_found', False))
        if korean_detected > 0:
            print(f"Korean content detected in {korean_detected} tests")
        else:
            print("No Korean content was detected in test files")
            print("Note: Test files may not contain Korean text")
    
    print("\n" + "=" * 80)
    print()

if __name__ == "__main__":
    generate_summary()