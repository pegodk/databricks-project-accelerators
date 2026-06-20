"""Gold layer: fact_events — events fact table with temporal breakdown."""

from __future__ import annotations

import dlt
from pyspark.sql import functions as F


@dlt.table(
    name="fact_events",
    comment="Events fact table — one row per event with temporal attributes",
)
def fact_events():
    return (
        dlt.read("events")
        .select(
            F.col("event_id"),
            F.col("value").alias("event_value"),
            F.col("created_at").alias("event_timestamp"),
            F.col("created_at").cast("date").alias("event_date"),
            F.year("created_at").alias("event_year"),
            F.month("created_at").alias("event_month"),
            F.col("attributes"),
        )
    )
