# Audio Converter Testing Guide

## Overview

This comprehensive test suite validates the audio conversion and speech recognition capabilities of the voidlight_markitdown audio converter. It includes tests for various audio formats, languages (with emphasis on Korean), performance benchmarks, and edge cases.

## Components

### 1. Test Audio Generation (`test_audio_generation.py`)

Generates various audio test files for comprehensive testing:

- **Speech samples** in multiple languages (English, Korean, mixed)
- **Pure tones** at different frequencies
- **Noise samples** at various levels
- **Silent audio** files
- **Mixed content** (speech + noise)
- **Different formats**: WAV, MP3, M4A, OGG
- **Various sample rates**: 8kHz to 48kHz
- **Different durations**: 5 seconds to 5 minutes

### 2. Comprehensive Test Suite (`test_audio_converter_comprehensive.py`)

Main test suite covering:

- **Dependency verification**
- **Format support testing**
- **Basic conversion validation**
- **Speech recognition accuracy**
- **Performance testing**
- **Edge case handling**
- **Korean language recognition**
- **Concurrent processing**

### 3. Performance Benchmarking (`benchmark_audio_performance.py`)

Measures performance characteristics:

- **File size scaling**: How performance scales with audio length
- **Format comparison**: Speed differences between formats
- **Sample rate impact**: Effect on processing time and accuracy
- **Concurrent load testing**: Multi-file processing capabilities
- **Resource usage monitoring**: CPU and memory consumption

### 4. Korean Language Testing (`test_korean_audio_recognition.py`)

Specialized tests for Korean speech:

- **Formal vs informal speech**
- **Technical terminology**
- **Mixed Korean-English content**
- **Number and date recognition**
- **Noise robustness**
- **Dialect variations**

### 5. Test Runner (`run_all_audio_tests.py`)

Orchestrates the entire test suite:

- Checks dependencies
- Runs all test scripts in order
- Generates summary reports
- Handles failures gracefully

## Requirements

### Python Dependencies

```bash
pip install SpeechRecognition pydub gtts psutil numpy matplotlib
```

### System Dependencies

- **ffmpeg**: Required for audio format conversion
  ```bash
  # macOS
  brew install ffmpeg
  
  # Ubuntu/Debian
  sudo apt install ffmpeg
  
  # Windows
  # Download from https://ffmpeg.org/download.html
  ```

- **Google Speech Recognition API**: Internet connection required

## Running the Tests

### Quick Start

Run all tests with the main runner:

```bash
cd tests/audio_test_suite
python run_all_audio_tests.py
```

### Individual Test Scripts

1. **Generate test audio files**:
   ```bash
   python test_audio_generation.py
   ```

2. **Run comprehensive tests**:
   ```bash
   python test_audio_converter_comprehensive.py
   ```

3. **Run performance benchmarks**:
   ```bash
   python benchmark_audio_performance.py
   ```

4. **Test Korean recognition**:
   ```bash
   python test_korean_audio_recognition.py
   ```

## Test Coverage

### Audio Formats

| Format | Extension | MIME Type | Tested |
|--------|-----------|-----------|---------|
| WAV | .wav | audio/x-wav | ✓ |
| MP3 | .mp3 | audio/mpeg | ✓ |
| M4A | .m4a | video/mp4 | ✓ |
| MP4 | .mp4 | video/mp4 | ✓ |
| OGG | .ogg | audio/ogg | ✓ |
| FLAC | .flac | audio/flac | ✓ |
| AIFF | .aiff | audio/aiff | ✓ |

### Test Scenarios

1. **Basic Functionality**
   - File format acceptance
   - Metadata extraction
   - Speech transcription

2. **Speech Recognition**
   - English speech
   - Korean speech
   - Mixed language content
   - Numbers and dates
   - Technical terminology

3. **Performance**
   - Processing speed vs file size
   - Memory usage
   - Concurrent processing
   - Different sample rates

4. **Edge Cases**
   - Empty files
   - Corrupted files
   - Silent audio
   - Very short/long files
   - High noise levels

5. **Korean-Specific**
   - Formal/informal speech
   - Regional dialects
   - Hanja mixed text
   - Business/technical contexts

## Output Reports

### Test Results

All test runs generate detailed reports in their respective directories:

1. **Test Audio Metadata**: `test_audio_files/test_metadata.json`
2. **Test Results**: `test_results/audio_test_results.json`
3. **Test Report**: `test_results/audio_test_report.md`
4. **Benchmark Results**: `benchmark_results/benchmark_results.json`
5. **Benchmark Report**: `benchmark_results/benchmark_report.md`
6. **Korean Test Results**: `korean_audio_tests/korean_audio_test_results.json`
7. **Korean Test Report**: `korean_audio_tests/korean_audio_test_report.md`

### Performance Visualizations

The benchmark suite generates performance graphs:

- `benchmark_results/file_size_scaling.png`: Processing time and speed vs file size
- `benchmark_results/format_comparison.png`: Performance comparison across formats

## Best Practices

### For Audio Conversion

1. **Optimal Formats**
   - Use WAV for best compatibility
   - MP3 for compressed audio with good support
   - M4A for Apple ecosystem

2. **Sample Rates**
   - 16kHz minimum for speech recognition
   - 44.1kHz for high quality
   - Higher rates don't improve recognition

3. **File Preparation**
   - Ensure clear audio without clipping
   - Minimize background noise
   - Use appropriate compression settings

### For Korean Recognition

1. **Audio Quality**
   - Clear pronunciation is crucial
   - Avoid overlapping speakers
   - Minimize background noise

2. **Content Optimization**
   - Separate Korean and English sections
   - Use standard pronunciation
   - Avoid extreme dialects

3. **Technical Terms**
   - English technical terms may not transcribe in Korean
   - Consider post-processing for mixed content

## Troubleshooting

### Common Issues

1. **No transcript generated**
   - Check internet connection (Google API)
   - Verify audio is not silent
   - Ensure sufficient audio quality

2. **Korean text not recognized**
   - Google API may default to English
   - Audio quality may be insufficient
   - Consider language hints in API

3. **Performance issues**
   - Large files may timeout
   - Consider chunking long audio
   - Monitor memory usage

4. **Format not supported**
   - Install ffmpeg for full support
   - Check pydub installation
   - Verify file is not corrupted

### Debug Tips

1. Enable verbose logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Test with known good files first

3. Verify dependencies:
   ```bash
   python -c "import speech_recognition as sr; print(sr.__version__)"
   ```

## Future Enhancements

1. **Additional Language Support**
   - Japanese, Chinese recognition
   - Multi-language detection
   - Language-specific models

2. **Advanced Features**
   - Speaker diarization
   - Emotion detection
   - Music vs speech classification

3. **Performance Optimization**
   - GPU acceleration
   - Streaming recognition
   - Batch processing

4. **Integration Testing**
   - API mocking for offline tests
   - CI/CD integration
   - Automated regression testing

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Generate appropriate test files
3. Include performance metrics
4. Document expected outcomes
5. Update this guide

## License

This test suite is part of the voidlight_markitdown project and follows the same license terms.