from pyspark import pipelines as dp

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
    @dp.table(
        name=f"{bronze_catalog}.{bronze_schema}.{table}",
        comment=f"Bronze: {table} ingested from samples.tpch",
        table_properties={"delta.appendOnly": "true"},
    )
    def _():
        return (
            spark.readStream  # type: ignore[name-defined]  # noqa: F821
            .format("delta")
            .table(f"samples.tpch.{table}")
        )


for _table in TABLES:
    _register(_table)
