#!/usr/bin/env python
"""Script to help install py-hanspell with various workarounds."""

import subprocess
import sys
import os


def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        return False


def try_install_methods():
    """Try various methods to install py-hanspell."""
    
    print("=" * 60)
    print("Attempting to install py-hanspell")
    print("=" * 60)
    
    # Method 1: Direct pip install
    print("\n🔧 Method 1: Direct pip install")
    if run_command("pip install py-hanspell", check=False):
        print("✅ Successfully installed via pip")
        return True
    
    # Method 2: Install from GitHub
    print("\n🔧 Method 2: Install from GitHub")
    if run_command("pip install git+https://github.com/ssut/py-hanspell.git", check=False):
        print("✅ Successfully installed from GitHub")
        return True
    
    # Method 3: Clone and install manually
    print("\n🔧 Method 3: Clone and install manually")
    temp_dir = "/tmp/py-hanspell-install"
    
    if os.path.exists(temp_dir):
        run_command(f"rm -rf {temp_dir}")
    
    if run_command(f"git clone https://github.com/ssut/py-hanspell.git {temp_dir}", check=False):
        if run_command(f"cd {temp_dir} && pip install .", check=False):
            print("✅ Successfully installed from cloned repository")
            run_command(f"rm -rf {temp_dir}")
            return True
    
    # Method 4: Install without dependencies and then install them separately
    print("\n🔧 Method 4: Install without dependencies")
    if run_command("pip install --no-deps py-hanspell", check=False):
        print("Installing dependencies separately...")
        deps = ["requests", "beautifulsoup4"]
        for dep in deps:
            run_command(f"pip install {dep}")
        print("✅ Installed without dependencies, then added them")
        return True
    
    return False


def test_hanspell():
    """Test if py-hanspell is working."""
    print("\n🧪 Testing py-hanspell...")
    
    test_code = """
try:
    from hanspell import spell_checker
    result = spell_checker.check('맞춤법 틀리면 알려주세요')
    print("✅ py-hanspell is working!")
    print(f"Test result: {result}")
except Exception as e:
    print(f"❌ py-hanspell test failed: {e}")
"""
    
    run_command(f'python -c "{test_code}"')


def create_alternative():
    """Create an alternative spell checker stub."""
    print("\n📝 Creating alternative spell checker stub...")
    
    stub_code = '''"""Alternative Korean spell checker stub for when py-hanspell is not available."""

class DummySpellChecker:
    """Dummy spell checker that returns the input unchanged."""
    
    @staticmethod
    def check(text):
        """Return input text unchanged with dummy result format."""
        return {
            'checked': text,
            'errors': 0,
            'words': len(text.split()),
            'time': 0
        }

# Create a compatible interface
spell_checker = DummySpellChecker()

print("⚠️  Using dummy spell checker. Install py-hanspell for actual spell checking.")
'''
    
    # Create a local hanspell module if it doesn't exist
    os.makedirs("hanspell_stub", exist_ok=True)
    with open("hanspell_stub/__init__.py", "w") as f:
        f.write(stub_code)
    
    print("✅ Created spell checker stub in hanspell_stub/")
    print("   You can use this as a fallback by adding the directory to Python path")


def main():
    """Main function."""
    print("py-hanspell Installation Helper")
    print("=" * 60)
    
    # Check current Python version
    print(f"Python version: {sys.version}")
    
    # Try to import existing installation
    try:
        import hanspell
        print("\n✅ py-hanspell is already installed!")
        test_hanspell()
        return
    except ImportError:
        print("\n❌ py-hanspell is not installed")
    
    # Try various installation methods
    if try_install_methods():
        test_hanspell()
    else:
        print("\n❌ All installation methods failed")
        print("\n💡 Alternatives:")
        print("1. Use voidlight-markitdown without spell checking")
        print("2. Use the dummy spell checker stub")
        print("3. Try installing in a fresh virtual environment")
        print("4. Report the issue at: https://github.com/ssut/py-hanspell/issues")
        
        create_alternative()


if __name__ == "__main__":
    main()