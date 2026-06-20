"""Gold layer: dim_entity — entity dimension."""

from __future__ import annotations

import dlt
from pyspark.sql import functions as F


@dlt.table(
    name="dim_entity",
    comment="Entity dimension — one row per unique entity",
)
def dim_entity():
    return (
        dlt.read("entities")
        .select(
            F.col("entity_id"),
            F.col("value").alias("entity_name"),
            F.col("created_at").alias("valid_from"),
            F.col("attributes"),
        )
    )
