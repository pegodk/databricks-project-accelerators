from pyspark import pipelines as dp
from pyspark.sql import functions as F

bronze_catalog = spark.conf.get("bronze_catalog")
bronze_schema  = spark.conf.get("bronze_schema")

TABLES = [
    "customer",
    "lineitem",
    "nation",
    "orders",
    "part",
    "partsupp",
    "region",
    "supplier",
]


def _register(table: str) -> None:
    dp.create_streaming_table(
        name=f"{bronze_catalog}.{bronze_schema}.{table}",
        comment=f"Bronze: {table} ingested from samples.tpch",
        table_properties={"delta.appendOnly": "true"},
    )

    @dp.append_flow(
        target=f"{bronze_catalog}.{bronze_schema}.{table}",
        name=f"ingest_{table}",
    )
    def _():
        return (
            spark.readStream  # type: ignore[name-defined]  # noqa: F821
            .format("delta")
            .table(f"samples.tpch.{table}")
            .withColumn("_ingested_at", F.current_timestamp())
        )


for _table in TABLES:
    _register(_table)
