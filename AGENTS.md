1: # Agent Guide
2:
3: ## Setup & Commands
4:
5: ```bash
6: # Initial setup (requires Python 3.11+)
7: python -m venv .venv && source .venv/bin/activate
8: uv sync && uv run pre-commit install
9:
10: # Build: N/A (Python project, no build step)
11: # Lint: uv run pre-commit run --all-files
12: # Test: uv run python3 -m unittest discover -p "test_*.py" -v
13: # Dev: python testcase_parser.py <testcase.yml> [output_dir]
14: ```
15:
16: ## Tech Stack
17: - **Language**: Python 3.11+
18: - **Package Manager**: uv (with pyproject.toml)
19: - **Key Libraries**: PyYAML, jsonschema
20: - **Linting**: black, isort, flake8, pre-commit hooks
21:
22: ## Code Style
23: - Line length: 120 (pyproject.toml) / 180 (.flake8)
24: - Formatting: black + isort (profile="black")
25: - Flake8 ignores: E203, W503
26:
