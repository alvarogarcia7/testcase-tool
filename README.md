# Test Case Parser - Shell Script Generator

A lightweight Python tool that converts YAML test case definitions into executable shell scripts.

## Features

- Parse YAML test case files
- Generate executable shell scripts from test definitions
- Support for environment variable expansion (`$VAR` and `${VAR}` syntax)
- Clean, minimal codebase focused on shell script generation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd testcase-tool

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install pyyaml
```

## Usage

### Command Line

```bash
python testcase_parser.py <testcase.yml> [output_dir]
```

Examples:
```bash
# Generate script in current directory
python testcase_parser.py test.yml

# Generate script in specific directory
python testcase_parser.py test.yml ./output/
```

### Environment Variable Expansion

The parser supports environment variable expansion in commands:

```yaml
commands:
  - step: 1
    description: Use API token
    commands:
      - curl -H "Authorization: Bearer ${API_TOKEN}" https://api.example.com
```

When run with `export API_TOKEN="secret123"`, the generated script will contain:
```bash
curl -H "Authorization: Bearer secret123" https://api.example.com
```

Both `$VAR` and `${VAR}` syntax are supported. Undefined variables are left unchanged.

### Demo

Run the included demo script:
```bash
./demo.sh
```

## YAML Structure

### Minimal Example

```yaml
testcase_id: TC001
commands:
  - step: 1
    description: Run basic test
    commands:
      - echo "Hello World"
```

### Complete Example

```yaml
testcase_id: API_001
requirement_id: REQ_API_001
description: Test API endpoint functionality

prerequisites:
  - API server is running
  - Valid credentials available

commands:
  - step: 1
    description: Test GET endpoint
    commands:
      - curl -X GET https://api.example.com/users

  - step: 2
    description: Test POST with authentication
    commands:
      - |
        curl -X POST https://api.example.com/users \
          -H "Authorization: Bearer ${API_TOKEN}" \
          -H "Content-Type: application/json" \
          -d '{"name": "Test User"}'

verification_commands:
  - description: Verify response
    commands:
      - test -f response.json
      - jq '.status' response.json
```

## Generated Script Features

The generated shell scripts include:
- Bash shebang (`#!/bin/bash`)
- Color-coded output (green, yellow, red)
- `set -e` for error handling
- Step-by-step execution with descriptions
- Prerequisites display
- Verification commands
- Executable permissions (chmod 755)

## Testing

Run the test suite:
```bash
python test_testcase_parser.py
```

All tests use Python's built-in `unittest` module, no external dependencies required.

## Code Statistics

- Main parser: ~159 lines (simplified from 312)
- Tests: ~502 lines (focused on core functionality)
- Zero unnecessary complexity
- Single responsibility: YAML to Shell

## Development

This is a simplified version focused solely on shell script generation. Previous features removed:
- Markdown documentation generation
- Actual log parsing and integration
- Complex helper functions

## License

See LICENSE file for details.
