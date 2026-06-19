"""Accelerator registry.

Add new accelerators here so ``dia list`` and ``dia init`` pick them up
automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dia.accelerators.base import BaseAccelerator

from dia.accelerators.app_streamlit import AppStreamlitAccelerator
from dia.accelerators.dashboard import DashboardAccelerator
from dia.accelerators.medallion_sdp import MedallionSdpAccelerator

ACCELERATOR_REGISTRY: dict[str, type[BaseAccelerator]] = {
    "medallion-sdp": MedallionSdpAccelerator,
    "app-streamlit": AppStreamlitAccelerator,
    "dashboard": DashboardAccelerator,
    # Future:
    # "medallion-notebooks": MedallionNotebooksAccelerator,
    # "genie-space": GenieSpaceAccelerator,
    # "mlflow-project": MlflowProjectAccelerator,
}


def get_accelerator(name: str) -> type[BaseAccelerator] | None:
    return ACCELERATOR_REGISTRY.get(name)
