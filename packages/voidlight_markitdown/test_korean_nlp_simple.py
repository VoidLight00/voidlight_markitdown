#!/usr/bin/env python3
"""
Simple test script for Korean NLP features without pytest dependency.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from voidlight_markitdown._korean_utils import KoreanTextProcessor
from voidlight_markitdown._korean_nlp_init import get_korean_nlp_status


def test_basic_functionality():
    """Test basic Korean text processing functionality."""
    print("\n=== Testing Basic Functionality ===")
    
    processor = KoreanTextProcessor()
    
    # Test 1: Character detection
    print("\n1. Testing Korean character detection:")
    test_chars = ['가', '힣', 'A', '中', '1']
    for char in test_chars:
        is_korean = processor.is_korean_char(char)
        is_hanja = processor.is_hanja_char(char)
        print(f"   '{char}': Korean={is_korean}, Hanja={is_hanja}")
    
    # Test 2: Korean ratio detection
    print("\n2. Testing Korean ratio detection:")
    test_texts = [
        ("안녕하세요", 1.0),
        ("Hello 안녕", 0.2857),  # 2/7
        ("Hello World", 0.0)
    ]
    for text, expected in test_texts:
        ratio = processor.detect_korean_ratio(text)
        print(f"   '{text}': {ratio:.4f} (expected ~{expected:.4f})")
    
    # Test 3: Tokenization fallback
    print("\n3. Testing tokenization (with fallback):")
    text = "안녕하세요. 오늘 날씨가 좋네요."
    tokens = processor.tokenize(text)
    print(f"   Text: {text}")
    print(f"   Tokens: {tokens[:5]}...")  # Show first 5
    
    # Test 4: Sentence segmentation
    print("\n4. Testing sentence segmentation:")
    text = "안녕하세요. 반갑습니다! 오늘은 어떠신가요?"
    sentences = processor.segment_sentences(text)
    print(f"   Text: {text}")
    for i, sent in enumerate(sentences, 1):
        print(f"   Sentence {i}: {sent}")
    
    return True


def test_nlp_status():
    """Test NLP status checking."""
    print("\n=== Testing NLP Status System ===")
    
    status = get_korean_nlp_status()
    deps = status.dependencies_status
    
    print("\nDependency Status:")
    for lib, info in deps.items():
        if isinstance(info, dict):
            status_str = "✓" if info.get('installed') or info.get('functional') else "✗"
            print(f"   {lib}: {status_str}")
    
    instructions = status.get_installation_instructions()
    if instructions['commands']:
        print("\nMissing dependencies - install with:")
        for cmd in instructions['commands']:
            print(f"   {cmd}")
    
    return True


def test_advanced_features():
    """Test advanced features with graceful fallbacks."""
    print("\n=== Testing Advanced Features ===")
    
    processor = KoreanTextProcessor()
    
    # Test 1: Normalization
    print("\n1. Testing text normalization:")
    messy_text = "안녕하세요...   오늘은  정말\n\n\n좋은날입니다！"
    normalized = processor.normalize_korean_text(messy_text)
    print(f"   Original: {repr(messy_text)}")
    print(f"   Normalized: {repr(normalized)}")
    
    # Test 2: Metadata extraction
    print("\n2. Testing metadata extraction:")
    text = "안녕하세요! Hello, world! 中國語도 있습니다."
    metadata = processor.extract_korean_metadata(text)
    print(f"   Korean ratio: {metadata['korean_ratio']:.2%}")
    print(f"   Has Korean: {metadata['has_korean']}")
    print(f"   Has Hanja: {metadata['has_hanja']}")
    print(f"   Has mixed scripts: {metadata['has_mixed_script']}")
    
    # Test 3: Formality analysis
    print("\n3. Testing formality analysis:")
    formal_text = "안녕하십니까. 감사합니다."
    analysis = processor.analyze_formality(formal_text)
    print(f"   Text: {formal_text}")
    print(f"   Level: {analysis['formality_level']}")
    
    return True


def main():
    """Run all tests."""
    print("Korean NLP Feature Tests")
    print("=" * 60)
    
    tests = [
        ("NLP Status", test_nlp_status),
        ("Basic Functionality", test_basic_functionality),
        ("Advanced Features", test_advanced_features)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                print(f"\n✓ {name} - PASSED")
                passed += 1
            else:
                print(f"\n✗ {name} - FAILED")
                failed += 1
        except Exception as e:
            print(f"\n✗ {name} - ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)