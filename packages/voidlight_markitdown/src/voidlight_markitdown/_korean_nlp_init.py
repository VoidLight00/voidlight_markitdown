"""
Korean NLP library initialization and status checking.

This module provides utilities to check the status of Korean NLP libraries
and their dependencies.
"""

import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class KoreanNLPStatus:
    """Status of Korean NLP libraries and dependencies."""
    dependencies_status: Dict[str, Dict[str, Any]]
    java_available: bool
    java_version: Optional[str]
    recommendations: list


def check_java_installation() -> tuple[bool, Optional[str]]:
    """Check if Java is installed and get version."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            # Java version is typically in stderr
            version_output = result.stderr or result.stdout
            # Extract version from output
            lines = version_output.strip().split('\n')
            if lines:
                return True, lines[0]
        return False, None
    except FileNotFoundError:
        return False, None
    except Exception:
        return False, None


def check_konlpy_functional() -> bool:
    """Check if KoNLPy is functional (Java dependencies met)."""
    try:
        from konlpy.tag import Okt
        okt = Okt()
        # Try a simple operation
        okt.pos("테스트")
        return True
    except Exception:
        return False


def get_korean_nlp_status() -> KoreanNLPStatus:
    """Get comprehensive status of Korean NLP libraries."""
    java_available, java_version = check_java_installation()
    
    dependencies_status = {
        'kiwipiepy': {
            'installed': False,
            'functional': False,
            'error': None
        },
        'konlpy': {
            'installed': False,
            'functional': False,
            'error': None,
            'java_required': True
        },
        'soynlp': {
            'installed': False,
            'functional': False,
            'error': None
        },
        'hanspell': {
            'installed': False,
            'functional': False,
            'error': None
        },
        'jamo': {
            'installed': False,
            'functional': False,
            'error': None
        },
        'hanja': {
            'installed': False,
            'functional': False,
            'error': None
        }
    }
    
    # Check kiwipiepy
    try:
        import kiwipiepy
        dependencies_status['kiwipiepy']['installed'] = True
        try:
            from kiwipiepy import Kiwi
            kiwi = Kiwi()
            dependencies_status['kiwipiepy']['functional'] = True
        except Exception as e:
            dependencies_status['kiwipiepy']['error'] = str(e)
    except ImportError:
        pass
    
    # Check konlpy
    try:
        import konlpy
        dependencies_status['konlpy']['installed'] = True
        if java_available:
            dependencies_status['konlpy']['functional'] = check_konlpy_functional()
        else:
            dependencies_status['konlpy']['error'] = "Java not found"
    except ImportError:
        pass
    
    # Check soynlp
    try:
        import soynlp
        dependencies_status['soynlp']['installed'] = True
        dependencies_status['soynlp']['functional'] = True
    except ImportError:
        pass
    
    # Check hanspell
    try:
        import hanspell
        dependencies_status['hanspell']['installed'] = True
        dependencies_status['hanspell']['functional'] = True
    except ImportError:
        pass
    
    # Check jamo
    try:
        import jamo
        dependencies_status['jamo']['installed'] = True
        dependencies_status['jamo']['functional'] = True
    except ImportError:
        pass
    
    # Check hanja
    try:
        import hanja
        dependencies_status['hanja']['installed'] = True
        dependencies_status['hanja']['functional'] = True
    except ImportError:
        pass
    
    # Generate recommendations
    recommendations = []
    
    if not dependencies_status['kiwipiepy']['installed']:
        recommendations.append("Install kiwipiepy for fast Korean tokenization: pip install kiwipiepy")
    
    if not java_available and dependencies_status['konlpy']['installed']:
        recommendations.append("Install Java for KoNLPy functionality")
    
    if not any(d['functional'] for d in dependencies_status.values()):
        recommendations.append("No Korean NLP libraries are functional. Install at least kiwipiepy or konlpy.")
    
    return KoreanNLPStatus(
        dependencies_status=dependencies_status,
        java_available=java_available,
        java_version=java_version,
        recommendations=recommendations
    )