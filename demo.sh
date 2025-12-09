#!/bin/bash
# Demo script showing the complete test case workflow

check_virtualenv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -f ".venv/bin/activate" ]; then
            echo "Activating: source .venv/bin/activate"
            source .venv/bin/activate
        else
          echo "Error: Virtual environment is not activated"
            echo "No virtual environment found. Please create one first."
        fi
    fi
    echo "Virtual environment is activated: $VIRTUAL_ENV"
}

# Check if virtual environment is activated
check_virtualenv


# Print header
echo "=========================================="
echo "Test Case Parser Demo"
echo "=========================================="
echo ""

# Check if testcase_parser.py exists
if [ ! -f "testcase_parser.py" ]; then
    echo "Error: testcase_parser.py not found"
    exit 1
fi

echo "Step 1: Parsing test case YAML..."
echo "Command: python3 testcase_parser.py X20_1_example.yml tmp/"
echo ""

mkdir -p tmp
python3 testcase_parser.py ./data/dataset_3/X20_I1_TC1.yml tmp/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully generated:"
    echo "   - X20_1_example.sh (executable test script)"
    echo "   - X20_1_example.md (markdown documentation)"
    echo ""
else
    echo "❌ Failed to generate outputs"
    exit 1
fi

echo "OK"
