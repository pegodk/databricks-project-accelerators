from pyspark import pipelines as dp
from pyspark.sql import functions as F

gold_catalog   = spark.conf.get("gold_catalog")
silver_catalog = spark.conf.get("silver_catalog")
gold_schema    = spark.conf.get("gold_schema")
silver_schema  = spark.conf.get("silver_schema")


@dp.materialized_view(
    name=f"{gold_catalog}.{gold_schema}.fact_order",
    cluster_by=["calendar_order_key", "customer_key"],
    comment="Gold Fact: fact_order — grain: one row per order line item",
)
def tpch_fact_order():
    df = spark.sql(f"""
        SELECT
          orders.o_orderdate                                            AS calendar_order_key,
          lineitem.l_commitdate                                         AS calendar_commit_key,
          lineitem.l_receiptdate                                        AS calendar_receipt_key,
          lineitem.l_shipdate                                           AS calendar_ship_key,
          orders.o_custkey                                              AS customer_key,
          lineitem.l_partkey                                            AS part_key,
          lineitem.l_suppkey                                            AS supplier_key,
          lineitem.l_orderkey                                           AS order_header_code,
          lineitem.l_linenumber                                         AS order_line_code,
          lineitem.l_quantity                                           AS order_quantity,
          lineitem.l_extendedprice                                      AS order_extended_price_usd,
          lineitem.l_discount                                           AS order_discount_usd,
          lineitem.l_tax                                                AS order_tax_usd,
          partsupp.ps_supplycost                                        AS part_supply_cost_usd,
          datediff(lineitem.l_commitdate,  orders.o_orderdate)          AS order_commit_lag_days,
          datediff(lineitem.l_receiptdate, orders.o_orderdate)          AS order_receipt_lag_days,
          datediff(lineitem.l_shipdate,    orders.o_orderdate)          AS order_ship_lag_days
        FROM {silver_catalog}.{silver_schema}.lineitem
        LEFT JOIN {silver_catalog}.{silver_schema}.orders
          ON lineitem.l_orderkey = orders.o_orderkey
        LEFT JOIN {silver_catalog}.{silver_schema}.partsupp
          ON lineitem.l_partkey = partsupp.ps_partkey AND lineitem.l_suppkey = partsupp.ps_suppkey
    """.strip())

    dim_customer = spark.table(f"{gold_catalog}.{gold_schema}.dim_customer")
    dim_part     = spark.table(f"{gold_catalog}.{gold_schema}.dim_part")
    dim_supplier = spark.table(f"{gold_catalog}.{gold_schema}.dim_supplier")

    return (
        df
        .join(dim_customer.select("customer_key", "customer_id"), on="customer_key", how="left")
        .join(dim_part.select("part_key", "part_id"), on="part_key", how="left")
        .join(dim_supplier.select("supplier_key", "supplier_id"), on="supplier_key", how="left")
    )
