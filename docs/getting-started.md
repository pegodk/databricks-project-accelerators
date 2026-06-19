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
dpa init medallion-sdp
```

This generates a complete project in `./medallion-sdp/`.

### Options

| Flag | Description |
|------|-------------|
| `--output`, `-o` | Parent directory for the generated project (default: `.`) |
| `--force` | Overwrite existing files |
| `--dry-run` | Print what would be generated without writing anything |

## Deploy

```bash
cd medallion-sdp
databricks bundle deploy --target dev
```

Or use the built-in deploy command:

```bash
dpa deploy --env dev --dir medallion-sdp
```

## List available accelerators

```bash
dpa list
```

## Environment variables

Set the following so the Databricks CLI can reach your workspace:

| Variable | Description |
|----------|-------------|
| `DATABRICKS_HOST` | Workspace URL, e.g. `https://dbc-xxx.cloud.databricks.com/` |
| `DATABRICKS_TOKEN` | Personal access token |
