# Live integration tests

The integration suite scaffolds a generated Asset Bundle, validates it, deploys it
to a real Databricks workspace, validates it again, and destroys it. It does not
run the generated workload itself.

## Prerequisites

Install the [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
and install this project with its development dependencies:

```bash
pip install -e ".[dev]"
```

Copy the repository example configuration and set a token belonging to a user who
can use serverless compute and create the relevant workspace and Unity Catalog
resources:

```bash
cp .env.example .env
# Edit .env and set DATABRICKS_TOKEN.
pytest -m integration -v --tb=short
```

`.env` is ignored by Git. It supplies the Free Edition workspace host by default,
but exported shell variables and CI secrets take precedence, so another isolated
workspace can be used without editing the example. Do not commit a token.

The test suite is intentionally serial. Each deployment is named
`dpa-test-<accelerator>-<run-id>`, making test resources easy to identify.

## Cleanup and recovery

The fixture runs `databricks bundle destroy` during teardown, including when an
assertion fails. Set `DPA_KEEP_DEPLOYED=1` only when debugging a deployment; the
warning includes the scaffold directory required for manual cleanup. If a run is
interrupted or destroy fails, return to that directory and run:

```bash
databricks bundle destroy --target dev --auto-approve
```

Use the `dpa-test-` prefix to locate any remaining resources. Cleanup failures
are emitted as warnings so they do not conceal the original deployment failure.

## Free Edition compatibility

Free Edition is serverless-only and quota-limited. Authentication, permissions,
and available quota are preconditions for a meaningful deployment run; quota
exhaustion is not treated as a passing test result. The compatibility matrix in
`tests/integration/test_deploy.py` is deliberately explicit: supported
accelerators run, while exclusions must name the unavailable platform capability.

The matrix below was exercised against the supplied Free Edition workspace on
2026-09-20. No accelerator is enabled until it completes a full bundle deployment.

| Accelerator | Status | Observed reason |
| --- | --- | --- |
| AI/BI | Excluded | The Free Edition metastore's Default Storage cannot create a Unity Catalog catalog through this bundle; its Genie sample-question IDs are also invalid. |
| Custom Python Wheel | Excluded | The bundle cannot create its Unity Catalog catalog with the Free Edition metastore's Default Storage configuration. |
| Lakebase Streamlit App | Excluded | The workspace had reached the Free Edition limit of three apps, and the static Lakebase PostgreSQL project ID already existed. |
| Medallion DBT | Excluded | The bundle cannot create its Unity Catalog catalogs with the Free Edition metastore's Default Storage configuration. |
| Medallion SDP | Excluded | The bundle cannot create its Unity Catalog catalogs with the Free Edition metastore's Default Storage configuration. |
| MLflow Project | Excluded | The bundle cannot create its Unity Catalog catalog with the Free Edition metastore's Default Storage configuration. |

The fixture completed `bundle destroy` without cleanup warnings after every
authenticated run. Once an accelerator is made compatible, move it into
`FREE_EDITION_SUPPORTED_ACCELERATORS`; its deployment failures will then remain
test failures rather than being converted to a skip.

## Optional connectivity diagnostic

`databricks-connect test` is optional troubleshooting only. It can help isolate
an authenticated interactive Spark/serverless connection, but requires a
Databricks Connect version compatible with the selected Python version and
serverless environment. It does not validate or deploy generated Asset Bundles,
so it is not a test dependency and is not part of the integration command above.
