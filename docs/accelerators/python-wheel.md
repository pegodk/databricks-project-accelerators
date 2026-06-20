# Python Wheel Accelerator

The **Python Wheel** accelerator scaffolds a self-contained Python package with a two-task Databricks job: one task builds the wheel from workspace files and uploads it to a Unity Catalog Volume, the next installs it and verifies that all public functions import and execute correctly.

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
│   ├── build_and_upload.py               # Builds wheel, uploads to UC Volume
│   └── verify_imports.py                 # Installs wheel, asserts functions work
└── resources/
    ├── jobs/
    │   └── wheel_job.yml                 # Two-task job: build → verify
    └── volumes/
        └── wheels_volume.yml             # UC schema + volume for wheel storage
```

## How it works

Both tasks run as `spark_python_task`, which executes `.py` files directly on serverless compute — no notebook object required, no cluster startup overhead.

**Task 1 — `build_and_upload`**

Receives the workspace file path, catalog, and schema as command-line arguments (`sys.argv`). Runs `pip wheel <workspace_file_path> --no-deps --wheel-dir /tmp/dist` to build the wheel directly from the workspace files, then uploads it to `/Volumes/{catalog}/{schema}/wheels/` using `dbutils.fs.cp`.

**Task 2 — `verify_imports`** (depends on task 1)

Finds the wheel in the UC Volume by glob, installs it with `pip install --force-reinstall`, and runs assertions against the public API:

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

databricks bundle deploy   # creates the schema + volume
databricks bundle run python_wheel_wheel
```

Replace the functions in `src/python_wheel/functions.py` with your own logic. Bump `version` in `pyproject.toml` when you release a new build — the job picks up the latest wheel matching `python_wheel-*.whl` in the volume.

## Variables

| Variable | Default | Description |
|---|---|---|
| `catalog` | `main` | Unity Catalog catalog for the wheel volume |
| `schema` | `python_wheel` | Schema for the wheel volume |

## Extending the package

Add new modules under `src/python_wheel/` and export them from `__init__.py`. Add assertions to `notebooks/verify_imports.py` for each new function. The wheel is rebuilt from source on every job run, so no separate publish step is needed during development.
