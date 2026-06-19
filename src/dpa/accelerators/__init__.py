"""Accelerator registry.

Add new accelerators here so ``dia list`` and ``dia init`` pick them up
automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpa.accelerators.base import BaseAccelerator

from dpa.accelerators.app_streamlit import AppStreamlitAccelerator
from dpa.accelerators.dashboard import DashboardAccelerator
from dpa.accelerators.medallion_sdp import MedallionSdpAccelerator

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
