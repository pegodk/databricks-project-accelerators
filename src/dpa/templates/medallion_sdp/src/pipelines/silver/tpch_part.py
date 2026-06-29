from pyspark import pipelines as dp

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect_or_fail("positive_size", "p_size > 0")
@dp.expect("positive_retail_price", "p_retailprice > 0")
@dp.temporary_view()
def v_part():
    return (
        spark.readStream  # type: ignore[name-defined]  # noqa: F821
        .format("delta")
        .table(f"{bronze_catalog}.{bronze_schema}.part")
    )


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.part",
    cluster_by=["p_type", "p_brand"],
    comment="Silver: part",
)

dp.create_auto_cdc_flow(
    target=f"{silver_catalog}.{silver_schema}.part",
    source="v_part",
    keys=["p_partkey"],
    sequence_by="p_partkey",  # placeholder: tpch is static reference data with no event sequence
    stored_as_scd_type=1,
)
