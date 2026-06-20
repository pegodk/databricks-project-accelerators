# App Streamlit Accelerator

The **App Streamlit** accelerator scaffolds a [Streamlit](https://streamlit.io/) analytics app hosted directly on Databricks, connected to the TPCH sample dataset via a SQL warehouse. No external hosting or infrastructure needed — the app runs inside your Databricks workspace and inherits workspace authentication automatically.

## What is a Databricks App?

Databricks Apps is a serverless hosting environment for Python web applications inside your workspace. You deploy code, Databricks handles compute, scaling, and authentication. Users access the app through a workspace URL and are authenticated via their Databricks identity — no separate auth system required.

Streamlit is the Python library used here. It lets you build interactive dashboards with plain Python: write a script, and Streamlit renders charts, tables, filters, and metrics as a web UI. The app connects to a SQL warehouse for data queries, so it benefits from Databricks SQL optimisations (photon, caching, compute scaling) without any extra configuration.

## What gets generated

```
app-streamlit/
├── databricks.yml              # Asset Bundle root config
├── .gitignore
├── app/
│   ├── app.py                  # Streamlit application
│   ├── app.yaml                # Databricks App entrypoint config
│   └── requirements.txt        # Python dependencies (streamlit, plotly, databricks-sdk)
└── resources/
    ├── apps/
    │   └── app.yml             # Databricks App resource definition
    └── warehouses/
        └── warehouse.yml       # Serverless SQL warehouse
```

## What the app shows

Five views backed by queries against `samples.tpch`:

- **KPI row** — Total Revenue, Total Orders, Avg Order Value, Unique Customers
- **Monthly Revenue** — area chart of revenue by month
- **Revenue by Market Segment** — bar chart across AUTOMOBILE / BUILDING / FURNITURE / HOUSEHOLD / MACHINERY
- **Orders by Status** — donut chart of Open / Fulfilled / Pending orders
- **Revenue & Discount by Ship Mode** — grouped bar chart of gross vs. net revenue per shipping mode
- **Top 20 Customers** — table with customer name, segment, nation, revenue, orders, avg order value

Results are cached for one hour (`@st.cache_data(ttl=3600)`), so repeated page views don't re-query the warehouse.

## Requirements

- Unity Catalog enabled in your workspace
- A SQL warehouse to serve queries (created automatically by the bundle)

## Usage

```bash
dpa init app-streamlit
cd app-streamlit
```

Set your warehouse ID in `databricks.yml`, or let the bundle create one automatically (the default). Deploy:

```bash
databricks bundle deploy --target dev
```

Find the app URL in the Databricks UI under **Apps → dpa-app-streamlit**. The app is accessible to anyone with workspace access — no additional sharing step needed.

For production:

```bash
databricks bundle deploy --target prod
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `warehouse_id` | _(auto-created)_ | SQL Warehouse ID to connect the app to. Leave unset to let the bundle create a serverless warehouse. |

## Customising the app

The app lives in `app/app.py` — it is a plain Python file. Edit the SQL queries, add new chart types, or introduce Streamlit sidebar filters. The only Databricks-specific part is the connection setup at the top:

```python
HOSTNAME = os.environ.get("DATABRICKS_HOST", "").replace("https://", "")
HTTP_PATH = os.environ.get("DATABRICKS_HTTP_PATH", "")
```

`DATABRICKS_HOST` and `DATABRICKS_HTTP_PATH` are injected automatically by the Databricks Apps runtime from the app environment configuration in `resources/apps/app.yml`. You do not need to manage credentials in the app code.

Add Python packages to `app/requirements.txt` and redeploy — the runtime installs them on app startup.
