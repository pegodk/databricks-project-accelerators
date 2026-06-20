"""Accelerator registry.

Add new accelerators here so ``dpa list`` and ``dpa init`` pick them up
automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpa.accelerators.base import BaseAccelerator

from dpa.accelerators.ai_bi import AiBiAccelerator
from dpa.accelerators.app_streamlit import AppStreamlitAccelerator
from dpa.accelerators.medallion_sdp import MedallionSdpAccelerator
from dpa.accelerators.medallion_spark import MedallionSparkAccelerator
from dpa.accelerators.mlflow_project import MlflowProjectAccelerator
from dpa.accelerators.python_wheel import PythonWheelAccelerator

ACCELERATOR_REGISTRY: dict[str, type[BaseAccelerator]] = {
    "medallion-sdp": MedallionSdpAccelerator,
    "medallion-spark": MedallionSparkAccelerator,
    "mlflow-project": MlflowProjectAccelerator,
    "app-streamlit": AppStreamlitAccelerator,
    "python-wheel": PythonWheelAccelerator,
    "ai-bi": AiBiAccelerator,
}


def get_accelerator(name: str) -> type[BaseAccelerator] | None:
    return ACCELERATOR_REGISTRY.get(name)
