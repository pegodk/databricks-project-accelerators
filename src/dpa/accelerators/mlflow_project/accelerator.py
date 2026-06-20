from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "mlflow_project"


class MlflowProjectAccelerator(BaseAccelerator):
    name = "mlflow-project"
    description = "MLflow training, model registration, and batch scoring over the TPCH sample dataset"
    default_config: dict[str, Any] = {
        "catalog": "main",
        "schema": "mlflow_demo",
        "experiment_name": "/Shared/tpch-order-value",
        "model_name": "tpch_order_value",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
