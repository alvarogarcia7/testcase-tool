#!/usr/bin/env python3
import sys

import yaml

try:
    from jsonschema import SchemaError, ValidationError, validate
except ImportError:
    print("Error: jsonschema library is required. Install with: uv add jsonschema")
    sys.exit(1)


def get_testcase_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Test Case Schema",
        "description": "Schema for YAML test case files",
        "type": "object",
        "anyOf": [
            {"required": ["id"]},
            {"required": ["testcase_id"]},
            {"required": ["requirement", "item", "tc"]},
        ],
        "properties": {
            "id": {"type": "string", "description": "Unified test case identifier"},
            "testcase_id": {"type": "string", "description": "Test case identifier (alternative format)"},
            "requirement_id": {"type": "string", "description": "Associated requirement identifier"},
            "requirement": {"type": "string", "description": "Requirement identifier (GSMA format)"},
            "item": {"type": "integer", "description": "Item number (GSMA format)"},
            "tc": {"type": "integer", "description": "Test case number (GSMA format)"},
            "metadata": {
                "type": "object",
                "properties": {
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "categories": {"type": "array", "items": {"type": "string"}},
                },
            },
            "description": {"type": "string", "description": "Test case description"},
            "general_initial_conditions": {
                "type": "array",
                "description": "General initial conditions (GSMA format)",
                "items": {"type": "object"},
            },
            "initial_conditions": {
                "description": "Initial conditions before test execution",
                "oneOf": [{"type": "object"}, {"type": "array"}],
            },
            "prerequisites": {
                "type": "array",
                "description": "List of prerequisites for test execution",
                "items": {"type": "string"},
            },
            "commands": {
                "type": "array",
                "description": "Test execution commands/steps",
                "items": {
                    "type": "object",
                    "required": ["step"],
                    "properties": {
                        "step": {"type": "integer", "description": "Step number"},
                        "description": {"type": "string", "description": "Step description"},
                        "commands": {
                            "type": "array",
                            "description": "Commands to execute",
                            "items": {"type": "string"},
                        },
                        "expected_status": {"type": "integer", "description": "Expected exit status"},
                        "expected_output": {"type": "string", "description": "Expected output"},
                        "notes": {"type": "string", "description": "Additional notes"},
                        "manual": {"type": "boolean", "description": "Whether step is manual"},
                        "command": {"type": "string", "description": "Single command (alternative format)"},
                        "expected": {
                            "type": "object",
                            "description": "Expected results for step",
                            "properties": {
                                "success": {"type": "boolean"},
                                "result": {"type": "string"},
                                "output": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "test_sequences": {
                "type": "object",
                "description": "Test sequences (GSMA format)",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "initial_conditions": {"type": "array"},
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["step"],
                                "properties": {
                                    "step": {"type": "integer"},
                                    "description": {"type": "string"},
                                    "command": {"type": "string"},
                                    "manual": {"type": "boolean"},
                                    "expected": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "result": {"type": "string"},
                                            "output": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "verification_commands": {
                "type": "array",
                "description": "Verification commands to run after test execution",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "commands": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "expected_result": {
                "type": "object",
                "description": "Expected results of test execution",
                "properties": {
                    "description": {"type": "string"},
                    "expected_outputs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string"},
                                "value": {"oneOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}]},
                                "condition": {"type": "string"},
                            },
                        },
                    },
                    "verification_commands": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "command": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "results": {
                "type": "object",
                "description": "Results section (alternative format)",
                "properties": {
                    "expected": {
                        "type": "object",
                        "properties": {"description": {"type": "string"}},
                    },
                    "actual": {
                        "type": "object",
                        "properties": {
                            "log_file": {"type": "string"},
                            "execution_date": {"type": "string"},
                            "executed_by": {"type": "string"},
                            "environment": {"type": "string"},
                            "summary": {"type": "object"},
                        },
                    },
                },
            },
            "actual_result": {
                "type": "object",
                "description": "Actual execution results",
                "properties": {
                    "log_file": {"type": "string"},
                    "execution_date": {"type": "string"},
                    "executed_by": {"type": "string"},
                    "environment": {"type": "string"},
                    "summary": {
                        "type": "object",
                        "properties": {
                            "total_steps": {"type": "integer"},
                            "total_commands": {"type": "integer"},
                            "total_duration_ms": {"type": "integer"},
                            "overall_status": {"type": "string"},
                        },
                    },
                },
            },
            "verification": {
                "type": "object",
                "description": "Verification results",
                "properties": {
                    "status": {"type": "string", "enum": ["PASS", "FAIL", "BLOCKED", "SKIPPED"]},
                    "verification_steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "check": {"type": "string"},
                                "result": {"type": "string"},
                            },
                        },
                    },
                    "comments": {"type": "string"},
                    "executed_by": {"type": "string"},
                    "execution_date": {"type": "string"},
                    "environment": {"type": "string"},
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "issue_id": {"type": "string"},
                                "description": {"type": "string"},
                                "severity": {
                                    "type": "string",
                                    "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW", ""],
                                },
                            },
                        },
                    },
                    "notes": {"type": "string"},
                },
            },
        },
    }


class TestCaseValidator:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.data = None
        self.schema = get_testcase_schema()

    def load_yaml(self):
        t = None
        try:
            t = open(self.yaml_file)
            self.data = yaml.safe_load(t)
            return True
        except FileNotFoundError:
            print(f"Error: File '{self.yaml_file}' not found")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
        finally:
            if t:
                t.close()
        return False

    def validate(self):
        if not self.data:
            print("Error: No data loaded. Call load_yaml() first.")
            return False
        try:
            validate(instance=self.data, schema=self.schema)
            return True
        except ValidationError as e:
            print(f"Validation Error: {e.message}")
            print(f"Failed at: {' -> '.join(str(p) for p in e.path) if e.path else 'root'}")
            if e.schema_path:
                print(f"Schema path: {' -> '.join(str(p) for p in e.schema_path)}")
            return False
        except SchemaError as e:
            print(f"Schema Error: {e.message}")
            return False

    def validate_and_report(self):
        print(f"Validating: {self.yaml_file}")
        print("-" * 80)
        if not self.load_yaml():
            return False
        if self.validate():
            print("✓ Validation successful")
            print(f"\nFile '{self.yaml_file}' is valid according to the test case schema.")
            return True
        else:
            print("\n✗ Validation failed")
            print(f"\nFile '{self.yaml_file}' contains schema violations.")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python testcase_validator.py <testcase.yml>")
        sys.exit(1)
    yaml_file = sys.argv[1]
    validator = TestCaseValidator(yaml_file)
    success = validator.validate_and_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
