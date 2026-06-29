"""Streamlit app accelerator — Databricks App scaffolding using TPCH sample data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "app_streamlit"


class AppStreamlitAccelerator(BaseAccelerator):
    name = "app-streamlit"
    description = "Databricks App (Streamlit) connected to the TPCH sample dataset"

    default_config: dict[str, Any] = {
        "app_name": "app-streamlit",
        "secret_scope": "dpa-secrets",
    }

    @property
    def project_slug(self) -> str:
        return self.default_config["app_name"]

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
