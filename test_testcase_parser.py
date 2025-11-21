#!/usr/bin/env python3
"""
Unit tests for TestCaseParser using Python's built-in unittest module.
No external dependencies required.
"""

import os
import shutil
import tempfile
import unittest

from testcase_parser import TestCaseParser


class TestTestCaseParserInit(unittest.TestCase):
    """Tests for TestCaseParser initialization"""

    def test_init_stores_yaml_file_path(self):
        """Parser should store the yaml file path"""
        parser = TestCaseParser("/some/path/test.yml")
        self.assertEqual(parser.yaml_file, "/some/path/test.yml")

    def test_init_test_case_is_none(self):
        """Parser should initialize with test_case as None"""
        parser = TestCaseParser("/some/path/test.yml")
        self.assertIsNone(parser.test_case)

    def test_init_actual_log_is_none(self):
        """Parser should initialize with actual_log as None"""
        parser = TestCaseParser("/some/path/test.yml")
        self.assertIsNone(parser.actual_log)


class TestLoadTestCase(unittest.TestCase):
    """Tests for load_test_case method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_load_valid_yaml_returns_true(self):
        """Loading a valid YAML file should return True"""
        yaml_content = """
id: X20_I1_TC1
description: Test description
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        result = parser.load_test_case()

        self.assertTrue(result)

    def test_load_valid_yaml_populates_test_case(self):
        """Loading a valid YAML file should populate test_case attribute"""
        yaml_content = """
id: X20_I1_TC1
description: Test description
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()

        self.assertEqual(parser.test_case["id"], "X20_I1_TC1")
        self.assertEqual(parser.test_case["description"], "Test description")

    def test_load_nonexistent_file_returns_false(self):
        """Loading a non-existent file should return False"""
        parser = TestCaseParser("/nonexistent/path/test.yml")
        result = parser.load_test_case()

        self.assertFalse(result)

    def test_load_invalid_yaml_returns_false(self):
        """Loading an invalid YAML file should return False"""
        yaml_file = os.path.join(self.temp_dir, "invalid.yml")
        with open(yaml_file, "w") as f:
            f.write("invalid: yaml: content: [")

        parser = TestCaseParser(yaml_file)
        result = parser.load_test_case()

        self.assertFalse(result)

    def test_load_yaml_with_prerequisites_list(self):
        """YAML with prerequisites list should be loaded correctly"""
        yaml_content = """
id: X20_I1_TC1
prerequisites:
  - Python 3.8+ installed
  - Network access
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()

        self.assertEqual(len(parser.test_case["prerequisites"]), 2)
        self.assertEqual(parser.test_case["prerequisites"][0], "Python 3.8+ installed")


class TestLoadActualLog(unittest.TestCase):
    """Tests for load_actual_log method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_returns_false_when_no_test_case_loaded(self):
        """Should return False if no test case is loaded"""
        parser = TestCaseParser("/some/path/test.yml")
        result = parser.load_actual_log()

        self.assertFalse(result)

    def test_returns_false_when_no_actual_result_section(self):
        """Should return False if test case has no actual_result section"""
        yaml_content = """
id: X20_I1_TC1
description: Test without actual_result
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.load_actual_log()

        self.assertFalse(result)

    def test_returns_false_when_log_file_empty(self):
        """Should return False if log_file path is empty"""
        yaml_content = """
id: X20_I1_TC1
actual_result:
  log_file: ""
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.load_actual_log()

        self.assertFalse(result)

    def test_returns_false_when_log_file_not_found(self):
        """Should return False if log file doesn't exist"""
        yaml_content = """
id: X20_I1_TC1
actual_result:
  log_file: nonexistent.log
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)
        actual_log = os.path.join(self.temp_dir, "test.actual.log")
        with open(yaml_file, "w") as f:
            f.write("LOG LOG LOG")

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.load_actual_log()

        self.assertFalse(result)

    def test_loads_valid_log_file(self):
        """Should load valid log file and return True"""
        yaml_content = """
id: X20_I1_TC1
actual_result:
  log_file: test.log
"""
        log_content = """
execution_log:
  - step: 1
    description: First step
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        log_file = os.path.join(self.temp_dir, "test.log")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)
        with open(log_file, "w") as f:
            f.write(log_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.load_actual_log()

        self.assertTrue(result)
        self.assertIsNotNone(parser.actual_log)


class TestGenerateShellScript(unittest.TestCase):
    """Tests for generate_shell_script method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_returns_false_when_no_test_case_loaded(self):
        """Should return False if no test case is loaded"""
        parser = TestCaseParser("/some/path/test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")
        result = parser.generate_shell_script(output_file)

        self.assertFalse(result)

    def test_generates_script_with_shebang(self):
        """Generated script should start with bash shebang"""
        yaml_content = """
id: X20_I1_TC1
requirement_id: REQ001
description: Test description
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_shell_script(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertTrue(content.startswith("#!/bin/bash"))

    def test_generates_script_with_testcase_id(self):
        """Generated script should contain the test case ID"""
        yaml_content = """
id: TC_UNIQUE_123
requirement_id: REQ001
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_shell_script(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("TC_UNIQUE_123", content)

    def test_script_is_executable(self):
        """Generated script should have executable permissions"""
        yaml_content = """
id: X20_I1_TC1
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_shell_script(output_file)

        # Check if file has executable permission
        self.assertTrue(os.access(output_file, os.X_OK))

    def test_generates_prerequisites_section(self):
        """Script should contain prerequisites check when prerequisites exist"""
        yaml_content = """
id: X20_I1_TC1
prerequisites:
  - Python installed
  - Docker running
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_shell_script(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("PREREQUISITES CHECK", content)
        self.assertIn("Python installed", content)
        self.assertIn("Docker running", content)

    def test_generates_commands_section(self):
        """Script should contain commands from test case"""
        yaml_content = """
id: X20_I1_TC1
commands:
  - step: 1
    description: Run test command
    commands:
      - echo "Hello World"
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_shell_script(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("TEST EXECUTION", content)
        self.assertIn('echo "Hello World"', content)

    def test_returns_true_on_success(self):
        """Should return True when script is generated successfully"""
        yaml_content = """
id: X20_I1_TC1
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.generate_shell_script(output_file)

        self.assertTrue(result)


class TestGenerateMarkdown(unittest.TestCase):
    """Tests for generate_markdown method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_returns_false_when_no_test_case_loaded(self):
        """Should return False if no test case is loaded"""
        parser = TestCaseParser("/some/path/test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")
        result = parser.generate_markdown(output_file)

        self.assertFalse(result)

    def test_generates_markdown_with_title(self):
        """Generated markdown should have test case ID as title"""
        yaml_content = """
id: X20_I1_TC1
requirement_id: REQ001
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("# Test Case: X20_I1_TC1", content)

    def test_generates_markdown_with_requirement_id(self):
        """Generated markdown should contain requirement ID"""
        yaml_content = """
id: X20_I1_TC1
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

    def test_generates_markdown_with_description(self):
        """Generated markdown should contain description section"""
        yaml_content = """
id: X20_I1_TC1
description: This is a test description
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("## Description", content)
        self.assertIn("This is a test description", content)

    def test_generates_markdown_with_prerequisites(self):
        """Generated markdown should list prerequisites"""
        yaml_content = """
id: X20_I1_TC1
prerequisites:
  - First prerequisite
  - Second prerequisite
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("## Prerequisites", content)
        self.assertIn("- First prerequisite", content)
        self.assertIn("- Second prerequisite", content)

    def test_generates_markdown_with_test_steps(self):
        """Generated markdown should contain test steps"""
        yaml_content = """
id: X20_I1_TC1
commands:
  - step: 1
    description: Execute first step
    commands:
      - echo "step 1"
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("## Test Steps", content)
        self.assertIn("### Step 1: Execute first step", content)

    def test_generates_markdown_with_metadata_tags(self):
        """Generated markdown should contain metadata tags"""
        yaml_content = """
id: X20_I1_TC1
metadata:
  tags:
    - smoke
    - regression
  categories:
    - unit
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("smoke", content)
        self.assertIn("regression", content)

    def test_generates_markdown_with_expected_result(self):
        """Generated markdown should contain expected result section"""
        yaml_content = """
id: X20_I1_TC1
expected_result:
  description: Should succeed
  expected_outputs:
    - field: status_code
      value: "0"
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("## Expected Result", content)
        self.assertIn("Should succeed", content)

    def test_returns_true_on_success(self):
        """Should return True when markdown is generated successfully"""
        yaml_content = """
id: X20_I1_TC1
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.generate_markdown(output_file)

        self.assertTrue(result)


class TestVerificationSection(unittest.TestCase):
    """Tests for verification section in markdown generation"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_generates_verification_status_pass(self):
        """Should show PASS status"""
        yaml_content = """
id: X20_I1_TC1
verification:
  status: PASS
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("## Verification Results", content)
        self.assertIn("PASS", content)

    def test_generates_verification_status_fail(self):
        """Should show FAIL status"""
        yaml_content = """
id: X20_I1_TC1
verification:
  status: FAIL
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("FAIL", content)

    def test_generates_verification_steps_table(self):
        """Should generate verification steps as table"""
        yaml_content = """
id: X20_I1_TC1
verification:
  status: PASS
  verification_steps:
    - check: Output matches expected
      result: PASS
    - check: Exit code is 0
      result: PASS
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("| Check | Result |", content)
        self.assertIn("Output matches expected", content)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_handles_empty_yaml_file(self):
        """Should handle empty YAML file gracefully"""
        yaml_file = os.path.join(self.temp_dir, "empty.yml")
        with open(yaml_file, "w") as f:
            f.write("")

        parser = TestCaseParser(yaml_file)
        result = parser.load_test_case()

        # Empty YAML loads as None, but function returns True
        self.assertTrue(result)
        self.assertIsNone(parser.test_case)

    def test_handles_multiline_description(self):
        """Should handle multiline description correctly"""
        yaml_content = """
id: X20_I1_TC1
description: |
  This is a multiline
  description that spans
  multiple lines
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_markdown(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("multiline", content)

    def test_handles_missing_optional_fields(self):
        """Should handle YAML with only required fields"""
        yaml_content = """
id: X20_I1_TC1
"""
        yaml_file = os.path.join(self.temp_dir, "minimal.yml")
        output_sh = os.path.join(self.temp_dir, "output.sh")
        output_md = os.path.join(self.temp_dir, "output.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()

        # Both should succeed
        self.assertTrue(parser.generate_shell_script(output_sh))
        self.assertTrue(parser.generate_markdown(output_md))

    def test_handles_multiline_commands(self):
        """Should handle multiline commands in shell script"""
        yaml_content = """
id: X20_I1_TC1
commands:
  - step: 1
    description: Multi-line command
    commands:
      - |
        for i in 1 2 3; do
          echo $i
        done
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        parser.generate_shell_script(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("for i in 1 2 3", content)
        self.assertIn("echo $i", content)


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflow"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_full_workflow_with_complete_yaml(self):
        """Test full parsing workflow with comprehensive YAML"""
        yaml_content = """
id: INT_001
requirement_id: REQ_INTEGRATION
metadata:
  tags:
    - integration
    - smoke
  categories:
    - e2e
description: Integration test for full workflow
prerequisites:
  - Python 3.8+
  - Write permissions
commands:
  - step: 1
    description: First step
    commands:
      - echo "Step 1"
    expected_status: 0
  - step: 2
    description: Second step
    commands:
      - echo "Step 2"
expected_result:
  description: All steps should complete successfully
  expected_outputs:
    - field: exit_code
      value: "0"
verification:
  status: PASS
  verification_steps:
    - check: All steps completed
      result: PASS
"""
        yaml_file = os.path.join(self.temp_dir, "integration.yml")
        output_sh = os.path.join(self.temp_dir, "integration.sh")
        output_md = os.path.join(self.temp_dir, "integration.md")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)

        # Load test case
        self.assertTrue(parser.load_test_case())

        # Generate outputs
        self.assertTrue(parser.generate_shell_script(output_sh))
        self.assertTrue(parser.generate_markdown(output_md))

        # Verify shell script
        with open(output_sh, "r") as f:
            sh_content = f.read()

        self.assertIn("INT_001", sh_content)
        self.assertIn('echo "Step 1"', sh_content)
        self.assertIn('echo "Step 2"', sh_content)

        # Verify markdown
        with open(output_md, "r") as f:
            md_content = f.read()

        self.assertIn("INT_001", md_content)
        self.assertIn("REQ_INTEGRATION", md_content)
        self.assertIn("Integration test for full workflow", md_content)
        self.assertIn("integration", md_content)
        self.assertIn("smoke", md_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
