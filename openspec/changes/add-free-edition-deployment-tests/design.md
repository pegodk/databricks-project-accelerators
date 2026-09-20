## Context

`tests/integration/conftest.py` already scaffolds each registered accelerator into a temporary directory, substitutes the workspace host in its generated bundle, and invokes `databricks bundle deploy`. `test_deploy.py` validates before and after deployment, and `.github/workflows/integration.yml` supplies `DATABRICKS_HOST` and `DATABRICKS_TOKEN` from GitHub environment secrets. Locally, however, there is no checked-in credential setup guide or `.env` loading. Cleanup is opt-in through `DPA_DESTROY_DEPLOYED`, which can accumulate resources in the configured workspace.

The supplied workspace is Databricks Free Edition. Free Edition is serverless-only and quota-limited, so the integration suite must be explicit about resource creation and must clean up reliably. Some accelerator resource types can be unavailable in a Free Edition workspace; a deployment result must distinguish an unsupported platform capability from an authentication or test-harness failure.

## Goals / Non-Goals

**Goals:**

- Make local live integration runs discoverable and safe using a developer-created, ignored `.env` file.
- Deploy the generated bundles to the supplied workspace (or a deliberately overridden workspace) through the Databricks CLI, validate them, and clean them up by default.
- Preserve CI secret injection and allow a developer to retain a failed deployment deliberately for diagnosis.
- Surface Free Edition prerequisites, feature limitations, quotas, and supported/unsupported accelerator outcomes clearly.

**Non-Goals:**

- Running each workload's data pipeline, job, dashboard, or app end-to-end.
- Altering accelerator templates just to make unsupported Free Edition services available.
- Making Databricks Connect a mandatory dependency or treating a Spark session check as bundle deployment coverage.
- Storing a personal access token, OAuth refresh token, or other secret in the repository.

## Decisions

### 1. Use dotenv-backed environment configuration with shell/CI precedence

Add a root `.env.example` containing the supplied host and blank credential placeholders, plus concise instructions to copy it to `.env`. Add a lightweight dotenv dependency to the development/test environment and load `.env` without overriding values already exported by the shell or injected by GitHub Actions. Continue to require `DATABRICKS_HOST` and `DATABRICKS_TOKEN` for this suite, so missing or blank values skip live tests with an actionable message.

The host in `.env.example` is a convenient default for this repository owner, not an assertion that prevents other contributors or CI from selecting their own isolated workspace.

**Alternatives considered:**
- Require manual `export` commands only: rejected because it leaves no discoverable local setup and is easy to misconfigure.
- Commit a working `.env`: rejected because it would expose credentials.
- Switch immediately to profile-only OAuth: rejected for this change because the existing CI contract is environment-based; profile support can be added later without breaking secrets-based CI.

### 2. Exercise deployment through Databricks Asset Bundles and the CLI

Keep the existing scaffold → patch test host → `bundle validate` → `bundle deploy` → post-deploy `bundle validate` flow, while making the deploy fixture the single lifecycle owner. It will produce a clearly test-prefixed bundle name, emit useful command output on failures, and always attempt `bundle destroy` in fixture teardown unless `DPA_KEEP_DEPLOYED=1` is explicitly set. Cleanup failures must be reported without hiding the original test failure.

Resource variable overrides and bundle naming will remain deterministic per accelerator and run, avoiding accidental collisions with developer projects and making orphaned resources identifiable. The implementation will serialize these live tests unless and until all resource names and workspace limits are proven safe for parallel execution.

**Alternatives considered:**
- Keep the current opt-in `DPA_DESTROY_DEPLOYED`: rejected because it leaks resources by default in a constrained shared workspace.
- Test only `bundle validate`: rejected because validation does not prove deployment permissions or resource compatibility.
- Use direct REST API calls: rejected because they bypass the generated Asset Bundle contract that the project promises users.

### 3. Treat Free Edition compatibility as explicit test configuration and reporting

Maintain an integration target list or capability matrix that identifies which registered accelerators are expected to deploy in the configured Free Edition workspace. The suite will run supported accelerators and mark intentionally unsupported Free Edition resource types with a documented, explicit reason rather than silently passing or failing them. Unexpected deployment failures remain failures.

The documentation will state that the user must authenticate with a principal that can use serverless and create the accelerator resources, and that Free Edition quota exhaustion can temporarily make the suite unavailable.

**Alternatives considered:**
- Require every registry member to deploy on every Free Edition workspace: rejected because Free Edition restricts available services and an unsupported product resource is not a regression in the test harness.
- Skip all failures on Free Edition: rejected because it would conceal invalid bundles, expired credentials, and permission regressions.

### 4. Keep Databricks Connect optional and diagnostic-only

Databricks Connect can test an authenticated interactive Spark connection to serverless, but it needs a compatible package/Python/serverless version and does not deploy or inspect Asset Bundle resources. Document a manual `databricks-connect test` option for developers who need to isolate connectivity issues. Do not add it to the default integration command or test dependency set.

**Alternatives considered:**
- Replace bundle deployment with Databricks Connect: rejected because it tests a different contract.
- Add a mandatory Connect smoke test: rejected because its versioned serverless prerequisites make the deployment suite less portable without increasing deployment coverage.

## Risks / Trade-offs

- Destructive cleanup can leave resources behind if the process is interrupted or the destroy command fails; the test prefix, logged project directory, and opt-in retention flag make manual recovery possible.
- A Free Edition workspace can exhaust its fair-use quota or lack a product feature. The documented compatibility matrix avoids masking these as generic success, but needs maintenance when accelerators or Databricks availability change.
- A personal token in `.env` remains sensitive on the developer machine; `.env` stays ignored and documentation will direct developers never to commit it.
