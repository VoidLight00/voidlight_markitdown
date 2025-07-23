#!/usr/bin/env python3
"""
Audio Converter Performance Benchmarking
Measures performance characteristics of audio conversion and speech recognition.
"""

import os
import sys
import time
import json
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from voidlight_markitdown import VoidlightMarkItDown
except ImportError as e:
    print(f"Failed to import voidlight_markitdown: {e}")
    sys.exit(1)


class AudioPerformanceBenchmark:
    """Benchmark audio conversion performance."""
    
    def __init__(self):
        self.markitdown = VoidlightMarkItDown()
        self.results_dir = Path(__file__).parent / "benchmark_results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.benchmark_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": self._get_system_info(),
            "benchmarks": {}
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "platform": sys.platform,
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "available_memory_gb": psutil.virtual_memory().available / (1024**3)
        }
    
    def _monitor_resources(self, stop_event: threading.Event) -> Dict[str, List[float]]:
        """Monitor CPU and memory usage during operation."""
        cpu_usage = []
        memory_usage = []
        
        while not stop_event.is_set():
            cpu_usage.append(psutil.cpu_percent(interval=0.1))
            memory_usage.append(psutil.virtual_memory().percent)
            time.sleep(0.1)
        
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "avg_cpu": np.mean(cpu_usage) if cpu_usage else 0,
            "max_cpu": max(cpu_usage) if cpu_usage else 0,
            "avg_memory": np.mean(memory_usage) if memory_usage else 0,
            "max_memory": max(memory_usage) if memory_usage else 0
        }
    
    def benchmark_file_size_scaling(self):
        """Benchmark how performance scales with file size."""
        print("\n=== File Size Scaling Benchmark ===")
        
        # Test different file sizes (durations in seconds)
        durations = [1, 5, 10, 30, 60, 120, 300]
        results = []
        
        for duration in durations:
            print(f"\nTesting {duration} second audio file...")
            
            # Create test file
            test_file = self._create_test_file(duration)
            file_size = os.path.getsize(test_file) / (1024 * 1024)  # MB
            
            # Monitor resources
            stop_event = threading.Event()
            monitor_thread = threading.Thread(
                target=lambda: self._monitor_resources(stop_event),
                args=(stop_event,)
            )
            
            # Measure conversion time
            monitor_thread.start()
            start_time = time.time()
            
            try:
                result = self.markitdown.convert(test_file)
                end_time = time.time()
                processing_time = end_time - start_time
                success = True
                error = None
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                success = False
                error = str(e)
            
            stop_event.set()
            monitor_thread.join()
            
            # Get resource usage
            resources = self._monitor_resources(stop_event)
            
            # Calculate metrics
            result_data = {
                "duration_seconds": duration,
                "file_size_mb": file_size,
                "processing_time": processing_time,
                "speed_mb_per_sec": file_size / processing_time if processing_time > 0 else 0,
                "realtime_factor": duration / processing_time if processing_time > 0 else 0,
                "success": success,
                "error": error,
                "avg_cpu_percent": resources["avg_cpu"],
                "max_cpu_percent": resources["max_cpu"],
                "avg_memory_percent": resources["avg_memory"],
                "max_memory_percent": resources["max_memory"]
            }
            
            results.append(result_data)
            
            print(f"  File size: {file_size:.2f} MB")
            print(f"  Processing time: {processing_time:.2f}s")
            print(f"  Speed: {result_data['speed_mb_per_sec']:.2f} MB/s")
            print(f"  Realtime factor: {result_data['realtime_factor']:.2f}x")
            print(f"  CPU usage: {resources['avg_cpu']:.1f}% avg, {resources['max_cpu']:.1f}% max")
            print(f"  Memory usage: {resources['avg_memory']:.1f}% avg, {resources['max_memory']:.1f}% max")
            
            # Cleanup
            os.remove(test_file)
        
        self.benchmark_results["benchmarks"]["file_size_scaling"] = results
        return results
    
    def benchmark_format_performance(self):
        """Benchmark performance across different audio formats."""
        print("\n=== Format Performance Benchmark ===")
        
        formats = ["wav", "mp3", "m4a", "ogg"]
        duration = 30  # seconds
        results = []
        
        for fmt in formats:
            print(f"\nTesting {fmt.upper()} format...")
            
            # Create test file
            test_file = self._create_test_file(duration, format=fmt)
            
            if not os.path.exists(test_file):
                print(f"  Skipping {fmt} - format not supported")
                continue
            
            file_size = os.path.getsize(test_file) / (1024 * 1024)  # MB
            
            # Measure conversion time (average of 3 runs)
            times = []
            for i in range(3):
                start_time = time.time()
                try:
                    result = self.markitdown.convert(test_file)
                    end_time = time.time()
                    times.append(end_time - start_time)
                except Exception as e:
                    print(f"  Error: {e}")
                    break
            
            if times:
                avg_time = np.mean(times)
                std_time = np.std(times)
                
                result_data = {
                    "format": fmt,
                    "file_size_mb": file_size,
                    "avg_processing_time": avg_time,
                    "std_processing_time": std_time,
                    "speed_mb_per_sec": file_size / avg_time,
                    "runs": len(times)
                }
                
                results.append(result_data)
                
                print(f"  File size: {file_size:.2f} MB")
                print(f"  Avg processing time: {avg_time:.2f}s ± {std_time:.3f}s")
                print(f"  Speed: {result_data['speed_mb_per_sec']:.2f} MB/s")
            
            # Cleanup
            os.remove(test_file)
        
        self.benchmark_results["benchmarks"]["format_performance"] = results
        return results
    
    def benchmark_sample_rate_impact(self):
        """Benchmark impact of different sample rates."""
        print("\n=== Sample Rate Impact Benchmark ===")
        
        sample_rates = [8000, 16000, 22050, 44100, 48000]
        duration = 30  # seconds
        results = []
        
        for rate in sample_rates:
            print(f"\nTesting {rate} Hz sample rate...")
            
            # Create test file
            test_file = self._create_test_file(duration, sample_rate=rate)
            file_size = os.path.getsize(test_file) / (1024 * 1024)  # MB
            
            start_time = time.time()
            try:
                result = self.markitdown.convert(test_file)
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Check if transcript was generated
                has_transcript = "Audio Transcript" in result.markdown
                
                result_data = {
                    "sample_rate": rate,
                    "file_size_mb": file_size,
                    "processing_time": processing_time,
                    "speed_mb_per_sec": file_size / processing_time,
                    "has_transcript": has_transcript,
                    "success": True
                }
                
            except Exception as e:
                result_data = {
                    "sample_rate": rate,
                    "file_size_mb": file_size,
                    "success": False,
                    "error": str(e)
                }
            
            results.append(result_data)
            
            if result_data.get("success"):
                print(f"  File size: {file_size:.2f} MB")
                print(f"  Processing time: {result_data['processing_time']:.2f}s")
                print(f"  Speed: {result_data['speed_mb_per_sec']:.2f} MB/s")
                print(f"  Transcript generated: {result_data['has_transcript']}")
            else:
                print(f"  Failed: {result_data.get('error')}")
            
            # Cleanup
            os.remove(test_file)
        
        self.benchmark_results["benchmarks"]["sample_rate_impact"] = results
        return results
    
    def benchmark_concurrent_load(self):
        """Benchmark concurrent processing capabilities."""
        print("\n=== Concurrent Load Benchmark ===")
        
        import concurrent.futures
        
        concurrent_levels = [1, 2, 4, 8]
        duration = 10  # seconds per file
        results = []
        
        for num_concurrent in concurrent_levels:
            print(f"\nTesting {num_concurrent} concurrent conversions...")
            
            # Create test files
            test_files = []
            for i in range(num_concurrent):
                test_file = self._create_test_file(duration)
                test_files.append(test_file)
            
            # Process concurrently
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(self.markitdown.convert, f) for f in test_files]
                
                success_count = 0
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        success_count += 1
                    except Exception as e:
                        print(f"    Concurrent error: {e}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calculate throughput
            total_size_mb = sum(os.path.getsize(f) / (1024 * 1024) for f in test_files)
            throughput = total_size_mb / total_time
            
            result_data = {
                "concurrent_count": num_concurrent,
                "total_files": num_concurrent,
                "successful": success_count,
                "total_time": total_time,
                "avg_time_per_file": total_time / num_concurrent,
                "total_size_mb": total_size_mb,
                "throughput_mb_per_sec": throughput
            }
            
            results.append(result_data)
            
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Avg time per file: {result_data['avg_time_per_file']:.2f}s")
            print(f"  Throughput: {throughput:.2f} MB/s")
            print(f"  Success rate: {success_count}/{num_concurrent}")
            
            # Cleanup
            for f in test_files:
                os.remove(f)
        
        self.benchmark_results["benchmarks"]["concurrent_load"] = results
        return results
    
    def _create_test_file(self, duration: int, format: str = "wav", 
                         sample_rate: int = 44100) -> str:
        """Create a test audio file."""
        import wave
        import struct
        import math
        
        filename = f"test_{duration}s_{sample_rate}hz.{format}"
        filepath = self.results_dir / filename
        
        if format == "wav":
            # Create WAV file
            with wave.open(str(filepath), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Generate a simple tone with varying frequency
                num_frames = sample_rate * duration
                frames = []
                
                for i in range(num_frames):
                    t = i / sample_rate
                    # Varying frequency from 440Hz to 880Hz
                    frequency = 440 + 440 * (i / num_frames)
                    value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t))
                    frames.append(value)
                
                data = struct.pack('<' + 'h' * num_frames, *frames)
                wav_file.writeframes(data)
        
        else:
            # For other formats, create WAV first then convert
            wav_file = str(filepath).replace(f".{format}", ".wav")
            self._create_test_file(duration, "wav", sample_rate)
            
            # Use ffmpeg to convert if available
            try:
                import subprocess
                cmd = ["ffmpeg", "-i", wav_file, "-y", str(filepath)]
                subprocess.run(cmd, capture_output=True, check=True)
                os.remove(wav_file)
            except:
                # If conversion fails, just rename to WAV
                os.rename(wav_file, str(filepath))
        
        return str(filepath)
    
    def generate_visualizations(self):
        """Generate performance visualization plots."""
        print("\n=== Generating Visualizations ===")
        
        # File size scaling plot
        if "file_size_scaling" in self.benchmark_results["benchmarks"]:
            data = self.benchmark_results["benchmarks"]["file_size_scaling"]
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
            
            # Processing time vs file size
            sizes = [d["file_size_mb"] for d in data if d["success"]]
            times = [d["processing_time"] for d in data if d["success"]]
            ax1.plot(sizes, times, 'b-o')
            ax1.set_xlabel("File Size (MB)")
            ax1.set_ylabel("Processing Time (s)")
            ax1.set_title("Processing Time vs File Size")
            ax1.grid(True)
            
            # Speed vs file size
            speeds = [d["speed_mb_per_sec"] for d in data if d["success"]]
            ax2.plot(sizes, speeds, 'g-o')
            ax2.set_xlabel("File Size (MB)")
            ax2.set_ylabel("Speed (MB/s)")
            ax2.set_title("Processing Speed vs File Size")
            ax2.grid(True)
            
            # Realtime factor
            durations = [d["duration_seconds"] for d in data if d["success"]]
            realtime_factors = [d["realtime_factor"] for d in data if d["success"]]
            ax3.bar(durations, realtime_factors)
            ax3.set_xlabel("Audio Duration (s)")
            ax3.set_ylabel("Realtime Factor")
            ax3.set_title("Realtime Processing Factor")
            ax3.axhline(y=1, color='r', linestyle='--', label='Realtime')
            ax3.legend()
            ax3.grid(True, axis='y')
            
            # Resource usage
            cpu_usage = [d["avg_cpu_percent"] for d in data if d["success"]]
            memory_usage = [d["avg_memory_percent"] for d in data if d["success"]]
            ax4.plot(durations, cpu_usage, 'r-o', label='CPU %')
            ax4.plot(durations, memory_usage, 'b-o', label='Memory %')
            ax4.set_xlabel("Audio Duration (s)")
            ax4.set_ylabel("Resource Usage (%)")
            ax4.set_title("Resource Usage vs Audio Duration")
            ax4.legend()
            ax4.grid(True)
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "file_size_scaling.png", dpi=300)
            plt.close()
        
        # Format comparison
        if "format_performance" in self.benchmark_results["benchmarks"]:
            data = self.benchmark_results["benchmarks"]["format_performance"]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            formats = [d["format"] for d in data]
            speeds = [d["speed_mb_per_sec"] for d in data]
            times = [d["avg_processing_time"] for d in data]
            
            ax1.bar(formats, speeds)
            ax1.set_xlabel("Audio Format")
            ax1.set_ylabel("Speed (MB/s)")
            ax1.set_title("Processing Speed by Format")
            ax1.grid(True, axis='y')
            
            ax2.bar(formats, times)
            ax2.set_xlabel("Audio Format")
            ax2.set_ylabel("Processing Time (s)")
            ax2.set_title("Processing Time by Format (30s audio)")
            ax2.grid(True, axis='y')
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "format_comparison.png", dpi=300)
            plt.close()
        
        print("Visualizations saved to benchmark_results/")
    
    def save_results(self):
        """Save benchmark results to file."""
        results_file = self.results_dir / "benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.benchmark_results, f, indent=2)
        
        # Generate summary report
        self._generate_summary_report()
    
    def _generate_summary_report(self):
        """Generate a markdown summary report."""
        report_file = self.results_dir / "benchmark_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Audio Converter Performance Benchmark Report\n\n")
            f.write(f"**Date:** {self.benchmark_results['timestamp']}\n\n")
            
            # System info
            f.write("## System Information\n\n")
            info = self.benchmark_results['system_info']
            f.write(f"- Platform: {info['platform']}\n")
            f.write(f"- CPU Cores: {info['cpu_count']}\n")
            f.write(f"- Total Memory: {info['total_memory_gb']:.1f} GB\n")
            f.write(f"- Python Version: {info['python_version'].split()[0]}\n\n")
            
            # File size scaling
            if "file_size_scaling" in self.benchmark_results["benchmarks"]:
                f.write("## File Size Scaling\n\n")
                f.write("| Duration | File Size | Processing Time | Speed | Realtime Factor |\n")
                f.write("|----------|-----------|-----------------|-------|------------------|\n")
                
                for data in self.benchmark_results["benchmarks"]["file_size_scaling"]:
                    if data["success"]:
                        f.write(f"| {data['duration_seconds']}s | "
                               f"{data['file_size_mb']:.1f} MB | "
                               f"{data['processing_time']:.2f}s | "
                               f"{data['speed_mb_per_sec']:.2f} MB/s | "
                               f"{data['realtime_factor']:.2f}x |\n")
                f.write("\n")
            
            # Format performance
            if "format_performance" in self.benchmark_results["benchmarks"]:
                f.write("## Format Performance\n\n")
                f.write("| Format | File Size | Avg Time | Speed |\n")
                f.write("|--------|-----------|----------|--------|\n")
                
                for data in self.benchmark_results["benchmarks"]["format_performance"]:
                    f.write(f"| {data['format'].upper()} | "
                           f"{data['file_size_mb']:.1f} MB | "
                           f"{data['avg_processing_time']:.2f}s | "
                           f"{data['speed_mb_per_sec']:.2f} MB/s |\n")
                f.write("\n")
            
            # Concurrent load
            if "concurrent_load" in self.benchmark_results["benchmarks"]:
                f.write("## Concurrent Processing\n\n")
                f.write("| Concurrent Files | Total Time | Avg/File | Throughput |\n")
                f.write("|------------------|------------|----------|-------------|\n")
                
                for data in self.benchmark_results["benchmarks"]["concurrent_load"]:
                    f.write(f"| {data['concurrent_count']} | "
                           f"{data['total_time']:.2f}s | "
                           f"{data['avg_time_per_file']:.2f}s | "
                           f"{data['throughput_mb_per_sec']:.2f} MB/s |\n")
        
        print(f"Benchmark report saved to: {report_file}")


def main():
    """Run performance benchmarks."""
    benchmark = AudioPerformanceBenchmark()
    
    print("Audio Converter Performance Benchmark")
    print("=" * 50)
    
    # Run benchmarks
    benchmark.benchmark_file_size_scaling()
    benchmark.benchmark_format_performance()
    benchmark.benchmark_sample_rate_impact()
    benchmark.benchmark_concurrent_load()
    
    # Generate visualizations
    try:
        benchmark.generate_visualizations()
    except ImportError:
        print("\nMatplotlib not available - skipping visualizations")
    
    # Save results
    benchmark.save_results()
    
    print("\n" + "=" * 50)
    print("Benchmark complete!")
    print(f"Results saved to: {benchmark.results_dir}")


if __name__ == "__main__":
    main()