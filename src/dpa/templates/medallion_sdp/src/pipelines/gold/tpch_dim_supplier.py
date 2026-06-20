from pyspark import pipelines as dp
from pyspark.sql import functions as F

gold_catalog   = spark.conf.get("gold_catalog")
silver_catalog = spark.conf.get("silver_catalog")
gold_schema    = spark.conf.get("gold_schema")
silver_schema  = spark.conf.get("silver_schema")


@dp.materialized_view(
    name=f"{gold_catalog}.{gold_schema}.dim_supplier",
    cluster_by=["supplier_key"],
    comment="Gold Dimension: dim_supplier",
)
def tpch_dim_supplier():
    df = spark.sql(f"""
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
    return df.select(F.xxhash64(F.col("supplier_key")).alias("supplier_id"), "*")
