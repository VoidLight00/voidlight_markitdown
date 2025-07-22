#!/usr/bin/env python3
"""
Korean NLP Features Demo

This script demonstrates the Korean NLP capabilities of voidlight_markitdown.
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from voidlight_markitdown._korean_utils import KoreanTextProcessor
from voidlight_markitdown._korean_nlp_init import print_status_report


def demo_basic_features():
    """Demonstrate basic Korean text processing features."""
    print("\n" + "="*60)
    print("Korean NLP Basic Features Demo")
    print("="*60)
    
    processor = KoreanTextProcessor()
    
    # Sample texts
    sample_text = "안녕하세요. 오늘 날씨가 정말 좋네요! 공원에서 산책하고 싶습니다."
    
    print(f"\nOriginal text: {sample_text}")
    
    # 1. Tokenization
    print("\n1. Tokenization:")
    tokens = processor.tokenize(sample_text)
    for token, pos in tokens[:10]:  # Show first 10 tokens
        print(f"   {token:10s} -> {pos}")
    if len(tokens) > 10:
        print(f"   ... and {len(tokens) - 10} more tokens")
    
    # 2. Sentence segmentation
    print("\n2. Sentence Segmentation:")
    sentences = processor.segment_sentences(sample_text)
    for i, sent in enumerate(sentences, 1):
        print(f"   Sentence {i}: {sent}")
    
    # 3. Noun extraction
    print("\n3. Noun Extraction:")
    nouns = processor.extract_nouns(sample_text)
    print(f"   Nouns: {', '.join(nouns)}")
    
    # 4. Keyword extraction
    print("\n4. Keyword Extraction:")
    keywords = processor.extract_keywords(sample_text, num_keywords=5)
    for word, score in keywords:
        print(f"   {word}: {score:.3f}")


def demo_spacing_correction():
    """Demonstrate spacing correction feature."""
    print("\n" + "="*60)
    print("Spacing Correction Demo")
    print("="*60)
    
    processor = KoreanTextProcessor()
    
    # Text with spacing issues
    texts = [
        "안녕하세요오늘날씨가좋네요",
        "한국어자연어처리는어렵습니다",
        "맛있는김치찌개를먹고싶어요"
    ]
    
    for text in texts:
        corrected = processor.correct_spacing(text)
        print(f"\nOriginal:  {text}")
        print(f"Corrected: {corrected}")
        
        if corrected == text:
            print("   (No spacing correction available - install kiwipiepy)")


def demo_formality_analysis():
    """Demonstrate formality level analysis."""
    print("\n" + "="*60)
    print("Formality Analysis Demo")
    print("="*60)
    
    processor = KoreanTextProcessor()
    
    texts = {
        "Formal": "안녕하십니까. 오늘 발표를 맡게 된 김철수입니다. 여러분께 인사드립니다.",
        "Polite": "안녕하세요. 만나서 반가워요. 잘 부탁드려요.",
        "Informal": "야, 뭐해? 오늘 시간 있어? 같이 놀자."
    }
    
    for style, text in texts.items():
        analysis = processor.analyze_formality(text)
        print(f"\n{style} Text: {text}")
        print(f"   Detected Level: {analysis['formality_level']}")
        print(f"   Formal endings: {analysis['formal_endings']}")
        print(f"   Informal endings: {analysis['informal_endings']}")
        print(f"   Honorifics: {analysis['honorific_count']}")


def demo_reading_difficulty():
    """Demonstrate reading difficulty estimation."""
    print("\n" + "="*60)
    print("Reading Difficulty Analysis Demo")
    print("="*60)
    
    processor = KoreanTextProcessor()
    
    texts = {
        "Simple": "나는 학생이다. 학교에 간다. 공부를 한다.",
        "Intermediate": "오늘 날씨가 매우 좋아서 친구들과 함께 공원에 갔습니다. 우리는 즐거운 시간을 보냈습니다.",
        "Complex": "現代 韓國 社會의 急速한 變化는 傳統的 價値觀과 西歐的 文化의 衝突을 야기하고 있으며, 이는 世代 간의 葛藤으로 이어지고 있다."
    }
    
    for level, text in texts.items():
        difficulty = processor.get_reading_difficulty(text)
        print(f"\n{level} Text: {text[:50]}...")
        print(f"   Difficulty Level: {difficulty['level']}")
        print(f"   Avg Sentence Length: {difficulty['avg_sentence_length']:.1f} words")
        print(f"   Complex Word Ratio: {difficulty['complex_word_ratio']:.2%}")
        print(f"   Hanja Ratio: {difficulty['hanja_ratio']:.2%}")


def demo_metadata_extraction():
    """Demonstrate comprehensive metadata extraction."""
    print("\n" + "="*60)
    print("Metadata Extraction Demo")
    print("="*60)
    
    processor = KoreanTextProcessor()
    
    # Mixed language text
    text = """안녕하세요! Hello, everyone! 
    오늘은 韓國語 수업입니다. Let's learn Korean together.
    여러분 모두 열심히 공부하세요. 화이팅! Fighting!"""
    
    metadata = processor.extract_korean_metadata(text)
    
    print(f"Text: {text}")
    print(f"\nMetadata:")
    print(f"   Korean ratio: {metadata['korean_ratio']:.2%}")
    print(f"   Has Korean: {metadata['has_korean']}")
    print(f"   Has Hanja: {metadata['has_hanja']}")
    print(f"   Has mixed scripts: {metadata['has_mixed_script']}")
    print(f"   Character count: {metadata['char_count']}")
    print(f"   Word count: {metadata['word_count']}")
    print(f"   Sentence count: {metadata['sentence_count']}")
    
    if 'top_nouns' in metadata and metadata['top_nouns']:
        print(f"   Top nouns: {', '.join(metadata['top_nouns'][:5])}")


def main():
    """Run all demos."""
    # First, show the NLP status
    print("\n" + "="*60)
    print("Korean NLP System Status")
    print("="*60)
    print_status_report()
    
    # Run demos
    demos = [
        demo_basic_features,
        demo_spacing_correction,
        demo_formality_analysis,
        demo_reading_difficulty,
        demo_metadata_extraction
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\nError in {demo.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    main()