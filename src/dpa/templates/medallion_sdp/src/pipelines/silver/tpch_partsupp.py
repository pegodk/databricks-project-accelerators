from pyspark import pipelines as dp

silver_catalog = spark.conf.get("silver_catalog")
bronze_catalog = spark.conf.get("bronze_catalog")
silver_schema  = spark.conf.get("silver_schema")
bronze_schema  = spark.conf.get("bronze_schema")


@dp.expect("sufficient_inventory", "ps_availqty >= 100")
@dp.expect("reasonable_cost", "ps_supplycost < 900")
@dp.temporary_view()
def v_partsupp():
    return (
        spark.readStream  # type: ignore[name-defined]  # noqa: F821
        .format("delta")
        .table(f"{bronze_catalog}.{bronze_schema}.partsupp")
    )


dp.create_streaming_table(
    name=f"{silver_catalog}.{silver_schema}.partsupp",
    cluster_by=["ps_suppkey"],
    comment="Silver: partsupp",
)

dp.create_auto_cdc_flow(
    target=f"{silver_catalog}.{silver_schema}.partsupp",
    source="v_partsupp",
    keys=["ps_partkey", "ps_suppkey"],
    sequence_by="ps_partkey",  # placeholder: tpch is static reference data with no event sequence
    stored_as_scd_type=1,
)
