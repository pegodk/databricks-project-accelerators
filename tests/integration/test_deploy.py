"""Integration tests: scaffold → validate → deploy → destroy against a live workspace."""

from __future__ import annotations

import pytest

from dpa.accelerators import ACCELERATOR_REGISTRY
from tests.integration.conftest import DeployedProject, run_bundle_workload, verify_deployed_app

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


RUNNABLE_RESOURCES = {
    "ai-bi": "ai_bi_setup_views",
    "custom-python-wheel": "custom_python_wheel_wheel",
    "medallion-dbt": "medallion_dbt_job",
    "medallion-sdp": "medallion_sdp_pipeline",
    "mlflow-project": "mlflow_project_pipeline",
}
APP_RESOURCES = {
    "lakebase-streamlit-app": "dpa-lakebase-streamlit-app",
}


@pytest.mark.integration
@pytest.mark.usefixtures("_workspace_env")
@pytest.mark.parametrize("deployed_project", FREE_EDITION_SUPPORTED_ACCELERATORS, indirect=True)
def test_bundle_deploys_and_runs(deployed_project: DeployedProject) -> None:
    """A supported bundle deploys and its runnable workload succeeds."""
    assert deployed_project.project_dir.is_dir()

    resource = RUNNABLE_RESOURCES.get(deployed_project.accelerator_name)
    if resource:
        run_bundle_workload(deployed_project, resource)

    app_name = APP_RESOURCES.get(deployed_project.accelerator_name)
    if app_name:
        verify_deployed_app(deployed_project, app_name)
