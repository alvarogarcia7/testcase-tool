#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

import yaml


class TestCaseParser:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.test_case = None

    def load_test_case(self):
        try:
            with open(self.yaml_file) as f:
                self.test_case = yaml.safe_load(f)
            return True
        except FileNotFoundError:
            print(f"Error: Test case file '{self.yaml_file}' not found")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
        return False

    def _expand_env_vars(self, text):
        """Expand environment variables in text ($VAR and ${VAR} syntax)"""
        if not isinstance(text, str):
            return text

        # Pattern to match $VAR or ${VAR}
        def replace_var(match):
            var_name = match.group(1) or match.group(2)
            return os.environ.get(var_name, match.group(0))

        # Match ${VAR} or $VAR (word characters only for $VAR)
        return re.sub(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)', replace_var, text)

    def generate_shell_script(self, output_file):
        if not self.test_case:
            print("Error: No test case loaded")
            return False

        tc = self.test_case
        lines = [
            "#!/bin/bash",
            f"# Test Case: {tc.get('testcase_id', tc.get('id', 'unknown'))}",
            f"# Requirement: {tc.get('requirement_id', 'N/A')}",
            "",
            "set -e",
            "",
        ]

        # Add description if available
        desc = tc.get("description", "").strip()
        if desc:
            lines.append(f"# Description: {desc.split(chr(10))[0]}")
            lines.append("")

        # Color codes
        lines.extend([
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'",
            "NC='\\033[0m'",
            "",
        ])

        # Header
        lines.extend([
            'echo "="*80',
            f'echo "Test Case: {tc.get("testcase_id", tc.get("id", "unknown"))}"',
            'echo "="*80',
            "",
        ])

        # Prerequisites
        prereqs = tc.get("prerequisites", [])
        if prereqs:
            lines.extend([
                'echo "${YELLOW}Prerequisites:${NC}"',
            ])
            for p in prereqs:
                lines.append(f'echo "  - {p}"')
            lines.append("")

        # Commands
        cmds = tc.get("commands", [])
        if cmds:
            lines.extend(['echo "${YELLOW}Executing test steps...${NC}"', ""])
            for step in cmds:
                step_num = step.get("step", 0)
                step_desc = step.get("description", f"Step {step_num}")
                lines.extend([
                    f'echo "Step {step_num}: {step_desc}"',
                    "",
                ])
                for cmd in step.get("commands", []):
                    cmd_text = cmd.strip() if isinstance(cmd, str) else str(cmd)
                    # Expand environment variables in command
                    cmd_text = self._expand_env_vars(cmd_text)
                    lines.extend([cmd_text, ""])

        # Verification commands
        vcmds = tc.get("verification_commands", [])
        if vcmds:
            lines.extend(['echo "${YELLOW}Running verification...${NC}"', ""])
            for vcmd in vcmds:
                if isinstance(vcmd, dict):
                    desc = vcmd.get("description", "")
                    if desc:
                        lines.append(f'echo "{desc}"')
                    for cmd in vcmd.get("commands", []):
                        cmd_text = cmd.strip() if isinstance(cmd, str) else str(cmd)
                        cmd_text = self._expand_env_vars(cmd_text)
                        lines.extend([cmd_text, ""])

        # Summary
        lines.extend([
            'echo ""',
            'echo "="*80',
            'echo "${GREEN}Test completed${NC}"',
            'echo "="*80',
        ])

        try:
            with open(output_file, "w") as f:
                f.write("\n".join(lines))
            os.chmod(output_file, 0o755)
            print(f"Generated shell script: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing shell script: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python testcase_parser.py <testcase.yml> [output_dir]")
        sys.exit(1)

    yaml_file = sys.argv[1]
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    parser = TestCaseParser(yaml_file)
    if not parser.load_test_case():
        sys.exit(1)

    output_file = out_dir / f"{Path(yaml_file).stem}.sh"
    if parser.generate_shell_script(str(output_file)):
        print(f"\nGeneration completed!\n  Shell script: {output_file}")
    else:
        print("\nGeneration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
