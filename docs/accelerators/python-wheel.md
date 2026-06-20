# Python Wheel Accelerator

The **Python Wheel** accelerator scaffolds a self-contained Python package with a two-task Databricks job: one task builds the wheel from workspace source files and uploads it to a Unity Catalog Volume, the next installs it and verifies that all public functions import and execute correctly.

## What gets generated

```
python-wheel/
├── databricks.yml                        # Asset Bundle root config
├── pyproject.toml                        # Package metadata (hatchling build backend)
├── .gitignore
├── src/
│   └── python_wheel/
│       ├── __init__.py                   # Public API exports
│       └── functions.py                  # greet() and add() — replace with your own
├── notebooks/
│   ├── build_and_upload.py               # Builds wheel, creates schema+volume, uploads
│   └── verify_imports.py                 # Installs wheel, asserts functions work
└── resources/
    └── jobs/
        └── wheel_job.yml                 # Two-task job: build → verify
```

## How it works

Both tasks run as `notebook_task` on serverless compute. The job passes `catalog`, `schema`, and `workspace_file_path` as `base_parameters`, which notebooks read via `dbutils.widgets`.

**Task 1 — `build_and_upload`**

Receives `workspace_file_path`, `catalog`, and `schema` as widget parameters. Creates the target schema and `wheels` volume if they do not exist, then runs `pip wheel <workspace_file_path> --no-deps --wheel-dir /tmp/dist` to build the wheel from workspace files and uploads it to `/Volumes/{catalog}/{schema}/wheels/` using `dbutils.fs.cp`.

**Task 2 — `verify_imports`** (depends on task 1)

Finds the wheel in the UC Volume by glob, installs it with `pip install --force-reinstall`, restarts the Python interpreter, then imports and asserts the public API in a separate cell:

```python
from python_wheel import greet, add

assert greet("Databricks") == "Hello, Databricks!"
assert add(2, 3) == 5.0
```

## Requirements

- Unity Catalog enabled
- The catalog specified in `${var.catalog}` must exist before deploying

## Usage

```bash
dpa init python-wheel
cd python-wheel

databricks bundle deploy
databricks bundle run python_wheel_wheel
```

Replace the functions in `src/python_wheel/functions.py` with your own logic. Bump `version` in `pyproject.toml` when you release a new build — the job picks up the latest wheel matching `python_wheel-*.whl` in the volume.

## Variables

| Variable | Default | Description |
|---|---|---|
| `catalog` | `dpa_gold_dev` | Unity Catalog catalog for the wheel volume |
| `schema` | `python_wheel` | Schema for the wheel volume |

## Extending the package

Add new modules under `src/python_wheel/` and export them from `__init__.py`. Add assertions to `notebooks/verify_imports.py` for each new function. The wheel is rebuilt from source on every job run, so no separate publish step is needed during development.
