"""Medallion SDP (Streaming Delta Pipeline) accelerator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dia.accelerators.base import BaseAccelerator, render_dir, strip_j2

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "medallion_sdp"


class MedallionSdpAccelerator(BaseAccelerator):
    name = "medallion-sdp"
    description = "Streaming Delta Pipeline (SDP) with bronze/silver/gold + DAB job"

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT

    def _pipeline_remap(self, pipeline_name: str):
        """Return a path transform that renames src/pipelines/main → src/pipelines/<pipeline_name>."""
        def _transform(rel: Path) -> Path:
            parts = list(rel.parts)
            if len(parts) >= 3 and parts[0] == "src" and parts[1] == "pipelines" and parts[2] == "main":
                parts[2] = pipeline_name
            return Path(*parts)
        return _transform

    def scaffold(self, target: Path, force: bool = False) -> None:
        pipeline_name: str = self.industry_config.get("pipeline_name", "main")
        from dia.accelerators.base import render_tree
        render_tree(
            template_root=self.template_root,
            target=target,
            context=self._build_context(),
            force=force,
            skip_subdirs=("industries",),
            path_transform=self._pipeline_remap(pipeline_name),
        )
        self._render_industry_templates(target=target, force=force)

    def list_files(self) -> list[Path]:
        pipeline_name: str = self.industry_config.get("pipeline_name", "main")
        remap = self._pipeline_remap(pipeline_name)
        files = [remap(p) for p in super().list_files()]
        industry_root = _TEMPLATE_ROOT / "industries" / self.industry
        if industry_root.exists():
            for src in sorted(industry_root.rglob("*")):
                if not src.is_file():
                    continue
                rel = src.relative_to(industry_root)
                dest = self._industry_dest(rel, pipeline_name)
                if dest is not None:
                    files.append(dest)
        return files

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _render_industry_templates(self, target: Path, force: bool) -> None:
        pipeline_name: str = self.industry_config.get("pipeline_name", "main")
        industry_root = _TEMPLATE_ROOT / "industries" / self.industry
        if not industry_root.exists():
            return

        context = self._build_context()

        from jinja2 import Environment, FileSystemLoader

        env = Environment(
            loader=FileSystemLoader(str(industry_root)),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        for src in sorted(industry_root.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(industry_root)
            dest_rel = self._industry_dest(rel, pipeline_name)
            if dest_rel is None:
                continue

            dest = target / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and not force:
                continue

            if src.suffix == ".j2":
                content = env.get_template(rel.as_posix()).render(**context)
                dest.write_text(content, encoding="utf-8")
            else:
                dest.write_bytes(src.read_bytes())

    def _industry_dest(self, rel: Path, pipeline_name: str) -> Path | None:
        """Map an industry template path to its destination relative to project root."""
        parts = rel.parts
        if not parts:
            return None

        subdir = parts[0]
        rest = Path(*parts[1:])

        mapping = {
            "data_sources": Path("src") / "pipelines" / pipeline_name / "data_sources",
            "gold": Path("src") / "pipelines" / pipeline_name / "transformations" / "gold",
        }

        base = mapping.get(subdir)
        if base is None:
            return None
        return base / strip_j2(rest)
