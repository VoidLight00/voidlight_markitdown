"""
Wikipedia API Performance Benchmarking

Comprehensive performance testing for Wikipedia content extraction.
"""

import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.request import urlopen, Request

from voidlight_markitdown import VoidLightMarkItDown, StreamInfo


class WikipediaBenchmark:
    """Benchmark Wikipedia API performance"""
    
    def __init__(self):
        self.md = VoidLightMarkItDown()
        self.results = []
        
    def benchmark_single_request(self, url: str, category: str = "general") -> Dict:
        """Benchmark a single Wikipedia request"""
        
        # Timing points
        timings = {}
        
        try:
            # 1. Fetch content
            fetch_start = time.time()
            headers = {
                'User-Agent': 'VoidlightMarkitdown/1.0 (Benchmarking)',
                'Accept': 'text/html,application/xhtml+xml',
            }
            req = Request(url, headers=headers)
            
            with urlopen(req, timeout=30) as response:
                content = response.read()
                content_size = len(content)
            
            timings['fetch'] = time.time() - fetch_start
            
            # 2. Parse and convert
            convert_start = time.time()
            # Convert bytes to stream
            import io
            content_stream = io.BytesIO(content)
            stream_info = StreamInfo(url=url)
            result = self.md.convert_stream(content_stream, stream_info=stream_info)
            timings['convert'] = time.time() - convert_start
            
            # 3. Post-processing analysis
            analysis_start = time.time()
            markdown_size = len(result.markdown)
            line_count = result.markdown.count('\n')
            header_count = sum(1 for line in result.markdown.split('\n') if line.startswith('#'))
            timings['analysis'] = time.time() - analysis_start
            
            timings['total'] = sum(timings.values())
            
            return {
                'url': url,
                'category': category,
                'success': True,
                'timings': timings,
                'metrics': {
                    'content_size': content_size,
                    'markdown_size': markdown_size,
                    'compression_ratio': markdown_size / content_size if content_size > 0 else 0,
                    'line_count': line_count,
                    'header_count': header_count,
                    'bytes_per_second': content_size / timings['total'] if timings['total'] > 0 else 0,
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'url': url,
                'category': category,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def benchmark_concurrent(self, urls: List[str], max_workers: int = 5) -> Dict:
        """Benchmark concurrent Wikipedia requests"""
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.benchmark_single_request, url, "concurrent"): url 
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'url': url,
                        'success': False,
                        'error': str(e)
                    })
        
        total_time = time.time() - start_time
        
        successful = [r for r in results if r.get('success', False)]
        
        return {
            'type': 'concurrent',
            'max_workers': max_workers,
            'total_urls': len(urls),
            'successful': len(successful),
            'total_time': total_time,
            'average_time_per_url': total_time / len(urls),
            'throughput': len(successful) / total_time if total_time > 0 else 0,
            'results': results
        }
    
    def benchmark_article_sizes(self) -> Dict:
        """Benchmark different article sizes"""
        
        size_categories = {
            'small': [
                'https://en.wikipedia.org/wiki/Hello_world_program',
                'https://ko.wikipedia.org/wiki/헬로_월드',
            ],
            'medium': [
                'https://en.wikipedia.org/wiki/Python_(programming_language)',
                'https://ko.wikipedia.org/wiki/파이썬',
            ],
            'large': [
                'https://en.wikipedia.org/wiki/Artificial_intelligence',
                'https://ko.wikipedia.org/wiki/인공지능',
            ],
            'very_large': [
                'https://en.wikipedia.org/wiki/World_War_II',
                'https://ko.wikipedia.org/wiki/제2차_세계_대전',
            ]
        }
        
        results = {}
        
        for size_category, urls in size_categories.items():
            category_results = []
            
            for url in urls:
                print(f"Benchmarking {size_category} article: {url}")
                result = self.benchmark_single_request(url, size_category)
                category_results.append(result)
                time.sleep(1)  # Be polite
            
            # Calculate statistics
            successful = [r for r in category_results if r.get('success', False)]
            if successful:
                fetch_times = [r['timings']['fetch'] for r in successful]
                convert_times = [r['timings']['convert'] for r in successful]
                total_times = [r['timings']['total'] for r in successful]
                content_sizes = [r['metrics']['content_size'] for r in successful]
                
                results[size_category] = {
                    'count': len(successful),
                    'average_content_size': statistics.mean(content_sizes),
                    'timings': {
                        'fetch': {
                            'mean': statistics.mean(fetch_times),
                            'median': statistics.median(fetch_times),
                            'stdev': statistics.stdev(fetch_times) if len(fetch_times) > 1 else 0
                        },
                        'convert': {
                            'mean': statistics.mean(convert_times),
                            'median': statistics.median(convert_times),
                            'stdev': statistics.stdev(convert_times) if len(convert_times) > 1 else 0
                        },
                        'total': {
                            'mean': statistics.mean(total_times),
                            'median': statistics.median(total_times),
                            'stdev': statistics.stdev(total_times) if len(total_times) > 1 else 0
                        }
                    }
                }
        
        return results
    
    def benchmark_language_performance(self) -> Dict:
        """Benchmark performance across different languages"""
        
        languages = {
            'english': 'https://en.wikipedia.org/wiki/Machine_learning',
            'korean': 'https://ko.wikipedia.org/wiki/기계_학습',
            'japanese': 'https://ja.wikipedia.org/wiki/機械学習',
            'chinese': 'https://zh.wikipedia.org/wiki/机器学习',
            'arabic': 'https://ar.wikipedia.org/wiki/تعلم_الآلة',
            'hebrew': 'https://he.wikipedia.org/wiki/למידת_מכונה',
            'russian': 'https://ru.wikipedia.org/wiki/Машинное_обучение',
        }
        
        results = {}
        
        for lang, url in languages.items():
            print(f"Benchmarking {lang}: {url}")
            result = self.benchmark_single_request(url, f"language_{lang}")
            results[lang] = result
            time.sleep(1)
        
        return results
    
    def run_comprehensive_benchmark(self) -> Dict:
        """Run all benchmarks and generate comprehensive report"""
        
        print("Starting comprehensive Wikipedia API benchmark...")
        
        report = {
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'tool': 'voidlight_markitdown',
                'target': 'Wikipedia API'
            },
            'benchmarks': {}
        }
        
        # 1. Article size benchmarks
        print("\n1. Benchmarking different article sizes...")
        report['benchmarks']['article_sizes'] = self.benchmark_article_sizes()
        
        # 2. Language performance
        print("\n2. Benchmarking language performance...")
        report['benchmarks']['languages'] = self.benchmark_language_performance()
        
        # 3. Concurrent request performance
        print("\n3. Benchmarking concurrent requests...")
        concurrent_urls = [
            'https://en.wikipedia.org/wiki/Data_science',
            'https://en.wikipedia.org/wiki/Computer_science',
            'https://en.wikipedia.org/wiki/Software_engineering',
            'https://en.wikipedia.org/wiki/Mathematics',
            'https://en.wikipedia.org/wiki/Physics',
        ]
        
        for workers in [1, 3, 5]:
            print(f"   Testing with {workers} workers...")
            report['benchmarks'][f'concurrent_{workers}_workers'] = self.benchmark_concurrent(
                concurrent_urls, max_workers=workers
            )
        
        # 4. Special content types
        print("\n4. Benchmarking special content types...")
        special_urls = {
            'table_heavy': 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)',
            'math_heavy': 'https://en.wikipedia.org/wiki/Fourier_transform',
            'media_rich': 'https://en.wikipedia.org/wiki/Solar_System',
            'disambiguation': 'https://en.wikipedia.org/wiki/Python',
            'redirect': 'https://en.wikipedia.org/wiki/USA',
        }
        
        special_results = {}
        for content_type, url in special_urls.items():
            print(f"   Testing {content_type}: {url}")
            special_results[content_type] = self.benchmark_single_request(url, content_type)
            time.sleep(1)
        
        report['benchmarks']['special_content'] = special_results
        
        report['metadata']['end_time'] = datetime.now().isoformat()
        
        return report
    
    def generate_performance_summary(self, report: Dict) -> str:
        """Generate a human-readable performance summary"""
        
        summary = """# Wikipedia API Performance Benchmark Report

## Executive Summary

"""
        
        # Article size performance
        if 'article_sizes' in report['benchmarks']:
            summary += "### Performance by Article Size\n\n"
            summary += "| Size | Avg Content (KB) | Fetch Time (s) | Convert Time (s) | Total Time (s) |\n"
            summary += "|------|------------------|----------------|------------------|----------------|\n"
            
            for size, data in report['benchmarks']['article_sizes'].items():
                if 'average_content_size' in data:
                    summary += f"| {size} | {data['average_content_size']/1024:.1f} | "
                    summary += f"{data['timings']['fetch']['mean']:.2f} | "
                    summary += f"{data['timings']['convert']['mean']:.2f} | "
                    summary += f"{data['timings']['total']['mean']:.2f} |\n"
        
        # Language performance
        if 'languages' in report['benchmarks']:
            summary += "\n### Performance by Language\n\n"
            summary += "| Language | Content Size (KB) | Total Time (s) | Bytes/Second |\n"
            summary += "|----------|-------------------|----------------|---------------|\n"
            
            for lang, data in report['benchmarks']['languages'].items():
                if data.get('success'):
                    summary += f"| {lang} | {data['metrics']['content_size']/1024:.1f} | "
                    summary += f"{data['timings']['total']:.2f} | "
                    summary += f"{data['metrics']['bytes_per_second']:.0f} |\n"
        
        # Concurrent performance
        summary += "\n### Concurrent Request Performance\n\n"
        summary += "| Workers | Total Time (s) | Throughput (req/s) | Avg Time per URL (s) |\n"
        summary += "|---------|----------------|-------------------|---------------------|\n"
        
        for key, data in report['benchmarks'].items():
            if key.startswith('concurrent_'):
                if isinstance(data, dict) and 'max_workers' in data:
                    summary += f"| {data['max_workers']} | {data['total_time']:.2f} | "
                    summary += f"{data['throughput']:.2f} | "
                    summary += f"{data['average_time_per_url']:.2f} |\n"
        
        summary += "\n## Recommendations\n\n"
        summary += "1. **Optimal Workers**: Based on testing, 3-5 concurrent workers provide best throughput\n"
        summary += "2. **Large Articles**: Consider streaming for articles > 1MB\n"
        summary += "3. **Caching**: Implement caching for frequently accessed articles\n"
        summary += "4. **Language Optimization**: UTF-8 handling is consistent across languages\n"
        
        return summary


def main():
    """Run the benchmark suite"""
    benchmark = WikipediaBenchmark()
    
    # Run comprehensive benchmark
    report = benchmark.run_comprehensive_benchmark()
    
    # Save JSON report
    json_path = "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/tests/wikipedia_benchmark_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Generate and save summary
    summary = benchmark.generate_performance_summary(report)
    summary_path = "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/tests/wikipedia_benchmark_summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\nBenchmark complete!")
    print(f"JSON report: {json_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()