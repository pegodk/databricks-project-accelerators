# CLAUDE.md — Databricks Project Accelerators

## Project identity

- **Package:** `databricks-project-accelerators`
- **CLI command:** `dpa`
- **Python import root:** `dpa`
- **Purpose:** CLI tool that scaffolds production-ready Databricks solutions (Streamlit apps, Lakeview dashboards, medallion pipelines, etc.) via Jinja2 templates + Databricks Asset Bundles.

## Repo layout

```
src/dpa/
├── cli.py                        # Typer CLI: dpa init / dpa list / dpa deploy
├── accelerators/
│   ├── __init__.py               # ACCELERATOR_REGISTRY — register new accelerators here
│   ├── base.py                   # BaseAccelerator abstract class + render helpers
│   ├── medallion_sdp/            # Example: existing accelerator
│   ├── app_streamlit/
│   └── dashboard/
├── deploy/bundle.py              # Thin wrapper around `databricks bundle deploy`
└── templates/                    # Jinja2 template trees, one directory per accelerator
    ├── medallion_sdp/
    ├── app_streamlit/
    └── dashboard/

tests/
├── unit/test_accelerator.py      # Fast, no Databricks required
└── integration/test_deploy.py    # Requires live workspace; mark with @pytest.mark.integration

docs/
└── accelerators/<name>.md        # One page per accelerator
```

## Adding a new accelerator — mandatory checklist

Every new accelerator requires ALL of the following. Do not mark a task done until every item is complete.

### 1. Template tree
Create `src/dpa/templates/<accelerator-slug>/` with at minimum:
- `databricks.yml.j2` — Asset Bundle root config with `bundle.name`, `variables`, and `include: resources/**/*.yml`
- `.gitignore` — ignore `.databricks/`, `.venv/`, `__pycache__/`, `*.pyc`, `.env`
- At least one resource YAML under `resources/`

All files that need Jinja2 rendering must have the `.j2` extension; static files are copied as-is.

### 2. Accelerator class
Create `src/dpa/accelerators/<slug>/`:
- `__init__.py` — re-export the class
- `accelerator.py` — subclass `BaseAccelerator`, set `name`, `description`, `default_config`, implement `template_root`

### 3. Registry
Add the new accelerator to `ACCELERATOR_REGISTRY` in `src/dpa/accelerators/__init__.py`:
```python
from dpa.accelerators.<slug> import <ClassName>
ACCELERATOR_REGISTRY = {
    ...
    "<accelerator-slug>": <ClassName>,
}
```

### 4. Unit tests
Add to `tests/unit/test_accelerator.py`:
- `test_get_<slug>_accelerator()` — registry lookup returns the correct class
- `test_<slug>_list_files()` — `list_files()` includes the expected output paths
- `test_<slug>_scaffold()` — scaffold to `tmp_path`, assert key files exist
- `test_<slug>_scaffold_renders_<key_content>()` — read a rendered file, assert key strings are present (project slug, variable names, injected config values)

Run `pytest tests/unit/ -v` — all tests must pass before moving on.

### 5. Integration test coverage
Add the new accelerator slug to the `ACCELERATORS` list in `tests/integration/test_deploy.py`:
```python
ACCELERATORS = ["medallion-sdp", "<new-slug>"]
```
The parametrised `test_bundle_validates` and `test_bundle_deploys` tests will pick it up automatically.

### 6. Docs page
Create `docs/accelerators/<accelerator-slug>.md` following the structure of `docs/accelerators/medallion-sdp.md`:
- What gets generated (file tree)
- Usage example (`dpa init <slug>`)
- Any required variables (warehouse ID, catalog name, etc.) and where to set them

Add the page to the `nav` in `mkdocs.yml` under the Accelerators section.

---

## Code quality — no technical debt

**Delete, don't stub.** If a file is no longer referenced or has been superseded, delete it and its directory. Never leave placeholder files with only comments or empty resource blocks (`resources: {}`). If a file has no content that matters, it has no reason to exist.

**Remove before adding.** When refactoring a feature (e.g. moving logic from a DAB resource file into a notebook), remove the old file in the same change. Do not leave both.

**Keep tests in sync.** Whenever a template file is added or removed, update the corresponding unit test assertions (`list_files`, `scaffold`, render tests) in the same commit. Stale test assertions that check for non-existent files, or missing assertions for new files, are both bugs.

**No dead config keys.** If a `default_config` key is removed from an accelerator, remove it from the template, the `databricks.yml.j2` variables block, the job `base_parameters`, and any notebook widget defaults in the same change.

**Consistent catalog defaults.** All accelerators use `dpa_bronze_dev` / `dpa_silver_dev` / `dpa_gold_dev` (or `dpa_gold_dev` for single-catalog accelerators) as default catalog values. Never use `main` as a default.

---

## Key conventions

**Template rendering**
- `.j2` files are rendered with Jinja2; available context variables: `accelerator` (slug), `project_slug`, `cfg` (the accelerator's `default_config` dict).
- Static files (no `.j2` extension) are byte-copied unchanged.
- Use `{{ cfg.some_key }}` to inject config values. Keep default_config sensible so the scaffold works out-of-the-box.

**Naming**
- Accelerator slugs use kebab-case: `app-streamlit`, `medallion-sdp`.
- Jinja2 template slugs for YAML keys use the slug with hyphens replaced by underscores: `{{ project_slug | replace('-', '_') }}`.
- Template directories use snake_case: `app_streamlit/`, `medallion_sdp/`.

**DAB structure**
- Always use `include: resources/**/*.yml` in `databricks.yml.j2` so resource files are auto-discovered.
- Variables go in `databricks.yml.j2`; resource files reference them with `${var.<name>}`.
- Provide `dev` (default, development mode) and `prod` (production mode) targets at minimum.

**CLI command**
The installed command is `dpa`. The Python module path is `dpa.`

## Running tests

```bash
# Unit tests (fast, no Databricks needed)
pytest tests/unit/ -v

# Integration tests (requires DATABRICKS_HOST + DATABRICKS_TOKEN in environment)
pytest -m integration -v --tb=short
```

## Making a release

1. Bump `version` in `pyproject.toml`.
2. Commit and push.
3. `git tag v<version> && git push --tags` — triggers the publish workflow automatically.
