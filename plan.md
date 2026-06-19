# Project Plan: Databricks Industry Accelerators

## 1. Package Name & Identity

### Recommendation: `dia`

**Full name:** `databricks-industry-accelerators`  
**PyPI package:** `databricks-industry-accelerators`  
**Import name / CLI command:** `dia`

Alternative names considered:

| Name | CLI | Pros | Cons |
|---|---|---|---|
| `databricks-industry-accelerators` | `dia` | Descriptive, memorable acronym | Long install name |
| `dbx-spark-starter` | `dss` | Technical clarity | Less brand-friendly |
| `dblaunch` | `dblaunch` | Short and punchy | Less descriptive |
| `databricks-kickstart` | `dks` | Clear intent | Generic |

**Decision:** Go with `dia`. Short, pronounceable, and `dia setup ...` reads naturally.

---

## 2. Repository Structure

```
databricks-industry-accelerators/
├── src/
│   └── dia/
│       ├── __init__.py
│       ├── cli.py                        # Typer CLI entrypoint
│       ├── accelerators/
│       │   ├── __init__.py
│       │   ├── base.py                   # Abstract accelerator base class
│       │   ├── medallion_notebooks/      # Spark notebooks + job
│       │   ├── medallion_sdp/            # Streaming Delta Pipeline + job
│       │   ├── dashboard/                # Lakeview dashboard
│       │   ├── genie_space/              # AI/BI Genie Space
│       │   ├── mlflow_project/           # MLflow experiment + model registry
│       │   └── app/                      # Streamlit / Flask / Dash / Node.js
│       ├── data/
│       │   ├── __init__.py
│       │   ├── source.py                 # Spark Custom DataSource base
│       │   ├── schemas/                  # YAML schema definitions per industry
│       │   └── generators/               # Faker-backed field generators
│       ├── industries/
│       │   ├── __init__.py
│       │   ├── finance/
│       │   ├── retail/
│       │   ├── manufacturing/
│       │   ├── healthcare/
│       │   └── logistics/
│       ├── deploy/
│       │   ├── __init__.py
│       │   └── bundle.py                 # Databricks Asset Bundle generator
│       └── templates/                    # Jinja2 templates for generated files
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── mkdocs.yml
│   └── docs/
│       ├── index.md
│       ├── getting-started.md
│       ├── cli-reference.md
│       ├── accelerators/
│       └── industries/
├── SKILL.md
├── README.md
├── pyproject.toml
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── publish.yml
│       └── docs.yml
└── examples/
```

---

## 3. CLI Design

**Tool:** [Typer](https://typer.tiangolo.com/) — best-in-class for Python CLIs, integrates with Click, auto-generates `--help`.

### Command Structure

```
dia <command> [subcommand] [options]
```

### Core Commands

```bash
# Initialize a new accelerator in the current directory
dia init <accelerator> --industry <industry> [--app-type <type>]

# List available accelerators and industries
dia list
dia list accelerators
dia list industries

# Deploy via Databricks Asset Bundle
dia deploy [--env <dev|staging|prod>]

# Generate synthetic data locally or to a target
dia data generate --schema <industry> --rows <n> [--output <path>]
dia data preview --schema <industry>

# Validate the generated bundle before deploying
dia validate

# Show version and config info
dia info
```

### Example Invocations

```bash
# Finance reporting dashboard
dia init dashboard --industry finance

# Retail medallion pipeline using notebooks
dia init medallion-notebooks --industry retail

# Manufacturing SDP pipeline
dia init medallion-sdp --industry manufacturing

# Streamlit app for healthcare
dia init app --industry healthcare --app-type streamlit

# MLflow churn model for retail
dia init mlflow-project --industry retail

# Deploy to dev after setup
dia deploy --env dev

# Preview generated fake data schema
dia data preview --schema finance.transactions
```

### Design Principles

- All commands are non-destructive by default; `--force` required to overwrite existing files.
- Every command respects a `--dry-run` flag that prints what would happen.
- Commands print structured progress with rich formatting (use [Rich](https://github.com/Textualize/rich)).
- Each accelerator generates a self-contained directory the user can inspect and modify before deploying.

---

## 4. Accelerators

Each accelerator is a class that:
1. Takes an `industry` and optional `config` dict as input.
2. Renders Jinja2 templates into a target directory.
3. Generates a valid Databricks Asset Bundle structure.

### Accelerator Matrix

| Accelerator | Description | Output |
|---|---|---|
| `medallion-notebooks` | Bronze/Silver/Gold using PySpark notebooks + DLT job | Notebooks + `databricks.yml` |
| `medallion-sdp` | Streaming Delta Pipeline (declarative) + job | Pipeline definition + `databricks.yml` |
| `dashboard` | Lakeview dashboard wired to Silver/Gold tables | Dashboard JSON + `databricks.yml` |
| `genie-space` | AI/BI Genie Space over Gold tables | Genie config + `databricks.yml` |
| `mlflow-project` | MLflow experiment, training job, model registry | MLproject + `databricks.yml` |
| `app` | Web app connecting to Databricks (choice of framework) | App source + `databricks.yml` |

### App Type Options (for `app` accelerator)

- `streamlit` (default)
- `flask`
- `dash`
- `nodejs`

---

## 5. Industry Variants

Industries affect two things: the **data schema** and the **semantic layer** (table names, metric names, column names). The accelerator structure (pipeline topology, app scaffolding) is identical — only the data model changes.

### Included Industries

| Industry | Key Use Cases | Characteristic Data Entities |
|---|---|---|
| `finance` | Financial reporting, P&L, risk | Accounts, transactions, ledger entries, FX rates |
| `retail` | Sales analytics, inventory, CRM | Products, orders, customers, stores, inventory |
| `manufacturing` | OEE, quality control, predictive maintenance | Assets, work orders, sensor readings, defects |
| `healthcare` | Patient analytics, clinical operations | Patients, encounters, diagnoses, procedures |
| `logistics` | Fleet tracking, route optimization, delivery SLA | Shipments, routes, vehicles, warehouses |

### Industry + Accelerator Combinations

Not all combinations make equal sense. Recommended pairings:

| | medallion-notebooks | medallion-sdp | dashboard | genie-space | mlflow-project | app |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| finance | ✓ | ✓ | ✓ | ✓ | ✓ (fraud) | ✓ |
| retail | ✓ | ✓ | ✓ | ✓ | ✓ (churn) | ✓ |
| manufacturing | ✓ | ✓ | ✓ | ✓ | ✓ (predictive maint.) | ✓ |
| healthcare | ✓ | — | ✓ | ✓ | ✓ (readmission) | ✓ |
| logistics | ✓ | ✓ | ✓ | ✓ | — | ✓ |

Unsupported combinations raise a clear CLI error with a suggestion.

---

## 6. Synthetic Data Framework

### Architecture

Use a **Spark Custom DataSource** (Python DataSource API, available in Databricks Runtime 14.0+). This means:
- Works in notebooks and SDP alike — same code path.
- Generates data lazily as a DataFrame; no files need to be materialized first.
- Partitioned by default so large volumes parallelize naturally.

### Schema Definitions

Each industry has YAML schema files:

```yaml
# src/dia/data/schemas/finance/transactions.yaml
name: transactions
description: Financial transactions ledger
fields:
  - name: transaction_id
    type: string
    generator: uuid
  - name: account_id
    type: string
    generator: foreign_key
    ref: accounts.account_id
  - name: amount
    type: decimal(18,2)
    generator: random_decimal
    min: -50000
    max: 50000
  - name: currency
    type: string
    generator: choice
    values: [USD, EUR, GBP, DKK, SEK]
  - name: transaction_date
    type: timestamp
    generator: timestamp_range
    start: "2020-01-01"
    end: "now"
  - name: category
    type: string
    generator: choice
    values: [income, expense, transfer, fee]
```

Users can override or extend schemas by placing their own YAML files in a local `dia_schemas/` directory — the package merges these over the defaults.

### Generators (built-in)

| Generator | Description |
|---|---|
| `uuid` | UUID v4 |
| `random_int` / `random_decimal` | Numeric range |
| `choice` | Weighted or uniform from a list |
| `timestamp_range` | Timestamps between start/end |
| `foreign_key` | Reference to another table's column |
| `name`, `email`, `address` | Faker-backed PII-like fields |
| `company`, `iban`, `product_sku` | Domain-specific via Faker providers |

---

## 7. Deployment via Databricks Asset Bundles

Every accelerator generates a valid **Databricks Asset Bundle (DAB)** structure:

```
my-project/
├── databricks.yml          # Bundle root — targets, workspace, resources
├── resources/
│   ├── jobs.yml            # Job definitions
│   ├── pipelines.yml       # SDP pipeline definitions (if applicable)
│   └── dashboards.yml      # Dashboard resources (if applicable)
├── src/
│   └── ...                 # Notebooks / pipeline code / app code
└── fixtures/
    └── ...                 # Optional: seed data or schema overrides
```

### Targets

By default, three targets are generated:

```yaml
targets:
  dev:
    mode: development
    workspace:
      host: ${var.workspace_host}
  staging:
    mode: staging
    workspace:
      host: ${var.workspace_host}
  prod:
    mode: production
    workspace:
      host: ${var.workspace_host}
```

Users set `workspace_host` via environment variables or a `.env` file (gitignored by default).

### Deploy Flow

```bash
dia init medallion-notebooks --industry retail
cd retail-medallion-notebooks
dia deploy --env dev
# Internally runs: databricks bundle deploy --target dev
```

The `dia deploy` command is a thin wrapper that validates the bundle, checks for a Databricks CLI installation, and then calls `databricks bundle deploy`.

---

## 8. Documentation

### SKILL.md

A single `SKILL.md` at repo root written for LLM agents (Copilot, Claude, Codex, etc.). Contents:

- What `dia` does and when to use it
- Full CLI command reference with argument types
- Decision tree: which accelerator + industry combination fits which use case
- How to extend schemas or add custom industries
- Deployment prerequisites checklist

Format follows the emerging SKILL.md convention: plain Markdown, structured with H2 sections, no assumed context from previous turns.

### Docs Site

Use **MkDocs with Material theme** for GitHub Pages — the standard for Python packages. The user mentioned "zensical"; if that refers to a specific internal tool, swap in that theme. Otherwise Material is the closest match for an excellent docs experience.

Structure:
- **Getting Started** — install, configure, first `dia init`
- **CLI Reference** — auto-generated from Typer (via `typer-cli docs`)
- **Accelerators** — one page per accelerator with diagram + example
- **Industries** — one page per industry with data model diagram
- **Data Generation** — schema format reference, custom schema guide
- **Deployment** — DAB concepts, environment setup, CI/CD guide
- **Contributing** — adding new accelerators or industries

GitHub Actions workflow auto-publishes `docs/` to `gh-pages` on every push to `main`.

---

## 9. Python Package Setup

**Build system:** `pyproject.toml` with `hatchling`.

### Key Dependencies

```toml
[project]
name = "databricks-industry-accelerators"
dependencies = [
    "typer[all]>=0.12",
    "rich>=13",
    "jinja2>=3.1",
    "pyyaml>=6",
    "faker>=25",
    "pyspark>=3.5",          # optional; users may have it from Databricks already
    "databricks-sdk>=0.26",   # for programmatic workspace interaction
]

[project.scripts]
dia = "dia.cli:app"
```

---

## 10. Development Roadmap

### Phase 1 — Foundation (MVP)

- [ ] Python package scaffold (`pyproject.toml`, `src/dia/`, CLI entrypoint)
- [ ] `dia list` command
- [ ] `medallion-notebooks` accelerator for `finance` industry
- [ ] Synthetic data framework: `transactions` and `accounts` schemas
- [ ] DAB bundle generator (dev + prod targets)
- [ ] `dia deploy` wrapper command
- [ ] README and basic SKILL.md
- [ ] Publish to PyPI (test instance first)

### Phase 2 — Accelerator Coverage

- [ ] `medallion-sdp` accelerator
- [ ] `dashboard` accelerator (Lakeview)
- [ ] `genie-space` accelerator
- [ ] All 5 industries for `medallion-notebooks`
- [ ] `dia data generate` and `dia data preview` commands
- [ ] Full schema library for all industries

### Phase 3 — Advanced Accelerators

- [ ] `mlflow-project` accelerator with industry-specific model examples
- [ ] `app` accelerator (Streamlit first, then Flask/Dash/Node.js)
- [ ] ERP data models: Dynamics 365, Salesforce, SAP (as schema extensions)
- [ ] `dia validate` command (bundle + schema validation)

### Phase 4 — Documentation & Polish

- [ ] Full MkDocs docs site with GitHub Actions publish
- [ ] Auto-generated CLI reference from Typer
- [ ] Data model diagrams (auto-generated from YAML schemas)
- [ ] Integration tests against a real Databricks Free workspace
- [ ] GitHub Releases with changelog

---

## 11. Open Decisions

These need resolution before or during Phase 1:

| Decision | Options | Recommendation |
|---|---|---|
| Docs tool | MkDocs Material, Docusaurus, "Zensical" | MkDocs Material unless "Zensical" is a specific requirement |
| PySpark dependency | Required, optional extra, omit entirely | Optional extra (`pip install dia[spark]`) |
| Databricks CLI requirement | Bundled, expected on PATH, SDK-only | Expect on PATH; document install steps |
| Schema override mechanism | Local YAML files, env var, CLI flag | Local `dia_schemas/` directory merged over defaults |
| Free workspace support | Auth via PAT, OAuth, service principal | Support all three; document each |
