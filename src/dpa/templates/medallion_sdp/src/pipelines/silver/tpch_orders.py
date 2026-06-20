from pyspark import pipelines as dp

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect_or_drop("valid_orderstatus", "o_orderstatus IN ('F', 'P', 'O')")
@dp.expect_or_drop("valid_priority", "o_orderpriority IN ('1-URGENT', '2-HIGH', '3-MEDIUM', '4-NOT SPECIFIED', '5-LOW')")
@dp.temporary_view()
def v_orders():
    return (
        spark.readStream  # type: ignore[name-defined]  # noqa: F821
        .format("delta")
        .table(f"{bronze_catalog}.{bronze_schema}.orders")
    )


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.orders",
    cluster_by=["o_orderdate", "o_orderstatus"],
    comment="Silver: orders",
)

dp.create_auto_cdc_flow(
    target=f"{silver_catalog}.{silver_schema}.orders",
    source="v_orders",
    keys=["o_orderkey"],
    sequence_by="o_orderkey",  # placeholder: tpch is static reference data with no event sequence
    stored_as_scd_type=1,
)
