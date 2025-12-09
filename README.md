# Test Case YAML Structure Documentation

## Overview
This document describes the YAML structure for test case documentation. Each test case is stored in a separate YAML file with a standardized format.

## File Naming Convention
- Format: `<RequirementID>_<TestCaseID>.yml`
- Example: `X20_1.yml`, `AUTH_05.yml`, `API_12.yml`

## Structure

### 1. Test Case Identification
```yaml
testcase_id: "X20_1"      # Unique test case identifier
requirement_id: "X20"      # Associated requirement
```

### 2. Metadata
```yaml
metadata:
  tags:                    # Flexible tags for filtering/searching
    - "integration"
    - "smoke"
    - "regression"
  categories:              # Hierarchical categorization
    - "authentication"
    - "api"
```

### 3. Description
Multi-line text describing the test purpose and scope.

### 4. Prerequisites
List of conditions that must be met before test execution:
```yaml
prerequisites:
  - "Database is running"
  - "User account exists"
```

### 5. Commands
Sequence of commands to execute:
```yaml
commands:
  - step: 1                          # Sequential step number
    description: "Optional description"  # Human-readable step description
    command: "actual command"         # Command to execute
    expected_status: 0                # Optional expected return code
    notes: "Optional notes"           # Additional context
```

### 6. Expected Result
What should happen when test executes correctly:
```yaml
expected_result:
  description: |                      # Narrative description
    What should happen...

  expected_outputs:                   # Specific values to check
    - field: "status_code"
      value: 200
    - field: "response.token"
      condition: "is not null"

  verification_commands:              # Commands to verify results
    - description: "Check token"
      command: "jwt decode $TOKEN"
```

### 7. Actual Result
Log of what actually happened during execution:
```yaml
actual_result:
  execution_log:
    - timestamp: "2025-01-15T10:30:00Z"  # ISO 8601 format
      step: 1                             # Corresponds to command step
      command: "command that was run"
      output: |                           # Actual output
        Command output here
      status_code: 0                      # Return code
      duration_ms: 3420                   # Execution time in milliseconds
```

**Suggested Format:**
- Use ISO 8601 timestamps
- Include full command output for debugging
- Record status codes and duration for performance tracking
- Can be populated manually or by automation tools

### 8. Verification
Final test results and analysis:
```yaml
verification:
  status: "PASS"                      # PASS, FAIL, BLOCKED, SKIPPED

  verification_steps:                 # Individual checks performed
    - check: "Description of check"
      result: "PASS"                  # PASS or FAIL

  comments: |                         # Overall assessment
    Analysis and observations

  executed_by: "user@example.com"     # Who ran the test
  execution_date: "2025-01-15T10:30:00Z"
  environment: "staging"              # Where it was run

  issues:                             # Problems found
    - issue_id: "BUG-123"
      description: "Brief description"
      severity: "HIGH"                # CRITICAL, HIGH, MEDIUM, LOW

  notes: |                            # Additional notes
    Any other relevant information
```

## Usage Guidelines

### For Test Authors
1. Create one YAML file per test case
2. Use clear, descriptive names for IDs and descriptions
3. Keep prerequisites specific and measurable
4. Write commands that can be copy-pasted and executed
5. Define clear, verifiable expected results

### For Test Executors
1. Check all prerequisites before starting
2. Execute commands in sequence
3. Record exact outputs in `actual_result` section
4. Complete all verification steps
5. Update `verification` section with results

### For Automation
The YAML structure supports both manual and automated testing:
- `commands` section can be parsed and executed by scripts
- `actual_result` can be populated automatically
- `verification_steps` can be automated with assertions

## Examples

See the following example files:
- `testcase_template.yml` - Comprehensive template with all options
- `X20_1_example.yml` - Filled example with realistic data

## Best Practices

1. **Be Specific**: Avoid vague descriptions; use concrete, measurable criteria
2. **Keep It Current**: Update test cases when requirements change
3. **Version Control**: Store YAML files in Git for change tracking
4. **Consistency**: Use consistent formatting and terminology across test cases
5. **Completeness**: Fill in all sections, even if some are marked as empty/N/A

## Status Values

### Test Status
- `PASS`: All verification steps passed
- `FAIL`: One or more verification steps failed
- `BLOCKED`: Cannot execute due to external dependencies
- `SKIPPED`: Intentionally not executed

### Issue Severity
- `CRITICAL`: System crash, data loss, security vulnerability
- `HIGH`: Major functionality broken
- `MEDIUM`: Moderate impact on functionality
- `LOW`: Minor issue, cosmetic problem
