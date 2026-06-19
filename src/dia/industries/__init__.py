"""Industry registry and config loader.

Each industry lives in its own subdirectory (e.g. ``finance/``) and provides
one YAML config file per supported accelerator, named after the accelerator
with hyphens replaced by underscores, e.g. ``medallion_sdp.yaml``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_INDUSTRIES_ROOT = Path(__file__).parent


def get_industry_config(accelerator: str, industry: str) -> dict[str, Any] | None:
    """Load the YAML config for *industry* in the context of *accelerator*.

    Returns ``None`` if the combination is not supported.
    """
    acc_key = accelerator.replace("-", "_")
    config_path = _INDUSTRIES_ROOT / industry / f"{acc_key}.yaml"
    if not config_path.exists():
        return None
    with config_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def list_industry_support() -> dict[str, dict[str, bool]]:
    """Return ``{industry: {accelerator: supported}}`` for all known industries."""
    from dia.accelerators import ACCELERATOR_REGISTRY

    result: dict[str, dict[str, bool]] = {}
    for industry_dir in sorted(_INDUSTRIES_ROOT.iterdir()):
        if not industry_dir.is_dir() or industry_dir.name.startswith("_"):
            continue
        industry = industry_dir.name
        result[industry] = {}
        for acc_name in ACCELERATOR_REGISTRY:
            acc_key = acc_name.replace("-", "_")
            result[industry][acc_name] = (industry_dir / f"{acc_key}.yaml").exists()
    return result
