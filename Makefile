init: install-dependencies install-hooks

install-dependencies: verify-virtualenv
	uv sync
.PHONY: install-dependencies

install-hooks: verify-virtualenv
	uv run pre-commit install
.PHONY: install-hooks

verify-virtualenv:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "Error: This command must be run inside a Python virtual environment."; \
		echo "source .venv/bin/activate"; \
		exit 1; \
	fi

test: verify-virtualenv
	uv run python3 -m unittest discover -p "test_*.py" -v
.PHONY: test

lint: verify-virtualenv
	@SKIP=unit-test uv run pre-commit run --all-files
.PHONY: lint
