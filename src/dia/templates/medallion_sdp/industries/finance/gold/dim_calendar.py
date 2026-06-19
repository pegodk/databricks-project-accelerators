"""Gold layer: dim_calendar — date dimension derived from transaction dates."""

from __future__ import annotations

import os
import sys

import dlt
from pyspark.sql import functions as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from framework.utils import add_ingest_timestamp, add_surrogate_id


@dlt.table(
    name="dim_calendar",
    comment="Calendar dimension derived from transaction dates",
)
def dim_calendar():
    return (
        dlt.read("transactions")
        .select(F.to_date(F.col("transaction_date")).alias("calendar_date"))
        .distinct()
        .select(
            F.col("calendar_date"),
            F.year("calendar_date").alias("year"),
            F.quarter("calendar_date").alias("quarter"),
            F.month("calendar_date").alias("month"),
            F.date_format("calendar_date", "MMMM").alias("month_name"),
            F.dayofmonth("calendar_date").alias("day_of_month"),
            F.dayofweek("calendar_date").alias("day_of_week"),
            F.date_format("calendar_date", "EEEE").alias("day_name"),
            F.weekofyear("calendar_date").alias("week_of_year"),
            (F.dayofweek("calendar_date").isin(1, 7)).cast("boolean").alias("is_weekend"),
        )
        .transform(lambda df: add_surrogate_id(df, "calendar_id"))
        .transform(add_ingest_timestamp)
    )
