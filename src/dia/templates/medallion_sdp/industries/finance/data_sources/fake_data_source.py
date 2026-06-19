"""Finance fake data source — PySpark Python DataSource (DBR 14.0+).

Generates realistic synthetic financial data using Faker.
Supported tables: transactions | accounts | customers

Usage inside a DLT pipeline:
    spark.dataSource.register(FinanceFakeDataSource)
    df = spark.read.format("FinanceFakeDataSource").option("table", "transactions").load()

Options:
    table          — which table to generate (required)
    numRows        — total rows to produce (default: 10 000)
    numPartitions  — number of Spark partitions (default: 10)
"""

from __future__ import annotations

from pyspark.sql.datasource import DataSource, DataSourceReader
from pyspark.sql.types import (
    DateType,
    DecimalType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------

_SCHEMAS: dict[str, StructType] = {
    "transactions": StructType(
        [
            StructField("transaction_id", StringType(), nullable=False),
            StructField("account_id", StringType(), nullable=False),
            StructField("customer_id", StringType(), nullable=False),
            StructField("amount", DecimalType(18, 2), nullable=False),
            StructField("transaction_date", TimestampType(), nullable=False),
            StructField("category", StringType(), nullable=False),
            StructField("status", StringType(), nullable=False),
            StructField("description", StringType(), nullable=True),
        ]
    ),
    "accounts": StructType(
        [
            StructField("account_id", StringType(), nullable=False),
            StructField("customer_id", StringType(), nullable=False),
            StructField("account_type", StringType(), nullable=False),
            StructField("currency", StringType(), nullable=False),
            StructField("balance", DecimalType(18, 2), nullable=False),
            StructField("opened_date", DateType(), nullable=False),
            StructField("status", StringType(), nullable=False),
        ]
    ),
    "customers": StructType(
        [
            StructField("customer_id", StringType(), nullable=False),
            StructField("first_name", StringType(), nullable=False),
            StructField("last_name", StringType(), nullable=False),
            StructField("email", StringType(), nullable=False),
            StructField("phone", StringType(), nullable=True),
            StructField("country", StringType(), nullable=False),
            StructField("city", StringType(), nullable=False),
            StructField("customer_segment", StringType(), nullable=False),
            StructField("created_date", DateType(), nullable=False),
        ]
    ),
}


# ---------------------------------------------------------------------------
# DataSource
# ---------------------------------------------------------------------------

class FinanceFakeDataSource(DataSource):
    @classmethod
    def name(cls) -> str:
        return "FinanceFakeDataSource"

    def schema(self) -> StructType:
        table = self.options.get("table", "transactions")
        if table not in _SCHEMAS:
            raise ValueError(f"Unknown table {table!r}. Choose from: {list(_SCHEMAS)}")
        return _SCHEMAS[table]

    def reader(self, schema: StructType) -> "FinanceFakeDataSourceReader":
        return FinanceFakeDataSourceReader(schema, self.options)


# ---------------------------------------------------------------------------
# DataSourceReader
# ---------------------------------------------------------------------------

class FinanceFakeDataSourceReader(DataSourceReader):
    def __init__(self, schema: StructType, options: dict[str, str]) -> None:
        self.schema = schema
        self.table = options.get("table", "transactions")
        self.num_rows = int(options.get("numRows", 10_000))
        self.num_partitions = int(options.get("numPartitions", 10))

    def partitions(self) -> list[dict]:
        rows_each = max(1, self.num_rows // self.num_partitions)
        return [
            {"start_index": i * rows_each, "num_rows": rows_each}
            for i in range(self.num_partitions)
        ]

    def read(self, partition: dict):  # noqa: ANN201
        from decimal import Decimal

        from faker import Faker

        fake = Faker()
        Faker.seed(partition["start_index"])

        table = self.table
        n = partition["num_rows"]

        if table == "transactions":
            categories = ["income", "expense", "transfer", "fee", "refund"]
            statuses = ["completed", "pending", "failed", "reversed"]
            for _ in range(n):
                yield (
                    fake.uuid4(),
                    fake.uuid4(),
                    fake.uuid4(),
                    Decimal(str(round(fake.pyfloat(left_digits=5, right_digits=2, positive=False), 2))),
                    fake.date_time_between(start_date="-3y"),
                    fake.random_element(categories),
                    fake.random_element(statuses),
                    fake.sentence(nb_words=6),
                )

        elif table == "accounts":
            account_types = ["checking", "savings", "investment", "credit"]
            currencies = ["USD", "EUR", "GBP", "DKK", "SEK", "CHF"]
            statuses = ["active", "inactive", "frozen", "closed"]
            for _ in range(n):
                yield (
                    fake.uuid4(),
                    fake.uuid4(),
                    fake.random_element(account_types),
                    fake.random_element(currencies),
                    Decimal(str(round(fake.pyfloat(left_digits=8, right_digits=2, positive=True), 2))),
                    fake.date_between(start_date="-10y"),
                    fake.random_element(statuses),
                )

        elif table == "customers":
            segments = ["retail", "private", "corporate", "institutional"]
            for _ in range(n):
                yield (
                    fake.uuid4(),
                    fake.first_name(),
                    fake.last_name(),
                    fake.email(),
                    fake.phone_number(),
                    fake.country(),
                    fake.city(),
                    fake.random_element(segments),
                    fake.date_between(start_date="-5y"),
                )

        else:
            raise ValueError(f"Unknown table {table!r}")
