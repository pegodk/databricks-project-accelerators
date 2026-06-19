"""Medallion layer configuration loaded from Spark pipeline variables."""

from __future__ import annotations

from dataclasses import dataclass


def _spark_conf(key: str, default: str = "") -> str:
    from pyspark.sql import SparkSession

    return SparkSession.builder.getOrCreate().conf.get(key, default)


@dataclass
class Config:
    bronze_catalog: str
    bronze_schema: str
    silver_catalog: str
    silver_schema: str
    gold_catalog: str
    gold_schema: str

    @classmethod
    def from_spark_config(cls) -> "Config":
        """Construct from Spark pipeline configuration variables."""
        return cls(
            bronze_catalog=_spark_conf("bronze_catalog"),
            bronze_schema=_spark_conf("bronze_schema"),
            silver_catalog=_spark_conf("silver_catalog"),
            silver_schema=_spark_conf("silver_schema"),
            gold_catalog=_spark_conf("gold_catalog"),
            gold_schema=_spark_conf("gold_schema"),
        )

    def layer(self, name: str) -> str:
        """Return ``catalog.schema`` for *name* (bronze | silver | gold)."""
        return f"{getattr(self, f'{name}_catalog')}.{getattr(self, f'{name}_schema')}"
