from pyspark import pipelines as dp
from pyspark.sql import functions as F

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect_or_fail("valid_region_name", "r_name IS NOT NULL AND LENGTH(r_name) > 0")
@dp.temporary_view()
def v_tpch_region():
    return spark.read.table(f"{bronze_catalog}.{bronze_schema}.region")


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.region",
    cluster_by=["r_name"],
    comment="Silver: region",
)

dp.create_auto_cdc_from_snapshot_flow(
    target=f"{silver_catalog}.{silver_schema}.region",
    source="v_tpch_region",
    keys=["r_regionkey"],
    stored_as_scd_type=1,
)
