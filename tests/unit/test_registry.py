"""Unit tests for the accelerator registry."""

from __future__ import annotations


def test_get_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("medallion-sdp")
    assert cls is not None
    assert cls.name == "medallion-sdp"


def test_get_unknown_accelerator():
    from dpa.accelerators import get_accelerator

    assert get_accelerator("unicorn-engine") is None


def test_registry_contains_all_accelerators():
    from dpa.accelerators import ACCELERATOR_REGISTRY

    assert "medallion-sdp" in ACCELERATOR_REGISTRY
    assert "custom-spark-lib" in ACCELERATOR_REGISTRY
    assert "medallion-dbt" in ACCELERATOR_REGISTRY
    assert "mlflow-project" in ACCELERATOR_REGISTRY
    assert "lakebase-app" in ACCELERATOR_REGISTRY
    assert "python-wheel" in ACCELERATOR_REGISTRY
    assert "ai-bi" in ACCELERATOR_REGISTRY
