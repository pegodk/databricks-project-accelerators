# Medallion SDP Accelerator

The **Medallion SDP** (Streaming Delta Pipeline) accelerator scaffolds a full medallion-architecture Databricks project with Delta Live Tables and a Databricks Asset Bundle job.

## What gets generated

```
medallion-sdp/
├── databricks.yml                          # Asset Bundle root config
├── pyproject.toml
├── resources/
│   ├── pipelines/pipeline.yml              # DLT pipeline definition
│   ├── jobs/job.yml                        # Orchestration job
│   └── schemas/schemas.yml                 # Unity Catalog schemas
└── src/
    ├── framework/
    │   ├── config.py                       # Pipeline config loader
    │   ├── dlt.py                          # DLT helpers
    │   ├── metadata.py                     # Table metadata loader
    │   └── utils.py
    └── pipelines/
        └── main/
            ├── data_sources/
            │   └── synthetic_data_source.py
            ├── metadata/
            │   ├── bronze/tables.yml       # Bronze table specs
            │   └── silver/tables.yml       # Silver expectations
            └── transformations/
                ├── bronze/ingest_tables.py
                ├── silver/clean_tables.py
                └── gold/
                    ├── dim_entity.py
                    └── fact_events.py
```

## Usage

```bash
dpa init medallion-sdp
cd medallion-sdp
databricks bundle deploy --target dev
```
