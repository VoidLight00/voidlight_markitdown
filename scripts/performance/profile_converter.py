#!/usr/bin/env python3
"""
Performance profiling script for voidlight_markitdown converters.

This script profiles the performance of different converters and generates
detailed reports including timing, memory usage, and bottlenecks.
"""

import argparse
import cProfile
import io
import os
import pstats
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from voidlight_markitdown import MarkItDown


def profile_converter(
    file_path: str,
    repeat: int = 1,
    profile_memory: bool = True
) -> Tuple[Dict[str, float], Optional[pstats.Stats], Optional[List]]:
    """Profile a converter's performance.
    
    Args:
        file_path: Path to the file to convert
        repeat: Number of times to repeat the conversion
        profile_memory: Whether to profile memory usage
        
    Returns:
        Tuple of (timing_results, cpu_profile, memory_snapshots)
    """
    markitdown = MarkItDown()
    
    # Timing results
    timing_results = {
        "min_time": float("inf"),
        "max_time": 0,
        "avg_time": 0,
        "total_time": 0,
    }
    
    # CPU profiling
    profiler = cProfile.Profile()
    
    # Memory profiling
    memory_snapshots = []
    
    times = []
    for i in range(repeat):
        # Memory snapshot before
        if profile_memory and i == 0:
            tracemalloc.start()
            
        # Time the conversion
        start_time = time.perf_counter()
        
        profiler.enable()
        result = markitdown.convert(file_path)
        profiler.disable()
        
        end_time = time.perf_counter()
        
        # Memory snapshot after
        if profile_memory and i == 0:
            snapshot = tracemalloc.take_snapshot()
            memory_snapshots.append(snapshot)
            tracemalloc.stop()
            
        elapsed = end_time - start_time
        times.append(elapsed)
        
        print(f"Run {i+1}/{repeat}: {elapsed:.3f}s")
        
    # Calculate timing statistics
    timing_results["min_time"] = min(times)
    timing_results["max_time"] = max(times)
    timing_results["avg_time"] = sum(times) / len(times)
    timing_results["total_time"] = sum(times)
    
    # Create stats object
    stats = pstats.Stats(profiler)
    
    return timing_results, stats, memory_snapshots


def print_timing_results(timing_results: Dict[str, float], file_path: str):
    """Print timing results in a formatted table."""
    print(f"\n{'='*50}")
    print(f"Performance Results for: {Path(file_path).name}")
    print(f"{'='*50}")
    print(f"{'Metric':<20} {'Value':>15}")
    print(f"{'-'*36}")
    print(f"{'Minimum Time':<20} {timing_results['min_time']:>14.3f}s")
    print(f"{'Maximum Time':<20} {timing_results['max_time']:>14.3f}s")
    print(f"{'Average Time':<20} {timing_results['avg_time']:>14.3f}s")
    print(f"{'Total Time':<20} {timing_results['total_time']:>14.3f}s")
    

def print_cpu_profile(stats: pstats.Stats, top_n: int = 20):
    """Print CPU profiling results."""
    print(f"\n{'='*50}")
    print(f"Top {top_n} Functions by Cumulative Time")
    print(f"{'='*50}")
    
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(top_n)
    
    print(f"\n{'='*50}")
    print(f"Top {top_n} Functions by Total Time")
    print(f"{'='*50}")
    
    stats.sort_stats("tottime")
    stats.print_stats(top_n)


def print_memory_profile(memory_snapshots: List):
    """Print memory profiling results."""
    if not memory_snapshots:
        return
        
    print(f"\n{'='*50}")
    print("Memory Usage Analysis")
    print(f"{'='*50}")
    
    snapshot = memory_snapshots[0]
    top_stats = snapshot.statistics("lineno")
    
    print("\nTop 10 memory allocations:")
    for index, stat in enumerate(top_stats[:10], 1):
        print(f"{index}. {stat}")
        
    # Total memory usage
    total = sum(stat.size for stat in top_stats)
    print(f"\nTotal allocated: {total / 1024 / 1024:.2f} MB")


def profile_all_converters(test_dir: Path, repeat: int = 1):
    """Profile all converters with available test files."""
    test_files = {
        "PDF": test_dir / "test.pdf",
        "DOCX": test_dir / "test.docx",
        "PPTX": test_dir / "test.pptx",
        "XLSX": test_dir / "test.xlsx",
        "HTML": test_dir / "test_blog.html",
        "EPUB": test_dir / "test.epub",
        "Image": test_dir / "test.jpg",
    }
    
    results = {}
    
    for converter_name, file_path in test_files.items():
        if file_path.exists():
            print(f"\n{'#'*60}")
            print(f"Profiling {converter_name} Converter")
            print(f"{'#'*60}")
            
            try:
                timing, stats, memory = profile_converter(
                    str(file_path),
                    repeat=repeat,
                    profile_memory=True
                )
                
                results[converter_name] = {
                    "timing": timing,
                    "stats": stats,
                    "memory": memory
                }
                
                print_timing_results(timing, str(file_path))
                
            except Exception as e:
                print(f"Error profiling {converter_name}: {e}")
                
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Profile voidlight_markitdown converter performance"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="File to profile (optional, profiles all if not specified)"
    )
    parser.add_argument(
        "-r", "--repeat",
        type=int,
        default=3,
        help="Number of times to repeat conversion (default: 3)"
    )
    parser.add_argument(
        "-t", "--top",
        type=int,
        default=20,
        help="Number of top functions to show (default: 20)"
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable memory profiling"
    )
    parser.add_argument(
        "--save-stats",
        help="Save profiling stats to file"
    )
    
    args = parser.parse_args()
    
    if args.file:
        # Profile single file
        timing, stats, memory = profile_converter(
            args.file,
            repeat=args.repeat,
            profile_memory=not args.no_memory
        )
        
        print_timing_results(timing, args.file)
        print_cpu_profile(stats, args.top)
        
        if not args.no_memory:
            print_memory_profile(memory)
            
        if args.save_stats:
            stats.dump_stats(args.save_stats)
            print(f"\nStats saved to: {args.save_stats}")
            
    else:
        # Profile all converters
        test_dir = Path(__file__).parent.parent.parent / "tests" / "fixtures"
        results = profile_all_converters(test_dir, repeat=args.repeat)
        
        # Summary
        print(f"\n{'='*60}")
        print("Performance Summary")
        print(f"{'='*60}")
        print(f"{'Converter':<15} {'Avg Time (s)':>15} {'Memory (MB)':>15}")
        print(f"{'-'*45}")
        
        for converter, data in results.items():
            avg_time = data["timing"]["avg_time"]
            memory_mb = "N/A"
            
            if data.get("memory"):
                snapshot = data["memory"][0]
                stats = snapshot.statistics("lineno")
                total_bytes = sum(stat.size for stat in stats)
                memory_mb = f"{total_bytes / 1024 / 1024:.2f}"
                
            print(f"{converter:<15} {avg_time:>14.3f} {memory_mb:>15}")


if __name__ == "__main__":
    main()