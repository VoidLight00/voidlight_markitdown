"""Korean language processing functionality for voidlight_markitdown."""

from .utils import extract_korean_keywords, is_korean_text
from .nlp import init_korean_nlp

__all__ = [
    "extract_korean_keywords",
    "is_korean_text",
    "init_korean_nlp",
]