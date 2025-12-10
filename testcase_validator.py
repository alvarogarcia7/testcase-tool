#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML library is required. Install with: uv add pyyaml")
    sys.exit(1)

try:
    from jsonschema import SchemaError, ValidationError, validate
except ImportError:
    print("Error: jsonschema library is required. Install with: uv add jsonschema")
    sys.exit(1)


class TestCaseValidator:
    def __init__(self, yaml_file, schema):
        self.yaml_file = yaml_file
        self.data = None
        self.schema = schema

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
    if len(sys.argv) < 3:
        print("Usage: python testcase_validator.py json_schema.json testcase.yml")
        sys.exit(1)
    path_ = Path(sys.argv[1])
    with Path.open(path_) as json_schema_file:
        try:
            lines = [line.strip() for line in json_schema_file.readlines()]
        except Exception as e:
            print("Error reading JSON schema file:", e)
            sys.exit(1)
    json_schema_contents = "".join(lines)
    try:
        json_schema = json.loads(json_schema_contents)
    except Exception as e:
        print("Error parsing JSON schema:", e)
        sys.exit(1)

    yaml_file = sys.argv[2]
    validator = TestCaseValidator(yaml_file, json_schema)
    success = validator.validate_and_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
