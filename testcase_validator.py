#!/usr/bin/env python3
import sys
from pathlib import Path

from yaml_schema_validator import YamlSchemaValidator


def main():
    if len(sys.argv) < 3:
        print("Usage: python testcase_validator.py json_schema.json testcase.yml")
        sys.exit(1)
    path_ = Path(sys.argv[1])
    json_schema = YamlSchemaValidator.load_json_schema(path_)[1]

    yaml_file = sys.argv[2]
    validator = YamlSchemaValidator(Path(yaml_file), json_schema)
    success = validator.validate_and_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
