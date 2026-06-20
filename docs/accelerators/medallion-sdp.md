# Medallion SDP Accelerator

The **Medallion SDP** (Streaming Delta Pipeline) accelerator scaffolds a medallion-architecture pipeline using **Delta Live Tables (DLT)** — Databricks' declarative pipeline framework — deployed via a Databricks Asset Bundle.

## What is Delta Live Tables?

With regular Spark pipelines you write imperative code: open a stream, apply transforms, write to a destination, manage checkpoints, handle retries. Delta Live Tables inverts that model: you declare what each table should contain using `@dlt.table` decorators, and DLT works out execution order, incremental processing, checkpointing, and retries automatically.

The SDP pattern specifically uses DLT with streaming sources, so data flows continuously through bronze → silver → gold as new records arrive rather than in scheduled batch windows. You can also run it in triggered mode (processing all available data then stopping), which makes it safe to schedule like a batch job while still being incremental under the hood.

Data quality constraints live alongside the table definition:

```python
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")
@dlt.table
def silver_orders():
    return dlt.read_stream("bronze_orders").filter(...)
```

DLT enforces these at runtime and surfaces pass/fail counts in the pipeline UI — no extra orchestration code required.

## What gets generated

```
medallion-sdp/
├── databricks.yml                            # Asset Bundle root config
├── pyproject.toml
├── resources/
│   ├── pipelines/pipeline.yml                # DLT pipeline definition
│   └── schemas/schemas.yml                   # Unity Catalog schema declarations
└── src/
    ├── framework/
    │   ├── config.py                         # Pipeline config loader
    │   ├── dlt.py                            # DLT helpers
    │   ├── metadata.py                       # Table metadata loader
    │   └── utils.py
    └── pipelines/
        └── main/
            ├── data_sources/
            │   └── synthetic_data_source.py  # Generates synthetic streaming events
            ├── metadata/
            │   ├── bronze/tables.yml         # Bronze table specs (schema, primary keys)
            │   └── silver/tables.yml         # Silver expectations (data quality rules)
            └── transformations/
                ├── bronze/ingest_tables.py   # Auto-generated from metadata
                ├── silver/clean_tables.py    # Applies expectations, drops bad rows
                └── gold/
                    ├── dim_entity.py
                    └── fact_events.py
```

## Data flow

The pipeline ships with a synthetic data source that generates events, entities, and records, making it runnable out of the box without any external dependencies. Swap in a real source by implementing the source interface in `src/pipelines/main/data_sources/`.

**Bronze** — raw ingestion with schema enforcement. Each table spec in `metadata/bronze/tables.yml` drives a `@dlt.table` definition that ingests the stream as-is. The framework generates these table definitions from the metadata at pipeline startup.

**Silver** — cleansed and validated. Expectations from `metadata/silver/tables.yml` are applied as `@dlt.expect_or_drop` constraints. Rows that fail are dropped and counted in the DLT event log, giving you data quality metrics without any extra monitoring code.

**Gold** — business-level aggregates and dimension tables, written as static DLT tables ready for BI tools.

## Usage

```bash
dpa init medallion-sdp
cd medallion-sdp

databricks bundle deploy --target dev
```

The pipeline appears under **Delta Live Tables** in the Databricks UI. Start it manually there or configure a schedule in `pipeline.yml`.

For production:

```bash
databricks bundle deploy --target prod
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `bronze_catalog` | `dpa_bronze_dev` | Catalog for raw ingested data |
| `silver_catalog` | `dpa_silver_dev` | Catalog for cleansed and validated data |
| `gold_catalog` | `dpa_gold_dev` | Catalog for business-level aggregates |

Override at deploy time:

```bash
databricks bundle deploy \
  --var="bronze_catalog=my_bronze" \
  --var="silver_catalog=my_silver" \
  --var="gold_catalog=my_gold"
```

## Customising the pipeline

The table structure is driven by metadata files rather than hardcoded. To add tables, edit `src/pipelines/main/metadata/bronze/tables.yml` — the framework reads these specs and generates DLT table definitions at runtime. Silver expectations follow the same pattern in `metadata/silver/tables.yml`.
