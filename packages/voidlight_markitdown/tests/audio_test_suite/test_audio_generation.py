#!/usr/bin/env python3
"""
Audio Test Generation Script
Generates various audio test files for comprehensive testing of the audio converter.
"""

import os
import sys
import wave
import struct
import numpy as np
from pathlib import Path
import subprocess
import json
from typing import Dict, Any, List, Tuple

# Check for required dependencies
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("WARNING: gTTS not available. Install with: pip install gtts")

try:
    import pydub
    from pydub import AudioSegment
    from pydub.generators import Sine, WhiteNoise
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("WARNING: pydub not available. Install with: pip install pydub")

class AudioTestGenerator:
    """Generate various audio test files for testing speech recognition."""
    
    def __init__(self, output_dir: str = "test_audio_files"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test phrases in different languages
        self.test_phrases = {
            "english": {
                "simple": "Hello, this is a test audio file.",
                "technical": "The artificial intelligence system processes natural language with high accuracy.",
                "numbers": "The temperature is twenty three degrees celsius at three forty five PM.",
                "long": "This is a longer test message to validate the speech recognition system's ability to handle extended audio content. The system should be able to transcribe multiple sentences accurately without losing context or introducing errors in the transcription process."
            },
            "korean": {
                "simple": "안녕하세요, 이것은 테스트 오디오 파일입니다.",
                "technical": "인공지능 시스템은 자연어를 높은 정확도로 처리합니다.",
                "numbers": "현재 온도는 섭씨 이십삼도이며 시간은 오후 세시 사십오분입니다.",
                "formal": "귀하의 요청을 검토한 결과, 다음과 같은 사항을 안내드립니다.",
                "informal": "오늘 날씨 정말 좋네요. 같이 커피 한잔 할래요?"
            },
            "mixed": {
                "code_switch": "안녕하세요, my name is Claude. 저는 AI assistant입니다.",
                "technical_mixed": "이 Python 코드는 machine learning algorithm을 구현합니다."
            }
        }
        
        # Audio parameters
        self.sample_rates = [8000, 16000, 22050, 44100, 48000]
        self.durations = [5, 30, 60, 180, 300]  # seconds
        
    def generate_all_tests(self) -> Dict[str, Any]:
        """Generate all test audio files and return metadata."""
        results = {
            "generated_files": [],
            "failed": [],
            "metadata": {}
        }
        
        # 1. Generate speech samples
        print("Generating speech samples...")
        speech_files = self._generate_speech_samples()
        results["generated_files"].extend(speech_files["success"])
        results["failed"].extend(speech_files["failed"])
        
        # 2. Generate pure tone tests
        print("Generating pure tone tests...")
        tone_files = self._generate_tone_tests()
        results["generated_files"].extend(tone_files)
        
        # 3. Generate noise tests
        print("Generating noise tests...")
        noise_files = self._generate_noise_tests()
        results["generated_files"].extend(noise_files)
        
        # 4. Generate silence tests
        print("Generating silence tests...")
        silence_files = self._generate_silence_tests()
        results["generated_files"].extend(silence_files)
        
        # 5. Generate mixed content tests
        print("Generating mixed content tests...")
        mixed_files = self._generate_mixed_tests()
        results["generated_files"].extend(mixed_files)
        
        # 6. Generate format conversion tests
        print("Generating format conversion tests...")
        format_files = self._convert_formats()
        results["generated_files"].extend(format_files)
        
        # 7. Generate edge case tests
        print("Generating edge case tests...")
        edge_files = self._generate_edge_cases()
        results["generated_files"].extend(edge_files)
        
        # Save metadata
        metadata_path = self.output_dir / "test_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    def _generate_speech_samples(self) -> Dict[str, List[str]]:
        """Generate speech samples using text-to-speech."""
        results = {"success": [], "failed": []}
        
        if not GTTS_AVAILABLE:
            print("Skipping TTS generation - gTTS not available")
            return results
        
        for lang_code, phrases in self.test_phrases.items():
            for phrase_type, text in phrases.items():
                try:
                    filename = f"speech_{lang_code}_{phrase_type}.mp3"
                    filepath = self.output_dir / filename
                    
                    # Determine language code for gTTS
                    if lang_code == "english":
                        tts_lang = "en"
                    elif lang_code == "korean":
                        tts_lang = "ko"
                    else:
                        tts_lang = "en"  # Default to English for mixed
                    
                    # Generate TTS
                    tts = gTTS(text=text, lang=tts_lang)
                    tts.save(str(filepath))
                    
                    results["success"].append(str(filepath))
                    print(f"Generated: {filename}")
                    
                except Exception as e:
                    print(f"Failed to generate {lang_code}_{phrase_type}: {e}")
                    results["failed"].append(f"{lang_code}_{phrase_type}: {str(e)}")
        
        return results
    
    def _generate_tone_tests(self) -> List[str]:
        """Generate pure tone test files."""
        files = []
        
        if not PYDUB_AVAILABLE:
            print("Skipping tone generation - pydub not available")
            return files
        
        frequencies = [440, 1000, 2000, 4000]  # Hz
        
        for freq in frequencies:
            for duration in [1, 5]:  # seconds
                filename = f"tone_{freq}hz_{duration}s.wav"
                filepath = self.output_dir / filename
                
                # Generate sine wave
                tone = Sine(freq).to_audio_segment(duration=duration*1000)
                tone.export(str(filepath), format="wav")
                
                files.append(str(filepath))
                print(f"Generated: {filename}")
        
        return files
    
    def _generate_noise_tests(self) -> List[str]:
        """Generate noise test files."""
        files = []
        
        if not PYDUB_AVAILABLE:
            print("Skipping noise generation - pydub not available")
            return files
        
        noise_levels = ["low", "medium", "high"]
        durations = [5, 10]  # seconds
        
        for level in noise_levels:
            for duration in durations:
                filename = f"noise_{level}_{duration}s.wav"
                filepath = self.output_dir / filename
                
                # Generate white noise
                noise = WhiteNoise().to_audio_segment(duration=duration*1000)
                
                # Adjust volume based on level
                if level == "low":
                    noise = noise - 20  # Reduce by 20dB
                elif level == "medium":
                    noise = noise - 10  # Reduce by 10dB
                # high = original volume
                
                noise.export(str(filepath), format="wav")
                files.append(str(filepath))
                print(f"Generated: {filename}")
        
        return files
    
    def _generate_silence_tests(self) -> List[str]:
        """Generate silent audio files."""
        files = []
        
        for duration in [5, 30]:
            filename = f"silence_{duration}s.wav"
            filepath = self.output_dir / filename
            
            # Generate silence using wave module
            with wave.open(str(filepath), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # 44.1kHz
                
                # Write silence (zeros)
                num_frames = 44100 * duration
                silence_data = struct.pack('<' + 'h' * num_frames, *[0] * num_frames)
                wav_file.writeframes(silence_data)
            
            files.append(str(filepath))
            print(f"Generated: {filename}")
        
        return files
    
    def _generate_mixed_tests(self) -> List[str]:
        """Generate mixed content tests (speech + noise/music)."""
        files = []
        
        if not PYDUB_AVAILABLE:
            print("Skipping mixed content generation - pydub not available")
            return files
        
        # This would require existing speech files
        # For now, we'll create a simple mixed tone example
        filename = "mixed_tones.wav"
        filepath = self.output_dir / filename
        
        # Mix two different frequency tones
        tone1 = Sine(440).to_audio_segment(duration=5000)
        tone2 = Sine(880).to_audio_segment(duration=5000)
        
        mixed = tone1.overlay(tone2 - 10)  # Second tone 10dB quieter
        mixed.export(str(filepath), format="wav")
        
        files.append(str(filepath))
        print(f"Generated: {filename}")
        
        return files
    
    def _convert_formats(self) -> List[str]:
        """Convert a base file to different formats."""
        files = []
        
        if not PYDUB_AVAILABLE:
            print("Skipping format conversion - pydub not available")
            return files
        
        # Create a base audio file
        base_audio = Sine(440).to_audio_segment(duration=5000)
        
        # Convert to different formats
        formats = {
            "mp3": {"codec": "mp3", "bitrate": "128k"},
            "m4a": {"codec": "aac", "bitrate": "128k"},
            "ogg": {"codec": "libvorbis", "bitrate": "128k"},
            "wav": {"codec": None, "bitrate": None}
        }
        
        for fmt, params in formats.items():
            for sample_rate in [8000, 16000, 44100]:
                filename = f"format_test_{sample_rate}hz.{fmt}"
                filepath = self.output_dir / filename
                
                # Set sample rate
                audio = base_audio.set_frame_rate(sample_rate)
                
                # Export with specific parameters
                if params["codec"]:
                    audio.export(
                        str(filepath),
                        format=fmt,
                        codec=params["codec"],
                        bitrate=params["bitrate"]
                    )
                else:
                    audio.export(str(filepath), format=fmt)
                
                files.append(str(filepath))
                print(f"Generated: {filename}")
        
        return files
    
    def _generate_edge_cases(self) -> List[str]:
        """Generate edge case test files."""
        files = []
        
        # 1. Very short file (0.1 seconds)
        filename = "edge_very_short.wav"
        filepath = self.output_dir / filename
        
        with wave.open(str(filepath), 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            
            # 0.1 seconds of audio
            num_frames = int(44100 * 0.1)
            data = struct.pack('<' + 'h' * num_frames, *[0] * num_frames)
            wav_file.writeframes(data)
        
        files.append(str(filepath))
        print(f"Generated: {filename}")
        
        # 2. Corrupted file (truncated)
        filename = "edge_corrupted.wav"
        filepath = self.output_dir / filename
        
        # Create a normal file first
        with wave.open(str(filepath), 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            num_frames = 44100  # 1 second
            data = struct.pack('<' + 'h' * num_frames, *[0] * num_frames)
            wav_file.writeframes(data)
        
        # Truncate it
        with open(filepath, 'r+b') as f:
            f.truncate(100)  # Keep only first 100 bytes
        
        files.append(str(filepath))
        print(f"Generated: {filename}")
        
        # 3. Empty file
        filename = "edge_empty.wav"
        filepath = self.output_dir / filename
        filepath.touch()  # Create empty file
        files.append(str(filepath))
        print(f"Generated: {filename}")
        
        return files
    
    def generate_korean_specific_tests(self) -> List[str]:
        """Generate Korean-specific test cases."""
        files = []
        
        if not GTTS_AVAILABLE:
            print("Skipping Korean-specific tests - gTTS not available")
            return files
        
        korean_tests = {
            "formal_business": "안녕하십니까. 오늘 회의 안건은 신제품 출시 전략입니다.",
            "technical_terms": "머신러닝 알고리즘의 정확도는 구십팔 퍼센트입니다.",
            "mixed_numbers": "내일 오후 2시 30분에 미팅이 있습니다. 장소는 회의실 A동 203호입니다.",
            "dialect_seoul": "어제 명동에 갔는데 사람이 엄청 많더라고요.",
            "hanja_mixed": "經濟(경제) 發展(발전)을 위한 政策(정책)을 수립했습니다."
        }
        
        for test_name, text in korean_tests.items():
            try:
                filename = f"korean_specific_{test_name}.mp3"
                filepath = self.output_dir / filename
                
                tts = gTTS(text=text, lang='ko')
                tts.save(str(filepath))
                
                files.append(str(filepath))
                print(f"Generated: {filename}")
                
            except Exception as e:
                print(f"Failed to generate Korean test {test_name}: {e}")
        
        return files


def main():
    """Main function to generate all test audio files."""
    print("Audio Test File Generator")
    print("=" * 50)
    
    generator = AudioTestGenerator()
    
    # Generate all test files
    results = generator.generate_all_tests()
    
    # Generate Korean-specific tests
    korean_files = generator.generate_korean_specific_tests()
    results["generated_files"].extend(korean_files)
    
    # Summary
    print("\n" + "=" * 50)
    print("Generation Summary:")
    print(f"Successfully generated: {len(results['generated_files'])} files")
    print(f"Failed: {len(results['failed'])} files")
    
    if results['failed']:
        print("\nFailed generations:")
        for fail in results['failed']:
            print(f"  - {fail}")
    
    print(f"\nAll files saved to: {generator.output_dir}")
    print(f"Metadata saved to: {generator.output_dir / 'test_metadata.json'}")


if __name__ == "__main__":
    main()