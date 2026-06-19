"""Gold layer: dim_entity — entity dimension with surrogate key."""

from __future__ import annotations

import os
import sys

import dlt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from framework.utils import add_ingest_timestamp, add_surrogate_id


@dlt.table(
    name="dim_entity",
    comment="Entity dimension — one row per unique entity, surrogate-keyed",
)
def dim_entity():
    return (
        dlt.read("entities")
        .transform(lambda df: add_surrogate_id(df, "entity_id"))
        .transform(add_ingest_timestamp)
    )
