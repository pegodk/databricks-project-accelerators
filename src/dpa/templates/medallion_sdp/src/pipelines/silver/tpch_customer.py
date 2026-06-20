from pyspark import pipelines as dp
from pyspark.sql import functions as F

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect("valid_phone_length", "LENGTH(c_phone) = 15")
@dp.expect("valid_market_segment", "c_mktsegment IS NOT NULL")
@dp.expect("non_negative_balance", "c_acctbal >= 0")
@dp.temporary_view()
def v_customer():
    return (
        spark.readStream  # type: ignore[name-defined]  # noqa: F821
        .format("delta")
        .table(f"{bronze_catalog}.{bronze_schema}.customer")
        .withColumn("_seq", F.col("_metadata.file_modification_time"))
    )


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.customer",
    cluster_by=["c_mktsegment", "c_nationkey"],
    comment="Silver: customer",
)

dp.create_auto_cdc_flow(
    target=f"{silver_catalog}.{silver_schema}.customer",
    source="v_customer",
    keys=["c_custkey"],
    sequence_by="_seq",
    stored_as_scd_type=1,
)
