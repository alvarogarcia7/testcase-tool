#!/usr/bin/env python3
"""
Unit tests for KiwiTCMSDownloader using Python's built-in unittest module.
Tests authentication, API connection, downloads, output formats, and error handling.
"""

import json
import os
import shutil
import tempfile
import unittest
from io import BytesIO
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from kiwi_tcms_downloader import KiwiTCMSDownloader


class TestKiwiTCMSDownloaderInit(unittest.TestCase):
    """Tests for KiwiTCMSDownloader initialization"""

    def test_init_stores_base_url(self):
        """Downloader should store the base URL"""
        downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")
        self.assertEqual(downloader.base_url, "https://test.com")

    def test_init_stores_base_url_strips_trailing_slash(self):
        """Downloader should strip trailing slash from base URL"""
        downloader = KiwiTCMSDownloader("https://test.com/", "user", "pass")
        self.assertEqual(downloader.base_url, "https://test.com")

    def test_init_stores_username(self):
        """Downloader should store the username"""
        downloader = KiwiTCMSDownloader("https://test.com", "testuser", "pass")
        self.assertEqual(downloader.username, "testuser")

    def test_init_stores_password(self):
        """Downloader should store the password"""
        downloader = KiwiTCMSDownloader("https://test.com", "user", "testpass")
        self.assertEqual(downloader.password, "testpass")

    def test_init_creates_opener(self):
        """Downloader should create an opener for authentication"""
        downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")
        self.assertIsNotNone(downloader.opener)

    def test_setup_auth_creates_opener(self):
        """_setup_auth should create a valid opener"""
        downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")
        opener = downloader._setup_auth()
        self.assertIsNotNone(opener)


class TestMakeRequest(unittest.TestCase):
    """Tests for _make_request method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_make_request_constructs_correct_url(self, mock_opener):
        """Should construct correct URL from base_url and endpoint"""
        mock_response = Mock()
        mock_response.read.return_value = b'{"result": "success"}'
        mock_opener.return_value.open.return_value = mock_response

        self.downloader.opener = mock_opener.return_value
        self.downloader._make_request("/api/TestRun/123/")

        call_args = mock_opener.return_value.open.call_args
        request = call_args[0][0]
        self.assertEqual(request.full_url, "https://test.com/api/TestRun/123/")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_make_request_returns_json(self, mock_opener):
        """Should parse and return JSON response"""
        test_data = {"id": 123, "name": "test"}
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(test_data).encode("utf-8")
        mock_opener.return_value.open.return_value = mock_response

        self.downloader.opener = mock_opener.return_value
        result = self.downloader._make_request("/api/test/")

        self.assertEqual(result, test_data)

    @patch("kiwi_tcms_downloader.build_opener")
    def test_make_request_handles_post_data(self, mock_opener):
        """Should encode POST data as JSON"""
        mock_response = Mock()
        mock_response.read.return_value = b'{"status": "created"}'
        mock_opener.return_value.open.return_value = mock_response

        self.downloader.opener = mock_opener.return_value
        post_data = {"field": "value"}
        self.downloader._make_request("/api/create/", method="POST", data=post_data)

        call_args = mock_opener.return_value.open.call_args
        request = call_args[0][0]
        self.assertEqual(json.loads(request.data.decode("utf-8")), post_data)

    @patch("kiwi_tcms_downloader.build_opener")
    def test_make_request_sets_correct_headers(self, mock_opener):
        """Should set Content-Type and Accept headers"""
        mock_response = Mock()
        mock_response.read.return_value = b"{}"
        mock_opener.return_value.open.return_value = mock_response

        self.downloader.opener = mock_opener.return_value
        self.downloader._make_request("/api/test/")

        call_args = mock_opener.return_value.open.call_args
        request = call_args[0][0]
        self.assertEqual(request.headers["Content-type"], "application/json")
        self.assertEqual(request.headers["Accept"], "application/json")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_make_request_raises_on_http_error(self, mock_opener):
        """Should raise HTTPError on HTTP error response"""
        mock_opener.return_value.open.side_effect = HTTPError(
            "https://test.com/api/test/", 404, "Not Found", {}, BytesIO(b"Not Found")
        )

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(HTTPError):
            self.downloader._make_request("/api/test/")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_make_request_raises_on_url_error(self, mock_opener):
        """Should raise URLError on network error"""
        mock_opener.return_value.open.side_effect = URLError("Connection failed")

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(URLError):
            self.downloader._make_request("/api/test/")


class TestDownloadTestRun(unittest.TestCase):
    """Tests for download_test_run method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def test_download_test_run_returns_run_data(self):
        """Should return test run data with executions"""
        run_data = {"id": 1, "summary": "Test Run"}
        executions = [{"id": 1, "status": "PASS"}, {"id": 2, "status": "FAIL"}]

        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [run_data, executions]
            result = self.downloader.download_test_run(1)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["summary"], "Test Run")
        self.assertEqual(len(result["executions"]), 2)

    def test_download_test_run_calls_correct_endpoints(self):
        """Should call both TestRun and TestExecution endpoints"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [{"id": 1}, []]
            self.downloader.download_test_run(123)

        calls = mock_request.call_args_list
        self.assertEqual(calls[0][0][0], "/api/TestRun/123/")
        self.assertEqual(calls[1][0][0], "/api/TestExecution/?run=123")

    def test_download_test_run_handles_empty_executions(self):
        """Should handle empty executions list"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [{"id": 1}, []]
            result = self.downloader.download_test_run(1)

        self.assertEqual(result["executions"], [])

    def test_download_test_run_handles_non_list_executions(self):
        """Should convert non-list executions to empty list"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [{"id": 1}, {"not": "list"}]
            result = self.downloader.download_test_run(1)

        self.assertEqual(result["executions"], [])

    def test_download_test_run_returns_none_on_error(self):
        """Should return None if request fails"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = HTTPError("https://test.com", 404, "Not Found", {}, BytesIO(b""))
            result = self.downloader.download_test_run(1)

        self.assertIsNone(result)


class TestDownloadTestPlan(unittest.TestCase):
    """Tests for download_test_plan method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def test_download_test_plan_returns_plan_data(self):
        """Should return test plan data with test runs"""
        plan_data = {"id": 1, "name": "Test Plan"}
        runs = [{"id": 1, "summary": "Run 1"}, {"id": 2, "summary": "Run 2"}]

        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [plan_data, runs]
            result = self.downloader.download_test_plan(1)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test Plan")
        self.assertEqual(len(result["test_runs"]), 2)

    def test_download_test_plan_calls_correct_endpoints(self):
        """Should call both TestPlan and TestRun endpoints"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [{"id": 1}, []]
            self.downloader.download_test_plan(456)

        calls = mock_request.call_args_list
        self.assertEqual(calls[0][0][0], "/api/TestPlan/456/")
        self.assertEqual(calls[1][0][0], "/api/TestRun/?plan=456")

    def test_download_test_plan_handles_empty_runs(self):
        """Should handle empty test runs list"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [{"id": 1}, []]
            result = self.downloader.download_test_plan(1)

        self.assertEqual(result["test_runs"], [])

    def test_download_test_plan_handles_non_list_runs(self):
        """Should convert non-list runs to empty list"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [{"id": 1}, {"not": "list"}]
            result = self.downloader.download_test_plan(1)

        self.assertEqual(result["test_runs"], [])

    def test_download_test_plan_returns_none_on_error(self):
        """Should return None if request fails"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = URLError("Network error")
            result = self.downloader.download_test_plan(1)

        self.assertIsNone(result)


class TestDownloadTestCase(unittest.TestCase):
    """Tests for download_test_case method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def test_download_test_case_returns_case_data(self):
        """Should return test case data"""
        case_data = {"id": 1, "summary": "Test Case", "text": "Description"}

        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.return_value = case_data
            result = self.downloader.download_test_case(1)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["summary"], "Test Case")

    def test_download_test_case_calls_correct_endpoint(self):
        """Should call TestCase endpoint"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.return_value = {"id": 1}
            self.downloader.download_test_case(789)

        mock_request.assert_called_once_with("/api/TestCase/789/")

    def test_download_test_case_returns_none_on_error(self):
        """Should return None if request fails"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = HTTPError("https://test.com", 500, "Server Error", {}, BytesIO(b""))
            result = self.downloader.download_test_case(1)

        self.assertIsNone(result)


class TestSaveAsYAML(unittest.TestCase):
    """Tests for save_as_yaml method"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_save_as_yaml_creates_file(self):
        """Should create YAML file with data"""
        data = {"id": 1, "name": "test"}
        output_file = os.path.join(self.temp_dir, "test.yaml")

        result = self.downloader.save_as_yaml(data, output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_save_as_yaml_writes_correct_content(self):
        """Should write YAML content correctly"""
        data = {"id": 1, "name": "test", "items": ["a", "b"]}
        output_file = os.path.join(self.temp_dir, "test.yaml")

        self.downloader.save_as_yaml(data, output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("id: 1", content)
        self.assertIn("name: test", content)
        self.assertIn("- a", content)

    def test_save_as_yaml_returns_false_for_empty_data(self):
        """Should return False if data is empty"""
        output_file = os.path.join(self.temp_dir, "test.yaml")
        result = self.downloader.save_as_yaml(None, output_file)
        self.assertFalse(result)

    def test_save_as_yaml_returns_false_on_error(self):
        """Should return False if file write fails"""
        data = {"id": 1}
        invalid_path = "/invalid/nonexistent/path/test.yaml"
        result = self.downloader.save_as_yaml(data, invalid_path)
        self.assertFalse(result)


class TestSaveAsJSON(unittest.TestCase):
    """Tests for save_as_json method"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_save_as_json_creates_file(self):
        """Should create JSON file with data"""
        data = {"id": 1, "name": "test"}
        output_file = os.path.join(self.temp_dir, "test.json")

        result = self.downloader.save_as_json(data, output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_save_as_json_writes_correct_content(self):
        """Should write JSON content correctly"""
        data = {"id": 1, "name": "test", "items": ["a", "b"]}
        output_file = os.path.join(self.temp_dir, "test.json")

        self.downloader.save_as_json(data, output_file)

        with open(output_file, "r") as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data, data)

    def test_save_as_json_indents_output(self):
        """Should indent JSON output for readability"""
        data = {"id": 1, "name": "test"}
        output_file = os.path.join(self.temp_dir, "test.json")

        self.downloader.save_as_json(data, output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("  ", content)

    def test_save_as_json_returns_false_for_empty_data(self):
        """Should return False if data is empty"""
        output_file = os.path.join(self.temp_dir, "test.json")
        result = self.downloader.save_as_json(None, output_file)
        self.assertFalse(result)

    def test_save_as_json_returns_false_on_error(self):
        """Should return False if file write fails"""
        data = {"id": 1}
        invalid_path = "/invalid/nonexistent/path/test.json"
        result = self.downloader.save_as_json(data, invalid_path)
        self.assertFalse(result)


class TestSaveAsCSV(unittest.TestCase):
    """Tests for save_as_csv method"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_save_as_csv_creates_file(self):
        """Should create CSV file with data"""
        data = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]
        output_file = os.path.join(self.temp_dir, "test.csv")

        result = self.downloader.save_as_csv(data, output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_save_as_csv_writes_headers(self):
        """Should write CSV headers"""
        data = [{"id": 1, "name": "test"}]
        output_file = os.path.join(self.temp_dir, "test.csv")

        self.downloader.save_as_csv(data, output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("id,name", content)

    def test_save_as_csv_writes_data_rows(self):
        """Should write data rows correctly"""
        data = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]
        output_file = os.path.join(self.temp_dir, "test.csv")

        self.downloader.save_as_csv(data, output_file)

        with open(output_file, "r") as f:
            lines = f.readlines()

        self.assertIn("test1", lines[1])
        self.assertIn("test2", lines[2])

    def test_save_as_csv_handles_dict_with_executions(self):
        """Should extract executions from dict data"""
        data = {"id": 1, "executions": [{"id": 10, "status": "PASS"}]}
        output_file = os.path.join(self.temp_dir, "test.csv")

        result = self.downloader.save_as_csv(data, output_file)

        self.assertTrue(result)
        with open(output_file, "r") as f:
            content = f.read()
        self.assertIn("status", content)

    def test_save_as_csv_handles_dict_with_test_runs(self):
        """Should extract test_runs from dict data"""
        data = {"id": 1, "test_runs": [{"id": 20, "summary": "Run"}]}
        output_file = os.path.join(self.temp_dir, "test.csv")

        result = self.downloader.save_as_csv(data, output_file)

        self.assertTrue(result)
        with open(output_file, "r") as f:
            content = f.read()
        self.assertIn("summary", content)

    def test_save_as_csv_flattens_nested_dict(self):
        """Should flatten nested dictionaries"""
        data = [{"id": 1, "meta": {"key": "value"}}]
        output_file = os.path.join(self.temp_dir, "test.csv")

        self.downloader.save_as_csv(data, output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("meta_key", content)

    def test_save_as_csv_returns_false_for_empty_data(self):
        """Should return False if data is empty"""
        output_file = os.path.join(self.temp_dir, "test.csv")
        result = self.downloader.save_as_csv(None, output_file)
        self.assertFalse(result)

    def test_save_as_csv_returns_false_for_empty_rows(self):
        """Should return False if rows are empty"""
        data = {"id": 1, "executions": [], "test_runs": []}
        output_file = os.path.join(self.temp_dir, "test.csv")
        result = self.downloader.save_as_csv(data, output_file)
        self.assertFalse(result)


class TestFlattenDict(unittest.TestCase):
    """Tests for _flatten_dict method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def test_flatten_dict_simple_dict(self):
        """Should return simple dict unchanged"""
        data = {"id": 1, "name": "test"}
        result = self.downloader._flatten_dict(data)
        self.assertEqual(result, data)

    def test_flatten_dict_nested_dict(self):
        """Should flatten nested dictionaries"""
        data = {"id": 1, "meta": {"key": "value", "nested": {"deep": "data"}}}
        result = self.downloader._flatten_dict(data)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["meta_key"], "value")
        self.assertEqual(result["meta_nested_deep"], "data")

    def test_flatten_dict_with_list(self):
        """Should convert lists to JSON strings"""
        data = {"id": 1, "tags": ["tag1", "tag2"]}
        result = self.downloader._flatten_dict(data)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["tags"], '["tag1", "tag2"]')

    def test_flatten_dict_custom_separator(self):
        """Should use custom separator"""
        data = {"id": 1, "meta": {"key": "value"}}
        result = self.downloader._flatten_dict(data, sep=".")
        self.assertIn("meta.key", result)


class TestSaveAsMarkdown(unittest.TestCase):
    """Tests for save_as_markdown method"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_save_as_markdown_creates_file(self):
        """Should create markdown file"""
        data = {"id": 1, "summary": "Test Case", "text": "Description"}
        output_file = os.path.join(self.temp_dir, "test.md")

        result = self.downloader.save_as_markdown(data, output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_save_as_markdown_formats_test_case(self):
        """Should format test case data as markdown"""
        data = {"id": 1, "summary": "Test Case"}
        output_file = os.path.join(self.temp_dir, "test.md")

        self.downloader.save_as_markdown(data, output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("# Test Case: Test Case", content)
        self.assertIn("**Case ID:** 1", content)

    def test_save_as_markdown_formats_test_run(self):
        """Should format test run data as markdown"""
        data = {"id": 1, "summary": "Test Run", "plan": 10, "executions": []}
        output_file = os.path.join(self.temp_dir, "test.md")

        self.downloader.save_as_markdown(data, output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("# Test Run: Test Run", content)
        self.assertIn("**Run ID:** 1", content)
        self.assertIn("**Plan:** 10", content)

    def test_save_as_markdown_formats_test_plan(self):
        """Should format test plan data as markdown"""
        data = {"id": 1, "name": "Test Plan", "summary": "Summary", "text": "Text"}
        output_file = os.path.join(self.temp_dir, "test.md")

        self.downloader.save_as_markdown(data, output_file)

        with open(output_file, "r") as f:
            content = f.read()

        self.assertIn("# Test Plan: Test Plan", content)
        self.assertIn("**Plan ID:** 1", content)

    def test_save_as_markdown_returns_false_for_empty_data(self):
        """Should return False if data is empty"""
        output_file = os.path.join(self.temp_dir, "test.md")
        result = self.downloader.save_as_markdown(None, output_file)
        self.assertFalse(result)

    def test_save_as_markdown_returns_false_on_error(self):
        """Should return False if file write fails"""
        data = {"id": 1}
        invalid_path = "/invalid/nonexistent/path/test.md"
        result = self.downloader.save_as_markdown(data, invalid_path)
        self.assertFalse(result)


class TestFormatTestPlanMarkdown(unittest.TestCase):
    """Tests for _format_test_plan_markdown method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def test_format_test_plan_markdown_includes_name(self):
        """Should include plan name in heading"""
        plan = {"name": "My Test Plan"}
        lines = self.downloader._format_test_plan_markdown(plan)
        content = "\n".join(lines)
        self.assertIn("# Test Plan: My Test Plan", content)

    def test_format_test_plan_markdown_includes_id(self):
        """Should include plan ID"""
        plan = {"id": 123, "name": "Plan"}
        lines = self.downloader._format_test_plan_markdown(plan)
        content = "\n".join(lines)
        self.assertIn("**Plan ID:** 123", content)

    def test_format_test_plan_markdown_includes_description(self):
        """Should include description text"""
        plan = {"name": "Plan", "text": "This is the plan description"}
        lines = self.downloader._format_test_plan_markdown(plan)
        content = "\n".join(lines)
        self.assertIn("## Description", content)
        self.assertIn("This is the plan description", content)

    def test_format_test_plan_markdown_includes_test_runs(self):
        """Should list test runs"""
        plan = {
            "name": "Plan",
            "test_runs": [
                {"id": 1, "summary": "Run 1"},
                {"id": 2, "summary": "Run 2"},
            ],
        }
        lines = self.downloader._format_test_plan_markdown(plan)
        content = "\n".join(lines)
        self.assertIn("## Test Runs", content)
        self.assertIn("Total runs: 2", content)
        self.assertIn("Run 1", content)

    def test_format_test_plan_markdown_limits_runs_display(self):
        """Should limit display to 10 runs"""
        runs = [{"id": i, "summary": f"Run {i}"} for i in range(15)]
        plan = {"name": "Plan", "test_runs": runs}
        lines = self.downloader._format_test_plan_markdown(plan)
        content = "\n".join(lines)
        self.assertIn("and 5 more runs", content)


class TestFormatTestRunMarkdown(unittest.TestCase):
    """Tests for _format_test_run_markdown method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def test_format_test_run_markdown_includes_summary(self):
        """Should include run summary in heading"""
        run = {"summary": "My Test Run"}
        lines = self.downloader._format_test_run_markdown(run)
        content = "\n".join(lines)
        self.assertIn("# Test Run: My Test Run", content)

    def test_format_test_run_markdown_includes_id(self):
        """Should include run ID"""
        run = {"id": 456, "summary": "Run"}
        lines = self.downloader._format_test_run_markdown(run)
        content = "\n".join(lines)
        self.assertIn("**Run ID:** 456", content)

    def test_format_test_run_markdown_includes_notes(self):
        """Should include notes section"""
        run = {"summary": "Run", "notes": "Important notes"}
        lines = self.downloader._format_test_run_markdown(run)
        content = "\n".join(lines)
        self.assertIn("## Notes", content)
        self.assertIn("Important notes", content)

    def test_format_test_run_markdown_includes_execution_counts(self):
        """Should count execution statuses"""
        run = {
            "summary": "Run",
            "executions": [
                {"id": 1, "status": "PASS"},
                {"id": 2, "status": "PASS"},
                {"id": 3, "status": "FAIL"},
            ],
        }
        lines = self.downloader._format_test_run_markdown(run)
        content = "\n".join(lines)
        self.assertIn("## Test Executions", content)
        self.assertIn("Total executions: 3", content)
        self.assertIn("PASS: 2", content)
        self.assertIn("FAIL: 1", content)


class TestFormatTestCaseMarkdown(unittest.TestCase):
    """Tests for _format_test_case_markdown method"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def test_format_test_case_markdown_includes_summary(self):
        """Should include case summary in heading"""
        case = {"summary": "My Test Case"}
        lines = self.downloader._format_test_case_markdown(case)
        content = "\n".join(lines)
        self.assertIn("# Test Case: My Test Case", content)

    def test_format_test_case_markdown_includes_id(self):
        """Should include case ID"""
        case = {"id": 789, "summary": "Case"}
        lines = self.downloader._format_test_case_markdown(case)
        content = "\n".join(lines)
        self.assertIn("**Case ID:** 789", content)

    def test_format_test_case_markdown_includes_sections(self):
        """Should include all case sections"""
        case = {
            "summary": "Case",
            "text": "Description",
            "setup": "Setup steps",
            "action": "Test actions",
            "expected_result": "Expected result",
            "breakdown": "Cleanup",
        }
        lines = self.downloader._format_test_case_markdown(case)
        content = "\n".join(lines)
        self.assertIn("## Description", content)
        self.assertIn("## Setup", content)
        self.assertIn("## Test Actions", content)
        self.assertIn("## Expected Result", content)
        self.assertIn("## Breakdown", content)

    def test_format_test_case_markdown_skips_empty_sections(self):
        """Should skip empty sections"""
        case = {"summary": "Case", "text": "", "setup": ""}
        lines = self.downloader._format_test_case_markdown(case)
        content = "\n".join(lines)
        self.assertNotIn("## Description", content)
        self.assertNotIn("## Setup", content)


class TestExportTestRun(unittest.TestCase):
    """Tests for export_test_run method"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_export_test_run_creates_output_directory(self):
        """Should create output directory if it doesn't exist"""
        output_dir = os.path.join(self.temp_dir, "new_dir")
        run_data = {"id": 1, "summary": "Run", "executions": []}

        with patch.object(self.downloader, "download_test_run", return_value=run_data):
            self.downloader.export_test_run(1, output_dir, ["json"])

        self.assertTrue(os.path.exists(output_dir))

    def test_export_test_run_saves_all_formats(self):
        """Should save all specified formats"""
        run_data = {"id": 1, "summary": "Run", "plan": 1, "executions": [{"id": 1, "status": "PASS"}]}

        with patch.object(self.downloader, "download_test_run", return_value=run_data):
            result = self.downloader.export_test_run(1, self.temp_dir, ["yaml", "json", "csv", "markdown"])

        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_run_1.yaml")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_run_1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_run_1.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_run_1.md")))

    def test_export_test_run_uses_default_formats(self):
        """Should use default formats if none specified"""
        run_data = {"id": 1, "summary": "Run", "plan": 1, "executions": [{"id": 1, "status": "PASS"}]}

        with patch.object(self.downloader, "download_test_run", return_value=run_data):
            self.downloader.export_test_run(1, self.temp_dir)

        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_run_1.yaml")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_run_1.json")))

    def test_export_test_run_returns_false_on_download_failure(self):
        """Should return False if download fails"""
        with patch.object(self.downloader, "download_test_run", return_value=None):
            result = self.downloader.export_test_run(1, self.temp_dir)

        self.assertFalse(result)

    def test_export_test_run_handles_unknown_format(self):
        """Should skip unknown formats"""
        run_data = {"id": 1, "summary": "Run", "executions": []}

        with patch.object(self.downloader, "download_test_run", return_value=run_data):
            result = self.downloader.export_test_run(1, self.temp_dir, ["unknown"])

        self.assertTrue(result)


class TestExportTestPlan(unittest.TestCase):
    """Tests for export_test_plan method"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_export_test_plan_creates_output_directory(self):
        """Should create output directory if it doesn't exist"""
        output_dir = os.path.join(self.temp_dir, "new_dir")
        plan_data = {"id": 1, "name": "Plan", "summary": "S", "text": "T", "test_runs": []}

        with patch.object(self.downloader, "download_test_plan", return_value=plan_data):
            self.downloader.export_test_plan(1, output_dir, ["json"])

        self.assertTrue(os.path.exists(output_dir))

    def test_export_test_plan_saves_all_formats(self):
        """Should save all specified formats"""
        plan_data = {"id": 1, "name": "Plan", "summary": "S", "text": "T", "test_runs": [{"id": 1, "summary": "Run"}]}

        with patch.object(self.downloader, "download_test_plan", return_value=plan_data):
            result = self.downloader.export_test_plan(1, self.temp_dir, ["yaml", "json", "csv", "markdown"])

        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_plan_1.yaml")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_plan_1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_plan_1.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_plan_1.md")))

    def test_export_test_plan_returns_false_on_download_failure(self):
        """Should return False if download fails"""
        with patch.object(self.downloader, "download_test_plan", return_value=None):
            result = self.downloader.export_test_plan(1, self.temp_dir)

        self.assertFalse(result)


class TestExportTestCase(unittest.TestCase):
    """Tests for export_test_case method"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_export_test_case_creates_output_directory(self):
        """Should create output directory if it doesn't exist"""
        output_dir = os.path.join(self.temp_dir, "new_dir")
        case_data = {"id": 1, "summary": "Case"}

        with patch.object(self.downloader, "download_test_case", return_value=case_data):
            self.downloader.export_test_case(1, output_dir, ["json"])

        self.assertTrue(os.path.exists(output_dir))

    def test_export_test_case_saves_specified_formats(self):
        """Should save specified formats (no CSV by default)"""
        case_data = {"id": 1, "summary": "Case"}

        with patch.object(self.downloader, "download_test_case", return_value=case_data):
            result = self.downloader.export_test_case(1, self.temp_dir, ["yaml", "json", "markdown"])

        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_case_1.yaml")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_case_1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "test_case_1.md")))

    def test_export_test_case_returns_false_on_download_failure(self):
        """Should return False if download fails"""
        with patch.object(self.downloader, "download_test_case", return_value=None):
            result = self.downloader.export_test_case(1, self.temp_dir)

        self.assertFalse(result)


class TestAuthenticationErrors(unittest.TestCase):
    """Tests for authentication error handling"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_handles_401_unauthorized(self, mock_opener):
        """Should handle 401 Unauthorized error"""
        mock_opener.return_value.open.side_effect = HTTPError(
            "https://test.com/api/test/", 401, "Unauthorized", {}, BytesIO(b"Unauthorized")
        )

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(HTTPError) as ctx:
            self.downloader._make_request("/api/test/")

        self.assertEqual(ctx.exception.code, 401)

    @patch("kiwi_tcms_downloader.build_opener")
    def test_handles_403_forbidden(self, mock_opener):
        """Should handle 403 Forbidden error"""
        mock_opener.return_value.open.side_effect = HTTPError(
            "https://test.com/api/test/", 403, "Forbidden", {}, BytesIO(b"Forbidden")
        )

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(HTTPError) as ctx:
            self.downloader._make_request("/api/test/")

        self.assertEqual(ctx.exception.code, 403)


class TestNetworkErrors(unittest.TestCase):
    """Tests for network error handling"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_handles_connection_timeout(self, mock_opener):
        """Should handle connection timeout"""
        mock_opener.return_value.open.side_effect = URLError("Connection timeout")

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(URLError):
            self.downloader._make_request("/api/test/")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_handles_dns_error(self, mock_opener):
        """Should handle DNS resolution error"""
        mock_opener.return_value.open.side_effect = URLError("Name or service not known")

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(URLError):
            self.downloader._make_request("/api/test/")


class TestAPIErrors(unittest.TestCase):
    """Tests for API error handling"""

    def setUp(self):
        """Create downloader instance"""
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    @patch("kiwi_tcms_downloader.build_opener")
    def test_handles_404_not_found(self, mock_opener):
        """Should handle 404 Not Found error"""
        mock_opener.return_value.open.side_effect = HTTPError(
            "https://test.com/api/test/", 404, "Not Found", {}, BytesIO(b"Not Found")
        )

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(HTTPError) as ctx:
            self.downloader._make_request("/api/test/")

        self.assertEqual(ctx.exception.code, 404)

    @patch("kiwi_tcms_downloader.build_opener")
    def test_handles_500_server_error(self, mock_opener):
        """Should handle 500 Internal Server Error"""
        mock_opener.return_value.open.side_effect = HTTPError(
            "https://test.com/api/test/",
            500,
            "Internal Server Error",
            {},
            BytesIO(b"Server Error"),
        )

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(HTTPError) as ctx:
            self.downloader._make_request("/api/test/")

        self.assertEqual(ctx.exception.code, 500)

    @patch("kiwi_tcms_downloader.build_opener")
    def test_handles_invalid_json_response(self, mock_opener):
        """Should handle invalid JSON response"""
        mock_response = Mock()
        mock_response.read.return_value = b"Invalid JSON {"
        mock_opener.return_value.open.return_value = mock_response

        self.downloader.opener = mock_opener.return_value
        with self.assertRaises(Exception):
            self.downloader._make_request("/api/test/")


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_handles_empty_string_run_id(self):
        """Should handle empty string run ID"""
        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [{"id": ""}, []]
            result = self.downloader.download_test_run("")

        self.assertIsNotNone(result)

    def test_handles_large_data_export(self):
        """Should handle export of large datasets"""
        large_data = {"executions": [{"id": i, "status": "PASS"} for i in range(1000)]}
        output_file = os.path.join(self.temp_dir, "large.json")

        result = self.downloader.save_as_json(large_data, output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_handles_unicode_in_data(self):
        """Should handle unicode characters in data"""
        data = {"id": 1, "summary": "Test with 日本語 and émojis 🎉"}
        yaml_file = os.path.join(self.temp_dir, "unicode.yaml")
        json_file = os.path.join(self.temp_dir, "unicode.json")

        self.downloader.save_as_yaml(data, yaml_file)
        self.downloader.save_as_json(data, json_file)

        with open(yaml_file, "r", encoding="utf-8") as f:
            yaml_content = f.read()
        with open(json_file, "r", encoding="utf-8") as f:
            json_content = f.read()

        self.assertIn("日本語", yaml_content)
        self.assertIn("日本語", json_content)

    def test_handles_special_characters_in_filenames(self):
        """Should handle data with special characters"""
        data = {"id": 1, "summary": "Test: with/special\\chars"}
        output_file = os.path.join(self.temp_dir, "special.json")

        result = self.downloader.save_as_json(data, output_file)

        self.assertTrue(result)

    def test_handles_deeply_nested_dictionaries(self):
        """Should handle deeply nested dictionaries in flattening"""
        data = {"level1": {"level2": {"level3": {"level4": "value"}}}}
        result = self.downloader._flatten_dict(data)
        self.assertEqual(result["level1_level2_level3_level4"], "value")

    def test_handles_none_values_in_data(self):
        """Should handle None values in data"""
        data = {"id": 1, "name": None, "value": "test"}
        output_file = os.path.join(self.temp_dir, "none.json")

        result = self.downloader.save_as_json(data, output_file)

        self.assertTrue(result)
        with open(output_file, "r") as f:
            loaded = json.load(f)
        self.assertIsNone(loaded["name"])

    def test_handles_empty_lists_and_dicts(self):
        """Should handle empty lists and dictionaries"""
        data = {"id": 1, "items": [], "meta": {}}
        output_file = os.path.join(self.temp_dir, "empty.yaml")

        result = self.downloader.save_as_yaml(data, output_file)

        self.assertTrue(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflows"""

    def setUp(self):
        """Create temporary directory and downloader instance"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = KiwiTCMSDownloader("https://test.com", "user", "pass")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_full_test_run_export_workflow(self):
        """Test complete test run download and export workflow"""
        run_data = {
            "id": 1,
            "summary": "Integration Test Run",
            "plan": 10,
            "build": "v1.0",
            "manager": "admin",
            "notes": "Integration test notes",
        }
        executions = [
            {"id": 1, "status": "PASS", "tested_by": "user1"},
            {"id": 2, "status": "FAIL", "tested_by": "user2"},
        ]

        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [run_data, executions]
            result = self.downloader.export_test_run(1, self.temp_dir, ["yaml", "json", "markdown"])

        self.assertTrue(result)
        yaml_file = os.path.join(self.temp_dir, "test_run_1.yaml")
        json_file = os.path.join(self.temp_dir, "test_run_1.json")
        md_file = os.path.join(self.temp_dir, "test_run_1.md")

        self.assertTrue(os.path.exists(yaml_file))
        self.assertTrue(os.path.exists(json_file))
        self.assertTrue(os.path.exists(md_file))

        with open(md_file, "r") as f:
            md_content = f.read()
        self.assertIn("Integration Test Run", md_content)
        self.assertIn("PASS: 1", md_content)
        self.assertIn("FAIL: 1", md_content)

    def test_full_test_plan_export_workflow(self):
        """Test complete test plan download and export workflow"""
        plan_data = {
            "id": 1,
            "name": "Integration Test Plan",
            "summary": "Summary",
            "text": "Plan description",
            "type": 1,
            "product": 1,
            "version": "1.0",
            "author": "admin",
        }
        runs = [
            {"id": 1, "summary": "Run 1"},
            {"id": 2, "summary": "Run 2"},
        ]

        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.side_effect = [plan_data, runs]
            result = self.downloader.export_test_plan(1, self.temp_dir, ["yaml", "json", "markdown"])

        self.assertTrue(result)
        yaml_file = os.path.join(self.temp_dir, "test_plan_1.yaml")
        json_file = os.path.join(self.temp_dir, "test_plan_1.json")
        md_file = os.path.join(self.temp_dir, "test_plan_1.md")

        self.assertTrue(os.path.exists(yaml_file))
        self.assertTrue(os.path.exists(json_file))
        self.assertTrue(os.path.exists(md_file))

        with open(md_file, "r") as f:
            md_content = f.read()
        self.assertIn("Integration Test Plan", md_content)
        self.assertIn("Total runs: 2", md_content)

    def test_full_test_case_export_workflow(self):
        """Test complete test case download and export workflow"""
        case_data = {
            "id": 1,
            "summary": "Integration Test Case",
            "setup": "Setup steps",
            "action": "Test actions",
            "expected_result": "Expected result",
            "case_status": 2,
            "priority": 1,
            "author": "admin",
        }

        with patch.object(self.downloader, "_make_request") as mock_request:
            mock_request.return_value = case_data
            result = self.downloader.export_test_case(1, self.temp_dir, ["yaml", "json", "markdown"])

        self.assertTrue(result)
        yaml_file = os.path.join(self.temp_dir, "test_case_1.yaml")
        json_file = os.path.join(self.temp_dir, "test_case_1.json")
        md_file = os.path.join(self.temp_dir, "test_case_1.md")

        self.assertTrue(os.path.exists(yaml_file))
        self.assertTrue(os.path.exists(json_file))
        self.assertTrue(os.path.exists(md_file))

        with open(md_file, "r") as f:
            md_content = f.read()
        self.assertIn("Integration Test Case", md_content)
        self.assertIn("## Setup", md_content)
        self.assertIn("## Test Actions", md_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
