"""Reusable PySpark transformation functions for the medallion gold layer."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_dim_customer(customer: DataFrame, nation: DataFrame, region: DataFrame) -> DataFrame:
    return (
        customer
        .join(nation, customer.c_nationkey == nation.n_nationkey)
        .join(region, nation.n_regionkey == region.r_regionkey)
        .select(
            F.col("c_custkey").alias("customer_key"),
            F.col("c_name").alias("customer_name"),
            F.col("c_address").alias("customer_address"),
            F.col("c_phone").alias("customer_phone"),
            F.col("c_acctbal").alias("customer_acctbal"),
            F.col("c_mktsegment").alias("customer_segment"),
            F.coalesce(F.col("n_name"), F.lit("Unknown")).alias("customer_nation"),
            F.coalesce(F.col("r_name"), F.lit("Unknown")).alias("customer_region"),
        )
    )


def build_dim_part(part: DataFrame) -> DataFrame:
    return part.select(
        F.col("p_partkey").alias("part_key"),
        F.col("p_name").alias("part_name"),
        F.col("p_mfgr").alias("part_manufacturer"),
        F.col("p_brand").alias("part_brand"),
        F.col("p_type").alias("part_type"),
        F.col("p_size").alias("part_size"),
        F.col("p_container").alias("part_container"),
        F.col("p_retailprice").alias("part_retail_price"),
    )


def build_dim_supplier(supplier: DataFrame, nation: DataFrame, region: DataFrame) -> DataFrame:
    return (
        supplier
        .join(nation, supplier.s_nationkey == nation.n_nationkey)
        .join(region, nation.n_regionkey == region.r_regionkey)
        .select(
            F.col("s_suppkey").alias("supplier_key"),
            F.col("s_name").alias("supplier_name"),
            F.col("s_address").alias("supplier_address"),
            F.col("s_phone").alias("supplier_phone"),
            F.coalesce(F.col("n_name"), F.lit("Unknown")).alias("supplier_nation"),
            F.coalesce(F.col("r_name"), F.lit("Unknown")).alias("supplier_region"),
        )
    )


def build_fact_order(lineitem: DataFrame, orders: DataFrame, partsupp: DataFrame) -> DataFrame:
    return (
        lineitem
        .join(orders, lineitem.l_orderkey == orders.o_orderkey)
        .join(
            partsupp,
            (lineitem.l_partkey == partsupp.ps_partkey) & (lineitem.l_suppkey == partsupp.ps_suppkey),
            "left",
        )
        .select(
            F.col("o_orderdate").alias("calendar_order_key"),
            F.col("l_commitdate").alias("calendar_commit_key"),
            F.col("l_receiptdate").alias("calendar_receipt_key"),
            F.col("l_shipdate").alias("calendar_ship_key"),
            F.col("o_custkey").alias("customer_key"),
            F.col("l_partkey").alias("part_key"),
            F.col("l_suppkey").alias("supplier_key"),
            F.col("l_orderkey").alias("order_header_code"),
            F.col("l_linenumber").alias("order_line_code"),
            F.col("l_quantity").alias("order_quantity"),
            F.col("l_extendedprice").alias("order_extended_price_usd"),
            F.col("l_discount").alias("order_discount_usd"),
            F.col("l_tax").alias("order_tax_usd"),
            F.col("ps_supplycost").alias("part_supply_cost_usd"),
            F.datediff(F.col("l_commitdate"), F.col("o_orderdate")).alias("order_commit_lag_days"),
            F.datediff(F.col("l_receiptdate"), F.col("o_orderdate")).alias("order_receipt_lag_days"),
            F.datediff(F.col("l_shipdate"), F.col("o_orderdate")).alias("order_ship_lag_days"),
        )
    )
