#!/bin/bash
# Activate the MCP Python environment

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/mcp-env/bin/activate"

echo "✅ MCP environment activated (Python $(python --version))"
echo "To deactivate, run: deactivate"