#!/usr/bin/env python3
"""Test Korean NLP functionality with actual libraries."""

from voidlight_markitdown import VoidLightMarkItDown
from voidlight_markitdown._korean_utils import KoreanTextProcessor
import tempfile
import os

print("=== Testing Korean NLP Functionality ===\n")

# Initialize Korean text processor
ktp = KoreanTextProcessor()

# Check available NLP libraries
print("1. Checking Available NLP Libraries:")
print(f"   - KoNLPy available: {'konlpy' in str(ktp.__dict__)}")
print(f"   - Kiwipiepy available: {hasattr(ktp, '_kiwi')}")
print(f"   - Soynlp available: {hasattr(ktp, '_word_extractor')}")
print(f"   - Hanja available: {hasattr(ktp, '_hanja_to_hangul')}")

# Test Korean text samples
test_texts = [
    "안녕하세요. 이것은 한국어 테스트입니다.",
    "대한민국의 수도는 서울입니다.",
    "인공지능 기술이 빠르게 발전하고 있습니다.",
    "漢字도 한글로 변환할 수 있습니다.",
    "띄어쓰기가잘못된문장도처리할수있습니다.",
]

print("\n2. Testing Text Processing Features:")

for i, text in enumerate(test_texts, 1):
    print(f"\n   Test {i}: {text}")
    
    # Test tokenization
    try:
        tokens = ktp.tokenize(text, normalize=True)
        print(f"   - Tokens: {tokens[:5]}..." if len(tokens) > 5 else f"   - Tokens: {tokens}")
    except Exception as e:
        print(f"   - Tokenization error: {e}")
    
    # Test noun extraction
    try:
        nouns = ktp.extract_nouns(text)
        print(f"   - Nouns: {nouns}")
    except Exception as e:
        print(f"   - Noun extraction error: {e}")
    
    # Test keyword extraction
    try:
        keywords = ktp.extract_keywords(text, num_keywords=3)
        print(f"   - Keywords: {keywords}")
    except Exception as e:
        print(f"   - Keyword extraction error: {e}")

# Test document conversion with Korean mode
print("\n3. Testing Document Conversion with Korean Mode:")

md_korean = VoidLightMarkItDown(korean_mode=True)

# Create test documents
test_docs = [
    ("korean_text.txt", "한국어 문서 테스트\n\n이것은 한국어로 작성된 문서입니다.\n여러 줄의 텍스트가 포함되어 있습니다."),
    ("mixed_text.txt", "English and 한국어 Mixed Document\n\n이 문서는 영어와 한국어가 섞여 있습니다.\nThis document contains both English and Korean text."),
    ("technical_korean.txt", "인공지능(AI) 기술 동향\n\n머신러닝과 딥러닝 기술이 발전하면서\n자연어 처리(NLP) 분야도 큰 진전을 이루고 있습니다."),
]

for filename, content in test_docs:
    print(f"\n   Converting {filename}:")
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            result = md_korean.convert(f.name)
            os.unlink(f.name)
            
            # Show first 100 chars of result
            preview = result.markdown[:100] + "..." if len(result.markdown) > 100 else result.markdown
            print(f"   - Result: {preview}")
            
            # Check if Korean metadata was extracted
            if hasattr(result, 'metadata') and result.metadata:
                print(f"   - Metadata: {result.metadata}")
    except Exception as e:
        print(f"   - Error: {e}")

# Test specific Korean NLP features
print("\n4. Testing Advanced Korean NLP Features:")

# Test spacing correction
print("\n   Spacing Correction:")
test_spacing = "띄어쓰기가잘못된문장입니다"
try:
    # The method is called fix_korean_line_breaks, not fix_korean_spacing
    # For spacing, we'd need to use the tokenizer with morpheme analysis
    tokens = ktp.tokenize(test_spacing)
    print(f"   - Original: {test_spacing}")
    print(f"   - Tokens: {tokens}")
except Exception as e:
    print(f"   - Error: {e}")

# Test sentence segmentation
print("\n   Sentence Segmentation:")
test_paragraph = "첫 번째 문장입니다. 두 번째 문장이에요! 세 번째 문장은 어떨까요? 네 번째 문장."
try:
    sentences = ktp.segment_sentences(test_paragraph)
    for i, sent in enumerate(sentences, 1):
        print(f"   - Sentence {i}: {sent}")
except Exception as e:
    print(f"   - Error: {e}")

# Test Hanja conversion
print("\n   Hanja to Hangul Conversion:")
test_hanja = "大韓民國"
try:
    hangul = ktp.convert_hanja_to_hangul(test_hanja)
    print(f"   - Hanja: {test_hanja}")
    print(f"   - Hangul: {hangul}")
except Exception as e:
    print(f"   - Error: {e}")

print("\n=== Korean NLP Testing Complete ===")

# Check if Java is available for KoNLPy
print("\n5. System Requirements Check:")
import subprocess
try:
    java_version = subprocess.run(['java', '-version'], capture_output=True, text=True)
    if java_version.returncode == 0:
        print("   ✓ Java is installed (required for KoNLPy)")
    else:
        print("   ✗ Java not found (required for KoNLPy)")
except:
    print("   ✗ Java not found (required for KoNLPy)")

# Check Python package installations
print("\n   Python packages:")
packages = ['konlpy', 'kiwipiepy', 'soynlp', 'jamo', 'hanja']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"   ✓ {pkg} installed")
    except ImportError:
        print(f"   ✗ {pkg} not installed")