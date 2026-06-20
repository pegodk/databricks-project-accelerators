# MLflow Project Accelerator

The **MLflow Project** accelerator scaffolds a complete MLflow training pipeline: feature engineering over the TPCH sample dataset, model training with experiment tracking, registration to the Unity Catalog Model Registry, and batch scoring — all wired into a three-task Databricks job.

## What gets generated

```
mlflow-project/
├── databricks.yml                     # Asset Bundle root config
├── .gitignore
├── notebooks/
│   ├── train.py                       # Feature engineering + RandomForestRegressor training
│   ├── register.py                    # Promote best run to UC Model Registry
│   └── score.py                       # Batch inference with champion model
└── resources/
    ├── jobs/
    │   └── mlflow_job.yml             # Three-task job on Databricks ML Runtime
    └── schemas/
        └── schema.yml                 # UC schema for the registered model
```

## Pipeline

```
samples.tpch  →  train.py  →  MLflow experiment
                                     │
                              register.py  →  catalog.schema.tpch_order_value@champion
                                                        │
                                               score.py  →  predictions DataFrame
```

**Task 1 — `train`**

Loads `orders`, `customer`, and `nation` from `samples.tpch`, joins them, and trains a `RandomForestRegressor` to predict `o_totalprice`. Logs parameters, RMSE / MAE / R² metrics, and the model artifact to the configured MLflow experiment.

**Task 2 — `register`** (depends on train)

Queries the experiment for the run with the lowest RMSE, registers it to the Unity Catalog Model Registry as `${var.catalog}.${var.schema}.${var.model_name}`, and sets the `champion` alias on the new version.

**Task 3 — `score`** (depends on register)

Loads `models:/${var.catalog}.${var.schema}.${var.model_name}@champion` via `mlflow.pyfunc.load_model` and scores 1 000 orders, displaying predictions alongside order metadata.

## Requirements

- Unity Catalog enabled
- `${var.catalog}` must exist before deploying (the schema is created by the bundle)
- Access to `samples.tpch`

## Usage

```bash
dpa init mlflow-project
cd mlflow-project

databricks bundle deploy                    # creates the schema
databricks bundle run mlflow_project_pipeline
```

Monitor the experiment in the Databricks UI under **Experiments → /Shared/tpch-order-value**.

For production:

```bash
databricks bundle deploy --target prod
databricks bundle run mlflow_project_pipeline --target prod
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `catalog` | `main` | Unity Catalog catalog for the model registry |
| `schema` | `mlflow_demo` | Schema for the registered model |
| `experiment_name` | `/Shared/tpch-order-value` | Workspace path for the MLflow experiment |
| `model_name` | `tpch_order_value` | Registered model name within the schema |
| `node_type_id` | `Standard_DS3_v2` | VM size (i3.xlarge for AWS, n2-highmem-4 for GCP) |

## Cluster runtime

The job uses **Databricks ML Runtime 15.4 LTS** (`15.4.x-cpu-ml-scala2.12`), which ships with scikit-learn, MLflow, and all standard ML libraries pre-installed — no `%pip install` required in the notebooks.

## Extending the model

To experiment with different algorithms or hyperparameters, edit `notebooks/train.py`. Each run is tracked in the MLflow experiment; `register.py` always promotes the run with the lowest RMSE, so you can run `train` multiple times before running `register`.

To add hyperparameter tuning, wrap the training loop in multiple `mlflow.start_run()` contexts with different parameter combinations — the registration task will pick the best one automatically.
