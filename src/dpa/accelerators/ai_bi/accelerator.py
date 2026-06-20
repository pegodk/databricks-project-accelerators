"""AI/BI accelerator — metric views + Lakeview dashboard + Genie Space over TPCH sample data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "ai_bi"


class AiBiAccelerator(BaseAccelerator):
    name = "ai-bi"
    description = "AI/BI Dashboards + Genie Space with metric views over the TPCH sample dataset"

    default_config: dict[str, Any] = {
        "dashboard_name": "TPCH Sales Overview",
        "genie_space_name": "TPCH Sales Genie",
        "catalog": "dpa_gold_dev",
        "schema": "tpch_metrics",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
