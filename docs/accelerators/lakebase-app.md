# App Streamlit Accelerator

The **App Streamlit** accelerator scaffolds a [Streamlit](https://streamlit.io/) analytics app hosted directly on Databricks, connected to the TPCH sample dataset via a SQL warehouse and a [Lakebase](https://docs.databricks.com/en/lakebase/index.html) (managed Postgres) instance for master data management. No external hosting or infrastructure needed — the app runs inside your Databricks workspace and inherits workspace authentication automatically.

## What is a Databricks App?

Databricks Apps is a serverless hosting environment for Python web applications inside your workspace. You deploy code, Databricks handles compute, scaling, and authentication. Users access the app through a workspace URL and are authenticated via their Databricks identity — no separate auth system required.

Streamlit is the Python library used here. It lets you build interactive dashboards with plain Python: write a script, and Streamlit renders charts, tables, filters, and metrics as a web UI.

## What gets generated

```
app-streamlit/
├── databricks.yml              # Asset Bundle root config
├── .gitignore
├── app/
│   ├── app.py                  # Streamlit application
│   ├── app.yaml                # Databricks App entrypoint config
│   └── requirements.txt        # Python dependencies
└── resources/
    └── apps/
        └── app.yml             # Databricks App resource definition
```

## What the app shows

The app has two tabs.

**Analytics** — five views backed by queries against `samples.tpch` via a SQL warehouse:

- **KPI row** — Total Revenue, Total Orders, Avg Order Value, Unique Customers
- **Monthly Revenue** — area chart of revenue by month
- **Revenue by Market Segment** — bar chart across the five TPCH market segments
- **Orders by Status** — donut chart of Open / Fulfilled / Pending orders
- **Revenue & Discount by Ship Mode** — grouped bar chart of gross vs. net revenue per shipping mode
- **Top 20 Customers** — table with customer name, segment, nation, revenue, orders, avg order value

Results are cached for one hour (`@st.cache_data(ttl=3600)`), so repeated page views don't re-query the warehouse.

**Master Data** — an editable table backed by Lakebase (Postgres):

- Loads the top 50 customers from `samples.tpch.customer` and merges with any overrides stored in Lakebase.
- Users can edit **Display Name** and **Market Segment** inline via `st.data_editor`.
- Saving upserts changes into a `customer_master` table in Lakebase. The table is created automatically on first load.

This demonstrates using Lakebase as a low-latency transactional layer alongside the analytical SQL warehouse — a pattern common in master data management and operational apps.

## Requirements

- Unity Catalog enabled in your workspace
- A SQL warehouse (resolved automatically via the `warehouse_id` variable)
- A Lakebase instance with connection credentials stored in a Databricks secret scope

## Usage

```bash
dpa init app-streamlit
cd app-streamlit
```

Store your Lakebase credentials in a Databricks secret scope (default scope name: `dpa-secrets`):

```bash
databricks secrets create-scope dpa-secrets
databricks secrets put-secret dpa-secrets lakebase_host    --string-value <host>
databricks secrets put-secret dpa-secrets lakebase_database --string-value <database>
databricks secrets put-secret dpa-secrets lakebase_user    --string-value <user>
databricks secrets put-secret dpa-secrets lakebase_password --string-value <password>
```

Deploy:

```bash
databricks bundle deploy --target dev
```

Find the app URL in the Databricks UI under **Apps → dpa-app-streamlit**.

For production:

```bash
databricks bundle deploy --target prod
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `warehouse_id` | _(auto-resolved)_ | SQL Warehouse used for TPCH analytics queries. Resolved by name ("Serverless Starter Warehouse") if not set. |
| `secret_scope` | `dpa-secrets` | Databricks secret scope that holds the Lakebase connection credentials. |

## Customising the app

The app lives in `app/app.py`. The Lakebase connection is configured via environment variables injected from the secret scope:

```python
LAKEBASE_HOST     = os.environ.get("LAKEBASE_HOST", "")
LAKEBASE_PORT     = int(os.environ.get("LAKEBASE_PORT", "5432"))
LAKEBASE_DATABASE = os.environ.get("LAKEBASE_DATABASE", "")
LAKEBASE_USER     = os.environ.get("LAKEBASE_USER", "")
LAKEBASE_PASSWORD = os.environ.get("LAKEBASE_PASSWORD", "")
```

Add Python packages to `app/requirements.txt` and redeploy — the runtime installs them on app startup.
