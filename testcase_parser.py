#!/usr/bin/env python3
import os, sys
from pathlib import Path
import yaml

def G(d, *keys, default=""):
    for k in keys:
        d = d.get(k, default) if isinstance(d, dict) else default
    return d if d is not None else default

class TestCaseParser:
    def __init__(self, yaml_file):
        self.yaml_file, self.test_case, self.actual_log = yaml_file, None, None

    def load_test_case(self):
        try:
            self.test_case = yaml.safe_load(open(self.yaml_file))
            return True
        except FileNotFoundError:
            print(f"Error: Test case file '{self.yaml_file}' not found")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
        return False

    def load_actual_log(self):
        log_file = G(self.test_case, "actual_result", "log_file")
        if not log_file: return False
        log_path = Path(self.yaml_file).parent / log_file
        if not log_path.exists(): return False
        try:
            self.actual_log = yaml.safe_load(open(log_path))
            return True
        except Exception as e:
            print(f"Warning: Could not load log file '{log_path}': {e}")
            return False

    def generate_shell_script(self, output_file):
        if not self.test_case:
            print("Error: No test case loaded")
            return False
        tc = self.test_case
        tid, desc = tc.get("testcase_id", "unknown"), tc.get("description", "").strip()
        L = [
            "#!/bin/bash", f"# Test Case: {tid}", f"# Requirement: {tc.get('requirement_id', 'N/A')}",
            "", "set -e", "", "RED='\\033[0;31m'", "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'", "NC='\\033[0m'", "", 'echo "="*80',
            f'echo "Test Case: {tid}"', f'echo "Description: {desc.split(chr(10))[0] if desc else "N/A"}"',
            'echo "="*80', ""
        ]
        prereqs = tc.get("prerequisites", [])
        if prereqs:
            L += ["# " + "="*76, "# PREREQUISITES CHECK", "# " + "="*76, "",
                  "check_prerequisites() {", '    echo "${YELLOW}Checking prerequisites...${NC}"',
                  "    local failed=0", ""]
            for i, p in enumerate(prereqs, 1):
                L += [f'    echo "  [{i}] {p}"', f"    # TODO: Add actual check for: {p}"]
            L += ["", "    if [ $failed -eq 0 ]; then", '        echo "${GREEN}All prerequisites met${NC}"',
                  "        return 0", "    else", '        echo "${RED}Prerequisites check failed${NC}"',
                  "        return 1", "    fi", "}", "", "check_prerequisites || exit 1", ""]
        cmds = tc.get("commands", [])
        if cmds:
            L += ["# " + "="*76, "# TEST EXECUTION", "# " + "="*76, ""]
            for step in cmds:
                sn, sd = step.get("step", 0), step.get("description", f"Step {step.get('step', 0)}")
                L.append(f"# Step {sn}: {sd}")
                if step.get("notes"): L.append(f"# Note: {step['notes']}")
                L += ['echo ""', f'echo "${{YELLOW}}Step {sn}: {sd}${{NC}}"', 'echo "-"*80', ""]
                for i, cmd in enumerate(step.get("commands", []), 1):
                    cs = cmd.strip() if isinstance(cmd, str) else str(cmd)
                    L += [f'echo "Executing command {i}..."',
                          f'echo "Command: {cs.split(chr(10))[0]}{"..." if chr(10) in cs else ""}"',
                          "", cs, f"STEP{sn}_CMD{i}_STATUS=$?", ""]
                L += [f'echo "${{GREEN}}Step {sn} completed${{NC}}"', ""]
        exp = tc.get("expected_result", {})
        vcmds, eouts = exp.get("verification_commands", []), exp.get("expected_outputs", [])
        if vcmds or eouts:
            L += ["# " + "="*76, "# VERIFICATION / ASSERTIONS", "# " + "="*76, "",
                  'echo ""', 'echo "${YELLOW}Running verification checks...${NC}"', ""]
            if eouts:
                L.append("# Expected outputs:")
                for o in eouts:
                    f, v, c = o.get("field", ""), o.get("value", ""), o.get("condition", "")
                    L.append(f"# - {f} should be: {v}" if v else f"# - {f} should: {c}")
                L.append("")
            for i, v in enumerate(vcmds, 1):
                L += [f'echo "Verification {i}: {v.get("description", f"Verification {i}")}"',
                      v.get("command", ""), f"VERIFY{i}_STATUS=$?", ""]
        L += ["# " + "="*76, "# TEST SUMMARY", "# " + "="*76, "", 'echo ""', 'echo "="*80',
              'echo "${GREEN}Test execution completed${NC}"', 'echo "="*80', ""]
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
        L = [f"# Test Case: {tc.get('testcase_id', 'Unknown')}", "",
             f"**Requirement ID:** {tc.get('requirement_id', 'N/A')}", ""]
        meta = tc.get("metadata", {})
        if meta.get("tags"): L.append(f"**Tags:** {', '.join(meta['tags'])}")
        if meta.get("categories"): L.append(f"**Categories:** {', '.join(meta['categories'])}")
        if meta: L.append("")
        desc = tc.get("description", "").strip()
        L += ["## Description", "", desc or "*No description provided*", ""]
        prereqs = tc.get("prerequisites", [])
        if prereqs: L += ["## Prerequisites", ""] + [f"- {p}" for p in prereqs] + [""]
        cmds = tc.get("commands", [])
        if cmds:
            L += ["## Test Steps", ""]
            for step in cmds:
                sn = step.get("step", 0)
                L += [f"### Step {sn}: {step.get('description', f'Step {sn}')}", ""]
                if step.get("notes"): L += [f"*Note: {step['notes']}*", ""]
                L += ["**Commands:**", "```bash"]
                L += [c.strip() if isinstance(c, str) else str(c) for c in step.get("commands", [])]
                L += ["```", ""]
        exp = tc.get("expected_result", {})
        if exp:
            L += ["## Expected Result", ""]
            if exp.get("description", "").strip(): L += [exp["description"].strip(), ""]
            if exp.get("expected_outputs"):
                L.append("**Expected Outputs:**")
                for o in exp["expected_outputs"]:
                    f, v, c = o.get("field", ""), o.get("value", ""), o.get("condition", "")
                    L.append(f"- `{f}`: {v}" if v else f"- `{f}`: {c}")
                L.append("")
            if exp.get("verification_commands"):
                L += ["**Verification Commands:**", "```bash"]
                for v in exp["verification_commands"]:
                    if v.get("description"): L.append(f"# {v['description']}")
                    L.append(v.get("command", ""))
                L += ["```", ""]
        actual = tc.get("actual_result", {})
        if actual or self.actual_log:
            L += ["## Actual Execution Results", "", "**Execution Info:**"]
            for k, lbl in [("execution_date", "Date"), ("executed_by", "Executed by"),
                           ("environment", "Environment"), ("log_file", "Log File")]:
                if actual.get(k): L.append(f"- **{lbl}:** {f'`{actual[k]}`' if k == 'log_file' else actual[k]}")
            L.append("")
            if actual.get("summary"):
                L.append("**Summary:**")
                L += [f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in actual["summary"].items()]
                L.append("")
            if self.actual_log: self._add_log(L)
        if tc.get("verification"): self._add_verif(L, tc["verification"])
        try:
            open(output_file, "w").write("\n".join(L))
            print(f"Generated markdown: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing markdown: {e}")
            return False

    def _add_log(self, L):
        entries = self.actual_log.get("execution_log", [])
        if entries:
            L += ["### Execution Log", ""]
            for e in entries:
                L += [f"#### Step {e.get('step', 0)}: {e.get('description', '')}", "",
                      f"*Timestamp: {e.get('timestamp', '')}*", ""]
                for i, c in enumerate(e.get("commands", []), 1):
                    L += [f"**Command {i}:**", "```bash", c.get("command", ""), "```", ""]
                    sc = c.get("status_code")
                    if sc is not None: L.append(f"**Status Code:** {sc} [{'OK' if sc == 0 else 'FAIL'}]")
                    if c.get("duration_ms"): L.append(f"**Duration:** {c['duration_ms']}ms")
                    if c.get("output"): L += ["", "**Output:**", "```", c["output"].strip(), "```"]
                    if c.get("stderr"): L += ["", "**Error Output:**", "```", c["stderr"].strip(), "```"]
                    L.append("")
        env = self.actual_log.get("environment_info", {})
        if env:
            L += ["### Environment Details", ""]
            L += [f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in env.items()] + [""]

    def _add_verif(self, L, v):
        L += ["## Verification Results", ""]
        if v.get("status"):
            L += [f"**Overall Status:** {v['status']}", ""]
        steps = v.get("verification_steps", [])
        if steps:
            L += ["**Verification Steps:**", "", "| Check | Result |", "|-------|--------|"]
            L += [f"| {s.get('check', '')} | {s.get('result', '')} |" for s in steps]
            L.append("")
        if v.get("comments", "").strip(): L += ["**Comments:**", "", v["comments"].strip(), ""]
        if any(v.get(k) for k in ["executed_by", "execution_date", "environment"]):
            L.append("**Execution Details:**")
            for k, lbl in [("execution_date", "Date"), ("executed_by", "Executed by"), ("environment", "Environment")]:
                if v.get(k): L.append(f"- **{lbl}:** {v[k]}")
            L.append("")
        issues = v.get("issues", [])
        if issues and any(i.get("issue_id") or i.get("description") for i in issues):
            L += ["**Issues:**", ""]
            for i in issues:
                if i.get("issue_id") or i.get("description"):
                    s = f"- **{i.get('issue_id', '')}**" if i.get("issue_id") else "- "
                    if i.get("severity"): s += f" [{i['severity']}]"
                    if i.get("description"): s += f" {i['description']}"
                    L.append(s)
            L.append("")
        if v.get("notes", "").strip(): L += ["**Notes:**", "", v["notes"].strip(), ""]

def main():
    if len(sys.argv) < 2:
        print("Usage: python testcase_parser.py <testcase.yml> [output_dir]")
        sys.exit(1)
    yf = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else str(Path(yf).parent)
    base = Path(yf).stem
    p = TestCaseParser(yf)
    if not p.load_test_case(): sys.exit(1)
    p.load_actual_log()
    sh, md = Path(out_dir) / f"{base}.sh", Path(out_dir) / f"{base}.md"
    if p.generate_shell_script(str(sh)) and p.generate_markdown(str(md)):
        print(f"\nGeneration completed!\n  Shell script: {sh}\n  Markdown doc: {md}")
    else:
        print("\nGeneration completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
