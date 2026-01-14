#!/usr/bin/env python3
"""
Unit tests for TestCaseParser using Python's built-in unittest module.
No external dependencies required.
"""

import os
import shutil
import tempfile
import unittest

import pytest

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
id: REQ1_I1_TC001
requirement_id: REQ001
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
id: REQ1_I1_TC001
description: Test description
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()

        self.assertEqual(parser.test_case["id"], "REQ1_I1_TC001")
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
id: REQ1_I1_TC001
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
id: REQ1_I1_TC001
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
id: REQ1_I1_TC001
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
id: REQ1_I1_TC001
actual_result:
  log_file: nonexistent.log
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)
        yaml_file = os.path.join(self.temp_dir, "test.actual.log")
        with open(yaml_file, "w") as f:
            f.write("LOG LOG LOG")

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.load_actual_log()

        self.assertFalse(result)

    def test_loads_valid_log_file(self):
        """Should load valid log file and return True"""
        yaml_content = """
id: REQ1_I1_TC001
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
id: REQ1_I1_TC001
test_sequences:
  - id: 1
    name: "Test Sequence #01 Nominal: Unset PPR1"
    description: |
                   This test case verifies that the eUICC correctly processes an ES6.UpdateMetadata command to unset PPR1
                   when the profile is in the operational state and PPR1 is currently set.
    steps:
      - step: 1
        description: "MTD_SENDS_SMS_PP([INSTALL_PERSO_RES_ISDP]; MTD_STORE_DATA_SCRIPT(#REMOVE_PPR1, FALSE))"
        command: echo "Hello World"
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

    def test_script_is_executable(self):
        """Generated script should have executable permissions"""
        yaml_content = """
id: REQ1_I1_TC001
test_sequences:
  - id: 1
    name: "Test Sequence #01 Nominal: Unset PPR1"
    description: |
                   This test case verifies that the eUICC correctly processes an ES6.UpdateMetadata command to unset PPR1
                   when the profile is in the operational state and PPR1 is currently set.
    steps:
      - step: 1
        description: "MTD_SENDS_SMS_PP([INSTALL_PERSO_RES_ISDP]; MTD_STORE_DATA_SCRIPT(#REMOVE_PPR1, FALSE))"
        command: |-
                     echo "Hello World"
                     another one
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

    @pytest.mark.skip("Prerequisites check is not implemented yet")
    def test_generates_prerequisites_section(self):
        """Script should contain prerequisites check when prerequisites exist"""
        yaml_content = """
id: REQ1_I1_TC001
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
id: REQ1_I1_TC001
test_sequences:
  - id: 1
    name: "Test Sequence #01 Nominal: Unset PPR1"
    description: |
                   This test case verifies that the eUICC correctly processes an ES6.UpdateMetadata command to unset PPR1
                   when the profile is in the operational state and PPR1 is currently set.
    steps:
      - step: 1
        description: "MTD_SENDS_SMS_PP([INSTALL_PERSO_RES_ISDP]; MTD_STORE_DATA_SCRIPT(#REMOVE_PPR1, FALSE))"
        command: |-
                     echo "Hello World"
                     another one
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

        self.assertIn('echo "Hello World"', content)

    def test_returns_true_on_success(self):
        """Should return True when script is generated successfully"""
        yaml_content = """
id: REQ1_I1_TC001
test_sequences:
  - id: 1
    name: "Test Sequence #01 Nominal: Unset PPR1"
    description: |
                   This test case verifies that the eUICC correctly processes an ES6.UpdateMetadata command to unset PPR1
                   when the profile is in the operational state and PPR1 is currently set.
    steps:
      - step: 1
        description: "MTD_SENDS_SMS_PP([INSTALL_PERSO_RES_ISDP]; MTD_STORE_DATA_SCRIPT(#REMOVE_PPR1, FALSE))"
        command: |-
                     echo "Hello World"
                     another one
"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.sh")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        parser = TestCaseParser(yaml_file)
        parser.load_test_case()
        result = parser.generate_shell_script(output_file)

        self.assertTrue(result)


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

    def test_handles_multiline_commands(self):
        """Should handle multiline commands in shell script"""
        yaml_content = """
id: REQ1_I1_TC001
test_sequences:
  - id: 1
    name: "Test Sequence #01 Nominal: Unset PPR1"
    description: |
                   This test case verifies that the eUICC correctly processes an ES6.UpdateMetadata command to unset PPR1
                   when the profile is in the operational state and PPR1 is currently set.
    steps:
      - step: 1
        description: "MTD_SENDS_SMS_PP([INSTALL_PERSO_RES_ISDP]; MTD_STORE_DATA_SCRIPT(#REMOVE_PPR1, FALSE))"
        command:
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
