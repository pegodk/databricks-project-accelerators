"""Lakebase App accelerator — Databricks App (Streamlit) with Lakebase master data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "lakebase_app"


class LakebaseAppAccelerator(BaseAccelerator):
    name = "lakebase-app"
    description = "Databricks App (Streamlit) connected to TPCH analytics + Lakebase master data"

    default_config: dict[str, Any] = {
        "app_name": "lakebase-app",
        "lakebase_project_id": "lakebase-app-lakebase",
        "lakebase_min_cu": 0.5,
        "lakebase_max_cu": 0.5,
        "lakebase_pghost": "<set-after-first-deploy>",
        "lakebase_endpoint": "<projects/.../branches/.../endpoints/primary>",
    }

    @property
    def project_slug(self) -> str:
        return self.default_config["app_name"]

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
