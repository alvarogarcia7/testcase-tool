#!/usr/bin/env python3
"""
Test Case Parser
Reads test case YAML files and generates:
1. Shell script (.sh) with prerequisites, commands, and assertions
2. Markdown documentation (.md) with test case details and execution logs
"""

import yaml
import sys
import os
from pathlib import Path


class TestCaseParser:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.test_case = None
        self.actual_log = None
        
    def load_test_case(self):
        """Load the test case YAML file"""
        try:
            with open(self.yaml_file, 'r') as f:
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
        if not self.test_case or 'actual_result' not in self.test_case:
            return False
        
        log_file = self.test_case.get('actual_result', {}).get('log_file', '')
        if not log_file:
            return False
        
        # Look for log file in same directory as test case
        log_path = Path(self.yaml_file).parent / log_file
        
        if not log_path.exists():
            return False
        
        try:
            with open(log_path, 'r') as f:
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
        
        testcase_id = self.test_case.get('testcase_id', 'unknown')
        description = self.test_case.get('description', '').strip()
        prerequisites = self.test_case.get('prerequisites', [])
        commands = self.test_case.get('commands', [])
        expected_result = self.test_case.get('expected_result', {})
        
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated test script",
            f"# Test Case: {testcase_id}",
            f"# Requirement: {self.test_case.get('requirement_id', 'N/A')}",
            "",
            "set -e  # Exit on error",
            "",
            "# Colors for output",
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'",
            "NC='\\033[0m' # No Color",
            "",
            "echo \"=\"*80",
            f"echo \"Test Case: {testcase_id}\"",
            f"echo \"Description: {description.split(chr(10))[0] if description else 'N/A'}\"",
            "echo \"=\"*80",
            "",
        ]
        
        # Prerequisites check section
        if prerequisites:
            script_lines.extend([
                "# ============================================================================",
                "# PREREQUISITES CHECK",
                "# ============================================================================",
                "",
                "check_prerequisites() {",
                "    echo \"${YELLOW}Checking prerequisites...${NC}\"",
                "    local failed=0",
                "",
            ])
            
            for i, prereq in enumerate(prerequisites, 1):
                script_lines.append(f"    echo \"  [{i}] {prereq}\"")
                script_lines.append(f"    # TODO: Add actual check for: {prereq}")
            
            script_lines.extend([
                "",
                "    if [ $failed -eq 0 ]; then",
                "        echo \"${GREEN}All prerequisites met${NC}\"",
                "        return 0",
                "    else",
                "        echo \"${RED}Prerequisites check failed${NC}\"",
                "        return 1",
                "    fi",
                "}",
                "",
                "check_prerequisites || exit 1",
                "",
            ])
        
        # Commands execution section
        if commands:
            script_lines.extend([
                "# ============================================================================",
                "# TEST EXECUTION",
                "# ============================================================================",
                "",
            ])
            
            for step_data in commands:
                step_num = step_data.get('step', 0)
                step_desc = step_data.get('description', f'Step {step_num}')
                step_commands = step_data.get('commands', [])
                expected_status = step_data.get('expected_status', 0)
                notes = step_data.get('notes', '')
                
                script_lines.extend([
                    f"# Step {step_num}: {step_desc}",
                ])
                
                if notes:
                    script_lines.append(f"# Note: {notes}")
                
                script_lines.extend([
                    "echo \"\"",
                    "echo \"${YELLOW}Step " + str(step_num) + ": " + step_desc + "${NC}\"",
                    "echo \"-\"*80",
                    "",
                ])
                
                for i, cmd in enumerate(step_commands, 1):
                    # Handle multi-line commands
                    cmd_str = cmd.strip() if isinstance(cmd, str) else str(cmd)
                    
                    script_lines.extend([
                        f"echo \"Executing command {i}...\"",
                        f"echo \"Command: {cmd_str.split(chr(10))[0]}...\"" if '\n' in cmd_str else f"echo \"Command: {cmd_str}\"",
                        "",
                    ])
                    
                    # Add the actual command
                    if '\n' in cmd_str:
                        # Multi-line command
                        script_lines.append(cmd_str)
                    else:
                        # Single line command
                        script_lines.append(cmd_str)
                    
                    script_lines.extend([
                        f"STEP{step_num}_CMD{i}_STATUS=$?",
                        "",
                    ])
                
                script_lines.extend([
                    "echo \"${GREEN}Step " + str(step_num) + " completed${NC}\"",
                    "",
                ])
        
        # Verification/Assertion section
        verification_commands = expected_result.get('verification_commands', [])
        expected_outputs = expected_result.get('expected_outputs', [])
        
        if verification_commands or expected_outputs:
            script_lines.extend([
                "# ============================================================================",
                "# VERIFICATION / ASSERTIONS",
                "# ============================================================================",
                "",
                "echo \"\"",
                "echo \"${YELLOW}Running verification checks...${NC}\"",
                "",
            ])
            
            if expected_outputs:
                script_lines.append("# Expected outputs:")
                for output in expected_outputs:
                    field = output.get('field', '')
                    value = output.get('value', '')
                    condition = output.get('condition', '')
                    
                    if value:
                        script_lines.append(f"# - {field} should be: {value}")
                    elif condition:
                        script_lines.append(f"# - {field} should: {condition}")
                
                script_lines.append("")
            
            if verification_commands:
                for i, verify in enumerate(verification_commands, 1):
                    verify_desc = verify.get('description', f'Verification {i}')
                    verify_cmd = verify.get('command', '')
                    
                    script_lines.extend([
                        f"echo \"Verification {i}: {verify_desc}\"",
                        verify_cmd,
                        f"VERIFY{i}_STATUS=$?",
                        "",
                    ])
        
        # Final status
        script_lines.extend([
            "# ============================================================================",
            "# TEST SUMMARY",
            "# ============================================================================",
            "",
            "echo \"\"",
            "echo \"=\"*80",
            "echo \"${GREEN}Test execution completed${NC}\"",
            "echo \"=\"*80",
            "",
        ])
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                f.write('\n'.join(script_lines))
            
            # Make script executable
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
        
        testcase_id = self.test_case.get('testcase_id', 'Unknown')
        requirement_id = self.test_case.get('requirement_id', 'N/A')
        metadata = self.test_case.get('metadata', {})
        description = self.test_case.get('description', '').strip()
        prerequisites = self.test_case.get('prerequisites', [])
        commands = self.test_case.get('commands', [])
        expected_result = self.test_case.get('expected_result', {})
        actual_result = self.test_case.get('actual_result', {})
        verification = self.test_case.get('verification', {})
        
        md_lines = [
            f"# Test Case: {testcase_id}",
            "",
            f"**Requirement ID:** {requirement_id}",
            "",
        ]
        
        # Metadata
        if metadata:
            tags = metadata.get('tags', [])
            categories = metadata.get('categories', [])
            
            if tags:
                md_lines.append(f"**Tags:** {', '.join(tags)}")
            if categories:
                md_lines.append(f"**Categories:** {', '.join(categories)}")
            md_lines.append("")
        
        # Description
        md_lines.extend([
            "## Description",
            "",
            description if description else "*No description provided*",
            "",
        ])
        
        # Prerequisites
        if prerequisites:
            md_lines.extend([
                "## Prerequisites",
                "",
            ])
            for prereq in prerequisites:
                md_lines.append(f"- {prereq}")
            md_lines.append("")
        
        # Test Steps
        if commands:
            md_lines.extend([
                "## Test Steps",
                "",
            ])
            
            for step_data in commands:
                step_num = step_data.get('step', 0)
                step_desc = step_data.get('description', f'Step {step_num}')
                step_commands = step_data.get('commands', [])
                notes = step_data.get('notes', '')
                
                md_lines.extend([
                    f"### Step {step_num}: {step_desc}",
                    "",
                ])
                
                if notes:
                    md_lines.append(f"*Note: {notes}*")
                    md_lines.append("")
                
                md_lines.append("**Commands:**")
                md_lines.append("```bash")
                for cmd in step_commands:
                    cmd_str = cmd.strip() if isinstance(cmd, str) else str(cmd)
                    md_lines.append(cmd_str)
                md_lines.append("```")
                md_lines.append("")
        
        # Expected Result
        if expected_result:
            md_lines.extend([
                "## Expected Result",
                "",
            ])
            
            exp_desc = expected_result.get('description', '').strip()
            if exp_desc:
                md_lines.append(exp_desc)
                md_lines.append("")
            
            exp_outputs = expected_result.get('expected_outputs', [])
            if exp_outputs:
                md_lines.append("**Expected Outputs:**")
                for output in exp_outputs:
                    field = output.get('field', '')
                    value = output.get('value', '')
                    condition = output.get('condition', '')
                    
                    if value:
                        md_lines.append(f"- `{field}`: {value}")
                    elif condition:
                        md_lines.append(f"- `{field}`: {condition}")
                md_lines.append("")
            
            verify_commands = expected_result.get('verification_commands', [])
            if verify_commands:
                md_lines.append("**Verification Commands:**")
                md_lines.append("```bash")
                for verify in verify_commands:
                    cmd = verify.get('command', '')
                    desc = verify.get('description', '')
                    if desc:
                        md_lines.append(f"# {desc}")
                    md_lines.append(cmd)
                md_lines.append("```")
                md_lines.append("")
        
        # Actual Execution Results
        if actual_result or self.actual_log:
            md_lines.extend([
                "## Actual Execution Results",
                "",
            ])
            
            # Basic info from test case
            log_file = actual_result.get('log_file', '')
            exec_date = actual_result.get('execution_date', '')
            executed_by = actual_result.get('executed_by', '')
            environment = actual_result.get('environment', '')
            summary = actual_result.get('summary', {})
            
            md_lines.append("**Execution Info:**")
            if exec_date:
                md_lines.append(f"- **Date:** {exec_date}")
            if executed_by:
                md_lines.append(f"- **Executed by:** {executed_by}")
            if environment:
                md_lines.append(f"- **Environment:** {environment}")
            if log_file:
                md_lines.append(f"- **Log File:** `{log_file}`")
            md_lines.append("")
            
            if summary:
                md_lines.append("**Summary:**")
                for key, value in summary.items():
                    label = key.replace('_', ' ').title()
                    md_lines.append(f"- **{label}:** {value}")
                md_lines.append("")
            
            # Detailed execution log from external file
            if self.actual_log:
                execution_log = self.actual_log.get('execution_log', [])
                
                if execution_log:
                    md_lines.extend([
                        "### Execution Log",
                        "",
                    ])
                    
                    for log_entry in execution_log:
                        timestamp = log_entry.get('timestamp', '')
                        step = log_entry.get('step', 0)
                        step_desc = log_entry.get('description', '')
                        log_commands = log_entry.get('commands', [])
                        
                        md_lines.extend([
                            f"#### Step {step}: {step_desc}",
                            "",
                            f"*Timestamp: {timestamp}*",
                            "",
                        ])
                        
                        for i, cmd_log in enumerate(log_commands, 1):
                            command = cmd_log.get('command', '')
                            output = cmd_log.get('output', '')
                            status_code = cmd_log.get('status_code', '')
                            duration = cmd_log.get('duration_ms', '')
                            stderr = cmd_log.get('stderr', '')
                            
                            md_lines.extend([
                                f"**Command {i}:**",
                                "```bash",
                                command,
                                "```",
                                "",
                            ])
                            
                            if status_code is not None:
                                status_emoji = "✅" if status_code == 0 else "❌"
                                md_lines.append(f"**Status Code:** {status_code} {status_emoji}")
                            
                            if duration:
                                md_lines.append(f"**Duration:** {duration}ms")
                            
                            if output:
                                md_lines.extend([
                                    "",
                                    "**Output:**",
                                    "```",
                                    output.strip(),
                                    "```",
                                ])
                            
                            if stderr:
                                md_lines.extend([
                                    "",
                                    "**Error Output:**",
                                    "```",
                                    stderr.strip(),
                                    "```",
                                ])
                            
                            md_lines.append("")
                
                # Environment info from log
                env_info = self.actual_log.get('environment_info', {})
                if env_info:
                    md_lines.extend([
                        "### Environment Details",
                        "",
                    ])
                    for key, value in env_info.items():
                        label = key.replace('_', ' ').title()
                        md_lines.append(f"- **{label}:** {value}")
                    md_lines.append("")
        
        # Verification Results
        if verification:
            md_lines.extend([
                "## Verification Results",
                "",
            ])
            
            status = verification.get('status', '')
            if status:
                status_emoji = {
                    'PASS': '✅',
                    'FAIL': '❌',
                    'BLOCKED': '🚫',
                    'SKIPPED': '⏭️'
                }.get(status, '')
                md_lines.append(f"**Overall Status:** {status} {status_emoji}")
                md_lines.append("")
            
            verify_steps = verification.get('verification_steps', [])
            if verify_steps:
                md_lines.append("**Verification Steps:**")
                md_lines.append("")
                md_lines.append("| Check | Result |")
                md_lines.append("|-------|--------|")
                for step in verify_steps:
                    check = step.get('check', '')
                    result = step.get('result', '')
                    result_emoji = '✅' if result == 'PASS' else '❌'
                    md_lines.append(f"| {check} | {result} {result_emoji} |")
                md_lines.append("")
            
            comments = verification.get('comments', '').strip()
            if comments:
                md_lines.extend([
                    "**Comments:**",
                    "",
                    comments,
                    "",
                ])
            
            exec_by = verification.get('executed_by', '')
            exec_date = verification.get('execution_date', '')
            env = verification.get('environment', '')
            
            if exec_by or exec_date or env:
                md_lines.append("**Execution Details:**")
                if exec_date:
                    md_lines.append(f"- **Date:** {exec_date}")
                if exec_by:
                    md_lines.append(f"- **Executed by:** {exec_by}")
                if env:
                    md_lines.append(f"- **Environment:** {env}")
                md_lines.append("")
            
            issues = verification.get('issues', [])
            if issues and any(issue.get('issue_id') or issue.get('description') for issue in issues):
                md_lines.extend([
                    "**Issues:**",
                    "",
                ])
                for issue in issues:
                    issue_id = issue.get('issue_id', '')
                    desc = issue.get('description', '')
                    severity = issue.get('severity', '')
                    
                    if issue_id or desc:
                        issue_str = f"- **{issue_id}**" if issue_id else "- "
                        if severity:
                            issue_str += f" [{severity}]"
                        if desc:
                            issue_str += f" {desc}"
                        md_lines.append(issue_str)
                md_lines.append("")
            
            notes = verification.get('notes', '').strip()
            if notes:
                md_lines.extend([
                    "**Notes:**",
                    "",
                    notes,
                    "",
                ])
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                f.write('\n'.join(md_lines))
            
            print(f"Generated markdown: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing markdown: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python testcase_parser.py <testcase.yml> [output_dir]")
        print("Example: python testcase_parser.py X20_1.yml")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else str(Path(yaml_file).parent)
    
    # Get base name without extension
    base_name = Path(yaml_file).stem
    
    # Create parser
    parser = TestCaseParser(yaml_file)
    
    # Load test case
    if not parser.load_test_case():
        sys.exit(1)
    
    # Load actual log if available
    parser.load_actual_log()
    
    # Generate outputs
    shell_file = Path(output_dir) / f"{base_name}.sh"
    markdown_file = Path(output_dir) / f"{base_name}.md"
    
    success = True
    success = parser.generate_shell_script(str(shell_file)) and success
    success = parser.generate_markdown(str(markdown_file)) and success
    
    if success:
        print("\nGeneration completed successfully!")
        print(f"  Shell script: {shell_file}")
        print(f"  Markdown doc: {markdown_file}")
    else:
        print("\nGeneration completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
