from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "medallion_dbt"


class MedallionDbtAccelerator(BaseAccelerator):
    name = "medallion-dbt"
    description = "Medallion architecture (bronze/silver/gold) using dbt models over TPCH"
    default_config: dict[str, Any] = {
        "bronze_catalog": "dpa_bronze_dev",
        "gold_catalog": "dpa_gold_dev",
        "schema": "tpch_dbt",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
