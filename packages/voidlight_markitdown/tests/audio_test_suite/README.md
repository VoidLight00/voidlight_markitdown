# Audio Converter Test Suite

Comprehensive testing framework for the voidlight_markitdown audio converter, focusing on speech-to-text capabilities, format support, and Korean language recognition.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install system dependencies (macOS example)
brew install ffmpeg

# Run all tests
python run_all_audio_tests.py
```

## Test Components

1. **`test_audio_generation.py`** - Generates test audio files
2. **`test_audio_converter_comprehensive.py`** - Main test suite
3. **`benchmark_audio_performance.py`** - Performance benchmarking
4. **`test_korean_audio_recognition.py`** - Korean language tests
5. **`run_all_audio_tests.py`** - Test orchestrator

## Key Features

- ✅ Multi-format support (WAV, MP3, M4A, OGG)
- ✅ Speech recognition accuracy testing
- ✅ Korean language specialized tests
- ✅ Performance benchmarking
- ✅ Edge case handling
- ✅ Concurrent processing tests
- ✅ Resource usage monitoring

## Reports Generated

- `test_results/audio_test_report.md` - Comprehensive test results
- `benchmark_results/benchmark_report.md` - Performance analysis
- `korean_audio_tests/korean_audio_test_report.md` - Korean recognition analysis

## Requirements

- Python 3.8+
- ffmpeg (system dependency)
- Internet connection (for Google Speech Recognition API)

See [AUDIO_TESTING_GUIDE.md](AUDIO_TESTING_GUIDE.md) for detailed documentation.