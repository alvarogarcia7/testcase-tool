#!/usr/bin/env python3
import abc
import argparse
import dataclasses
import json
import os
import sys
from abc import ABC
from functools import partial
from pathlib import Path
from typing import Callable, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from typing_extensions import override

from yaml_schema_validator import YamlSchemaValidator


class GenericTestPlanRenderer(ABC):
    def __init__(self, input_file):
        self.input_file = input_file
        self.payload = None

    def load_payload(self):
        file_path = self.input_file
        file_path_name = self.input_file.__str__()
        try:
            with open(file_path) as f:
                if file_path_name.endswith(".json"):
                    self.payload = json.load(f)
                elif file_path_name.endswith((".yaml", ".yml")):
                    self.payload = yaml.safe_load(f)
                else:
                    print(f"Error: Unsupported file format '{file_path_name}'")
                    return False
            return True
        except FileNotFoundError:
            print(f"Error: File '{file_path_name}' not found")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            print(f"Error parsing file: {e}")
        except Exception as e:
            print(f"Error loading file: {e}")
        return False

    # Safe helper that reads files only from the template directory
    @staticmethod
    def read_file_safe(template_dir: Path, name: str) -> str:
        assert isinstance(template_dir, Path), f"Expected Path, got {type(template_dir)}, {template_dir}"
        assert isinstance(name, str), f"Expected str, got {type(name)}: {name}"
        path = (template_dir / name).resolve()
        template_dir = template_dir.resolve()
        # Prevent escaping the template dir: ensure path is inside template_dir
        if template_dir not in path.parents and path != template_dir:
            raise RuntimeError(f"Access denied: Error: Path '{path}' is outside of template directory '{template_dir}'")
        return path.read_text()

    # Creating a typed wrapper factory
    @staticmethod
    def _make_partial(func: Callable, /, *args, **kwargs) -> Callable:
        """Return a partial with the same call semantics."""
        return partial(func, *args, **kwargs)

    def render(self, template_path=None, template_string=None, output_file=None):
        if not self.payload:
            print("Error: No test plan loaded")
            return False

        try:
            if template_path:
                template_file = Path(template_path).absolute()
                if not template_file.exists():
                    print(f"Error: Template file '{template_path}' not found")
                    return False
                env = Environment(
                    loader=FileSystemLoader(template_file.parent),
                    undefined=StrictUndefined,
                )
                # Expose helper to templates
                env.globals["read_file"] = self._make_partial(TestCaseRenderer.read_file_safe, template_file.parent)
                template = env.get_template(template_file.name)
            elif template_string:
                template = Template(template_string)
            else:
                print("Error: No template provided")
                return False

            rendered = self._actual_render(template)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(rendered)
            else:
                print(rendered)

            return True
        except Exception as e:
            print(f"Error rendering template: {e}")
            raise e

    @abc.abstractmethod
    def _actual_render(self, template):
        pass


class TestCaseRenderer(GenericTestPlanRenderer):
    @override
    def _actual_render(self, template: Template) -> str:
        return template.render(tc=self.payload, toc_entry="4.2.2.2")


class ContainerRenderer(GenericTestPlanRenderer):
    @override
    def _actual_render(self, template: Template) -> str:
        return template.render(container=self.payload)


def parse_args(argv):
    """Require both --container and --test-case modes to be provided. --test-case accepts a schema plus multiple files."""
    parser = argparse.ArgumentParser(
        prog="testplan_renderer_gsma.py",
        description="Create a document with all the test cases from a test plan.",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        required=False,
        help="Output file for container rendering (if not provided prints container render to stdout)",
    )

    parser.add_argument(
        "--container",
        nargs=3,
        required=True,
        metavar=("CONTAINER_SCHEMA", "CONTAINER_TEMPLATE", "CONTAINER_FILE"),
        help="Provide container schema, template, and a container file to render (three args):"
        " --container container_schema.json container.j2 container.json",
    )

    # test-case: schema + one or more files; we'll validate minimum count in main
    parser.add_argument(
        "--test-case",
        required=True,
        nargs="+",
        metavar=("TEST_CASE_SCHEMA", "TEST_CASE_TEMPLATE TEST_CASE_FILE [REST_TEST_CASE_FILES]"),
        help=(
            "Provide first the testcase schema, template, and then one or more testcase files: "
            "--test-case testcase_schema.json testcase.j2 test1.yml test2.yml ..."
        ),
    )

    return parser.parse_args(argv)


def usage(return_code):
    print(
        "Usage: python testplan_renderer_gsma.py [-o out] --container container_schema.json container.json --test-case testcase_schema.json test1.yml test2.yml ..."
    )
    sys.exit(return_code)


def main(argv=None):
    parsed_args = parse_and_validate_args(argv)

    errors = []
    for fpath in [tcr.data_file for tcr in parsed_args.test_case_renderers]:
        renderer = TestCaseRenderer(fpath)
        if not renderer.load_payload():
            print(f"Skipping file due to load error: {fpath}")
            errors.append(fpath)
            continue
        print(f"----- Rendering test case file: {fpath} -----")
        test_plan_md = (parsed_args.container_renderer.template_file.parent / "test_plan.md").resolve()
        os.unlink(test_plan_md)
        assert not Path(test_plan_md).exists(), f"Test plan markdown still exists before creating it: {test_plan_md}"
        if not renderer.render(
            template_path=parsed_args.test_case_renderers[0].template_file, output_file=test_plan_md
        ):
            print(f"Error rendering {fpath}")
    if errors:
        print(f"Errors rendering {len(errors)} files:")
        for e in errors:
            print(f"-  {e}")
        sys.exit(1)

    container_renderer = ContainerRenderer(parsed_args.container_renderer.data_file)
    if not container_renderer.load_payload():
        sys.exit(1)
    if not container_renderer.render(
        template_path=parsed_args.container_renderer.template_file, output_file=parsed_args.output_file
    ):
        print("Error rendering container")
        sys.exit(1)


@dataclasses.dataclass(frozen=True)
class RendererArgs:
    template_file: Path
    schema_file: Path
    data_file: Path

    def validate(self):
        errors = []
        if not self.data_file.exists():
            errors.append(f"Data file not found: {self.data_file}")
        if not self.template_file.exists():
            errors.append(f"Template file not found: {self.template_file}")
        if not self.schema_file.exists():
            errors.append(f"Schema file not found: {self.schema_file}")
        schema = YamlSchemaValidator.load_json_schema(self.schema_file)
        if not (schema[0] and schema[1]):
            errors.append(f"Invalid schema file: {self.schema_file}")

        if not YamlSchemaValidator(self.data_file, schema[1]).validate_and_report():
            print(f"Error validating test case file: {self.data_file}")
            sys.exit(1)

        if not self.data_file.__str__().endswith((".json", ".yaml", ".yml")):
            errors.append(f"Data file must be JSON or YAML: {self.data_file}")

        if not self.template_file.__str__().endswith(".j2"):
            errors.append(f"Container template must be a Jinja2 template: {self.template_file!s}. Must end with '.j2'.")

        return errors


@dataclasses.dataclass(frozen=True)
class TestPlanRendererArgsOutput:
    output_file: Optional[Path]
    container_renderer: RendererArgs
    test_case_renderers: list[RendererArgs]


def parse_and_validate_args(argv) -> TestPlanRendererArgsOutput:
    from collections import Counter
    from typing import Iterable, List

    def _repeated_elements(arr: Iterable) -> List:
        """
        Return list of elements that appear more than once.
        """
        freq = Counter(arr)
        return [x for x, c in freq.items() if c > 1]

    args = parse_args(argv)

    print("----- Command line arguments -----")
    for arg in vars(args):
        print(f"{arg}: {getattr(args, arg)}")

    for file in args.container:
        assert Path(file).exists(), f"Container file not found: {file}"

    if args.output_file:
        args.output_file = Path(args.output_file)
    else:
        print("No output file provided, printing to stdout")
        args.output_file = None

    container_schema_file = args.container[0]
    container_template_file = args.container[1]
    container_data_file = args.container[2]

    container_renderer_args = RendererArgs(
        Path(container_template_file), Path(container_schema_file), Path(container_data_file)
    )
    errors = container_renderer_args.validate()
    if errors:
        print("Errors validating container renderer args:")
        for e in errors:
            print(f"-  {e}")
        sys.exit(1)

    if not (args.container and args.test_case):
        print("Error: you must provide BOTH --container and --test-case arguments")
        usage(1)

    # Validate that --test-case includes schema + at least two testcase files
    # (assumption: user requested at least 2 test-case files)
    if len(args.test_case) < 3:
        print("Error: --test-case requires a schema, a template, plus at least ONE testcase files")
        usage(1)

    for fpath in args.test_case:
        assert Path(fpath).exists(), f"File not found: {fpath}"

    test_case_schema = args.test_case[0]
    test_case_template = args.test_case[1]
    test_case_files = args.test_case[2:]
    assert (
        len(test_case_files) >= 1
    ), f"At least ONE test case files must be provided: {test_case_files} (len={len(test_case_files)})"

    assert len(test_case_files) == len(
        set(test_case_files)
    ), f"Duplicate test case files provided: {', '.join(_repeated_elements(test_case_files))}. The whole list is: {test_case_files}."

    test_case_renderers = []
    for test_case_file in test_case_files:
        renderer_args = RendererArgs(Path(test_case_template), Path(test_case_schema), Path(test_case_file))
        errors = renderer_args.validate()
        if errors:
            print(f"Errors validating test case renderer args: {test_case_file}")
            for e in errors:
                print(f"-  {e}")
            sys.exit(1)
        test_case_renderers.append(renderer_args)

    return TestPlanRendererArgsOutput(
        args.output_file,
        container_renderer_args,
        test_case_renderers,
    )


if __name__ == "__main__":
    main()
