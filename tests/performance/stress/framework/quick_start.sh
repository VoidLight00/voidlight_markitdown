#!/bin/bash
# Quick start script for VoidLight MarkItDown MCP Server Stress Testing

echo "=============================================="
echo "VoidLight MarkItDown MCP Server Stress Testing"
echo "=============================================="

# Change to stress testing directory
cd "$(dirname "$0")"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "Attempting to activate mcp-env..."
    
    if [ -f "../mcp-env/bin/activate" ]; then
        source ../mcp-env/bin/activate
        echo "✓ Activated mcp-env"
    else
        echo "✗ Could not find mcp-env"
        echo "Please activate your virtual environment first"
        exit 1
    fi
fi

# Run validation
echo ""
echo "Running setup validation..."
echo ""
python validate_setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Validation failed. Please fix the issues above."
    exit 1
fi

# Offer test options
echo ""
echo "=============================================="
echo "Available Test Profiles:"
echo "=============================================="
echo "1. Quick Test (5 minutes)"
echo "2. Korean Focus Test (15 minutes)"
echo "3. Comprehensive Test (30+ minutes)"
echo "4. Stress to Failure Test (20 minutes)"
echo "5. Custom Configuration"
echo "=============================================="
echo ""

read -p "Select test profile (1-5): " choice

case $choice in
    1)
        echo "Running Quick Test..."
        python run_stress_tests.py --profile quick
        ;;
    2)
        echo "Running Korean Focus Test..."
        python run_stress_tests.py --profile korean_focus
        ;;
    3)
        echo "Running Comprehensive Test..."
        echo "⚠️  This will take 30+ minutes"
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            python run_stress_tests.py --profile comprehensive
        fi
        ;;
    4)
        echo "Running Stress to Failure Test..."
        echo "⚠️  This will push the server to its limits"
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            python run_stress_tests.py --profile stress_only
        fi
        ;;
    5)
        echo "Custom Configuration"
        read -p "Enter config file path (or press Enter for sample): " config_file
        if [ -z "$config_file" ]; then
            config_file="sample_test_config.json"
        fi
        
        if [ -f "$config_file" ]; then
            echo "Running with config: $config_file"
            python run_stress_tests.py --config "$config_file"
        else
            echo "Config file not found: $config_file"
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Show results location
if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ Stress testing completed!"
    echo "=============================================="
    echo "Results are available in: stress_test_results/"
    echo ""
    echo "To view the monitoring dashboard (if still running):"
    echo "  http://localhost:8050"
    echo ""
fi