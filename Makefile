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
	uv run pytest . -v
	uv run python testcase_validator.py data/dataset_4_GSMA/test_case/schema.json data/dataset_4_GSMA/test_case/gsma_4.4.2.2_TC.yml
	$(eval D=./data/dataset_4_GSMA) uv run python testplan_renderer_gsma.py --container ${D}/container/schema.json ${D}/container/template.j2 ${D}/container/data.yml --test-case ${D}/test_case/schema.json ${D}/test_case/template.j2 ${D}/test_case/*yml
.PHONY: test

lint: verify-virtualenv
	@SKIP=unit-test uv run pre-commit run --all-files
.PHONY: lint

pytest-junit: verify-virtualenv
	@uv run pytest --junitxml=data_working/results.xml > /dev/null
.PHONY: pytest-junit
