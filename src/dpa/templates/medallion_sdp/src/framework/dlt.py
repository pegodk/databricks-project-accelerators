"""DLT table decorator with integrated data quality expectations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import dlt
from pyspark.sql import DataFrame


def create_dlt_table(
    name: str,
    *,
    comment: str = "",
    table_properties: dict[str, str] | None = None,
    primary_keys: list[str] | None = None,
    expectations_warn: dict[str, str] | None = None,
    expectations_fail_update: dict[str, str] | None = None,
    expectations_drop_row: dict[str, str] | None = None,
) -> Callable[[Callable[[], DataFrame]], Any]:
    """Decorator that registers a DLT table with optional data quality rules.

    Expectation precedence (applied innermost → outermost):
      1. warn          → @dlt.expect_all        (logs violations, data passes)
      2. drop_row      → @dlt.expect_all_or_drop (removes failing rows)
      3. fail_update   → @dlt.expect_all_or_fail (stops the pipeline update)

    Primary key null checks are automatically added to ``fail_update``.
    """
    pk_nulls = {f"{k}_not_null": f"{k} IS NOT NULL" for k in (primary_keys or [])}
    all_fail = {**pk_nulls, **(expectations_fail_update or {})}
    all_drop = expectations_drop_row or {}
    all_warn = expectations_warn or {}

    def decorator(fn: Callable[[], DataFrame]) -> Any:
        decorated = fn
        if all_warn:
            decorated = dlt.expect_all(all_warn)(decorated)
        if all_drop:
            decorated = dlt.expect_all_or_drop(all_drop)(decorated)
        if all_fail:
            decorated = dlt.expect_all_or_fail(all_fail)(decorated)
        return dlt.table(
            name=name,
            comment=comment,
            table_properties=table_properties or {},
        )(decorated)

    return decorator
