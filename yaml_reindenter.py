#!/usr/bin/env python3
import re
import sys
from typing import Dict, List, Optional, Tuple


class YamlReindenter:
    def __init__(self, yaml_file: str) -> None:
        self.yaml_file: str = yaml_file
        self.content: Optional[str] = None
        self.lines: Optional[List[str]] = None

    def load_file(self) -> bool:
        try:
            with open(self.yaml_file, "r") as f:
                self.content = f.read()
                self.lines = self.content.splitlines()
                return True
        except FileNotFoundError:
            print(f"Error: File '{self.yaml_file}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")
        return False

    def detect_pipe_blocks(self) -> List[Dict[str, any]]:
        blocks = []
        for i, line in enumerate(self.lines):
            if re.search(r":\s*\|", line):
                indent = len(line) - len(line.lstrip())
                blocks.append({"line_num": i, "pipe_indent": indent, "key_line": line})
        return blocks

    def get_block_content(self, start_line: int, pipe_indent: int) -> Tuple[List[int], int]:
        content_lines = []
        expected_indent = pipe_indent + 2
        for i in range(start_line + 1, len(self.lines)):
            line = self.lines[i]
            if not line.strip():
                content_lines.append(i)
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= pipe_indent:
                break
            content_lines.append(i)
        return content_lines, expected_indent

    def check_indentation(self, line_nums: List[int], expected_indent: int) -> List[Dict[str, int]]:
        issues = []
        for ln in line_nums:
            line = self.lines[ln]
            if not line.strip():
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent != expected_indent:
                issues.append({"line_num": ln, "current_indent": current_indent, "expected_indent": expected_indent})
        return issues

    def fix_indentation(self, issues: List[Dict[str, int]]) -> bool:
        if not issues:
            return False
        fixed_lines = self.lines.copy()
        for issue in issues:
            ln = issue["line_num"]
            line = fixed_lines[ln]
            expected_indent = issue["expected_indent"]
            stripped = line.lstrip()
            fixed_lines[ln] = " " * expected_indent + stripped
        self.lines = fixed_lines
        self.content = "\n".join(fixed_lines)
        return True

    def analyze(self) -> List[Dict[str, int]]:
        if not self.content:
            print("Error: No content loaded")
            return []
        blocks = self.detect_pipe_blocks()
        all_issues = []
        for block in blocks:
            content_lines, expected_indent = self.get_block_content(block["line_num"], block["pipe_indent"])
            issues = self.check_indentation(content_lines, expected_indent)
            if issues:
                all_issues.extend(issues)
        return all_issues

    def reindent(self) -> bool:
        issues = self.analyze()
        if not issues:
            return False
        return self.fix_indentation(issues)

    def save_file(self, output_file: Optional[str] = None) -> bool:
        if not self.content:
            print("Error: No content to save")
            return False
        out = output_file or self.yaml_file
        try:
            with open(out, "w") as f:
                f.write(self.content)
                if not self.content.endswith("\n"):
                    f.write("\n")
            print(f"Saved: {out}")
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python yaml_reindenter.py <yaml_file> [output_file]")
        print("  <yaml_file>   - YAML file to reindent")
        print("  [output_file] - Optional output file (defaults to overwriting input)")
        sys.exit(1)
    yaml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    reindenter = YamlReindenter(yaml_file)
    if not reindenter.load_file():
        sys.exit(1)
    issues = reindenter.analyze()
    if not issues:
        print("No indentation issues found")
        sys.exit(0)
    print(f"Found {len(issues)} indentation issue(s)")
    for issue in issues:
        print(f"  Line {issue['line_num'] + 1}: {issue['current_indent']} spaces -> {issue['expected_indent']} spaces")
    if reindenter.reindent():
        if reindenter.save_file(output_file):
            print("Reindentation completed successfully")
        else:
            sys.exit(1)
    else:
        print("Failed to fix indentation")
        sys.exit(1)


if __name__ == "__main__":
    main()
