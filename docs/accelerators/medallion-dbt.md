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
│   │   ├── region.sql
│   │   ├── part.sql
│   │   ├── supplier.sql
│   │   └── partsupp.sql
│   ├── silver/
│   │   └── orders_enriched.sql
│   └── gold/
│       ├── dim_customer.sql
│       ├── dim_part.sql
│       ├── dim_supplier.sql
│       └── fact_order.sql
└── resources/
    └── jobs/
        └── dbt_job.yml     # Job with dbt_task pointing at this project
```

## Model layers

| Layer | Materialisation | Location |
|-------|----------------|----------|
| Bronze | view | `dpa_dbt_bronze_dev.{schema}` |
| Silver | table | `dpa_dbt_silver_dev.{schema}` |
| Gold | table | `dpa_dbt_gold_dev.{schema}` |

**Bronze** selects directly from `samples.tpch` source tables with no transformation — a thin view layer that decouples downstream models from the raw source path. If the source table name or location changes, only `sources.yml` needs updating.

**Silver** (`orders_enriched`) joins orders with customer, nation, and region to resolve descriptive attributes (customer segment, nation, region) onto every order row, so downstream gold models never need to repeat that join.

**Gold** implements a small star schema:

- `dim_customer`, `dim_part`, `dim_supplier` — descriptive dimension tables built directly from bronze reference data
- `fact_order` — one row per order line, built from `lineitem` joined against `orders_enriched` (for order/customer attributes) and `partsupp` (for supply cost), with commit/receipt/ship lag calculated in days

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
| `bronze_catalog` | `dpa_dbt_bronze_dev` | Catalog for bronze views |
| `silver_catalog` | `dpa_dbt_silver_dev` | Catalog for silver tables |
| `gold_catalog` | `dpa_dbt_gold_dev` | Catalog for gold tables |
| `schema` | `tpch_dbt` | Schema name used across all three catalogs (DAB prefixes with initials in dev mode) |

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
