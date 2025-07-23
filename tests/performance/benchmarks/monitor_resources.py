#!/usr/bin/env python3
"""
Real-time resource monitoring for performance testing.

This script monitors system resources (CPU, memory, disk I/O) during
file processing operations and generates detailed reports.
"""

import os
import sys
import time
import json
import psutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import numpy as np


class ResourceMonitor:
    """Monitor and visualize system resources in real-time."""
    
    def __init__(self, sample_interval: float = 0.1, history_size: int = 1000):
        self.sample_interval = sample_interval
        self.history_size = history_size
        
        # Process to monitor (current process by default)
        self.process = psutil.Process()
        
        # Data storage
        self.timestamps = deque(maxlen=history_size)
        self.cpu_percent = deque(maxlen=history_size)
        self.memory_rss = deque(maxlen=history_size)
        self.memory_vms = deque(maxlen=history_size)
        self.disk_read_bytes = deque(maxlen=history_size)
        self.disk_write_bytes = deque(maxlen=history_size)
        self.thread_count = deque(maxlen=history_size)
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Disk I/O tracking
        self.last_disk_io = None
        
        # Event markers
        self.events = []  # List of (timestamp, event_name) tuples
    
    def start(self):
        """Start monitoring resources."""
        self.monitoring = True
        self.last_disk_io = self.process.io_counters()
        
        def monitor_loop():
            while self.monitoring:
                try:
                    # Timestamp
                    timestamp = datetime.now()
                    self.timestamps.append(timestamp)
                    
                    # CPU usage
                    cpu = self.process.cpu_percent(interval=None)
                    self.cpu_percent.append(cpu)
                    
                    # Memory usage
                    mem_info = self.process.memory_info()
                    self.memory_rss.append(mem_info.rss / (1024 * 1024))  # MB
                    self.memory_vms.append(mem_info.vms / (1024 * 1024))  # MB
                    
                    # Disk I/O
                    io_counters = self.process.io_counters()
                    if self.last_disk_io:
                        read_rate = (io_counters.read_bytes - self.last_disk_io.read_bytes) / self.sample_interval
                        write_rate = (io_counters.write_bytes - self.last_disk_io.write_bytes) / self.sample_interval
                        self.disk_read_bytes.append(read_rate / (1024 * 1024))  # MB/s
                        self.disk_write_bytes.append(write_rate / (1024 * 1024))  # MB/s
                    else:
                        self.disk_read_bytes.append(0)
                        self.disk_write_bytes.append(0)
                    self.last_disk_io = io_counters
                    
                    # Thread count
                    self.thread_count.append(self.process.num_threads())
                    
                    time.sleep(self.sample_interval)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(self.sample_interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Resource monitoring started...")
    
    def stop(self):
        """Stop monitoring resources."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("Resource monitoring stopped.")
    
    def mark_event(self, event_name: str):
        """Mark an event in the timeline."""
        self.events.append((datetime.now(), event_name))
        print(f"Event marked: {event_name}")
    
    def get_statistics(self) -> Dict:
        """Get current statistics."""
        if not self.cpu_percent:
            return {}
        
        return {
            'samples': len(self.cpu_percent),
            'duration_seconds': (self.timestamps[-1] - self.timestamps[0]).total_seconds() if len(self.timestamps) > 1 else 0,
            'cpu': {
                'current': self.cpu_percent[-1],
                'average': np.mean(list(self.cpu_percent)),
                'peak': max(self.cpu_percent),
                'std': np.std(list(self.cpu_percent)),
            },
            'memory_rss_mb': {
                'current': self.memory_rss[-1],
                'average': np.mean(list(self.memory_rss)),
                'peak': max(self.memory_rss),
                'min': min(self.memory_rss),
            },
            'disk_read_mbps': {
                'current': self.disk_read_bytes[-1] if self.disk_read_bytes else 0,
                'average': np.mean(list(self.disk_read_bytes)) if self.disk_read_bytes else 0,
                'peak': max(self.disk_read_bytes) if self.disk_read_bytes else 0,
            },
            'disk_write_mbps': {
                'current': self.disk_write_bytes[-1] if self.disk_write_bytes else 0,
                'average': np.mean(list(self.disk_write_bytes)) if self.disk_write_bytes else 0,
                'peak': max(self.disk_write_bytes) if self.disk_write_bytes else 0,
            },
            'threads': {
                'current': self.thread_count[-1] if self.thread_count else 0,
                'average': np.mean(list(self.thread_count)) if self.thread_count else 0,
                'peak': max(self.thread_count) if self.thread_count else 0,
            },
        }
    
    def save_data(self, filepath: str):
        """Save monitoring data to file."""
        data = {
            'metadata': {
                'start_time': self.timestamps[0].isoformat() if self.timestamps else None,
                'end_time': self.timestamps[-1].isoformat() if self.timestamps else None,
                'duration_seconds': (self.timestamps[-1] - self.timestamps[0]).total_seconds() if len(self.timestamps) > 1 else 0,
                'sample_interval': self.sample_interval,
                'samples': len(self.timestamps),
            },
            'statistics': self.get_statistics(),
            'events': [(ts.isoformat(), event) for ts, event in self.events],
            'raw_data': {
                'timestamps': [ts.isoformat() for ts in self.timestamps],
                'cpu_percent': list(self.cpu_percent),
                'memory_rss_mb': list(self.memory_rss),
                'memory_vms_mb': list(self.memory_vms),
                'disk_read_mbps': list(self.disk_read_bytes),
                'disk_write_mbps': list(self.disk_write_bytes),
                'thread_count': list(self.thread_count),
            },
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Monitoring data saved to: {filepath}")
    
    def plot_resources(self, output_path: Optional[str] = None):
        """Generate resource usage plots."""
        if not self.timestamps:
            print("No data to plot")
            return
        
        # Convert timestamps to matplotlib format
        timestamps = list(self.timestamps)
        
        # Create figure with subplots
        fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        fig.suptitle('Resource Usage During File Processing', fontsize=16)
        
        # CPU Usage
        ax = axes[0]
        ax.plot(timestamps, list(self.cpu_percent), 'b-', linewidth=1)
        ax.set_ylabel('CPU Usage (%)')
        ax.set_ylim(0, max(max(self.cpu_percent) * 1.1, 100))
        ax.grid(True, alpha=0.3)
        
        # Memory Usage
        ax = axes[1]
        ax.plot(timestamps, list(self.memory_rss), 'g-', linewidth=1, label='RSS')
        ax.plot(timestamps, list(self.memory_vms), 'g--', linewidth=1, alpha=0.5, label='VMS')
        ax.set_ylabel('Memory (MB)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Disk I/O
        ax = axes[2]
        ax.plot(timestamps, list(self.disk_read_bytes), 'r-', linewidth=1, label='Read')
        ax.plot(timestamps, list(self.disk_write_bytes), 'orange', linewidth=1, label='Write')
        ax.set_ylabel('Disk I/O (MB/s)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Thread Count
        ax = axes[3]
        ax.plot(timestamps, list(self.thread_count), 'm-', linewidth=1)
        ax.set_ylabel('Thread Count')
        ax.set_xlabel('Time')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            
            # Add event markers
            for event_time, event_name in self.events:
                if timestamps[0] <= event_time <= timestamps[-1]:
                    ax.axvline(x=event_time, color='red', linestyle='--', alpha=0.5)
        
        # Add event labels to the last subplot
        for event_time, event_name in self.events:
            if timestamps[0] <= event_time <= timestamps[-1]:
                axes[-1].text(event_time, axes[-1].get_ylim()[1] * 0.9, event_name,
                            rotation=90, verticalalignment='bottom', fontsize=8)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300)
            print(f"Plot saved to: {output_path}")
        else:
            plt.show()
    
    def live_plot(self, update_interval: int = 1000):
        """Show live updating plot of resources."""
        # This would require a GUI environment
        print("Live plotting requires GUI environment")
        # Implementation would use matplotlib animation


class FileProcessingMonitor:
    """Monitor resources during file processing operations."""
    
    def __init__(self):
        self.monitor = ResourceMonitor()
        self.results = []
    
    def monitor_file_processing(self, process_func, file_path: str, *args, **kwargs):
        """Monitor resources while processing a file."""
        print(f"\nMonitoring resources for: {file_path}")
        
        # Start monitoring
        self.monitor.start()
        self.monitor.mark_event("Start")
        
        start_time = time.time()
        result = None
        error = None
        
        try:
            # Execute the processing function
            result = process_func(file_path, *args, **kwargs)
            self.monitor.mark_event("Complete")
        except Exception as e:
            error = str(e)
            self.monitor.mark_event(f"Error: {error[:50]}")
        
        end_time = time.time()
        
        # Stop monitoring
        time.sleep(0.5)  # Allow final samples
        self.monitor.stop()
        
        # Get statistics
        stats = self.monitor.get_statistics()
        
        # Store results
        processing_result = {
            'file_path': file_path,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'success': error is None,
            'error': error,
            'resource_stats': stats,
        }
        
        self.results.append(processing_result)
        
        # Generate report
        self._print_summary(processing_result)
        
        return result, processing_result
    
    def _print_summary(self, result: Dict):
        """Print processing summary."""
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        print(f"File: {os.path.basename(result['file_path'])}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Success: {'✅' if result['success'] else '❌'}")
        
        if result['error']:
            print(f"Error: {result['error']}")
        
        if result['resource_stats']:
            stats = result['resource_stats']
            print("\nResource Usage:")
            print(f"  CPU: {stats['cpu']['average']:.1f}% avg, {stats['cpu']['peak']:.1f}% peak")
            print(f"  Memory: {stats['memory_rss_mb']['average']:.1f}MB avg, {stats['memory_rss_mb']['peak']:.1f}MB peak")
            print(f"  Disk Read: {stats['disk_read_mbps']['average']:.2f}MB/s avg, {stats['disk_read_mbps']['peak']:.2f}MB/s peak")
            print(f"  Disk Write: {stats['disk_write_mbps']['average']:.2f}MB/s avg, {stats['disk_write_mbps']['peak']:.2f}MB/s peak")
            print(f"  Threads: {stats['threads']['average']:.1f} avg, {stats['threads']['peak']} peak")
    
    def save_results(self, output_dir: str):
        """Save monitoring results."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed monitoring data
        data_path = output_dir / f"monitoring_data_{timestamp}.json"
        self.monitor.save_data(str(data_path))
        
        # Save processing results
        results_path = output_dir / f"processing_results_{timestamp}.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate plot
        plot_path = output_dir / f"resource_usage_{timestamp}.png"
        self.monitor.plot_resources(str(plot_path))
        
        print(f"\nResults saved to: {output_dir}")


def monitor_voidlight_conversion(file_path: str, output_dir: str = None):
    """Monitor voidlight_markitdown conversion of a file."""
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from voidlight_markitdown import VoidLightMarkItDown
    
    # Create monitor
    monitor = FileProcessingMonitor()
    
    # Define processing function
    def process_file(filepath):
        converter = VoidLightMarkItDown(korean_mode=True)
        return converter.convert_local(filepath)
    
    # Monitor the conversion
    result, stats = monitor.monitor_file_processing(process_file, file_path)
    
    # Save results
    if output_dir:
        monitor.save_results(output_dir)
    
    return result, stats


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor resource usage during file processing')
    parser.add_argument('file', help='File to process and monitor')
    parser.add_argument('--output-dir', default='./monitoring_results', help='Output directory for results')
    parser.add_argument('--interval', type=float, default=0.1, help='Sampling interval in seconds')
    
    args = parser.parse_args()
    
    # Monitor conversion
    result, stats = monitor_voidlight_conversion(args.file, args.output_dir)
    
    print("\n✅ Monitoring complete!")


if __name__ == "__main__":
    main()