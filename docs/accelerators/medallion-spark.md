# Medallion Spark Accelerator

The **Medallion Spark** accelerator scaffolds a three-layer medallion pipeline (bronze → silver → gold) using Spark Structured Streaming notebooks deployed via a Databricks Asset Bundle job. Each layer runs as a notebook task on a shared job cluster with `trigger(availableNow=True)`, processing all new data since the last checkpoint before stopping — safe to schedule repeatedly.

## What gets generated

```
medallion-spark/
├── databricks.yml                     # Asset Bundle root config
├── .gitignore
├── notebooks/
│   ├── bronze/
│   │   └── ingest.py                  # Stream TPCH tables → bronze catalog
│   ├── silver/
│   │   └── transform.py               # Stream-static join → orders_enriched
│   └── gold/
│       └── aggregate.py               # Windowed aggregates → sales_summary, customer_summary
└── resources/
    └── jobs/
        └── medallion_job.yml          # Three-task job with shared Photon cluster
```

## Data flow

**Source:** `samples.tpch` (built-in Databricks sample data)

```
samples.tpch.orders      ─┐
samples.tpch.lineitem    ─┤─► bronze_dev.tpch.*  ─► silver_dev.tpch.orders_enriched  ─► gold_dev.tpch.sales_summary
samples.tpch.customer    ─┤                                                            └► gold_dev.tpch.customer_summary
samples.tpch.nation      ─┤
samples.tpch.region      ─┘
```

## Layers

**Bronze — raw ingestion**

Streams each TPCH source table into the bronze catalog using `readStream` with `ignoreChanges: true` and `trigger(availableNow=True)`. Checkpoints are stored at `dbfs:/checkpoints/{bronze_catalog}/{schema}/{table}`. Re-running the job is idempotent — only new rows since the last checkpoint are processed.

Tables ingested: `orders`, `lineitem`, `customer`, `nation`, `region`.

**Silver — cleansed & enriched**

Performs a stream-static join: `orders` streams from bronze while `customer`, `nation`, and `region` are batch-loaded as dimension tables. Outputs `orders_enriched` with resolved customer name, market segment, nation, and region alongside cleaned order fields.

**Gold — business aggregates**

Reads from `silver_dev.tpch.orders_enriched` and writes two tables:

| Table | Grain | Measures |
|---|---|---|
| `sales_summary` | order_month × market_segment × region | total_revenue, order_count, unique_customers, avg_order_value |
| `customer_summary` | customer_name | lifetime_revenue, order_count, avg_order_value, first/last order date |

Both use `outputMode("complete")` — the full aggregate is rewritten on each trigger.

## Requirements

- Unity Catalog enabled
- Access to `samples.tpch`
- Three catalogs pre-created: `bronze_dev`, `silver_dev`, `gold_dev` (or override via variables)
- Photon-enabled cluster (included in job config)

## Usage

```bash
dpa init medallion-spark
cd medallion-spark

databricks bundle deploy
databricks bundle run <project_slug>_medallion
```

For production:

```bash
databricks bundle deploy --target prod
databricks bundle run <project_slug>_medallion --target prod
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `bronze_catalog` | `bronze_dev` | Catalog for raw ingested data |
| `silver_catalog` | `silver_dev` | Catalog for cleansed and enriched data |
| `gold_catalog` | `gold_dev` | Catalog for business-level aggregates |
| `schema` | `tpch` | Schema name used across all three catalogs |
| `node_type_id` | `Standard_DS3_v2` | VM size (i3.xlarge for AWS, n2-highmem-4 for GCP) |

Override at deploy time:

```bash
databricks bundle deploy \
  --var="bronze_catalog=my_bronze" \
  --var="silver_catalog=my_silver" \
  --var="gold_catalog=my_gold"
```

## Checkpoints

Streaming checkpoints are written to `dbfs:/checkpoints/{catalog}/{schema}/{table}`. In production workspaces where DBFS is restricted, move checkpoints to a Unity Catalog Volume by updating the `checkpoint_base` variable in each notebook.
