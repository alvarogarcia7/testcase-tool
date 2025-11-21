#!/usr/bin/env python3
"""YAML Validator for Test Case files.

Validates YAML test case files against the testcase_schema.json schema.
"""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, ValidationError


def load_schema(schema_path: str | Path | None = None) -> dict:
    """Load the JSON schema from file.

    Args:
        schema_path: Path to the schema file. If None, uses default location.

    Returns:
        The loaded schema as a dictionary.
    """
    if schema_path is None:
        schema_path = Path(__file__).parent / "testcase_schema.json"
    else:
        schema_path = Path(schema_path)

    with open(schema_path) as f:
        return json.load(f)


def load_yaml(yaml_path: str | Path) -> dict:
    """Load a YAML file.

    Args:
        yaml_path: Path to the YAML file.

    Returns:
        The loaded YAML as a dictionary.
    """
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def validate_yaml(yaml_path: str | Path, schema_path: str | Path | None = None) -> tuple[bool, list[str]]:
    """Validate a YAML file against the schema.

    Args:
        yaml_path: Path to the YAML file to validate.
        schema_path: Path to the schema file. If None, uses default location.

    Returns:
        A tuple of (is_valid, list of error messages).
    """
    errors = []

    try:
        schema = load_schema(schema_path)
    except FileNotFoundError:
        return False, ["Schema file not found"]
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON schema: {e}"]

    try:
        data = load_yaml(yaml_path)
    except FileNotFoundError:
        return False, [f"YAML file not found: {yaml_path}"]
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]

    validator = Draft7Validator(schema)
    validation_errors = list(validator.iter_errors(data))

    if validation_errors:
        for error in validation_errors:
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
            errors.append(f"Error at '{path}': {error.message}")
        return False, errors

    return True, []


def validate_yaml_string(yaml_content: str, schema_path: str | Path | None = None) -> tuple[bool, list[str]]:
    """Validate a YAML string against the schema.

    Args:
        yaml_content: YAML content as a string.
        schema_path: Path to the schema file. If None, uses default location.

    Returns:
        A tuple of (is_valid, list of error messages).
    """
    errors = []

    try:
        schema = load_schema(schema_path)
    except FileNotFoundError:
        return False, ["Schema file not found"]
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON schema: {e}"]

    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]

    validator = Draft7Validator(schema)
    validation_errors = list(validator.iter_errors(data))

    if validation_errors:
        for error in validation_errors:
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
            errors.append(f"Error at '{path}': {error.message}")
        return False, errors

    return True, []


class YAMLValidator:
    """A class to validate YAML test case files against a schema."""

    def __init__(self, schema_path: str | Path | None = None):
        """Initialize the validator with a schema.

        Args:
            schema_path: Path to the schema file. If None, uses default location.
        """
        self.schema = load_schema(schema_path)
        self.validator = Draft7Validator(self.schema)

    def validate(self, yaml_path: str | Path) -> tuple[bool, list[str]]:
        """Validate a YAML file.

        Args:
            yaml_path: Path to the YAML file to validate.

        Returns:
            A tuple of (is_valid, list of error messages).
        """
        return validate_yaml(yaml_path, schema_path=None)

    def validate_string(self, yaml_content: str) -> tuple[bool, list[str]]:
        """Validate a YAML string.

        Args:
            yaml_content: YAML content as a string.

        Returns:
            A tuple of (is_valid, list of error messages).
        """
        return validate_yaml_string(yaml_content, schema_path=None)

    def validate_dict(self, data: dict) -> tuple[bool, list[str]]:
        """Validate a dictionary directly.

        Args:
            data: Dictionary to validate.

        Returns:
            A tuple of (is_valid, list of error messages).
        """
        errors = []
        validation_errors = list(self.validator.iter_errors(data))

        if validation_errors:
            for error in validation_errors:
                path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
                errors.append(f"Error at '{path}': {error.message}")
            return False, errors

        return True, []


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python yaml_validator.py <yaml_file> [schema_file]")
        print("\nValidates a YAML test case file against the schema.")
        print("\nArguments:")
        print("  yaml_file    Path to the YAML file to validate")
        print("  schema_file  Optional path to a custom schema file")
        sys.exit(1)

    yaml_path = sys.argv[1]
    schema_path = sys.argv[2] if len(sys.argv) > 2 else None

    is_valid, errors = validate_yaml(yaml_path, schema_path)

    if is_valid:
        print(f"VALID: {yaml_path}")
        sys.exit(0)
    else:
        print(f"INVALID: {yaml_path}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
