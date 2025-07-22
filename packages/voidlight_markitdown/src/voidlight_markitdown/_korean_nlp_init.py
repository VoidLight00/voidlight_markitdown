"""
Korean NLP Initialization System

This module handles the initialization and verification of Korean NLP dependencies,
providing graceful fallbacks when dependencies are missing.
"""

import sys
import subprocess
import logging
from typing import Optional, Dict, Any, Tuple
import os
import platform

logger = logging.getLogger(__name__)


class KoreanNLPInitializer:
    """Handles initialization and verification of Korean NLP dependencies."""
    
    def __init__(self):
        self.dependencies_status = {}
        self.java_status = None
        self.check_dependencies()
    
    def check_java_installation(self) -> Tuple[bool, Optional[str]]:
        """Check if Java is installed and accessible for KoNLPy.
        
        Returns:
            Tuple of (is_installed, version_string)
        """
        try:
            result = subprocess.run(
                ['java', '-version'], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            # Java outputs version info to stderr
            version_output = result.stderr
            if 'version' in version_output.lower():
                # Extract version number
                import re
                version_match = re.search(r'"(\d+\.\d+\.\d+[^"]*)"', version_output)
                if version_match:
                    version = version_match.group(1)
                else:
                    version = "Unknown version"
                
                logger.info(f"Java detected: {version}")
                return True, version
            else:
                logger.warning("Java command found but version unclear")
                return True, "Unknown version"
                
        except FileNotFoundError:
            logger.warning("Java not found in PATH")
            return False, None
        except subprocess.TimeoutExpired:
            logger.warning("Java version check timed out")
            return False, None
        except Exception as e:
            logger.warning(f"Error checking Java: {e}")
            return False, None
    
    def check_jpype_installation(self) -> bool:
        """Check if JPype1 is installed for KoNLPy Java bridge."""
        try:
            import jpype1
            logger.info(f"JPype1 version {jpype1.__version__} detected")
            return True
        except ImportError:
            logger.warning("JPype1 not installed (required for KoNLPy)")
            return False
    
    def verify_konlpy_functionality(self) -> Tuple[bool, Optional[str]]:
        """Verify that KoNLPy can actually function with Java."""
        try:
            from konlpy.tag import Okt
            
            # Try to initialize and use Okt
            okt = Okt()
            # Test with simple text
            result = okt.pos("테스트")
            
            if result:
                logger.info("KoNLPy Okt tokenizer verified and functional")
                return True, "Okt"
            else:
                logger.warning("KoNLPy Okt initialized but not producing results")
                return False, None
                
        except ImportError:
            logger.warning("KoNLPy not installed")
            return False, None
        except Exception as e:
            logger.warning(f"KoNLPy initialization failed: {e}")
            # Check if it's a Java-related error
            error_msg = str(e).lower()
            if 'java' in error_msg or 'jvm' in error_msg:
                logger.error("KoNLPy Java dependency issue detected")
            return False, None
    
    def verify_kiwi_functionality(self) -> Tuple[bool, Optional[str]]:
        """Verify that Kiwi tokenizer is functional."""
        try:
            from kiwipiepy import Kiwi
            
            kiwi = Kiwi()
            # Test with simple text
            result = kiwi.tokenize("테스트")
            
            if result:
                logger.info("Kiwi tokenizer verified and functional")
                return True, f"Kiwi (version {kiwi.version() if hasattr(kiwi, 'version') else 'unknown'})"
            else:
                logger.warning("Kiwi initialized but not producing results")
                return False, None
                
        except ImportError:
            logger.warning("kiwipiepy not installed")
            return False, None
        except Exception as e:
            logger.warning(f"Kiwi initialization failed: {e}")
            return False, None
    
    def check_dependencies(self):
        """Check all Korean NLP dependencies and their status."""
        # Check Java first (required for KoNLPy)
        java_installed, java_version = self.check_java_installation()
        self.java_status = {
            'installed': java_installed,
            'version': java_version
        }
        
        # Check JPype1
        jpype_installed = self.check_jpype_installation()
        
        # Core NLP libraries
        self.dependencies_status['java'] = self.java_status
        self.dependencies_status['jpype1'] = {'installed': jpype_installed}
        
        # Check Kiwi (doesn't require Java)
        kiwi_ok, kiwi_info = self.verify_kiwi_functionality()
        self.dependencies_status['kiwipiepy'] = {
            'installed': kiwi_ok,
            'functional': kiwi_ok,
            'info': kiwi_info
        }
        
        # Check KoNLPy (requires Java)
        if java_installed and jpype_installed:
            konlpy_ok, konlpy_info = self.verify_konlpy_functionality()
            self.dependencies_status['konlpy'] = {
                'installed': konlpy_ok,
                'functional': konlpy_ok,
                'info': konlpy_info
            }
        else:
            self.dependencies_status['konlpy'] = {
                'installed': False,
                'functional': False,
                'info': 'Java or JPype1 not available'
            }
        
        # Check optional libraries
        optional_libs = {
            'soynlp': 'soynlp',
            'hanspell': 'py-hanspell',
            'jamo': 'jamo',
            'hanja': 'hanja'
        }
        
        for lib_name, pip_name in optional_libs.items():
            try:
                __import__(lib_name)
                self.dependencies_status[lib_name] = {
                    'installed': True,
                    'pip_name': pip_name
                }
                logger.info(f"{lib_name} is available")
            except ImportError:
                self.dependencies_status[lib_name] = {
                    'installed': False,
                    'pip_name': pip_name
                }
                logger.debug(f"{lib_name} not installed (optional)")
    
    def get_installation_instructions(self) -> Dict[str, Any]:
        """Get installation instructions for missing dependencies."""
        instructions = {
            'summary': '',
            'commands': [],
            'optional_commands': [],
            'notes': []
        }
        
        missing_core = []
        missing_optional = []
        
        # Check core dependencies
        if not self.dependencies_status['kiwipiepy']['functional']:
            missing_core.append('kiwipiepy')
            instructions['commands'].append('pip install kiwipiepy')
        
        if not self.dependencies_status['konlpy']['functional']:
            if not self.java_status['installed']:
                instructions['notes'].append(
                    "KoNLPy requires Java. Please install Java 8 or higher:"
                )
                
                system = platform.system()
                if system == 'Darwin':  # macOS
                    instructions['notes'].append(
                        "  macOS: brew install openjdk@11"
                    )
                elif system == 'Linux':
                    instructions['notes'].append(
                        "  Ubuntu/Debian: sudo apt-get install openjdk-11-jdk"
                    )
                elif system == 'Windows':
                    instructions['notes'].append(
                        "  Windows: Download from https://adoptopenjdk.net/"
                    )
            
            if not self.dependencies_status['jpype1']['installed']:
                instructions['commands'].append('pip install JPype1')
            
            instructions['commands'].append('pip install konlpy')
        
        # Check optional dependencies
        for lib_name, info in self.dependencies_status.items():
            if lib_name in ['soynlp', 'hanspell', 'jamo', 'hanja']:
                if not info['installed']:
                    missing_optional.append(info['pip_name'])
        
        if missing_optional:
            instructions['optional_commands'].append(
                f"pip install {' '.join(missing_optional)}"
            )
            instructions['notes'].append(
                "Optional libraries provide additional features but are not required."
            )
        
        # Generate summary
        if missing_core:
            instructions['summary'] = f"Missing core dependencies: {', '.join(missing_core)}"
        else:
            instructions['summary'] = "All core dependencies are installed and functional!"
        
        return instructions
    
    def get_status_report(self) -> str:
        """Generate a human-readable status report."""
        lines = ["Korean NLP Dependencies Status Report", "=" * 40]
        
        # Java status
        java_status = self.java_status
        lines.append(f"\nJava Runtime:")
        lines.append(f"  Installed: {'✓' if java_status['installed'] else '✗'}")
        if java_status['version']:
            lines.append(f"  Version: {java_status['version']}")
        
        # Core NLP libraries
        lines.append(f"\nCore NLP Libraries:")
        
        # Kiwi
        kiwi_status = self.dependencies_status['kiwipiepy']
        lines.append(f"  Kiwi (C++ based, no Java required):")
        lines.append(f"    Functional: {'✓' if kiwi_status['functional'] else '✗'}")
        if kiwi_status.get('info'):
            lines.append(f"    Info: {kiwi_status['info']}")
        
        # KoNLPy
        konlpy_status = self.dependencies_status['konlpy']
        lines.append(f"  KoNLPy (Java-based):")
        lines.append(f"    Functional: {'✓' if konlpy_status['functional'] else '✗'}")
        if konlpy_status.get('info'):
            lines.append(f"    Info: {konlpy_status['info']}")
        
        # Optional libraries
        lines.append(f"\nOptional Libraries:")
        for lib_name in ['soynlp', 'hanspell', 'jamo', 'hanja']:
            if lib_name in self.dependencies_status:
                status = self.dependencies_status[lib_name]
                lines.append(f"  {lib_name}: {'✓' if status['installed'] else '✗'}")
        
        # Add recommendations
        lines.append(f"\nRecommendations:")
        if kiwi_status['functional']:
            lines.append("  ✓ Kiwi is functional - primary tokenizer ready")
        else:
            lines.append("  ! Install kiwipiepy for best performance")
        
        if not konlpy_status['functional'] and java_status['installed']:
            lines.append("  ! KoNLPy available but needs setup")
        elif not java_status['installed']:
            lines.append("  ! Install Java for KoNLPy support (optional)")
        
        return '\n'.join(lines)


# Singleton instance
_initializer = None


def get_korean_nlp_status() -> KoreanNLPInitializer:
    """Get the singleton Korean NLP initializer instance."""
    global _initializer
    if _initializer is None:
        _initializer = KoreanNLPInitializer()
    return _initializer


def print_status_report():
    """Print the Korean NLP status report."""
    initializer = get_korean_nlp_status()
    print(initializer.get_status_report())
    
    instructions = initializer.get_installation_instructions()
    if instructions['commands'] or instructions['optional_commands']:
        print("\nInstallation Instructions:")
        print("-" * 40)
        
        if instructions['commands']:
            print("\nRequired:")
            for cmd in instructions['commands']:
                print(f"  {cmd}")
        
        if instructions['optional_commands']:
            print("\nOptional:")
            for cmd in instructions['optional_commands']:
                print(f"  {cmd}")
        
        if instructions['notes']:
            print("\nNotes:")
            for note in instructions['notes']:
                print(f"  {note}")


if __name__ == "__main__":
    # Run status check when module is executed directly
    print_status_report()