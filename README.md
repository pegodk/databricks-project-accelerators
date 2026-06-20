# Databricks Project Accelerators

![](docs/assets/hero.png)

CLI tool that scaffolds production-ready Databricks solutions via Jinja2 templates and Databricks Asset Bundles.

**[Documentation](https://pegodk.github.io/databricks-project-accelerators/)**

## Installation

```bash
pip install databricks-project-accelerators
```

## Quickstart

Open an empty folder in VS Code, then run in the terminal:

```bash
# See what's available
dpa list

# Scaffold a project
dpa init medallion-spark

# Open the generated project
code medallion-spark
cd medallion-spark

# Authenticate the Databricks CLI if you haven't already
databricks configure

# Deploy to your workspace
databricks bundle deploy

# Run the job
databricks bundle run medallion_spark_medallion
```

That's it — your Databricks solution is live.

## Accelerators

| Name | Description |
|------|-------------|
| `medallion-sdp` | Streaming Delta Pipeline (DLT) with bronze/silver/gold layers and a DAB job |
| `medallion-spark` | Medallion architecture using Spark Structured Streaming notebooks |
| `python-wheel` | Python wheel package with build-and-upload job and import verification |
| `app-streamlit` | Databricks-hosted Databricks app wired to a SQL warehouse |
| `ai-bi` | Lakeview dashboard + Genie Space with metric views over the TPCH sample dataset |

## CLI reference

```bash
dpa init <accelerator>          # scaffold a project
dpa init <accelerator> --dry-run  # preview files without writing
dpa init <accelerator> --force    # overwrite existing files
dpa list                          # list all accelerators
dpa deploy --env prod             # deploy via Databricks Asset Bundle
```

## Requirements

- Python 3.10+
- [Databricks CLI v1.3.0+](https://docs.databricks.com/dev-tools/cli/install.html) configured against a Unity Catalog workspace
