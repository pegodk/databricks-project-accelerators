from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "medallion_spark"


class MedallionSparkAccelerator(BaseAccelerator):
    name = "medallion-spark"
    description = "Medallion architecture (bronze/silver/gold) using Spark Structured Streaming notebooks over the TPCH sample dataset"
    default_config: dict[str, Any] = {
        "bronze_catalog": "bronze_dev",
        "silver_catalog": "silver_dev",
        "gold_catalog": "gold_dev",
        "schema": "tpch",
        "node_type_id": "Standard_DS3_v2",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
