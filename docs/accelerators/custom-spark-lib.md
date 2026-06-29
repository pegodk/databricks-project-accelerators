# Custom Spark Lib Accelerator

The **Custom Spark Lib** accelerator scaffolds a medallion pipeline (bronze → gold) using **Spark Structured Streaming** notebooks, with transformation logic packaged as a reusable Python wheel and deployed automatically via DAB `artifacts`. This demonstrates the pattern of extracting shared PySpark logic into a proper library that is built and distributed as part of the bundle deploy.

## What gets generated

```
custom-spark-lib/
├── databricks.yml                     # Asset Bundle root config (includes artifacts)
├── pyproject.toml                     # Wheel build config for the spark_transforms library
├── .gitignore
├── src/
│   └── spark_transforms/
│       ├── __init__.py
│       └── medallion.py               # Reusable PySpark transformation functions
├── notebooks/
│   ├── bronze/
│   │   └── ingest.py                  # Stream TPCH tables → bronze catalog
│   └── gold/
│       └── aggregate.py               # Import spark_transforms, write dim/fact tables
└── resources/
    └── jobs/
        └── medallion_job.yml          # Two-task job; each task installs the wheel
```

## How the wheel deploy works

The `databricks.yml` includes an `artifacts` section that builds the wheel before deploy:

```yaml
artifacts:
  default:
    type: whl
    path: .
    build: "pip install build && python -m build --wheel --outdir dist/ ."
```

Running `databricks bundle deploy` will:

1. Build the wheel from `pyproject.toml` into `dist/`
2. Upload the `.whl` to the workspace alongside the notebooks
3. Deploy the job resource

Each notebook task installs the wheel via:

```yaml
libraries:
  - whl: /Workspace${workspace.file_path}/dist/*.whl
```

## The spark_transforms library

`src/spark_transforms/medallion.py` exports four functions:

| Function | Input | Output |
|---|---|---|
| `build_dim_customer(customer, nation, region)` | Raw TPCH DataFrames | `dim_customer` with nation/region hierarchy |
| `build_dim_part(part)` | Raw TPCH part DataFrame | `dim_part` |
| `build_dim_supplier(supplier, nation, region)` | Raw TPCH DataFrames | `dim_supplier` with nation/region hierarchy |
| `build_fact_order(lineitem, orders, partsupp)` | Raw TPCH DataFrames | `fact_order` with calendar lag columns |

The gold notebook imports these functions and writes the resulting DataFrames to Unity Catalog tables using `saveAsTable`.

## Data flow

**Source:** `samples.tpch` (built-in Databricks sample data — no setup needed)

```
samples.tpch.*  →  dpa_bronze_dev.tpch_spark.*  →  dpa_gold_dev.tpch_model_spark.{dim_customer, dim_part, dim_supplier, fact_order}
```

## Requirements

- Unity Catalog enabled
- Access to `samples.tpch`
- Two catalogs pre-created: `dpa_bronze_dev`, `dpa_gold_dev` (or override via variables)

## Usage

```bash
dpa init custom-spark-lib
cd custom-spark-lib

databricks bundle deploy
databricks bundle run custom_spark_lib_medallion
```

For production:

```bash
databricks bundle deploy --target prod
databricks bundle run custom_spark_lib_medallion --target prod
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `bronze_catalog` | `dpa_bronze_dev` | Catalog for raw ingested data |
| `gold_catalog` | `dpa_gold_dev` | Catalog for dimensional model tables |
| `bronze_schema` | `tpch_spark` | Schema name in the bronze catalog |
| `gold_schema` | `tpch_model_spark` | Schema name in the gold catalog |

Override at deploy time:

```bash
databricks bundle deploy \
  --var="bronze_catalog=my_bronze" \
  --var="gold_catalog=my_gold"
```

## Extending the library

Add new transformation modules under `src/spark_transforms/`, import them in the relevant notebook, and redeploy. The wheel is rebuilt automatically on every `databricks bundle deploy`.
