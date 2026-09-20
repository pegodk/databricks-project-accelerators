"""Integration tests: scaffold → validate → deploy → destroy against a live workspace."""

from __future__ import annotations

from pathlib import Path

import pytest

from dpa.accelerators import ACCELERATOR_REGISTRY

# Verified against https://dbc-b208d150-24a9.cloud.databricks.com/ on 2026-09-20.
# Free Edition targets are enabled only after a successful full bundle deployment.
FREE_EDITION_SUPPORTED_ACCELERATORS: tuple[str, ...] = ()
FREE_EDITION_EXCLUDED_ACCELERATORS = {
    "ai-bi": (
        "Free Edition Default Storage cannot create the bundle's Unity Catalog catalog; "
        "the Genie resource also has invalid sample-question IDs."
    ),
    "custom-python-wheel": "Free Edition Default Storage cannot create the bundle's Unity Catalog catalog.",
    "lakebase-streamlit-app": (
        "The Free Edition workspace has reached its three-app quota, and the static Lakebase PostgreSQL project ID "
        "already exists."
    ),
    "medallion-dbt": "Free Edition Default Storage cannot create the bundle's Unity Catalog catalogs.",
    "medallion-sdp": "Free Edition Default Storage cannot create the bundle's Unity Catalog catalogs.",
    "mlflow-project": "Free Edition Default Storage cannot create the bundle's Unity Catalog catalog.",
}

assert set(FREE_EDITION_SUPPORTED_ACCELERATORS) | set(FREE_EDITION_EXCLUDED_ACCELERATORS) == set(ACCELERATOR_REGISTRY)

@pytest.mark.integration
@pytest.mark.usefixtures("_workspace_env")
@pytest.mark.parametrize("deployed_project", FREE_EDITION_SUPPORTED_ACCELERATORS, indirect=True)
def test_bundle_deploys(deployed_project: Path) -> None:
    """A supported bundle completed the fixture-managed deployment lifecycle."""
    assert deployed_project.is_dir()
