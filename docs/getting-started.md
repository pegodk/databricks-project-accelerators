# Getting Started

## Installation

```bash
pip install databricks-project-accelerators
```

Or with uv:

```bash
uv pip install databricks-project-accelerators
```

## Prerequisites

- Python 3.10+
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) configured with a workspace
- A Databricks workspace with Unity Catalog enabled

## Scaffold a project

```bash
dia init medallion-sdp --industry finance --output ./projects
```

This generates a complete project under `./projects/finance-medallion-sdp/`.

### Options

| Flag | Description |
|------|-------------|
| `--industry` | Industry variant (e.g. `finance`) |
| `--output` | Parent directory for the generated project (default: `.`) |
| `--force` | Overwrite existing files |
| `--dry-run` | Print what would be generated without writing anything |

## Deploy

```bash
cd projects/finance-medallion-sdp
databricks bundle deploy --target dev
```

## List available accelerators

```bash
dia list
```

## Environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `DATABRICKS_HOST` | Workspace URL, e.g. `https://dbc-xxx.cloud.databricks.com/` |
| `DATABRICKS_TOKEN` | Personal access token |
