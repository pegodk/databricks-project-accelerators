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
def v_tpch_customer():
    return spark.read.table(f"{bronze_catalog}.{bronze_schema}.customer")


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.customer",
    cluster_by=["c_mktsegment", "c_nationkey"],
    comment="Silver: customer",
)

dp.create_auto_cdc_from_snapshot_flow(
    target=f"{silver_catalog}.{silver_schema}.customer",
    source="v_tpch_customer",
    keys=["c_custkey"],
    stored_as_scd_type=1,
)
