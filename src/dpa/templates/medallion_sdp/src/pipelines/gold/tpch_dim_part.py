from pyspark import pipelines as dp
from pyspark.sql import functions as F

gold_catalog   = spark.conf.get("gold_catalog")
silver_catalog = spark.conf.get("silver_catalog")
gold_schema    = spark.conf.get("gold_schema")
silver_schema  = spark.conf.get("silver_schema")


@dp.temporary_view()
def v_tpch_dim_part():
    return spark.sql(f"""
        SELECT
          p_partkey       AS part_key,
          p_name          AS part_name,
          p_mfgr          AS part_manufacturer,
          p_brand         AS part_brand,
          p_type          AS part_type,
          p_size          AS part_size,
          p_container     AS part_container,
          p_retailprice   AS part_retail_price,
          p_comment       AS part_comment
        FROM {silver_catalog}.{silver_schema}.part
    """.strip())


dp.create_streaming_table(
    name=f"{gold_catalog}.{gold_schema}.dim_part_cdc",
    cluster_by=["part_key"],
    comment="Gold Dimension CDC: dim_part",
)

dp.create_auto_cdc_from_snapshot_flow(
    target=f"{gold_catalog}.{gold_schema}.dim_part_cdc",
    source="v_tpch_dim_part",
    keys=["part_key"],
    stored_as_scd_type=1,
)


@dp.materialized_view(
    name=f"{gold_catalog}.{gold_schema}.dim_part",
    cluster_by=["part_key"],
    comment="Gold Dimension: dim_part",
)
def tpch_dim_part():
    base_df = spark.table(f"{gold_catalog}.{gold_schema}.dim_part_cdc")
    return base_df.select(F.xxhash64(F.col("part_key")).alias("part_id"), "*")
