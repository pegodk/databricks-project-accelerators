from pyspark import pipelines as dp
from pyspark.sql import functions as F

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect_or_fail("valid_nation_name", "n_name IS NOT NULL AND LENGTH(n_name) > 0")
@dp.temporary_view()
def v_tpch_nation():
    return spark.read.table(f"{bronze_catalog}.{bronze_schema}.nation")


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.nation",
    cluster_by=["n_regionkey"],
    comment="Silver: nation",
)

dp.create_auto_cdc_from_snapshot_flow(
    target=f"{silver_catalog}.{silver_schema}.nation",
    source="v_tpch_nation",
    keys=["n_nationkey"],
    stored_as_scd_type=1,
)
