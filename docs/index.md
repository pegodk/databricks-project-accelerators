# Databricks Project Accelerators

![](assets/hero.png)

A CLI tool that scaffolds production-ready Databricks solutions via Jinja2 templates and Databricks Asset Bundles.

## Features

- Scaffold complete Databricks projects in seconds
- Medallion architecture (Bronze → Silver → Gold) out of the box
- Delta Live Tables pipeline templates
- Streamlit apps hosted on Databricks
- Lakeview dashboards with SQL metric views
- Databricks Asset Bundle compatible

## Quick Start

```bash
pip install databricks-project-accelerators
dpa init medallion-sdp --output ./my-project
```

See [Getting Started](getting-started.md) for a full walkthrough.
