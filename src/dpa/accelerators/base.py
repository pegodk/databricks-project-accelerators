"""Abstract base class for all accelerators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

# Files common to every accelerator (.gitignore, CI pipelines) live here.
# An accelerator's own template_root takes precedence for any path that
# exists in both places, so accelerators can still override individual files.
SHARED_TEMPLATE_ROOT = Path(__file__).parent.parent / "templates" / "_shared"


class BaseAccelerator(ABC):
    """Renders a Jinja2 template tree into a target directory.

    Subclasses declare ``name``, ``description``, ``default_config``, and a
    ``template_root``, then override ``scaffold()`` for custom rendering.
    """

    description: str = ""
    name: str = ""
    default_config: dict[str, Any] = {}

    @property
    def project_slug(self) -> str:
        return self.name

    @property
    @abstractmethod
    def template_root(self) -> Path:
        """Path to the Jinja2 template directory for this accelerator."""

    def scaffold(self, target: Path, force: bool = False) -> None:
        """Render the template tree into *target*."""
        render_tree(
            template_root=self.template_root,
            target=target,
            context=self._build_context(),
            force=force,
            shared_root=SHARED_TEMPLATE_ROOT,
        )

    def list_files(self) -> list[Path]:
        """Return relative output paths of all files that would be generated."""
        return [
            strip_j2(rel)
            for rel in sorted(_merged_files([self.template_root, SHARED_TEMPLATE_ROOT]))
        ]

    def _build_context(self) -> dict[str, Any]:
        return {
            "accelerator": self.name,
            "project_slug": self.project_slug,
            "cfg": self.default_config,
        }


# ---------------------------------------------------------------------------
# Shared rendering helpers used by subclasses
# ---------------------------------------------------------------------------

def _merged_files(roots: Sequence[Path]) -> dict[Path, Path]:
    """Map relative path -> absolute source file across *roots*.

    Earlier roots take precedence over later ones when the same relative
    path exists in more than one root.
    """
    merged: dict[Path, Path] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for src in sorted(root.rglob("*")):
            if src.is_file():
                merged.setdefault(src.relative_to(root), src)
    return merged


def render_tree(
    template_root: Path,
    target: Path,
    context: dict[str, Any],
    force: bool,
    path_transform: Callable[[Path], Path] | None = None,
    exclude_dirs: frozenset[str] | None = None,
    shared_root: Path | None = None,
) -> None:
    """Walk *template_root* (plus optional *shared_root*) and render / copy each file into *target*."""
    from jinja2 import Environment, FileSystemLoader

    roots = [template_root, shared_root] if shared_root else [template_root]
    env = Environment(
        loader=FileSystemLoader([str(r) for r in roots]),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    for rel, src in sorted(_merged_files(roots).items()):
        if exclude_dirs and rel.parts[0] in exclude_dirs:
            continue
        rel_out = path_transform(strip_j2(rel)) if path_transform else strip_j2(rel)
        dest = target / rel_out
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not force:
            continue

        if src.suffix == ".j2":
            content = env.get_template(_posix(rel)).render(**context)
            dest.write_text(content, encoding="utf-8")
        else:
            dest.write_bytes(src.read_bytes())


def render_dir(
    src_root: Path,
    dest_root: Path,
    context: dict[str, Any],
    force: bool,
) -> None:
    """Render all templates under *src_root* into *dest_root*."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(str(src_root)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    for src in sorted(src_root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_root)
        dest = dest_root / strip_j2(rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not force:
            continue
        if src.suffix == ".j2":
            content = env.get_template(_posix(rel)).render(**context)
            dest.write_text(content, encoding="utf-8")
        else:
            dest.write_bytes(src.read_bytes())


def strip_j2(path: Path) -> Path:
    return path.with_suffix("") if path.suffix == ".j2" else path


def _posix(path: Path) -> str:
    return path.as_posix()
