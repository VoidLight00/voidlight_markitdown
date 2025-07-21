import re
import unicodedata
from typing import Optional, Dict, Any


class KoreanTextProcessor:
    """Enhanced Korean text processing utilities."""
    
    # Korean Unicode blocks
    HANGUL_SYLLABLES = (0xAC00, 0xD7A3)
    HANGUL_JAMO = (0x1100, 0x11FF)
    HANGUL_COMPATIBILITY_JAMO = (0x3130, 0x318F)
    HANGUL_JAMO_EXTENDED_A = (0xA960, 0xA97F)
    HANGUL_JAMO_EXTENDED_B = (0xD7B0, 0xD7FF)
    
    # Common Korean encoding mappings
    ENCODING_PRIORITY = [
        'utf-8',
        'euc-kr',
        'cp949',
        'johab',
        'iso2022_kr',
        'utf-16',
        'utf-16-le',
        'utf-16-be'
    ]
    
    @staticmethod
    def is_korean_char(char: str) -> bool:
        """Check if a character is Korean."""
        if not char:
            return False
        
        code = ord(char[0])
        
        # Check various Korean Unicode blocks
        return (
            (KoreanTextProcessor.HANGUL_SYLLABLES[0] <= code <= KoreanTextProcessor.HANGUL_SYLLABLES[1]) or
            (KoreanTextProcessor.HANGUL_JAMO[0] <= code <= KoreanTextProcessor.HANGUL_JAMO[1]) or
            (KoreanTextProcessor.HANGUL_COMPATIBILITY_JAMO[0] <= code <= KoreanTextProcessor.HANGUL_COMPATIBILITY_JAMO[1]) or
            (KoreanTextProcessor.HANGUL_JAMO_EXTENDED_A[0] <= code <= KoreanTextProcessor.HANGUL_JAMO_EXTENDED_A[1]) or
            (KoreanTextProcessor.HANGUL_JAMO_EXTENDED_B[0] <= code <= KoreanTextProcessor.HANGUL_JAMO_EXTENDED_B[1])
        )
    
    @staticmethod
    def detect_korean_ratio(text: str) -> float:
        """Calculate the ratio of Korean characters in the text."""
        if not text:
            return 0.0
        
        korean_chars = sum(1 for char in text if KoreanTextProcessor.is_korean_char(char))
        total_chars = len(text)
        
        return korean_chars / total_chars if total_chars > 0 else 0.0
    
    @staticmethod
    def normalize_korean_text(text: str) -> str:
        """Normalize Korean text for better processing.
        
        - Normalize Unicode (NFC)
        - Fix common encoding issues
        - Normalize whitespace
        - Remove zero-width characters
        """
        if not text:
            return text
        
        # Normalize to NFC form
        text = unicodedata.normalize('NFC', text)
        
        # Remove zero-width characters
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\u00A0\u1680\u180E\u2000-\u200A\u202F\u205F\u3000]', ' ', text)
        
        # Fix common mojibake patterns
        mojibake_patterns = {
            '占쏙옙': '?',  # Common replacement for unknown characters
            '�': '?',      # Unicode replacement character
        }
        
        for pattern, replacement in mojibake_patterns.items():
            text = text.replace(pattern, replacement)
        
        return text.strip()
    
    @staticmethod
    def fix_korean_line_breaks(text: str) -> str:
        """Fix line break issues in Korean text.
        
        Korean text sometimes has inappropriate line breaks in the middle of sentences.
        """
        if not text:
            return text
        
        # Remove line breaks between Korean characters unless followed by punctuation
        text = re.sub(
            r'([가-힣])\n([가-힣])',
            r'\1 \2',
            text
        )
        
        # Preserve line breaks after Korean punctuation
        korean_punctuation = '。、·‥…｡､･‥…'
        text = re.sub(
            f'([{korean_punctuation}])\n',
            r'\1\n',
            text
        )
        
        return text
    
    @staticmethod
    def extract_korean_metadata(text: str) -> Dict[str, Any]:
        """Extract metadata about Korean text content."""
        metadata = {
            'korean_ratio': KoreanTextProcessor.detect_korean_ratio(text),
            'has_korean': False,
            'has_hanja': False,
            'has_mixed_script': False,
            'detected_encoding_issues': False
        }
        
        if metadata['korean_ratio'] > 0:
            metadata['has_korean'] = True
        
        # Check for Hanja (Chinese characters used in Korean)
        hanja_pattern = r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]'
        if re.search(hanja_pattern, text):
            metadata['has_hanja'] = True
        
        # Check for mixed scripts
        if metadata['has_korean'] and re.search(r'[a-zA-Z]', text):
            metadata['has_mixed_script'] = True
        
        # Check for potential encoding issues
        if re.search(r'[�占쏙옙]', text):
            metadata['detected_encoding_issues'] = True
        
        return metadata
    
    @staticmethod
    def smart_decode(data: bytes) -> str:
        """Smart decode bytes with Korean encoding detection."""
        # Try encodings in priority order
        for encoding in KoreanTextProcessor.ENCODING_PRIORITY:
            try:
                decoded = data.decode(encoding)
                # Verify the decoding by checking for replacement characters
                if '�' not in decoded and '占쏙옙' not in decoded:
                    return decoded
            except (UnicodeDecodeError, LookupError):
                continue
        
        # Fallback to UTF-8 with error handling
        return data.decode('utf-8', errors='replace')
    
    @staticmethod
    def preprocess_korean_document(text: str, normalize: bool = True) -> str:
        """Preprocess Korean document for better conversion."""
        if not text:
            return text
        
        # Fix line breaks
        text = KoreanTextProcessor.fix_korean_line_breaks(text)
        
        # Normalize if requested
        if normalize:
            text = KoreanTextProcessor.normalize_korean_text(text)
        
        return text