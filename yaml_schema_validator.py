import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML library is required. Install with: uv add pyyaml, or uv sync")
    sys.exit(1)

try:
    from jsonschema import SchemaError, ValidationError, validate
except ImportError:
    print("Error: jsonschema library is required. Install with: uv add jsonschema, or uv sync")
    sys.exit(1)


class YamlSchemaValidator:
    @staticmethod
    def load_json_schema(path_: Path) -> tuple[bool, Any]:
        with Path.open(path_) as json_schema_file:
            try:
                lines = [line.strip() for line in json_schema_file.readlines()]
            except Exception as e:
                print("Error reading JSON schema file:", e)
                sys.exit(1)
        json_schema_contents = "".join(lines)
        try:
            json_schema = json.loads(json_schema_contents)
            return True, json_schema
        except Exception as e:
            print("Error parsing JSON schema:", e)
        return False, None

    def __init__(self, yaml_file: Path, schema_object: dict[str, Any]):
        """
        :type yaml_file: Path to the yaml file to validate. Must exist.
        :type schema_object: dict[str, Any] - JSON.loads(object) where object is the JSON string
        :see self::load_json_schema
        """
        self.yaml_file = yaml_file
        self.data = None
        self.schema = schema_object

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
