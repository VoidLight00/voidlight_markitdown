"""Korean text processing utilities for voidlight_markitdown."""

import re
import unicodedata
from typing import Optional, Dict, Any, List, Tuple
from .nlp import get_korean_nlp_status
from ..utils.logging import get_logger, LoggingMixin, log_performance

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


class KoreanTextProcessor(LoggingMixin):
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
        self.nlp_status = get_korean_nlp_status()
        
        self.log_info("Initializing Korean text processor")
        
        # Initialize Kiwi if available (preferred for performance)
        if KIWI_AVAILABLE:
            try:
                self.kiwi = Kiwi(num_workers=2)
                # Add common proper nouns and terms
                self._add_kiwi_user_words()
                self.log_info("Kiwi tokenizer initialized successfully")
            except Exception as e:
                self.log_warning(f"Failed to initialize Kiwi: {e}", exc_info=True)
                self.kiwi = None
        
        # Fallback to KoNLPy if Kiwi is not available
        if not self.kiwi and KONLPY_AVAILABLE:
            try:
                # Check if Java dependencies are met
                if self.nlp_status.dependencies_status['konlpy'].get('functional', False):
                    self.okt = Okt()
                    self.log_info("Okt tokenizer initialized as fallback")
                else:
                    self.log_warning("KoNLPy available but Java dependencies not met")
            except Exception as e:
                self.log_warning(f"Failed to initialize Okt: {e}", exc_info=True)
                self.okt = None
        
        # Log initialization status
        self._log_initialization_status()
    
    def _log_initialization_status(self):
        """Log the initialization status of Korean NLP components."""
        status_parts = []
        
        if self.kiwi:
            status_parts.append("Kiwi")
        if self.okt:
            status_parts.append("Okt")
            
        if status_parts:
            self.log_info(f"Korean NLP initialized with: {', '.join(status_parts)}")
        else:
            self.log_warning("No Korean NLP tokenizers available - using fallback methods")
            
        # Log optional components
        optional_status = []
        if SOYNLP_AVAILABLE:
            optional_status.append("soynlp")
        if HANSPELL_AVAILABLE:
            optional_status.append("hanspell")
        if JAMO_AVAILABLE:
            optional_status.append("jamo")
        if HANJA_AVAILABLE:
            optional_status.append("hanja")
            
        if optional_status:
            self.log_debug(f"Optional Korean modules available: {', '.join(optional_status)}")
    
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
                self.kiwi.add_user_word(word, tag, 5.0)  # Add with default score
            except Exception as e:
                self.log_debug(f"Failed to add user word '{word}': {e}")
    
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
        
        with log_performance(self.logger, "normalize_korean_text", text_length=len(text)):
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
    
    def tokenize(self, text: str, normalize: bool = True) -> List[Tuple[str, str]]:
        """Tokenize Korean text with POS tagging.
        
        Args:
            text: Text to tokenize
            normalize: Whether to normalize text before tokenization
            
        Returns:
            List of (token, pos_tag) tuples.
        """
        if not text:
            return []
            
        if normalize:
            text = self.normalize_korean_text(text)
            
        if self.kiwi:
            try:
                result = self.kiwi.tokenize(text)
                return [(token.form, token.tag) for token in result]
            except Exception as e:
                self.log_debug(f"Kiwi tokenization failed: {e}")
        
        if self.okt:
            try:
                return self.okt.pos(text, norm=normalize, stem=False)
            except Exception as e:
                self.log_debug(f"Okt tokenization failed: {e}")
        
        # Fallback: simple whitespace tokenization with basic POS guessing
        tokens = []
        for token in text.split():
            if self.is_korean_char(token[0] if token else ''):
                # Basic POS tagging for Korean
                if token.endswith(('다', '요', '니다', '습니다')):
                    pos = 'VV'  # Verb
                elif token.endswith(('은', '는', '이', '가', '을', '를')):
                    pos = 'JK'  # Particle
                else:
                    pos = 'NN'  # Noun (default)
            else:
                pos = 'SL' if re.match(r'^[a-zA-Z]+$', token) else 'SY'
            tokens.append((token, pos))
        
        return tokens
    
    def extract_nouns(self, text: str) -> List[str]:
        """Extract nouns from Korean text."""
        if not text:
            return []
            
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
        if not text:
            return ['']
            
        if self.kiwi:
            try:
                # Kiwi has built-in sentence segmentation
                result = self.kiwi.split_into_sents(text)
                return [sent.text for sent in result]
            except Exception as e:
                self.log_debug(f"Kiwi sentence segmentation failed: {e}")
        
        # Enhanced rule-based segmentation
        # Korean sentence endings with context
        sentence_endings = r'([.!?。！？…])\s*'
        
        # Special handling for quotes and parentheses
        text = re.sub(r'([.!?。！？…])(["\'])\s*', r'\1\2\n', text)
        
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
    
    def correct_spacing(self, text: str) -> str:
        """Correct spacing in Korean text using available NLP tools.
        
        Korean text often has spacing issues that need correction.
        """
        if not text:
            return text
            
        if self.kiwi:
            try:
                # Kiwi has built-in spacing correction
                result = self.kiwi.space(text)
                if result and hasattr(result, 'text'):
                    return result.text
                elif isinstance(result, str):
                    return result
            except Exception as e:
                self.log_debug(f"Kiwi spacing correction failed: {e}")
        
        # Fallback: No spacing correction available
        self.log_debug("No spacing correction available, returning original text")
        return text
    
    def get_morphemes(self, text: str) -> List[Dict[str, str]]:
        """Extract morphemes from Korean text.
        
        Returns:
            List of dicts with 'surface', 'pos', and 'lemma' keys.
        """
        morphemes = []
        
        if self.kiwi:
            try:
                result = self.kiwi.tokenize(text)
                for token in result:
                    morphemes.append({
                        'surface': token.form,
                        'pos': token.tag,
                        'lemma': token.form,  # Kiwi doesn't provide lemma directly
                        'start': token.start,
                        'end': token.end
                    })
                return morphemes
            except Exception as e:
                self.log_debug(f"Kiwi morpheme extraction failed: {e}")
        
        if self.okt:
            try:
                # Get morphemes with normalization
                result = self.okt.morphs(text, stem=True)
                pos_result = self.okt.pos(text, stem=True)
                
                # Combine morpheme and POS information
                for i, (morph, pos) in enumerate(pos_result):
                    morphemes.append({
                        'surface': morph,
                        'pos': pos,
                        'lemma': morph,  # Okt returns stemmed form
                        'start': -1,  # Okt doesn't provide positions
                        'end': -1
                    })
                return morphemes
            except Exception as e:
                self.log_debug(f"Okt morpheme extraction failed: {e}")
        
        # Fallback: Basic tokenization
        tokens = self.tokenize(text)
        for i, (token, pos) in enumerate(tokens):
            morphemes.append({
                'surface': token,
                'pos': pos,
                'lemma': token,
                'start': -1,
                'end': -1
            })
        
        return morphemes
    
    def analyze_formality(self, text: str) -> Dict[str, Any]:
        """Analyze the formality level of Korean text.
        
        Returns dict with formality indicators.
        """
        analysis = {
            'formality_level': 'unknown',
            'honorific_count': 0,
            'formal_endings': 0,
            'informal_endings': 0,
            'polite_particles': 0
        }
        
        # Formal endings
        formal_patterns = [
            r'습니다$',  # 습니다
            r'입니다$',  # 입니다
            r'습니까$',  # 습니까
            r'입니까$',  # 입니까
            r'세요$',    # 세요
            r'어요$',    # 어요
            r'아요$',    # 아요
            r'십니까$',  # 십니까
            r'십니다$'   # 십니다
        ]
        
        # Informal endings
        informal_patterns = [
            r'다$',      # 다 (but not 니다)
            r'냐$',      # 냐
            r'어$',      # 어
            r'아$',      # 아
            r'지$',      # 지
            r'야$',      # 야
            r'네$',      # 네
            r'군$',      # 군
            r'구나$',    # 구나
            r'자$',      # 자
            r'라$'       # 라
        ]
        
        # Honorific words
        honorific_words = [
            '님',        # 님
            '께서',      # 께서
            '드리다',    # 드리다
            '모시다',    # 모시다
            '여쭙다',    # 여쭙다
            '주시',      # 주시
            '하십',      # 하십
            '셔서'       # 셔서
        ]
        
        # Analyze sentences
        sentences = self.segment_sentences(text)
        
        for sentence in sentences:
            # Remove punctuation for ending analysis
            sentence_clean = sentence.rstrip('.!?。！？…')
            
            # Check formal endings
            for pattern in formal_patterns:
                if re.search(pattern, sentence_clean):
                    analysis['formal_endings'] += 1
                    break
            
            # Check informal endings - but exclude formal endings that contain 다
            is_formal = False
            for pattern in formal_patterns:
                if re.search(pattern, sentence_clean):
                    is_formal = True
                    break
            
            if not is_formal:
                for pattern in informal_patterns:
                    if re.search(pattern, sentence_clean):
                        analysis['informal_endings'] += 1
                        break
            
            # Count honorifics
            for honorific in honorific_words:
                analysis['honorific_count'] += sentence.count(honorific)
        
        # Determine overall formality level
        total_sentences = len(sentences)
        if total_sentences > 0:
            formal_ratio = analysis['formal_endings'] / total_sentences
            
            if formal_ratio > 0.7:
                analysis['formality_level'] = 'formal'
            elif formal_ratio > 0.3:
                analysis['formality_level'] = 'polite'
            else:
                analysis['formality_level'] = 'informal'
        
        return analysis
    
    def get_reading_difficulty(self, text: str) -> Dict[str, Any]:
        """Estimate reading difficulty of Korean text.
        
        Returns dict with difficulty metrics.
        """
        difficulty = {
            'level': 'unknown',
            'avg_word_length': 0,
            'avg_sentence_length': 0,
            'hanja_ratio': 0,
            'complex_word_ratio': 0,
            'unique_word_ratio': 0
        }
        
        # Get basic metrics
        metadata = self.extract_korean_metadata(text)
        difficulty['hanja_ratio'] = metadata.get('hanja_ratio', 0)
        
        # Sentence analysis
        sentences = self.segment_sentences(text)
        if sentences:
            words_per_sentence = []
            for sent in sentences:
                tokens = self.tokenize(sent)
                # Count only content words (not particles)
                content_words = [t for t, pos in tokens if not pos.startswith('J')]
                words_per_sentence.append(len(content_words))
            
            difficulty['avg_sentence_length'] = sum(words_per_sentence) / len(words_per_sentence)
        
        # Word analysis
        tokens = self.tokenize(text)
        if tokens:
            words = [token for token, pos in tokens if not pos.startswith('J')]
            if words:
                # Average word length
                difficulty['avg_word_length'] = sum(len(w) for w in words) / len(words)
                
                # Unique word ratio
                unique_words = set(words)
                difficulty['unique_word_ratio'] = len(unique_words) / len(words)
                
                # Complex words (3+ syllables)
                complex_words = [w for w in words if len(w) >= 3]
                difficulty['complex_word_ratio'] = len(complex_words) / len(words)
        
        # Estimate difficulty level
        score = 0
        
        # Sentence length factor
        if difficulty['avg_sentence_length'] > 15:
            score += 2
        elif difficulty['avg_sentence_length'] > 10:
            score += 1
        
        # Word complexity factor
        if difficulty['complex_word_ratio'] > 0.3:
            score += 2
        elif difficulty['complex_word_ratio'] > 0.2:
            score += 1
        
        # Hanja factor
        if difficulty['hanja_ratio'] > 0.1:
            score += 2
        elif difficulty['hanja_ratio'] > 0.05:
            score += 1
        
        # Determine level
        if score >= 4:
            difficulty['level'] = 'advanced'
        elif score >= 2:
            difficulty['level'] = 'intermediate'
        else:
            difficulty['level'] = 'beginner'
        
        return difficulty


# Aliases for backward compatibility
def is_korean_text(text: str, threshold: float = 0.3) -> bool:
    """Check if text contains Korean characters above a certain threshold."""
    return KoreanTextProcessor.detect_korean_ratio(text) >= threshold


def extract_korean_keywords(text: str, num_keywords: int = 10) -> List[str]:
    """Extract keywords from Korean text (simplified API)."""
    processor = KoreanTextProcessor()
    keywords = processor.extract_keywords(text, num_keywords)
    return [keyword for keyword, _ in keywords]