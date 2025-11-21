# Test Case Parser - Usage Guide

## Overview

The `testcase_parser.py` tool reads test case YAML files and generates two outputs:
1. **Shell script (.sh)** - Executable test script with prerequisites, commands, and assertions
2. **Markdown documentation (.md)** - Human-readable test case documentation with execution logs

## Requirements

- Python 3.x (no external dependencies required)
- PyYAML (part of Python standard library)

## Usage

### Basic Usage

```bash
python3 testcase_parser.py <testcase.yml>
```

This will generate:
- `<testcase>.sh` - Executable shell script
- `<testcase>.md` - Markdown documentation

### Specify Output Directory

```bash
python3 testcase_parser.py <testcase.yml> <output_dir>
```

### Examples

```bash
# Parse X20_1_example.yml in current directory
python3 testcase_parser.py X20_1_example.yml

# Parse test case and output to specific directory
python3 testcase_parser.py tests/X20_1.yml output/

# Make the script executable and run it
python3 testcase_parser.py X20_1.yml
chmod +x X20_1.sh
./X20_1.sh
```

## Generated Outputs

### Shell Script (.sh)

The generated shell script includes:
- **Prerequisites check section** - Validates all prerequisites before execution
- **Test execution section** - Runs all test commands in sequence
- **Verification section** - Performs assertions and checks expected outputs
- **Colored output** - Uses ANSI colors for better readability
- **Error handling** - Exits on error with proper status codes

Example structure:
```bash
#!/bin/bash
# Auto-generated test script
# Test Case: X20_1

# Prerequisites check
check_prerequisites() {
    # Validates all prerequisites
}

# Test execution
echo "Step 1: ..."
command1
command2

# Verification
echo "Running verification checks..."
assertion1
assertion2
```

### Markdown Documentation (.md)

The generated markdown includes:
- **Test case metadata** - ID, requirement, tags, categories
- **Description** - Test purpose and scope
- **Prerequisites** - Required conditions
- **Test steps** - All commands with descriptions
- **Expected results** - What should happen
- **Actual execution results** - From the .actual.log file if available
- **Verification results** - Pass/fail status and details

## Log File Integration

The parser automatically reads the corresponding `.actual.log` file if it exists and merges the execution data into the markdown documentation.

Log file naming: `<testcase_id>.actual.log`

Example:
- Test case: `X20_1.yml`
- Log file: `X20_1.actual.log` (automatically detected and loaded)
- Output: `X20_1.md` (includes log data)

## Features

### Prerequisites Handling
- Lists all prerequisites in the shell script
- Provides placeholders for actual checks
- Can be easily extended with real validation logic

### Multi-line Commands
- Properly handles multi-line shell commands
- Preserves command formatting
- Supports complex bash syntax

### No Escaping Required
- Shell commands are written to the script exactly as they appear in YAML
- No need to worry about quote escaping
- Supports all bash features (pipes, redirects, conditionals)

### Execution Tracking
- Captures command exit status codes
- Records execution time (from log file)
- Shows detailed output for each command

### Rich Markdown Output
- Uses emojis for status indicators (✅ ❌)
- Proper code formatting with syntax highlighting
- Tables for verification results
- Expandable sections for long outputs

## Workflow Example

1. **Write test case YAML**
   ```bash
   vim X20_1.yml
   ```

2. **Generate shell script and documentation**
   ```bash
   python3 testcase_parser.py X20_1.yml
   ```

3. **Execute the test**
   ```bash
   ./X20_1.sh > X20_1.actual.log 2>&1
   ```

4. **Format execution log** (manually or with automation)
   ```bash
   # Convert plain text log to structured YAML format
   # This step would typically be done by test automation
   ```

5. **Regenerate documentation with logs**
   ```bash
   python3 testcase_parser.py X20_1.yml
   # Now X20_1.md includes execution results
   ```

6. **Review results**
   ```bash
   cat X20_1.md
   # Or open in markdown viewer
   ```

## Batch Processing

Process multiple test cases:

```bash
#!/bin/bash
# Process all test cases in a directory

for testcase in tests/*.yml; do
    echo "Processing $testcase..."
    python3 testcase_parser.py "$testcase" output/
done

echo "All test cases processed!"
```

## Customization

The parser can be extended to:
- Add custom prerequisite checks
- Integrate with CI/CD pipelines
- Generate additional output formats (HTML, PDF, etc.)
- Automate log file generation
- Add test result aggregation

## Tips

1. **Keep test cases modular** - One test case per file for easier management
2. **Use descriptive IDs** - Makes it easier to find and reference tests
3. **Add detailed descriptions** - Helps others understand test purpose
4. **Version control everything** - Track changes to test cases over time
5. **Automate log generation** - Use test runners to create structured logs

## Troubleshooting

### "Error: Test case file not found"
- Check the file path
- Ensure the YAML file exists
- Use absolute or relative paths correctly

### "Error parsing YAML"
- Validate YAML syntax
- Check for proper indentation
- Ensure no special characters are breaking parsing

### Log file not loaded
- Verify log file naming: `<testcase_id>.actual.log`
- Check log file location (same directory as test case)
- Ensure log file is valid YAML format

### Shell script not executable
- Run: `chmod +x <script>.sh`
- Or execute with: `bash <script>.sh`

## Support

For issues or questions:
1. Check the YAML syntax in your test case files
2. Review the README.md for YAML format specifications
3. Examine the example files provided
4. Test with the provided examples first
