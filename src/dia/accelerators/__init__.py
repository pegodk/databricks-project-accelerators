"""Accelerator registry.

Add new accelerators here so ``dia list`` and ``dia init`` pick them up
automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dia.accelerators.base import BaseAccelerator

from dia.accelerators.medallion_sdp import MedallionSdpAccelerator

ACCELERATOR_REGISTRY: dict[str, type[BaseAccelerator]] = {
    "medallion-sdp": MedallionSdpAccelerator,
    # Future:
    # "medallion-notebooks": MedallionNotebooksAccelerator,
    # "dashboard": DashboardAccelerator,
    # "genie-space": GenieSpaceAccelerator,
    # "mlflow-project": MlflowProjectAccelerator,
    # "app": AppAccelerator,
}


def get_accelerator(name: str) -> type[BaseAccelerator] | None:
    return ACCELERATOR_REGISTRY.get(name)
