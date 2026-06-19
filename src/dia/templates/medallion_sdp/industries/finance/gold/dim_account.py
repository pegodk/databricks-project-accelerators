"""Gold layer: dim_account — account dimension with surrogate key."""

from __future__ import annotations

import os
import sys

import dlt
from pyspark.sql import functions as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from framework.utils import add_dummy_row, add_ingest_timestamp, add_surrogate_id


@dlt.table(
    name="dim_account",
    comment="Account dimension — one row per unique account, surrogate-keyed",
)
def dim_account():
    return (
        dlt.read("accounts")
        .select(
            F.col("account_id").alias("account_key"),
            F.col("customer_id").alias("customer_key"),  # FK to dim_customer
            F.col("account_type"),
            F.col("currency"),
            F.col("opened_date"),
            F.col("status").alias("account_status"),
        )
        .transform(lambda df: add_surrogate_id(df, "account_id"))
        .transform(add_ingest_timestamp)
        .transform(lambda df: add_dummy_row(df, "account_id"))
    )
