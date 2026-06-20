# AI/BI Accelerator

The **AI/BI** accelerator scaffolds a complete Databricks AI/BI solution over the TPCH sample dataset: a single unified metric view as the semantic layer, a Lakeview dashboard for visual analytics, and a Genie Space for natural-language querying — all deployed via a single Databricks Asset Bundle.

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
│   │   ├── tpch_genie.genie_space.yml                    # Genie Space resource
│   │   └── tpch_genie.geniespace.json                    # Genie Space definition
│   ├── jobs/
│   │   └── setup_views_job.yml                           # One-time job to deploy metric view
│   ├── metric_views/
│   │   └── v_tpch.yml                                    # Metric view YAML definition
│   └── warehouses/
│       └── warehouse.yml                                 # Serverless SQL warehouse
└── src/
    └── sql/
        └── setup_metric_views.sql                        # Generated SQL (v_tpch.yml inlined)
```

## Metric view — `v_tpch`

A single metric view joining from `samples.tpch.lineitem` through the full TPCH dimension hierarchy:

```
lineitem → orders → customer → nation → region
```

**Fields (dimensions)**

| Field | Expression | Description |
|---|---|---|
| `order_date` | `orders.o_orderdate` | Date the order was placed |
| `order_month` | `DATE_TRUNC('MONTH', ...)` | Month grain for trend analysis |
| `order_status` | `orders.o_orderstatus` | O / F / P |
| `order_priority` | `orders.o_orderpriority` | 1-URGENT through 5-LOW |
| `ship_mode` | `l_shipmode` | AIR / MAIL / SHIP / TRUCK / REG AIR / FOB / RAIL |
| `ship_date` | `l_shipdate` | Date the line item shipped |
| `customer_name` | `orders.customer.c_name` | Customer display name |
| `market_segment` | `orders.customer.c_mktsegment` | AUTOMOBILE / BUILDING / FURNITURE / HOUSEHOLD / MACHINERY |
| `nation` | `orders.customer.nation.n_name` | Customer nation |
| `region` | `orders.customer.nation.region.r_name` | AFRICA / AMERICA / ASIA / EUROPE / MIDDLE EAST |

**Measures**

| Measure | Expression |
|---|---|
| `order_count` | `COUNT(DISTINCT orders.o_orderkey)` |
| `unique_customers` | `COUNT(DISTINCT orders.o_custkey)` |
| `gross_revenue` | `SUM(l_extendedprice)` |
| `net_revenue` | `SUM(l_extendedprice * (1 - l_discount))` |
| `net_revenue_with_tax` | `SUM(l_extendedprice * (1 - l_discount) * (1 + l_tax))` |
| `avg_discount` | `AVG(l_discount)` |
| `avg_quantity` | `AVG(l_quantity)` |
| `avg_order_value` | `net_revenue / order_count` |
| `line_item_count` | `COUNT(*)` |

All measures carry `display_name` and `synonyms` for AI/BI discovery.
All joins use `rely.at_most_one_match: true` for query optimisation.

## Lakeview dashboard

Three pages backed by `MEASURE()` queries against `v_tpch`:

- **Overview** — Net Revenue, Total Orders, Avg Order Value counters; monthly revenue trend (area chart); revenue by segment (bar) and by priority (pie)
- **Logistics & Geography** — revenue and discount by ship mode (bar charts); revenue by region/nation (table)
- **Top Customers** — top 20 customers by net revenue (table); revenue by segment for those customers (bar)

## Genie Space

Pre-seeded with 10 curated questions and instructions tuned to the TPCH domain. The single `v_tpch` metric view is registered as the table source — Genie uses its `display_name` and `synonyms` metadata for semantic resolution.

Example questions:
- "What is the total net revenue?"
- "Which market segment generates the most revenue?"
- "Which shipping mode has the highest average discount?"

## Why the setup job is still needed

DAB does not yet support `metric_views` as a native resource type. The setup job runs `src/sql/setup_metric_views.sql` against the warehouse, which executes a `CREATE OR REPLACE METRIC VIEW` statement with the `v_tpch.yml` definition inlined via Jinja2. When Databricks adds native DAB support, the job can be removed and `resources/metric_views/v_tpch.yml` will deploy directly.

## Requirements

- Databricks CLI v1.3.0+ (required for Genie Space bundle support)
- Direct deployment engine enabled (default for new bundles with CLI v1.3.0+)
- Unity Catalog enabled in your workspace
- Access to `samples.tpch` (built-in Databricks sample data)

## Usage

```bash
dpa init ai-bi
cd ai-bi

# Deploy resources (warehouse, dashboard, genie space)
databricks bundle deploy

# Create the metric view (run once before opening dashboard or Genie Space)
databricks bundle run <project_slug>_setup_views
```

For production:

```bash
databricks bundle deploy --target prod
databricks bundle run <project_slug>_setup_views --target prod
```

## Variables

Defined in `databricks.yml` with sensible defaults:

| Variable | Default | Description |
|---|---|---|
| `catalog` | `main` | Unity Catalog catalog for the metric view |
| `schema` | `tpch_metrics` | Schema for the metric view |

Override at deploy time:

```bash
databricks bundle deploy --var="catalog=my_catalog" --var="schema=my_schema"
```

## Customising the Genie Space

After deploying, you can refine the Genie Space in the Databricks UI. To pull changes back into the bundle:

```bash
databricks bundle generate genie-space --resource <project_slug>_genie --force
```

!!! warning
    Redeploying overwrites any existing Genie Space with the same name, including chat history. Use dev/prod targets to keep environments isolated.
