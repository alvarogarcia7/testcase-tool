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

# Check if example file exists
if [ ! -f "X20_1_example.yml" ]; then
    echo "Error: X20_1_example.yml not found"
    exit 1
fi

echo "Step 1: Parsing test case YAML..."
echo "Command: python3 testcase_parser.py X20_1_example.yml tmp/"
echo ""

mkdir -p tmp
python3 testcase_parser.py X20_1_example.yml tmp/

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

echo "Step 2: Viewing generated files..."
echo ""

if [ -f "X20_1_example.sh" ]; then
    echo "📄 Shell script preview (first 20 lines):"
    echo "-------------------------------------------"
    head -20 X20_1_example.sh
    echo "..."
    echo ""
fi

if [ -f "X20_1_example.md" ]; then
    echo "📄 Markdown preview (first 30 lines):"
    echo "-------------------------------------------"
    head -30 X20_1_example.md
    echo "..."
    echo ""
fi

echo "=========================================="
echo "Demo completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review the generated shell script: cat X20_1_example.sh"
echo "2. Review the markdown document: cat X20_1_example.md"
echo "3. Execute the test script: ./X20_1_example.sh"
echo "4. Try with your own test cases: python3 testcase_parser.py <your_test>.yml"
echo ""
