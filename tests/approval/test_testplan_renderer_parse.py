#!/usr/bin/env python3
import json
import os
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), Path("..") / ".."))
from testplan_renderer import RendererArgs, TestPlanRendererArgsOutput, parse_and_validate_args  # noqa: E402


class TestParseAndValidateArgsSuccess(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self._create_schema_files()
        self._create_template_files()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _create_schema_files(self):
        """Create valid JSON schema files for testing."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
            "required": ["id", "name"],
        }
        self.container_schema_file = os.path.join(self.temp_dir, "container_schema.json")
        self.test_case_schema_file = os.path.join(self.temp_dir, "testcase_schema.json")
        with open(self.container_schema_file, "w") as f:
            json.dump(schema, f)
        with open(self.test_case_schema_file, "w") as f:
            json.dump(schema, f)

    def _create_template_files(self):
        """Create valid Jinja2 template files for testing."""
        self.container_template_file = os.path.join(self.temp_dir, "container.j2")
        self.test_case_template_file = os.path.join(self.temp_dir, "testcase.j2")
        with open(self.container_template_file, "w") as f:
            f.write("{{ container }}")
        with open(self.test_case_template_file, "w") as f:
            f.write("{{ tc }}")

    def _create_container_data_file(self, filename="container.json"):
        """Create a valid container data file."""
        data = {"id": 1, "name": "Test Container"}
        container_file = os.path.join(self.temp_dir, filename)
        with open(container_file, "w") as f:
            json.dump(data, f)
        return container_file

    def _create_test_case_data_file(self, filename="testcase.json"):
        """Create a valid test case data file."""
        data = {"id": 1, "name": "Test Case"}
        test_case_file = os.path.join(self.temp_dir, filename)
        with open(test_case_file, "w") as f:
            json.dump(data, f)
        return test_case_file

    def test_parse_valid_minimal_args(self):
        """Test parsing with minimal required arguments."""
        container_file = self._create_container_data_file()
        test_case_file = self._create_test_case_data_file()

        # Suppress stdout during parsing
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertIsInstance(result, TestPlanRendererArgsOutput)
        self.assertIsNone(result.output_file)
        self.assertEqual(len(result.test_case_renderers), 1)

    def test_parse_with_output_file(self):
        """Test parsing with output file specified."""
        container_file = self._create_container_data_file()
        test_case_file = self._create_test_case_data_file()
        output_file = os.path.join(self.temp_dir, "output.md")

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "-o",
                    output_file,
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertEqual(result.output_file, Path(output_file))

    def test_parse_with_multiple_test_case_files(self):
        """Test parsing with multiple test case files."""
        container_file = self._create_container_data_file()
        test_case_file1 = self._create_test_case_data_file("testcase1.json")
        test_case_file2 = self._create_test_case_data_file("testcase2.json")

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file1,
                    test_case_file2,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertEqual(len(result.test_case_renderers), 2)
        self.assertEqual(result.test_case_renderers[0].data_file, Path(test_case_file1))
        self.assertEqual(result.test_case_renderers[1].data_file, Path(test_case_file2))

    def test_parse_with_yml_extension(self):
        """Test parsing with .yml file extension."""
        # Create YAML data files with .yml extension
        container_file = os.path.join(self.temp_dir, "container.yml")
        test_case_file = os.path.join(self.temp_dir, "testcase.yml")

        with open(container_file, "w") as f:
            f.write("id: 1\nname: Container\n")
        with open(test_case_file, "w") as f:
            f.write("id: 1\nname: Test Case\n")

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertIsInstance(result, TestPlanRendererArgsOutput)

    def test_parse_container_renderer_has_correct_fields(self):
        """Test that container renderer is properly constructed."""
        container_file = self._create_container_data_file()
        test_case_file = self._create_test_case_data_file()

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        container_renderer = result.container_renderer
        self.assertIsInstance(container_renderer, RendererArgs)
        self.assertEqual(container_renderer.template_file, Path(self.container_template_file))
        self.assertEqual(container_renderer.schema_file, Path(self.container_schema_file))
        self.assertEqual(container_renderer.data_file, Path(container_file))

    def test_parse_test_case_renderers_have_correct_fields(self):
        """Test that test case renderers are properly constructed."""
        container_file = self._create_container_data_file()
        test_case_file = self._create_test_case_data_file()

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        tc_renderer = result.test_case_renderers[0]
        self.assertIsInstance(tc_renderer, RendererArgs)
        self.assertEqual(tc_renderer.template_file, Path(self.test_case_template_file))
        self.assertEqual(tc_renderer.schema_file, Path(self.test_case_schema_file))
        self.assertEqual(tc_renderer.data_file, Path(test_case_file))


class TestParseAndValidateArgsMissingRequired(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_missing_container_flag(self):
        """Test that missing --container flag causes exit."""
        with self.assertRaises(SystemExit):
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--test-case",
                        "schema.json",
                        "template.j2",
                        "testcase.json",
                    ]
                )
            finally:
                sys.stdout = old_stdout

    def test_missing_test_case_flag(self):
        """Test that missing --test-case flag causes exit."""
        with self.assertRaises(SystemExit):
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        "schema.json",
                        "template.j2",
                        "container.json",
                    ]
                )
            finally:
                sys.stdout = old_stdout

    def test_container_missing_file_args(self):
        """Test that --container requires exactly 3 arguments."""
        with self.assertRaises(SystemExit):
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        "schema.json",
                        "template.j2",
                        "--test-case",
                        "schema.json",
                        "template.j2",
                        "testcase.json",
                    ]
                )
            finally:
                sys.stdout = old_stdout

    def test_test_case_missing_minimum_files(self):
        """Test that --test-case requires at least schema, template, and one data file."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        }
        container_schema = os.path.join(self.temp_dir, "container_schema.json")
        test_case_schema = os.path.join(self.temp_dir, "testcase_schema.json")
        container_template = os.path.join(self.temp_dir, "container.j2")
        test_case_template = os.path.join(self.temp_dir, "testcase.j2")
        container_file = os.path.join(self.temp_dir, "container.json")

        with open(container_schema, "w") as f:
            json.dump(schema, f)
        with open(test_case_schema, "w") as f:
            json.dump(schema, f)
        with open(container_template, "w") as f:
            f.write("{{ container }}")
        with open(test_case_template, "w") as f:
            f.write("{{ tc }}")
        with open(container_file, "w") as f:
            json.dump({"id": 1}, f)

        with self.assertRaises(SystemExit):
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        container_schema,
                        container_template,
                        container_file,
                        "--test-case",
                        test_case_schema,
                        test_case_template,
                    ]
                )
            finally:
                sys.stdout = old_stdout


class TestParseAndValidateArgsFileValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self._create_schema_files()
        self._create_template_files()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _create_schema_files(self):
        """Create valid JSON schema files for testing."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
            "required": ["id", "name"],
        }
        self.container_schema_file = os.path.join(self.temp_dir, "container_schema.json")
        self.test_case_schema_file = os.path.join(self.temp_dir, "testcase_schema.json")
        with open(self.container_schema_file, "w") as f:
            json.dump(schema, f)
        with open(self.test_case_schema_file, "w") as f:
            json.dump(schema, f)

    def _create_template_files(self):
        """Create valid Jinja2 template files for testing."""
        self.container_template_file = os.path.join(self.temp_dir, "container.j2")
        self.test_case_template_file = os.path.join(self.temp_dir, "testcase.j2")
        with open(self.container_template_file, "w") as f:
            f.write("{{ container }}")
        with open(self.test_case_template_file, "w") as f:
            f.write("{{ tc }}")

    def test_nonexistent_container_file(self):
        """Test error when container data file doesn't exist."""
        with self.assertRaises(AssertionError) as context:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        self.container_schema_file,
                        self.container_template_file,
                        "/nonexistent/container.json",
                        "--test-case",
                        self.test_case_schema_file,
                        self.test_case_template_file,
                        "/nonexistent/testcase.json",
                    ]
                )
            finally:
                sys.stdout = old_stdout
        self.assertIn("Container file not found", str(context.exception))

    def test_nonexistent_test_case_file(self):
        """Test error when test case data file doesn't exist."""
        container_data = {"id": 1, "name": "Container"}
        container_file = os.path.join(self.temp_dir, "container.json")
        with open(container_file, "w") as f:
            json.dump(container_data, f)

        with self.assertRaises(AssertionError) as context:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        self.container_schema_file,
                        self.container_template_file,
                        container_file,
                        "--test-case",
                        self.test_case_schema_file,
                        self.test_case_template_file,
                        "/nonexistent/testcase.json",
                    ]
                )
            finally:
                sys.stdout = old_stdout
        self.assertIn("File not found", str(context.exception))

    def test_nonexistent_container_template(self):
        """Test error when container template file doesn't exist."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        container_file = os.path.join(self.temp_dir, "container.json")
        test_case_file = os.path.join(self.temp_dir, "testcase.json")
        with open(container_file, "w") as f:
            json.dump(container_data, f)
        with open(test_case_file, "w") as f:
            json.dump(test_case_data, f)

        with self.assertRaises(AssertionError) as context:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        self.container_schema_file,
                        "/nonexistent/container.j2",
                        container_file,
                        "--test-case",
                        self.test_case_schema_file,
                        self.test_case_template_file,
                        test_case_file,
                    ]
                )
            finally:
                sys.stdout = old_stdout
        self.assertIn("Container file not found", str(context.exception))

    def test_nonexistent_container_schema(self):
        """Test error when container schema file doesn't exist."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        container_file = os.path.join(self.temp_dir, "container.json")
        test_case_file = os.path.join(self.temp_dir, "testcase.json")
        with open(container_file, "w") as f:
            json.dump(container_data, f)
        with open(test_case_file, "w") as f:
            json.dump(test_case_data, f)

        with self.assertRaises(AssertionError) as context:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        "/nonexistent/schema.json",
                        self.container_template_file,
                        container_file,
                        "--test-case",
                        self.test_case_schema_file,
                        self.test_case_template_file,
                        test_case_file,
                    ]
                )
            finally:
                sys.stdout = old_stdout
        self.assertIn("Container file not found", str(context.exception))

    def test_invalid_container_data_format(self):
        """Test error when container data file is invalid format."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        invalid_file = os.path.join(self.temp_dir, "invalid.txt")
        test_case_file = os.path.join(self.temp_dir, "testcase.json")
        container_file = os.path.join(self.temp_dir, "container.json")

        with open(invalid_file, "w") as f:
            f.write("invalid content")
        with open(test_case_file, "w") as f:
            json.dump(test_case_data, f)
        with open(container_file, "w") as f:
            json.dump(container_data, f)

        with self.assertRaises(SystemExit):
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        self.container_schema_file,
                        self.container_template_file,
                        invalid_file,
                        "--test-case",
                        self.test_case_schema_file,
                        self.test_case_template_file,
                        test_case_file,
                    ]
                )
            finally:
                sys.stdout = old_stdout

    def test_invalid_template_extension(self):
        """Test error when template file doesn't have .j2 extension."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        container_file = os.path.join(self.temp_dir, "container.json")
        test_case_file = os.path.join(self.temp_dir, "testcase.json")
        invalid_template = os.path.join(self.temp_dir, "template.txt")

        with open(container_file, "w") as f:
            json.dump(container_data, f)
        with open(test_case_file, "w") as f:
            json.dump(test_case_data, f)
        with open(invalid_template, "w") as f:
            f.write("invalid template")

        with self.assertRaises(SystemExit):
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        self.container_schema_file,
                        invalid_template,
                        container_file,
                        "--test-case",
                        self.test_case_schema_file,
                        self.test_case_template_file,
                        test_case_file,
                    ]
                )
            finally:
                sys.stdout = old_stdout


class TestParseAndValidateArgsEdgeCases(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self._create_schema_files()
        self._create_template_files()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _create_schema_files(self):
        """Create valid JSON schema files for testing."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
            "required": ["id", "name"],
        }
        self.container_schema_file = os.path.join(self.temp_dir, "container_schema.json")
        self.test_case_schema_file = os.path.join(self.temp_dir, "testcase_schema.json")
        with open(self.container_schema_file, "w") as f:
            json.dump(schema, f)
        with open(self.test_case_schema_file, "w") as f:
            json.dump(schema, f)

    def _create_template_files(self):
        """Create valid Jinja2 template files for testing."""
        self.container_template_file = os.path.join(self.temp_dir, "container.j2")
        self.test_case_template_file = os.path.join(self.temp_dir, "testcase.j2")
        with open(self.container_template_file, "w") as f:
            f.write("{{ container }}")
        with open(self.test_case_template_file, "w") as f:
            f.write("{{ tc }}")

    def test_duplicate_test_case_files(self):
        """Test error when duplicate test case files are provided."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        container_file = os.path.join(self.temp_dir, "container.json")
        test_case_file = os.path.join(self.temp_dir, "testcase.json")

        with open(container_file, "w") as f:
            json.dump(container_data, f)
        with open(test_case_file, "w") as f:
            json.dump(test_case_data, f)

        with self.assertRaises(AssertionError) as context:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                parse_and_validate_args(
                    [
                        "--container",
                        self.container_schema_file,
                        self.container_template_file,
                        container_file,
                        "--test-case",
                        self.test_case_schema_file,
                        self.test_case_template_file,
                        test_case_file,
                        test_case_file,  # Same file twice
                    ]
                )
            finally:
                sys.stdout = old_stdout
        self.assertIn("Duplicate test case files", str(context.exception))

    def test_output_file_with_spaces(self):
        """Test output file path with spaces."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        container_file = os.path.join(self.temp_dir, "container.json")
        test_case_file = os.path.join(self.temp_dir, "testcase.json")
        output_file = os.path.join(self.temp_dir, "output with spaces.md")

        with open(container_file, "w") as f:
            json.dump(container_data, f)
        with open(test_case_file, "w") as f:
            json.dump(test_case_data, f)

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "-o",
                    output_file,
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertEqual(result.output_file, Path(output_file))

    def test_file_paths_with_special_characters(self):
        """Test file paths with special characters."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        container_file = os.path.join(self.temp_dir, "container-v1.0_test.json")
        test_case_file = os.path.join(self.temp_dir, "testcase-v1.0_test.json")

        with open(container_file, "w") as f:
            json.dump(container_data, f)
        with open(test_case_file, "w") as f:
            json.dump(test_case_data, f)

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertIsInstance(result, TestPlanRendererArgsOutput)

    def test_three_test_case_files(self):
        """Test with three test case files."""
        container_data = {"id": 1, "name": "Container"}
        test_case_data = {"id": 1, "name": "Test Case"}
        container_file = os.path.join(self.temp_dir, "container.json")
        test_case_file1 = os.path.join(self.temp_dir, "testcase1.json")
        test_case_file2 = os.path.join(self.temp_dir, "testcase2.json")
        test_case_file3 = os.path.join(self.temp_dir, "testcase3.json")

        with open(container_file, "w") as f:
            json.dump(container_data, f)
        for f in [test_case_file1, test_case_file2, test_case_file3]:
            with open(f, "w") as file:
                json.dump(test_case_data, file)

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    self.container_schema_file,
                    self.container_template_file,
                    container_file,
                    "--test-case",
                    self.test_case_schema_file,
                    self.test_case_template_file,
                    test_case_file1,
                    test_case_file2,
                    test_case_file3,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertEqual(len(result.test_case_renderers), 3)

    def test_nested_directory_paths(self):
        """Test with nested directory paths."""
        nested_dir = os.path.join(self.temp_dir, "nested", "deep", "path")
        os.makedirs(nested_dir, exist_ok=True)

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
            "required": ["id", "name"],
        }

        container_schema = os.path.join(nested_dir, "container_schema.json")
        test_case_schema = os.path.join(nested_dir, "testcase_schema.json")
        container_template = os.path.join(nested_dir, "container.j2")
        test_case_template = os.path.join(nested_dir, "testcase.j2")
        container_file = os.path.join(nested_dir, "container.json")
        test_case_file = os.path.join(nested_dir, "testcase.json")

        with open(container_schema, "w") as f:
            json.dump(schema, f)
        with open(test_case_schema, "w") as f:
            json.dump(schema, f)
        with open(container_template, "w") as f:
            f.write("{{ container }}")
        with open(test_case_template, "w") as f:
            f.write("{{ tc }}")
        with open(container_file, "w") as f:
            json.dump({"id": 1, "name": "Container"}, f)
        with open(test_case_file, "w") as f:
            json.dump({"id": 1, "name": "Test Case"}, f)

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = parse_and_validate_args(
                [
                    "--container",
                    container_schema,
                    container_template,
                    container_file,
                    "--test-case",
                    test_case_schema,
                    test_case_template,
                    test_case_file,
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertIsInstance(result, TestPlanRendererArgsOutput)


if __name__ == "__main__":
    unittest.main(verbosity=2)
