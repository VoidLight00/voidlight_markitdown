#!/bin/bash
# VoidLight MarkItDown - Project Cleanup Script

echo "🧹 Cleaning VoidLight MarkItDown project..."

# Python cache and compiled files
echo "Removing Python cache files..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Test artifacts
echo "Removing test artifacts..."
rm -rf .pytest_cache .coverage .coverage.* htmlcov/ .mypy_cache .tox .nox 2>/dev/null || true
rm -rf test_artifacts test_results test_output reports 2>/dev/null || true
rm -f test_*.py test_*.json *_test_report.json *_test_report.md .report.json 2>/dev/null || true

# Log files
echo "Removing log files..."
find . -type f -name "*.log" -delete 2>/dev/null || true
find . -type f -name "*.log.*" -delete 2>/dev/null || true
rm -rf logs 2>/dev/null || true

# Temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.temp" -delete 2>/dev/null || true
find . -type f -name "*.swp" -delete 2>/dev/null || true
find . -type f -name "*.swo" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true
find . -type f -name ".#*" -delete 2>/dev/null || true
find . -type f -name "#*#" -delete 2>/dev/null || true

# CI/CD artifacts
echo "Removing CI/CD artifacts..."
rm -f ci_validation_report_*.json local_ci_test_report_*.json integration_test_report_*.json 2>/dev/null || true
rm -rf docker_build_logs 2>/dev/null || true

# Large test files
echo "Removing large test files..."
rm -f large_*.txt huge_*.txt 2>/dev/null || true
find . -type f -name "performance_test_*" -delete 2>/dev/null || true
rm -rf benchmark_results 2>/dev/null || true

# Audio test files
echo "Removing audio test files..."
find . -type f \( -name "*.wav" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.ogg" \) -delete 2>/dev/null || true
rm -rf audio_samples 2>/dev/null || true

# System temporary files
echo "Removing system temporary files..."
rm -rf /tmp/voidlight* /tmp/pytest* /tmp/test_* 2>/dev/null || true

# Node modules (if any)
echo "Removing node_modules..."
find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "package-lock.json" -delete 2>/dev/null || true

# Build artifacts
echo "Removing build artifacts..."
rm -rf build dist *.egg-info 2>/dev/null || true

# Archive files (be careful with this)
# Uncomment if you want to remove archives
# find . -type f \( -name "*.zip" -o -name "*.tar" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*.rar" -o -name "*.7z" \) -delete 2>/dev/null || true

echo "✅ Cleanup complete!"

# Show disk usage
echo ""
echo "📊 Project size after cleanup:"
du -sh .
echo ""
echo "Largest directories:"
du -h -d 1 . | sort -hr | head -10

# Optional: Clean virtual environment
echo ""
read -p "Do you want to remove the virtual environment (mcp-env)? This will require reinstallation. (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Removing virtual environment..."
    rm -rf mcp-env
    echo "✅ Virtual environment removed"
fi

echo ""
echo "🎉 Cleanup finished!"