from pyspark import pipelines as dp
from pyspark.sql import functions as F

gold_catalog   = spark.conf.get("gold_catalog")
silver_catalog = spark.conf.get("silver_catalog")
gold_schema    = spark.conf.get("gold_schema")
silver_schema  = spark.conf.get("silver_schema")


@dp.temporary_view()
def v_tpch_dim_supplier():
    return spark.sql(f"""
        SELECT
          sup.s_suppkey                       AS supplier_key,
          sup.s_name                          AS supplier_name,
          sup.s_address                       AS supplier_address,
          sup.s_phone                         AS supplier_phone,
          COALESCE(nat.n_name, 'Unknown')     AS supplier_nation,
          COALESCE(reg.r_name, 'Unknown')     AS supplier_region
        FROM {silver_catalog}.{silver_schema}.supplier sup
        LEFT JOIN {silver_catalog}.{silver_schema}.nation nat ON sup.s_nationkey = nat.n_nationkey
        LEFT JOIN {silver_catalog}.{silver_schema}.region reg ON nat.n_regionkey = reg.r_regionkey
    """.strip())


dp.create_streaming_table(
    name=f"{gold_catalog}.{gold_schema}.dim_supplier_cdc",
    cluster_by=["supplier_key"],
    comment="Gold Dimension CDC: dim_supplier",
)

dp.create_auto_cdc_from_snapshot_flow(
    target=f"{gold_catalog}.{gold_schema}.dim_supplier_cdc",
    source="v_tpch_dim_supplier",
    keys=["supplier_key"],
    stored_as_scd_type=1,
)


@dp.materialized_view(
    name=f"{gold_catalog}.{gold_schema}.dim_supplier",
    cluster_by=["supplier_key"],
    comment="Gold Dimension: dim_supplier",
)
def tpch_dim_supplier():
    base_df = spark.table(f"{gold_catalog}.{gold_schema}.dim_supplier_cdc")
    return base_df.select(F.xxhash64(F.col("supplier_key")).alias("supplier_id"), "*")
