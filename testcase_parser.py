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
