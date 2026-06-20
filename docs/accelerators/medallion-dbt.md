# Medallion DBT Accelerator

The **Medallion DBT** accelerator scaffolds a [dbt](https://docs.getdbt.com/) project that implements the medallion architecture (bronze → silver → gold) over the Databricks TPCH sample dataset, deployed as a Databricks job using the native `dbt_task`.

## What is dbt?

dbt (data build tool) is a SQL-first transformation framework. Instead of writing ETL scripts that manage connections, table creation, and dependencies, you write plain SQL `SELECT` statements — called models — and dbt compiles them into `CREATE TABLE` or `CREATE VIEW` statements, resolves dependencies between models, and runs them in the correct order.

On Databricks, the `dbt_task` job type runs dbt natively against a SQL warehouse — no separate dbt server or additional infrastructure needed. dbt commands (`dbt deps`, `dbt run`, `dbt test`) execute directly inside the job, and results are visible in the Databricks job run UI.

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
        └── dbt_job.yml     # Job with dbt_task pointing at this project
```

## Model layers

| Layer | Materialisation | Output schemas |
|-------|----------------|----------------|
| Bronze | view | `{gold_catalog}.{bronze_schema}` |
| Silver | table | `{gold_catalog}.{silver_schema}` |
| Gold | table | `{gold_catalog}.{gold_schema}` |

**Bronze** selects directly from `samples.tpch` source tables with no transformation — a thin view layer that decouples downstream models from the raw source path. If the source table name or location changes, only `sources.yml` needs updating.

**Silver** (`orders_enriched`) joins the orders stream with customer, nation, and region dimensions to produce a wide fact table with all descriptive attributes resolved.

**Gold** produces two aggregated tables:

- `sales_summary` — revenue, order count, and unique customers grouped by month × market segment × region
- `customer_summary` — lifetime revenue and first/last order dates per customer

## Usage

```bash
dpa init medallion-dbt
cd medallion-dbt
```

Set your warehouse ID in `databricks.yml` (find it under **SQL Warehouses → your warehouse → Connection details**):

```yaml
variables:
  warehouse_id:
    default: <your-warehouse-id>
```

Deploy and run:

```bash
databricks bundle deploy --target dev
databricks bundle run medallion_dbt_job --target dev
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `warehouse_id` | _(required)_ | SQL Warehouse ID for dbt execution |
| `bronze_catalog` | `dpa_bronze_dev` | Catalog for bronze views |
| `silver_catalog` | `dpa_silver_dev` | Catalog for silver tables |
| `gold_catalog` | `dpa_gold_dev` | Catalog for gold tables |
| `bronze_schema` | `tpch_dbt` | Schema name in the bronze catalog |
| `silver_schema` | `tpch_dbt` | Schema name in the silver catalog |
| `gold_schema` | `tpch_dbt` | Schema name in the gold catalog |

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
