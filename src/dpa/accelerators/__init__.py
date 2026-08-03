"""Accelerator registry.

Add new accelerators here so ``dpa list`` and ``dpa init`` pick them up
automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpa.accelerators.base import BaseAccelerator

from dpa.accelerators.ai_bi import AiBiAccelerator
from dpa.accelerators.custom_python_wheel import CustomPythonWheelAccelerator
from dpa.accelerators.lakebase_streamlit_app import LakebaseStreamlitAppAccelerator
from dpa.accelerators.medallion_dbt import MedallionDbtAccelerator
from dpa.accelerators.medallion_sdp import MedallionSdpAccelerator
from dpa.accelerators.mlflow_project import MlflowProjectAccelerator

ACCELERATOR_REGISTRY: dict[str, type[BaseAccelerator]] = {
    "ai-bi": AiBiAccelerator,
    "custom-python-wheel": CustomPythonWheelAccelerator,
    "lakebase-streamlit-app": LakebaseStreamlitAppAccelerator,
    "medallion-dbt": MedallionDbtAccelerator,
    "medallion-sdp": MedallionSdpAccelerator,
    "mlflow-project": MlflowProjectAccelerator,
}


def get_accelerator(name: str) -> type[BaseAccelerator] | None:
    return ACCELERATOR_REGISTRY.get(name)
