# Databricks Project Accelerators

![](assets/hero.png)

A CLI tool that scaffolds production-ready Databricks solutions via Jinja2 templates and Databricks Asset Bundles.

## Quickstart

Open an empty folder in VS Code, then run in the terminal:

```bash
pip install databricks-project-accelerators

dpa list                    # browse available accelerators
dpa init medallion-spark    # scaffold a project

cd medallion-spark
databricks bundle deploy    # deploy to your workspace
databricks bundle run medallion_spark_medallion
```

## Available accelerators

| Accelerator | What you get |
|---|---|
| [`medallion-sdp`](accelerators/medallion-sdp.md) | Delta Live Tables pipeline — declarative bronze/silver/gold with data quality constraints |
| [`medallion-spark`](accelerators/medallion-spark.md) | Spark Structured Streaming notebooks — bronze ingestion, silver joins, gold aggregates |
| [`medallion-dbt`](accelerators/medallion-dbt.md) | dbt SQL models — bronze views, silver joins, gold aggregates, run via native dbt_task |
| [`mlflow-project`](accelerators/mlflow-project.md) | MLflow training pipeline — experiment tracking, model registry, batch scoring |
| [`app-streamlit`](accelerators/app-streamlit.md) | Streamlit app hosted on Databricks, wired to a SQL warehouse |
| [`ai-bi`](accelerators/ai-bi.md) | Lakeview dashboard + Genie Space with a metric view over the TPCH sample dataset |
| [`python-wheel`](accelerators/python-wheel.md) | Python package with a build-and-upload job and an import verification task |

See [Getting Started](getting-started.md) for a full walkthrough including authentication, environment targeting, and variable overrides.
