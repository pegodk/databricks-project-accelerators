from pyspark import pipelines as dp
from pyspark.sql import functions as F

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect("positive_supplier_balance", "s_acctbal >= 0")
@dp.expect_or_fail("valid_supplier_name", "s_name IS NOT NULL")
@dp.temporary_view()
def v_supplier():
    return (
        spark.readStream  # type: ignore[name-defined]  # noqa: F821
        .format("delta")
        .table(f"{bronze_catalog}.{bronze_schema}.supplier")
        .withColumn("_seq", F.col("_metadata.file_modification_time"))
    )


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.supplier",
    cluster_by=["s_nationkey"],
    comment="Silver: supplier",
)

dp.create_auto_cdc_flow(
    target=f"{silver_catalog}.{silver_schema}.supplier",
    source="v_supplier",
    keys=["s_suppkey"],
    sequence_by="_seq",
    stored_as_scd_type=1,
)
