#!/usr/bin/env python3
"""
Main Audio Test Runner
Runs all audio converter tests and generates comprehensive reports.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List

def run_command(cmd: List[str], description: str) -> Dict[str, Any]:
    """Run a command and capture output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✓ Completed in {duration:.2f} seconds")
        
        return {
            "success": True,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✗ Failed after {duration:.2f} seconds")
        print(f"Error: {e}")
        if e.stdout:
            print(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"STDERR:\n{e.stderr}")
        
        return {
            "success": False,
            "duration": duration,
            "error": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr
        }


def check_dependencies():
    """Check and install required dependencies."""
    print("\n=== Checking Dependencies ===")
    
    dependencies = {
        "speech_recognition": "SpeechRecognition",
        "pydub": "pydub",
        "gtts": "gtts",
        "psutil": "psutil",
        "numpy": "numpy",
        "matplotlib": "matplotlib"
    }
    
    missing = []
    
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - Missing")
            missing.append(package)
    
    # Check for ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ ffmpeg")
    except:
        print("✗ ffmpeg - Missing (required for format conversion)")
        print("  Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
    
    if missing:
        print(f"\nInstall missing dependencies with:")
        print(f"  pip install {' '.join(missing)}")
        
        response = input("\nInstall now? (y/N): ")
        if response.lower() == 'y':
            cmd = [sys.executable, "-m", "pip", "install"] + missing
            subprocess.run(cmd)
    
    return len(missing) == 0


def main():
    """Main test runner."""
    print("Audio Converter Test Suite")
    print("=" * 80)
    print("This will run comprehensive tests for audio conversion capabilities")
    print("including speech recognition, format support, and Korean language processing.")
    print("=" * 80)
    
    # Check dependencies
    if not check_dependencies():
        print("\nSome dependencies are missing. Tests may be limited.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    # Test scripts to run
    test_dir = Path(__file__).parent
    test_scripts = [
        {
            "script": "test_audio_generation.py",
            "description": "Generate test audio files",
            "required": True
        },
        {
            "script": "test_audio_converter_comprehensive.py",
            "description": "Comprehensive audio converter tests",
            "required": True
        },
        {
            "script": "benchmark_audio_performance.py",
            "description": "Performance benchmarking",
            "required": False
        },
        {
            "script": "test_korean_audio_recognition.py",
            "description": "Korean language recognition tests",
            "required": False
        }
    ]
    
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {}
    }
    
    # Run each test script
    for test_info in test_scripts:
        script_path = test_dir / test_info["script"]
        
        if not script_path.exists():
            print(f"\nWarning: {test_info['script']} not found")
            continue
        
        cmd = [sys.executable, str(script_path)]
        result = run_command(cmd, test_info["description"])
        
        results["tests"][test_info["script"]] = {
            "description": test_info["description"],
            "success": result["success"],
            "duration": result["duration"],
            "required": test_info["required"]
        }
        
        if not result["success"] and test_info["required"]:
            print(f"\nCritical test failed: {test_info['script']}")
            print("Stopping test suite.")
            break
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    
    total_tests = len(results["tests"])
    successful_tests = sum(1 for t in results["tests"].values() if t["success"])
    total_duration = sum(t["duration"] for t in results["tests"].values())
    
    print(f"\nTotal tests run: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Total duration: {total_duration:.2f} seconds")
    
    print("\nIndividual test results:")
    for script, result in results["tests"].items():
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {script}: {result['duration']:.2f}s")
    
    # Save summary
    summary_file = test_dir / "test_suite_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest summary saved to: {summary_file}")
    
    # List generated reports
    print("\nGenerated reports:")
    report_files = [
        "test_audio_files/test_metadata.json",
        "test_results/audio_test_results.json",
        "test_results/audio_test_report.md",
        "benchmark_results/benchmark_results.json",
        "benchmark_results/benchmark_report.md",
        "korean_audio_tests/korean_audio_test_results.json",
        "korean_audio_tests/korean_audio_test_report.md"
    ]
    
    for report in report_files:
        report_path = test_dir / report
        if report_path.exists():
            print(f"  ✓ {report}")
    
    print("\n" + "=" * 80)
    print("Audio test suite complete!")
    
    return 0 if successful_tests == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())