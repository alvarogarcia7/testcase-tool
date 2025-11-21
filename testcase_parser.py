#!/usr/bin/env python3
"""
Test Case Parser
Reads test case YAML files and generates:
1. Shell script (.sh) with prerequisites, commands, and assertions
2. Markdown documentation (.md) with test case details and execution logs
"""

import os
import sys
from pathlib import Path

import yaml


def get(data, *keys, default=""):
    """Safely get nested values from dict."""
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key, default)
    return data if data is not None else default


class TestCaseParser:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.test_case = None
        self.actual_log = None

    def load_test_case(self):
        """Load the test case YAML file"""
        try:
            with open(self.yaml_file, "r") as f:
                self.test_case = yaml.safe_load(f)
            return True
        except FileNotFoundError:
            print(f"Error: Test case file '{self.yaml_file}' not found")
            return False
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return False

    def load_actual_log(self):
        """Load the actual execution log if it exists"""
        log_file = get(self.test_case, "actual_result", "log_file")
        if not log_file:
            return False

        log_path = Path(self.yaml_file).parent / log_file
        if not log_path.exists():
            return False

        try:
            with open(log_path, "r") as f:
                self.actual_log = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Warning: Could not load log file '{log_path}': {e}")
            return False

    def generate_shell_script(self, output_file):
        """Generate shell script with prerequisites, commands, and assertions"""
        if not self.test_case:
            print("Error: No test case loaded")
            return False

        tc = self.test_case
        testcase_id = tc.get("testcase_id", "unknown")
        desc = tc.get("description", "").strip()
        desc_line = desc.split("\n")[0] if desc else "N/A"

        lines = [
            "#!/bin/bash",
            "# Auto-generated test script",
            f"# Test Case: {testcase_id}",
            f"# Requirement: {tc.get('requirement_id', 'N/A')}",
            "",
            "set -e  # Exit on error",
            "",
            "# Colors for output",
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'",
            "NC='\\033[0m' # No Color",
            "",
            'echo "="*80',
            f'echo "Test Case: {testcase_id}"',
            f'echo "Description: {desc_line}"',
            'echo "="*80',
            "",
        ]

        # Prerequisites
        prereqs = tc.get("prerequisites", [])
        if prereqs:
            lines += [
                "# ============================================================================",
                "# PREREQUISITES CHECK",
                "# ============================================================================",
                "",
                "check_prerequisites() {",
                '    echo "${YELLOW}Checking prerequisites...${NC}"',
                "    local failed=0",
                "",
            ]
            for i, prereq in enumerate(prereqs, 1):
                lines += [f'    echo "  [{i}] {prereq}"', f"    # TODO: Add actual check for: {prereq}"]
            lines += [
                "",
                "    if [ $failed -eq 0 ]; then",
                '        echo "${GREEN}All prerequisites met${NC}"',
                "        return 0",
                "    else",
                '        echo "${RED}Prerequisites check failed${NC}"',
                "        return 1",
                "    fi",
                "}",
                "",
                "check_prerequisites || exit 1",
                "",
            ]

        # Commands
        commands = tc.get("commands", [])
        if commands:
            lines += [
                "# ============================================================================",
                "# TEST EXECUTION",
                "# ============================================================================",
                "",
            ]
            for step in commands:
                step_num = step.get("step", 0)
                step_desc = step.get("description", f"Step {step_num}")
                notes = step.get("notes", "")

                lines.append(f"# Step {step_num}: {step_desc}")
                if notes:
                    lines.append(f"# Note: {notes}")
                lines += [
                    'echo ""',
                    f'echo "${{YELLOW}}Step {step_num}: {step_desc}${{NC}}"',
                    'echo "-"*80',
                    "",
                ]

                for i, cmd in enumerate(step.get("commands", []), 1):
                    cmd_str = cmd.strip() if isinstance(cmd, str) else str(cmd)
                    cmd_preview = f"{cmd_str.split(chr(10))[0]}..." if "\n" in cmd_str else cmd_str
                    lines += [
                        f'echo "Executing command {i}..."',
                        f'echo "Command: {cmd_preview}"',
                        "",
                        cmd_str,
                        f"STEP{step_num}_CMD{i}_STATUS=$?",
                        "",
                    ]
                lines.append(f'echo "${{GREEN}}Step {step_num} completed${{NC}}"')
                lines.append("")

        # Verification
        exp = tc.get("expected_result", {})
        verify_cmds = exp.get("verification_commands", [])
        exp_outputs = exp.get("expected_outputs", [])

        if verify_cmds or exp_outputs:
            lines += [
                "# ============================================================================",
                "# VERIFICATION / ASSERTIONS",
                "# ============================================================================",
                "",
                'echo ""',
                'echo "${YELLOW}Running verification checks...${NC}"',
                "",
            ]
            if exp_outputs:
                lines.append("# Expected outputs:")
                for out in exp_outputs:
                    f, v, c = out.get("field", ""), out.get("value", ""), out.get("condition", "")
                    lines.append(f"# - {f} should be: {v}" if v else f"# - {f} should: {c}")
                lines.append("")

            for i, v in enumerate(verify_cmds, 1):
                lines += [
                    f'echo "Verification {i}: {v.get("description", f"Verification {i}")}"',
                    v.get("command", ""),
                    f"VERIFY{i}_STATUS=$?",
                    "",
                ]

        # Summary
        lines += [
            "# ============================================================================",
            "# TEST SUMMARY",
            "# ============================================================================",
            "",
            'echo ""',
            'echo "="*80',
            'echo "${GREEN}Test execution completed${NC}"',
            'echo "="*80',
            "",
        ]

        try:
            with open(output_file, "w") as f:
                f.write("\n".join(lines))
            os.chmod(output_file, 0o755)
            print(f"Generated shell script: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing shell script: {e}")
            return False

    def generate_markdown(self, output_file):
        """Generate markdown documentation with test case details and execution logs"""
        if not self.test_case:
            print("Error: No test case loaded")
            return False

        tc = self.test_case
        lines = [
            f"# Test Case: {tc.get('testcase_id', 'Unknown')}",
            "",
            f"**Requirement ID:** {tc.get('requirement_id', 'N/A')}",
            "",
        ]

        # Metadata
        meta = tc.get("metadata", {})
        if meta.get("tags"):
            lines.append(f"**Tags:** {', '.join(meta['tags'])}")
        if meta.get("categories"):
            lines.append(f"**Categories:** {', '.join(meta['categories'])}")
        if meta:
            lines.append("")

        # Description
        desc = tc.get("description", "").strip()
        lines += ["## Description", "", desc or "*No description provided*", ""]

        # Prerequisites
        prereqs = tc.get("prerequisites", [])
        if prereqs:
            lines += ["## Prerequisites", ""] + [f"- {p}" for p in prereqs] + [""]

        # Test Steps
        commands = tc.get("commands", [])
        if commands:
            lines += ["## Test Steps", ""]
            for step in commands:
                step_num = step.get("step", 0)
                lines += [f"### Step {step_num}: {step.get('description', f'Step {step_num}')}", ""]
                if step.get("notes"):
                    lines += [f"*Note: {step['notes']}*", ""]
                lines += ["**Commands:**", "```bash"]
                for cmd in step.get("commands", []):
                    lines.append(cmd.strip() if isinstance(cmd, str) else str(cmd))
                lines += ["```", ""]

        # Expected Result
        exp = tc.get("expected_result", {})
        if exp:
            lines += ["## Expected Result", ""]
            if exp.get("description", "").strip():
                lines += [exp["description"].strip(), ""]

            if exp.get("expected_outputs"):
                lines.append("**Expected Outputs:**")
                for out in exp["expected_outputs"]:
                    f, v, c = out.get("field", ""), out.get("value", ""), out.get("condition", "")
                    lines.append(f"- `{f}`: {v}" if v else f"- `{f}`: {c}")
                lines.append("")

            if exp.get("verification_commands"):
                lines += ["**Verification Commands:**", "```bash"]
                for v in exp["verification_commands"]:
                    if v.get("description"):
                        lines.append(f"# {v['description']}")
                    lines.append(v.get("command", ""))
                lines += ["```", ""]

        # Actual Execution Results
        actual = tc.get("actual_result", {})
        if actual or self.actual_log:
            lines += ["## Actual Execution Results", "", "**Execution Info:**"]
            for key, label in [("execution_date", "Date"), ("executed_by", "Executed by"),
                               ("environment", "Environment"), ("log_file", "Log File")]:
                if actual.get(key):
                    val = f"`{actual[key]}`" if key == "log_file" else actual[key]
                    lines.append(f"- **{label}:** {val}")
            lines.append("")

            if actual.get("summary"):
                lines.append("**Summary:**")
                for k, v in actual["summary"].items():
                    lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
                lines.append("")

            if self.actual_log:
                self._add_execution_log(lines)

        # Verification Results
        verif = tc.get("verification", {})
        if verif:
            self._add_verification(lines, verif)

        try:
            with open(output_file, "w") as f:
                f.write("\n".join(lines))
            print(f"Generated markdown: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing markdown: {e}")
            return False

    def _add_execution_log(self, lines):
        """Add execution log section to markdown."""
        log_entries = self.actual_log.get("execution_log", [])
        if log_entries:
            lines += ["### Execution Log", ""]
            for entry in log_entries:
                lines += [
                    f"#### Step {entry.get('step', 0)}: {entry.get('description', '')}",
                    "",
                    f"*Timestamp: {entry.get('timestamp', '')}*",
                    "",
                ]
                for i, cmd in enumerate(entry.get("commands", []), 1):
                    lines += [f"**Command {i}:**", "```bash", cmd.get("command", ""), "```", ""]
                    sc = cmd.get("status_code")
                    if sc is not None:
                        lines.append(f"**Status Code:** {sc} {'✅' if sc == 0 else '❌'}")
                    if cmd.get("duration_ms"):
                        lines.append(f"**Duration:** {cmd['duration_ms']}ms")
                    if cmd.get("output"):
                        lines += ["", "**Output:**", "```", cmd["output"].strip(), "```"]
                    if cmd.get("stderr"):
                        lines += ["", "**Error Output:**", "```", cmd["stderr"].strip(), "```"]
                    lines.append("")

        env_info = self.actual_log.get("environment_info", {})
        if env_info:
            lines += ["### Environment Details", ""]
            for k, v in env_info.items():
                lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            lines.append("")

    def _add_verification(self, lines, verif):
        """Add verification results section to markdown."""
        lines += ["## Verification Results", ""]

        status = verif.get("status", "")
        if status:
            emoji = {"PASS": "✅", "FAIL": "❌", "BLOCKED": "🚫", "SKIPPED": "⏭️"}.get(status, "")
            lines += [f"**Overall Status:** {status} {emoji}", ""]

        steps = verif.get("verification_steps", [])
        if steps:
            lines += ["**Verification Steps:**", "", "| Check | Result |", "|-------|--------|"]
            for s in steps:
                emoji = "✅" if s.get("result") == "PASS" else "❌"
                lines.append(f"| {s.get('check', '')} | {s.get('result', '')} {emoji} |")
            lines.append("")

        if verif.get("comments", "").strip():
            lines += ["**Comments:**", "", verif["comments"].strip(), ""]

        if any(verif.get(k) for k in ["executed_by", "execution_date", "environment"]):
            lines.append("**Execution Details:**")
            for key, label in [("execution_date", "Date"), ("executed_by", "Executed by"), ("environment", "Environment")]:
                if verif.get(key):
                    lines.append(f"- **{label}:** {verif[key]}")
            lines.append("")

        issues = verif.get("issues", [])
        if issues and any(i.get("issue_id") or i.get("description") for i in issues):
            lines += ["**Issues:**", ""]
            for issue in issues:
                if issue.get("issue_id") or issue.get("description"):
                    s = f"- **{issue.get('issue_id', '')}**" if issue.get("issue_id") else "- "
                    if issue.get("severity"):
                        s += f" [{issue['severity']}]"
                    if issue.get("description"):
                        s += f" {issue['description']}"
                    lines.append(s)
            lines.append("")

        if verif.get("notes", "").strip():
            lines += ["**Notes:**", "", verif["notes"].strip(), ""]


def main():
    if len(sys.argv) < 2:
        print("Usage: python testcase_parser.py <testcase.yml> [output_dir]")
        print("Example: python testcase_parser.py X20_1.yml")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else str(Path(yaml_file).parent)
    base_name = Path(yaml_file).stem

    parser = TestCaseParser(yaml_file)
    if not parser.load_test_case():
        sys.exit(1)

    parser.load_actual_log()

    shell_file = Path(output_dir) / f"{base_name}.sh"
    markdown_file = Path(output_dir) / f"{base_name}.md"

    success = parser.generate_shell_script(str(shell_file)) and parser.generate_markdown(str(markdown_file))

    if success:
        print(f"\nGeneration completed successfully!")
        print(f"  Shell script: {shell_file}")
        print(f"  Markdown doc: {markdown_file}")
    else:
        print("\nGeneration completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
