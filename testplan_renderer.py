#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template


class TestPlanRenderer:
    def __init__(self, input_file):
        self.input_file = input_file
        self.test_plan = None

    def load_test_plan(self):
        try:
            with open(self.input_file) as f:
                if self.input_file.endswith(".json"):
                    self.test_plan = json.load(f)
                elif self.input_file.endswith((".yaml", ".yml")):
                    self.test_plan = yaml.safe_load(f)
                else:
                    print("Error: Unsupported file format")
                    return False
            return True
        except FileNotFoundError:
            print(f"Error: File '{self.input_file}' not found")
        except (json.JSONDecodeError, yaml.YAMLError):
            print("Error parsing file")
        except Exception:
            print("Error loading file")
        return False

    def render(self, template_path=None, template_string=None, output_file=None):
        if not self.test_plan:
            print("Error: No test plan loaded")
            return False

        try:
            if template_path:
                template_file = Path(template_path)
                if not template_file.exists():
                    print(f"Error: Template file '{template_path}' not found")
                    return False
                env = Environment(
                    loader=FileSystemLoader(template_file.parent),
                    undefined=StrictUndefined,
                )
                template = env.get_template(template_file.name)
            elif template_string:
                template = Template(template_string)
            else:
                print("Error: No template provided")
                return False

            rendered = template.render(plan=self.test_plan)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(rendered)
                print(f"Rendered output saved to: {output_file}")
            else:
                print(rendered)

            return True
        except Exception as e:
            print(f"Error rendering template: {e}")
            raise e


def main():
    if len(sys.argv) < 2:
        print("Usage: python testplan_renderer.py <input_file> [output_file] [--template <template_file>]")
        print("\nArguments:")
        print("  input_file    - TestPlan data file (JSON or YAML)")
        print("  output_file   - Output file (optional, prints to stdout if not provided)")
        print("  --template    - Custom template file (optional, uses testplan_default.j2 if not provided)")
        print("\nExamples:")
        print("  python testplan_renderer.py plan.json")
        print("  python testplan_renderer.py plan.yaml output.md")
        print("  python testplan_renderer.py plan.json output.md --template testplan_detailed.j2")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    template_file = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--template" and i + 1 < len(sys.argv):
            template_file = sys.argv[i + 1]
            i += 2
        else:
            output_file = sys.argv[i]
            i += 1

    if not template_file:
        script_dir = Path(__file__).parent
        default_template = script_dir / "tests" / "approval" / "testplan_default.j2"
        if default_template.exists():
            template_file = str(default_template)
        else:
            print("Error: Default template 'testplan_default.j2' not found")
            sys.exit(1)

    renderer = TestPlanRenderer(input_file)
    if not renderer.load_test_plan():
        sys.exit(1)

    if not renderer.render(template_path=template_file, output_file=output_file):
        sys.exit(1)


if __name__ == "__main__":
    main()
