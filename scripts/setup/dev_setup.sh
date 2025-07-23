#!/bin/bash
# Development environment setup script for voidlight_markitdown

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Setting up voidlight_markitdown development environment...${NC}"

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo -e "${RED}Error: Python 3.9 or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "mcp-env" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv mcp-env
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source mcp-env/bin/activate

# Upgrade pip and setuptools
echo -e "\n${YELLOW}Upgrading pip and setuptools...${NC}"
pip install --upgrade pip setuptools wheel

# Install development dependencies
echo -e "\n${YELLOW}Installing development dependencies...${NC}"
pip install -r requirements/development.txt

# Install the package in editable mode
echo -e "\n${YELLOW}Installing package in editable mode...${NC}"
pip install -e ".[dev]"

# Install pre-commit hooks
echo -e "\n${YELLOW}Installing pre-commit hooks...${NC}"
pre-commit install
pre-commit install --hook-type commit-msg

# Set up Git hooks
echo -e "\n${YELLOW}Setting up Git hooks...${NC}"
cp scripts/git/pre-commit .git/hooks/
cp scripts/git/pre-push .git/hooks/
chmod +x .git/hooks/pre-commit .git/hooks/pre-push

# Check for required system dependencies
echo -e "\n${YELLOW}Checking system dependencies...${NC}"

# Check for tesseract (for OCR)
if command -v tesseract &> /dev/null; then
    echo -e "${GREEN}✓ Tesseract OCR installed${NC}"
else
    echo -e "${YELLOW}⚠ Tesseract OCR not found. Install it for OCR support.${NC}"
fi

# Check for ffmpeg (for audio processing)
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓ FFmpeg installed${NC}"
else
    echo -e "${YELLOW}⚠ FFmpeg not found. Install it for audio processing support.${NC}"
fi

# Check for Korean language support
echo -e "\n${YELLOW}Checking Korean language support...${NC}"
if python3 -c "import konlpy" 2>/dev/null; then
    echo -e "${GREEN}✓ KoNLPy installed${NC}"
else
    echo -e "${YELLOW}⚠ KoNLPy not available. Korean NLP features may be limited.${NC}"
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating project directories...${NC}"
mkdir -p logs
mkdir -p data/cache
mkdir -p reports
echo -e "${GREEN}✓ Project directories created${NC}"

# Run initial tests to verify setup
echo -e "\n${YELLOW}Running quick tests to verify setup...${NC}"
python -m pytest tests/unit/utils/test_module_misc.py -v --tb=short || {
    echo -e "${YELLOW}⚠ Some tests failed. This might be expected for a fresh setup.${NC}"
}

# Setup completion message
echo -e "\n${GREEN}✅ Development environment setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Activate the virtual environment: ${YELLOW}source mcp-env/bin/activate${NC}"
echo -e "2. Run tests: ${YELLOW}pytest tests/${NC}"
echo -e "3. Start developing!"
echo -e "\n${BLUE}Useful commands:${NC}"
echo -e "- Format code: ${YELLOW}make format${NC}"
echo -e "- Run linting: ${YELLOW}make lint${NC}"
echo -e "- Run tests with coverage: ${YELLOW}make test-coverage${NC}"
echo -e "- Build documentation: ${YELLOW}make docs${NC}"