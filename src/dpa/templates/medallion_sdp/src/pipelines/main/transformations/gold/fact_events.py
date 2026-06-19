"""Gold layer: fact_events — events fact table."""

from __future__ import annotations

import os
import sys

import dlt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from framework.utils import add_ingest_timestamp


@dlt.table(
    name="fact_events",
    comment="Events fact table",
)
def fact_events():
    return dlt.read("events").transform(add_ingest_timestamp)
