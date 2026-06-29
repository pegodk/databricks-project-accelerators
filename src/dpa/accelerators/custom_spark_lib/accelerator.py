from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "custom_spark_lib"


class CustomSparkLibAccelerator(BaseAccelerator):
    name = "custom-spark-lib"
    description = "Medallion pipeline with a custom PySpark library packaged as a wheel and deployed via DAB artifacts"
    default_config: dict[str, Any] = {
        "bronze_catalog": "dpa_bronze_dev",
        "gold_catalog": "dpa_gold_dev",
        "bronze_schema": "tpch_spark",
        "gold_schema": "tpch_model_spark",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
