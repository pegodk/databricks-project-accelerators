from pyspark import pipelines as dp
from pyspark.sql import functions as F

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect("valid_quantity", "l_quantity >= 1 AND l_quantity <= 100")
@dp.expect("reasonable_tax", "l_tax < 0.15")
@dp.expect("reasonable_discount", "l_discount < 0.10")
@dp.temporary_view()
def v_lineitem():
    return (
        spark.readStream  # type: ignore[name-defined]  # noqa: F821
        .format("delta")
        .table(f"{bronze_catalog}.{bronze_schema}.lineitem")
        .withColumn("_seq", F.col("_metadata.file_modification_time"))
    )


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.lineitem",
    cluster_by=["l_shipdate", "l_returnflag"],
    comment="Silver: lineitem",
)

dp.create_auto_cdc_flow(
    target=f"{silver_catalog}.{silver_schema}.lineitem",
    source="v_lineitem",
    keys=["l_orderkey", "l_linenumber"],
    sequence_by="_seq",
    stored_as_scd_type=1,
)
