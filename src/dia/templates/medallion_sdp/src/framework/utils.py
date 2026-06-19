"""DataFrame helpers shared across all pipeline layers."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T


def add_ingest_timestamp(df: DataFrame) -> DataFrame:
    """Append an ``ingest_timestamp`` column with the current time."""
    return df.withColumn("ingest_timestamp", F.current_timestamp())


def add_surrogate_id(df: DataFrame, col_name: str = "id") -> DataFrame:
    """Prepend a monotonically increasing surrogate key starting from 1."""
    df = df.withColumn(col_name, F.monotonically_increasing_id() + 1)
    cols = [col_name] + [c for c in df.columns if c != col_name]
    return df.select(cols)


def add_dummy_row(df: DataFrame, id_col: str = "id") -> DataFrame:
    """Prepend a -1 / 'N/A' sentinel row for unknown dimension members (Kimball pattern)."""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()

    dummy: dict[str, Any] = {}
    for field in df.schema:
        if field.name == id_col:
            dummy[field.name] = -1
        elif isinstance(field.dataType, T.StringType):
            dummy[field.name] = "N/A"
        elif isinstance(field.dataType, (T.IntegerType, T.LongType, T.ShortType, T.ByteType)):
            dummy[field.name] = -1
        elif isinstance(field.dataType, (T.DoubleType, T.FloatType, T.DecimalType)):
            dummy[field.name] = -1.0
        else:
            dummy[field.name] = None

    dummy_row = [tuple(dummy[f.name] for f in df.schema)]
    dummy_df = spark.createDataFrame(dummy_row, df.schema)
    return dummy_df.union(df)


def enrich_with_surrogate_keys(
    fact_df: DataFrame,
    dim_mappings: dict[str, DataFrame],
) -> DataFrame:
    """Replace natural keys (*_key columns) with surrogate IDs from dimension tables.

    *dim_mappings* maps natural-key column names to DataFrames with two columns:
    ``<dim>_key`` (natural) and ``<dim>_id`` (surrogate).
    """
    result = fact_df
    for natural_key_col, mapping_df in dim_mappings.items():
        dim_name = natural_key_col.removesuffix("_key")
        surrogate_col = f"{dim_name}_id"
        result = (
            result.join(mapping_df, on=natural_key_col, how="left")
            .drop(natural_key_col)
            .fillna({surrogate_col: -1})
        )
    return result


# Type hint only — avoid importing at module level so non-Spark environments work
from typing import Any  # noqa: E402
