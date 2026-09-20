# Live integration tests

The integration suite scaffolds each generated Asset Bundle under
`tests/integration/bundles/`, validates it, deploys it to a real Databricks
workspace, validates it again, runs each generated job or pipeline, and destroys
it. The bundle directory is ignored by Git and remains available for inspection
after the run.

## Prerequisites

Install the [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
and install this project with its development dependencies:

```bash
pip install -e ".[dev]"
```

Log in with the Databricks CLI using a user who can use serverless compute and
create the relevant workspace and Unity Catalog resources. Then copy the local
configuration:

```bash
databricks auth login --profile dpa-free-edition --host https://dbc-b208d150-24a9.cloud.databricks.com/
cp .env.example .env
pytest -m integration -v --tb=short
```

`.env` is ignored by Git. `DATABRICKS_CONFIG_PROFILE` is the Databricks CLI's
standard profile selector; it is a local profile name, not a token. The test
fixture reads the authenticated profile's host and invokes every bundle command
with `--profile`, so it never reads `DATABRICKS_TOKEN`.

GitHub-hosted runners cannot complete interactive OAuth. The integration workflow
therefore skips until a non-interactive CLI OAuth/OIDC profile is provisioned for
that runner.

The test suite is intentionally serial. Each deployment is named
`dpa-test-<accelerator>-<run-id>`, making test resources easy to identify.

## Cleanup and recovery

The fixture runs `databricks bundle destroy` during teardown, including when an
assertion or workload run fails. Set `DPA_KEEP_DEPLOYED=1` only when debugging a
deployment; the warning includes the scaffold directory required for manual
cleanup. If a run is interrupted or destroy fails, return to that directory and
run:

```bash
databricks bundle destroy --target dev --auto-approve
```

Use the `dpa-test-` prefix to locate any remaining resources. Cleanup failures
are emitted as warnings so they do not conceal the original deployment failure.

## Full accelerator coverage

The integration matrix is derived from `ACCELERATOR_REGISTRY`, so every
registered accelerator is deployed. Use a workspace that can create Unity
Catalog catalogs, run jobs and pipelines, create Databricks Apps and Lakebase
resources, and provision AI/BI resources. Free Edition workspaces may not have
the required quotas or capabilities; any resulting deployment failure is a test
failure and must be resolved rather than excluded from the suite.

## Optional connectivity diagnostic

`databricks-connect test` is optional troubleshooting only. It can help isolate
an authenticated interactive Spark/serverless connection, but requires a
Databricks Connect version compatible with the selected Python version and
serverless environment. It does not validate or deploy generated Asset Bundles,
so it is not a test dependency and is not part of the integration command above.
