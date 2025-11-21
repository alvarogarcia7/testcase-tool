# Test Case YAML Structure Documentation

## Overview
This document describes the YAML structure for test case documentation. Each test case is stored in a separate YAML file with a standardized format.

## File Naming Convention
- **Test Case YAML**: `<RequirementID>_<TestCaseID>.yml`
  - Example: `X20_1.yml`, `AUTH_05.yml`, `API_12.yml`
- **Execution Log**: `<TestCaseID>.actual.log`
  - Example: `X20_1.actual.log`, `AUTH_05.actual.log`, `API_12.actual.log`

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
Sequence of commands to execute. Each step can contain multiple commands:
```yaml
commands:
  - step: 1                          # Sequential step number
    description: "Optional description"  # Human-readable step description
    commands:                         # List of commands to execute
      - command1
      - command2
      - |
        multi-line
        command here
    expected_status: 0                # Optional expected return code
    notes: "Optional notes"           # Additional context
```

**No Escaping Required:**
- Use plain YAML strings for simple commands: `docker ps`
- Use literal block scalar `|` for multi-line or complex commands with quotes
- No need to escape quotes, brackets, or special characters

**Examples:**
```yaml
# Simple command - no quotes needed
commands:
  - docker-compose up -d

# Command with quotes - use literal block
commands:
  - |
    curl -X POST http://api.com/login \
      -H "Content-Type: application/json" \
      -d '{"user":"test","pass":"123"}'

# Multiple commands in one step
commands:
  - step: 1
    commands:
      - echo "Starting test"
      - ./run_test.sh
      - echo "Test complete"
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
Reference to external log file containing execution details:
```yaml
actual_result:
  log_file: "X20_1.actual.log"      # Path to external log file
  execution_date: "2025-01-15T14:23:45Z"
  executed_by: "qa-automation"
  environment: "staging"
  summary:
    total_steps: 1
    total_commands: 1
    total_duration_ms: 156
    overall_status: "SUCCESS"        # SUCCESS, FAILED, ERROR
```

**Log File Naming Convention:**
- Format: `<TestCaseID>.actual.log`
- Example: `X20_1.actual.log`, `AUTH_05.actual.log`

**Log File Format (YAML):**
The external log file uses structured YAML format:
```yaml
execution_log:
  - timestamp: "2025-01-15T10:30:00Z"
    step: 1
    description: "Step description"
    commands:
      - command: actual command here
        output: |
          Command output here...
        status_code: 0
        duration_ms: 3200
        stderr: ""
      
      - command: second command
        output: "output text"
        status_code: 0
        duration_ms: 150
        stderr: ""

summary:
  total_steps: 3
  total_commands: 5
  successful_commands: 5
  failed_commands: 0
  total_duration_ms: 8446
  start_time: "2025-01-15T10:30:00.000Z"
  end_time: "2025-01-15T10:30:08.446Z"
  overall_status: "SUCCESS"

environment_info:
  hostname: "test-runner-01"
  os: "Linux 5.15.0-91-generic"
  python_version: "3.11.4"
  shell: "/bin/bash"
  working_directory: "/home/qa/tests"
```

See `testcase.actual.log.template` for a complete example.

**Benefits of External Log Files:**
- Keeps YAML test case files clean and readable
- Allows for large outputs without bloating the test case file
- Easier to parse and process execution logs separately
- Can be generated automatically by test execution tools
- Better for version control (can .gitignore log files)
- Structured format enables automated analysis and reporting

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
- `actual_result.log_file` should be generated automatically during execution
- `verification_steps` can be automated with assertions
- Log files can be parsed by CI/CD systems for reporting

**Example Automation Workflow:**
1. Parse YAML file to extract commands
2. Execute each step's commands in sequence
3. Capture output, status codes, and timing
4. Write results to `<TestCaseID>.actual.log`
5. Update YAML's `verification` section based on results
6. Archive both YAML and log files together

## Examples

See the following example files:
- `testcase_template.yml` - Comprehensive template with all options
- `X20_1_example.yml` - Filled example with realistic data
- `X20_1.actual.log` - Example execution log file
- `testcase.actual.log.template` - Template for execution log files
- `API_03_no_escape_example.yml` - Examples of shell commands without escaping (PASS)
- `X20_1.actual.log` - Example execution log file (successful test)
- `DB_05_failed_example.yml` - Example of a failed test case
- `DB_05.actual.log` - Example execution log file (failed test)
- `actual_log_template.txt` - Template for execution log files
- `API_03_no_escape_example.yml` - Examples of shell commands without escaping

## Best Practices

1. **Be Specific**: Avoid vague descriptions; use concrete, measurable criteria
2. **Keep It Current**: Update test cases when requirements change
3. **Version Control**: Store YAML files in Git for change tracking
4. **Consistency**: Use consistent formatting and terminology across test cases
5. **Completeness**: Fill in all sections, even if some are marked as empty/N/A
6. **File Organization**: 
   - Keep test case YAML and its log file together
   - Suggested directory structure:
     ```
     tests/
       X20_1.yml
       X20_1.actual.log
       X20_2.yml
       X20_2.actual.log
       AUTH_01.yml
       AUTH_01.actual.log
     ```
   - Consider organizing by requirement or feature area for large test suites
7. **Log File Management**: 
   - Archive old log files when re-running tests
   - Consider timestamped log files for multiple runs: `X20_1.actual.2025-01-15.log`

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
