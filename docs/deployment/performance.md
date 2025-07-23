# Performance Tuning Guide

This guide covers performance optimization strategies for VoidLight MarkItDown in production environments.

## Table of Contents

1. [Performance Overview](#performance-overview)
2. [Configuration Optimization](#configuration-optimization)
3. [Memory Management](#memory-management)
4. [Concurrent Processing](#concurrent-processing)
5. [Korean Processing Optimization](#korean-processing-optimization)
6. [Caching Strategies](#caching-strategies)
7. [Monitoring & Profiling](#monitoring-profiling)
8. [Best Practices](#best-practices)

## Performance Overview

### Baseline Performance Metrics

| Document Type | Size | Default | Optimized | Korean Mode |
|--------------|------|---------|-----------|-------------|
| PDF | 1MB | 0.5s | 0.3s | 0.8s |
| PDF | 10MB | 3.2s | 2.1s | 4.5s |
| DOCX | 5MB | 1.8s | 1.2s | 2.3s |
| Image (OCR) | 2MB | 5.2s | 3.8s | 8.7s |
| Batch (100 files) | Mixed | 45s | 12s | 58s |

### Performance Goals

- **P50 Latency**: < 500ms for documents under 5MB
- **P99 Latency**: < 2s for documents under 10MB
- **Throughput**: 100+ documents/minute
- **Memory**: < 500MB per worker
- **CPU**: < 80% utilization

## Configuration Optimization

### Core Settings

```python
from voidlight_markitdown import Config, VoidLightMarkItDown

# Optimized configuration
config = Config(
    # Performance settings
    stream_mode=True,              # Enable streaming for large files
    chunk_size=1024 * 1024,       # 1MB chunks
    max_workers=8,                # Parallel processing threads
    
    # Memory settings
    max_file_size=100 * 1024 * 1024,  # 100MB limit
    temp_cleanup=True,            # Auto cleanup temp files
    cache_enabled=True,           # Enable result caching
    
    # Timeout settings
    timeout=300,                  # 5 minute timeout
    ocr_timeout=60,              # 1 minute OCR timeout
    
    # Feature toggles
    ocr_enabled=False,           # Disable if not needed
    extract_images=False,        # Skip image extraction
    preserve_formatting=False    # Simple markdown output
)

converter = VoidLightMarkItDown(config=config)
```

### Environment Variables

```bash
# Performance tuning
export VOIDLIGHT_MAX_WORKERS=8
export VOIDLIGHT_CHUNK_SIZE=2097152  # 2MB
export VOIDLIGHT_CACHE_SIZE=1000     # Cache 1000 results
export VOIDLIGHT_TEMP_DIR=/fast/ssd/temp

# Memory limits
export VOIDLIGHT_MAX_MEMORY=2048     # 2GB limit
export VOIDLIGHT_GC_THRESHOLD=100    # Force GC after 100 conversions
```

## Memory Management

### Stream Processing

For large files, use streaming to prevent memory overflow:

```python
def process_large_file(file_path: str):
    """Process large file with streaming."""
    converter = VoidLightMarkItDown(stream_mode=True)
    
    with converter.convert_stream(file_path) as stream:
        with open("output.md", "w") as output:
            for chunk in stream:
                output.write(chunk.content)
                # Process chunk without storing all in memory
```

### Memory-Efficient Batch Processing

```python
import gc
from pathlib import Path

def batch_convert_efficient(files: List[Path], output_dir: Path):
    """Memory-efficient batch conversion."""
    converter = VoidLightMarkItDown(
        config=Config(
            stream_mode=True,
            max_memory_per_file=50 * 1024 * 1024  # 50MB per file
        )
    )
    
    for i, file_path in enumerate(files):
        try:
            # Convert single file
            result = converter.convert(file_path)
            
            # Write immediately to free memory
            output_path = output_dir / f"{file_path.stem}.md"
            output_path.write_text(result.markdown)
            
            # Explicit cleanup every 10 files
            if i % 10 == 0:
                gc.collect()
                
        except Exception as e:
            logger.error(f"Failed to convert {file_path}: {e}")
            continue
```

### Memory Profiling

```python
from memory_profiler import profile
import tracemalloc

@profile
def convert_with_profiling(file_path):
    """Profile memory usage during conversion."""
    tracemalloc.start()
    
    converter = VoidLightMarkItDown()
    result = converter.convert(file_path)
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
    return result
```

## Concurrent Processing

### Parallel Batch Conversion

```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
import multiprocessing

def parallel_batch_convert(
    files: List[Path],
    output_dir: Path,
    max_workers: Optional[int] = None
):
    """Convert multiple files in parallel."""
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), 8)
    
    # Create converter with thread-safe config
    converter = VoidLightMarkItDown(
        config=Config(
            thread_safe=True,
            cache_enabled=False  # Disable cache for parallel
        )
    )
    
    # Process files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create conversion function
        convert_fn = partial(convert_single_file, converter, output_dir)
        
        # Submit all files
        futures = {
            executor.submit(convert_fn, file): file 
            for file in files
        }
        
        # Process results
        results = []
        for future in concurrent.futures.as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                results.append((file, result))
            except Exception as e:
                logger.error(f"Failed to convert {file}: {e}")
                
    return results

def convert_single_file(converter, output_dir, file_path):
    """Convert single file (thread-safe)."""
    result = converter.convert(file_path)
    output_path = output_dir / f"{file_path.stem}.md"
    output_path.write_text(result.markdown)
    return result
```

### Async Processing with asyncio

```python
import asyncio
from typing import List

async def async_batch_convert(files: List[Path]) -> List[ConversionResult]:
    """Asynchronous batch conversion."""
    converter = VoidLightMarkItDown()
    
    async def convert_async(file_path: Path):
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            converter.convert, 
            file_path
        )
    
    # Convert all files concurrently
    tasks = [convert_async(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful conversions
    successful = [r for r in results if not isinstance(r, Exception)]
    return successful

# Usage
results = asyncio.run(async_batch_convert(file_list))
```

## Korean Processing Optimization

### Optimized Korean Configuration

```python
# Fast Korean processing
korean_config = Config(
    korean_mode=True,
    korean_nlp_features={
        'tokenize': True,      # Fast tokenization
        'pos_tagging': False,  # Skip heavy POS tagging
        'ner': False,         # Skip NER for speed
    },
    korean_tokenizer='mecab',  # Fastest tokenizer
    korean_cache_enabled=True,  # Cache NLP results
)

# Accurate Korean processing
korean_config_accurate = Config(
    korean_mode=True,
    korean_nlp_features={
        'tokenize': True,
        'pos_tagging': True,
        'ner': True,
        'morpheme_analysis': True,
    },
    korean_tokenizer='kkma',  # Most accurate
)
```

### Korean Text Preprocessing Cache

```python
from functools import lru_cache
import hashlib

class KoreanTextCache:
    """Cache for Korean text preprocessing results."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
    
    def get_hash(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[str]:
        """Get cached result."""
        key = self.get_hash(text)
        return self.cache.get(key)
    
    def set(self, text: str, result: str):
        """Cache result."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))
        
        key = self.get_hash(text)
        self.cache[key] = result

# Use with converter
korean_cache = KoreanTextCache()

def process_korean_with_cache(text: str) -> str:
    """Process Korean text with caching."""
    cached = korean_cache.get(text)
    if cached:
        return cached
    
    # Process text
    result = process_korean_text(text)
    korean_cache.set(text, result)
    return result
```

## Caching Strategies

### Result Caching

```python
from diskcache import Cache
import hashlib

class ConversionCache:
    """Disk-based cache for conversion results."""
    
    def __init__(self, cache_dir: Path, size_limit: int = 1024**3):
        self.cache = Cache(cache_dir, size_limit=size_limit)
    
    def get_key(self, file_path: Path, config: Config) -> str:
        """Generate cache key from file and config."""
        file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        config_hash = hashlib.md5(str(config).encode()).hexdigest()
        return f"{file_hash}_{config_hash}"
    
    def get(self, file_path: Path, config: Config) -> Optional[ConversionResult]:
        """Get cached conversion result."""
        key = self.get_key(file_path, config)
        return self.cache.get(key)
    
    def set(self, file_path: Path, config: Config, result: ConversionResult):
        """Cache conversion result."""
        key = self.get_key(file_path, config)
        # Cache for 24 hours
        self.cache.set(key, result, expire=86400)

# Use with converter
cache = ConversionCache(Path("/var/cache/voidlight"))

def convert_with_cache(file_path: Path) -> ConversionResult:
    """Convert with caching."""
    config = Config()
    
    # Check cache
    cached = cache.get(file_path, config)
    if cached:
        return cached
    
    # Convert
    converter = VoidLightMarkItDown(config=config)
    result = converter.convert(file_path)
    
    # Cache result
    cache.set(file_path, config, result)
    return result
```

### Redis Caching for Distributed Systems

```python
import redis
import pickle
from typing import Optional

class RedisConversionCache:
    """Redis-based cache for distributed systems."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[ConversionResult]:
        """Get from Redis cache."""
        data = self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    def set(self, key: str, result: ConversionResult):
        """Set in Redis cache."""
        data = pickle.dumps(result)
        self.redis.setex(key, self.ttl, data)
    
    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern."""
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)
```

## Monitoring & Profiling

### Performance Metrics

```python
import time
from dataclasses import dataclass
from typing import Dict
import prometheus_client as prom

# Define metrics
conversion_duration = prom.Histogram(
    'voidlight_conversion_duration_seconds',
    'Time spent converting documents',
    ['format', 'korean_mode']
)

conversion_counter = prom.Counter(
    'voidlight_conversions_total',
    'Total number of conversions',
    ['format', 'status']
)

memory_usage = prom.Gauge(
    'voidlight_memory_usage_bytes',
    'Current memory usage'
)

@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    conversion_time: float
    memory_used: int
    file_size: int
    format: str
    korean_mode: bool

class MonitoredConverter:
    """Converter with performance monitoring."""
    
    def __init__(self, config: Config):
        self.converter = VoidLightMarkItDown(config)
        self.metrics = []
    
    def convert(self, source: Path) -> ConversionResult:
        """Convert with monitoring."""
        start_time = time.time()
        format = source.suffix
        
        # Monitor conversion
        with conversion_duration.labels(
            format=format, 
            korean_mode=self.converter.config.korean_mode
        ).time():
            try:
                result = self.converter.convert(source)
                conversion_counter.labels(
                    format=format, 
                    status='success'
                ).inc()
            except Exception as e:
                conversion_counter.labels(
                    format=format, 
                    status='error'
                ).inc()
                raise
        
        # Record metrics
        elapsed = time.time() - start_time
        self.metrics.append(PerformanceMetrics(
            conversion_time=elapsed,
            memory_used=get_memory_usage(),
            file_size=source.stat().st_size,
            format=format,
            korean_mode=self.converter.config.korean_mode
        ))
        
        return result
```

### Profiling Tools

```python
import cProfile
import pstats
from line_profiler import LineProfiler

def profile_conversion(file_path: Path):
    """Profile conversion performance."""
    profiler = cProfile.Profile()
    
    # Profile conversion
    profiler.enable()
    converter = VoidLightMarkItDown()
    result = converter.convert(file_path)
    profiler.disable()
    
    # Print statistics
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    return result

# Line-by-line profiling
def detailed_profile():
    lp = LineProfiler()
    lp.add_function(VoidLightMarkItDown.convert)
    lp.add_function(PDFConverter.convert)
    
    # Run with profiler
    lp.enable()
    converter = VoidLightMarkItDown()
    converter.convert("document.pdf")
    lp.disable()
    
    lp.print_stats()
```

## Best Practices

### 1. Resource Allocation

```yaml
# Docker resource limits
services:
  converter:
    image: voidlight/markitdown
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 2. Load Balancing

```python
from typing import List
import random

class LoadBalancedConverter:
    """Load balance across multiple converter instances."""
    
    def __init__(self, num_instances: int = 4):
        self.converters = [
            VoidLightMarkItDown(
                config=Config(instance_id=i)
            )
            for i in range(num_instances)
        ]
    
    def convert(self, source: Path) -> ConversionResult:
        """Convert using least loaded instance."""
        # Simple round-robin (can be enhanced)
        converter = random.choice(self.converters)
        return converter.convert(source)
```

### 3. Circuit Breaker Pattern

```python
from circuit_breaker import CircuitBreaker

class ResilientConverter:
    """Converter with circuit breaker for resilience."""
    
    def __init__(self):
        self.converter = VoidLightMarkItDown()
        self.breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=ConversionError
        )
    
    @property
    def convert(self):
        return self.breaker(self._convert)
    
    def _convert(self, source: Path) -> ConversionResult:
        """Actual conversion with circuit breaker."""
        return self.converter.convert(source)
```

### 4. Performance Checklist

- [ ] Enable streaming for files > 10MB
- [ ] Use appropriate chunk size (1-2MB)
- [ ] Configure worker pool based on CPU cores
- [ ] Enable caching for repeated conversions
- [ ] Disable unnecessary features (OCR, image extraction)
- [ ] Monitor memory usage and set limits
- [ ] Use connection pooling for external services
- [ ] Implement request timeouts
- [ ] Profile hotspots regularly
- [ ] Use CDN for static assets

## Optimization Examples

### High-Throughput Configuration

```python
# For maximum throughput
high_throughput_config = Config(
    # Maximum parallelism
    max_workers=16,
    thread_pool_size=32,
    
    # Fast processing
    stream_mode=True,
    chunk_size=2 * 1024 * 1024,  # 2MB
    
    # Skip expensive operations
    ocr_enabled=False,
    extract_images=False,
    preserve_formatting=False,
    
    # Aggressive caching
    cache_enabled=True,
    cache_size=10000,
    
    # Quick timeouts
    timeout=60,  # 1 minute max
)
```

### Low-Latency Configuration

```python
# For minimum latency
low_latency_config = Config(
    # Fewer workers, less contention
    max_workers=4,
    
    # Pre-loaded models
    preload_models=True,
    warm_start=True,
    
    # Fast operations only
    quick_mode=True,
    approximate_layout=True,
    
    # Memory over disk
    use_memory_cache=True,
    temp_in_memory=True,
)
```

### Memory-Constrained Configuration

```python
# For limited memory environments
memory_safe_config = Config(
    # Conservative settings
    max_workers=2,
    chunk_size=512 * 1024,  # 512KB
    
    # Streaming mandatory
    stream_mode=True,
    force_streaming=True,
    
    # Aggressive cleanup
    immediate_cleanup=True,
    gc_interval=10,
    
    # Memory limits
    max_memory_per_conversion=100 * 1024 * 1024,  # 100MB
    total_memory_limit=500 * 1024 * 1024,  # 500MB
)
```

---

<div align="center">
  <p>For deployment guidance, see <a href="production-deployment.md">Production Deployment</a></p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>