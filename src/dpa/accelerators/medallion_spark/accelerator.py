from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "medallion_spark"


class MedallionSparkAccelerator(BaseAccelerator):
    name = "medallion-spark"
    description = "Medallion architecture (bronze/silver/gold) using Spark Structured Streaming notebooks over TPCH"
    default_config: dict[str, Any] = {
        "bronze_catalog": "dpa_bronze_dev",
        "silver_catalog": "dpa_silver_dev",
        "gold_catalog": "dpa_gold_dev",
        "bronze_schema": "tpch_spark",
        "silver_schema": "tpch_spark",
        "gold_schema": "tpch_spark",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
