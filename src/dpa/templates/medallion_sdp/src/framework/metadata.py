"""YAML-based table metadata loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_table_configs(config_dir: str | Path) -> list[dict[str, Any]]:
    """Load and merge all ``*.yml`` table config files from *config_dir*.

    Each file may contain a single mapping or a list of mappings.
    """
    configs: list[dict[str, Any]] = []
    for path in sorted(Path(config_dir).glob("*.yml")):
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, list):
            configs.extend(data)
        elif isinstance(data, dict):
            configs.append(data)
    return configs
