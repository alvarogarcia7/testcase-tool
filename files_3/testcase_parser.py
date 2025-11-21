#!/usr/bin/env python3
"""
Test Case Parser - Generates shell scripts and markdown from YAML test cases.
"""

import yaml
import sys
import os
from pathlib import Path


def get(data, *keys, default=''):
    """Safely traverse nested dict with dot notation support."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data if data is not None else default


class TestCaseParser:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.tc = None
        self.log = None

    def load(self):
        """Load test case and optional log file."""
        try:
            with open(self.yaml_file) as f:
                self.tc = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error loading {self.yaml_file}: {e}")
            return False

        # Load log file if referenced
        log_file = get(self.tc, 'actual_result', 'log_file')
        if log_file:
            log_path = Path(self.yaml_file).parent / log_file
            if log_path.exists():
                try:
                    with open(log_path) as f:
                        self.log = yaml.safe_load(f)
                except Exception:
                    pass
        return True

    def generate_shell_script(self, output_file):
        """Generate shell script from test case."""
        tc = self.tc
        testcase_id = get(tc, 'testcase_id', default='unknown')
        desc = get(tc, 'description').strip().split('\n')[0]

        lines = [
            "#!/bin/bash",
            f"# Test Case: {testcase_id}",
            f"# Requirement: {get(tc, 'requirement_id', default='N/A')}",
            "set -e",
            "",
            "RED='\\033[0;31m' GREEN='\\033[0;32m' YELLOW='\\033[1;33m' NC='\\033[0m'",
            "",
            f'echo "Test Case: {testcase_id} - {desc}"',
            'echo "="*80',
            "",
        ]

        # Prerequisites
        prereqs = get(tc, 'prerequisites', default=[])
        if prereqs:
            lines.append("# Prerequisites")
            for p in prereqs:
                lines.append(f'echo "  - {p}"')
            lines.append("")

        # Commands
        for step in get(tc, 'commands', default=[]):
            step_num = step.get('step', 0)
            step_desc = step.get('description', f'Step {step_num}')
            lines.extend([
                f'echo ""',
                f'echo "${{YELLOW}}Step {step_num}: {step_desc}${{NC}}"',
            ])
            for cmd in step.get('commands', [step.get('command', '')]):
                if cmd:
                    lines.append(cmd.strip())
            lines.append("")

        # Verification commands
        for i, v in enumerate(get(tc, 'expected_result', 'verification_commands', default=[]), 1):
            lines.append(f"# Verify: {v.get('description', '')}")
            lines.append(v.get('command', ''))

        lines.extend(['', 'echo "${GREEN}Test completed${NC}"'])

        try:
            with open(output_file, 'w') as f:
                f.write('\n'.join(lines))
            os.chmod(output_file, 0o755)
            print(f"Generated: {output_file}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def generate_markdown(self, output_file):
        """Generate markdown documentation from test case."""
        tc = self.tc

        lines = [
            f"# Test Case: {get(tc, 'testcase_id')}",
            "",
            f"**Requirement ID:** {get(tc, 'requirement_id', default='N/A')}",
        ]

        # Metadata
        meta = get(tc, 'metadata', default={})
        if meta.get('tags'):
            lines.append(f"**Tags:** {', '.join(meta['tags'])}")
        if meta.get('categories'):
            lines.append(f"**Categories:** {', '.join(meta['categories'])}")

        # Description
        lines.extend(["", "## Description", "", get(tc, 'description').strip() or "*No description*", ""])

        # Prerequisites
        prereqs = get(tc, 'prerequisites', default=[])
        if prereqs:
            lines.extend(["## Prerequisites", ""])
            lines.extend([f"- {p}" for p in prereqs])
            lines.append("")

        # Test Steps
        commands = get(tc, 'commands', default=[])
        if commands:
            lines.extend(["## Test Steps", ""])
            for step in commands:
                lines.extend([
                    f"### Step {step.get('step', 0)}: {step.get('description', '')}",
                    "",
                    "```bash",
                ])
                for cmd in step.get('commands', [step.get('command', '')]):
                    if cmd:
                        lines.append(cmd.strip())
                lines.extend(["```", ""])

        # Expected Result
        exp = get(tc, 'expected_result', default={})
        if exp:
            lines.extend(["## Expected Result", ""])
            if exp.get('description'):
                lines.extend([exp['description'].strip(), ""])
            if exp.get('expected_outputs'):
                lines.append("**Expected Outputs:**")
                for o in exp['expected_outputs']:
                    val = o.get('value', o.get('condition', ''))
                    lines.append(f"- `{o.get('field', '')}`: {val}")
                lines.append("")

        # Actual Results - dump as YAML for simplicity
        actual = get(tc, 'actual_result', default={})
        if actual:
            lines.extend(["## Actual Result", "", "```yaml"])
            lines.append(yaml.dump(actual, default_flow_style=False, sort_keys=False).strip())
            lines.extend(["```", ""])

        # Verification - dump as YAML
        verify = get(tc, 'verification', default={})
        if verify:
            status = verify.get('status', '')
            emoji = {'PASS': 'PASS', 'FAIL': 'FAIL'}.get(status, status)
            lines.extend([f"## Verification: {emoji}", "", "```yaml"])
            lines.append(yaml.dump(verify, default_flow_style=False, sort_keys=False).strip())
            lines.extend(["```", ""])

        try:
            with open(output_file, 'w') as f:
                f.write('\n'.join(lines))
            print(f"Generated: {output_file}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python testcase_parser.py <testcase.yml> [output_dir]")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else str(Path(yaml_file).parent)
    base_name = Path(yaml_file).stem

    parser = TestCaseParser(yaml_file)
    if not parser.load():
        sys.exit(1)

    shell_file = Path(output_dir) / f"{base_name}.sh"
    md_file = Path(output_dir) / f"{base_name}.md"

    ok = parser.generate_shell_script(str(shell_file))
    ok = parser.generate_markdown(str(md_file)) and ok

    print(f"\nDone: {shell_file}, {md_file}" if ok else "\nCompleted with errors")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
