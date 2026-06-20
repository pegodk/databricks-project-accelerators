"""Medallion SDP (Streaming Delta Pipeline) accelerator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator, render_tree

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "medallion_sdp"


class MedallionSdpAccelerator(BaseAccelerator):
    name = "medallion-sdp"
    description = "Streaming Delta Pipeline (SDP) with bronze/silver/gold + DAB job"

    default_config: dict[str, Any] = {
        "pipeline_name": "main",
        "source_class": "SyntheticDataSource",
        "bronze_schema": "tpch_sdp",
        "silver_schema": "tpch_sdp",
        "gold_schema": "tpch_sdp",
        "bronze_tables": [
            {"name": "events", "primary_keys": ["event_id"], "description": "Raw events"},
            {"name": "entities", "primary_keys": ["entity_id"], "description": "Entity records"},
            {"name": "records", "primary_keys": ["record_id"], "description": "Source records"},
        ],
        "silver_expectations": {
            "events": {"fail_update": {"event_id_not_null": "event_id IS NOT NULL"}},
            "entities": {"fail_update": {"entity_id_not_null": "entity_id IS NOT NULL"}},
            "records": {"fail_update": {"record_id_not_null": "record_id IS NOT NULL"}},
        },
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT

    def scaffold(self, target: Path, force: bool = False) -> None:
        pipeline_name: str = self.default_config["pipeline_name"]
        render_tree(
            template_root=self.template_root,
            target=target,
            context=self._build_context(),
            force=force,
            path_transform=self._pipeline_remap(pipeline_name),
        )

    def list_files(self) -> list[Path]:
        pipeline_name: str = self.default_config["pipeline_name"]
        remap = self._pipeline_remap(pipeline_name)
        return [remap(p) for p in super().list_files()]

    def _pipeline_remap(self, pipeline_name: str):
        """Return a path transform that renames src/pipelines/main → src/pipelines/<pipeline_name>."""
        def _transform(rel: Path) -> Path:
            parts = list(rel.parts)
            if len(parts) >= 3 and parts[0] == "src" and parts[1] == "pipelines" and parts[2] == "main":
                parts[2] = pipeline_name
            return Path(*parts)
        return _transform
