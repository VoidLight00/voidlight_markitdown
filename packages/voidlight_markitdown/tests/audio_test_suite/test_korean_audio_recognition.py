#!/usr/bin/env python3
"""
Korean Audio Recognition Test Suite
Tests specifically for Korean speech recognition capabilities.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from voidlight_markitdown import VoidlightMarkItDown
    from voidlight_markitdown.converters import AudioConverter
except ImportError as e:
    print(f"Failed to import voidlight_markitdown: {e}")
    sys.exit(1)

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("WARNING: gTTS not available. Install with: pip install gtts")


class KoreanAudioTestSuite:
    """Test suite for Korean audio recognition."""
    
    def __init__(self):
        self.markitdown = VoidlightMarkItDown()
        self.converter = AudioConverter()
        self.test_dir = Path(__file__).parent
        self.korean_test_dir = self.test_dir / "korean_audio_tests"
        self.korean_test_dir.mkdir(exist_ok=True)
        
        # Korean test scenarios
        self.korean_scenarios = {
            "business_formal": {
                "text": "안녕하십니까. 오늘 회의에서는 다음 분기 매출 목표와 마케팅 전략에 대해 논의하겠습니다. 각 부서별로 준비한 자료를 발표해 주시기 바랍니다.",
                "context": "Formal business meeting",
                "expected_keywords": ["회의", "매출", "마케팅", "전략", "부서"]
            },
            "technical_presentation": {
                "text": "인공지능 기술의 발전으로 자연어 처리 분야에서 큰 성과를 거두고 있습니다. 특히 트랜스포머 모델의 등장 이후 한국어 처리 정확도가 크게 향상되었습니다.",
                "context": "Technical presentation",
                "expected_keywords": ["인공지능", "자연어", "처리", "트랜스포머", "한국어"]
            },
            "customer_service": {
                "text": "고객님, 안녕하세요. 무엇을 도와드릴까요? 제품에 문제가 있으시면 구체적으로 설명해 주시면 감사하겠습니다.",
                "context": "Customer service interaction",
                "expected_keywords": ["고객님", "도와드릴까요", "제품", "문제", "설명"]
            },
            "news_broadcast": {
                "text": "오늘 서울의 날씨는 맑고 기온은 영상 이십삼도까지 오를 예정입니다. 내일은 전국적으로 비가 예상되니 우산을 준비하시기 바랍니다.",
                "context": "News/weather broadcast",
                "expected_keywords": ["서울", "날씨", "기온", "이십삼도", "비"]
            },
            "casual_conversation": {
                "text": "어제 봤던 영화 정말 재밌었어. 너도 시간 있으면 꼭 봐. 주말에 같이 또 영화 보러 갈래?",
                "context": "Casual conversation",
                "expected_keywords": ["영화", "재밌었어", "시간", "주말", "같이"]
            },
            "mixed_language": {
                "text": "이번 프로젝트는 Python과 JavaScript를 사용해서 개발할 예정입니다. API는 REST 방식으로 구현하고 데이터베이스는 PostgreSQL을 사용합니다.",
                "context": "Technical discussion with English terms",
                "expected_keywords": ["프로젝트", "Python", "JavaScript", "API", "REST", "데이터베이스", "PostgreSQL"]
            },
            "numbers_and_units": {
                "text": "총 예산은 삼억 오천만원이며, 프로젝트 기간은 육개월입니다. 첫 번째 마일스톤은 이천이십오년 삼월 십오일까지 완료해야 합니다.",
                "context": "Numbers and dates in Korean",
                "expected_keywords": ["삼억", "오천만원", "육개월", "이천이십오년", "삼월"]
            },
            "dialect_variations": {
                "text": "아이고, 정말 맛있네요. 이 음식은 우리 할머니가 만들어 주시던 것과 똑같아요. 고맙습니다.",
                "context": "Regional dialect/expression",
                "expected_keywords": ["아이고", "맛있네요", "음식", "할머니", "고맙습니다"]
            }
        }
        
        # Test results storage
        self.test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scenarios": {},
            "accuracy_metrics": {},
            "performance_metrics": {},
            "errors": []
        }
    
    def generate_korean_test_files(self) -> Dict[str, str]:
        """Generate Korean audio test files."""
        print("\n=== Generating Korean Test Audio Files ===")
        
        if not GTTS_AVAILABLE:
            print("ERROR: gTTS not available. Cannot generate test files.")
            return {}
        
        generated_files = {}
        
        for scenario_name, scenario_data in self.korean_scenarios.items():
            try:
                filename = f"korean_{scenario_name}.mp3"
                filepath = self.korean_test_dir / filename
                
                # Generate audio
                tts = gTTS(text=scenario_data["text"], lang='ko')
                tts.save(str(filepath))
                
                generated_files[scenario_name] = str(filepath)
                print(f"✓ Generated: {filename}")
                
                # Also generate with different speeds
                # Slow speed
                slow_filename = f"korean_{scenario_name}_slow.mp3"
                slow_filepath = self.korean_test_dir / slow_filename
                tts_slow = gTTS(text=scenario_data["text"], lang='ko', slow=True)
                tts_slow.save(str(slow_filepath))
                generated_files[f"{scenario_name}_slow"] = str(slow_filepath)
                
            except Exception as e:
                print(f"✗ Failed to generate {scenario_name}: {e}")
                self.test_results["errors"].append({
                    "type": "generation",
                    "scenario": scenario_name,
                    "error": str(e)
                })
        
        return generated_files
    
    def test_recognition_accuracy(self, test_files: Dict[str, str]):
        """Test recognition accuracy for Korean speech."""
        print("\n=== Korean Recognition Accuracy Test ===")
        
        for scenario_name, filepath in test_files.items():
            if not os.path.exists(filepath):
                continue
            
            print(f"\nTesting: {scenario_name}")
            
            try:
                # Convert audio
                start_time = time.time()
                result = self.markitdown.convert(filepath)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # Extract transcript
                transcript = self._extract_transcript(result.markdown)
                
                # Analyze results
                has_transcript = transcript is not None
                has_korean = False
                keyword_matches = []
                
                if transcript:
                    # Check for Korean characters
                    has_korean = any('\uac00' <= char <= '\ud7af' for char in transcript)
                    
                    # Check for expected keywords (if not a slow version)
                    if "_slow" not in scenario_name:
                        original_scenario = scenario_name
                        if original_scenario in self.korean_scenarios:
                            expected = self.korean_scenarios[original_scenario]["expected_keywords"]
                            keyword_matches = [kw for kw in expected if kw in transcript]
                
                # Calculate accuracy metrics
                keyword_accuracy = len(keyword_matches) / len(self.korean_scenarios.get(
                    scenario_name.replace("_slow", ""), {}).get("expected_keywords", [1])) * 100
                
                self.test_results["scenarios"][scenario_name] = {
                    "success": True,
                    "has_transcript": has_transcript,
                    "has_korean": has_korean,
                    "transcript_length": len(transcript) if transcript else 0,
                    "transcript": transcript[:200] if transcript else None,
                    "processing_time": processing_time,
                    "keyword_matches": keyword_matches,
                    "keyword_accuracy": keyword_accuracy
                }
                
                print(f"  ✓ Success")
                print(f"  Has transcript: {has_transcript}")
                print(f"  Has Korean text: {has_korean}")
                print(f"  Keyword accuracy: {keyword_accuracy:.1f}%")
                if transcript:
                    print(f"  Transcript preview: {transcript[:50]}...")
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                self.test_results["scenarios"][scenario_name] = {
                    "success": False,
                    "error": str(e)
                }
    
    def test_noise_robustness(self):
        """Test recognition with background noise."""
        print("\n=== Noise Robustness Test ===")
        
        if not GTTS_AVAILABLE:
            print("Skipping - gTTS not available")
            return
        
        try:
            import pydub
            from pydub import AudioSegment
            from pydub.generators import WhiteNoise
        except ImportError:
            print("Skipping - pydub not available")
            return
        
        # Use a simple test phrase
        test_text = "안녕하세요. 오늘 날씨가 참 좋네요."
        
        noise_levels = [
            ("clean", 0),
            ("low_noise", -20),
            ("medium_noise", -10),
            ("high_noise", -5)
        ]
        
        for noise_name, noise_db in noise_levels:
            try:
                print(f"\nTesting with {noise_name}...")
                
                # Generate clean audio
                clean_file = self.korean_test_dir / f"noise_test_{noise_name}.mp3"
                tts = gTTS(text=test_text, lang='ko')
                tts.save(str(clean_file))
                
                if noise_db < 0:
                    # Add noise
                    speech = AudioSegment.from_mp3(str(clean_file))
                    noise = WhiteNoise().to_audio_segment(duration=len(speech))
                    noise = noise + noise_db  # Adjust noise level
                    
                    # Mix speech with noise
                    mixed = speech.overlay(noise)
                    mixed.export(str(clean_file), format="mp3")
                
                # Test recognition
                result = self.markitdown.convert(str(clean_file))
                transcript = self._extract_transcript(result.markdown)
                
                has_korean = transcript and any('\uac00' <= char <= '\ud7af' for char in transcript)
                
                self.test_results["scenarios"][f"noise_{noise_name}"] = {
                    "success": True,
                    "has_transcript": transcript is not None,
                    "has_korean": has_korean,
                    "noise_level_db": noise_db,
                    "transcript": transcript[:100] if transcript else None
                }
                
                print(f"  Transcript found: {transcript is not None}")
                print(f"  Has Korean: {has_korean}")
                
            except Exception as e:
                print(f"  Failed: {e}")
                self.test_results["scenarios"][f"noise_{noise_name}"] = {
                    "success": False,
                    "error": str(e)
                }
    
    def test_multiple_speakers(self):
        """Test recognition with multiple speakers/voices."""
        print("\n=== Multiple Speakers Test ===")
        
        # This would require more sophisticated audio generation
        # For now, we'll test with overlapping speech
        
        print("Note: Multi-speaker testing requires advanced audio synthesis")
        print("Current implementation uses single TTS engine")
    
    def calculate_metrics(self):
        """Calculate overall accuracy metrics."""
        print("\n=== Calculating Metrics ===")
        
        successful_tests = [s for s in self.test_results["scenarios"].values() if s.get("success")]
        
        if successful_tests:
            # Recognition rate
            recognition_rate = sum(1 for s in successful_tests if s.get("has_transcript")) / len(successful_tests) * 100
            
            # Korean detection rate
            korean_rate = sum(1 for s in successful_tests if s.get("has_korean")) / len(successful_tests) * 100
            
            # Average keyword accuracy
            keyword_accuracies = [s.get("keyword_accuracy", 0) for s in successful_tests if "keyword_accuracy" in s]
            avg_keyword_accuracy = sum(keyword_accuracies) / len(keyword_accuracies) if keyword_accuracies else 0
            
            # Processing speed
            processing_times = [s.get("processing_time", 0) for s in successful_tests if "processing_time" in s]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            self.test_results["accuracy_metrics"] = {
                "total_tests": len(self.test_results["scenarios"]),
                "successful_tests": len(successful_tests),
                "recognition_rate": recognition_rate,
                "korean_detection_rate": korean_rate,
                "average_keyword_accuracy": avg_keyword_accuracy,
                "average_processing_time": avg_processing_time
            }
            
            print(f"Total tests: {len(self.test_results['scenarios'])}")
            print(f"Successful: {len(successful_tests)}")
            print(f"Recognition rate: {recognition_rate:.1f}%")
            print(f"Korean detection: {korean_rate:.1f}%")
            print(f"Avg keyword accuracy: {avg_keyword_accuracy:.1f}%")
    
    def _extract_transcript(self, markdown: str) -> Optional[str]:
        """Extract transcript from markdown output."""
        if "Audio Transcript:" not in markdown:
            return None
        
        lines = markdown.split('\n')
        transcript_start = False
        
        for i, line in enumerate(lines):
            if "Audio Transcript:" in line:
                # Get the next non-empty line
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        return lines[j].strip()
        
        return None
    
    def generate_report(self):
        """Generate comprehensive test report."""
        # Save JSON results
        results_file = self.korean_test_dir / "korean_audio_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # Generate Markdown report
        report_file = self.korean_test_dir / "korean_audio_test_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Korean Audio Recognition Test Report\n\n")
            f.write(f"**Test Date:** {self.test_results['timestamp']}\n\n")
            
            # Summary metrics
            if self.test_results["accuracy_metrics"]:
                f.write("## Summary Metrics\n\n")
                metrics = self.test_results["accuracy_metrics"]
                f.write(f"- **Total Tests:** {metrics['total_tests']}\n")
                f.write(f"- **Successful Tests:** {metrics['successful_tests']}\n")
                f.write(f"- **Recognition Rate:** {metrics['recognition_rate']:.1f}%\n")
                f.write(f"- **Korean Detection Rate:** {metrics['korean_detection_rate']:.1f}%\n")
                f.write(f"- **Average Keyword Accuracy:** {metrics['average_keyword_accuracy']:.1f}%\n")
                f.write(f"- **Average Processing Time:** {metrics['average_processing_time']:.2f}s\n\n")
            
            # Scenario results
            f.write("## Scenario Test Results\n\n")
            
            for scenario_name, result in self.test_results["scenarios"].items():
                f.write(f"### {scenario_name}\n\n")
                
                if result.get("success"):
                    f.write(f"- **Status:** ✓ Success\n")
                    f.write(f"- **Has Transcript:** {result.get('has_transcript', False)}\n")
                    f.write(f"- **Has Korean Text:** {result.get('has_korean', False)}\n")
                    
                    if "keyword_accuracy" in result:
                        f.write(f"- **Keyword Accuracy:** {result['keyword_accuracy']:.1f}%\n")
                    
                    if result.get("transcript"):
                        f.write(f"- **Transcript Preview:** {result['transcript'][:100]}...\n")
                else:
                    f.write(f"- **Status:** ✗ Failed\n")
                    f.write(f"- **Error:** {result.get('error', 'Unknown')}\n")
                
                f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("1. **Language Model**: Consider using Korean-specific speech recognition models\n")
            f.write("2. **Preprocessing**: Apply noise reduction for better accuracy\n")
            f.write("3. **Context**: Use domain-specific vocabulary for technical terms\n")
            f.write("4. **Testing**: Expand test set with real-world recordings\n")
        
        print(f"\nReports saved to:")
        print(f"  JSON: {results_file}")
        print(f"  Markdown: {report_file}")


def main():
    """Run Korean audio recognition tests."""
    print("Korean Audio Recognition Test Suite")
    print("=" * 50)
    
    tester = KoreanAudioTestSuite()
    
    # Generate test files
    test_files = tester.generate_korean_test_files()
    
    if test_files:
        # Run recognition tests
        tester.test_recognition_accuracy(test_files)
        
        # Test noise robustness
        tester.test_noise_robustness()
        
        # Test multiple speakers
        tester.test_multiple_speakers()
        
        # Calculate metrics
        tester.calculate_metrics()
    else:
        print("\nNo test files generated. Please install gTTS:")
        print("  pip install gtts")
    
    # Generate report
    tester.generate_report()
    
    print("\n" + "=" * 50)
    print("Korean audio testing complete!")


if __name__ == "__main__":
    main()