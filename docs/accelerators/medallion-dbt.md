# Medallion DBT

Scaffolds a [dbt](https://docs.getdbt.com/) project that implements the medallion architecture (bronze → silver → gold) over the Databricks TPCH sample dataset, deployed as a Databricks job using the native `dbt_task`.

## What gets generated

```
medallion-dbt/
├── databricks.yml          # Asset Bundle root config
├── dbt_project.yml         # dbt project definition
├── profiles.yml            # Local dbt connection profile
├── .gitignore
├── models/
│   ├── sources.yml         # TPCH source declarations
│   ├── bronze/
│   │   ├── orders.sql
│   │   ├── lineitem.sql
│   │   ├── customer.sql
│   │   ├── nation.sql
│   │   └── region.sql
│   ├── silver/
│   │   └── orders_enriched.sql
│   └── gold/
│       ├── sales_summary.sql
│       └── customer_summary.sql
└── resources/
    └── jobs/
        └── dbt_job.yml
```

## Usage

```bash
dpa init medallion-dbt
cd medallion-dbt
```

Edit `databricks.yml` and fill in your workspace URLs and SQL warehouse ID:

```yaml
targets:
  dev:
    workspace:
      host: https://<your-dev-workspace>.azuredatabricks.net
  prod:
    workspace:
      host: https://<your-prod-workspace>.azuredatabricks.net

variables:
  warehouse_id:
    default: <your-warehouse-id>   # Settings → SQL Warehouses → Copy ID
  catalog:
    default: main
  schema:
    default: dbt_tpch
```

Deploy and run:

```bash
databricks bundle deploy --target dev
databricks bundle run medallion_dbt_job --target dev
```

## Model layers

| Layer | Materialisation | Output schemas |
|-------|----------------|----------------|
| Bronze | view | `{catalog}.{schema}_bronze` |
| Silver | table | `{catalog}.{schema}_silver` |
| Gold | table | `{catalog}.{schema}_gold` |

**Bronze** selects directly from `samples.tpch` source tables — no transformation, just a thin view layer that decouples downstream models from the raw source.

**Silver** (`orders_enriched`) joins orders with customer, nation, and region dimensions to produce a wide fact table with order metrics and all descriptive attributes.

**Gold** produces two aggregated tables:

- `sales_summary` — revenue, order count, and unique customers grouped by month × market segment × region
- `customer_summary` — lifetime revenue and first/last order dates per customer

## Local development

For local `dbt run` commands, set three environment variables and use `profiles.yml`:

```bash
export DATABRICKS_HOST=https://<your-workspace-url>
export DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/<warehouse-id>
export DATABRICKS_TOKEN=<your-token>

pip install dbt-databricks
dbt deps
dbt run
```
