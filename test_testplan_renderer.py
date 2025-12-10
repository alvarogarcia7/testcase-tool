#!/usr/bin/env python3
import json
import os
import shutil
import tempfile
import unittest

import pytest
from jinja2 import TemplateSyntaxError

from testplan_renderer import TestPlanRenderer


class TestTestPlanRendererInit(unittest.TestCase):
    def test_init_stores_input_file_path(self):
        renderer = TestPlanRenderer("/some/path/testplan.json")
        self.assertEqual(renderer.input_file, "/some/path/testplan.json")

    def test_init_test_plan_is_none(self):
        renderer = TestPlanRenderer("/some/path/testplan.json")
        self.assertIsNone(renderer.test_plan)


class TestLoadTestPlanJSON(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_valid_json_returns_true(self):
        json_content = {
            "id": 1,
            "name": "Test Plan 1",
            "product": "Product A",
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        with open(json_file, "w") as f:
            json.dump(json_content, f)

        renderer = TestPlanRenderer(json_file)
        result = renderer.load_test_plan()

        self.assertTrue(result)

    def test_load_valid_json_populates_test_plan(self):
        json_content = {
            "id": 1,
            "name": "Test Plan 1",
            "product": "Product A",
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        with open(json_file, "w") as f:
            json.dump(json_content, f)

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()

        self.assertEqual(renderer.test_plan["id"], 1)
        self.assertEqual(renderer.test_plan["name"], "Test Plan 1")
        self.assertEqual(renderer.test_plan["product"], "Product A")

    def test_load_nonexistent_json_file_returns_false(self):
        renderer = TestPlanRenderer("/nonexistent/path/test.json")
        result = renderer.load_test_plan()

        self.assertFalse(result)

    def test_load_invalid_json_returns_false(self):
        json_file = os.path.join(self.temp_dir, "invalid.json")
        with open(json_file, "w") as f:
            f.write("{invalid json content")

        renderer = TestPlanRenderer(json_file)
        result = renderer.load_test_plan()

        self.assertFalse(result)

    def test_load_json_with_nested_test_runs(self):
        json_content = {
            "id": 1,
            "name": "Test Plan 1",
            "test_runs": [
                {"id": 101, "summary": "Run 1"},
                {"id": 102, "summary": "Run 2"},
            ],
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        with open(json_file, "w") as f:
            json.dump(json_content, f)

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()

        self.assertEqual(len(renderer.test_plan["test_runs"]), 2)
        self.assertEqual(renderer.test_plan["test_runs"][0]["id"], 101)


class TestLoadTestPlanYAML(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_valid_yaml_returns_true(self):
        yaml_content = """
id: 1
name: Test Plan 1
product: Product A
"""
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        renderer = TestPlanRenderer(yaml_file)
        result = renderer.load_test_plan()

        self.assertTrue(result)

    def test_load_valid_yaml_populates_test_plan(self):
        yaml_content = """
id: 1
name: Test Plan 1
product: Product A
"""
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        renderer = TestPlanRenderer(yaml_file)
        renderer.load_test_plan()

        self.assertEqual(renderer.test_plan["id"], 1)
        self.assertEqual(renderer.test_plan["name"], "Test Plan 1")
        self.assertEqual(renderer.test_plan["product"], "Product A")

    def test_load_yml_extension_works(self):
        yaml_content = """
id: 1
name: Test Plan 1
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        renderer = TestPlanRenderer(yaml_file)
        result = renderer.load_test_plan()

        self.assertTrue(result)

    def test_load_invalid_yaml_returns_false(self):
        yaml_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(yaml_file, "w") as f:
            f.write("invalid: yaml: [unclosed")

        renderer = TestPlanRenderer(yaml_file)
        result = renderer.load_test_plan()

        self.assertFalse(result)

    def test_load_yaml_with_list_test_runs(self):
        yaml_content = """
id: 1
name: Test Plan 1
test_runs:
  - id: 101
    summary: Run 1
  - id: 102
    summary: Run 2
"""
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        renderer = TestPlanRenderer(yaml_file)
        renderer.load_test_plan()

        self.assertEqual(len(renderer.test_plan["test_runs"]), 2)


class TestLoadTestPlanUnsupportedFormat(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_unsupported_format_returns_false(self):
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, "w") as f:
            f.write("Some text content")

        renderer = TestPlanRenderer(txt_file)
        result = renderer.load_test_plan()

        self.assertFalse(result)


class TestRenderWithTemplateString(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_render_without_loaded_test_plan_returns_false(self):
        renderer = TestPlanRenderer("/some/path/test.json")
        template_string = "Plan: {{ plan.name }}"
        result = renderer.render(template_string=template_string)

        self.assertFalse(result)

    def test_render_with_template_string_returns_true(self):
        json_content = {"id": 1, "name": "Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")
        with open(json_file, "w") as f:
            json.dump(json_content, f)

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()

        template_string = "Plan: {{ plan.name }}"
        result = renderer.render(template_string=template_string)

        self.assertTrue(result)

    def test_render_outputs_to_file(self):
        json_content = {"id": 1, "name": "Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()

        template_string = "Plan: {{ plan.name }}"
        renderer.render(template_string=template_string, output_file=output_file)

        self.assertTrue(os.path.exists(output_file))
        with open(output_file) as f:
            content = f.read()
        self.assertEqual(content, "Plan: Test Plan")

    def test_render_without_template_returns_false(self):
        json_content = {"id": 1, "name": "Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")
        with open(json_file, "w") as f:
            json.dump(json_content, f)

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()

        result = renderer.render()

        self.assertFalse(result)


class TestRenderWithTemplateFile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_render_with_template_file_returns_true(self):
        json_content = {"id": 1, "name": "Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")
        template_file = os.path.join(self.temp_dir, "template.j2")

        with open(json_file, "w") as f:
            json.dump(json_content, f)
        with open(template_file, "w") as f:
            f.write("Plan ID: {{ plan.id }}, Name: {{ plan.name }}")

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()

        result = renderer.render(template_path=template_file)

        self.assertTrue(result)

    def test_render_with_nonexistent_template_returns_false(self):
        json_content = {"id": 1, "name": "Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()

        result = renderer.render(template_path="/nonexistent/template.j2")

        self.assertFalse(result)

    def test_render_template_file_to_output_file(self):
        json_content = {"id": 1, "name": "My Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")
        template_file = os.path.join(self.temp_dir, "template.j2")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)
        with open(template_file, "w") as f:
            f.write("# {{ plan.name }}\nID: {{ plan.id }}")

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_path=template_file, output_file=output_file)

        self.assertTrue(os.path.exists(output_file))
        with open(output_file) as f:
            content = f.read()
        self.assertIn("My Test Plan", content)
        self.assertIn("ID: 1", content)


class TestRenderAllTestPlanFields(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_render_all_basic_fields(self):
        json_content = {
            "id": 123,
            "name": "Comprehensive Test Plan",
            "type": "Integration",
            "product": "Product X",
            "version": "2.0",
            "author": "John Doe",
            "create_date": "2024-01-15",
            "text": "This is a detailed test plan description.",
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """
ID: {{ plan.id }}
Name: {{ plan.name }}
Type: {{ plan.type }}
Product: {{ plan.product }}
Version: {{ plan.version }}
Author: {{ plan.author }}
Created: {{ plan.create_date }}
Description: {{ plan.text }}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("ID: 123", content)
        self.assertIn("Name: Comprehensive Test Plan", content)
        self.assertIn("Type: Integration", content)
        self.assertIn("Product: Product X", content)
        self.assertIn("Version: 2.0", content)
        self.assertIn("Author: John Doe", content)
        self.assertIn("Created: 2024-01-15", content)
        self.assertIn("Description: This is a detailed test plan description.", content)

    def test_render_test_runs_list(self):
        json_content = {
            "id": 1,
            "name": "Test Plan",
            "test_runs": [
                {
                    "id": 201,
                    "summary": "First Run",
                    "build": "1.0",
                    "manager": "Alice",
                },
                {
                    "id": 202,
                    "summary": "Second Run",
                    "build": "1.1",
                    "manager": "Bob",
                },
            ],
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """
Test Runs:
{% for run in plan.test_runs %}
- Run {{ run.id }}: {{ run.summary }} (Build: {{ run.build }}, Manager: {{ run.manager }})
{% endfor %}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Run 201: First Run", content)
        self.assertIn("Build: 1.0", content)
        self.assertIn("Manager: Alice", content)
        self.assertIn("Run 202: Second Run", content)

    def test_render_empty_test_runs(self):
        json_content = {"id": 1, "name": "Test Plan", "test_runs": []}
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """
{% if plan.test_runs %}
Has test runs
{% else %}
No test runs
{% endif %}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("No test runs", content)


class TestRenderEdgeCases(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_render_missing_fields_with_defaults(self):
        json_content = {"id": 1}
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """
Name: {{ plan.name|default('Untitled') }}
Product: {{ plan.product|default('N/A') }}
Author: {{ plan.author|default('Unknown') }}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Name: Untitled", content)
        self.assertIn("Product: N/A", content)
        self.assertIn("Author: Unknown", content)

    def test_render_empty_test_plan_data(self):
        json_content = {}
        json_file = os.path.join(self.temp_dir, "test.json")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = "ID: {{ plan.id|default('None') }}"

        renderer = TestPlanRenderer(json_file)
        result = renderer.load_test_plan()

        self.assertTrue(result)
        self.assertEqual(renderer.test_plan, {})

        result = renderer.render(template_string=template_string)
        self.assertFalse(result)

    def test_render_unicode_characters(self):
        json_content = {
            "id": 1,
            "name": "测试计划 🚀",
            "author": "José García",
            "text": "Тестовый план with émojis 😊",
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_content, f, ensure_ascii=False)

        template_string = """
Name: {{ plan.name }}
Author: {{ plan.author }}
Text: {{ plan.text }}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file, encoding="utf-8") as f:
            content = f.read()

        self.assertIn("测试计划 🚀", content)
        self.assertIn("José García", content)
        self.assertIn("Тестовый план with émojis 😊", content)

    def test_render_nested_data_structures(self):
        json_content = {
            "id": 1,
            "name": "Test Plan",
            "test_runs": [
                {
                    "id": 1,
                    "summary": "Run 1",
                    "metadata": {
                        "tags": ["smoke", "regression"],
                        "priority": "high",
                    },
                }
            ],
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """
{% for run in plan.test_runs %}
Run {{ run.id }}: {{ run.summary }}
Priority: {{ run.metadata.priority }}
Tags: {% for tag in run.metadata.tags %}{{ tag }}{% if not loop.last %}, {% endif %}{% endfor %}
{% endfor %}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Priority: high", content)
        self.assertIn("Tags: smoke, regression", content)

    def test_render_null_values(self):
        json_content = {
            "id": 1,
            "name": "Test Plan",
            "author": None,
            "version": None,
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """
Author: {{ plan.author if plan.author is not none else 'N/A' }}
Version: {{ plan.version if plan.version is not none else 'N/A' }}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Author: N/A", content)
        self.assertIn("Version: N/A", content)

    def test_render_special_characters_in_text(self):
        json_content = {
            "id": 1,
            "name": "Test <Plan> with & symbols",
            "text": "Description with \"quotes\" and 'apostrophes'",
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """
Name: {{ plan.name }}
Text: {{ plan.text }}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Test <Plan> with & symbols", content)
        self.assertIn("Description with \"quotes\" and 'apostrophes'", content)


class TestRenderErrorHandling(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_render_with_invalid_template_syntax(self):
        json_content = {"id": 1, "name": "Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = "{{ plan.name"

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        with pytest.raises(TemplateSyntaxError):
            renderer.render(template_string=template_string)

    def test_render_accessing_nonexistent_field_with_default(self):
        json_content = {"id": 1}
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = "Name: {{ plan.nonexistent|default('N/A') }}"

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        result = renderer.render(template_string=template_string, output_file=output_file)

        self.assertTrue(result)
        with open(output_file) as f:
            content = f.read()
        self.assertIn("Name: N/A", content)

    def test_render_to_invalid_output_path(self):
        json_content = {"id": 1, "name": "Test Plan"}
        json_file = os.path.join(self.temp_dir, "test.json")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = "Name: {{ plan.name }}"

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        with pytest.raises(FileNotFoundError):
            renderer.render(
                template_string=template_string,
                output_file="/nonexistent/directory/output.md",
            )


class TestRenderWithDefaultTemplate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_render_with_default_template_file(self):
        json_content = {
            "id": 1,
            "name": "Test Plan Name",
            "type": "Functional",
            "product": "MyProduct",
            "version": "1.0",
            "author": "Test Author",
            "create_date": "2024-01-01",
            "text": "Test plan description",
            "test_runs": [],
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        if os.path.exists("testplan_default.j2"):
            renderer = TestPlanRenderer(json_file)
            renderer.load_test_plan()
            result = renderer.render(template_path="testplan_default.j2", output_file=output_file)

            self.assertTrue(result)
            with open(output_file) as f:
                content = f.read()

            self.assertIn("Test Plan Name", content)
            self.assertIn("Plan ID:", content)
            self.assertIn("MyProduct", content)

    def test_render_with_detailed_template(self):
        json_content = {
            "id": 2,
            "name": "Detailed Test Plan",
            "type": "Integration",
            "product": "Product B",
            "version": "2.1",
            "author": "Jane Doe",
            "create_date": "2024-02-01",
            "text": "Detailed description",
            "test_runs": [
                {
                    "id": 101,
                    "summary": "Test Run 1",
                    "plan": 2,
                    "build": "Build 1",
                    "manager": "Manager 1",
                    "default_tester": "Tester 1",
                    "start_date": "2024-02-05",
                    "stop_date": "2024-02-10",
                    "notes": "Some notes",
                }
            ],
        }
        json_file = os.path.join(self.temp_dir, "test.json")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        if os.path.exists("testplan_detailed.j2"):
            renderer = TestPlanRenderer(json_file)
            renderer.load_test_plan()
            result = renderer.render(template_path="testplan_detailed.j2", output_file=output_file)

            self.assertTrue(result)
            with open(output_file) as f:
                content = f.read()

            self.assertIn("Detailed Test Plan", content)
            self.assertIn("Test Run 1", content)
            self.assertIn("Build 1", content)


class TestIntegrationWithRealData(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_full_workflow_json_to_markdown(self):
        test_plan_data = {
            "id": 100,
            "name": "Integration Test Plan",
            "type": "Regression",
            "product": "WebApp",
            "version": "3.0.0",
            "author": "Integration Tester",
            "create_date": "2024-01-15T10:30:00Z",
            "text": "Comprehensive integration test plan for WebApp 3.0",
            "test_runs": [
                {
                    "id": 1001,
                    "summary": "Smoke Test Run",
                    "plan": 100,
                    "build": "3.0.0-alpha",
                    "manager": "Alice Smith",
                    "default_tester": "Bob Jones",
                    "start_date": "2024-01-20",
                    "stop_date": "2024-01-21",
                    "planned_start": "2024-01-20T09:00:00",
                    "planned_stop": "2024-01-21T17:00:00",
                    "notes": "Initial smoke testing",
                },
                {
                    "id": 1002,
                    "summary": "Full Regression Run",
                    "plan": 100,
                    "build": "3.0.0-beta",
                    "manager": "Carol White",
                    "default_tester": "Dave Brown",
                    "start_date": "2024-01-25",
                    "stop_date": None,
                    "planned_start": "2024-01-25T09:00:00",
                    "planned_stop": "2024-02-01T17:00:00",
                    "notes": "Complete regression testing suite",
                },
            ],
        }

        json_file = os.path.join(self.temp_dir, "integration_plan.json")
        output_file = os.path.join(self.temp_dir, "integration_plan.md")

        with open(json_file, "w") as f:
            json.dump(test_plan_data, f, indent=2)

        renderer = TestPlanRenderer(json_file)
        self.assertTrue(renderer.load_test_plan())

        template_string = """# Test Plan: {{ plan.name }}

**Plan ID:** {{ plan.id }}
**Type:** {{ plan.type }}
**Product:** {{ plan.product }} v{{ plan.version }}
**Author:** {{ plan.author }}
**Created:** {{ plan.create_date }}

## Description

{{ plan.text }}

## Test Runs

{% if plan.test_runs %}
Total Runs: {{ plan.test_runs|length }}

{% for run in plan.test_runs %}
### Run {{ loop.index }}: {{ run.summary }}

- **Run ID:** {{ run.id }}
- **Build:** {{ run.build }}
- **Manager:** {{ run.manager }}
- **Tester:** {{ run.default_tester }}
- **Dates:** {{ run.start_date }} to {{ run.stop_date|default('In Progress') }}
{% if run.notes %}
- **Notes:** {{ run.notes }}
{% endif %}

{% endfor %}
{% else %}
No test runs defined.
{% endif %}
"""

        self.assertTrue(renderer.render(template_string=template_string, output_file=output_file))

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Integration Test Plan", content)
        self.assertIn("100", content)
        self.assertIn("Regression", content)
        self.assertIn("WebApp v3.0.0", content)
        self.assertIn("Total Runs: 2", content)
        self.assertIn("Smoke Test Run", content)
        self.assertIn("Full Regression Run", content)
        self.assertIn("Alice Smith", content)
        self.assertIn("Dave Brown", content)
        self.assertIn("2024-01-25 to None", content)

    def test_full_workflow_yaml_to_markdown(self):
        yaml_content = """
id: 200
name: YAML Test Plan
type: Unit
product: API Gateway
version: 1.5.0
author: YAML Tester
create_date: 2024-03-01
text: |
  Multi-line description
  of the test plan
  with several lines.
test_runs:
  - id: 2001
    summary: Unit Test Suite
    plan: 200
    build: 1.5.0-rc1
    manager: Manager A
    default_tester: Tester A
    start_date: 2024-03-05
    stop_date: 2024-03-06
  - id: 2002
    summary: Integration Test Suite
    plan: 200
    build: 1.5.0-rc2
    manager: Manager B
    default_tester: Tester B
    start_date: 2024-03-10
    stop_date: 2024-03-12
"""
        yaml_file = os.path.join(self.temp_dir, "yaml_plan.yml")
        output_file = os.path.join(self.temp_dir, "yaml_plan.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        renderer = TestPlanRenderer(yaml_file)
        self.assertTrue(renderer.load_test_plan())

        template_string = """# {{ plan.name }}

ID: {{ plan.id }} | Type: {{ plan.type }} | Product: {{ plan.product }}

{{ plan.text }}

## Test Runs ({{ plan.test_runs|length }})

{% for run in plan.test_runs %}
{{ loop.index }}. **{{ run.summary }}** (ID: {{ run.id }})
   - Build: {{ run.build }}
   - Period: {{ run.start_date }} - {{ run.stop_date }}
   - Team: {{ run.manager }} / {{ run.default_tester }}

{% endfor %}
"""

        self.assertTrue(renderer.render(template_string=template_string, output_file=output_file))

        with open(output_file) as f:
            content = f.read()

        self.assertIn("YAML Test Plan", content)
        self.assertIn("ID: 200", content)
        self.assertIn("API Gateway", content)
        self.assertIn("Multi-line description", content)
        self.assertIn("Unit Test Suite", content)
        self.assertIn("Integration Test Suite", content)
        self.assertIn("Test Runs (2)", content)

    def test_minimal_test_plan(self):
        json_content = {"id": 1, "name": "Minimal Plan"}
        json_file = os.path.join(self.temp_dir, "minimal.json")
        output_file = os.path.join(self.temp_dir, "minimal.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """# {{ plan.name|default('Untitled') }}

**ID:** {{ plan.id|default('N/A') }}
**Type:** {{ plan.type|default('Not specified') }}
**Product:** {{ plan.product|default('Not specified') }}
**Version:** {{ plan.version|default('Not specified') }}
**Author:** {{ plan.author|default('Unknown') }}

## Description
{{ plan.text|default('No description provided.') }}

## Test Runs
{% if plan.test_runs %}
Total: {{ plan.test_runs|length }}
{% else %}
No test runs associated with this plan.
{% endif %}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Minimal Plan", content)
        self.assertIn("1", content)
        self.assertIn("Not specified", content)
        self.assertIn("No description provided.", content)
        self.assertIn("No test runs associated", content)

    def test_complex_nested_test_plan(self):
        json_content = {
            "id": 999,
            "name": "Complex Nested Plan",
            "product": "Enterprise System",
            "test_runs": [
                {
                    "id": 1,
                    "summary": "Run with nested data",
                    "metadata": {
                        "priority": 1,
                        "tags": ["critical", "p0"],
                        "environment": {"os": "Linux", "browser": "Chrome"},
                    },
                }
            ],
        }
        json_file = os.path.join(self.temp_dir, "complex.json")
        output_file = os.path.join(self.temp_dir, "complex.md")

        with open(json_file, "w") as f:
            json.dump(json_content, f)

        template_string = """# {{ plan.name }}

{% for run in plan.test_runs %}
## {{ run.summary }}
{% if run.metadata %}
- Priority: {{ run.metadata.priority }}
- Tags: {{ run.metadata.tags|join(', ') }}
- Environment: {{ run.metadata.environment.os }} / {{ run.metadata.environment.browser }}
{% endif %}
{% endfor %}
"""

        renderer = TestPlanRenderer(json_file)
        renderer.load_test_plan()
        renderer.render(template_string=template_string, output_file=output_file)

        with open(output_file) as f:
            content = f.read()

        self.assertIn("Complex Nested Plan", content)
        self.assertIn("Priority: 1", content)
        self.assertIn("Tags: critical, p0", content)
        self.assertIn("Environment: Linux / Chrome", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
