from pyspark import pipelines as dp
from pyspark.sql import functions as F

gold_catalog   = spark.conf.get("gold_catalog")
silver_catalog = spark.conf.get("silver_catalog")
gold_schema    = spark.conf.get("gold_schema")
silver_schema  = spark.conf.get("silver_schema")


@dp.materialized_view(
    name=f"{gold_catalog}.{gold_schema}.dim_customer",
    cluster_by=["customer_key"],
    comment="Gold Dimension: dim_customer",
)
def tpch_dim_customer():
    df = spark.sql(f"""
        SELECT
          cust.c_custkey                      AS customer_key,
          cust.c_name                         AS customer_name,
          cust.c_address                      AS customer_address,
          cust.c_phone                        AS customer_phone,
          cust.c_acctbal                      AS customer_acctbal,
          cust.c_mktsegment                   AS customer_segment,
          COALESCE(nat.n_name, 'Unknown')     AS customer_nation,
          COALESCE(reg.r_name, 'Unknown')     AS customer_region
        FROM {silver_catalog}.{silver_schema}.customer cust
        LEFT JOIN {silver_catalog}.{silver_schema}.nation nat ON cust.c_nationkey = nat.n_nationkey
        LEFT JOIN {silver_catalog}.{silver_schema}.region reg ON nat.n_regionkey = reg.r_regionkey
    """.strip())
    return df.select(F.xxhash64(F.col("customer_key")).alias("customer_id"), "*")
