# GitHub Actions CI/CD Workflow

This document describes the CI/CD pipeline configured in `.github/workflows/ci.yml`.

## Workflow Overview

The workflow runs on:
- **Push** to `master` or `main` branches
- **Pull requests** to `master` or `main` branches

## Jobs

### 1. Lint Job
**Runs on:** Ubuntu Latest
**Purpose:** Code quality checks and testing

**Steps:**
1. **Checkout code** - Clone the repository
2. **Setup Python 3.11** - Install Python environment
3. **Install linting tools** - Setup uv, PyYAML, and dependencies
4. **Black formatting check** - Verify code formatting consistency
5. **Import sorting check** - Verify import order with isort
6. **Flake8 linting** - Run static code analysis
7. **Run tests** - Execute test suite with unittest discover

**Success Criteria:**
- All code must pass Black formatting (120 char line length)
- Imports must be sorted correctly
- No flake8 linting violations
- All unit tests must pass

### 2. Generate GSMA Report Job
**Runs on:** Ubuntu Latest
**Depends on:** `lint` job (only runs after lint succeeds)
**Purpose:** Generate GSMA test plan rendering report

**Steps:**
1. **Checkout code** - Clone the repository
2. **Setup Python 3.11** - Install Python environment
3. **Install dependencies** - Setup uv and project dependencies
4. **Generate GSMA Test Plan Report** - Execute `testplan_renderer_gsma.py` with:
   - Container schema: `./data/dataset_4_GSMA/container/schema.json`
   - Container template: `./data/dataset_4_GSMA/container/template.j2`
   - Container data: `./data/dataset_4_GSMA/container/data.yml`
   - Test case schema: `./data/dataset_4_GSMA/test_case/schema.json`
   - Test case template: `./data/dataset_4_GSMA/test_case/template.j2`
   - Test case files: `./data/dataset_4_GSMA/test_case/*yml`
   - Output file: `report.md`

5. **Upload generated report** - Save report as artifact
   - **Name:** `gsma-test-plan-report`
   - **Path:** `report.md`
   - **Retention:** 30 days
   - **Condition:** Only if generation succeeds

6. **Create release with report** - Attach report to GitHub release
   - **Condition:** Only on tagged releases (`refs/tags/*`)
   - **File:** `report.md`
   - **Token:** Uses `GITHUB_TOKEN` secret

## Artifacts

### GSMA Test Plan Report
- **Artifact Name:** `gsma-test-plan-report`
- **File:** `report.md`
- **Availability:** 30 days after workflow run
- **Download:** Available in GitHub Actions "Artifacts" section
- **Contents:** Rendered test plan and test case documentation

## Releases

When pushing a tag (e.g., `v1.0.0`), the generated report is automatically:
1. Attached to the GitHub release
2. Available for download from the release page
3. Included in the release assets

Example:
```bash
git tag v1.0.0
git push origin v1.0.0
```

The `report.md` will then appear in the release assets.

## Usage

### Viewing Workflow Runs
1. Go to GitHub repository
2. Click "Actions" tab
3. Select "CI" workflow
4. View specific run details

### Downloading Artifacts
1. Open the completed workflow run
2. Scroll to "Artifacts" section
3. Click "gsma-test-plan-report" to download `report.md`

### Troubleshooting

**Lint Job Fails:**
- Check code formatting: `uv run black --check --diff --line-length=120 .`
- Check import ordering: `uv run isort --check-only --diff --profile black .`
- Check linting: `uv run flake8`
- Run tests: `uv run pytest . -v`

**Generate Report Job Fails:**
- Check data files exist: `./data/dataset_4_GSMA/`
- Check schema validity
- Check template syntax
- Run locally: `uv run python testplan_renderer_gsma.py --container ... --test-case ...`

**Artifact Not Found:**
- Ensure the `lint` job passed
- Check that `report.md` was created successfully
- Verify workflow execution completed

## Local Testing

To run the same checks locally:

```bash
# Install dependencies
make init

# Run full pipeline
make lint
make test

# Generate report manually
uv run python testplan_renderer.py \
  --container ./data/dataset_4_GSMA/container/schema.json \
              ./data/dataset_4_GSMA/container/template.j2 \
              ./data/dataset_4_GSMA/container/data.yml \
  --test-case ./data/dataset_4_GSMA/test_case/schema.json \
              ./data/dataset_4_GSMA/test_case/template.j2 \
              ./data/dataset_4_GSMA/test_case/*yml \
  -o report.md
```

## Files Modified

- `.github/workflows/ci.yml` - Updated CI/CD pipeline configuration
