#!/usr/bin/env python3
import csv
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, Request, build_opener

import yaml


class KiwiTCMSDownloader:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.opener = self._setup_auth()

    def _setup_auth(self):
        password_mgr = HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.base_url, self.username, self.password)
        auth_handler = HTTPBasicAuthHandler(password_mgr)
        return build_opener(auth_handler)

    def _make_request(self, endpoint, method="GET", data=None):
        url = urljoin(self.base_url, endpoint)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        req_data = json.dumps(data).encode("utf-8") if data else None
        request = Request(url, data=req_data, headers=headers, method=method)
        try:
            response = self.opener.open(request)
            return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            try:
                error_body = e.read().decode("utf-8")
                print(f"Error details: {error_body}")
            except Exception:
                pass
            raise
        except URLError as e:
            print(f"URL Error: {e.reason}")
            raise
        except Exception as e:
            print(f"Error making request: {e}")
            raise

    def download_test_run(self, run_id):
        try:
            run_data = self._make_request(f"/api/TestRun/{run_id}/")
            executions = self._make_request(f"/api/TestExecution/?run={run_id}")
            run_data["executions"] = executions if isinstance(executions, list) else []
            return run_data
        except Exception as e:
            print(f"Error downloading test run {run_id}: {e}")
            return None

    def download_test_plan(self, plan_id):
        try:
            plan_data = self._make_request(f"/api/TestPlan/{plan_id}/")
            runs = self._make_request(f"/api/TestRun/?plan={plan_id}")
            plan_data["test_runs"] = runs if isinstance(runs, list) else []
            return plan_data
        except Exception as e:
            print(f"Error downloading test plan {plan_id}: {e}")
            return None

    def download_test_case(self, case_id):
        try:
            return self._make_request(f"/api/TestCase/{case_id}/")
        except Exception as e:
            print(f"Error downloading test case {case_id}: {e}")
            return None

    def save_as_yaml(self, data, output_file):
        if not data:
            print("Error: No data to save")
            return False
        try:
            with open(output_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"Saved YAML to: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing YAML file: {e}")
            return False

    def save_as_json(self, data, output_file):
        if not data:
            print("Error: No data to save")
            return False
        try:
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved JSON to: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing JSON file: {e}")
            return False

    def save_as_csv(self, data, output_file):
        if not data:
            print("Error: No data to save")
            return False
        try:
            rows = []
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                if "executions" in data:
                    rows = data["executions"]
                elif "test_runs" in data:
                    rows = data["test_runs"]
                else:
                    rows = [data]
            if not rows:
                print("Warning: No rows to export to CSV")
                return False
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=self._flatten_dict(rows[0]).keys())
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(self._flatten_dict(row))
            print(f"Saved CSV to: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing CSV file: {e}")
            return False

    def _flatten_dict(self, d, parent_key="", sep="_"):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    def save_as_markdown(self, data, output_file):
        if not data:
            print("Error: No data to save")
            return False
        try:
            lines = []
            if isinstance(data, dict):
                if "summary" in data and "text" in data:
                    lines = self._format_test_plan_markdown(data)
                elif "plan" in data:
                    lines = self._format_test_run_markdown(data)
                else:
                    lines = self._format_test_case_markdown(data)
            else:
                lines = ["# Data Export", "", "```json", json.dumps(data, indent=2), "```"]
            with open(output_file, "w") as f:
                f.write("\n".join(lines))
            print(f"Saved Markdown to: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing Markdown file: {e}")
            return False

    def _format_test_plan_markdown(self, plan):
        L = [f"# Test Plan: {plan.get('name', 'Untitled')}", ""]
        if plan.get("id"):
            L.append(f"**Plan ID:** {plan['id']}")
        if plan.get("type"):
            L.append(f"**Type:** {plan['type']}")
        if plan.get("product"):
            L.append(f"**Product:** {plan['product']}")
        if plan.get("version"):
            L.append(f"**Version:** {plan['version']}")
        L.append("")
        if plan.get("text", "").strip():
            L += ["## Description", "", plan["text"].strip(), ""]
        if plan.get("author"):
            L.append(f"**Author:** {plan['author']}")
        if plan.get("create_date"):
            L.append(f"**Created:** {plan['create_date']}")
        L.append("")
        runs = plan.get("test_runs", [])
        if runs:
            L += ["## Test Runs", "", f"Total runs: {len(runs)}", ""]
            for run in runs[:10]:
                L.append(f"- **Run {run.get('id', 'N/A')}**: {run.get('summary', 'No summary')}")
            if len(runs) > 10:
                L.append(f"- ... and {len(runs) - 10} more runs")
            L.append("")
        return L

    def _format_test_run_markdown(self, run):
        L = [f"# Test Run: {run.get('summary', 'Untitled')}", ""]
        if run.get("id"):
            L.append(f"**Run ID:** {run['id']}")
        if run.get("plan"):
            L.append(f"**Plan:** {run['plan']}")
        if run.get("build"):
            L.append(f"**Build:** {run['build']}")
        if run.get("manager"):
            L.append(f"**Manager:** {run['manager']}")
        L.append("")
        if run.get("notes", "").strip():
            L += ["## Notes", "", run["notes"].strip(), ""]
        if run.get("start_date"):
            L.append(f"**Started:** {run['start_date']}")
        if run.get("stop_date"):
            L.append(f"**Stopped:** {run['stop_date']}")
        L.append("")
        execs = run.get("executions", [])
        if execs:
            L += ["## Test Executions", "", f"Total executions: {len(execs)}", ""]
            status_counts = {}
            for ex in execs:
                status = ex.get("status", "Unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            L.append("**Status Summary:**")
            for status, count in status_counts.items():
                L.append(f"- {status}: {count}")
            L.append("")
        return L

    def _format_test_case_markdown(self, case):
        L = [f"# Test Case: {case.get('summary', 'Untitled')}", ""]
        if case.get("id"):
            L.append(f"**Case ID:** {case['id']}")
        if case.get("case_status"):
            L.append(f"**Status:** {case['case_status']}")
        if case.get("priority"):
            L.append(f"**Priority:** {case['priority']}")
        if case.get("category"):
            L.append(f"**Category:** {case['category']}")
        L.append("")
        if case.get("text", "").strip():
            L += ["## Description", "", case["text"].strip(), ""]
        if case.get("setup", "").strip():
            L += ["## Setup", "", case["setup"].strip(), ""]
        if case.get("action", "").strip():
            L += ["## Test Actions", "", case["action"].strip(), ""]
        if case.get("expected_result", "").strip():
            L += ["## Expected Result", "", case["expected_result"].strip(), ""]
        if case.get("breakdown", "").strip():
            L += ["## Breakdown", "", case["breakdown"].strip(), ""]
        if case.get("author"):
            L.append(f"**Author:** {case['author']}")
        if case.get("create_date"):
            L.append(f"**Created:** {case['create_date']}")
        L.append("")
        return L

    def export_test_run(self, run_id, output_dir=".", formats=None):
        if formats is None:
            formats = ["yaml", "json", "csv", "markdown"]
        run_data = self.download_test_run(run_id)
        if not run_data:
            return False
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        success = True
        base = Path(output_dir) / f"test_run_{run_id}"
        for fmt in formats:
            if fmt == "yaml":
                success &= self.save_as_yaml(run_data, f"{base}.yaml")
            elif fmt == "json":
                success &= self.save_as_json(run_data, f"{base}.json")
            elif fmt == "csv":
                success &= self.save_as_csv(run_data, f"{base}.csv")
            elif fmt == "markdown":
                success &= self.save_as_markdown(run_data, f"{base}.md")
            else:
                print(f"Warning: Unknown format '{fmt}'")
        return success

    def export_test_plan(self, plan_id, output_dir=".", formats=None):
        if formats is None:
            formats = ["yaml", "json", "csv", "markdown"]
        plan_data = self.download_test_plan(plan_id)
        if not plan_data:
            return False
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        success = True
        base = Path(output_dir) / f"test_plan_{plan_id}"
        for fmt in formats:
            if fmt == "yaml":
                success &= self.save_as_yaml(plan_data, f"{base}.yaml")
            elif fmt == "json":
                success &= self.save_as_json(plan_data, f"{base}.json")
            elif fmt == "csv":
                success &= self.save_as_csv(plan_data, f"{base}.csv")
            elif fmt == "markdown":
                success &= self.save_as_markdown(plan_data, f"{base}.md")
            else:
                print(f"Warning: Unknown format '{fmt}'")
        return success

    def export_test_case(self, case_id, output_dir=".", formats=None):
        if formats is None:
            formats = ["yaml", "json", "markdown"]
        case_data = self.download_test_case(case_id)
        if not case_data:
            return False
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        success = True
        base = Path(output_dir) / f"test_case_{case_id}"
        for fmt in formats:
            if fmt == "yaml":
                success &= self.save_as_yaml(case_data, f"{base}.yaml")
            elif fmt == "json":
                success &= self.save_as_json(case_data, f"{base}.json")
            elif fmt == "csv":
                success &= self.save_as_csv(case_data, f"{base}.csv")
            elif fmt == "markdown":
                success &= self.save_as_markdown(case_data, f"{base}.md")
            else:
                print(f"Warning: Unknown format '{fmt}'")
        return success


def main():
    if len(sys.argv) < 4:
        print("Usage: python kiwi_tcms_downloader.py <command> <id> <output_dir> [formats]")
        print("Commands: test-run, test-plan, test-case")
        print("Formats: yaml,json,csv,markdown (default: all)")
        print("\nEnvironment variables:")
        print("  KIWI_TCMS_URL - Kiwi TCMS base URL (default: https://public.tenant.kiwitcms.org/)")
        print("  KIWI_TCMS_USERNAME - Username for authentication")
        print("  KIWI_TCMS_PASSWORD - Password for authentication")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    item_id = sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    formats = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    base_url = os.environ.get("KIWI_TCMS_URL", "https://public.tenant.kiwitcms.org/")
    username = os.environ.get("KIWI_TCMS_USERNAME", "")
    password = os.environ.get("KIWI_TCMS_PASSWORD", "")
    if not username or not password:
        print("Error: KIWI_TCMS_USERNAME and KIWI_TCMS_PASSWORD must be set")
        sys.exit(1)
    downloader = KiwiTCMSDownloader(base_url, username, password)
    success = False
    if cmd == "test-run":
        success = downloader.export_test_run(item_id, out_dir, formats)
    elif cmd == "test-plan":
        success = downloader.export_test_plan(item_id, out_dir, formats)
    elif cmd == "test-case":
        success = downloader.export_test_case(item_id, out_dir, formats)
    else:
        print(f"Error: Unknown command '{cmd}'")
        sys.exit(1)
    if success:
        print("\nExport completed successfully!")
    else:
        print("\nExport completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
