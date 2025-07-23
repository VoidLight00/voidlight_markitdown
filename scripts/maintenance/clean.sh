#!/bin/bash
# Clean up project directory

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}Cleaning up project directory...${NC}"

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true

# Remove pytest cache
echo "Removing pytest cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove mypy cache
echo "Removing mypy cache..."
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove coverage files
echo "Removing coverage files..."
rm -f .coverage
rm -f coverage.xml
rm -rf htmlcov/

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf src/*.egg-info

# Remove tox artifacts
echo "Removing tox artifacts..."
rm -rf .tox/

# Remove ruff cache
echo "Removing ruff cache..."
rm -rf .ruff_cache/

# Remove Jupyter checkpoints
echo "Removing Jupyter checkpoints..."
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

# Remove DS_Store files (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Removing .DS_Store files..."
    find . -type f -name ".DS_Store" -delete 2>/dev/null || true
fi

# Remove log files (keeping the logs directory)
echo "Cleaning log files..."
if [ -d "logs" ]; then
    find logs -type f -name "*.log" -delete 2>/dev/null || true
fi

# Clean temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.temp" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true

echo -e "${GREEN}✓ Cleanup complete!${NC}"

# Show disk usage
echo -e "\n${YELLOW}Project size:${NC}"
du -sh .