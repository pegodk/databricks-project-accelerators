# Medallion Spark Accelerator

The **Medallion Spark** accelerator scaffolds a three-layer medallion pipeline (bronze → silver → gold) using **Spark Structured Streaming** notebooks deployed as a Databricks job. Each layer runs as a notebook task with `trigger(availableNow=True)`, which processes all new data since the last checkpoint and then stops — making it safe to schedule repeatedly like a batch job while only touching incremental data.

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

**Source:** `samples.tpch` (built-in Databricks sample data — no setup needed)

```
samples.tpch.orders      ─┐
samples.tpch.lineitem    ─┤─► dpa_bronze_dev.tpch.*  ─► dpa_silver_dev.tpch.orders_enriched  ─► dpa_gold_dev.tpch.sales_summary
samples.tpch.customer    ─┤                                                                    └► dpa_gold_dev.tpch.customer_summary
samples.tpch.nation      ─┤
samples.tpch.region      ─┘
```

## Layers

**Bronze — raw ingestion**

Streams each TPCH source table into the bronze catalog using `readStream` with `ignoreChanges: true` and `trigger(availableNow=True)`. Checkpoints are stored at `dbfs:/checkpoints/{bronze_catalog}/{schema}/{table}`. Re-running the job is safe — only new rows since the last checkpoint are processed.

Tables ingested: `orders`, `lineitem`, `customer`, `nation`, `region`.

**Silver — cleansed & enriched**

Performs a stream-static join: `orders` streams from bronze while `customer`, `nation`, and `region` are loaded as batch dimension tables. Outputs `orders_enriched` with resolved customer name, market segment, nation, and region alongside cleaned order fields.

**Gold — business aggregates**

Reads from `dpa_silver_dev.tpch.orders_enriched` and writes two tables:

| Table | Grain | Measures |
|---|---|---|
| `sales_summary` | order_month × market_segment × region | total_revenue, order_count, unique_customers, avg_order_value |
| `customer_summary` | customer_name | lifetime_revenue, order_count, avg_order_value, first/last order date |

Both use `outputMode("complete")` — the full aggregate is rewritten on each trigger.

## Requirements

- Unity Catalog enabled
- Access to `samples.tpch`
- Three catalogs pre-created: `dpa_bronze_dev`, `dpa_silver_dev`, `dpa_gold_dev` (or override via variables)
- Photon-enabled cluster (included in the job config)

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
| `bronze_catalog` | `dpa_bronze_dev` | Catalog for raw ingested data |
| `silver_catalog` | `dpa_silver_dev` | Catalog for cleansed and enriched data |
| `gold_catalog` | `dpa_gold_dev` | Catalog for business-level aggregates |
| `bronze_schema` | `tpch_spark` | Schema name in the bronze catalog |
| `silver_schema` | `tpch_spark` | Schema name in the silver catalog |
| `gold_schema` | `tpch_spark` | Schema name in the gold catalog |
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
