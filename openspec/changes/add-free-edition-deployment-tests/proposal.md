## Why

The repository has a live-workspace integration suite and a GitHub Actions job, but a developer cannot discover or safely configure the required local credentials from the repository. The current deployment fixture also leaves deployed resources behind unless a non-obvious opt-in cleanup variable is set, which is unsuitable for a quota-limited Databricks Free Edition workspace.

## What Changes

- Add a tracked `.env.example` that identifies the Free Edition workspace at `https://dbc-b208d150-24a9.cloud.databricks.com/`, documents the required developer-provided credential, and explains how to create an ignored `.env` file.
- Make integration-test configuration load a local `.env` when present while preserving explicitly exported environment variables and never committing credentials.
- Refine the live deployment suite to use an isolated, clearly named test bundle deployment for each supported accelerator, validate the deployed bundle, and destroy it by default; provide an explicit keep-deployment escape hatch for debugging.
- Document local prerequisites, authentication, commands, cleanup behavior, and Free Edition quota/feature caveats in the contributor-facing test documentation.
- Keep Databricks Asset Bundles plus the Databricks CLI as the deployment-test mechanism. Do not add Databricks Connect as a required test dependency; document it as an optional developer connectivity diagnostic because it validates an interactive Spark session, not generated bundle resources, and requires serverless/version compatibility.

## Impact

- Affects `tests/integration/`, test dependencies, `.gitignore`, and integration-test documentation; the existing GitHub Actions secret-based path remains supported.
- Live integration runs will create and remove real workspace resources and therefore require the configured principal to have the necessary Free Edition/serverless permissions and available quota.
- No accelerator templates, generated solution behavior, or production deployment command changes are included.
