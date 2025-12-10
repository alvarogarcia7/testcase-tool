# Test Case Validator Usage

## Overview

The `testcase_validator.py` program validates YAML test case files against a defined schema to ensure they conform to the expected structure and data types.

## Installation

Install the required dependency (jsonschema):

```bash
uv sync
```

## Usage

```bash
python testcase_validator.py <testcase.yml>
```

### Example

```bash
python testcase_validator.py data/dataset_4_GSMA/gsma_4.4.2.2_TC.yml
```

## Output

The validator will output:
- **Success**: If the YAML file passes all schema validations
- **Failure**: If the YAML file contains schema violations, with detailed error messages showing:
  - The validation error message
  - The path to the problematic field
  - The schema path that failed

### Example Success Output

```
Validating: data/dataset_2/testcase_template.yml
--------------------------------------------------------------------------------
✓ Validation successful

File 'data/dataset_2/testcase_template.yml' is valid according to the test case schema.
```

### Example Failure Output

```
Validating: invalid_testcase.yml
--------------------------------------------------------------------------------
Validation Error: 'testcase_id' is a required property
Failed at: root
Schema path: anyOf -> 1 -> required

✗ Validation failed

File 'invalid_testcase.yml' contains schema violations.
```

## Supported Schema

The validator supports multiple test case formats found in this project:

### Format 1: Standard Test Case
- **Required**: `testcase_id` or `id`
- **Optional**: `requirement_id`, `metadata`, `description`, `prerequisites`, `commands`, `expected_result`, `actual_result`, `verification`

### Format 2: GSMA Test Case
- **Required**: `requirement`, `item`, `tc`
- **Optional**: `id`, `description`, `general_initial_conditions`, `initial_conditions`, `test_sequences`

### Common Fields

- **metadata**: Tags and categories
- **description**: Test case description
- **prerequisites**: List of prerequisites
- **commands**: Array of test steps with commands
- **expected_result**: Expected outputs and verification commands
- **actual_result**: Execution results with log file reference
- **verification**: Verification status and results

## Exit Codes

- **0**: Validation successful
- **1**: Validation failed or file not found
