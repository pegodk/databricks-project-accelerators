"""Medallion SDP (Streaming Delta Pipeline) accelerator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator, render_tree

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "medallion_sdp"
_EXCLUDE = frozenset({"src_example"})


class MedallionSdpAccelerator(BaseAccelerator):
    name = "medallion-sdp"
    description = "Streaming Delta Pipeline (DLT) with bronze/silver/gold over TPCH"

    default_config: dict[str, Any] = {
        "bronze_schema": "tpch",
        "silver_schema": "tpch",
        "gold_schema": "tpch",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT

    def list_files(self) -> list[Path]:
        return [p for p in super().list_files() if p.parts[0] not in _EXCLUDE]

    def scaffold(self, target: Path, force: bool = False) -> None:
        render_tree(
            template_root=self.template_root,
            target=target,
            context=self._build_context(),
            force=force,
            exclude_dirs=_EXCLUDE,
        )
