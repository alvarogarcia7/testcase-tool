#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import approvaltests.approvals
from approvaltests import verify
from approvaltests.namer import NamerFactory
from approvaltests.reporters import PythonNativeReporter  # , ReporterThatAutomaticallyApproves


class TestPlanRendererApprovalTests(unittest.TestCase):
    """End-to-end approval tests for testplan_renderer.py CLI."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.maxDiff = None
        approvaltests.approvals.set_default_reporter(PythonNativeReporter())
        # approvaltests.approvals.set_default_reporter(ReporterThatAutomaticallyApproves())

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

    def _create_test_plan_json(self, filename, data):
        """Create a test plan JSON file in temp directory."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath

    def _create_test_plan_yaml(self, filename, content):
        """Create a test plan YAML file in temp directory."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def _create_custom_template(self, filename, content):
        """Create a custom template file in temp directory."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def test_render_with_default_template_and_real_data(self):
        """Test rendering exported_testplans.json with default template."""
        verify(self._run_cli("exported_testplans.json"))

    def test_render_with_default_template_to_file(self):
        """Test rendering to output file with default template."""
        test_data = {
            "id": 1001,
            "name": "Sample Test Plan",
            "type": "Functional",
            "product": "MyApp",
            "version": "1.0",
            "author": "John Doe",
            "create_date": "2024-01-15",
            "text": "This is a sample test plan for approval testing.",
            "test_runs": [
                {"id": 101, "summary": "Test Run 1"},
                {"id": 102, "summary": "Test Run 2"},
            ],
        }

        input_file = self._create_test_plan_json("testplan.json", test_data)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(input_file, output_file)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            content = f.read()
        verify(content)

    def test_render_with_detailed_template(self):
        """Test rendering with testplan_detailed.j2 template."""
        test_data = {
            "id": 2001,
            "name": "Detailed Test Plan",
            "type": "Integration",
            "product": "WebApp",
            "version": "2.5",
            "author": "Jane Smith",
            "create_date": "2024-02-20",
            "text": "Comprehensive test plan with detailed information.",
            "test_runs": [
                {
                    "id": 201,
                    "summary": "Integration Test Run",
                    "plan": 2001,
                    "build": "2.5.0-beta1",
                    "manager": "Alice Manager",
                    "default_tester": "Bob Tester",
                    "start_date": "2024-02-25",
                    "stop_date": "2024-02-28",
                    "planned_start": "2024-02-25T09:00:00",
                    "planned_stop": "2024-02-28T17:00:00",
                    "notes": "Critical integration tests for release.",
                }
            ],
        }

        input_file = self._create_test_plan_json("testplan.json", test_data)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(input_file, output_file, "--template", "testplan_detailed.j2")

        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            content = f.read()
        verify(content)

    def test_render_with_custom_template(self):
        """Test rendering with a custom template."""
        # approvaltests.approvals.set_default_reporter(ReporterThatAutomaticallyApproves())
        test_data = {"id": 3001, "name": "Custom Template Plan", "product": "CustomProduct", "version": "3.0"}

        custom_template = """Plan ID: {{ plan.id }}
Plan Name: {{ plan.name }}
Product: {{ plan.product }}
Version: {{ plan.version }}
"""

        input_file = self._create_test_plan_json("testplan.json", test_data)
        template_file = self._create_custom_template("custom.j2", custom_template)
        output_file = os.path.join(self.temp_dir, "output.txt")

        result = self._run_cli_result(input_file, output_file, "--template", template_file)

        self.assertEqual(0, result.returncode)

        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)
        with open(output_file) as f:
            content = f.read()
        verify(content, namer=NamerFactory.with_parameters("output").namer)

    def test_render_yaml_input_with_default_template(self):
        """Test rendering YAML input file."""
        yaml_content = """id: 4001
name: YAML Test Plan
type: Unit Test
product: YAML App
version: 1.2.3
author: YAML Author
create_date: "2024-03-10"
text: |
  Multi-line description
  of the YAML test plan.
test_runs:
  - id: 401
    summary: First YAML Run
  - id: 402
    summary: Second YAML Run
"""

        input_file = self._create_test_plan_yaml("testplan.yaml", yaml_content)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(input_file, output_file)

        self.assertEqual(0, result.returncode)

        with open(output_file) as f:
            content = f.read()
        verify(content)

    def test_render_minimal_test_plan(self):
        """Test rendering with minimal fields."""
        test_data = {"id": 5001, "name": "Minimal Plan"}

        input_file = self._create_test_plan_json("minimal.json", test_data)

        verify(self._run_cli(input_file))

    def test_render_empty_test_runs_list(self):
        """Test rendering with empty test_runs list."""
        test_data = {
            "id": 6001,
            "name": "Plan Without Runs",
            "type": "Smoke",
            "product": "TestProduct",
            "version": "1.0",
            "author": "Tester",
            "create_date": "2024-04-01",
            "text": "Test plan with no test runs.",
            "test_runs": [],
        }

        input_file = self._create_test_plan_json("empty_runs.json", test_data)

        verify(self._run_cli(input_file))

    def test_render_missing_optional_fields(self):
        """Test rendering with missing optional fields."""
        test_data = {
            "id": 7001,
            "name": "Plan with Missing Fields",
            "test_runs": [{"id": 701, "summary": "Run 1"}, {"id": 702}],
        }

        input_file = self._create_test_plan_json("missing_fields.json", test_data)

        verify(self._run_cli(input_file))

    def test_render_with_null_values(self):
        """Test rendering with null values in fields."""
        test_data = {
            "id": 8001,
            "name": "Plan with Nulls",
            "type": None,
            "product": "NullProduct",
            "version": None,
            "author": None,
            "create_date": "2024-05-01",
            "text": None,
            "test_runs": [{"id": 801, "summary": "Run with nulls", "build": None, "manager": None}],
        }

        input_file = self._create_test_plan_json("null_values.json", test_data)

        result = self._run_cli_result(input_file)

        self.assertEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_render_with_unicode_characters(self):
        """Test rendering with unicode and special characters."""
        test_data = {
            "id": 9001,
            "name": "测试计划 🚀",
            "type": "Тест",
            "product": "Produit",
            "version": "1.0",
            "author": "José García",
            "create_date": "2024-06-01",
            "text": "Description with émojis 😊 and 中文字符",
            "test_runs": [{"id": 901, "summary": "Тестовый прогон with symbols: @#$%"}],
        }

        input_file = self._create_test_plan_json("unicode.json", test_data)

        result = self._run_cli_result(input_file)

        self.assertEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_render_with_special_html_characters(self):
        """Test rendering with HTML special characters."""
        test_data = {
            "id": 10001,
            "name": 'Plan with <HTML> & "quotes"',
            "type": "Type with 'apostrophes'",
            "product": "Product & Co.",
            "version": "1.0",
            "author": "Author <test@example.com>",
            "text": "Text with <b>tags</b> and & symbols",
        }

        input_file = self._create_test_plan_json("html_chars.json", test_data)

        result = self._run_cli_result(input_file)

        self.assertEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_render_with_nested_data_structures(self):
        """Test rendering with deeply nested data."""
        test_data = {
            "id": 11001,
            "name": "Nested Data Plan",
            "product": "NestedApp",
            "test_runs": [
                {
                    "id": 1101,
                    "summary": "Complex Run",
                    "metadata": {
                        "priority": 1,
                        "tags": ["critical", "regression", "p0"],
                        "environment": {"os": "Linux", "browser": "Chrome", "version": "120"},
                        "configuration": {"timeout": 3600, "retries": 3, "parallel": True},
                    },
                }
            ],
        }

        custom_template = """# {{ plan.name }}

{% for run in plan.test_runs %}
## {{ run.summary }}
{% if run.metadata %}
- Priority: {{ run.metadata.priority }}
- Tags: {{ run.metadata.tags|join(', ') }}
- OS: {{ run.metadata.environment.os }}
- Browser: {{ run.metadata.environment.browser }} v{{ run.metadata.environment.version }}
- Config: timeout={{ run.metadata.configuration.timeout }}, retries={{ run.metadata.configuration.retries }}
{% endif %}
{% endfor %}
"""

        input_file = self._create_test_plan_json("nested.json", test_data)
        template_file = self._create_custom_template("nested.j2", custom_template)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(input_file, output_file, "--template", template_file)

        self.assertEqual(0, result.returncode)

        # verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

        with open(output_file) as f:
            content = f.read()
        verify(content, namer=NamerFactory.with_parameters("output").namer)

    def test_render_large_test_runs_list(self):
        """Test rendering with many test runs."""
        test_runs = [{"id": 12000 + i, "summary": f"Test Run {i+1}"} for i in range(50)]

        test_data = {
            "id": 12001,
            "name": "Large Test Plan",
            "product": "LargeApp",
            "version": "1.0",
            "test_runs": test_runs,
        }

        input_file = self._create_test_plan_json("large.json", test_data)

        verify(self._run_cli(input_file))

    def test_error_nonexistent_input_file(self):
        """Test error handling for nonexistent input file."""
        result = self._run_cli_result("/nonexistent/file.json")

        self.assertNotEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_error_invalid_json_format(self):
        """Test error handling for malformed JSON."""
        malformed_file = os.path.join(self.temp_dir, "malformed.json")
        with open(malformed_file, "w") as f:
            f.write("{invalid json content")

        result = self._run_cli_result(malformed_file)

        self.assertNotEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_error_invalid_yaml_format(self):
        """Test error handling for malformed YAML."""
        malformed_file = os.path.join(self.temp_dir, "malformed.yaml")
        with open(malformed_file, "w") as f:
            f.write("invalid: yaml: [unclosed")

        result = self._run_cli_result(malformed_file)

        self.assertNotEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_error_unsupported_file_format(self):
        """Test error handling for unsupported file format."""
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, "w") as f:
            f.write("plain text content")

        result = self._run_cli_result(txt_file)

        self.assertNotEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_error_nonexistent_template_file(self):
        """Test error handling for nonexistent template file."""
        test_data = {"id": 1, "name": "Test Plan"}
        input_file = self._create_test_plan_json("test.json", test_data)

        result = self._run_cli_result(input_file, "--template", "/nonexistent/template.j2")

        self.assertNotEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_error_invalid_template_syntax(self):
        """Test error handling for template with invalid syntax."""
        test_data = {"id": 1, "name": "Test Plan"}
        input_file = self._create_test_plan_json("test.json", test_data)

        invalid_template = "{{ plan.name"
        template_file = self._create_custom_template("invalid.j2", invalid_template)

        result = self._run_cli_result(input_file, "--template", template_file)

        self.assertNotEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_error_no_arguments(self):
        """Test error handling when no arguments provided."""
        result = self._run_cli_result()

        self.assertNotEqual(0, result.returncode)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)
        verify(result.stderr, namer=NamerFactory.with_parameters("stderr").namer)

    def test_render_with_multi_line_text_field(self):
        """Test rendering with multi-line text descriptions."""
        test_data = {
            "id": 13001,
            "name": "Multi-line Description Plan",
            "product": "MultiLineApp",
            "text": """This is a multi-line description.

It contains multiple paragraphs.

- Bullet point 1
- Bullet point 2
- Bullet point 3

And some final text.""",
            "test_runs": [
                {
                    "id": 1301,
                    "summary": "Run with notes",
                    "notes": """These are multi-line notes.

Step 1: Do something
Step 2: Do something else
Step 3: Verify results""",
                }
            ],
        }

        input_file = self._create_test_plan_json("multiline.json", test_data)

        verify(self._run_cli(input_file))

    def test_render_real_exported_testplans_with_detailed_template(self):
        """Test rendering real exported_testplans.json with detailed template."""
        output_file = os.path.join(self.temp_dir, "real_detailed.md")

        result = self._run_cli_result("exported_testplans.json", output_file, "--template", "testplan_detailed.j2")

        self.assertEqual(result.returncode, 0)

        with open(output_file) as f:
            content = f.read()
        verify(content)

    def test_render_with_custom_markdown_format(self):
        """Test rendering with custom markdown formatting template."""
        test_data = {
            "id": 14001,
            "name": "Custom Markdown Plan",
            "type": "System Test",
            "product": "MarkdownApp",
            "version": "2.0",
            "author": "Markdown Author",
            "test_runs": [
                {"id": 1401, "summary": "First Run", "build": "2.0.1"},
                {"id": 1402, "summary": "Second Run", "build": "2.0.2"},
                {"id": 1403, "summary": "Third Run", "build": "2.0.3"},
            ],
        }

        custom_template = """---
title: {{ plan.name }}
id: {{ plan.id }}
---

# {{ plan.name }}

> **Type:** {{ plan.type|default('N/A') }}
> **Product:** {{ plan.product|default('N/A') }} ({{ plan.version|default('N/A') }})
> **Author:** {{ plan.author|default('Unknown') }}

## Test Runs

| # | Run ID | Summary | Build |
|---|--------|---------|-------|
{% for run in plan.test_runs -%}
| {{ loop.index }} | {{ run.id }} | {{ run.summary|default('N/A') }} | {{ run.build|default('N/A') }} |
{% endfor -%}

Total: **{{ plan.test_runs|length if plan.test_runs else 0 }}** test runs
"""

        input_file = self._create_test_plan_json("markdown.json", test_data)
        template_file = self._create_custom_template("markdown.j2", custom_template)
        output_file = os.path.join(self.temp_dir, "output.md")

        result = self._run_cli_result(input_file, output_file, "--template", template_file)

        self.assertEqual(result.returncode, 0)

        with open(output_file) as f:
            content = f.read()
        verify(content)

    def test_render_with_json_list_input(self):
        """Test rendering when input is a JSON list (array of test plans)."""
        if not os.path.exists("exported_testplans.json"):
            with open("exported_testplans.json") as f:
                content = f.read()
                if content.strip().startswith("["):
                    custom_template = """{% if plan is iterable and plan is not mapping %}
{% for p in plan %}
# Test Plan: {{ p.name|default('Untitled') }}
- ID: {{ p.id|default('N/A') }}
- Product: {{ p.product__name|default(p.product)|default('N/A') }}
- Type: {{ p.type__name|default(p.type)|default('N/A') }}
- Author: {{ p.author__username|default(p.author)|default('N/A') }}

{% endfor %}
{% else %}
# Test Plan: {{ plan.name|default('Untitled') }}
- ID: {{ plan.id|default('N/A') }}
{% endif %}
"""
                    template_file = self._create_custom_template("list.j2", custom_template)
                    output_file = os.path.join(self.temp_dir, "list_output.md")

                    result = self._run_cli_result("exported_testplans.json", output_file, "--template", template_file)

                    assert result.returncode == 0

                    with open(output_file) as f:
                        file_content = f.read()
                    verify(file_content, namer=NamerFactory.with_parameters("list_output").namer)

        test_data = [
            {"id": 15001, "name": "First Plan", "product": "Product1"},
            {"id": 15002, "name": "Second Plan", "product": "Product2"},
        ]

        input_file = self._create_test_plan_json("list.json", test_data)

        custom_template = """{% if plan is iterable and plan is not mapping %}
{% for p in plan %}
Plan {{ loop.index }}: {{ p.name }} (ID: {{ p.id }})
{% endfor %}
{% else %}
Single Plan: {{ plan.name }}
{% endif %}
"""
        template_file = self._create_custom_template("list.j2", custom_template)

        result = self._run_cli_result(input_file, "--template", template_file)

        self.assertEqual(result.returncode, 0)

        verify(result.stdout, namer=NamerFactory.with_parameters("stdout").namer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
