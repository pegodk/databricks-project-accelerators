from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "medallion_dbt"


class MedallionDbtAccelerator(BaseAccelerator):
    name = "medallion-dbt"
    description = "Medallion architecture (bronze/silver/gold) using dbt models over TPCH"
    default_config: dict[str, Any] = {
        "catalog": "main",
        "schema": "dbt_tpch",
        "warehouse_id": "<your-warehouse-id>",
        "node_type_id": "Standard_DS3_v2",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
