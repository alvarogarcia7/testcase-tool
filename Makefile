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
	uv run python testcase_validator.py data/dataset_4_GSMA/json_schema.json data/dataset_4_GSMA/gsma_4.4.2.2_TC.yml
	uv run python testplan_renderer_gsma.py --container data/dataset_4_GSMA/json_schema.json template_gsma.j2 data/dataset_4_GSMA/gsma_4.4.2.2_TC.yml --test-case data/dataset_4_GSMA/json_schema.json data/dataset_4_GSMA/gsma_4.4.2.2_TC.yml data/dataset_4_GSMA/gsma_4.4.2.2_TC.yml
.PHONY: test

lint: verify-virtualenv
	@SKIP=unit-test uv run pre-commit run --all-files
.PHONY: lint

pytest-junit: verify-virtualenv
	@uv run pytest --junitxml=data_working/results.xml > /dev/null
.PHONY: pytest-junit
