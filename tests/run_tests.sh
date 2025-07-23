#!/bin/bash

# VoidLight MarkItDown Test Runner
# Run tests by category or all tests

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE=""
VERBOSE=false
COVERAGE=false
MARKERS=""

# Help function
show_help() {
    echo "VoidLight MarkItDown Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE      Run specific test type: unit, integration, e2e, performance, all"
    echo "  -m, --marker MARKER  Run tests with specific marker (e.g., korean, mcp)"
    echo "  -v, --verbose        Enable verbose output"
    echo "  -c, --coverage       Generate coverage report"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -t unit                    # Run all unit tests"
    echo "  $0 -t integration -m mcp      # Run MCP integration tests"
    echo "  $0 -c                         # Run all tests with coverage"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -m|--marker)
            MARKERS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python3 -m pytest"

# Add test type
case $TEST_TYPE in
    unit)
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        echo -e "${GREEN}Running unit tests...${NC}"
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        echo -e "${GREEN}Running integration tests...${NC}"
        ;;
    e2e)
        PYTEST_CMD="$PYTEST_CMD tests/e2e/"
        echo -e "${GREEN}Running end-to-end tests...${NC}"
        ;;
    performance)
        PYTEST_CMD="$PYTEST_CMD tests/performance/"
        echo -e "${YELLOW}Running performance tests (this may take a while)...${NC}"
        ;;
    all|"")
        PYTEST_CMD="$PYTEST_CMD tests/"
        echo -e "${GREEN}Running all tests...${NC}"
        ;;
    *)
        echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
        show_help
        exit 1
        ;;
esac

# Add markers
if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m $MARKERS"
fi

# Add verbose flag
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vv"
fi

# Add coverage flags
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=voidlight_markitdown --cov-report=html --cov-report=term"
fi

# Run tests
echo "Executing: $PYTEST_CMD"
echo "----------------------------------------"

# Execute pytest
eval $PYTEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    if [ "$COVERAGE" = true ]; then
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi