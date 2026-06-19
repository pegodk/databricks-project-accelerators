# Databricks Project Accelerators

A CLI tool that scaffolds production-ready Databricks solutions for industry use cases. It generates Delta Live Tables pipelines, Databricks Asset Bundles, and industry-specific transformations with a single command.

## Features

- Scaffold complete Databricks projects in seconds
- Industry-specific configurations (finance, and more to come)
- Medallion architecture (Bronze → Silver → Gold) out of the box
- Delta Live Tables pipeline templates
- Databricks Asset Bundle compatible

## Quick Start

```bash
pip install databricks-project-accelerators
dia scaffold medallion-sdp --industry finance --output ./my-project
```

See [Getting Started](getting-started.md) for a full walkthrough.
