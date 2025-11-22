#!/bin/bash
# Demo script for shell script generation from YAML test cases

check_virtualenv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -f ".venv/bin/activate" ]; then
            echo "Activating: source .venv/bin/activate"
            source .venv/bin/activate
        else
            echo "Error: No virtual environment found"
            echo "Please create one first: python -m venv .venv"
            exit 1
        fi
    fi
    echo "Virtual environment: $VIRTUAL_ENV"
}

# Check virtual environment
check_virtualenv

echo "=========================================="
echo "Test Case Parser Demo - Shell Script Only"
echo "=========================================="
echo ""

# Check if testcase_parser.py exists
if [ ! -f "testcase_parser.py" ]; then
    echo "Error: testcase_parser.py not found"
    exit 1
fi

echo "Parsing test case YAML and generating shell script..."
echo "Command: python3 testcase_parser.py ./data/dataset_3/X20_I1_TC1.yml tmp/"
echo ""

mkdir -p tmp
python3 testcase_parser.py ./data/dataset_3/X20_I1_TC1.yml tmp/

if [ $? -eq 0 ]; then
    echo ""
    echo "Successfully generated executable test script: tmp/X20_I1_TC1.sh"
    echo ""
    echo "You can run it with: ./tmp/X20_I1_TC1.sh"
else
    echo "Failed to generate script"
    exit 1
fi
