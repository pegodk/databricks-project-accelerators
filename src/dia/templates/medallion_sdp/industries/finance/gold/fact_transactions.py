"""Gold layer: fact_transactions — transaction fact table with surrogate keys.

Natural keys from the silver transactions table are replaced with surrogate IDs
by joining against the dimension tables. Missing dimension members resolve to -1
(the dummy row inserted by add_dummy_row).
"""

from __future__ import annotations

import os
import sys

import dlt
from pyspark.sql import functions as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from framework.utils import add_ingest_timestamp


@dlt.table(
    name="fact_transactions",
    comment="Transaction fact table — fully surrogate-keyed, ready for BI",
)
def fact_transactions():
    transactions = dlt.read("transactions")
    dim_customer = dlt.read("dim_customer").select("customer_key", "customer_id")
    dim_account = dlt.read("dim_account").select("account_key", "account_id")
    dim_calendar = dlt.read("dim_calendar").select(
        F.to_date("calendar_date").alias("calendar_date"), "calendar_id"
    )

    return (
        transactions
        # Resolve customer surrogate key
        .join(dim_customer, transactions["customer_id"] == dim_customer["customer_key"], "left")
        .drop("customer_key")
        # Resolve account surrogate key
        .join(dim_account, transactions["account_id"] == dim_account["account_key"], "left")
        .drop("account_key")
        # Resolve calendar surrogate key
        .join(
            dim_calendar,
            F.to_date(transactions["transaction_date"]) == dim_calendar["calendar_date"],
            "left",
        )
        .drop("calendar_date")
        # Fill -1 for unresolved foreign keys (handled by dummy rows in dims)
        .fillna({"customer_id": -1, "account_id": -1, "calendar_id": -1})
        .select(
            F.col("transaction_id"),
            F.col("customer_id"),
            F.col("account_id"),
            F.col("calendar_id"),
            F.col("amount"),
            F.col("transaction_date"),
            F.col("category"),
            F.col("status"),
            F.col("description"),
        )
        .transform(add_ingest_timestamp)
    )
