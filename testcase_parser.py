#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import yaml


def G(d, *keys, default=""):
    for k in keys:
        d = d.get(k, default) if isinstance(d, dict) else default
    return d if d is not None else default


def comment(lines: list[str]):
    return list(map(lambda line: f"# {line}", lines))


class TestCaseParser:
    def __init__(self, yaml_file):
        self.yaml_file, self.test_case, self.actual_log = yaml_file, None, None

    def load_test_case(self):
        t = None
        try:
            t = open(self.yaml_file)
            self.test_case = yaml.safe_load(t)
            return True
        except FileNotFoundError:
            print(f"Error: Test case file '{self.yaml_file}' not found")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
        finally:
            t.close() if t else None
        return False

    def load_actual_log(self):
        log_file = G(self.test_case, "actual_result", "log_file")
        if not log_file:
            return False
        log_path = Path(self.yaml_file).parent / log_file
        assert log_path.exists(), f"Log file '{log_path}' does not exist"
        try:
            with open(log_path) as f:
                self.actual_log = [line.strip() for line in f.readlines()]
                return True
        except Exception as e:
            print(f"Warning: Could not load log file '{log_path}': {e}")
            return False

    def generate_shell_script(self, output_file):
        if not self.test_case:
            print("Error: No test case loaded")
            return False
        tc = self.test_case
        requirement_id = tc.get("requirement")
        tid = requirement_id
        item_no = tc.get("item")
        testcase = tc.get("tc")
        description = tc.get("description", "").strip()
        L = [
            "#!/bin/bash",
            f"# Test Case: {tid}",
            f"# Requirement: {tc.get('requirement_id', 'N/A')}",
            f"# **Requirement ID**: {requirement_id}, Item {item_no}, Test Case {testcase}",
            "",
            "set -e",
            "",
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'",
            "NC='\\033[0m'",
            "",
            'echo "="*80',
            f'echo "Test Case: {tid}"',
            f'echo "Description: {description.split(chr(10))[0] if description else "N/A"}"',
            'echo "="*80',
            "",
        ]
        prereqs = tc.get("prerequisites", [])
        if prereqs:
            L += [
                "# " + "=" * 76,
                "# PREREQUISITES CHECK",
                "# " + "=" * 76,
                "",
                "check_prerequisites() {",
                '    echo "${YELLOW}Checking prerequisites...${NC}"',
                "    local failed=0",
                "",
            ]
            for i, p in enumerate(prereqs, 1):
                L += [f'    echo "  [{i}] {p}"', f"    # TODO: Add actual check for: {p}"]
            L += [
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
        desc = tc.get("description", "").strip()
        L += comment(["# Description", "", desc or "*No description provided*", ""])
        prereqs = tc.get("prerequisites", [])
        if prereqs:
            L += comment(["# Prerequisites", ""] + [f"- {p}" for p in prereqs] + [""])
        for test_sequence in tc.get("test_sequences"):
            L += [f"## Test Sequence: {test_sequence.get('name', 'N/A')}"]
            L += ["## Test Steps"]
            for step in test_sequence.get("steps", []):
                sn = step.get("step", 0)
                L += [f"### Step {sn}: {step.get('description', f'Step {sn}')}"]
                command = step.get("command", None)
                if command:
                    if isinstance(command, str):
                        L += [command]
                    elif isinstance(command, list):
                        L += [c.strip() for c in command]
                L += [f"### End of step {sn}", ""]
        exp = tc.get("expected_result", {})
        vcmds, eouts = exp.get("verification_commands", []), exp.get("expected_outputs", [])
        if vcmds or eouts:
            L += [
                "# " + "=" * 76,
                "# VERIFICATION / ASSERTIONS",
                "# " + "=" * 76,
                "",
                'echo ""',
                'echo "${YELLOW}Running verification checks...${NC}"',
                "",
            ]
            if eouts:
                L.append("# Expected outputs:")
                for o in eouts:
                    f, v, c = o.get("field", ""), o.get("value", ""), o.get("condition", "")
                    L.append(f"# - {f} should be: {v}" if v else f"# - {f} should: {c}")
                L.append("")
            for i, v in enumerate(vcmds, 1):
                L += [
                    f'echo "Verification {i}: {v.get("description", f"Verification {i}")}"',
                    v.get("command", ""),
                    f"VERIFY{i}_STATUS=$?",
                    "",
                ]
        L += [
            "# " + "=" * 76,
            "# TEST SUMMARY",
            "# " + "=" * 76,
            "",
            'echo ""',
            'echo "="*80',
            'echo "${GREEN}Test execution completed${NC}"',
            'echo "="*80',
            "",
        ]
        try:
            open(output_file, "w").write("\n".join(L))
            os.chmod(output_file, 0o755)
            print(f"Generated shell script: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing shell script: {e}")
            return False

    def generate_markdown(self, output_file):
        if not self.test_case:
            print("Error: No test case loaded")
            return False
        tc = self.test_case
        requirement_id = tc.get("requirement")
        item_no = tc.get("item")
        testcase = tc.get("tc")
        L = [
            f"# **Requirement ID**: {requirement_id}, Item {item_no}, Test Case {testcase}",
            "",
        ]
        meta = tc.get("metadata", {})
        if meta.get("tags"):
            L.append(f"**Tags:** {', '.join(meta['tags'])}")
        if meta.get("categories"):
            L.append(f"**Categories:** {', '.join(meta['categories'])}")
        if meta:
            L.append("")
        desc = tc.get("description", "").strip()
        L += comment(["Description", "", desc or "*No description provided*", ""])
        prereqs = tc.get("prerequisites", [])
        if prereqs:
            L += comment(["Prerequisites", ""] + [f"- {p}" for p in prereqs] + [""])
        for test_sequence in tc.get("test_sequences", []):
            L += [f"## Test Sequence: {test_sequence.get('name', 'N/A')}"]
            L += ["## Test Steps", ""]
            for step in test_sequence.get("steps", []):
                sn = step.get("step", 0)
                L += [f"### Step {sn}: {step.get('description', f'Step {sn}')}", ""]
                L += comment([f"- {step.get('description', 'N/A')}", ""])
                command = step.get("command", [])
                if command:
                    L += [c.strip() if isinstance(c, str) else str(c) for c in step.get("commands", [])]
        exp = tc.get("expected_result", {})
        if exp:
            L += ["## Expected Result", ""]
            if exp.get("description", "").strip():
                L += [exp["description"].strip(), ""]
            if exp.get("expected_outputs"):
                L.append("**Expected Outputs:**")
                for o in exp["expected_outputs"]:
                    f, v, c = o.get("field", ""), o.get("value", ""), o.get("condition", "")
                    L.append(f"- `{f}`: {v}" if v else f"- `{f}`: {c}")
                L.append("")
            if exp.get("verification_commands"):
                L += ["**Verification Commands:**", "```bash"]
                for v in exp["verification_commands"]:
                    if v.get("description"):
                        L.append(f"# {v['description']}")
                    L.append(v.get("command", ""))
                L += ["```", ""]
        actual = tc.get("actual_result", {})
        if actual or self.actual_log:
            L += ["## Actual Execution Results", "", "**Execution Info:**"]
            for k, lbl in [
                ("execution_date", "Date"),
                ("executed_by", "Executed by"),
                ("environment", "Environment"),
                ("log_file", "Log File"),
            ]:
                if actual.get(k):
                    L.append(f"- **{lbl}:** {f'`{actual[k]}`' if k == 'log_file' else actual[k]}")
            L.append("")
            if actual.get("summary"):
                L.append("**Summary:**")
                L += [f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in actual["summary"].items()]
                L.append("")
            if self.actual_log:
                self._add_log(L)
        if tc.get("verification"):
            self._add_verif(L, tc["verification"])
        try:
            t = open(output_file, "w")
            t.write("\n".join(L))
            print(f"Generated markdown: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing markdown: {e}")
            return False
        finally:
            t.close()

    def _add_log(self, L):
        L.extend(["**Actual Execution Log:**", ""])
        L.append("```")
        for line in self.actual_log:
            if line.strip() and not line.startswith("#"):
                L.append(line)
        L.extend(["```", ""])

    def _add_verif(self, L, v):
        L += ["## Verification Results", ""]
        if v.get("status"):
            L += [f"**Overall Status:** {v['status']}", ""]
        steps = v.get("verification_steps", [])
        if steps:
            L += ["**Verification Steps:**", "", "| Check | Result |", "|-------|--------|"]
            L += [f"| {s.get('check', '')} | {s.get('result', '')} |" for s in steps]
            L.append("")
        if v.get("comments", "").strip():
            L += ["**Comments:**", "", v["comments"].strip(), ""]
        if any(v.get(k) for k in ["executed_by", "execution_date", "environment"]):
            L.append("**Execution Details:**")
            for k, lbl in [("execution_date", "Date"), ("executed_by", "Executed by"), ("environment", "Environment")]:
                if v.get(k):
                    L.append(f"- **{lbl}:** {v[k]}")
            L.append("")
        issues = v.get("issues", [])
        if issues and any(i.get("issue_id") or i.get("description") for i in issues):
            L += ["**Issues:**", ""]
            for i in issues:
                if i.get("issue_id") or i.get("description"):
                    s = f"- **{i.get('issue_id', '')}**" if i.get("issue_id") else "- "
                    if i.get("severity"):
                        s += f" [{i['severity']}]"
                    if i.get("description"):
                        s += f" {i['description']}"
                    L.append(s)
            L.append("")
        if v.get("notes", "").strip():
            L += ["**Notes:**", "", v["notes"].strip(), ""]


def main():
    if len(sys.argv) < 2:
        print("Usage: python testcase_parser.py <testcase.yml> <output_dir>")
        sys.exit(1)
    yf = sys.argv[1]
    out_dir = Path(sys.argv[2]).absolute() if len(sys.argv) > 2 else "."
    base = Path(yf).absolute()
    p = TestCaseParser(yf)
    if not p.load_test_case():
        sys.exit(1)
    p.load_actual_log()
    sh = Path(out_dir) / f"{base.stem}.sh"
    if p.generate_shell_script(str(sh)):
        print(f"\nGeneration completed!\n  Shell script: {sh}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
