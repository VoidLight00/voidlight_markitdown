#!/usr/bin/env python
"""Test script to verify voidlight-markitdown installation and dependencies."""

import sys
import importlib
import subprocess
from typing import List, Tuple, Optional

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 9):
        print("❌ Python 3.9 or higher is required")
        return False
    elif version >= (3, 9) and version < (3, 14):
        print("✅ Python version is compatible")
        return True
    else:
        print("⚠️  Python version is newer than tested versions (3.9-3.13)")
        return True

def check_module(module_name: str, package_name: Optional[str] = None) -> bool:
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name} - {str(e)}")
        return False

def check_core_dependencies() -> List[Tuple[str, bool]]:
    """Check core dependencies."""
    print("\n📦 Core Dependencies:")
    deps = [
        ("bs4", "beautifulsoup4"),
        ("markdownify", None),
        ("charset_normalizer", None),
        ("magika", None),
        ("requests", None),
        ("tabulate", None),
    ]
    
    results = []
    for module, package in deps:
        results.append((package or module, check_module(module, package)))
    return results

def check_optional_dependencies():
    """Check optional dependencies by category."""
    
    categories = {
        "📄 Document Processing": [
            ("docx", "python-docx"),
            ("mammoth", None),
            ("pptx", "python-pptx"),
            ("openpyxl", None),
            ("pandas", None),
            ("xlrd", None),
            ("pdfplumber", None),
            ("PyPDF2", None),
            ("ebooklib", None),
            ("extract_msg", "extract-msg"),
        ],
        "🖼️  Media Processing": [
            ("PIL", "pillow"),
            ("pytesseract", None),
            ("easyocr", None),
            ("speech_recognition", "SpeechRecognition"),
            ("pydub", None),
        ],
        "🌐 Web/API": [
            ("feedparser", None),
            ("youtube_transcript_api", None),
        ],
        "📦 Archive Handling": [
            ("rarfile", None),
            ("py7zr", None),
        ],
        "🇰🇷 Korean Language": [
            ("konlpy", None),
            ("kiwipiepy", None),
            ("soynlp", None),
            ("jamo", None),
            ("hanja", None),
            # ("hanspell", "py-hanspell"),  # Known installation issues
        ],
        "🤖 AI/LLM": [
            ("openai", None),
            ("azure.cognitiveservices.speech", "azure-cognitiveservices-speech"),
        ],
    }
    
    for category, deps in categories.items():
        print(f"\n{category}:")
        for module, package in deps:
            check_module(module, package)

def check_voidlight_markitdown():
    """Check if voidlight_markitdown can be imported."""
    print("\n🚀 VoidLight MarkItDown:")
    
    try:
        from voidlight_markitdown import VoidLightMarkItDown
        print("✅ Main module imported successfully")
        
        # Test basic initialization
        md = VoidLightMarkItDown()
        print("✅ VoidLightMarkItDown instance created")
        
        # Test Korean mode
        md_korean = VoidLightMarkItDown(korean_mode=True)
        print("✅ Korean mode initialized")
        
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_system_dependencies():
    """Check system-level dependencies."""
    print("\n🔧 System Dependencies:")
    
    commands = {
        "tesseract": "Tesseract OCR (for pytesseract)",
        "ffmpeg": "FFmpeg (for audio processing)",
        "java": "Java (for KoNLPy)",
        "exiftool": "ExifTool (for metadata extraction)",
    }
    
    for cmd, description in commands.items():
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - command failed")
        except FileNotFoundError:
            print(f"❌ {description} - not found")

def main():
    """Run all checks."""
    print("=" * 60)
    print("VoidLight MarkItDown Installation Test")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check core dependencies
    core_results = check_core_dependencies()
    core_success = all(result for _, result in core_results)
    
    # Check if package is installed
    if not check_voidlight_markitdown():
        print("\n⚠️  VoidLight MarkItDown is not properly installed")
        print("Run: pip install -e . (for development)")
        print("Or: pip install voidlight-markitdown")
        return
    
    # Check optional dependencies
    check_optional_dependencies()
    
    # Check system dependencies
    check_system_dependencies()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    if core_success:
        print("✅ All core dependencies are installed")
    else:
        print("❌ Some core dependencies are missing")
        print("   Run: pip install -r requirements-minimal.txt")
    
    print("\n💡 Tips:")
    print("- For full functionality: pip install -r requirements.txt")
    print("- For specific features: pip install 'voidlight-markitdown[pdf,korean,image]'")
    print("- For py-hanspell: pip install git+https://github.com/ssut/py-hanspell.git")

if __name__ == "__main__":
    main()