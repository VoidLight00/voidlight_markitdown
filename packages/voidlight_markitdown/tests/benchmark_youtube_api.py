#!/usr/bin/env python3
"""
YouTube API Performance Benchmarking Suite
Measures performance characteristics of YouTube video conversion
"""
import os
import sys
import time
import json
import psutil
import tracemalloc
from datetime import datetime
from typing import Dict, List, Tuple
from statistics import mean, median, stdev

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidlight_markitdown import VoidLightMarkItDown


class YouTubeAPIBenchmark:
    """Benchmark YouTube API performance"""
    
    def __init__(self):
        self.markitdown = VoidLightMarkItDown()
        self.results = []
        
    def measure_conversion(self, video_url: str, video_name: str) -> Dict:
        """Measure performance metrics for a single conversion"""
        
        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Measure conversion time
        start_time = time.time()
        try:
            result = self.markitdown.convert(video_url)
            success = True
            error = None
            content_length = len(result.text_content)
            has_transcript = "### Transcript" in result.text_content
        except Exception as e:
            success = False
            error = str(e)
            content_length = 0
            has_transcript = False
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "video_name": video_name,
            "video_url": video_url,
            "success": success,
            "error": error,
            "duration_seconds": round(duration, 2),
            "content_length": content_length,
            "has_transcript": has_transcript,
            "memory_used_mb": round((peak / 1024 / 1024), 2),
            "memory_delta_mb": round((final_memory - initial_memory), 2),
            "timestamp": datetime.now().isoformat(),
        }
    
    def run_benchmark_suite(self) -> List[Dict]:
        """Run complete benchmark suite"""
        
        test_videos = [
            # Short videos
            ("Short English Tutorial", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            ("Short Music Video", "https://www.youtube.com/watch?v=IHNzOHi8sJs"),
            
            # Medium videos
            ("Medium Tech Talk", "https://www.youtube.com/watch?v=V2qZ_lgxTzg"),
            
            # Long videos (be careful with API quotas)
            ("Long Podcast", "https://www.youtube.com/watch?v=EngW7tLk6R8"),
            
            # Edge cases
            ("No Captions", "https://www.youtube.com/watch?v=aqz-KE-bpKQ"),
            ("Live Recording", "https://www.youtube.com/watch?v=21X5lGlDOfg"),
            
            # Error cases
            ("Invalid Video", "https://www.youtube.com/watch?v=INVALID_ID"),
            ("Malformed URL", "https://youtube.com/watch?v="),
        ]
        
        print("Starting YouTube API Benchmark Suite")
        print("=" * 60)
        
        for video_name, video_url in test_videos:
            print(f"\nTesting: {video_name}")
            print(f"URL: {video_url}")
            
            result = self.measure_conversion(video_url, video_name)
            self.results.append(result)
            
            # Print immediate results
            if result["success"]:
                print(f"✓ Success in {result['duration_seconds']}s")
                print(f"  Content: {result['content_length']} chars")
                print(f"  Memory: {result['memory_used_mb']} MB")
                print(f"  Transcript: {'Yes' if result['has_transcript'] else 'No'}")
            else:
                print(f"✗ Failed: {result['error']}")
            
            # Rate limiting - wait between requests
            time.sleep(2)
        
        return self.results
    
    def analyze_results(self) -> Dict:
        """Analyze benchmark results"""
        successful_results = [r for r in self.results if r["success"]]
        
        if not successful_results:
            return {"error": "No successful conversions"}
        
        durations = [r["duration_seconds"] for r in successful_results]
        memory_usage = [r["memory_used_mb"] for r in successful_results]
        content_lengths = [r["content_length"] for r in successful_results]
        
        analysis = {
            "total_tests": len(self.results),
            "successful_tests": len(successful_results),
            "failure_rate": (len(self.results) - len(successful_results)) / len(self.results),
            "duration_stats": {
                "min": min(durations),
                "max": max(durations),
                "mean": round(mean(durations), 2),
                "median": round(median(durations), 2),
                "stdev": round(stdev(durations), 2) if len(durations) > 1 else 0,
            },
            "memory_stats": {
                "min": min(memory_usage),
                "max": max(memory_usage),
                "mean": round(mean(memory_usage), 2),
                "median": round(median(memory_usage), 2),
            },
            "content_stats": {
                "min": min(content_lengths),
                "max": max(content_lengths),
                "mean": round(mean(content_lengths), 2),
            },
            "transcript_availability": sum(1 for r in successful_results if r["has_transcript"]) / len(successful_results),
        }
        
        return analysis
    
    def save_results(self, filename: str = "youtube_benchmark_results.json"):
        """Save benchmark results to file"""
        output = {
            "benchmark_date": datetime.now().isoformat(),
            "results": self.results,
            "analysis": self.analyze_results(),
        }
        
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to {filename}")
    
    def print_summary(self):
        """Print summary of benchmark results"""
        analysis = self.analyze_results()
        
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        
        print(f"\nTests Run: {analysis['total_tests']}")
        print(f"Successful: {analysis['successful_tests']}")
        print(f"Failure Rate: {analysis['failure_rate']:.1%}")
        
        print(f"\nDuration Statistics (seconds):")
        for stat, value in analysis['duration_stats'].items():
            print(f"  {stat.capitalize()}: {value}")
        
        print(f"\nMemory Usage Statistics (MB):")
        for stat, value in analysis['memory_stats'].items():
            print(f"  {stat.capitalize()}: {value}")
        
        print(f"\nContent Length Statistics (characters):")
        for stat, value in analysis['content_stats'].items():
            print(f"  {stat.capitalize()}: {value}")
        
        print(f"\nTranscript Availability: {analysis['transcript_availability']:.1%}")
        
        # Performance recommendations
        print("\n" + "=" * 60)
        print("PERFORMANCE RECOMMENDATIONS")
        print("=" * 60)
        
        avg_duration = analysis['duration_stats']['mean']
        if avg_duration > 10:
            print("⚠️  Average conversion time is high (>10s)")
            print("   Consider implementing caching for frequently accessed videos")
        
        max_memory = analysis['memory_stats']['max']
        if max_memory > 100:
            print("⚠️  High memory usage detected (>100MB)")
            print("   Consider streaming transcript processing for long videos")
        
        if analysis['failure_rate'] > 0.2:
            print("⚠️  High failure rate (>20%)")
            print("   Review error handling and retry mechanisms")
        
        if analysis['transcript_availability'] < 0.8:
            print("ℹ️  Low transcript availability (<80%)")
            print("   Consider fallback mechanisms for videos without captions")


def run_concurrent_benchmark():
    """Test concurrent request handling"""
    import concurrent.futures
    
    print("\n" + "=" * 60)
    print("CONCURRENT REQUEST BENCHMARK")
    print("=" * 60)
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=IHNzOHi8sJs",
        "https://www.youtube.com/watch?v=V2qZ_lgxTzg",
    ]
    
    markitdown = VoidLightMarkItDown()
    
    def convert_video(url):
        start = time.time()
        try:
            result = markitdown.convert(url)
            return {
                "url": url,
                "duration": time.time() - start,
                "success": True,
                "content_length": len(result.text_content)
            }
        except Exception as e:
            return {
                "url": url,
                "duration": time.time() - start,
                "success": False,
                "error": str(e)
            }
    
    # Test different levels of concurrency
    for max_workers in [1, 2, 3]:
        print(f"\nTesting with {max_workers} concurrent workers:")
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(convert_video, url) for url in test_urls]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_duration = time.time() - start_time
        
        successful = sum(1 for r in results if r["success"])
        avg_duration = mean([r["duration"] for r in results])
        
        print(f"  Total time: {total_duration:.2f}s")
        print(f"  Average per request: {avg_duration:.2f}s")
        print(f"  Successful: {successful}/{len(test_urls)}")
        print(f"  Speedup: {(avg_duration * len(test_urls)) / total_duration:.2f}x")


if __name__ == "__main__":
    # Check for environment variable to skip
    if os.environ.get("SKIP_YOUTUBE_TESTS"):
        print("YouTube tests skipped (SKIP_YOUTUBE_TESTS is set)")
        sys.exit(0)
    
    # Run main benchmark
    benchmark = YouTubeAPIBenchmark()
    benchmark.run_benchmark_suite()
    benchmark.print_summary()
    benchmark.save_results()
    
    # Run concurrent benchmark
    run_concurrent_benchmark()
    
    print("\nBenchmark complete!")