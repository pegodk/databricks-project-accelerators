# Lakebase App Accelerator

The **Lakebase App** accelerator scaffolds a [Streamlit](https://streamlit.io/) analytics app hosted directly on Databricks, connected to the TPCH sample dataset via a SQL warehouse and a [Lakebase](https://docs.databricks.com/en/lakebase/index.html) (managed Postgres) instance for master data management. No external hosting or infrastructure needed — the app runs inside your Databricks workspace and inherits workspace authentication automatically.

## What is a Databricks App?

Databricks Apps is a serverless hosting environment for Python web applications inside your workspace. You deploy code, Databricks handles compute, scaling, and authentication. Users access the app through a workspace URL and are authenticated via their Databricks identity — no separate auth system required.

Streamlit is the Python library used here. It lets you build interactive dashboards with plain Python: write a script, and Streamlit renders charts, tables, filters, and metrics as a web UI.

## What gets generated

```
lakebase-app/
├── databricks.yml              # Asset Bundle root config
├── .gitignore
├── app/
│   ├── app.py                  # Streamlit application
│   ├── app.yaml                # Databricks App entrypoint config
│   └── requirements.txt        # Python dependencies
└── resources/
    ├── apps/
    │   └── app.yml             # Databricks App resource definition
    ├── postgres_projects/
    │   └── lakebase.yml        # Lakebase project (managed Postgres)
    ├── postgres_branches/
    │   └── production.yml      # Production branch (protected, no expiry)
    └── postgres_endpoints/
        └── primary.yml         # Read/write endpoint (autoscaling)
```

## Two-step deploy

Lakebase resources must exist before the app can connect to them. The first deploy provisions the Postgres project, branch, and endpoint. Then you copy the connection details from the Databricks UI and redeploy.

**Step 1 — provision Lakebase:**

```bash
dpa init lakebase-app
cd lakebase-app
databricks bundle deploy --target dev
```

After the deploy completes, open the Databricks UI under **Lakebase** and copy:

- **PGHOST** — the endpoint hostname (from the Connect modal)
- **ENDPOINT_NAME** — the endpoint resource path (from the Computes tab, e.g. `projects/.../branches/.../endpoints/primary`)

**Step 2 — deploy the app with connection details:**

```bash
databricks bundle deploy --target dev \
  --var="lakebase_pghost=<host>" \
  --var="lakebase_endpoint=<endpoint-path>"
```

The app will appear under **Apps** in the Databricks UI.

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

## Authentication

The app connects to Lakebase using OAuth tokens issued by the Databricks SDK. Tokens are rotated automatically on each connection (tokens expire after 1 hour) using a custom `psycopg3` connection class:

```python
class _OAuthConn(psycopg.Connection):
    @classmethod
    def connect(cls, conninfo="", **kwargs):
        cred = WorkspaceClient().postgres.generate_database_credential(endpoint=ENDPOINT_NAME)
        kwargs["password"] = cred.token
        return super().connect(conninfo, **kwargs)
```

The `DATABRICKS_CLIENT_ID` env var is auto-injected by Databricks Apps as the service principal identity and is used as the Postgres username.

## Variables

| Variable | Default | Description |
|---|---|---|
| `warehouse_id` | _(auto-resolved)_ | SQL Warehouse for TPCH analytics. Resolved by name ("Serverless Starter Warehouse"). |
| `lakebase_project_id` | `lakebase-app-lakebase` | Lakebase project ID (lowercase, hyphen-delimited). |
| `lakebase_min_cu` | `0.5` | Minimum compute units for the Lakebase endpoint. |
| `lakebase_max_cu` | `0.5` | Maximum compute units for the Lakebase endpoint. |
| `lakebase_pghost` | _(set after first deploy)_ | Endpoint hostname — copy from Lakebase Connect modal. |
| `lakebase_endpoint` | _(set after first deploy)_ | Endpoint resource path — copy from Lakebase Computes tab. |

## Customising the app

The app lives in `app/app.py`. Add Python packages to `app/requirements.txt` and redeploy — the runtime installs them on app startup.
