# AI/BI Accelerator

The **AI/BI** accelerator scaffolds a complete Databricks AI/BI solution over the TPCH sample dataset: a metric view as the semantic layer, a Lakeview dashboard for visual analytics, and a Genie Space for natural-language querying — all deployed via a single Databricks Asset Bundle.

## What gets generated

```
ai-bi/
├── databricks.yml                                        # Asset Bundle root config
├── .gitignore
├── resources/
│   ├── dashboards/
│   │   ├── dashboard.yml                                 # Lakeview dashboard resource
│   │   └── tpch_overview.lvdash.json                     # Dashboard definition (3 pages)
│   ├── genie_spaces/
│   │   └── tpch_genie.genie_space.yml                    # Genie Space resource + config
│   ├── jobs/
│   │   └── setup_views_job.yml                           # One-time job to deploy metric view
│   └── warehouses/
│       └── warehouse.yml                                 # Serverless SQL warehouse
└── src/
    └── sql/
        └── setup_metric_views.sql                        # CREATE METRIC VIEW statement
```

## Metric view — `v_tpch`

A single metric view sourced from `samples.tpch.orders`, joined to customer and nation:

```
orders → customer → nation
```

Filter: `o_orderdate >= '1995-01-01'`

The metric view acts as the semantic layer for both the dashboard and the Genie Space. Fields carry `display_name` and `synonyms` metadata so Genie can resolve natural-language terms like "revenue", "sales", or "AOV" to the correct measure without additional configuration.

**Fields (dimensions)**

| Field | Expression | Description |
|---|---|---|
| `order_date` | `o_orderdate` | Date the order was placed |
| `order_month` | `DATE_TRUNC('MONTH', order_date)` | Month grain for trend analysis |
| `order_year` | `YEAR(order_date)` | Year grain |
| `order_status` | CASE on `o_orderstatus` | Open / Processing / Fulfilled |
| `order_priority` | `SPLIT(o_orderpriority, '-')[0]` | Priority number (1–5) |
| `customer_name` | `customer.c_name` | Customer display name |
| `market_segment` | `customer.c_mktsegment` | AUTOMOBILE / BUILDING / FURNITURE / HOUSEHOLD / MACHINERY |
| `customer_nation` | `customer.nation.n_name` | Customer country (synonyms: nation, country) |

**Measures**

| Measure | Expression | Format |
|---|---|---|
| `order_count` | `COUNT(DISTINCT o_orderkey)` | compact number |
| `total_revenue` | `SUM(o_totalprice)` | compact USD (synonyms: revenue, sales) |
| `unique_customers` | `COUNT(DISTINCT o_custkey)` | compact number |
| `avg_order_value` | `MEASURE(total_revenue) / MEASURE(order_count)` | USD (synonym: AOV) |
| `revenue_per_customer` | `MEASURE(total_revenue) / MEASURE(unique_customers)` | USD |
| `open_order_revenue` | `SUM(o_totalprice) FILTER (WHERE o_orderstatus = 'O')` | USD (synonym: backlog) |
| `fulfilled_order_revenue` | `SUM(o_totalprice) FILTER (WHERE o_orderstatus = 'F')` | USD |
| `t7d_customers` | `COUNT(DISTINCT o_custkey)` trailing 7-day window | compact number |

## Lakeview dashboard

Three pages backed by `MEASURE()` queries against `v_tpch`:

- **Overview** — Total Revenue, Total Orders, Avg Order Value counters; monthly revenue trend (area chart); revenue by market segment (bar) and by priority (pie)
- **Order Analysis** — Revenue and count by order status (bar + pie); revenue by country (table); unique customers counter
- **Top Customers** — Top 20 customers by total revenue (table with segment, country, avg order value); revenue by segment for those customers (bar)

## Genie Space

Pre-seeded with 10 curated sample questions and domain-specific instructions tuned to the TPCH dataset. Genie uses the metric view's `display_name` and `synonyms` fields for semantic resolution, so users can phrase questions naturally:

- "What is the total revenue?"
- "Which market segment generates the most revenue?"
- "What is the revenue split between open, processing, and fulfilled orders?"

## Why the setup job is needed

DAB does not yet support `metric_views` as a native resource type. The setup job runs `src/sql/setup_metric_views.sql` against the warehouse, which executes a `CREATE OR REPLACE METRIC VIEW` statement with the full view definition inlined as a SQL heredoc. The dashboard and Genie Space depend on `v_tpch` existing — run the setup job once before opening either.

## Requirements

- Databricks CLI v1.3.0+ (required for Genie Space bundle support)
- Unity Catalog enabled in your workspace
- Access to `samples.tpch` (built-in Databricks sample data — no setup needed)

## Usage

```bash
dpa init ai-bi
cd ai-bi

# Deploy resources (warehouse, dashboard, genie space)
databricks bundle deploy

# Create the metric view (run once before opening the dashboard or Genie Space)
databricks bundle run ai_bi_setup_views
```

For production:

```bash
databricks bundle deploy --target prod
databricks bundle run ai_bi_setup_views --target prod
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `catalog` | `dpa_gold_dev` | Unity Catalog catalog for the metric view |
| `schema` | `tpch_metrics` | Schema for the metric view |
| `warehouse_id` | _(required)_ | SQL Warehouse ID for the setup job and Genie Space |

Set `warehouse_id` in `databricks.yml` before deploying (find it under **SQL Warehouses → your warehouse → Connection details**). Override other variables at deploy time:

```bash
databricks bundle deploy --var="catalog=my_catalog" --var="schema=my_schema"
```

## Customising the Genie Space

After deploying, you can refine the Genie Space in the Databricks UI — add example SQL queries, adjust instructions, or add more sample questions. To pull changes back into the bundle:

```bash
databricks bundle generate genie-space --resource ai_bi_genie --force
```

!!! warning
    Redeploying overwrites any existing Genie Space with the same name, including chat history. Use dev/prod targets to keep environments isolated.
