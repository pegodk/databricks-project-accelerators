# Getting Started

This guide walks you from an empty folder to a running Databricks project in under five minutes.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.10+** — check with `python --version`
- **Databricks CLI v1.3.0+** — [installation guide](https://docs.databricks.com/dev-tools/cli/install.html), check with `databricks --version`
- A **Databricks workspace** with Unity Catalog enabled

## 1. Install

```bash
pip install databricks-project-accelerators
```

Verify the CLI is available:

```bash
dpa --help
```

## 2. Authenticate the Databricks CLI

If you haven't already, configure the CLI against your workspace:

```bash
databricks configure
```

You'll be prompted for:

- **Host** — your workspace URL, e.g. `https://adb-1234567890.azuredatabricks.net`
- **Token** — a personal access token (Settings → Developer → Access tokens in the Databricks UI)

Test the connection:

```bash
databricks workspace list /
```

## 3. Browse available accelerators

```bash
dpa list
```

```
┌────────────────┬──────────────────────────────────────────────────────────┐
│ Name           │ Description                                              │
├────────────────┼──────────────────────────────────────────────────────────┤
│ medallion-sdp  │ Streaming Delta Pipeline with bronze/silver/gold layers  │
│ medallion-spark│ Medallion architecture using Spark Structured Streaming  │
│ app-streamlit  │ Databricks-hosted Streamlit app wired to a SQL warehouse │
│ python-wheel   │ Python wheel package with build-and-upload job           │
│ ai-bi          │ Lakeview dashboard + Genie Space with metric views       │
└────────────────┴──────────────────────────────────────────────────────────┘
```

## 4. Scaffold a project

Open an empty folder in VS Code, then run in its terminal:

```bash
dpa init medallion-spark
```

This generates a complete project in `./medallion-spark/`:

```
medallion-spark/
├── databricks.yml
├── notebooks/
│   ├── bronze/ingest.py
│   ├── silver/transform.py
│   └── gold/aggregate.py
└── resources/
    └── jobs/medallion_job.yml
```

Open the generated folder:

```bash
code medallion-spark
```

## 5. Review the bundle config

Open `databricks.yml`. Key variables are pre-filled with sensible defaults:

```yaml
variables:
  bronze_catalog:
    default: bronze_dev
  silver_catalog:
    default: silver_dev
  gold_catalog:
    default: gold_dev
```

Change any defaults before deploying, or override them at deploy time with `--var`.

## 6. Deploy

```bash
cd medallion-spark
databricks bundle deploy
```

This uploads notebooks and resources to your workspace under the `dev` target (the default). You can also use the built-in command:

```bash
dpa deploy          # deploys to dev by default
dpa deploy --env prod
```

Confirm the deploy succeeded:

```bash
databricks bundle validate
```

## 7. Run the job

```bash
databricks bundle run medallion_spark_medallion
```

Monitor progress in the Databricks UI under **Workflows → Jobs**.

## Targeting environments

Each accelerator ships with `dev` and `prod` targets. Switch with `--target`:

```bash
databricks bundle deploy --target prod
databricks bundle run medallion_spark_medallion --target prod
```

Override variables at deploy time without editing any files:

```bash
databricks bundle deploy \
  --var="bronze_catalog=my_bronze" \
  --var="silver_catalog=my_silver" \
  --var="gold_catalog=my_gold"
```

## Preview before scaffolding

Use `--dry-run` to see what files would be created without writing anything:

```bash
dpa init ai-bi --dry-run
```

## Force overwrite

If a project directory already exists:

```bash
dpa init medallion-spark --force
```

## Output to a specific directory

```bash
dpa init ai-bi --output ~/projects
# generates ~/projects/ai-bi/
```
