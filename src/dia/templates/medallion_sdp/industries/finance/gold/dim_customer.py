"""Gold layer: dim_customer — customer dimension with surrogate key."""

from __future__ import annotations

import os
import sys

import dlt
from pyspark.sql import functions as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from framework.utils import add_dummy_row, add_ingest_timestamp, add_surrogate_id


@dlt.table(
    name="dim_customer",
    comment="Customer dimension — one row per unique customer, surrogate-keyed",
)
def dim_customer():
    return (
        dlt.read("customers")
        .select(
            F.col("customer_id").alias("customer_key"),
            F.concat_ws(" ", F.col("first_name"), F.col("last_name")).alias("full_name"),
            F.col("first_name"),
            F.col("last_name"),
            F.col("email"),
            F.col("phone"),
            F.col("country"),
            F.col("city"),
            F.col("customer_segment"),
            F.col("created_date"),
        )
        .transform(lambda df: add_surrogate_id(df, "customer_id"))
        .transform(add_ingest_timestamp)
        .transform(lambda df: add_dummy_row(df, "customer_id"))
    )
