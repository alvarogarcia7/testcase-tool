#!/usr/bin/env python3
"""
Unit tests for YamlReindenter using Python's built-in unittest module.
No external dependencies required.
"""

import os
import shutil
import tempfile
import unittest

from yaml_reindenter import YamlReindenter


class TestYamlReindenterInit(unittest.TestCase):
    """Tests for YamlReindenter initialization"""

    def test_init_stores_yaml_file_path(self):
        """Reindenter should store the yaml file path"""
        reindenter = YamlReindenter("/some/path/test.yml")
        self.assertEqual(reindenter.yaml_file, "/some/path/test.yml")

    def test_init_content_is_none(self):
        """Reindenter should initialize with content as None"""
        reindenter = YamlReindenter("/some/path/test.yml")
        self.assertIsNone(reindenter.content)

    def test_init_lines_is_none(self):
        """Reindenter should initialize with lines as None"""
        reindenter = YamlReindenter("/some/path/test.yml")
        self.assertIsNone(reindenter.lines)


class TestLoadFile(unittest.TestCase):
    """Tests for load_file method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_load_valid_file_returns_true(self):
        """Loading a valid file should return True"""
        yaml_content = "key: value\n"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        result = reindenter.load_file()

        self.assertTrue(result)

    def test_load_valid_file_populates_content(self):
        """Loading a valid file should populate content attribute"""
        yaml_content = "key: value\nother: data"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()

        self.assertEqual(reindenter.content, yaml_content)

    def test_load_valid_file_populates_lines(self):
        """Loading a valid file should populate lines attribute"""
        yaml_content = "key: value\nother: data"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()

        self.assertEqual(len(reindenter.lines), 2)
        self.assertEqual(reindenter.lines[0], "key: value")
        self.assertEqual(reindenter.lines[1], "other: data")

    def test_load_nonexistent_file_returns_false(self):
        """Loading a non-existent file should return False"""
        reindenter = YamlReindenter("/nonexistent/path/test.yml")
        result = reindenter.load_file()

        self.assertFalse(result)

    def test_load_empty_file_returns_true(self):
        """Loading an empty file should return True"""
        yaml_file = os.path.join(self.temp_dir, "empty.yml")
        with open(yaml_file, "w") as f:
            f.write("")

        reindenter = YamlReindenter(yaml_file)
        result = reindenter.load_file()

        self.assertTrue(result)
        self.assertEqual(reindenter.content, "")


class TestDetectPipeBlocks(unittest.TestCase):
    """Tests for detect_pipe_blocks method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_detects_single_pipe_block(self):
        """Should detect a single pipe block"""
        yaml_content = "key: |\n  content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["line_num"], 0)
        self.assertEqual(blocks[0]["pipe_indent"], 0)

    def test_detects_multiple_pipe_blocks(self):
        """Should detect multiple pipe blocks"""
        yaml_content = "key1: |\n  content1\nkey2: |\n  content2"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0]["line_num"], 0)
        self.assertEqual(blocks[1]["line_num"], 2)

    def test_detects_indented_pipe_block(self):
        """Should detect pipe block with indentation"""
        yaml_content = "parent:\n  child: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["line_num"], 1)
        self.assertEqual(blocks[0]["pipe_indent"], 2)

    def test_detects_no_pipe_blocks(self):
        """Should return empty list when no pipe blocks exist"""
        yaml_content = "key: value\nother: data"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(len(blocks), 0)

    def test_detects_pipe_with_spaces(self):
        """Should detect pipe with varying spaces around colon"""
        yaml_content = "key:  |\n  content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(len(blocks), 1)

    def test_detects_nested_pipe_blocks(self):
        """Should detect nested pipe blocks at different indentation levels"""
        yaml_content = "level1: |\n  content1\n  nested:\n    level2: |\n      content2"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0]["pipe_indent"], 0)
        self.assertEqual(blocks[1]["pipe_indent"], 4)


class TestGetBlockContent(unittest.TestCase):
    """Tests for get_block_content method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_gets_single_line_content(self):
        """Should get single line of content"""
        yaml_content = "key: |\n  content line"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        content_lines, expected_indent = reindenter.get_block_content(0, 0)

        self.assertEqual(len(content_lines), 1)
        self.assertEqual(content_lines[0], 1)
        self.assertEqual(expected_indent, 2)

    def test_gets_multiple_line_content(self):
        """Should get multiple lines of content"""
        yaml_content = "key: |\n  line1\n  line2\n  line3"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        content_lines, expected_indent = reindenter.get_block_content(0, 0)

        self.assertEqual(len(content_lines), 3)
        self.assertEqual(content_lines, [1, 2, 3])

    def test_stops_at_same_indent_level(self):
        """Should stop when encountering same or lower indentation"""
        yaml_content = "key1: |\n  content1\nkey2: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        content_lines, expected_indent = reindenter.get_block_content(0, 0)

        self.assertEqual(len(content_lines), 1)
        self.assertEqual(content_lines[0], 1)

    def test_includes_empty_lines(self):
        """Should include empty lines in content"""
        yaml_content = "key: |\n  line1\n\n  line3"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        content_lines, expected_indent = reindenter.get_block_content(0, 0)

        self.assertEqual(len(content_lines), 3)
        self.assertIn(2, content_lines)

    def test_calculates_expected_indent(self):
        """Should calculate expected indent as pipe_indent + 2"""
        yaml_content = "  key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        content_lines, expected_indent = reindenter.get_block_content(0, 2)

        self.assertEqual(expected_indent, 4)


class TestCheckIndentation(unittest.TestCase):
    """Tests for check_indentation method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_no_issues_with_correct_indentation(self):
        """Should return empty list when indentation is correct"""
        yaml_content = "key: |\n  content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.check_indentation([1], 2)

        self.assertEqual(len(issues), 0)

    def test_detects_incorrect_indentation(self):
        """Should detect incorrect indentation"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.check_indentation([1], 2)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["line_num"], 1)
        self.assertEqual(issues[0]["current_indent"], 4)
        self.assertEqual(issues[0]["expected_indent"], 2)

    def test_detects_multiple_incorrect_lines(self):
        """Should detect multiple lines with incorrect indentation"""
        yaml_content = "key: |\n    line1\n     line2\n    line3"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.check_indentation([1, 2, 3], 2)

        self.assertEqual(len(issues), 3)

    def test_skips_empty_lines(self):
        """Should skip empty lines when checking indentation"""
        yaml_content = "key: |\n  line1\n\n  line3"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.check_indentation([1, 2, 3], 2)

        self.assertEqual(len(issues), 0)

    def test_detects_too_little_indentation(self):
        """Should detect lines with too little indentation"""
        yaml_content = "key: |\n content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.check_indentation([1], 2)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["current_indent"], 1)


class TestFixIndentation(unittest.TestCase):
    """Tests for fix_indentation method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_returns_false_with_no_issues(self):
        """Should return False when no issues to fix"""
        yaml_content = "key: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        result = reindenter.fix_indentation([])

        self.assertFalse(result)

    def test_returns_true_with_issues(self):
        """Should return True when issues are fixed"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = [{"line_num": 1, "current_indent": 4, "expected_indent": 2}]
        result = reindenter.fix_indentation(issues)

        self.assertTrue(result)

    def test_fixes_single_line(self):
        """Should fix indentation of single line"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = [{"line_num": 1, "current_indent": 4, "expected_indent": 2}]
        reindenter.fix_indentation(issues)

        self.assertEqual(reindenter.lines[1], "  content")

    def test_fixes_multiple_lines(self):
        """Should fix indentation of multiple lines"""
        yaml_content = "key: |\n    line1\n     line2\n    line3"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = [
            {"line_num": 1, "current_indent": 4, "expected_indent": 2},
            {"line_num": 2, "current_indent": 5, "expected_indent": 2},
            {"line_num": 3, "current_indent": 4, "expected_indent": 2},
        ]
        reindenter.fix_indentation(issues)

        self.assertEqual(reindenter.lines[1], "  line1")
        self.assertEqual(reindenter.lines[2], "  line2")
        self.assertEqual(reindenter.lines[3], "  line3")

    def test_preserves_line_content(self):
        """Should preserve line content while fixing indentation"""
        yaml_content = "key: |\n    special: chars & symbols!"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = [{"line_num": 1, "current_indent": 4, "expected_indent": 2}]
        reindenter.fix_indentation(issues)

        self.assertIn("special: chars & symbols!", reindenter.lines[1])

    def test_updates_content_attribute(self):
        """Should update content attribute after fixing"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = [{"line_num": 1, "current_indent": 4, "expected_indent": 2}]
        reindenter.fix_indentation(issues)

        self.assertIn("  content", reindenter.content)


class TestAnalyze(unittest.TestCase):
    """Tests for analyze method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_returns_empty_list_with_no_content(self):
        """Should return empty list when no content loaded"""
        reindenter = YamlReindenter("/some/path/test.yml")
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 0)

    def test_returns_empty_list_with_correct_indentation(self):
        """Should return empty list when indentation is correct"""
        yaml_content = "key: |\n  content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 0)

    def test_detects_issues_in_single_block(self):
        """Should detect issues in single pipe block"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 1)

    def test_detects_issues_in_multiple_blocks(self):
        """Should detect issues across multiple pipe blocks"""
        yaml_content = "key1: |\n    content1\nkey2: |\n    content2"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 2)

    def test_returns_issue_details(self):
        """Should return detailed information about issues"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertIn("line_num", issues[0])
        self.assertIn("current_indent", issues[0])
        self.assertIn("expected_indent", issues[0])


class TestReindent(unittest.TestCase):
    """Tests for reindent method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_returns_false_with_no_issues(self):
        """Should return False when no issues found"""
        yaml_content = "key: |\n  content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        result = reindenter.reindent()

        self.assertFalse(result)

    def test_returns_true_with_issues_fixed(self):
        """Should return True when issues are fixed"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        result = reindenter.reindent()

        self.assertTrue(result)

    def test_fixes_indentation(self):
        """Should fix indentation issues"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()

        self.assertEqual(reindenter.lines[1], "  content")


class TestSaveFile(unittest.TestCase):
    """Tests for save_file method"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_returns_false_with_no_content(self):
        """Should return False when no content to save"""
        reindenter = YamlReindenter("/some/path/test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        result = reindenter.save_file(output_file)

        self.assertFalse(result)

    def test_returns_true_on_success(self):
        """Should return True when file saved successfully"""
        yaml_content = "key: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        result = reindenter.save_file(output_file)

        self.assertTrue(result)

    def test_saves_to_specified_file(self):
        """Should save content to specified output file"""
        yaml_content = "key: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.save_file(output_file)

        self.assertTrue(os.path.exists(output_file))
        with open(output_file, "r") as f:
            content = f.read()
        self.assertIn("key: value", content)

    def test_saves_to_original_file_when_no_output_specified(self):
        """Should save to original file when output file not specified"""
        yaml_content = "key: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.content = "modified: content"
        reindenter.save_file()

        with open(yaml_file, "r") as f:
            content = f.read()
        self.assertIn("modified: content", content)

    def test_adds_newline_at_end_if_missing(self):
        """Should add newline at end of file if missing"""
        yaml_content = "key: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.save_file(output_file)

        with open(output_file, "r") as f:
            content = f.read()
        self.assertTrue(content.endswith("\n"))

    def test_preserves_fixed_content(self):
        """Should preserve content after fixing indentation"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()
        reindenter.save_file(output_file)

        with open(output_file, "r") as f:
            content = f.read()
        self.assertIn("  content", content)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and special scenarios"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_handles_empty_pipe_block(self):
        """Should handle pipe block with no content"""
        yaml_content = "key: |\nother: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 0)

    def test_handles_pipe_block_with_only_empty_lines(self):
        """Should handle pipe block with only empty lines"""
        yaml_content = "key: |\n\n\nother: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 0)

    def test_handles_mixed_correct_and_incorrect_indentation(self):
        """Should handle mixed correct and incorrect indentation"""
        yaml_content = "key: |\n  correct\n    incorrect\n  correct"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["line_num"], 2)

    def test_handles_special_characters_in_content(self):
        """Should handle special characters in pipe block content"""
        yaml_content = "key: |\n    $pecial: @chars & symbols! <>"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()

        self.assertIn("$pecial: @chars & symbols! <>", reindenter.lines[1])

    def test_handles_unicode_characters(self):
        """Should handle unicode characters in content"""
        yaml_content = "key: |\n    Hello 世界 🌍"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()

        self.assertIn("世界", reindenter.lines[1])
        self.assertIn("🌍", reindenter.lines[1])

    def test_handles_tabs_in_content(self):
        """Should handle tabs in pipe block content"""
        yaml_content = "key: |\n    line\twith\ttabs"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()

        self.assertIn("\t", reindenter.lines[1])

    def test_handles_trailing_whitespace(self):
        """Should preserve trailing whitespace in content"""
        yaml_content = "key: |\n    content  "
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()

        self.assertTrue(reindenter.lines[1].endswith("  "))

    def test_handles_deeply_nested_pipe_blocks(self):
        """Should handle deeply nested pipe blocks"""
        yaml_content = "l1:\n  l2:\n    l3:\n      key: |\n        content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["pipe_indent"], 6)

    def test_handles_multiple_consecutive_empty_lines(self):
        """Should handle multiple consecutive empty lines in pipe block"""
        yaml_content = "key: |\n  line1\n\n\n  line4"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        content_lines, _ = reindenter.get_block_content(0, 0)

        self.assertEqual(len(content_lines), 4)

    def test_handles_pipe_block_at_end_of_file(self):
        """Should handle pipe block at the end of file"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 1)

    def test_handles_line_with_only_spaces(self):
        """Should handle lines with only spaces"""
        yaml_content = "key: |\n  line1\n    \n  line3"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 0)

    def test_handles_zero_indent_pipe_block(self):
        """Should handle pipe block at zero indentation"""
        yaml_content = "key: |\n  content\n  more content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        blocks = reindenter.detect_pipe_blocks()

        self.assertEqual(blocks[0]["pipe_indent"], 0)

    def test_handles_extremely_long_lines(self):
        """Should handle extremely long lines"""
        long_content = "a" * 1000
        yaml_content = f"key: |\n    {long_content}"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()

        self.assertIn(long_content, reindenter.lines[1])


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflow"""

    def setUp(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_full_workflow_single_block(self):
        """Test complete workflow with single pipe block"""
        yaml_content = "key: |\n    incorrect indentation"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        self.assertTrue(reindenter.load_file())

        issues = reindenter.analyze()
        self.assertEqual(len(issues), 1)

        self.assertTrue(reindenter.reindent())
        self.assertTrue(reindenter.save_file(output_file))

        with open(output_file, "r") as f:
            content = f.read()
        self.assertIn("  incorrect indentation", content)

    def test_full_workflow_multiple_blocks(self):
        """Test complete workflow with multiple pipe blocks"""
        yaml_content = "key1: |\n    content1\n    content1b\nkey2: |\n     content2\nkey3: value"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertGreater(len(issues), 0)

        reindenter.reindent()
        reindenter.save_file(output_file)

        with open(output_file, "r") as f:
            lines = f.readlines()

        self.assertTrue(lines[1].startswith("  content1"))
        self.assertTrue(lines[2].startswith("  content1b"))
        self.assertTrue(lines[4].startswith("  content2"))

    def test_full_workflow_nested_structure(self):
        """Test complete workflow with nested YAML structure"""
        yaml_content = """parent:
  child1:
    grandchild: |
        deeply nested content
        with multiple lines
  child2: |
      another pipe block
other: value"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertGreater(len(issues), 0)

        reindenter.reindent()
        reindenter.save_file(output_file)

        self.assertTrue(os.path.exists(output_file))

    def test_full_workflow_no_changes_needed(self):
        """Test complete workflow when no changes are needed"""
        yaml_content = "key: |\n  correct indentation\n  more correct"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        issues = reindenter.analyze()

        self.assertEqual(len(issues), 0)

        result = reindenter.reindent()
        self.assertFalse(result)

    def test_full_workflow_complex_document(self):
        """Test complete workflow with complex YAML document"""
        yaml_content = """testcase_id: TC001
requirement_id: REQ001
description: Test case with pipe blocks
commands:
  - step: 1
    description: |
        This is a multiline description
        with incorrect indentation
    commands:
      - echo "test"
  - step: 2
    expected_output: |
          Output with wrong indent
          Multiple lines here
expected_result:
  description: Should work
verification:
  notes: |
     Final pipe block
     With issues"""
        yaml_file = os.path.join(self.temp_dir, "complex.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.analyze()

        blocks = reindenter.detect_pipe_blocks()
        self.assertEqual(len(blocks), 3)

        reindenter.reindent()
        reindenter.save_file(output_file)

        self.assertTrue(os.path.exists(output_file))

    def test_idempotent_operation(self):
        """Test that running reindent twice produces same result"""
        yaml_content = "key: |\n    content"
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()
        first_result = reindenter.content

        reindenter2 = YamlReindenter(yaml_file)
        reindenter2.content = first_result
        reindenter2.lines = first_result.splitlines()
        result = reindenter2.reindent()

        self.assertFalse(result)

    def test_preserves_file_structure(self):
        """Test that reindenting preserves overall file structure"""
        yaml_content = """key1: value1
section:
  nested: value2
pipe_section: |
    wrong indent
another_key: value3"""
        yaml_file = os.path.join(self.temp_dir, "test.yml")
        output_file = os.path.join(self.temp_dir, "output.yml")
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        reindenter = YamlReindenter(yaml_file)
        reindenter.load_file()
        reindenter.reindent()
        reindenter.save_file(output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("key1: value1", content)
        self.assertIn("nested: value2", content)
        self.assertIn("another_key: value3", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
