#!/usr/bin/env python3
"""
Comprehensive Audio Converter Test Suite
Tests the audio conversion and speech recognition capabilities thoroughly.
"""

import os
import sys
import time
import json
import unittest
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import io
import wave
import struct

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from voidlight_markitdown import VoidlightMarkItDown
    from voidlight_markitdown.converters import AudioConverter
    from voidlight_markitdown._stream_info import StreamInfo
    from voidlight_markitdown._exceptions import MissingDependencyException
except ImportError as e:
    print(f"Failed to import voidlight_markitdown: {e}")
    sys.exit(1)

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pydub
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class AudioConverterTestSuite(unittest.TestCase):
    """Comprehensive test suite for audio converter."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = Path(__file__).parent
        cls.audio_files_dir = cls.test_dir / "test_audio_files"
        cls.results_dir = cls.test_dir / "test_results"
        cls.results_dir.mkdir(exist_ok=True)
        
        cls.converter = AudioConverter()
        cls.markitdown = VoidlightMarkItDown()
        
        # Test results storage
        cls.test_results = {
            "test_info": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "platform": sys.platform,
                "python_version": sys.version,
                "dependencies": {
                    "speech_recognition": SPEECH_RECOGNITION_AVAILABLE,
                    "pydub": PYDUB_AVAILABLE
                }
            },
            "format_tests": {},
            "recognition_tests": {},
            "performance_tests": {},
            "edge_case_tests": {},
            "korean_tests": {},
            "errors": []
        }
    
    def test_01_dependency_check(self):
        """Test dependency availability."""
        print("\n=== Dependency Check ===")
        
        deps = {
            "speech_recognition": SPEECH_RECOGNITION_AVAILABLE,
            "pydub": PYDUB_AVAILABLE
        }
        
        for dep, available in deps.items():
            print(f"{dep}: {'✓ Available' if available else '✗ Not Available'}")
            if not available and dep == "speech_recognition":
                print("  Install with: pip install SpeechRecognition")
            elif not available and dep == "pydub":
                print("  Install with: pip install pydub")
        
        # Check for ffmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            ffmpeg_available = result.returncode == 0
        except:
            ffmpeg_available = False
        
        print(f"ffmpeg: {'✓ Available' if ffmpeg_available else '✗ Not Available'}")
        if not ffmpeg_available:
            print("  Install ffmpeg for full format support")
        
        self.test_results["test_info"]["ffmpeg"] = ffmpeg_available
    
    def test_02_format_support(self):
        """Test different audio format support."""
        print("\n=== Format Support Test ===")
        
        formats = {
            ".wav": "audio/x-wav",
            ".mp3": "audio/mpeg",
            ".m4a": "video/mp4",
            ".mp4": "video/mp4",
            ".ogg": "audio/ogg",
            ".flac": "audio/flac",
            ".aiff": "audio/aiff",
            ".aac": "audio/aac"
        }
        
        for ext, mime in formats.items():
            # Test extension acceptance
            stream_info = StreamInfo(
                source="test" + ext,
                extension=ext,
                mimetype=None
            )
            
            with io.BytesIO() as dummy_stream:
                ext_accepted = self.converter.accepts(dummy_stream, stream_info)
            
            # Test mimetype acceptance
            stream_info_mime = StreamInfo(
                source="test",
                extension=None,
                mimetype=mime
            )
            
            with io.BytesIO() as dummy_stream:
                mime_accepted = self.converter.accepts(dummy_stream, stream_info_mime)
            
            self.test_results["format_tests"][ext] = {
                "extension_accepted": ext_accepted,
                "mimetype_accepted": mime_accepted,
                "supported": ext_accepted or mime_accepted
            }
            
            status = "✓" if (ext_accepted or mime_accepted) else "✗"
            print(f"{ext:8} ({mime:20}): {status}")
    
    def test_03_basic_conversion(self):
        """Test basic audio file conversion."""
        print("\n=== Basic Conversion Test ===")
        
        # Create a simple WAV file
        test_file = self._create_test_wav_file()
        
        try:
            result = self.markitdown.convert(test_file)
            
            print(f"Conversion successful: {len(result.markdown)} characters")
            print(f"Content preview:\n{result.markdown[:200]}...")
            
            self.test_results["recognition_tests"]["basic_wav"] = {
                "success": True,
                "content_length": len(result.markdown),
                "has_metadata": "SampleRate" in result.markdown,
                "has_transcript": "Audio Transcript" in result.markdown
            }
            
        except Exception as e:
            print(f"Conversion failed: {e}")
            self.test_results["recognition_tests"]["basic_wav"] = {
                "success": False,
                "error": str(e)
            }
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_04_speech_recognition(self):
        """Test speech recognition accuracy."""
        print("\n=== Speech Recognition Test ===")
        
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("Skipping - speech_recognition not available")
            return
        
        # Use existing test files if available
        test_files = list(self.audio_files_dir.glob("speech_*.mp3")) if self.audio_files_dir.exists() else []
        
        if not test_files:
            print("No speech test files found. Run test_audio_generation.py first.")
            return
        
        for test_file in test_files[:3]:  # Test first 3 files
            print(f"\nTesting: {test_file.name}")
            
            try:
                result = self.markitdown.convert(str(test_file))
                
                has_transcript = "Audio Transcript" in result.markdown
                transcript = ""
                
                if has_transcript:
                    # Extract transcript
                    lines = result.markdown.split('\n')
                    transcript_start = False
                    for line in lines:
                        if "Audio Transcript:" in line:
                            transcript_start = True
                            continue
                        if transcript_start and line.strip():
                            transcript = line.strip()
                            break
                
                print(f"  Transcript found: {has_transcript}")
                if transcript:
                    print(f"  Content: {transcript[:100]}...")
                
                self.test_results["recognition_tests"][test_file.name] = {
                    "success": True,
                    "has_transcript": has_transcript,
                    "transcript_length": len(transcript),
                    "transcript_preview": transcript[:100] if transcript else None
                }
                
            except Exception as e:
                print(f"  Failed: {e}")
                self.test_results["recognition_tests"][test_file.name] = {
                    "success": False,
                    "error": str(e)
                }
    
    def test_05_performance(self):
        """Test performance with different file sizes."""
        print("\n=== Performance Test ===")
        
        sizes = [
            (5, "5 seconds"),
            (30, "30 seconds"),
            (60, "1 minute")
        ]
        
        for duration, label in sizes:
            print(f"\nTesting {label} audio...")
            
            # Create test file
            test_file = self._create_test_wav_file(duration=duration)
            file_size = os.path.getsize(test_file)
            
            try:
                start_time = time.time()
                result = self.markitdown.convert(test_file)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                print(f"  File size: {file_size / 1024:.1f} KB")
                print(f"  Processing time: {processing_time:.2f} seconds")
                print(f"  Speed: {file_size / processing_time / 1024:.1f} KB/s")
                
                self.test_results["performance_tests"][label] = {
                    "file_size_kb": file_size / 1024,
                    "duration_seconds": duration,
                    "processing_time": processing_time,
                    "speed_kb_per_sec": file_size / processing_time / 1024,
                    "success": True
                }
                
            except Exception as e:
                print(f"  Failed: {e}")
                self.test_results["performance_tests"][label] = {
                    "success": False,
                    "error": str(e)
                }
            finally:
                if os.path.exists(test_file):
                    os.remove(test_file)
    
    def test_06_edge_cases(self):
        """Test edge cases and error handling."""
        print("\n=== Edge Cases Test ===")
        
        # Test 1: Empty file
        print("\n1. Empty file test")
        empty_file = self.results_dir / "empty.wav"
        empty_file.touch()
        
        try:
            result = self.markitdown.convert(str(empty_file))
            print(f"  Result: {len(result.markdown)} characters")
            self.test_results["edge_case_tests"]["empty_file"] = {
                "handled": True,
                "result_length": len(result.markdown)
            }
        except Exception as e:
            print(f"  Exception: {e}")
            self.test_results["edge_case_tests"]["empty_file"] = {
                "handled": False,
                "error": str(e)
            }
        finally:
            empty_file.unlink()
        
        # Test 2: Silent audio
        print("\n2. Silent audio test")
        silent_file = self._create_test_wav_file(duration=5, silent=True)
        
        try:
            result = self.markitdown.convert(silent_file)
            has_no_speech = "[No speech detected]" in result.markdown or "Audio Transcript" not in result.markdown
            print(f"  No speech detected: {has_no_speech}")
            
            self.test_results["edge_case_tests"]["silent_audio"] = {
                "handled": True,
                "no_speech_detected": has_no_speech
            }
        except Exception as e:
            print(f"  Exception: {e}")
            self.test_results["edge_case_tests"]["silent_audio"] = {
                "handled": False,
                "error": str(e)
            }
        finally:
            if os.path.exists(silent_file):
                os.remove(silent_file)
        
        # Test 3: Corrupted file
        print("\n3. Corrupted file test")
        corrupted_file = self.results_dir / "corrupted.wav"
        with open(corrupted_file, 'wb') as f:
            f.write(b'RIFF')  # Invalid WAV file
        
        try:
            result = self.markitdown.convert(str(corrupted_file))
            print(f"  Handled gracefully: True")
            self.test_results["edge_case_tests"]["corrupted_file"] = {
                "handled_gracefully": True
            }
        except Exception as e:
            print(f"  Exception (expected): {type(e).__name__}")
            self.test_results["edge_case_tests"]["corrupted_file"] = {
                "handled_gracefully": True,
                "exception_type": type(e).__name__
            }
        finally:
            corrupted_file.unlink()
    
    def test_07_korean_recognition(self):
        """Test Korean speech recognition."""
        print("\n=== Korean Speech Recognition Test ===")
        
        korean_files = list(self.audio_files_dir.glob("*korean*.mp3")) if self.audio_files_dir.exists() else []
        
        if not korean_files:
            print("No Korean test files found. Run test_audio_generation.py first.")
            return
        
        for test_file in korean_files[:3]:
            print(f"\nTesting: {test_file.name}")
            
            try:
                result = self.markitdown.convert(str(test_file))
                
                # Check if Korean characters are in the result
                has_korean = any('\uac00' <= char <= '\ud7af' for char in result.markdown)
                
                print(f"  Conversion successful")
                print(f"  Contains Korean text: {has_korean}")
                
                if "Audio Transcript" in result.markdown:
                    # Extract transcript
                    lines = result.markdown.split('\n')
                    for i, line in enumerate(lines):
                        if "Audio Transcript:" in line and i + 1 < len(lines):
                            transcript = lines[i + 1].strip()
                            print(f"  Transcript: {transcript[:50]}...")
                            break
                
                self.test_results["korean_tests"][test_file.name] = {
                    "success": True,
                    "has_korean": has_korean,
                    "has_transcript": "Audio Transcript" in result.markdown
                }
                
            except Exception as e:
                print(f"  Failed: {e}")
                self.test_results["korean_tests"][test_file.name] = {
                    "success": False,
                    "error": str(e)
                }
    
    def test_08_concurrent_processing(self):
        """Test concurrent audio processing."""
        print("\n=== Concurrent Processing Test ===")
        
        import concurrent.futures
        
        # Create multiple test files
        test_files = []
        for i in range(3):
            test_file = self._create_test_wav_file(duration=5)
            test_files.append(test_file)
        
        print(f"Processing {len(test_files)} files concurrently...")
        
        start_time = time.time()
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self.markitdown.convert, f): f 
                    for f in test_files
                }
                
                results = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        results.append(True)
                    except Exception as e:
                        results.append(False)
                        print(f"  Concurrent processing error: {e}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            success_rate = sum(results) / len(results) * 100
            
            print(f"  Total time: {total_time:.2f} seconds")
            print(f"  Success rate: {success_rate:.1f}%")
            
            self.test_results["performance_tests"]["concurrent_processing"] = {
                "num_files": len(test_files),
                "total_time": total_time,
                "success_rate": success_rate
            }
            
        finally:
            # Cleanup
            for f in test_files:
                if os.path.exists(f):
                    os.remove(f)
    
    def _create_test_wav_file(self, duration: int = 5, sample_rate: int = 44100, 
                            silent: bool = False) -> str:
        """Create a test WAV file."""
        filename = f"test_{duration}s_{sample_rate}hz.wav"
        filepath = self.results_dir / filename
        
        with wave.open(str(filepath), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            num_frames = sample_rate * duration
            
            if silent:
                # Generate silence
                frames = [0] * num_frames
            else:
                # Generate a simple tone
                import math
                frequency = 440  # A4 note
                frames = []
                for i in range(num_frames):
                    t = i / sample_rate
                    value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t))
                    frames.append(value)
            
            data = struct.pack('<' + 'h' * num_frames, *frames)
            wav_file.writeframes(data)
        
        return str(filepath)
    
    @classmethod
    def tearDownClass(cls):
        """Save test results."""
        # Save results to JSON
        results_file = cls.results_dir / "audio_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(cls.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nTest results saved to: {results_file}")
        
        # Generate summary report
        cls._generate_summary_report()
    
    @classmethod
    def _generate_summary_report(cls):
        """Generate a summary report of test results."""
        report_file = cls.results_dir / "audio_test_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Audio Converter Test Report\n\n")
            f.write(f"**Test Date:** {cls.test_results['test_info']['timestamp']}\n")
            f.write(f"**Platform:** {cls.test_results['test_info']['platform']}\n\n")
            
            # Dependencies
            f.write("## Dependencies\n\n")
            for dep, available in cls.test_results['test_info']['dependencies'].items():
                status = "✓" if available else "✗"
                f.write(f"- {dep}: {status}\n")
            f.write("\n")
            
            # Format Support
            f.write("## Format Support\n\n")
            f.write("| Format | Extension | MIME Type | Supported |\n")
            f.write("|--------|-----------|-----------|------------|\n")
            for ext, info in cls.test_results['format_tests'].items():
                status = "✓" if info['supported'] else "✗"
                f.write(f"| {ext} | {info['extension_accepted']} | {info['mimetype_accepted']} | {status} |\n")
            f.write("\n")
            
            # Recognition Tests
            f.write("## Recognition Tests\n\n")
            success_count = sum(1 for t in cls.test_results['recognition_tests'].values() if t.get('success', False))
            total_count = len(cls.test_results['recognition_tests'])
            f.write(f"**Success Rate:** {success_count}/{total_count}\n\n")
            
            # Performance Summary
            if cls.test_results['performance_tests']:
                f.write("## Performance Summary\n\n")
                f.write("| Test | File Size | Processing Time | Speed |\n")
                f.write("|------|-----------|-----------------|--------|\n")
                for test, info in cls.test_results['performance_tests'].items():
                    if info.get('success'):
                        f.write(f"| {test} | {info.get('file_size_kb', 0):.1f} KB | "
                               f"{info.get('processing_time', 0):.2f}s | "
                               f"{info.get('speed_kb_per_sec', 0):.1f} KB/s |\n")
            
            # Korean Tests
            if cls.test_results['korean_tests']:
                f.write("\n## Korean Speech Recognition\n\n")
                korean_success = sum(1 for t in cls.test_results['korean_tests'].values() if t.get('success', False))
                f.write(f"**Success Rate:** {korean_success}/{len(cls.test_results['korean_tests'])}\n")
            
            # Edge Cases
            f.write("\n## Edge Case Handling\n\n")
            for case, result in cls.test_results['edge_case_tests'].items():
                handled = result.get('handled', False) or result.get('handled_gracefully', False)
                status = "✓" if handled else "✗"
                f.write(f"- {case}: {status}\n")
        
        print(f"Summary report saved to: {report_file}")


def main():
    """Run the test suite."""
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(AudioConverterTestSuite)
    
    # Run tests
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())