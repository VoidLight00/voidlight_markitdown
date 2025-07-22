import re
import unicodedata
from typing import Optional, Dict, Any, List, Tuple
import logging

# Optional imports with fallbacks
try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False
    
try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False

try:
    from soynlp.normalizer import repeat_normalize
    from soynlp.word import WordExtractor
    SOYNLP_AVAILABLE = True
except ImportError:
    SOYNLP_AVAILABLE = False

try:
    from hanspell import spell_checker
    HANSPELL_AVAILABLE = True
except ImportError:
    HANSPELL_AVAILABLE = False

try:
    import jamo
    JAMO_AVAILABLE = True
except ImportError:
    JAMO_AVAILABLE = False

try:
    import hanja
    HANJA_AVAILABLE = True
except ImportError:
    HANJA_AVAILABLE = False


logger = logging.getLogger(__name__)


class KoreanTextProcessor:
    """Enhanced Korean text processing utilities with NLP library integration."""
    
    # Korean Unicode blocks
    HANGUL_SYLLABLES = (0xAC00, 0xD7A3)
    HANGUL_JAMO = (0x1100, 0x11FF)
    HANGUL_COMPATIBILITY_JAMO = (0x3130, 0x318F)
    HANGUL_JAMO_EXTENDED_A = (0xA960, 0xA97F)
    HANGUL_JAMO_EXTENDED_B = (0xD7B0, 0xD7FF)
    
    # CJK Unified Ideographs (Hanja)
    CJK_UNIFIED = (0x4E00, 0x9FFF)
    CJK_EXTENSION_A = (0x3400, 0x4DBF)
    CJK_COMPATIBILITY = (0xF900, 0xFAFF)
    
    # Common Korean encoding mappings
    ENCODING_PRIORITY = [
        'utf-8',
        'cp949',
        'euc-kr',
        'johab',
        'iso2022_kr',
        'utf-16',
        'utf-16-le',
        'utf-16-be'
    ]
    
    def __init__(self):
        """Initialize Korean text processor with available NLP tools."""
        self.kiwi = None
        self.okt = None
        
        # Initialize Kiwi if available (preferred for performance)
        if KIWI_AVAILABLE:
            try:
                self.kiwi = Kiwi(num_workers=2)
                # Add common proper nouns and terms
                self._add_kiwi_user_words()
                logger.info("Kiwi tokenizer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Kiwi: {e}")
                self.kiwi = None
        
        # Fallback to KoNLPy if Kiwi is not available
        if not self.kiwi and KONLPY_AVAILABLE:
            try:
                self.okt = Okt()
                logger.info("Okt tokenizer initialized as fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize Okt: {e}")
                self.okt = None
    
    def _add_kiwi_user_words(self):
        """Add common user words to Kiwi dictionary."""
        if not self.kiwi:
            return
            
        # Common IT/technical terms
        tech_terms = [
            ('인공지능', 'NNP'),
            ('머신러닝', 'NNP'),
            ('딥러닝', 'NNP'),
            ('빅데이터', 'NNP'),
            ('블록체인', 'NNP'),
            ('클라우드', 'NNP'),
            ('데이터베이스', 'NNP'),
            ('알고리즘', 'NNP'),
        ]
        
        for word, tag in tech_terms:
            try:
                self.kiwi.add_user_word(word, tag)
            except:
                pass
    
    @staticmethod
    def is_korean_char(char: str) -> bool:
        """Check if a character is Korean (Hangul)."""
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
    def is_hanja_char(char: str) -> bool:
        """Check if a character is Hanja (Chinese character used in Korean)."""
        if not char:
            return False
        
        code = ord(char[0])
        
        return (
            (KoreanTextProcessor.CJK_UNIFIED[0] <= code <= KoreanTextProcessor.CJK_UNIFIED[1]) or
            (KoreanTextProcessor.CJK_EXTENSION_A[0] <= code <= KoreanTextProcessor.CJK_EXTENSION_A[1]) or
            (KoreanTextProcessor.CJK_COMPATIBILITY[0] <= code <= KoreanTextProcessor.CJK_COMPATIBILITY[1])
        )
    
    @staticmethod
    def detect_korean_ratio(text: str) -> float:
        """Calculate the ratio of Korean characters in the text."""
        if not text:
            return 0.0
        
        korean_chars = sum(1 for char in text if KoreanTextProcessor.is_korean_char(char))
        total_chars = len(text)
        
        return korean_chars / total_chars if total_chars > 0 else 0.0
    
    def normalize_korean_text(self, text: str) -> str:
        """Normalize Korean text for better processing.
        
        - Normalize Unicode (NFC)
        - Fix common encoding issues
        - Normalize whitespace
        - Remove zero-width characters
        - Apply spell checking if available
        """
        if not text:
            return text
        
        # Step 1: Normalize to NFC form
        text = unicodedata.normalize('NFC', text)
        
        # Step 2: Remove zero-width characters
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        
        # Step 3: Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\u00A0\u1680\u180E\u2000-\u200A\u202F\u205F\u3000]', ' ', text)
        
        # Step 4: Fix common mojibake patterns
        mojibake_patterns = {
            '占쏙옙': '?',  # Common replacement for unknown characters
            '�': '?',      # Unicode replacement character
            '째': 'ㅉ',     # Common misencoding
            '찮': 'ㅊ',     # Common misencoding
        }
        
        for pattern, replacement in mojibake_patterns.items():
            text = text.replace(pattern, replacement)
        
        # Step 5: Normalize repeated characters if soynlp is available
        if SOYNLP_AVAILABLE:
            try:
                text = repeat_normalize(text, num_repeats=2)
            except:
                pass
        
        # Step 6: Apply spell checking if available and text is not too long
        if HANSPELL_AVAILABLE and len(text) < 500:
            try:
                result = spell_checker.check(text)
                if result.checked:
                    text = result.checked
            except:
                pass
        
        # Step 7: Decompose and recompose Hangul if jamo is available
        if JAMO_AVAILABLE:
            try:
                # This helps normalize old-style Korean text
                decomposed = jamo.h2j(text)
                text = jamo.j2h(decomposed)
            except:
                pass
        
        return text.strip()
    
    def fix_korean_line_breaks(self, text: str) -> str:
        """Fix line break issues in Korean text.
        
        Korean text sometimes has inappropriate line breaks in the middle of sentences.
        """
        if not text:
            return text
        
        # Remove line breaks between Korean characters unless followed by punctuation
        # Korean sentence endings
        sentence_endings = '。.!?！？…'
        
        # Pattern: Korean char + newline + Korean char (not after sentence ending)
        def replace_break(match):
            prev_char = match.group(1)
            next_char = match.group(2)
            
            # Keep line break if previous character is a sentence ending
            if prev_char in sentence_endings:
                return match.group(0)
            
            # Otherwise replace with space
            return prev_char + ' ' + next_char
        
        text = re.sub(
            r'([가-힣])\n([가-힣])',
            replace_break,
            text
        )
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def tokenize(self, text: str) -> List[Tuple[str, str]]:
        """Tokenize Korean text with POS tagging.
        
        Returns list of (token, pos_tag) tuples.
        """
        if self.kiwi:
            try:
                result = self.kiwi.tokenize(text)
                return [(token.form, token.tag) for token in result]
            except:
                pass
        
        if self.okt:
            try:
                return self.okt.pos(text)
            except:
                pass
        
        # Fallback: simple whitespace tokenization
        return [(token, 'UNK') for token in text.split()]
    
    def extract_nouns(self, text: str) -> List[str]:
        """Extract nouns from Korean text."""
        if self.kiwi:
            try:
                result = self.kiwi.tokenize(text)
                return [token.form for token in result if token.tag.startswith('N')]
            except:
                pass
        
        if self.okt:
            try:
                return self.okt.nouns(text)
            except:
                pass
        
        # Fallback: return empty list
        return []
    
    def convert_hanja_to_hangul(self, text: str) -> str:
        """Convert Hanja (Chinese characters) to Hangul if possible."""
        if not HANJA_AVAILABLE:
            return text
        
        try:
            # Convert character by character
            result = []
            for char in text:
                if self.is_hanja_char(char):
                    try:
                        hangul = hanja.translate(char, 'substitution')
                        result.append(hangul if hangul != char else char)
                    except:
                        result.append(char)
                else:
                    result.append(char)
            
            return ''.join(result)
        except:
            return text
    
    def extract_korean_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata about Korean text content."""
        metadata = {
            'korean_ratio': self.detect_korean_ratio(text),
            'has_korean': False,
            'has_hanja': False,
            'has_mixed_script': False,
            'detected_encoding_issues': False,
            'char_count': len(text),
            'word_count': 0,
            'sentence_count': 0,
            'noun_count': 0,
        }
        
        if metadata['korean_ratio'] > 0:
            metadata['has_korean'] = True
        
        # Check for Hanja
        hanja_chars = sum(1 for char in text if self.is_hanja_char(char))
        if hanja_chars > 0:
            metadata['has_hanja'] = True
            metadata['hanja_ratio'] = hanja_chars / len(text) if len(text) > 0 else 0
        
        # Check for mixed scripts
        if metadata['has_korean'] and re.search(r'[a-zA-Z]', text):
            metadata['has_mixed_script'] = True
        
        # Check for potential encoding issues
        if re.search(r'[�占쏙옙]', text) or '?' * 3 in text:
            metadata['detected_encoding_issues'] = True
        
        # Count sentences (Korean sentence endings)
        sentence_endings = r'[.!?。！？…]\s*'
        metadata['sentence_count'] = len(re.findall(sentence_endings, text))
        
        # Tokenize and count words/nouns
        if self.kiwi or self.okt:
            tokens = self.tokenize(text)
            metadata['word_count'] = len(tokens)
            
            nouns = self.extract_nouns(text)
            metadata['noun_count'] = len(nouns)
            
            # Get top nouns
            if nouns:
                noun_freq = {}
                for noun in nouns:
                    noun_freq[noun] = noun_freq.get(noun, 0) + 1
                
                top_nouns = sorted(noun_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                metadata['top_nouns'] = [noun for noun, _ in top_nouns]
        else:
            # Fallback word count
            metadata['word_count'] = len(text.split())
        
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
                    # Additional check: if it's supposed to be Korean, verify Korean content
                    if KoreanTextProcessor.detect_korean_ratio(decoded) > 0.1:
                        return decoded
                    elif not any(ord(c) > 127 for c in decoded):
                        # Pure ASCII is likely correct
                        return decoded
            except (UnicodeDecodeError, LookupError):
                continue
        
        # If no encoding worked perfectly, try again with error handling
        for encoding in KoreanTextProcessor.ENCODING_PRIORITY:
            try:
                decoded = data.decode(encoding, errors='replace')
                return decoded
            except LookupError:
                continue
        
        # Final fallback
        return data.decode('utf-8', errors='replace')
    
    def preprocess_korean_document(self, text: str, normalize: bool = True) -> str:
        """Preprocess Korean document for better conversion."""
        if not text:
            return text
        
        # Fix line breaks
        text = self.fix_korean_line_breaks(text)
        
        # Normalize if requested
        if normalize:
            text = self.normalize_korean_text(text)
        
        # Convert Hanja to Hangul if configured
        # (This is optional and depends on use case)
        # text = self.convert_hanja_to_hangul(text)
        
        return text
    
    def segment_sentences(self, text: str) -> List[str]:
        """Segment Korean text into sentences."""
        if self.kiwi:
            try:
                # Kiwi has built-in sentence segmentation
                result = self.kiwi.split_into_sents(text)
                return [sent.text for sent in result]
            except:
                pass
        
        # Fallback: simple rule-based segmentation
        # Korean sentence endings
        sentence_endings = r'([.!?。！？…])\s*'
        
        sentences = re.split(sentence_endings, text)
        
        # Reconstruct sentences with their endings
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sent = sentences[i] + sentences[i + 1]
                sent = sent.strip()
                if sent:
                    result.append(sent)
        
        # Add last sentence if it doesn't have an ending
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return result if result else [text]
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords from Korean text with importance scores."""
        if not text:
            return []
        
        # Extract nouns as potential keywords
        nouns = self.extract_nouns(text)
        if not nouns:
            return []
        
        # Count frequency
        noun_freq = {}
        for noun in nouns:
            # Skip single character nouns unless they're meaningful
            if len(noun) == 1 and not self.is_hanja_char(noun):
                continue
            noun_freq[noun] = noun_freq.get(noun, 0) + 1
        
        # Calculate TF scores
        total_nouns = len(nouns)
        tf_scores = {noun: freq / total_nouns for noun, freq in noun_freq.items()}
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:num_keywords]