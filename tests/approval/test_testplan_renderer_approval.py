#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import approvaltests.approvals
import yaml
from approvaltests import verify
from approvaltests.namer import NamerFactory
from approvaltests.reporters import PythonNativeReporter


class TestPlanRendererGsmaApprovalTests(unittest.TestCase):
    """End-to-end approval tests for testplan_renderer.py CLI."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.maxDiff = None
        approvaltests.approvals.set_default_reporter(PythonNativeReporter())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _run_cli(self, *args):
        result = self._run_cli_result(*args)
        return f"""\
Result code: {result.returncode}
Standard Output (starting on the new line):
{result.stdout}
Standard Error (starting on the new line):
{result.stderr}"""

    def _run_cli_result(self, *args):
        """Run testplan_renderer.py CLI and return stdout, stderr, and return code."""
        cmd = [sys.executable, "testplan_renderer.py"] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def _create_container_schema(self, filename="container_schema.json"):
        """Create a container schema file in temp directory."""
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "product": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["date", "product", "description"],
        }
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            json.dump(schema, f, indent=2)
        return filepath

    def _create_container_data(self, filename="container_data.yml", **kwargs):
        """Create a container data file in temp directory."""
        data = {
            "date": kwargs.get("date", "2024-01-01"),
            "product": kwargs.get("product", "Test Product"),
            "description": kwargs.get("description", "Test Description"),
        }
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            yaml.dump(data, f)
        return filepath

    def _create_container_template(self, filename="container_template.j2", content=None):
        """Create a container template file in temp directory."""
        if content is None:
            content = """# Test Document

Product: {{ container.product }}
Date: {{ container.date }}

{{ read_file('test_plan.md') }}

---
{{ container.description }}
"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def _create_test_case_schema(self, filename="testcase_schema.json"):
        """Create a test case schema file in temp directory."""
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "requirement": {"type": "string"},
                "item": {"type": "integer"},
                "tc": {"type": "integer"},
                "id": {"type": "string"},
                "description": {"type": "string"},
                "initial_conditions": {"type": "object"},
                "test_sequences": {"type": "array"},
            },
            "required": ["requirement", "item", "tc", "id", "description"],
        }
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            json.dump(schema, f, indent=2)
        return filepath

    def _create_test_case_template(self, filename="testcase_template.j2", content=None):
        """Create a test case template file in temp directory."""
        if content is None:
            content = """\
# {{ toc_entry }} Test Case: {{ tc.id }}

**Requirement**: {{ tc.requirement }}
**Item**: {{ tc.item }}

# Description

{{ tc.description }}

{%- if "initial_conditions" in tc -%}
# General Initial Conditions

| **Entity** | **Description of the general initial condition** |
| ------------- | --------- |
{% for entity,conditions in tc.initial_conditions.items() -%}
{% for condition in conditions -%}
| {{ entity }} | {{ condition }} |
{% endfor %}
{%- endfor %}
{%- endif -%}

{%- if "test_sequences" in tc -%}
{% for ts in tc.test_sequences %}
# Test Sequence {{ ts.id }} {{ ts.name }}

{{ ts.description }}

| **Step Number** | **Action** | **Expected Result** | **Expected Output** |
| ------------- | --------- | --------- |
{% for step in ts.steps -%}
| {{ step.step }} | {{ step.description }} | {{ step.expected.result }} | {{ step.expected.output }} |
{% endfor %}
{% endfor %}
{%- endif -%}
"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def _create_test_case_data(self, filename, data):
        """Create a test case YAML file in temp directory."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        return filepath

    def _setup_test_plan_md_placeholder(self, template_dir):
        """Create placeholder test_plan.md file for container template."""
        filepath = os.path.join(template_dir, "test_plan.md")
        with open(filepath, "w") as f:
            f.write("")
        return filepath

    def test_render_with_real_gsma_data(self):
        """Test rendering with real GSMA dataset."""
        self._setup_test_plan_md_placeholder("data/container")

        result = self._run_cli_result(
            "--container",
            "data/container/schema.json",
            "data/container/template.j2",
            "data/container/data.yml",
            "--test-case",
            "data/test_case/schema.json",
            "data/test_case/template.j2",
            "data/test_case/gsma_4.4.2.2_TC.yml",
        )

        verify(
            f"Return Code: {result.returncode}\n\nStdout:\n{result.stdout}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("gsma_real").namer,
        )

    def test_render_with_multiple_test_cases(self):
        """Test rendering with multiple test case files."""
        self._setup_test_plan_md_placeholder("data/container")

        result = self._run_cli_result(
            "--container",
            "data/container/schema.json",
            "data/container/template.j2",
            "data/container/data.yml",
            "--test-case",
            "data/test_case/schema.json",
            "data/test_case/template.j2",
            "data/test_case/gsma_4.4.2.2_TC.yml",
            "data/test_case/gsma_4.4.2.3_TC.yml",
        )

        verify(
            f"Return Code: {result.returncode}\n\nStdout:\n{result.stdout}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("multiple_cases").namer,
        )

    def test_render_minimal_test_case(self):
        """Test rendering with minimal test case data."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data()
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        minimal_testcase = {
            "requirement": "REQ001",
            "item": 1,
            "tc": 1,
            "id": "1.1.1",
            "description": "Minimal test case",
        }
        testcase_file = self._create_test_case_data("minimal_tc.yml", minimal_testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        with open(output_file) as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("minimal").namer,
        )

    def test_render_with_unicode_characters(self):
        """Test rendering with unicode and special characters."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data(
            product="测试产品 🚀",
            date="2024-01-01",
            description="Тестовое описание with émojis 😊",
        )
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        unicode_testcase = {
            "requirement": "РЕК001",
            "item": 1,
            "tc": 1,
            "id": "测试-1.1.1",
            "description": "Test with unicode: 中文字符 and émojis 🎉",
            "initial_conditions": {"eUICC": ["条件一", "条件二"]},
            "test_sequences": [
                {
                    "id": 1,
                    "name": "Тест последовательность",
                    "description": "Описание с unicode symbols: @#$%",
                    "steps": [
                        {
                            "step": 1,
                            "description": "步骤描述",
                            "command": "ssh",
                            "expected": {"result": "成功", "output": "Success ✓"},
                        }
                    ],
                }
            ],
        }
        testcase_file = self._create_test_case_data("unicode_tc.yml", unicode_testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        with open(output_file, encoding="utf-8") as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("unicode").namer,
        )

    def test_render_with_empty_test_sequences(self):
        """Test rendering with empty test sequences."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data()
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        empty_sequences_testcase = {
            "requirement": "REQ002",
            "item": 2,
            "tc": 2,
            "id": "2.2.2",
            "description": "Test case with empty sequences",
            "test_sequences": [],
        }
        testcase_file = self._create_test_case_data("empty_sequences_tc.yml", empty_sequences_testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        with open(output_file) as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("empty_sequences").namer,
        )

    def test_render_with_missing_optional_fields(self):
        """Test rendering with missing optional fields."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data()
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        missing_fields_testcase = {
            "requirement": "REQ003",
            "item": 3,
            "tc": 3,
            "id": "3.3.3",
            "description": "Test case with missing optional fields",
        }
        testcase_file = self._create_test_case_data("missing_fields_tc.yml", missing_fields_testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        with open(output_file) as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("missing_fields").namer,
        )

    def test_render_complex_nested_structure(self):
        """Test rendering with complex nested data structures."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data(product="Complex Product", description="Complex test")
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        complex_testcase = {
            "requirement": "REQ_COMPLEX",
            "item": 10,
            "tc": 10,
            "id": "10.10.10",
            "description": "Complex nested test case with multiple levels",
            "initial_conditions": {
                "eUICC": ["Condition A", "Condition B", "Condition C"],
                "SM-DP+": ["Server ready", "Auth configured"],
                "Device": ["Registered", "Active"],
            },
            "test_sequences": [
                {
                    "id": 1,
                    "name": "First Sequence",
                    "description": "Multi-step sequence with various conditions",
                    "steps": [
                        {
                            "step": 1,
                            "description": "Initialize connection",
                            "command": "init_connection",
                            "expected": {"result": "CONNECTED", "output": "Connection established"},
                        },
                        {
                            "step": 2,
                            "description": "Authenticate device",
                            "command": "authenticate",
                            "expected": {"result": "AUTH_SUCCESS", "output": "Device authenticated"},
                        },
                        {
                            "step": 3,
                            "description": "Download profile",
                            "command": "download_profile",
                            "expected": {"result": "DOWNLOAD_OK", "output": "Profile downloaded"},
                        },
                    ],
                },
                {
                    "id": 2,
                    "name": "Second Sequence",
                    "description": "Verification sequence",
                    "steps": [
                        {
                            "step": 1,
                            "description": "Verify profile installation",
                            "command": "verify_install",
                            "expected": {"result": "VERIFIED", "output": "Profile installed correctly"},
                        }
                    ],
                },
            ],
        }
        testcase_file = self._create_test_case_data("complex_tc.yml", complex_testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        print(result.stdout)

        with open(output_file) as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("complex").namer,
        )

    def test_error_missing_container_argument(self):
        """Test error handling when --container argument is missing."""
        result = self._run_cli_result(
            "--test-case",
            "data/test_case/schema.json",
            "data/test_case/template.j2",
            "data/test_case/gsma_4.4.2.2_TC.yml",
        )

        verify(result.stderr, namer=NamerFactory.with_parameters("missing_container").namer)

    def test_error_missing_test_case_argument(self):
        """Test error handling when --test-case argument is missing."""
        result = self._run_cli_result(
            "--container",
            "data/container/schema.json",
            "data/container/template.j2",
            "data/container/data.yml",
        )

        verify(result.stderr, namer=NamerFactory.with_parameters("missing_testcase").namer)

    def test_error_invalid_test_case_yaml(self):
        """Test error handling with invalid YAML in test case file."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data()
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        invalid_yaml = os.path.join(self.temp_dir, "invalid.yml")
        with open(invalid_yaml, "w") as f:
            f.write("invalid: yaml: [unclosed")

        self._setup_test_plan_md_placeholder(self.temp_dir)

        result = self._run_cli_result(
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            invalid_yaml,
        )

        verify(
            f"Return Code: {result.returncode}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("invalid_yaml").namer,
        )

    def test_error_schema_validation_failure(self):
        """Test error handling when data doesn't match schema."""
        container_schema = self._create_container_schema()
        # Create data missing required fields
        invalid_container_data = os.path.join(self.temp_dir, "invalid_data.yml")
        with open(invalid_container_data, "w") as f:
            yaml.dump({"date": "2024-01-01"}, f)  # Missing required 'product' and 'description'

        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()
        testcase_file = self._create_test_case_data(
            "tc.yml",
            {"requirement": "REQ001", "item": 1, "tc": 1, "id": "1.1.1", "description": "Test"},
        )

        self._setup_test_plan_md_placeholder(self.temp_dir)

        result = self._run_cli_result(
            "--container",
            container_schema,
            container_template,
            invalid_container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        verify(
            f"Return Code: {result.returncode}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("schema_validation").namer,
        )

    def test_error_insufficient_test_case_arguments(self):
        """Test error handling when insufficient test-case arguments provided."""
        result = self._run_cli_result(
            "--container",
            "data/container/schema.json",
            "data/container/template.j2",
            "data/container/data.yml",
            "--test-case",
            "data/test_case/schema.json",
            "data/test_case/template.j2",
        )

        verify(result.stderr, namer=NamerFactory.with_parameters("insufficient_args").namer)

    def test_render_to_output_file(self):
        """Test rendering output to a specified file."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data()
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        testcase = {
            "requirement": "REQ_OUTPUT",
            "item": 5,
            "tc": 5,
            "id": "5.5.5",
            "description": "Test output to file",
            "test_sequences": [
                {
                    "id": 1,
                    "name": "Sequence One",
                    "description": "Test sequence",
                    "steps": [
                        {
                            "step": 1,
                            "description": "Step one",
                            "command": "cmd",
                            "expected": {"result": "OK", "output": "Success"},
                        }
                    ],
                }
            ],
        }
        testcase_file = self._create_test_case_data("output_tc.yml", testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "custom_output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        print(result.stdout)

        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nFile exists: {os.path.exists(output_file)}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("output_file").namer,
        )

    def test_render_with_special_characters_in_descriptions(self):
        """Test rendering with special characters like <, >, &, quotes in descriptions."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data(
            product='Product with <tags> & "quotes"',
            description="Description with 'apostrophes' and <html> tags",
        )
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        special_chars_testcase = {
            "requirement": "REQ<001>",
            "item": 6,
            "tc": 6,
            "id": "6.6.6 <Test>",
            "description": "Test with special chars: < > & \" ' and @#$%",
            "test_sequences": [
                {
                    "id": 1,
                    "name": "Sequence with <brackets>",
                    "description": 'Description with & ampersands and "quotes"',
                    "steps": [
                        {
                            "step": 1,
                            "description": "Step with <html> tags & symbols",
                            "command": "cmd --param='value'",
                            "expected": {
                                "result": "Result with <> and &",
                                "output": "Output with \"double\" and 'single' quotes",
                            },
                        }
                    ],
                }
            ],
        }
        testcase_file = self._create_test_case_data("special_chars_tc.yml", special_chars_testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        with open(output_file) as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("special_chars").namer,
        )

    def test_render_with_multiline_descriptions(self):
        """Test rendering with multi-line descriptions."""
        container_schema = self._create_container_schema()
        container_data = self._create_container_data(
            description="""This is a multi-line description.

It contains multiple paragraphs.

- Bullet point 1
- Bullet point 2
- Bullet point 3

And some final text."""
        )
        container_template = self._create_container_template()

        testcase_schema = self._create_test_case_schema()
        testcase_template = self._create_test_case_template()

        multiline_testcase = {
            "requirement": "REQ_MULTILINE",
            "item": 7,
            "tc": 7,
            "id": "7.7.7",
            "description": """This test case has a multi-line description.

It spans multiple lines and includes:
- Important point 1
- Important point 2

And additional details.""",
            "test_sequences": [
                {
                    "id": 1,
                    "name": "Multiline Sequence",
                    "description": """Step-by-step sequence:

1. First step
2. Second step
3. Third step

Each step is important.""",
                    "steps": [
                        {
                            "step": 1,
                            "description": "Single line step",
                            "command": "cmd",
                            "expected": {"result": "OK", "output": "Success\nWith newline"},
                        }
                    ],
                }
            ],
        }
        testcase_file = self._create_test_case_data("multiline_tc.yml", multiline_testcase)

        self._setup_test_plan_md_placeholder(self.temp_dir)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(
            "-o",
            output_file,
            "--container",
            container_schema,
            container_template,
            container_data,
            "--test-case",
            testcase_schema,
            testcase_template,
            testcase_file,
        )

        with open(output_file) as f:
            output_content = f.read()

        verify(
            f"Return Code: {result.returncode}\n\nOutput File:\n{output_content}\n\nStderr:\n{result.stderr}",
            namer=NamerFactory.with_parameters("multiline").namer,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
