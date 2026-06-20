# AI/BI Accelerator

The **AI/BI** accelerator scaffolds a complete Databricks AI/BI solution over the TPCH sample dataset: metric views as the semantic layer, a Lakeview dashboard for visual analytics, and a Genie Space for natural-language querying — all deployed via a single Databricks Asset Bundle.

## What gets generated

```
ai-bi/
├── databricks.yml                                    # Asset Bundle root config
├── .gitignore
├── src/
│   └── sql/
│       └── metric_views.sql                          # 7 metric views over samples.tpch
├── dashboard/
│   └── tpch_overview.lvdash.json                     # Lakeview dashboard (3 pages)
├── genie/
│   └── tpch_genie.geniespace.json                    # Genie Space definition
└── resources/
    ├── warehouses/warehouse.yml                      # Serverless SQL warehouse
    ├── jobs/setup_views_job.yml                      # One-time job to create metric views
    ├── dashboards/dashboard.yml                      # Lakeview dashboard resource
    └── genie_spaces/tpch_genie.genie_space.yml       # Genie Space resource
```

### Metric views (`src/sql/metric_views.sql`)

Seven views are created in your catalog/schema over `samples.tpch`:

| View | Description |
|---|---|
| `v_kpis` | Single-row summary: total orders, revenue, avg order value, unique customers |
| `v_revenue_by_month` | Monthly revenue trend |
| `v_revenue_by_segment` | Revenue by customer market segment |
| `v_revenue_by_region` | Revenue by geographic region and nation |
| `v_top_customers` | Top 50 customers by lifetime revenue |
| `v_shipmode_summary` | Revenue, discount, and quantity by shipping mode |
| `v_order_priority_summary` | Revenue and order count by priority level |

### Lakeview dashboard (`dashboard/tpch_overview.lvdash.json`)

Three pages with counters, area charts, bar charts, pie charts, and tables:

- **Overview** — KPI counters, monthly revenue trend, revenue by segment and order priority
- **Logistics & Geography** — revenue and discounts by ship mode, region/nation breakdown table
- **Top Customers** — top 20 customers table, revenue by customer segment

### Genie Space (`genie/tpch_genie.geniespace.json`)

Pre-seeded with 10 curated questions and instructions tuned to the TPCH domain. All seven metric views are bound as tables. Users can ask questions like:

- "What is the total revenue across all orders?"
- "Which market segment generates the most revenue?"
- "Which shipping mode has the highest average discount?"

## Requirements

- Databricks CLI v1.3.0+ (required for Genie Space bundle support)
- Direct deployment engine enabled (default for new bundles with CLI v1.3.0+)
- Unity Catalog enabled in your workspace
- Access to `samples.tpch` (built-in Databricks sample data)

## Usage

```bash
dpa init ai-bi
cd ai-bi

# Deploy (dev target by default)
databricks bundle deploy

# Run the setup job to create metric views before opening the dashboard or Genie Space
databricks bundle run <project_slug>_setup_views
```

For production:

```bash
databricks bundle deploy --target prod
```

## Variables

Defined in `databricks.yml` with sensible defaults:

| Variable | Default | Description |
|---|---|---|
| `catalog` | `main` | Unity Catalog catalog for metric views |
| `schema` | `tpch_metrics` | Schema for metric views |

Override at deploy time:

```bash
databricks bundle deploy --var="catalog=my_catalog" --var="schema=my_schema"
```

## Customising the Genie Space

After deploying, you can refine the Genie Space in the Databricks UI (add curated questions, adjust instructions, tune table descriptions). To pull your changes back into the bundle:

```bash
databricks bundle generate genie-space --resource <project_slug>_genie --force
```

!!! warning
    Redeploying overwrites any existing Genie Space with the same name, including its chat history. Use dev/prod targets to keep environments isolated.
